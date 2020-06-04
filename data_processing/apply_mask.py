"""
Filename:     apply_mask.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Apply a lat/lon mask to a data file

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
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

def create_mask(mask_cube, target_shape):
    """Create mask from an sftlf (land surface fraction) file.

    There is no land when cell value == 0

    """

    target_ndim = len(target_shape)
    land_array = numpy.where(mask_cube.data < 0.001, False, True)
    mask = uconv.broadcast_array(land_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    return mask


def copy_mask(mask_cube, target_shape):
    """Copy mask from another file."""

    target_ndim = len(target_shape)
    mask_coords = [coord.name() for coord in mask_cube.dim_coords]

    assert mask_cube.ndim in [2, 3, 4]
    if mask_cube.ndim == 2:
        mask_cube_subset = mask_cube.data
    elif mask_cube.ndim == 3:
        mask_cube_subset = mask_cube[0, ::]
        print(mask_cube_subset.coord(mask_coords[0]))
    else:
        mask_cube_subset = mask_cube[0, 0, ::]
        print(mask_cube_subset.coord(mask_coords[0]))
        print(mask_cube_subset.coord(mask_coords[1]))

    mask = uconv.broadcast_array(mask_cube_subset.data.mask, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape

    return mask
    

def main(inargs):
    """Run the program."""

    if inargs.var == 'ocean_volume':
        data_cube = gio.get_ocean_weights(inargs.infile, sanity_check=False)
    else:
        data_cube, data_history = gio.combine_files(inargs.infile, inargs.var)
    mask_cube, mask_history = gio.combine_files(inargs.mask_file, inargs.mask_var)

    if inargs.mask_method == 'copy':    
        mask = copy_mask(mask_cube, data_cube.shape)
    else:
        mask = create_mask(mask_cube, data_cube.shape)
    data_cube.data = numpy.ma.asarray(data_cube.data)
    data_cube.data.mask = mask
            
    data_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir) 
    iris.save(data_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
"""

    description='Apply a spatial mask to a data file'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input data file")
    parser.add_argument("var", type=str, help="Input variable standard_name")
    parser.add_argument("mask_file", type=str, help="Input mask file")
    parser.add_argument("mask_var", type=str, help="Input mask variable standard_name")
    parser.add_argument("mask_method", type=str, choices=('copy', 'sftlf'), help="Mask method")
    parser.add_argument("outfile", type=str, help="Output data file")

    args = parser.parse_args()             

    main(args)
