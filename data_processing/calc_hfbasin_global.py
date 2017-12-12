"""
Filename:     calc_hfbasin_global.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate zonal mean northward ocean heat transport for the global ocean.
              Can handle hfbasin or hfy/hfx data.

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes

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
    import grids
    import timeseries
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def get_history_attribute(y_files, data_cube, basin_file, basin_cube):
    """Generate the history attribute for the output file."""

    history_dict = {y_files[0]: data_cube.attributes['history']}
    if basin_file:
        history_dict[basin_file] = basin_cube.attributes['history']

    return history_dict
        

def read_data(infile_list, var, basin_cube):
    """Read the data files.

    The CSIRO-Mk3-6-0 model seems to be formatted incorrectly
      and you can't select the "global_ocean" by name

    """
    cube = iris.load(infile_list, gio.check_iris_var(var), callback=save_history)
    atts = cube[0].attributes
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)
    cube.attributes = atts
    cube.attributes['history'] = history[0]
    model = atts['model_id']

    if var == 'northward_ocean_heat_transport':
        if model == 'CSIRO-Mk3-6-0':
            cube = cube[:, 2, :]
        else:
            cube = cube.extract(iris.Constraint(region='global_ocean'))

    cube = timeseries.convert_to_annual(cube, full_months=True)

    if basin_cube:
        cube = uconv.mask_marginal_seas(cube, basin_cube)

    return cube


def main(inargs):
    """Run the program."""

    # Basin data
    hfbasin = True if inargs.var == 'northward_ocean_heat_transport' else False
    if inargs.basin_file and not hfbasin:
        basin_cube = iris.load_cube(inargs.basin_file)
    else:
        basin_cube = None
        inargs.basin_file = None

    # Heat transport data
    data_cube = read_data(inargs.infiles, inargs.var, basin_cube)
    orig_standard_name = data_cube.standard_name
    orig_var_name = data_cube.var_name
  
    history_attribute = get_history_attribute(inargs.infiles, data_cube, inargs.basin_file, basin_cube)
    data_cube.attributes['history'] = gio.write_metadata(file_info=history_attribute)

    # Regrid (if needed)
    if inargs.regrid:
        data_cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(data_cube)

    dim_coord_names = [coord.name() for coord in data_cube.dim_coords]
    aux_coord_names = [coord.name() for coord in data_cube.aux_coords]
    
    regular_grid = False if aux_coord_names else True

    if hfbasin:
        assert len(dim_coord_names) == 2
        assert dim_coord_names[0] == 'time'
        y_axis_name = dim_coord_names[1]
    else:
        assert len(dim_coord_names) == 3
        assert dim_coord_names[0] == 'time'
        y_axis_name, x_axis_name = dim_coord_names[1:]    
        for aux_coord in aux_coord_names:
            data_cube.remove_coord(aux_coord)

    # Basin array
    if inargs.basin_file and not inargs.regrid:
        ndim = cube.ndim
        basin_array = uconv.broadcast_array(basin_cube.data, [ndim - 2, ndim - 1], cube.shape) 
    elif regular_grid and not hfbasin: 
        basin_array = uconv.create_basin_array(data_cube)

    # Calculate output for global ocean
    data_cube_copy = data_cube.copy()
 
    if hfbasin:
        zonal_cube = data_cube_copy
    else:
        zonal_cube = data_cube_copy.collapsed(x_axis_name, iris.analysis.SUM)
        zonal_cube.remove_coord(x_axis_name)

    # Attributes
    standard_name = 'northward_ocean_heat_transport'
    var_name = 'hfbasin'

    zonal_cube.standard_name = standard_name
    zonal_cube.long_name = standard_name.replace('_', ' ')
    zonal_cube.var_name = var_name   

    iris.save(zonal_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com

"""

    description='Calculate zonal mean northward ocean heat transport for the global ocean'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input data files")
    parser.add_argument("var", type=str, help="Input variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--basin_file", type=str, default=None,
                        help="Cell basin file (used to mask marginal seas)")
    
    parser.add_argument("--regrid", action="store_true", default=False,
                        help="Regrid to a regular lat/lon grid")

    args = parser.parse_args()            
    main(args)
