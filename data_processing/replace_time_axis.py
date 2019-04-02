"""
Filename:     replace_time_axis.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Replace the time axis

"""

# Import general Python modules

import sys, os, pdb
import argparse
import iris
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

def switch_data(cube, time_cube):
    """Switch the data rather than the time axis."""

    new_cube = time_cube.copy()
    new_cube.data = cube.data
    new_cube.attributes = cube.attributes

    return new_cube


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.start_date)
    cube = iris.load_cube(inargs.infile)
    time_cube = iris.load_cube(inargs.timefile, time_constraint)

    if cube.coord('time').shape[0] > time_cube.coord('time').shape[0]:
        cube = cube[0:time_cube.coord('time').shape[0], ::]

    if inargs.switch_data:
        cube = switch_data(cube, time_cube)
    else:
        len_time = cube.coord('time').shape[0]
        cube.replace_coord(time_cube.coord('time')[0:len_time])

    cube.attributes['history'] = cmdprov.new_log(infile_history={inargs.infile: cube.attributes['history']}, git_repo=repo_dir)
    iris.save(cube, inargs.outfile)
    

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Replace the time axis'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="File that needs new time axis")
    parser.add_argument("timefile", type=str, help="File that has the desired time axis")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--start_date", type=str, default=None,
                        help="Start date for new time axis [default = entire]")
    parser.add_argument("--switch_data", action="store_true", default=False,
                        help="Switch out the data from the timefile instead [default: False]")

    args = parser.parse_args()             
    main(args)
