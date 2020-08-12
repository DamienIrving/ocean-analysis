"""
Filename:     calc_areacello.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the CMIP5 areacello variable

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
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def construct_area_cube(var_name, area_data, global_atts, dim_coords):
    """Construct the new area cube """

    dim_coords_list = []
    for i, coord in enumerate(dim_coords):
        dim_coords_list.append((coord, i))

    if var_name == 'areacello':
        long_name = 'Grid-Cell Area for Ocean Variables'
    else:
        long_name = 'Grid-Cell Area for Atmospheric Grid Variables'

    area_cube = iris.cube.Cube(area_data,
                               standard_name='cell_area',
                               long_name=long_name,
                               var_name=var_name,
                               units='m2',
                               attributes=global_atts,
                               dim_coords_and_dims=dim_coords_list) 

    return area_cube


def main(inargs):
    """Run the program."""

    data_cube = iris.load_cube(inargs.dummy_file, inargs.dummy_var)
    coord_names = [coord.name() for coord in data_cube.dim_coords]
    if inargs.volcello_file:
        assert data_cube.ndim == 4
        volume_cube = gio.get_ocean_weights(inargs.volcello_file)
        depth_coord = data_cube.coord(coord_names[1])
        assert depth_coord.units in ['m', 'dbar']
        surface_depth = depth_coord.bounds[0][1] - depth_coord.bounds[0][0]
        area_data = volume_cube.data[0, ::] / surface_depth
        data_cube = data_cube[0, 0, ::]
        data_cube.remove_coord(coord_names[0])
        data_cube.remove_coord(coord_names[1])
    else:
        assert coord_names[-2:] == ['latitude', 'longitude']
        if data_cube.ndim == 3:
            data_cube = data_cube[0, ::]
            data_cube.remove_coord(coord_names[0])
        else:
            data_cube = data_cube[0, 0, ::]
            data_cube.remove_coord(coord_names[0])
            data_cube.remove_coord(coord_names[1])
        area_data = spatial_weights.area_array(data_cube)
        area_data = numpy.ma.asarray(area_data)
        if inargs.outvar == 'areacello':
            area_data.mask = data_cube.data.mask
        
    area_cube = construct_area_cube(inargs.outvar, area_data, data_cube.attributes, data_cube.dim_coords)    
    area_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)

    if inargs.outvar == 'areacello':
        gio.check_global_ocean_area(area_cube.data.sum())
    else:
        gio.check_global_surface_area(area_cube.data.sum())

    iris.save(area_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Calculate the CMIP area variable'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("dummy_file", type=str, help="Dummy file (for horizontal grid information)")
    parser.add_argument("dummy_var", type=str, help="Dummy variable")
    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("outvar", type=str, choices=('areacella', 'areacello'), help="Output variable")

    parser.add_argument("--volcello_file", type=str, default=None,
                        help="Volume file (still need dummy file because of iris issues with reading volcello files)")

    args = parser.parse_args()
    main(args)

