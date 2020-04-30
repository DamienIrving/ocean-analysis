"""
Filename:     correct_mask.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Correct a bogus mask (e.g. some models put 1.0 or Nan as the mask value) 

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
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

    cube = iris.load_cube(inargs.infile, inargs.var)

    cube.data = numpy.ma.masked_invalid(cube.data)
    if inargs.fill_value:
        cube.data = numpy.ma.masked_where(cube.data >= cube.data.fill_value, cube.data)
    if inargs.mask_value:
        cube.data = numpy.ma.masked_where(cube.data == inargs.mask_value, cube.data)

    cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir, infile_history={inargs.infile: cube.attributes['history']})
    iris.save(cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Correct a bogus mask (e.g. some models put 1.0 or Nan as the mask value)'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input files")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--fill_value", action="store_true", default=False,
                        help="Mask points greater or equal to the fill value")

    parser.add_argument("--mask_value", type=float, default=None,
                        help="Value to mask")

    args = parser.parse_args()            
    main(args)
