"""
Filename:     calc_pe.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate precipitation minus evaporation

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def get_file_names(precip_file, evap_dir, pe_dir, evs=False):
    """Get evap and p-e file names corresponding to precip file."""

    precip_fname = precip_file.split('/')[-1]

    evap_var = 'evs_' if evs else 'evspsbl_'
    evap_fname = precip_fname.replace('pr_', evap_var)
    evap_file = evap_dir + '/' + evap_fname

    pe_fname = precip_fname.replace('pr_', 'pe_')
    pe_file = pe_dir + '/' + pe_fname

    return evap_file, pe_file


def main(inargs):
    """Run the program."""

    for precip_file in inargs.precip_files:
        precip_cube = iris.load_cube(precip_file, inargs.precip_var)
        evap_file, pe_file = get_file_names(precip_file, inargs.evap_dir, inargs.pe_dir, evs=inargs.evs)

        evap_cube = iris.load_cube(evap_file, inargs.evap_var)

        pe_cube = precip_cube - evap_cube

        pe_cube.metadata = precip_cube.metadata
        iris.std_names.STD_NAMES['precipitation_minus_evaporation_flux'] = {'canonical_units': pe_cube.units}
        pe_cube.standard_name = 'precipitation_minus_evaporation_flux'
        pe_cube.long_name = 'precipitation minus evaporation flux'
        pe_cube.var_name = 'pe'
        metadata_dict = {precip_file: precip_cube.attributes['history'], 
                         evap_file: evap_cube.attributes['history']}
        pe_cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

        assert pe_cube.data.dtype == numpy.float32
        iris.save(pe_cube, pe_file, netcdf_format='NETCDF3_CLASSIC')
        print(pe_file)
        del pe_cube


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

    parser.add_argument("precip_files", type=str, nargs='*', help="Precipitation file")
    parser.add_argument("precip_var", type=str, help="Precipitation standard_name")
    parser.add_argument("evap_dir", type=str, help="Evaporation directory")
    parser.add_argument("evap_var", type=str, help="Evaporation standard_name")
    parser.add_argument("pe_dir", type=str, help="Output p-e directory")

    parser.add_argument("--evs", action="store_true", default=False,
                        help="Evaporation variable is evs instead of evspsbl")

    args = parser.parse_args()            

    main(args)
