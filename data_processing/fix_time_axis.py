"""
Filename:     fix_time_axis.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Fix a bogus time step

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

def main(inargs):
    """Run the program."""

    cube = iris.load_cube(inargs.infile)
    
    t1 = inargs.timestep
    t0 = t1 - 1
    t2 = t1 + 1
    pdb.set_trace()
    cube.coord('time').points[t1] = (cube.coord('time').points[t2] + cube.coord('time').points[t0]) / 2
    cube.coord('time').bounds[t1][0] = cube.coord('time').bounds[t0][-1]
    cube.coord('time').bounds[t1][1] = cube.coord('time').bounds[t2][0]
    iris.util.promote_aux_coord_to_dim_coord(cube, 'time')

    cube.attributes['history'] = cmdprov.new_log(infile_history={inargs.infile: cube.attributes['history']}, git_repo=repo_dir)
    iris.save(cube, inargs.outfile)
    

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Fix a bogus time step'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="File that needs new time axis")
    parser.add_argument("timestep", type=int, help="index for bogus time step")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()             
    main(args)
