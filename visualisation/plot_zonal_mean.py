"""
Filename:     plot_zonal_mean.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import matplotlib.pyplot as plt
from matplotlib import gridspec
import iris
import iris.plot as iplt
from iris.experimental.equalise_cubes import equalise_attributes
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_colors = {}
experiment_colors['historical'] = 'green'
experiment_colors['piControl'] = 'black'
experiment_colors['historicalAA'] = 'blue'
experiment_colors['historicalGHG'] = 'red'
experiment_colors['historicalnoAA'] = 'orange'
               

def scale_data(cube, var):
    """Scale data"""

    if var == 'precipitation_minus_evaporation_flux':
        cube.data = cube.data * 86400
        units = 'mm/day'
    else:
        units = cube.units

    return cube, units


def set_plot_grid(tas_trend=False):
    """Set the grid of plots.
    
    Args:
      tas_trend (bool): Include a panel for the tas trend?
    
    """
    
    if tas_trend:
        nrows = 4
        heights = [3, 1, 1, 1]
    else:
        nrows = 3
        heights = [3, 1, 1]
        
    gs = gridspec.GridSpec(nrows, 1, height_ratios=heights)

    return gs


def calculate_climatology(cube, time_bounds, experiment):
    """Calculate annual mean climatology"""
    
    if not experiment == 'piControl':
        time_constraint = gio.get_time_constraint(time_bounds)
        cube = cube.extract(time_constraint) 
        
    cube = cube.collapsed('time', iris.analysis.MEAN)
    cube.remove_coord('time')

    return cube


def calc_linear_trend(data, xaxis):
    """Calculate the linear trend.
    polyfit returns [a, b] corresponding to y = a + bx
    """    

    if data.mask[0]:
        return data.fill_value
    else:    
        return numpy.polynomial.polynomial.polyfit(xaxis, data, 1)[-1]


def get_trend_cube(cube, xaxis='time'):
    """Get the trend data.
    Args:
      cube (iris.cube.Cube)
      xaxis (iris.cube.Cube)
    """

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names[0] == 'time'

    if xaxis == 'time':
        trend_data = timeseries.calc_trend(cube, per_yr=True)
        trend_unit = ' yr-1'
    else:
        trend_data = numpy.ma.apply_along_axis(calc_linear_trend, 0, cube.data, xaxis.data)
        trend_data = numpy.ma.masked_values(trend_data, cube.data.fill_value)
        trend_unit = ' '+str(xaxis.units)+'-1'

    trend_cube = cube[0, ::].copy()
    trend_cube.data = trend_data
    trend_cube.remove_coord('time')
    trend_cube.units = str(cube.units) + trend_unit

    return trend_cube

def plot_climatology(climatology_dict, var, model, run, units, legloc):
    """Plot the zonal mean climatology"""
    
    for experiment in ['historical', 'historicalGHG', 'historicalAA', 'historicalnoAA', 'piControl']:
        if climatology_dict[experiment]:
            color = experiment_colors[experiment]
            iplt.plot(climatology_dict[experiment], color=color, alpha=0.8, label=experiment)

    plt.legend(loc=legloc)
    plt.ylabel('Zonal mean %s (%s)' %(var.replace('_', ' '), units) )
    plt.title('%s (%s)' %(model, run.replace('_', ' ')))


def check_lats(climatology_dict, experiment):
    """Sometimes the latitude axes are not exactly equal after regridding."""

    experiment_lats = climatology_dict[experiment].coord('latitude')
    control_lats = climatology_dict['piControl'].coord('latitude')
    if not control_lats == experiment_lats:
        diffs = experiment_lats.points - control_lats.points
        assert numpy.abs(diffs).max() < 0.0001, "%s and control have very different latitude axes" %(experiment) 
        climatology_dict[experiment].coord('latitude').points = control_lats.points
        climatology_dict[experiment].coord('latitude').bounds = control_lats.bounds
        assert climatology_dict[experiment].coord('latitude') == climatology_dict['piControl'].coord('latitude'), \
        "Problem with %s latitude axis" %(experiment)

    return climatology_dict[experiment]


def plot_difference(climatology_dict):
    """Plot the difference between experiment and control climatology"""
    
    assert climatology_dict['piControl'], 'must have control data for difference plot'
    
    for experiment in ['historical', 'historicalGHG', 'historicalAA', 'historicalnoAA']:
        if climatology_dict[experiment]:
            climatology_dict[experiment] = check_lats(climatology_dict, experiment)
            diff_cube = climatology_dict[experiment] - climatology_dict['piControl']
            iplt.plot(diff_cube, color=experiment_colors[experiment], alpha=0.8)

    plt.ylabel('Experiment - piControl')


def plot_trend(trend_dict, xaxis='time'):
    """Plot the trend"""

    for experiment in ['historical', 'historicalGHG', 'historicalAA', 'historicalnoAA']:
        if trend_dict[experiment]:    
            iplt.plot(trend_dict[experiment], color=experiment_colors[experiment], alpha=0.8)

    if xaxis == 'time':
        plt.ylabel('Trend ($K \enspace yr^{-1}$)')
    elif xaxis == 'tas':
        plt.ylabel('Trend ($K \enspace K^{-1}$)')


def main(inargs):
    """Run the program."""

    # Read the data

    file_dict = {'historical': inargs.historical_files,
                 'historicalGHG': inargs.historicalghg_files,
                 'historicalAA': inargs.historicalaa_files,
                 'historicalnoAA': inargs.historicalaa_files,
                 'piControl': inargs.picontrol_files}
    
    tas_dict = {'historical': inargs.historical_tas_file,
                'historicalGHG': inargs.historicalghg_tas_file,
                'historicalAA': inargs.historicalaa_tas_file,
                'historicalnoAA': inargs.historicalnoaa_tas_file,
                'piControl': None}
    
    metadata_dict = {}
    climatology_dict = {}
    time_trend_dict = {}
    tas_trend_dict = {}
    experiments = file_dict.keys()
    for experiment in experiments:
        filenames = file_dict[experiment]
        if not filenames:
            climatology_dict[experiment] = None
            time_trend_dict[experiment] = None
            tas_trend_dict[experiment] = None
        else:
            with iris.FUTURE.context(cell_datetime_objects=True):
                cube = iris.load(filenames, gio.check_iris_var(inargs.var))

                metadata_dict[filenames[0]] = cube[0].attributes['history']
                equalise_attributes(cube)
                cube = cube.concatenate_cube()
                cube, units = scale_data(cube, inargs.var)

                cube = timeseries.convert_to_annual(cube)
                cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)

                zonal_mean_cube = cube.collapsed('longitude', iris.analysis.MEAN)
                zonal_mean_cube.remove_coord('longitude')

                climatology_dict[experiment] = calculate_climatology(zonal_mean_cube, inargs.time, experiment)
                time_trend_dict[experiment] = get_trend_cube(zonal_mean_cube)
                if tas_dict[experiment]:
                    tas_cube = iris.load_cube(tas_dict[experiment], 'air_temperature')
                    tas_trend_dict[experiment] = get_trend_cube(zonal_mean_cube, xaxis=tas_cube)
                    metadata_dict[tas_dict[experiment]] = tas_cube.attributes['history']
                else:
                    tas_trend_dict[experiment] = None
        
    # Create the plots
    
    tas_trend_flag = tas_trend_dict['historicalGHG'] and tas_trend_dict['historicalAA']
    
    fig = plt.figure(figsize=[10, 10])
    gs = set_plot_grid(tas_trend=tas_trend_flag)
    
    ax_main = plt.subplot(gs[0])
    plt.sca(ax_main)
    plot_climatology(climatology_dict, inargs.var, inargs.model, inargs.run, units, inargs.legloc)
    
    ax_diff = plt.subplot(gs[1])
    plt.sca(ax_diff)
    plot_difference(climatology_dict)
    
    ax_time_trend = plt.subplot(gs[2])
    plt.sca(ax_time_trend)
    plot_trend(time_trend_dict, xaxis='time')

    if tas_trend_flag:
        ax_tas_trend = plt.subplot(gs[3])
        plt.sca(ax_tas_trend)
        plot_trend(tas_trend_dict, xaxis='tas')
    
    plt.xlabel('latitude')
        
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com

note:
   
"""

    description=''
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("model", type=str, help="Model name")
    parser.add_argument("run", type=str, help="Run (e.g. r1)")
    
    parser.add_argument("--historical_files", type=str, default=None, nargs='*',
                        help="Input files for the historical experiment")
    parser.add_argument("--historicalghg_files", type=str, default=None, nargs='*',
                        help="Input files for the historicalGHG experiment")
    parser.add_argument("--historicalaa_files", type=str, default=None, nargs='*',
                        help="Input files for the historicalAA experiment")
    parser.add_argument("--historicalnoaa_files", type=str, default=None, nargs='*',
                        help="Input files for the historicalnoAA experiment")
    parser.add_argument("--picontrol_files", type=str, default=None, nargs='*',
                        help="Input files for the piControl experiment")

    parser.add_argument("--historical_tas_file", type=str, default=None,
                        help="Global mean surface temperature file for historical experiment")
    parser.add_argument("--historicalghg_tas_file", type=str, default=None,
                        help="Global mean surface temperature file for historicalGHG experiment")
    parser.add_argument("--historicalaa_tas_file", type=str, default=None,
                        help="Global mean surface temperature file for historicalAA experiment")
    parser.add_argument("--historicalnoaa_tas_file", type=str, default=None,
                        help="Global mean surface temperature file for historicalAA experiment")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1986-01-01', '2005-12-31'), help="Time period for climatology [default = entire]")

    parser.add_argument("--legloc", type=int, default=8,
                        help="Legend location")
    
    args = parser.parse_args()            
    main(args)
