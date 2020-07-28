"""
Filename:     calc_sfci.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the total internal surface forcing

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy as np
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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def main(inargs):
    """Run the program."""

    sfc_cube = iris.load_cube(inargs.sfc_file, 'total surface forcing')
    wfo_cube = iris.load_cube(inargs.wfo_file, 'water_flux_into_sea_water')
    metadata = {inargs.sfc_file: sfc_cube.attributes['history'],
                inargs.wfo_file: wfo_cube.attributes['history']}

    cp = 3992.10322329649   #J kg-1 degC-1
    lower_thetao_bounds = sfc_cube.coord('sea_water_potential_temperature').bounds[:, 0]
    theta = uconv.broadcast_array(lower_thetao_bounds, 1, sfc_cube.shape)

    sfci_cube = sfc_cube.copy()
    sfci_cube.data = sfc_cube.data - (cp * theta * wfo_cube.data)       # SFCI = SFC - Cp*THETA*SVF
    sfci_cube.var_name = 'sfci'
    sfci_cube.long_name = 'total internal surface forcing'
    log = cmdprov.new_log(infile_history=metadata, git_repo=repo_dir)
    sfci_cube.attributes['history'] = log

    iris.save(sfci_cube, inargs.sfci_file)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the total internal surface forcing'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("sfc_file", type=str, help="Total surface forcing file")
    parser.add_argument("wfo_file", type=str, help="Surface freshwater flux file")
    parser.add_argument("sfci_file", type=str, help="Output file")
    
    args = parser.parse_args()            
    main(args)
