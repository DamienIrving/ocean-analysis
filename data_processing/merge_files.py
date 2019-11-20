"""
Filename:     merge_files.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Merge a bunch of files

"""

# Import general Python modules

import sys, os, pdb, re
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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def main(inargs):
    """Run the program."""

    cube_list = iris.cube.CubeList([])
    for var in inargs.variables:
        cube, history = gio.combine_files(inargs.infiles, var)
        cube_list.append(cube)

    metadata_dict = {inargs.infiles[-1]: history[-1]}
    log_entry = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    if len(cube_list) > 1:
        equalise_attributes(cube_list)
        for cube in cube_list:
            cube.attributes['history'] = log_entry
    else:
        cube_list = cube_list[0]
        cube_list.attributes['history'] = log_entry

    iris.save(cube_list, inargs.outfile)
        

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Merge files'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("outfile", type=str, help="Output file")
    parser.add_argument("--variables", type=str, nargs='*', help="Variables to include")

    args = parser.parse_args()
    main(args)
