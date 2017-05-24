"""
Filename:     calc_annual.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Apply annual timescale smoothing

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes

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

def main(inargs):
    """Run the program."""

    for infile in inargs.infiles:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(infile, inargs.var)
            cube = timeseries.convert_to_annual(cube)

        metadata_dict = {infile: cube.attributes['history']}
        cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

        outfile = infile.replace('mon', 'yr')
        outfile = outfile.replace('ua6', 'r87/dbi599')

        #assert cube.data.dtype == numpy.float32
        iris.save(cube, outfile, netcdf_format='NETCDF3_CLASSIC')

        print(outfile)
        del cube


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Apply annual timescale smoothing'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable name")

    args = parser.parse_args()            

    main(args)
