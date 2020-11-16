"""
Filename:     calc_binned_flux_sum.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the sum of multiple surface fluxes binned by temperature

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

long_names = {'sfch': 'surface heat fluxes',
              'sfcv': 'surface heat fluxes from surface volume fluxes',
              'vmix': 'vertical mixing',
              'smix': 'miscellaneous mixing',
              'rmix': 'neutral diffusion',
              'ten': 'total tendency',
              'sfc': 'total surface forcing',
              'mix': 'total explicit mixing',
             }

def main(inargs):
    """Run the program."""

    assert len(inargs.infiles) == len(inargs.invars)
    cube_list = iris.cube.CubeList([])
    bin_vars = ['tbin', 'sbin', 'tsbin']
    bin_names = ['temperature', 'salinity', 'temperature and salinity']
    for bin_var, bin_name in zip(bin_vars, bin_names):
        running_sum = 0
        metadata_dict = {}
        for file_name, base_var in zip(inargs.infiles, inargs.invars):
            cube = iris.load_cube(file_name, f'{base_var} binned by {bin_name}')
            metadata_dict[file_name] = cube.attributes['history']
            running_sum = running_sum + cube.data
        cube.data = running_sum
        if inargs.ref_file:
            ref_cube = iris.load_cube(inargs.ref_file, inargs.new_var)
            cube.attributes = ref_cube.attributes
            cube.var_name = ref_cube.var_name + '_' + bin_var
            cube.long_name = ref_cube.long_name + ' binned by ' + bin_name
        else:
            assert new_var in long_names.keys()
            cube.var_name = inargs.new_var + '_' + bin_var
            cube.long_name = long_names[inargs.new_var] + ' binned by ' + bin_name
            assert cube.units == 'W'
        cube_list.append(cube)

    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    for cube in cube_list:
        cube.attributes['history'] = log

    iris.save(cube_list, inargs.new_file)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the sum of multiple surface fluxes binned by temperature'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("new_var", type=str, help="New output variable")
    parser.add_argument("new_file", type=str, help="New output file")
    
    parser.add_argument("--invars", type=str, nargs='*', help="Input variables")
    parser.add_argument("--ref_file", type=str, help="reference cube for new file attributes")

    args = parser.parse_args()            
    main(args)
