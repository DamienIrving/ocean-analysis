"""
Filename:     calc_time_diff.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate difference between two time periods
"""

# Import general Python modules

import sys, os, pdb
import argparse
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import cmdline_provenance as cmdprov

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


def period_mean(cube, time_period):
    """Calculate the mean for a particular time period."""

    time_constraint = gio.get_time_constraint(time_period)
    cube = cube.extract(time_constraint)
    cube = cube.collapsed('time', iris.analysis.MEAN)
    cube.remove_coord('time')

    return cube


def main(inargs):
    """Run the program."""

    cube = iris.load(inargs.infiles, gio.check_iris_var(inargs.var), callback=save_history)
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
   
    start_cube = period_mean(cube.copy(), inargs.start_period)
    end_cube = period_mean(cube.copy(), inargs.end_period)

    outcube = cube[0, ::].copy()
    outcube.remove_coord('time')
    outcube.data = end_cube.data - start_cube.data

    log = cmdprov.new_log(infile_history={inargs.infiles[0]: history[0]}, git_repo=repo_dir) 
    outcube.attributes['history'] = log

    iris.save(outcube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the difference between two time periods'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable name")
    parser.add_argument("start_period", type=str, nargs=2, 
                        help="Start time period bounds (YYYY-MM-DD YYYY-MM-DD)")
    parser.add_argument("end_period", type=str, nargs=2, 
                        help="End time period bounds (YYYY-MM-DD YYYY-MM-DD)")
    parser.add_argument("outfile", type=str, help="Output file")

    args = parser.parse_args()            

    main(args)
