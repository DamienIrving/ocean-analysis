"""
Filename:     calc_pe.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate precipitation minus evaporation

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

    pr_cube, pr_history = gio.combine_files(inargs.pr_files, 'precipitation_flux', checks=True)
    evap_cube, evap_history = gio.combine_files(inargs.evap_files, 'water_evapotranspiration_flux', checks=True)

    pe_cube = pr_cube - evap_cube

    pe_cube.metadata = pr_cube.metadata
    iris.std_names.STD_NAMES['precipitation_minus_evaporation_flux'] = {'canonical_units': pe_cube.units}
    pe_cube.standard_name = 'precipitation_minus_evaporation_flux'
    pe_cube.long_name = 'precipitation minus evaporation flux'
    pe_cube.var_name = 'pe'
    metadata_dict = {inargs.pr_files[0]: pr_history[0], 
                     inargs.evap_files[0]: evap_history[0]}
    pe_cube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)

    iris.save(pe_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the precipitation minus evaporation'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--pr_files", type=str, nargs='*', required=True,
                        help="precipitation files")
    parser.add_argument("--evap_files", type=str, nargs='*', required=True,
                        help="evaporation files")

    args = parser.parse_args()            
    main(args)
