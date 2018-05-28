"""
Filename:     calc_volume.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the volume

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
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_depth_array(data_cube, depth_name):
    """Get the depth data array"""

    depth_coord = data_cube.coord(depth_name)
    coord_names = [coord.name() for coord in data_cube.dim_coords]

    error_msg =  "Unrecognised depth axis units, " +  str(depth_coord.units)
    assert depth_coord.units in ['m', 'dbar'], error_msg
    if depth_coord.units == 'm':
        depth_interval_array = spatial_weights.calc_vertical_weights_1D(depth_coord, coord_names, data_cube.shape)
    elif depth_coord.units == 'dbar':
        assert coord_names == ['depth', 'latitude', 'longitude'], "2D weights will not work for curvilinear grid"
        depth_interval_array = spatial_weights.calc_vertical_weights_2D(depth_coord, data_cube.coord('latitude'), coord_names, data_cube.shape)

    return depth_interval_array


def construct_volume_cube(volume_data, global_atts, dim_coords):
    """Construct the new volume cube """

    dim_coords_list = []
    for i, coord in enumerate(dim_coords):
        dim_coords_list.append((coord, i))

    volume_cube = iris.cube.Cube(volume_data,
                                 standard_name='ocean_volume',
                                 long_name='Ocean Grid-Cell Volume',
                                 var_name='volcello',
                                 units='m3',
                                 attributes=global_atts,
                                 dim_coords_and_dims=dim_coords_list) 

    return volume_cube

     
def main(inargs):
    """Run the program."""

    # Depth data
    data_cube = iris.load_cube(inargs.thetao_file, 'sea_water_potential_temperature')
    coord_names = [coord.name() for coord in data_cube.dim_coords]
    assert coord_names[0] == 'time'
    depth_name = coord_names[1]
    data_cube = data_cube[0, ::]
    data_cube.remove_coord('time')

    depth_data = get_depth_array(data_cube, depth_name)

    # Area data
    area_cube = iris.load_cube(inargs.area_file)
    area_data = uconv.broadcast_array(area_cube.data, [1, 2], depth_data.shape)

    volume_data = depth_data * area_data
    volume_data = numpy.ma.asarray(volume_data)
    volume_data.mask = data_cube.data.mask
    volume_cube = construct_volume_cube(volume_data, area_cube.attributes, data_cube.dim_coords)    
    volume_cube.attributes['history'] = gio.write_metadata()

    print('Global ocean volume:', volume_cube.data.sum())
    print('(Typical value: 1.3e+18)')    

    iris.save(volume_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Calculate the volume'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("area_file", type=str, help="Input file name")
    parser.add_argument("thetao_file", type=str, help="Input sea water potential temperature file (for depth information)")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()
    main(args)

