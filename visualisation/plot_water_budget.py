"""
Filename:     plot_water_budget.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot climatology and trends in precipitation and evaporation  

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

line_characteristics = {'pr': ('precipitation', 'blue', 'dotted'), 
                        'evspsbl': ('evaporation', 'orange', 'dotted'),
                        'pe': ('P-E', 'green', 'solid')
                       }

plot_order = ['pr', 'evspsbl', 'pe']


def get_data(filenames, var, metadata_dict, time_constraint, area=False, invert_evap=False):
    """Read, merge, temporally aggregate and calculate zonal mean."""
    
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

        assert cube.units == 'kg m-2 s-1'
        cube.data = cube.data * 86400
        units = 'mm/day'

        if invert_evap and (var == 'water_evaporation_flux'):
            cube.data = cube.data * -1

        if area:
            cube = multiply_by_area(cube) 

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


def climatology_plot(cube_dict, gs, plotnum, area_scaled=False):
    """Plot the climatology """
    
    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    for var in plot_order:
        if cube_dict[var]:
            climatology_cube = cube_dict[var].collapsed('time', iris.analysis.MEAN)
            label, color, style = line_characteristics[var]
            iplt.plot(climatology_cube, label=label, color=color, linestyle=style)
    ax.axhline(y=0, color='0.5', linestyle='--', linewidth=0.5)
    ax.legend()
    ax.set_title('climatology')
    if area_scaled:
        ax.set_ylabel('$mm \: day^{-1} \: m^2$')
    else:
        ax.set_ylabel('$mm \: day^{-1}$')
    

def trend_plot(cube_dict, gs, plotnum, area_scaled=False):
    """Plot the trends"""
    
    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    for var in plot_order:
        if cube_dict[var]:
            trend_cube = calc_trend_cube(cube_dict[var])
            label, color, style = line_characteristics[var]
            iplt.plot(trend_cube, color=color, linestyle=style)
    ax.axhline(y=0, color='0.5', linestyle='--', linewidth=0.5)
    ax.legend()
    ax.set_title('trends')
    if area_scaled:
        ax.set_ylabel('$mm \: day^{-1} \: m^2 \: yr^{-1}$')
    else:
        ax.set_ylabel('$mm \: day^{-1} \: yr^{-1}$')
    ax.set_xlabel('latitude')
    

def get_title(cube_dict):
    """Get the plot title."""

    for cube in cube_dict.values():
        if cube:
            run = 'r%si%sp%s'  %(cube.attributes['realization'], cube.attributes['initialization_method'], cube.attributes['physics_version'])
            title = 'Surface water budget for global ocean surface \n %s, %s, %s'  %(cube.attributes['model_id'], cube.attributes['experiment'], run)
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
    cube.units = units + 'm2'

    return cube


def main(inargs):
    """Run the program."""
  
    cube_dict = {}
    metadata_dict = {}
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()    

    cube_dict['pr'], metadata_dict = get_data(inargs.pr_files, 'precipitation_flux', metadata_dict, time_constraint, area=inargs.area)
    cube_dict['evspsbl'], metadata_dict = get_data(inargs.evspsbl_files, 'water_evaporation_flux', metadata_dict, time_constraint,
                                                   area=inargs.area, invert_evap=inargs.invert_evap)
    cube_dict['pe'], metadata_dict = get_data(inargs.pe_files, 'precipitation_minus_evaporation_flux', metadata_dict, time_constraint, area=inargs.area)
                          
    fig = plt.figure(figsize=[12, 14])
    gs = gridspec.GridSpec(2, 1)
    climatology_plot(cube_dict, gs, 0, area_scaled=inargs.area)
    trend_plot(cube_dict, gs, 1, area_scaled=inargs.area)
        
    title = get_title(cube_dict)
    plt.suptitle(title)    

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot climatology and trends in precipitation and evaporation fluxes'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("outfile", type=str, help="Output file")                                     

    parser.add_argument("--pr_files", type=str, nargs='*', default=None, required=True,
                        help="precipitation flux files")
    parser.add_argument("--evspsbl_files", type=str, nargs='*', default=None, required=True,
                        help="precipitation flux files")
    parser.add_argument("--pe_files", type=str, nargs='*', default=None, required=True,
                        help="P-E flux files")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--area", action="store_true", default=False,
	                help="Multiple data by area")

    parser.add_argument("--invert_evap", action="store_true", default=False,
	                help="Multiply evap by -1")

    args = parser.parse_args()             
    main(args)
