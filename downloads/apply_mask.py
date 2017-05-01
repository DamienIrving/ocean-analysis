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

def check_coords(cube):
    """Check that lat and lon are last two coordinates."""

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names[-2] == 'latitude'
    assert coord_names[-1] == 'longitude'


def read_data(infile):
    """Read a data file."""

    cube_list = iris.load(infile)
    assert len(cube_list) == 1
    cube = cube_list[0]

    check_coords(cube)

    return cube
    

def copy_mask(mask_cube, target_shape):
    """Copy mask."""

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

    mask = uconv.broadcast_array(mask_cube_subset.data.mask, [mask_cube.ndim - 2, mask_cube.ndim - 1], target_shape)

    return mask


def main(inargs):
    """Run the program."""

    data_cube = read_data(inargs.infile)
    mask_cube = read_data(inargs.mask_file)

    if inargs.mask_method == 'copy':    
        mask = copy_mask(mask_cube, data_cube.shape)

        data_cube.data = numpy.ma.asarray(data_cube.data)
        data_cube.data.mask = mask

    outfile_metadata = {inargs.infile: data_cube.attributes['history'],}
    data_cube.attributes['history'] = gio.write_metadata(file_info=outfile_metadata)
    iris.save(data_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
"""

    description='Apply a lat/lon mask to a data file'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input data file")
    parser.add_argument("mask_file", type=str, help="Input mask file")
    parser.add_argument("mask_method", type=str, choices=('copy', 'sftlf'), help="Mask method")
    parser.add_argument("outfile", type=str, help="Output file name")    

    args = parser.parse_args()             

    main(args)
