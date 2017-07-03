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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

line_styles = {'rsds': 'dashed', 'rsus': 'dotted', 'rsns': 'dashdot',
               'rlds': 'dashed', 'rlus': 'dotted', 'rlns': 'dashdot',
               'rns': 'solid',
               'hfss': 'dashed', 'hfls': 'dotted', 'hfds': 'dashdot', 'hfns': 'solid'
              }

line_colors = {'rs': 'orange',
               'rl': 'red',
               'rn': 'brown',
               'hf': 'blue'}

labels = {'rsds': 'downwelling shortwave',
          'rsus': 'upwelling shortwave',
          'rsns': 'net shortwave',
          'rlds': 'downwelling longwave',
          'rlus': 'upwelling longwave',
          'rlns': 'net longwave',
          'rns': 'net radiative flux',
          'hfss': 'sensible heat flux',
          'hfls': 'latent heat flux',
          'hfds': 'heat flux into ocean',
          'hfns': 'net heat flux'
         }

plot_order = ['rsds', 'rsus', 'rsns', 'rlds', 'rlus', 'rlns', 'rns', 'hfss', 'hfls', 'hfds', 'hfns']


def get_data(filenames, var, metadata_dict):
    """Read, merge, temporally aggregate and calculate zonal mean.
    
    Positive is defined as down.
    
    """
    
    if filenames:
        cube = iris.load(filenames, gio.check_iris_var(var))

        metadata_dict[filenames[0]] = cube[0].attributes['history']
        equalise_attributes(cube)
        iris.util.unify_time_units(cube)
        cube = cube.concatenate_cube()
        cube = gio.check_time_units(cube)

        cube = timeseries.convert_to_annual(cube, full_months=True)

        if 'up' in cube.standard_name:
            cube.data = cube.data * -1

        cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)
        zonal_mean = cube.collapsed('longitude', iris.analysis.MEAN)
        zonal_mean.remove_coord('longitude')
    else:
        zonal_mean = None

    return zonal_mean, metadata_dict


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


def derived_energy_terms(cube_dict, inargs):
    """Calculate the net energy balance.
    
    FIXME: This could possibly calculate hfsithermds too
    
    """
    
    if inargs.hfss_files and inargs.hfls_files and inargs.hfds_files:
        cube_dict['hfns'] = cube_dict['hfss'] + cube_dict['hfls'] + cube_dict['hfds']
    else:
        cube_dict['hfns'] = None
    
    return cube_dict


def climatology_plot(cube_dict, gs, plotnum):
    """Plot the climatology """
    
    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    for var in plot_order:
        if cube_dict[var]:
            climatology_cube = cube_dict[var].collapsed('time', iris.analysis.MEAN)
            iplt.plot(climatology_cube, label=labels[var],
                      color=line_colors[var[0:2]],
                      linestyle=line_styles[var])
    ax.legend()
    ax.set_title('climatology')
    ax.set_ylabel('$W m^{-2}$')
    

def trend_plot(cube_dict, gs, plotnum):
    """Plot the trends """
    
    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    for var in plot_order:
        if cube_dict[var]:
            trend_cube = calc_trend_cube(cube_dict[var])
            iplt.plot(trend_cube,
                      color=line_colors[var[0:2]],
                      linestyle=line_styles[var])
    ax.set_title('trends')
    ax.set_ylabel('$W m^{-2} yr^{-1}$')
    ax.set_xlabel('latitude')
    

def get_title(cube_dict):
    """Get the plot title."""

    for cube in cube_dict.values():
        if cube:
            run = 'r%si%sp%s'  %(cube.attributes['realization'], cube.attributes['initialization_method'], cube.attributes['physics_version'])
            title = '%s, %s, %s'  %(cube.attributes['model_id'], cube.attributes['experiment'], run)
            break
    
    return title


def main(inargs):
    """Run the program."""
  
    cube_dict = {}
    metadata_dict = {}
    
    # Radiation flux at surface
    cube_dict['rsds'], metadata_dict = get_data(inargs.rsds_files, 'surface_downwelling_shortwave_flux_in_air', metadata_dict)
    cube_dict['rsus'], metadata_dict = get_data(inargs.rsus_files, 'surface_upwelling_shortwave_flux_in_air', metadata_dict)
    cube_dict['rlds'], metadata_dict = get_data(inargs.rlds_files, 'surface_downwelling_longwave_flux_in_air', metadata_dict)
    cube_dict['rlus'], metadata_dict = get_data(inargs.rlus_files, 'surface_upwelling_longwave_flux_in_air', metadata_dict)
    cube_dict = derived_radiation_fluxes(cube_dict, inargs)
 
    # Surface energy balance
    cube_dict['hfss'], metadata_dict = get_data(inargs.hfss_files, 'surface_upward_sensible_heat_flux', metadata_dict)
    cube_dict['hfls'], metadata_dict = get_data(inargs.hfls_files, 'surface_upward_latent_heat_flux', metadata_dict)
    cube_dict['hfds'], metadata_dict = get_data(inargs.hfds_files, 'surface_downward_heat_flux_in_sea_water', metadata_dict)
    cube_dict = derived_energy_terms(cube_dict, inargs)

    # Plot
    fig = plt.figure(figsize=[10, 14])
    gs = gridspec.GridSpec(2, 1)
    climatology_plot(cube_dict, gs, 0)
    trend_plot(cube_dict, gs, 1)
        
    title = get_title(cube_dict)
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
                        help="surface upward sensible heat flux files")
    parser.add_argument("--hfls_files", type=str, nargs='*', default=None,
                        help="surface upward latent heat flux files")
    parser.add_argument("--hfds_files", type=str, nargs='*', default=None,
                        help="surface downward heat flux files")
    ## FIXME: hfsithermds (heat flux into sea water due to sea ice thermdynamics) file

    parser.add_argument("--legloc", type=int, default=2,
                        help="Legend location")

    args = parser.parse_args()             
    main(args)
