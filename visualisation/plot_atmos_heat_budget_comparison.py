"""
Filename:     plot_atmos_heat_budget_comparison.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot trends in surface radiative and energy fluxes for two experiments 

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

line_characteristics = {'rnds': ('net downward radiative flux', 'black', 'solid'), 
                        'hfss': ('sensible heat flux', 'red', 'solid'),
                        'hfls': ('latent heat flux', 'orange', 'solid'),
                        'hfds': ('heat flux into ocean', 'blue', 'solid'),
                        'hfds-inferred': ('inferred heat flux into ocean', 'blue', 'dashed')}

plot_order = ['rnds', 'hfss', 'hfls', 'hfds', 'hfds-inferred']


def create_land_ocean_mask(mask_cube, target_shape, include_only):
    """Create a land or ocean mask from an sftlf (land surface fraction) file.
    There is no land when cell value == 0
    """

    target_ndim = len(target_shape)

    if include_only == 'land':
        mask_array = numpy.where(mask_cube.data > 50, False, True)
    elif include_only == 'ocean':
        mask_array = numpy.where(mask_cube.data < 50, False, True)

    mask = uconv.broadcast_array(mask_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    return mask


def get_data(filenames, var, metadata_dict, time_constraint, sftlf_cube=None):
    """Read, merge, temporally aggregate and calculate zonal sum."""
    
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

        cube = timeseries.convert_to_annual(cube, full_months=True)
        cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)
        cube = multiply_by_area(cube) 
        
        if sftlf_cube:
            mask = create_land_ocean_mask(sftlf_cube, cube.shape, 'ocean')
            cube.data = numpy.ma.asarray(cube.data)
            cube.data.mask = mask

        zonal_sum = cube.collapsed('longitude', iris.analysis.SUM)
        zonal_sum.remove_coord('longitude')

        grid_spacing = numpy.diff(zonal_sum.coord('latitude').points) 
        mean_grid_spacing = grid_spacing.mean()
        assert numpy.abs(grid_spacing - mean_grid_spacing).max() < 0.1, "Grid must be equally spaced" 
        zonal_sum.data = zonal_sum.data / mean_grid_spacing        

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
    """Calculate the net radiation flux."""

    if inargs.rsds_files and inargs.rsus_files and inargs.rlds_files and inargs.rlus_files:
        cube_dict['rnds'] = cube_dict['rsds'] - cube_dict['rsus'] + cube_dict['rlds'] - cube_dict['rlus']
    else:
        cube_dict['rnds'] = None

    return cube_dict


def infer_hfds(cube_dict):
    """Infer the downward heat flux into ocean."""

    cube_dict['hfds-inferred'] = cube_dict['rnds'] - cube_dict['hfss'] - cube_dict['hfls']

    return cube_dict


def raw_trend_plot(cube_dict, gs, plotnum, time_bounds):
    """Plot the trends"""
    
    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    for var in plot_order:
        if cube_dict[var]:
            trend_cube = calc_trend_cube(cube_dict[var])
            label, color, style = line_characteristics[var]
            iplt.plot(trend_cube, color=color, linestyle=style, label=label)
 
    ax.set_xlim(-90, 90)
    ax.legend(ncol=2)
    ax.set_ylabel('$W \: lat^{-1} \: yr^{-1}$')
    ax.set_xlabel('latitude')

    start_time, end_time = time_bounds
    start_year = start_time.split('-')[0]
    end_year = end_time.split('-')[0]
    ax.set_title('Trend in zonal sum, %s-%s'  %(start_year, end_year))    

    
def get_title(cube_dict):
    """Get the plot title."""

    for cube in cube_dict.values():
        if cube:
            run = 'r%si%sp%s'  %(cube.attributes['realization'], cube.attributes['initialization_method'], cube.attributes['physics_version'])
            title = 'Radiation and energy budgets for global ocean surface \n %s, %s, %s'  %(cube.attributes['model_id'], cube.attributes['experiment'], run)
            break
    
    return title


def multiply_by_area(cube):
    """Multiply by cell area."""

    if not cube.coord('latitude').has_bounds():
        cube.coord('latitude').guess_bounds()
    if not cube.coord('longitude').has_bounds():
        cube.coord('longitude').guess_bounds()
    area_weights = iris.analysis.cartography.area_weights(cube)

    units = str(cube.units)
    cube.data = cube.data * area_weights   
    cube.units = units.replace('m-2', '')

    return cube


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
    cube_dict['rsds'], metadata_dict = get_data(inargs.rsds_files, 'surface_downwelling_shortwave_flux_in_air', metadata_dict, time_constraint, sftlf_cube=sftlf_cube)
    cube_dict['rsus'], metadata_dict = get_data(inargs.rsus_files, 'surface_upwelling_shortwave_flux_in_air', metadata_dict, time_constraint, sftlf_cube=sftlf_cube)
    cube_dict['rlds'], metadata_dict = get_data(inargs.rlds_files, 'surface_downwelling_longwave_flux_in_air', metadata_dict, time_constraint, sftlf_cube=sftlf_cube)
    cube_dict['rlus'], metadata_dict = get_data(inargs.rlus_files, 'surface_upwelling_longwave_flux_in_air', metadata_dict, time_constraint, sftlf_cube=sftlf_cube)
    cube_dict = derived_radiation_fluxes(cube_dict, inargs)
 
    # Surface energy balance
    if inargs.hfrealm == 'atmos':
        hfss_name = 'surface_upward_sensible_heat_flux'
        hfls_name = 'surface_upward_latent_heat_flux'
        cube_dict['hfss'], metadata_dict = get_data(inargs.hfss_files, hfss_name, metadata_dict, time_constraint, sftlf_cube=sftlf_cube)
        cube_dict['hfls'], metadata_dict = get_data(inargs.hfls_files, hfls_name, metadata_dict, time_constraint, sftlf_cube=sftlf_cube)
        cube_dict = infer_hfds(cube_dict) 
    elif inargs.hfrealm == 'ocean':
        hfss_name = 'surface_downward_sensible_heat_flux'
        hfls_name = 'surface_downward_latent_heat_flux'
        cube_dict['hfss'], metadata_dict = get_data(inargs.hfss_files, hfss_name, metadata_dict, time_constraint)
        cube_dict['hfls'], metadata_dict = get_data(inargs.hfls_files, hfls_name, metadata_dict, time_constraint)

    cube_dict['hfds'], metadata_dict = get_data(inargs.hfds_files, 'surface_downward_heat_flux_in_sea_water', metadata_dict, time_constraint)
                          
    # Plot
    fig = plt.figure(figsize=[12, 14])
    gs = gridspec.GridSpec(2, 1)
    raw_trend_plot(cube_dict, gs, 0, inargs.time)
    #percentage_trend_plot(cube_dict, gs, 1)
        
    title = get_title(cube_dict)
    plt.suptitle(title)    

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot trends in surface radiative and energy fluxes for two experiments'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("sftlf_file", type=str, help="Land fraction file")
    parser.add_argument("outfile", type=str, help="Output file")                                     

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

    parser.add_argument("--hfrealm", type=str, choices=('atmos', 'ocean'), default='atmos',
                        help="specify whether original hfss and hfls data were atmos or ocean")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1850-01-01', '2005-12-31'),
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
