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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')



# Define functions

ocean_names = {0: 'land', 1: 'southern_ocean', 2: 'atlantic', 
               3: 'pacific', 4: 'arctic', 5: 'indian', 
               6: 'mediterranean', 7: 'black_sea', 8: 'hudson_bay',
               9: 'baltic_sea', 10: 'red_sea'}

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
    lats = uconv.broadcast_array(dcube.coord('latitude').points, [1, 2], dcube.shape)
    lons = uconv.broadcast_array(dcube.coord('longitude').points, [1, 2], dcube.shape)
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
    df['latitude'] = lat_data.filled(fill_value=5000)
    df['longitude'] = lon_data.filled(fill_value=5000)
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
    title = '%s volume distribution, %s model' %(basin, model) 

    return title


def get_labels(cube, variable_name):
    """Get the axis labels"""

    if 'temperature' in variable_name:
        var = 'temperature'
    elif 'salinity' in variable_name:
        var = 'salinity'

    units = str(cube.units)
    ylabel = '$m^3 / %s$'  %(units)
    xlabel = '%s (%s)' %(var, units)

    return xlabel, ylabel


def plot_raw(hist_dict, xvals, inargs):
    """Plot the raw volume distributions"""

    
 

def combine_infiles(infiles, inargs, time_constraint):
    """Combine multiple input files into one cube"""

    cube, history = gio.combine_files(infiles, inargs.var)
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
        dcube = combine_infiles(infiles, inargs, time_constaint)
        dcube = timeseries.convert_to_annual(dcube, full_months=True)

        voldist_timeseries = numpy.array([])
        for time_slice in dcube.slices_over('time'):
            df = create_df(dcube, inargs.variable, vcube, bcube, basin=inargs.basin)
            voldist, edges, binnum = scipy.stats.binned_statistic(df[inargs.variable].values, df['volume'].values, statistic='sum', bins=bin_edges)
            voldist_timeseries = numpy.vstack([voldist_timeseries, vt]) if voldist_timeseries.size else voldist
 
        if inargs.time_agg == 'trend':
            ntime = voldist_timeseries.shape[0]
            seconds = numpy.arange(ntime) * 60 * 60 * 24 * 365.25
            hist_dict[inargs.labels[filenum]] = numpy.apply_along_axis(linear_trend, 0, voldist_timeseries, seconds)
        elif inargs.time_agg == 'mean':
            hist_dict[inargs.labels[filenum]] = voldist_timeseries.mean(axis=0)
            
    fig = plt.figure(figsize=(10, 7))
    plt.axhline(y=0.0, color='0.5', linestyle='--')
    for plotnum, label in enumerate(inargs.labels):
        plt.plot(xvals, hist_dict[label], 'o-', color=inargs.colors[plotnum], label=label)
    title = get_title(dcube, inargs.basin) 
    plt.title(title)
    xlabel, ylabel = get_labels(dcube, inargs.variable)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc=1)

    # Save output
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    
    # Metadata
    metadata_dict = {inargs.basin_file: bcube.attributes['history'],
                     inargs.volume_file: vcube.attributes['history'],
                     dfile: dcube.attributes['history']}
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot ocean volume distribution.'
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

    parser.add_argument("--diff", action="store_true", default=False,
                        help="Plot the difference between the first data file group and all subsequent groups")

    parser.add_argument("--time_bounds", type=str, nargs=2, default=None, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    parser.add_argument("--bin_bounds", type=float, nargs=2, required=True,
                        help='bounds for the bins')

    parser.add_argument("--basin", type=str, default='globe',
                        choices=('globe', 'indian', 'north_atlantic', 'south_atlantic', 'north_pacific', 'south_pacific'),
                        help='ocean basin to plot')

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)
