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


def main(inargs):
    """Run the program."""

    cube = iris.load_cube(inargs.infile)
    for bogus_indexes, target_indexes in zip(inargs.bogus_indexes, inargs.target_indexes):
        exec('cube.data[%s] = cube.data[%s]' %(bogus_indexes, target_indexes))

    cube.attributes['history'] = cmdprov.new_log(infile_history={inargs.infile: cube.attributes['history']}, git_repo=repo_dir)
    iris.save(cube, inargs.outfile)
    

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Replace values in a data file'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="File that needs new time axis")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--bogus_indexes", type=str, nargs='*',
                        help="""Array indexes for values that need replacing in literal form (e.g. "7, 58:60, :, :")""")
    parser.add_argument("--target_indexes", type=str, nargs='*',
                        help="""Array indexes for values that should replace the bogus ones in literal form (e.g. "19, 58:60, :, :")""")

    args = parser.parse_args()  
    assert len(args.bogus_indexes) == len(args.target_indexes)
    main(args)
