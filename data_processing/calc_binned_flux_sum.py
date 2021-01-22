"""Calculate sum surface fluxes binned by temperature and/or salinity."""

import sys
script_dir = sys.path[0]
import os
import pdb
import argparse

import iris
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
except ImportError:
    raise ImportError('Script and modules in wrong directories')


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
            assert inargs.new_var in long_names.keys()
            cube.var_name = inargs.new_var + '_' + bin_var
            cube.long_name = long_names[inargs.new_var] + ' binned by ' + bin_name
            assert cube.units == 'W'
        cube_list.append(cube)

    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    for cube in cube_list:
        cube.attributes['history'] = log

    iris.save(cube_list, inargs.new_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("new_var", type=str, help="New output variable")
    parser.add_argument("new_file", type=str, help="New output file")
    
    parser.add_argument("--invars", type=str, nargs='*', help="Input variables")
    parser.add_argument("--ref_file", type=str, default=None, help="reference cube for new file attributes")

    args = parser.parse_args()            
    main(args)
