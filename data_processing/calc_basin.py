"""
Filename:     calc_basin.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create a CMIP5 basin file

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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def construct_basin_cube(basin_array, global_atts, dim_coords):
    """Construct the new basin cube """

    dim_coords_list = []
    for i, coord in enumerate(dim_coords):
        dim_coords_list.append((coord, i))

    basin_cube = iris.cube.Cube(basin_array,
                                 standard_name='region',
                                 long_name='Region Selection Index',
                                 var_name='basin',
                                 units='1',
                                 attributes=global_atts,
                                 dim_coords_and_dims=dim_coords_list) 

    return basin_cube


def create_basin_array(cube):
    """Create an ocean basin array.

    For similarity with the CMIP5 basin file, in the output:
      Atlantic Ocean = 2
      Pacific Ocean = 3
      Indian Ocean = 5
      (land = 0)

    FIXME: When applied to CMIP5 data, some of the marginal seas might
      not be masked

    """

    lat_coord = cube.coord('latitude')
    lon_coord = cube.coord('longitude')    

    if lat_coord.ndim == 1:
        # rectilinear grid
        lat_axis = lat_coord.points
        lon_axis = uconv.adjust_lon_range(lon_coord.points, radians=False)

        coord_names = [coord.name() for coord in cube.dim_coords]
        lat_index = coord_names.index('latitude')
        lon_index = coord_names.index('longitude')

        lat_array = uconv.broadcast_array(lat_axis, lat_index, cube.shape)
        lon_array = uconv.broadcast_array(lon_axis, lon_index, cube.shape)
    else:
        # curvilinear grid
        assert lon_coord.points.min() > 0
        assert lon_coord.points.max() < 360

        if cube.ndim == 3:
            lat_array = uconv.broadcast_array(lat_coord.points, [1, 2], cube.shape)
            lon_array = uconv.broadcast_array(lon_coord.points, [1, 2], cube.shape)
        else:
            assert cube.ndim == 2
            lat_array = lat_coord.points
            lon_array = lon_coord.points

    pacific_bounds = [147, 294]
    indian_bounds = [23, 147]

    basin_array = numpy.ones(cube.shape) * 2
    basin_array = numpy.where((lon_array >= pacific_bounds[0]) & (lon_array <= pacific_bounds[1]), 3, basin_array)
    basin_array = numpy.where((lon_array >= indian_bounds[0]) & (lon_array <= indian_bounds[1]), 5, basin_array)

    basin_array = numpy.where((basin_array == 3) & (lon_array >= 279) & (lat_array >= 10), 2, basin_array)
    basin_array = numpy.where((basin_array == 5) & (lon_array >= 121) & (lat_array >= 0), 3, basin_array)

    basin_array = numpy.where((basin_array == 5) & (lat_array >= 25), 0, basin_array)

    return basin_array
    
 
def main(inargs):
    """Run the program."""

    # grid information
    data_cube = iris.load_cube(inargs.thetao_file, 'sea_water_potential_temperature')
    coord_names = [coord.name() for coord in data_cube.dim_coords]
    assert coord_names[0] == 'time'
    depth_name = coord_names[1]
    data_cube = data_cube[0, ::]
    data_cube.remove_coord('time')

    basin_array = create_basin_array(data_cube)
    basin_cube = construct_basin_cube(basin_array, data_cube.attributes, data_cube.dim_coords)    
    basin_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)

    iris.save(basin_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Create a CMIP5 basin file'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("thetao_file", type=str, help="Input sea water potential temperature file (for grid information)")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()
    main(args)

