"""
Filename:     plot_heat_trends.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot trend in ocean heat transport convergence, surface heat flux and ocean heat content

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

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

    return ohc_tendency_trend_cube, ohc_trend_cube, metadata_dict


def get_hfds_data(hfds_file, metadata_dict, rolling_window=None):
    """Read surface heat flux data and calculate mean and trend.
    
    Input units: W
    Output units: W s-1
    
    """
    
    long_name = 'zonal sum surface downward heat flux in sea water globe'
    hfds_cube = iris.load_cube(hfds_file, long_name)
    metadata_dict[hfds_file] = hfds_cube.attributes['history']

    if rolling_window:
        hfds_cube = hfds_cube.rolling_window('latitude', iris.analysis.MEAN, rolling_window)

    hfds_trend = calc_trend_cube(hfds_cube)
    hfds_mean = hfds_cube.collapsed('time', iris.analysis.MEAN)    

    return hfds_trend, hfds_mean, metadata_dict


def get_htc_data(htc_file, metadata_dict, rolling_window=None):
    """Read ocean heat transport convergence data and calculate mean and trend.
    
    A hfbasin-convengence or hfy-convergence file is expected.
    
    Input: units = W, timescale = monhtly
    Output: units = W s-1, timescale = annual
    
    """
    
    if 'hfy' in htc_file:
        htc_cube = iris.load_cube(htc_file, 'zonal sum ocean heat y transport convergence globe')
    else:
        htc_cube = iris.load_cube(htc_file)
    metadata_dict[htc_file] = htc_cube.attributes['history']

    htc_cube = timeseries.convert_to_annual(htc_cube)
    if rolling_window:
        htc_cube = htc_cube.rolling_window('latitude', iris.analysis.MEAN, rolling_window)

    htc_trend = calc_trend_cube(htc_cube)
    htc_mean = htc_cube.collapsed('time', iris.analysis.MEAN)

    htc_trend.attributes = htc_cube.attributes
    htc_mean.atributes = htc_cube.attributes
    
    return htc_trend, htc_mean, metadata_dict


def plot_data(htc_data, hfds_data, ohc_data, inargs, gs, plotnum, plot_type):
    """Plot trends."""

    ax = plt.subplot(gs[plotnum])
    plt.sca(ax)

    if plot_type == 'trends':
        htc_label = 'trend in heat transport convergence (HTC)'
        hfds_label = 'trend in surface heat flux (SFL)'
        ohc_label = 'trend in ocean heat content tendency'
        y_label = 'Trend ($W yr^{-1}$)'
    else:
        htc_label = 'average annual mean heat transport convergence (HTC)'
        hfds_label = 'average annual mean surface heat flux (SFL)'
        ohc_label = 'trend in ocean heat content'
        y_label = '$W$ (or $W yr^{-1}$ for OHC trend)'

    if not inargs.exclude_htc:
        iplt.plot(htc_data, label=htc_label, color='green') 
    if not inargs.exclude_hfds:
        iplt.plot(hfds_data, label=hfds_label, color='orange', linestyle='--')  
    if not inargs.exclude_ohc:
        iplt.plot(ohc_data, label=ohc_label, color='black') 
    
    if not (inargs.exclude_htc and inargs.exclude_hfds):
        #htc_trend.remove_coord('region')
        ref_lats = [('latitude', hfds_data.coord('latitude').points)]  
        regridded_htc_data = htc_data.interpolate(ref_lats, iris.analysis.Linear())
        regridded_htc_data.coord('latitude').bounds = hfds_data.coord('latitude').bounds
        regridded_htc_data.coord('latitude').coord_system = hfds_data.coord('latitude').coord_system
        regridded_htc_data.coord('latitude').attributes = hfds_data.coord('latitude').attributes

        regridded_htc_data.coord('latitude').var_name = 'lat'
        hfds_data.coord('latitude').var_name = 'lat'
        regridded_htc_data.coord('latitude').standard_name = 'latitude'
        hfds_data.coord('latitude').standard_name = 'latitude'
        regridded_htc_data.coord('latitude').long_name = 'latitude'
        hfds_data.coord('latitude').long_name = 'latitude'
        
        iplt.plot(regridded_htc_data + hfds_data, label='HTC + SFL', color='0.5')  
  
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
    plt.xlabel('latitude')
    plt.ylabel(y_label)
    plt.title(plot_type)


def main(inargs):
    """Run the program."""
  
    metadata_dict = {}
   
    fig = plt.figure(figsize=[10, 15])
    gs = gridspec.GridSpec(2, 1)

    htc_trend, htc_mean, metadata_dict = get_htc_data(inargs.htc_file, metadata_dict, rolling_window=inargs.rolling_window)
    hfds_trend, hfds_mean, metadata_dict = get_hfds_data(inargs.hfds_file, metadata_dict, rolling_window=inargs.rolling_window)  
    ohc_tendency_trend, ohc_trend, metadata_dict = get_ohc_data(inargs.ohc_file, metadata_dict)  
    
    plot_data(htc_mean, hfds_mean, ohc_trend, inargs, gs, 0, 'mean')
    plot_data(htc_trend, hfds_trend, ohc_tendency_trend, inargs, gs, 1, 'trends')
    
    plt.suptitle(htc_trend.attributes['model_id'])

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot trend in ocean heat transport convergence, surface heat flux and ocean heat content'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("htc_file", type=str, help="Heat transport convergence file (usually hfbasin)")
    parser.add_argument("hfds_file", type=str, help="Surface heat flux file (usually hfds)")
    parser.add_argument("ohc_file", type=str, help="Ocean heat content file")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--rolling_window", type=int, default=None,
                        help="Smoothing applied to htc and hfds data (along lat axis)")

    parser.add_argument("--exclude_htc", action="store_true", default=False,
                        help="Leave htc off plot")
    parser.add_argument("--exclude_hfds", action="store_true", default=False,
                        help="Leave hfds off plot")
    parser.add_argument("--exclude_ohc", action="store_true", default=False,
                        help="Leave ohc off plot")

    parser.add_argument("--nummelin", action="store_true", default=False,
                        help="Restrict plot to Nummelin et al (2016) bounds")

    parser.add_argument("--ylim", type=float, nargs=2, metavar=('MIN', 'MAX'), default=None,
                        help="limits for y axis")
    parser.add_argument("--legloc", type=int, default=2,
                        help="Legend location")

    args = parser.parse_args()             
    main(args)
