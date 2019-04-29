"""
Filename:     plot_volume_distribution.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ocean volume distribution  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import numpy
import pandas
import matplotlib.pyplot as plt
import scipy

import iris
import cmdline_provenance as cmdprov

#import matplotlib as mpl
#mpl.rcParams['axes.labelsize'] = 'large'
#mpl.rcParams['axes.titlesize'] = 'x-large'
#mpl.rcParams['xtick.labelsize'] = 'medium'
#mpl.rcParams['ytick.labelsize'] = 'medium'
#mpl.rcParams['legend.fontsize'] = 'large'


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
    import convenient_universal as uconv
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

ocean_names = {0: 'land', 1: 'southern_ocean', 2: 'atlantic', 
               3: 'pacific', 4: 'arctic', 5: 'indian', 
               6: 'mediterranean', 7: 'black_sea', 8: 'hudson_bay',
               9: 'baltic_sea', 10: 'red_sea'}

metric_names = {'dV/dT': """volume distribution (dV/dT)""",
                'dVdT/dt': 'trend in volume distribution (dV/dT / dt)',
                'V(T)': 'volume of water colder than T (V(T))',
                'dV/dt': 'transformation rate (dV/dt)',
                'dVdt/dVdT': 'implied diabatic temperature tendency (dV/dt / dV/dT)'}

def get_ocean_name(ocean_num):
    return ocean_names[ocean_num]


def select_basin(df, basin_name):
    """Select basin"""

    if not basin_name == 'globe':
        df['basin'] = df['basin'].apply(get_ocean_name)
        basin_components = basin_name.split('_')
        if len(basin_components) == 1:
            ocean = basin_components[0]
            hemisphere = None
        else:
            hemisphere, ocean = basin_components

        df = df[(df.basin == ocean)]
        if hemisphere == 'north':
            df = df[(df.latitude > 0)]
        elif hemisphere == 'south':
            df = df[(df.latitude < 0)]

    return df


def create_df(dcube, variable_name, vcube, bcube, basin):
    """Create DataFrame"""

    if 'temperature' in variable_name:
        dcube = gio.temperature_unit_check(dcube, convert_to_celsius=True)
    elif 'salinity' in variable_name:
        dcube = gio.salinity_unit_check(dcube)

    assert dcube.ndim == 3
    coord_names = [coord.name() for coord in dcube.dim_coords]
    assert coord_names[0] == 'depth'
    
    if dcube.coord('latitude').ndim == 1:
        lat_loc = coord_names.index('latitude')
        lon_loc = coord_names.index('longitude')
    else:
        lat_loc = lon_loc = [1, 2]

    lats = uconv.broadcast_array(dcube.coord('latitude').points, lat_loc, dcube.shape)
    lons = uconv.broadcast_array(dcube.coord('longitude').points, lon_loc, dcube.shape)
    levs = uconv.broadcast_array(dcube.coord('depth').points, 0, dcube.shape)

    ddata = dcube.data.flatten()
    vdata = vcube.data.flatten()
    bdata = bcube.data.flatten()
    lat_data = lats.flatten()
    lon_data = lons.flatten()
    depth_data = levs.flatten()
   
    df = pandas.DataFrame(index=range(ddata.shape[0]))
    df[variable_name] = ddata.filled(fill_value=5000)
    df['volume'] = vdata.filled(fill_value=5000)
    df['basin'] = bdata.filled(fill_value=5000)
    df['latitude'] = lat_data
    df['longitude'] = lon_data
    df['depth'] = depth_data

    df = df[df[variable_name] != 5000]
    df = df[df[variable_name] != -273.15]

    if basin:
        df = select_basin(df, basin)

    return df


def get_title(cube, basin):
    """Get the plot title."""

    model = cube.attributes['model_id']
    basin = basin.replace('_', ' ').title()
    title = '%s, %s model' %(basin, model) 

    return title


def get_labels(cube, variable_name, metric):
    """Get the axis labels"""

    if 'temperature' in variable_name:
        var = 'temperature'
    elif 'salinity' in variable_name:
        var = 'salinity'

    units = str(cube.units)

    metric_units = {'dV/dT': '$m^3 %s^{-1}$'  %(units),
                    'dVdT/dt': '$m^3 %s^{-1} yr^{-1}$'  %(units),
                    'V(T)': '$m^3 %s^{-1}$'  %(units),
                    'dV/dt': '$m^3 %s^{-1} yr^{-1}$'  %(units),
                    'dVdt/dVdT': '$%s yr^{-1}$'  %(units)}

    ylabel = metric_units[metric]
    xlabel = '%s (%s)' %(var, units)

    return xlabel, ylabel
 

def combine_infiles(infiles, inargs, time_constraint):
    """Combine multiple input files into one cube"""

    cube, history = gio.combine_files(infiles, inargs.variable)
    atts = cube[0].attributes

    cube = cube.extract(time_constraint)
    cube = iris.util.squeeze(cube)

    log = cmdprov.new_log(infile_history={infiles[0]: history[0]}, git_repo=repo_dir)
    cube.attributes['history'] = log

    return cube


def linear_trend(data, time_axis):
    """Calculate the linear trend.

    polyfit returns [b, a] corresponding to y = a + bx
    """    

    return numpy.polyfit(time_axis, data, 1)[0]


def calc_metric(voldist_timeseries, V_timeseries, metric):
    """Calculate the chosen metric.

    dV/dT = volume distribution
    dVdT/dt = trend in volume distribution
    V(T) = volume of water colder than T
    dV/dt = transformation rate
    dVdt/dVdT = implied diabatic temperature tendency
    
    """

    ntime = voldist_timeseries.shape[0]
    years = numpy.arange(ntime)

    if metric == 'dV/dT':
        result = voldist_timeseries.mean(axis=0)
    elif metric == 'dVdT/dt':
        result = numpy.apply_along_axis(linear_trend, 0, voldist_timeseries, years)
    elif metric == 'V(T)':
        result = V_timeseries.mean(axis=0)
    elif metric == 'dV/dt':
        result = numpy.apply_along_axis(linear_trend, 0, V_timeseries, years)
    elif metric == 'dVdt/dVdT':
         dVdt = numpy.apply_along_axis(linear_trend, 0, V_timeseries, years)
         dVdT = voldist_timeseries.mean(axis=0)
         result = dVdt / dVdT

    return result
        

def set_axis_limits(ax, plotnum, xlim_list, ylim_list):
    """Adjust the default axis limits if necessary"""

    for xlim_item in xlim_list:
        upper, lower, num = xlim_item
        if num == plotnum:
            ax.set_xlim(upper, lower)
    
    for ylim_item in ylim_list:
        upper, lower, num = ylim_item
        if num == plotnum:
            ax.set_ylim(upper, lower)


def main(inargs):
    """Run the program."""

    vcube = iris.load_cube(inargs.volume_file)
    bcube = iris.load_cube(inargs.basin_file)

    bmin, bmax = inargs.bin_bounds
    bin_edges = numpy.arange(bmin, bmax + 1, 1)
    xvals = (bin_edges[1:] + bin_edges[:-1]) / 2

    time_constraint = gio.get_time_constraint(inargs.time_bounds)

    hist_dict = {}
    for groupnum, infiles in enumerate(inargs.data_files):
        dcube = combine_infiles(infiles, inargs, time_constraint)
        voldist_timeseries = numpy.array([])
        V_timeseries = numpy.array([])
        for time_slice in dcube.slices_over('time'):
            df = create_df(time_slice, inargs.variable, vcube, bcube, basin=inargs.basin)
            voldist, edges, binnum = scipy.stats.binned_statistic(df[inargs.variable].values, df['volume'].values, statistic='sum', bins=bin_edges)
            V = voldist.cumsum()
            voldist_timeseries = numpy.vstack([voldist_timeseries, voldist]) if voldist_timeseries.size else voldist
            V_timeseries = numpy.vstack([V_timeseries, V]) if V_timeseries.size else V
        for metric in inargs.metrics:
            hist_dict[(inargs.labels[groupnum], metric)] = calc_metric(voldist_timeseries, V_timeseries, metric)
    
    nrows, ncols = inargs.subplot_config
    fig, axes = plt.subplots(nrows, ncols, figsize=(9*ncols, 6*nrows))
    for plotnum, metric in enumerate(inargs.metrics):
        ax = axes.flatten()[plotnum] if type(axes) == numpy.ndarray else axes
        ax.axhline(y=0.0, color='0.5', linestyle='--')
        for labelnum, label in enumerate(inargs.labels):
            ax.plot(xvals, hist_dict[(label, metric)], 'o-', color=inargs.colors[labelnum], label=label) 
        ax.set_title(metric_names[metric])
        xlabel, ylabel = get_labels(time_slice, inargs.variable, metric)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        set_axis_limits(ax, plotnum, inargs.xlim, inargs.ylim)
        ax.legend(loc=1)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
        ax.yaxis.major.formatter._useMathText = True
    title = get_title(dcube, inargs.basin)
    plt.suptitle(title)

    # Save output
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    
    # Metadata
    metadata_dict = {inargs.basin_file: bcube.attributes['history'],
                     inargs.volume_file: vcube.attributes['history'],
                     infiles[0]: dcube.attributes['history']}
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot ocean volume distribution. Assumes annual timescale input data.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("variable", type=str, help="Variable name")
    parser.add_argument("volume_file", type=str, help="Volume file name")
    parser.add_argument("basin_file", type=str, help="Basin file name")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--data_files", nargs='*', type=str, action='append',
                        help="Data files for a particular grouping (e.g. a particular variable/experiment)")

    parser.add_argument("--colors", nargs='*', type=str,
                        help="Color for data files group")
    parser.add_argument("--labels", nargs='*', type=str, required=True, 
                        help="Label for each data files group")

    parser.add_argument("--time_bounds", type=str, nargs=2, default=None, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    parser.add_argument("--bin_bounds", type=float, nargs=2, required=True,
                        help='bounds for the bins')

    parser.add_argument("--xlim", type=float, nargs=3, action='append', default=[],
                        help='lower_limit, upper_limit, plot_index')
    parser.add_argument("--ylim", type=float, nargs=3, action='append', default=[],
                        help='lower_limit, upper_limit, plot_index')

    parser.add_argument("--metrics", type=str, nargs='*', required=True,
                        choices=('dV/dT', 'dVdT/dt', 'V(T)', 'dV/dt', 'dVdt/dVdT'), help='Metrics to plot')
    parser.add_argument("--subplot_config", type=int, nargs=2, default=(1, 1), metavar=('nrows', 'ncols'),
                        help="Subplot configuration (nrows, ncols) [default = (1, 1)]")

    parser.add_argument("--basin", type=str, default='globe',
                        choices=('globe', 'indian', 'north_atlantic', 'south_atlantic', 'north_pacific', 'south_pacific'),
                        help='ocean basin to plot')

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()      
    assert len(args.metrics) <= args.subplot_config[0] * args.subplot_config[1]       
    main(args)
