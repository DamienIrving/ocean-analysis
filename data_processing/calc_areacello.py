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

def construct_area_cube(area_data, global_atts, dim_coords):
    """Construct the new area cube """

    dim_coords_list = []
    for i, coord in enumerate(dim_coords):
        dim_coords_list.append((coord, i))

    area_cube = iris.cube.Cube(area_data,
                               standard_name='cell_area',
                               long_name='Grid-Cell Area for Ocean Variables',
                               var_name='areacello',
                               units='m2',
                               attributes=global_atts,
                               dim_coords_and_dims=dim_coords_list) 

    return area_cube

     
def main(inargs):
    """Run the program."""

    # Depth data
    pdb.set_trace()
    data_cube = iris.load_cube(inargs.dummy_file, inargs.dummy_var)
    coord_names = [coord.name() for coord in data_cube.dim_coords]
    assert coord_names == ['time', 'latitude', 'longitude']
    data_cube = data_cube[0, ::]
    data_cube.remove_coord('time')

    area_data = spatial_weights.area_array(data_cube)
    area_data.mask = data_cube.data.mask
    area_cube = construct_area_cube(area_data, data_cube.attributes, data_cube.dim_coords)    
    area_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)

    print('Global ocean area:', area_cube.data.sum())
    print('(Typical value: 3.6e+14)')    

    iris.save(area_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Calculate the CMIP5 areacello variable'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("dummy_file", type=str, help="Dummy file (for horizontal grid information)")
    parser.add_argument("dummy_var", type=str, help="Dummy variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()
    main(args)

