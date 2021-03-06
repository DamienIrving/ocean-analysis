"""
Filename:     calc_volcello.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the CMIP5 volcello variable

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

def construct_volume_cube(volume_data, data_cube, global_atts):
    """Construct the new volume cube """

    volume_cube = data_cube.copy()
    volume_cube.data = volume_data
    volume_cube.standard_name = 'ocean_volume'
    volume_cube.long_name = 'Ocean Grid-Cell Volume'
    volume_cube.var_name = 'volcello'
    volume_cube.units = 'm3'
    volume_cube.cell_methods = ()
    if global_atts:
        volume_cube.attributes = global_atts
                              
    return volume_cube

     
def main(inargs):
    """Run the program."""

    # Depth data
    data_cube = iris.load_cube(inargs.dummy_file, inargs.dummy_var)
    dim_coord_names = [coord.name() for coord in data_cube.dim_coords]
    aux_coord_names = [coord.name() for coord in data_cube.aux_coords]
    assert dim_coord_names[0] == 'time'
    depth_name = dim_coord_names[1]
    data_cube = data_cube[0, ::]
    data_cube.remove_coord('time')
    depth_data = spatial_weights.get_depth_array(data_cube, depth_name)
    # Area data
    if inargs.area_file:
        area_cube = iris.load_cube(inargs.area_file, 'cell_area')
        gio.check_global_ocean_area(area_cube.data.sum())
        area_data = uconv.broadcast_array(area_cube.data, [1, 2], depth_data.shape)
    else:
        area_data = spatial_weights.area_array(data_cube)
    
    volume_data = depth_data * area_data
    
    if inargs.sftof_file:
        sftof_cube = iris.load_cube(inargs.sftof_file)
        assert sftof_cube.data.max() == 100
        sftof_data = uconv.broadcast_array(sftof_cube.data, [1, 2], depth_data.shape)
        volume_data = volume_data * (sftof_data / 100.0)

    volume_data = numpy.ma.asarray(volume_data)
    data = numpy.ma.masked_invalid(data_cube.data)
    volume_data.mask = data.mask
    global_atts = area_cube.attributes if inargs.area_file else None
    volume_cube = construct_volume_cube(volume_data, data_cube, global_atts)    
    volume_cube.attributes['history'] = gio.write_metadata()

    gio.check_global_ocean_volume(volume_cube.data.sum()) 

    iris.save(volume_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Calculate the CMIP volcello variable'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("dummy_file", type=str, help="Dummy file (for depth information)")
    parser.add_argument("dummy_var", type=str, help="Dummy variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--sftof_file", type=str, default=None,
                        help="Sea area fraction file name")
    parser.add_argument("--area_file", type=str, default=None,
                        help="Area file name (required for curvilinear grids, optional otherwise)")

    args = parser.parse_args()
    main(args)

