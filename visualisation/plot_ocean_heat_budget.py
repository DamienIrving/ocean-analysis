"""
Filename:     plot_ocean_heat_budget.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot climatology and trend in ocean heat transport convergence, surface heat flux and ocean heat content

Input:        List of netCDF files to plot
Output:       An image in either bitmap (e.g. .png) or vector (e.g. .svg, .eps) format

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_y_axis_name(cube, verbose=False):
    """Get the name of the y axis.
 
    Verbose gives var_name, standard_name and long_name

    """

    dim_coord_names = [coord.name() for coord in cube.dim_coords]
    y_axis_name = dim_coord_names[-1]
  
    if verbose:
        var_name = cube.coord(y_axis_name).var_name
        long_name = cube.coord(y_axis_name).long_name
        standard_name = cube.coord(y_axis_name).standard_name
        return y_axis_name, var_name, long_name, standard_name
    else:
        return y_axis_name


def calc_trend_cube(cube):
    """Calculate and trend and put into appropriate cube."""
    
    trend_array = timeseries.calc_trend(cube, per_yr=True)
    new_cube = cube[0,:].copy()
    new_cube.remove_coord('time')
    new_cube.data = trend_array
    
    return new_cube


def estimate_ohc_tendency(data, time_axis):
    """Estimate the OHC tendency by taking derivative of fitted polynomial.

    polyfit returns [c, b, a] corresponding to y = a + bx + cx^2
    
    """    

    if data.mask[0]:
        new_data = data
    else:
        coef_c, coef_b, coef_a = numpy.ma.polyfit(time_axis, data, 2)
        new_data = coef_b + 2 * coef_c * time_axis

    return new_data


def get_ohc_data(ohc_file, metadata_dict):
    """Read ocean heat content data and calculate trend in mean and tendency.
    
    Input units: J
    Output units: W s-1
    
    """

    if ohc_file:
        long_name = 'zonal sum ocean heat content globe'
        ohc_cube = iris.load_cube(ohc_file, long_name)
        metadata_dict[ohc_file] = ohc_cube.attributes['history']

        # OHC tendency trend
        time_axis = timeseries.convert_to_seconds(ohc_cube.coord('time'))
        ohc_tendency_data = numpy.ma.apply_along_axis(estimate_ohc_tendency, 0, ohc_cube.data, time_axis.points)
        ohc_tendency_data = numpy.ma.masked_values(ohc_tendency_data, ohc_cube.data.fill_value)

        ohc_tendency_cube = ohc_cube.copy()
        ohc_tendency_cube.data = ohc_tendency_data

        ohc_tendency_trend_cube = calc_trend_cube(ohc_tendency_cube)
        ohc_tendency_trend_cube.attributes = ohc_cube.attributes
    
        # OHC trend
        ohc_trend_cube = calc_trend_cube(ohc_cube / (60 * 60 * 24 * 365.25))  # units go from J to W, then calculate trend
        ohc_trend_cube.attributes = ohc_cube.attributes
    else:
        ohc_tendency_trend_cube = None
        ohc_trend_cube = None

    return ohc_tendency_trend_cube, ohc_trend_cube, metadata_dict


def get_hfds_data(hfds_file, metadata_dict, rolling_window=None):
    """Read surface heat flux data and calculate mean and trend.
    
    Input units: W
    Output units: W s-1
    
    """
    
    if hfds_file:
        long_name = 'zonal sum surface downward heat flux in sea water globe'
        hfds_cube = iris.load_cube(hfds_file, long_name)
        metadata_dict[hfds_file] = hfds_cube.attributes['history']

        if rolling_window:
            y_axis_name = get_y_axis_name(hfds_cube)
            hfds_cube = hfds_cube.rolling_window(y_axis_name, iris.analysis.MEAN, rolling_window)

        hfds_trend = calc_trend_cube(hfds_cube)
        hfds_mean = hfds_cube.collapsed('time', iris.analysis.MEAN)    
    else:
        hfds_trend = None
        hfds_mean = None

    return hfds_trend, hfds_mean, metadata_dict


def get_htc_data(htc_file, metadata_dict, rolling_window=None):
    """Read ocean heat transport convergence data and calculate mean and trend.
    
    A hfbasin-convengence or hfy-convergence file is expected.
    
    Input: units = W, timescale = monhtly
    Output: units = W s-1, timescale = annual
    
    """
    
    if htc_file:
        if 'hfy' in htc_file:
            htc_cube = iris.load_cube(htc_file, 'zonal sum ocean heat y transport convergence globe')
        else:
            htc_cube = iris.load_cube(htc_file)
        metadata_dict[htc_file] = htc_cube.attributes['history']

        htc_cube = timeseries.convert_to_annual(htc_cube)
        if rolling_window:
            y_axis_name = get_y_axis_name(htc_cube)
            htc_cube = htc_cube.rolling_window(y_axis_name, iris.analysis.MEAN, rolling_window)

        htc_trend = calc_trend_cube(htc_cube)
        htc_mean = htc_cube.collapsed('time', iris.analysis.MEAN)

        htc_trend.attributes = htc_cube.attributes
        htc_mean.atributes = htc_cube.attributes
    else:
        htc_trend = None
        htc_mean = None
    
    return htc_trend, htc_mean, metadata_dict


def plot_inferred_data(primary_data, secondary_data, y_axis_name, y_var_name, y_standard_name, y_long_name, quantity):
    """Plot the inferred data.

    inferred = primary + secondary (for quantity = OHC)
    OR
    inferred = primary - secondary (for HTC and SFL)

    """

    primary_data.coord(y_axis_name).var_name = y_var_name
    primary_data.coord(y_axis_name).standard_name = y_standard_name
    primary_data.coord(y_axis_name).long_name = y_long_name
    primary_data.units= ''
    regridded_secondary_data = grids.regrid_1D(secondary_data, primary_data, y_axis_name, clear_units=True)

    if 'OHC' in quantity:       
        label = 'inferred ' + quantity + ' (= HTC + SFL)'
        iplt.plot(primary_data + regridded_secondary_data, label=label, color='black', linestyle='--')  
    elif 'HTC' in quantity:       
        label = 'inferred ' + quantity + ' (= OHC - SFL)'
        iplt.plot(primary_data - regridded_secondary_data, label=label, color='green', linestyle='--')
    elif 'SFL' in quantity:
        label = 'inferred ' + quantity + ' (= OHC - HTC)'
        iplt.plot(primary_data - regridded_secondary_data, label=label, color='orange', linestyle='--')


def plot_data(htc_data, hfds_data, ohc_data, inargs, gs, plotnum, plot_type, infer_list):
    """Plot trends."""

    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    if plot_type == 'trends':
        htc_label = 'trend in heat transport convergence (HTC)'
        hfds_label = 'trend in surface heat flux (SFL)'
        ohc_label = 'trend in ocean heat content tendency (OHC)'
        y_label = 'Trend ($W yr^{-1}$)'
    else:
        htc_label = 'average annual mean heat transport convergence (HTC)'
        hfds_label = 'average annual mean surface heat flux (SFL)'
        ohc_label = 'trend in ocean heat content (OHC)'
        y_label = '$W$ (or $W yr^{-1}$ for OHC trend)'

    if htc_data:
        iplt.plot(htc_data, label=htc_label, color='green')
        y_axis_name, y_var_name, y_long_name, y_standard_name = get_y_axis_name(htc_data, verbose=True) 
    if hfds_data:
        iplt.plot(hfds_data, label=hfds_label, color='orange') 
        y_axis_name, y_var_name, y_long_name, y_standard_name = get_y_axis_name(hfds_data, verbose=True) 
    if ohc_data:
        iplt.plot(ohc_data, label=ohc_label, color='black')
        y_axis_name, y_var_name, y_long_name, y_standard_name = get_y_axis_name(ohc_data, verbose=True) 

    if 'OHC' in infer_list:
        plot_inferred_data(hfds_data, htc_data, y_axis_name, y_var_name, y_standard_name, y_long_name, quantity=ohc_label)
    if 'HTC' in infer_list:
        plot_inferred_data(ohc_data, hfds_data, y_axis_name, y_var_name, y_standard_name, y_long_name, quantity=htc_label)
    if 'SFL' in infer_list:
        plot_inferred_data(ohc_data, htc_data, y_axis_name, y_var_name, y_standard_name, y_long_name, quantity=hfds_label)
      
    if inargs.nummelin:
        color = '0.7'
        width = 0.5
        plt.axhline(y=0, linestyle='--', color=color, linewidth=width)
        plt.axvline(x=30, color=color, linewidth=width)
        plt.axvline(x=50, color=color, linewidth=width)
        plt.axvline(x=77, color=color, linewidth=width)
        plt.xlim(20, 90)

    if inargs.ylim:
        ymin, ymax = inargs.ylim
        plt.ylim(ymin, ymax)

    plt.legend(loc=inargs.legloc)
    plt.xlabel(y_axis_name)
    plt.ylabel(y_label)
    plt.title(plot_type)


def get_title(htc_cube, hfds_cube, ohc_cube):
    """Get the plot title."""

    for cube in [htc_cube, hfds_cube, ohc_cube]:
        if cube:
            run = 'r%si%sp%s'  %(cube.attributes['realization'], cube.attributes['initialization_method'], cube.attributes['physics_version'])
            title = '%s, %s, %s'  %(cube.attributes['model_id'], cube.attributes['experiment'], run)
            break
    
    return title


def select_inferred_plots(user_selection, htc_cube, hfds_cube, ohc_cube):
    """Determine which inferred curves to plot."""

    if user_selection == 'withhold':
        infer_list = []
    elif user_selection:
        infer_list = user_selection
    else:
        infer_list = []
        if (htc_cube and hfds_cube):
            infer_list.append('OHC')
        if (ohc_cube and hfds_cube) and not htc_cube:
            infer_list.append('HTC')
        if (ohc_cube and htc_cube) and not hfds_cube:
            infer_list.append('SFL')

    return infer_list
    

def main(inargs):
    """Run the program."""
  
    metadata_dict = {}
   
    fig = plt.figure(figsize=[10, 14])
    gs = gridspec.GridSpec(2, 1)

    htc_trend, htc_mean, metadata_dict = get_htc_data(inargs.htc_file, metadata_dict, rolling_window=inargs.rolling_window)
    hfds_trend, hfds_mean, metadata_dict = get_hfds_data(inargs.hfds_file, metadata_dict, rolling_window=inargs.rolling_window)  
    ohc_tendency_trend, ohc_trend, metadata_dict = get_ohc_data(inargs.ohc_file, metadata_dict)  
  
    infer_list = select_inferred_plots(inargs.infer, htc_trend, hfds_trend, ohc_tendency_trend)

    plot_data(htc_mean, hfds_mean, ohc_trend, inargs, gs, 0, 'mean', infer_list)
    plot_data(htc_trend, hfds_trend, ohc_tendency_trend, inargs, gs, 1, 'trends', infer_list)

    title = get_title(htc_trend, hfds_trend, ohc_tendency_trend)
    plt.suptitle(title)    

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot climatology and trend in ocean heat transport convergence, surface heat flux and ocean heat content'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("outfile", type=str, help="Output file")                                     

    parser.add_argument("--htc_file", type=str, default=None,
                        help="Heat transport convergence file (usually hfbasin or hfy)")
    parser.add_argument("--hfds_file", type=str, default=None,
                        help="Surface heat flux file (usually hfds)")
    parser.add_argument("--ohc_file", type=str, default=None,
                        help="Ocean heat content file")
    
    parser.add_argument("--infer", type=str, nargs='*', default=None,
                        help="plots to infer (can be HTC, OHC and/or SFL. Or the word withhold to not plot any.")

    parser.add_argument("--rolling_window", type=int, default=None,
                        help="Smoothing applied to htc and hfds data (along lat axis)")

    parser.add_argument("--nummelin", action="store_true", default=False,
                        help="Restrict plot to Nummelin et al (2016) bounds")

    parser.add_argument("--ylim", type=float, nargs=2, metavar=('MIN', 'MAX'), default=None,
                        help="limits for y axis")
    parser.add_argument("--legloc", type=int, default=2,
                        help="Legend location")

    args = parser.parse_args()             
    main(args)
