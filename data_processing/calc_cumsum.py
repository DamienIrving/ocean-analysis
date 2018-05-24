"""
Filename:     calc_cumsum.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the cumulative sum

"""

# Import general Python modules

import sys, os, pdb
import argparse, copy
import numpy
import iris

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

import general_io as gio
import timeseries
import convenient_universal as uconv


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
     
def cumsum(cube, clim=None):
    """Calculate the cumulative sum of the anomaly data."""

    if clim:
        cube.data = cube.data - clim.data
        print('Climatology sum:', clim.data.sum())
    
    cube.data = numpy.cumsum(cube.data, axis=0)
    
    return cube


def main(inargs):
    """Run the program."""

    cube = iris.load_cube(inargs.infile, gio.check_iris_var(inargs.var))
    cube = uconv.convert_to_joules(cube)
    assert cube.units == 'J'
    metadata_dict = {} 
    metadata_dict[inargs.infile] = cube.attributes['history']
    if inargs.clim:
        clim_data_cube = iris.load_cube(inargs.clim, gio.check_iris_var(inargs.var))
        clim_data_cube = uconv.convert_to_joules(clim_data_cube)
        clim_cube = clim_data_cube.collapsed('time', iris.analysis.MEAN)
        
        assert clim_cube.units == 'J'
        metadata_dict[inargs.clim] = clim_cube.attributes['history']
    else:
        clim_cube = None

    cube = cumsum(cube, clim=clim_cube)  

    cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)
    iris.save(cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Calculate the cumulative sum'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("var", type=str, help="Input file variable (standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--clim", type=str, default=None,
                        help="Calculate the cumulative anomaly relative to this climatology")

    args = parser.parse_args()
    main(args)

