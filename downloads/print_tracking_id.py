"""
Filename:     print_tracking_id.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Print tracking ids 
"""

# Import general Python modules

import sys, os, pdb
import argparse
import glob
import iris

import warnings
warnings.filterwarnings('ignore')

def main(inargs):
    """Run the program."""

    files = glob.glob('/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/mon/*/%s/%s/latest/*.nc'  %(inargs.model, inargs.experiment, inargs.rip, inargs.var) )
    files.sort()
    for infile in files:
        cube = iris.load(infile)[0]
        filename = infile.split('/')[-1]
        track_id = cube.attributes['tracking_id']

        if inargs.id_only:
            print(track_id)
        else:
            print(infile, track_id)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Print tracking ids'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("model", type=str, help="model")
    parser.add_argument("experiment", type=str, help="experiment") 
    parser.add_argument("rip", type=str, help="run, intialisation, physics")
    parser.add_argument("var", type=str, help="variable")
  
    parser.add_argument("--id_only", action="store_true", default=False,
                        help="Output the tracking id only")
    
    args = parser.parse_args()             
    main(args)
