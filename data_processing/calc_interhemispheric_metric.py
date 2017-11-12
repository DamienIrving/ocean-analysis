"""
Filename:     calc_interhemispheric_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the interhemispheric timeseries for a general input variable

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
iris.FUTURE.netcdf_promote = True

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
    import spatial_weights
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def calc_mean(infiles, variable, lat_constraint):
    """Load the infiles and calculate the hemispheric mean value."""
    
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load(infiles, variable & lat_constraint, callback=save_history)

        equalise_attributes(cube)
        cube = cube.concatenate_cube()
        cube = gio.check_time_units(cube)
        cube = timeseries.convert_to_annual(cube) 

    area_weights = spatial_weights.area_array(cube)
    mean = cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=area_weights)

    return mean


def update_history(cube, infiles):
    """Update the history attribute"""
    
    infile_history = {}
    infile_history[infiles[0]] = history[0] 
 
    cube.attributes['history'] = gio.write_metadata(file_info=infile_history)

    return cube


def calc_metric(nh_mean, sh_mean):
    """Calculate the metric"""
    
    metric = nh_mean.copy()
    metric.data = nh_mean.data - sh_mean.data
    
    return metric
    
    
def main(inargs):
    """Run the program."""

    nh_lower, nh_upper = inargs.nh_lat_bounds
    nh_constraint = iris.Constraint(latitude=lambda cell: nh_lower <= cell < nh_upper)

    sh_lower, sh_upper = inargs.sh_lat_bounds
    sh_constraint = iris.Constraint(latitude=lambda cell: sh_lower <= cell < sh_upper)

    nh_mean = calc_mean(inargs.infiles, inargs.variable, nh_constraint)
    sh_mean = calc_mean(inargs.infiles, inargs.variable, sh_constraint)
    
    metric = calc_metric(nh_mean, sh_mean)    
    metric = update_history(metric, inargs.infiles)

    iris.save(metric, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate the interhemispheric timeseries for a general input variable'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")            
    parser.add_argument("variable", type=str, help="Input variable")                                                 
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--nh_lat_bounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=(0.0, 91.0),
                        help="Northern Hemisphere latitude bounds [default = entire hemisphere]")
    parser.add_argument("--sh_lat_bounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=(-91.0, 0.0),
                        help="Southern Hemisphere latitude bounds [default = entire hemisphere]")

    args = parser.parse_args()             
    main(args)
