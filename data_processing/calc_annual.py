"""
Filename:     calc_annual.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Apply annual timescale smoothing
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
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def main(inargs):
    """Run the program."""

    cube = iris.load_cube(inargs.infile, inargs.var)
    cube = timeseries.convert_to_annual(cube)

    log = cmdprov.new_log(infile_history={inargs.infile: cube.attributes['history']}, git_repo=repo_dir) 
    cube.attributes['history'] = log

    #assert cube.data.dtype == numpy.float32
    #iris.save(cube, outfile, netcdf_format='NETCDF3_CLASSIC')
    iris.save(cube, inargs.outfile)


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

    parser.add_argument("infile", type=str, help="Input file")
    parser.add_argument("var", type=str, help="Variable name")
    parser.add_argument("outfile", type=str, help="Output file")

    args = parser.parse_args()            

main(args)
