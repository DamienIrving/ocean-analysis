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

def get_data(filenames, var, metadata_dict):
    """Calculate zonal mean climatology and trend."""
    
    cube = iris.load(filenames, gio.check_iris_var(var))

    metadata_dict[filenames[0]] = cube[0].attributes['history']
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)

    # Temporal smoothing
    cube = timeseries.convert_to_annual(cube, full_months=True)

    # Regrid
    cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)

    # FIXME: Check sign (down is positive)

    # Zonal mean
    zonal_mean = cube.collapsed('longitude', iris.analysis.MEAN)
    zonal_cube.remove_coord('longitude')

    # Climatology and trends
    climatology_cube = zonal_cube.collapsed('time', iris.analysis.MEAN)
    trend_cube = get_trend_cube(zonal_cube)

    return climatology_cube, trend_cube, metadata_dict
    

def main(inargs):
    """Run the program."""
  





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
