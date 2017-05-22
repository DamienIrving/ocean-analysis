"""
Filename:     plot_heat_trends.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
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


def get_ohc_trend(ohc_file, metadata_dict):
    """Read ocean heat content data and calculate trend.
    
    Input units: 10^12 J m-2
    Output units: W m-2 s-1
    
    """
    
    # FIXME: I haven't accounted for the 10^12 (remove from ohc calculation)
    
    ohc_cube = iris.load_cube(ohc_file, 'ocean heat content 2D')
    metadata_dict[ohc_file] = ohc_cube.attributes['history']

    ohc_cube = ohc_cube / 86400.   # J m-2 to W m-2

    ohc_trend = calc_trend_cube(ohc_cube)
    ohc_trend.attributes = ohc_cube.attributes
    
    return ohc_trend, metadata_dict


def get_hfds_trend(hfds_file, metadata_dict):
    """Read surface heat flux data and calculate trend.
    
    Input units: W m-2
    Output units: W m-2 s-1
    
    """
    
    hfds_cube = iris.load_cube(hfds_file, 'zonal mean surface downward heat flux in sea water globe')
    metadata_dict[hfds_file] = hfds_cube.attributes['history']

    hfds_trend = calc_trend_cube(hfds_cube)
    
    return hfds_trend, metadata_dict


def get_htc_trend(htc_file, metadata_dict):
    """Read ocean heat transport convergence data and calculate trend.
    
    A hfbasin CMIP5 file is expected.
    
    Input units: W
    Output units: W m-2 s-2
    
    """
    
    htc_cube = iris.load_cube(htc_file)
    metadata_dict[htc_file] = htc_cube.attributes['history']

    htc_cube = htc_cube.extract(iris.Constraint(region='global_ocean'))
    htc_cube = timeseries.convert_to_annual(htc_cube)

    htc_trend = calc_trend_cube(htc_cube / (3.1 * 10**12)) # FIXME: Need to convert W to W m -2 more accurately (use actual ocean area at each latitude)
    htc_trend.attributes = htc_cube.attributes
    
    return htc_trend, metadata_dict


def main(inargs):
    """Run the program."""
  
    metadata_dict = {}
  
    htc_trend, metadata_dict = get_htc_trend(inargs.htc_file, metadata_dict)
    hfds_trend, metadata_dict = get_hfds_trend(inargs.hfds_file, metadata_dict)  
    ohc_trend, metadata_dict = get_ohc_trend(inargs.ohc_file, metadata_dict)  
    
    iplt.plot(htc_trend * -1, label='heat transport convergence') 
    iplt.plot(hfds_trend, label='surface heat flux')  
    iplt.plot(ohc_trend, label='ocean heat content') 
     
    plt.legend(loc=2)
    plt.xlabel('latitude')
    plt.ylabel('Trend ($W m^{-2} s^{-1}$)')  # FIXME: Include an option for W s-1 (otherwise small ocean areas come up large)
    pdb.set_trace()
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

    args = parser.parse_args()             
    main(args)
