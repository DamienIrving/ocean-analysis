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
    
    trend_array = timeseries.calc_trend(cube)
    new_cube = cube[0,:].copy()
    new_cube.remove_coord('time')
    new_cube.data = trend_array
    
    return new_cube


def get_ohc_trend(ohc_file, metadata_dict, zonal_stat='sum', derivative='sqrt'):
    """Read ocean heat content data and calculate tendency trend.
    
    Input units: J
    Output units: W s-1
    
    """
    
    long_name = 'ocean heat content zonal %s'  %(zonal_stat)
    ohc_cube = iris.load_cube(ohc_file, long_name)
    metadata_dict[ohc_file] = ohc_cube.attributes['history']

    seconds_per_year = 60 * 60 * 24 * 365.25  # J to W
    ohc_cube.data = ohc_cube.data / seconds_per_year

    assert derivative in ['sqrt', 'pass']
    if derivative == 'sqrt':
        ohc_cube.data = numpy.ma.sqrt(ohc_cube.data)
        ohc_trend = calc_trend_cube(ohc_cube)
        ohc_trend = ohc_trend ** 2
    elif derivative == 'pass':
        ohc_trend = calc_trend_cube(ohc_cube)

    ohc_trend.attributes = ohc_cube.attributes
    
    return ohc_trend, metadata_dict


def get_hfds_trend(hfds_file, metadata_dict, zonal_stat='sum'):
    """Read surface heat flux data and calculate trend.
    
    Input units: W
    Output units: W s-1
    
    """
    
    long_name = 'zonal %s surface downward heat flux in sea water globe'  %(zonal_stat)
    hfds_cube = iris.load_cube(hfds_file, long_name)
    metadata_dict[hfds_file] = hfds_cube.attributes['history']

    hfds_trend = calc_trend_cube(hfds_cube)
    
    return hfds_trend, metadata_dict


def get_htc_trend(htc_file, metadata_dict):
    """Read ocean heat transport convergence data and calculate trend.
    
    A hfbasin-convengence file is expected.
    
    Input: units = W, timescale = monhtly
    Output: units = W s-1, timescale = annual
    
    """
    
    htc_cube = iris.load_cube(htc_file)
    metadata_dict[htc_file] = htc_cube.attributes['history']

    htc_cube = timeseries.convert_to_annual(htc_cube)

    htc_trend = calc_trend_cube(htc_cube)
    htc_trend.attributes = htc_cube.attributes
    
    return htc_trend, metadata_dict


def main(inargs):
    """Run the program."""
  
    metadata_dict = {}
  
    htc_trend, metadata_dict = get_htc_trend(inargs.htc_file, metadata_dict)
    hfds_trend, metadata_dict = get_hfds_trend(inargs.hfds_file, metadata_dict, zonal_stat=inargs.zonal_stat)  
    ohc_trend, metadata_dict = get_ohc_trend(inargs.ohc_file, metadata_dict,
                                             zonal_stat=inargs.zonal_stat,
                                             derivative=inargs.derivative)  
    
    if not inargs.exclude_htc:
        iplt.plot(htc_trend, label='heat transport convergence', color='green') 
    if not inargs.exclude_hfds:
        iplt.plot(hfds_trend, label='surface heat flux', color='orange', linestyle='--')  
    if not inargs.exclude_ohc:
        iplt.plot(ohc_trend, label='ocean heat content tendency', color='black') 
    
    # FIXME: Plot residual hfds - htc. Should come close to ohc   
  
    if inargs.nummelin:
        color = '0.7'
        width = 0.5
        plt.axhline(y=0, linestyle='--', color=color, linewidth=width)
        plt.axvline(x=30, color=color, linewidth=width)
        plt.axvline(x=50, color=color, linewidth=width)
        plt.axvline(x=77, color=color, linewidth=width)
        plt.xlim(20, 90)

    plt.legend(loc=2)
    plt.xlabel('latitude')
    plt.ylabel('Trend ($W s^{-1}$)')
    plt.title(htc_trend.attributes['model_id'])

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

    parser.add_argument("--exclude_htc", action="store_true", default=False,
                        help="Leave htc off plot")
    parser.add_argument("--exclude_hfds", action="store_true", default=False,
                        help="Leave hfds off plot")
    parser.add_argument("--exclude_ohc", action="store_true", default=False,
                        help="Leave ohc off plot")

    parser.add_argument("--derivative", type=str, choices=('sqrt', 'pass'), default='sqrt',
                        help="Method used to calculate the OHC tendency")

    parser.add_argument("--nummelin", action="store_true", default=False,
                        help="Restrict plot to Nummelin et al (2016) bounds")

    parser.add_argument("--zonal_stat", type=str, choices=('mean', 'sum'), default='sum',
                        help="Zonal statistic")

    args = parser.parse_args()             
    main(args)
