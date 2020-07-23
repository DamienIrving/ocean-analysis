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

def main(inargs):
    """Run the program."""

    long_names = {'sfch': 'surface heat fluxes',
                  'sfcv': 'surface heat fluxes from surface volume fluxes',
                  'vmix': 'vertical mixing',
                  'smix': 'miscellaneous mixing',
                  'rmix': 'neutral diffusion',
                  'ten': 'total tendency',
                  'sfc': 'total surface forcing',
                  'mix': 'total explicit mixing'}

    assert len(inargs.infiles) == len(inargs.invars)
    cube = iris.load_cube(inargs.infiles[0], gio.check_iris_var(inargs.invars[0]))
    for file_name, file_var in zip(inargs.infiles[1:], inargs.invars[1:]):
        next_cube = iris.load_cube(file_name, gio.check_iris_var(file_var))
        cube.data = cube.data + next_cube.data

    cube.var_name = inargs.new_var
    cube.long_name = long_names[inargs.new_var]
    cube.standard_name = None
    assert cube.units == 'W'
    log = cmdprov.new_log(infile_history={inargs.infiles[0]: cube.attributes['history']}, git_repo=repo_dir)
    cube.attributes['history'] = log

    iris.save(cube, inargs.new_file)


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

    args = parser.parse_args()            
    main(args)
