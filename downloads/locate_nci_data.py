"""
Filename:     locate_nci_data.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Locate CMIP5 data at NCI

"""

# Import general Python modules

import sys, os, pdb
import argparse
from ARCCSSive import CMIP5
import six
import glob


# Define functions

def main(inargs):
    """Run the program."""

    cmip5 = CMIP5.DB.connect()

    outputs = cmip5.outputs(experiment = inargs.experiment,
                            variable = inargs.variable,
                            mip = inargs.mip,
                            model = inargs.model,
                            ensemble = inargs.ensemble)
 
    ua6_path = '/g/data/ua6/DRSv2/CMIP5/%s/%s/%s/%s/%s/%s/latest/*' %(inargs.model, inargs.experiment, inargs.time_freq, inargs.realm, inargs.ensemble, inargs.variable)
    print('DRSv2:', glob.glob(ua6_path))

    my_path = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/%s/%s/%s/%s/latest' %(inargs.model, inargs.experiment, inargs.time_freq, inargs.realm, inargs.ensemble, inargs.variable)

    print('Elsewhere path:')
    elsewhere_path = []
    for o in outputs:
        var = o.variable
        for v in o.versions:
            elsewhere_path.append(v.path)
            print(v.path)
            
    print('Elsewhere files:')
    for f in outputs.first().filenames():
        six.print_(f)
        if inargs.symlink:
            assert len(elsewhere_path) == 1
            command1 = 'mkdir -p %s' %(my_path)
            command2 = 'ln -s %s/%s %s/%s'  %(elsewhere_path[0], f, my_path, f)
            if inargs.execute:
                os.system(command1)
                os.system(command2)
            else:
                print(command1)
                print(command2) 
        
if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

dependencies:
    vdi $ pip install --user ARCCSSive
    vdi $ export CMIP5_DB=sqlite:////g/data1/ua6/unofficial-ESG-replica/tmp/tree/cmip5_raijin_latest.db

"""

    description='Locate CMIP5 data at NCI'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("experiment", type=str, help="Experiment name")
    parser.add_argument("variable", type=str, help="var_name")
    parser.add_argument("time_freq", type=str, help="e.g. mon or fx")
    parser.add_argument("mip", type=str, help="e.g. Omon, Amon, fx or aero")
    parser.add_argument("realm", type=str, help="e.g. atmos, ocean or aerosol")
    parser.add_argument("model", type=str, help="Model name")
    parser.add_argument("ensemble", type=str, help="e.g. r1i1p1")

    parser.add_argument("--symlink", action="store_true", default=False,
                        help="Create a symlink for the elsewhere files")
    parser.add_argument("--execute", action="store_true", default=False,
                        help="Execute the symlink command rather than printing to screen")

    args = parser.parse_args()             
    main(args)
