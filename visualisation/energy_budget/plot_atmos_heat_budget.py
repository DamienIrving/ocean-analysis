"""
Filename:     plot_atmos_heat_budget.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot climatology and trends in surface radiative and energy fluxes  

Input:        List of netCDF files to plot
Output:       An image in either bitmap (e.g. .png) or vector (e.g. .svg, .eps) format

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
from iris.experimental.equalise_cubes import equalise_attributes
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
try:
    import general_io as gio
    import timeseries
    import grids
    import convenient_universal as uconv
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

line_characteristics = {'rsds': ('downwelling shortwave', 'orange', 'dashed'), 
                        'rsus': ('upwelling shortwave', 'orange', 'dotted'),
                        'rsns': ('net shortwave', 'orange', 'dashdot'),
                        'rlds': ('downwelling longwave', 'red', 'dashed'), 
                        'rlus': ('upwelling longwave', 'red', 'dotted'),
                        'rlns': ('net longwave', 'red', 'dashdot'),
                        'rns':  ('net radiative flux', 'brown','solid'),
                        'hfss': ('sensible heat flux', 'green', 'dashed'),
                        'hfls': ('latent heat flux', 'green', 'dotted'),
                        'hfds': ('heat flux into ocean', 'blue', 'solid'),
                        'hfds-inferred': ('inferred heat flux into ocean', 'blue', 'dashdot'),
                        'hfsithermds' : ('heat flux from sea ice', 'blue', 'dotted')}

plot_order = ['rsds', 'rsus', 'rlds', 'rlus', 'rns', 'hfss', 'hfls', 'hfds', 'hfds-inferred', 'hfsithermds']


def get_data(filenames, var, metadata_dict, time_constraint, sftlf_cube=None, realm=None):
    """Read, merge, temporally aggregate and calculate zonal sum.
    
    Positive is defined as down.
    
    """
    
    if filenames:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load(filenames, gio.check_iris_var(var))

            metadata_dict[filenames[0]] = cube[0].attributes['history']
            equalise_attributes(cube)
            iris.util.unify_time_units(cube)
            cube = cube.concatenate_cube()
            cube = gio.check_time_units(cube)
            cube = iris.util.squeeze(cube)

            cube = cube.extract(time_constraint)
        
        coord_names = [coord.name() for coord in cube.dim_coords]
        if 'depth' in coord_names:
            depth_constraint = iris.Constraint(depth=0)
            cube = cube.extract(depth_constraint)

        cube = timeseries.convert_to_annual(cube, full_months=True)

        cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)
        cube = spatial_weights.multiply_by_area(cube) 

        if 'up' in cube.standard_name:
            cube.data = cube.data * -1

        if sftlf_cube and realm in ['ocean', 'land']:
            cube = uconv.apply_land_ocean_mask(cube, sftlf_cube, realm)

        zonal_sum = cube.collapsed('longitude', iris.analysis.SUM)
        zonal_sum.remove_coord('longitude')

        grid_spacing = grids.get_grid_spacing(zonal_sum) 
        zonal_sum.data = zonal_sum.data / grid_spacing    

    else:
        zonal_sum = None

    return zonal_sum, metadata_dict


def calc_trend_cube(cube):
    """Calculate trend and put into appropriate cube."""
    
    trend_array = timeseries.calc_trend(cube, per_yr=True)
    new_cube = cube[0,:].copy()
    new_cube.remove_coord('time')
    new_cube.data = trend_array
    
    return new_cube


def derived_radiation_fluxes(cube_dict, inargs):
    """Calculate the net shortwave, longwave and total radiation flux."""

    if inargs.rsds_files and inargs.rsus_files:
        cube_dict['rsns'] = cube_dict['rsds'] + cube_dict['rsus']   # net shortwave flux
    else:
        cube_dict['rsns'] = None
    
    if inargs.rlds_files and inargs.rlus_files:
        cube_dict['rlns'] = cube_dict['rlds'] + cube_dict['rlus']   # net longwave flux
    else:
        cube_dict['rlns'] = None

    if inargs.rsds_files and inargs.rsus_files and inargs.rlds_files and inargs.rlus_files:
        cube_dict['rns'] = cube_dict['rsns'] + cube_dict['rlns']

    return cube_dict


def infer_hfds(cube_dict, inargs):
    """Infer the downward heat flux into ocean."""
    
    hfls_data = grids.regrid_1D(cube_dict['hfls'], cube_dict['rns'], 'latitude', clear_units=False)
    hfss_data = grids.regrid_1D(cube_dict['hfss'], cube_dict['rns'], 'latitude', clear_units=False)
    data_list = [hfls_data, hfss_data, cube_dict['rns']]
    if inargs.hfsithermds_files:
         hfsithermds_data = grids.regrid_1D(cube_dict['hfsithermds'], cube_dict['rns'], 'latitude', clear_units=False)
         data_list.append(hfsithermds_data)
    else:
         hfsithermds_data = 0.0

    iris.util.unify_time_units(data_list)

    cube_dict['hfds-inferred'] = cube_dict['rns'] + hfls_data + hfss_data + hfsithermds_data
            
    return cube_dict


def climatology_plot(cube_dict, gs, plotnum):
    """Plot the climatology """
    
    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    for var in plot_order:
        if cube_dict[var]:
            climatology_cube = cube_dict[var].collapsed('time', iris.analysis.MEAN)
            label, color, style = line_characteristics[var]
            iplt.plot(climatology_cube, label=label, color=color, linestyle=style)
    ax.legend(ncol=2, loc=4)
    ax.set_xlim(-90, 90)
    ax.set_title('annual mean zonal sum')
    ax.set_ylabel('$W \: lat^{-1}$')
    

def trend_plot(cube_dict, gs, plotnum, time_bounds, guidelines=False):
    """Plot the trends"""
    
    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    for var in plot_order:
        if cube_dict[var]:
            trend_cube = calc_trend_cube(cube_dict[var])
            label, color, style = line_characteristics[var]
            iplt.plot(trend_cube, color=color, linestyle=style)
 
    start_time, end_time = time_bounds
    start_year = start_time.split('-')[0]
    end_year = end_time.split('-')[0]
    ax.set_title('trend in zonal sum, %s-%s' %(start_year, end_year)) 

    if guidelines:
        ax.axvline(-42, linestyle='dashed', color='0.5', alpha=0.5)
        ax.axvline(0, linestyle='dashed', color='0.5', alpha=0.5)
        ax.axvline(42, linestyle='dashed', color='0.5', alpha=0.5)
        ax.axvline(67, linestyle='dashed', color='0.5', alpha=0.5)

    ax.set_xlim(-90, 90)
    ax.set_ylabel('$W \: lat^{-1} \: yr^{-1}$')
    ax.set_xlabel('latitude')
    

def get_title(cube_dict, realm):
    """Get the plot title."""

    for cube in cube_dict.values():
        if cube:
            run = 'r%si%sp%s'  %(cube.attributes['realization'], cube.attributes['initialization_method'], cube.attributes['physics_version'])
            title = 'Radiation and energy budgets for global %s surface \n %s, %s, %s'  %(realm, cube.attributes['model_id'], cube.attributes['experiment'], run)
            break
    
    title = title.replace('other historical forcing', 'historicalAA')

    return title


def main(inargs):
    """Run the program."""
  
    cube_dict = {}
    metadata_dict = {}
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()    

    sftlf_cube = iris.load_cube(inargs.sftlf_file, 'land_area_fraction')

    # Radiation flux at surface
    cube_dict['rsds'], metadata_dict = get_data(inargs.rsds_files, 'surface_downwelling_shortwave_flux_in_air', metadata_dict,
                                                time_constraint, sftlf_cube=sftlf_cube, realm=inargs.plot_realm)
    cube_dict['rsus'], metadata_dict = get_data(inargs.rsus_files, 'surface_upwelling_shortwave_flux_in_air', metadata_dict,
                                                time_constraint, sftlf_cube=sftlf_cube, realm=inargs.plot_realm)
    cube_dict['rlds'], metadata_dict = get_data(inargs.rlds_files, 'surface_downwelling_longwave_flux_in_air', metadata_dict,
                                                time_constraint, sftlf_cube=sftlf_cube, realm=inargs.plot_realm)
    cube_dict['rlus'], metadata_dict = get_data(inargs.rlus_files, 'surface_upwelling_longwave_flux_in_air', metadata_dict,
                                                time_constraint, sftlf_cube=sftlf_cube, realm=inargs.plot_realm)
    cube_dict = derived_radiation_fluxes(cube_dict, inargs)
 
    # Surface energy balance
    if inargs.hfrealm == 'atmos':
        hfss_name = 'surface_upward_sensible_heat_flux'
        hfls_name = 'surface_upward_latent_heat_flux'
        cube_dict['hfss'], metadata_dict = get_data(inargs.hfss_files, hfss_name, metadata_dict, time_constraint,
                                                    sftlf_cube=sftlf_cube, realm=inargs.plot_realm)
        cube_dict['hfls'], metadata_dict = get_data(inargs.hfls_files, hfls_name, metadata_dict, time_constraint,
                                                    sftlf_cube=sftlf_cube, realm=inargs.plot_realm)
    elif inargs.hfrealm == 'ocean':
        hfss_name = 'surface_downward_sensible_heat_flux'
        hfls_name = 'surface_downward_latent_heat_flux'
        cube_dict['hfss'], metadata_dict = get_data(inargs.hfss_files, hfss_name, metadata_dict, time_constraint)
        cube_dict['hfls'], metadata_dict = get_data(inargs.hfls_files, hfls_name, metadata_dict, time_constraint)

    cube_dict['hfds'], metadata_dict = get_data(inargs.hfds_files, 'surface_downward_heat_flux_in_sea_water', metadata_dict, time_constraint)
    cube_dict['hfsithermds'], metadata_dict = get_data(inargs.hfsithermds_files,
                                                       'heat_flux_into_sea_water_due_to_sea_ice_thermodynamics',
                                                       metadata_dict, time_constraint)                           
    cube_dict = infer_hfds(cube_dict, inargs)

    # Plot
    fig = plt.figure(figsize=[12, 14])
    gs = gridspec.GridSpec(2, 1)
    climatology_plot(cube_dict, gs, 0)
    trend_plot(cube_dict, gs, 1, inargs.time, guidelines=inargs.guidelines)
        
    title = get_title(cube_dict, inargs.plot_realm)
    plt.suptitle(title)    

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot climatology and trends in surface radiative and energy fluxes'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("sftlf_file", type=str, help="Land fraction file")
    parser.add_argument("outfile", type=str, help="Output file")                                     
    
    parser.add_argument("--plot_realm", type=str, choices=('land', 'ocean', 'both'), default='ocean',
                        help="plot can be fluxes for ocean, land or both")

    parser.add_argument("--rsds_files", type=str, nargs='*', default=None,
                        help="surface downwelling shortwave flux files")
    parser.add_argument("--rsus_files", type=str, nargs='*', default=None,
                        help="surface upwelling shortwave flux files")
    parser.add_argument("--rlds_files", type=str, nargs='*', default=None,
                        help="surface downwelling longwave flux files")
    parser.add_argument("--rlus_files", type=str, nargs='*', default=None,
                        help="surface upwelling longwave flux files")

    parser.add_argument("--hfss_files", type=str, nargs='*', default=None,
                        help="surface sensible heat flux files")
    parser.add_argument("--hfls_files", type=str, nargs='*', default=None,
                        help="surface latent heat flux files")
    parser.add_argument("--hfds_files", type=str, nargs='*', default=None,
                        help="surface downward heat flux files")
    parser.add_argument("--hfsithermds_files", type=str, nargs='*', default=None,
                        help="heat flux due to sea ice files")

    parser.add_argument("--hfrealm", type=str, choices=('atmos', 'ocean'), default='atmos',
                        help="specify whether original hfss and hfls data were atmos or ocean")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1850-01-01', '2005-12-31'),
                        help="Time period [default = entire]")

    parser.add_argument("--guidelines", action="store_true", default=False,
	                help="Show boundaries of 5 panel budget plots [default=False]")

    args = parser.parse_args()             
    main(args)
