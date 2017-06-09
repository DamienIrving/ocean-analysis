"""
Filename:     calc_surface_forcing_maps.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate zonal mean surface forcing for each ocean basin

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

basins = {'atlantic': 2, 
          'pacific': 3,
          'indian': 5}

aggregation_functions = {'mean': iris.analysis.MEAN,
                         'sum': iris.analysis.SUM}

aggregation_abbreviations = {'mean': 'zm',
                             'sum': 'zs'}


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def get_history_attribute(data_file, data_history):
    """Generate the history attribute for the output file."""

    history_dict = {data_file: data_history}

    return history_dict
        

def multiply_by_area(cube, area_option):
    """Multiply by cell area."""

    if '.nc' in area_option:
        area_cube = iris.load_cube(area_option)
        area_weights = area_cube.data
    else:
        if not cube.coord('latitude').has_bounds():
            cube.coord('latitude').guess_bounds()
        if not cube.coord('longitude').has_bounds():
            cube.coord('longitude').guess_bounds()
        area_weights = iris.analysis.cartography.area_weights(cube)

    units = str(cube.units)
    cube = cube * area_weights   
    cube.units = units.replace('m-2', '')

    return cube


def main(inargs):
    """Run the program."""

    cube = iris.load(inargs.infiles, gio.check_iris_var(inargs.var), callback=save_history)

    atts = cube[0].attributes
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)    

    cube.attributes = atts
    orig_long_name = cube.long_name
    if cube.standard_name == None:
        orig_standard_name = orig_long_name.replace(' ', '_')
    else:
        orig_standard_name = cube.standard_name
    orig_var_name = cube.var_name

    # Temporal smoothing
    cube = timeseries.convert_to_annual(cube, full_months=True)

    # Mask marginal seas
    if inargs.basin:
        if '.nc' in inargs.basin:
            basin_cube = iris.load_cube(inargs.basin_file)
            cube = uconv.mask_marginal_seas(cube, basin_cube)
        else:
            basin_cube = 'create'
    else:
        basin_cube = None

    # Regrid (if needed)
    if inargs.regrid:
        cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)

    # Change units (remove m-2)
    if inargs.area:
        cube = multiply_by_area(cube, inargs.area)
        cube.attributes = atts
        cube.long_name = orig_long_name
        cube.standard_name = orig_standard_name
        cube.var_name = orig_var_name

    # History
    history_attribute = get_history_attribute(inargs.infiles[0], history[0])
    cube.attributes['history'] = gio.write_metadata(file_info=history_attribute)

    # Calculate output for each basin
    if type(basin_cube) == iris.cube.Cube:
        ndim = cube.ndim
        basin_array = uconv.broadcast_array(basin_cube.data, [ndim - 2, ndim - 1], cube.shape) 
        basin_list = ['atlantic', 'pacific', 'indian', 'globe']
    elif type(basin_cube) == str: 
        basin_array = uconv.create_basin_array(cube)
        basin_list = ['atlantic', 'pacific', 'indian', 'globe']
    else:
        basin_array = None
        basin_list = ['globe']

    dim_coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    assert len(dim_coord_names) == 3
    assert dim_coord_names[0] == 'time'
    x_axis = dim_coord_names[2]    

    for aux_coord in aux_coord_names:
        cube.remove_coord(aux_coord)

    out_cubes = []
    for basin_name in basin_list:
        data_cube = cube.copy()
        if not basin_name == 'globe':            
            data_cube.data.mask = numpy.where((data_cube.data.mask == False) & (basin_array == basins[basin_name]), False, True)

        # Zonal statistic
        zonal_cube = data_cube.collapsed(x_axis, aggregation_functions[inargs.zonal_stat])
        zonal_cube.remove_coord(x_axis)

        # Attributes
        standard_name = 'zonal_%s_%s_%s' %(inargs.zonal_stat, orig_standard_name, basin_name)
        var_name = '%s_%s_%s'   %(orig_var_name, aggregation_abbreviations[inargs.zonal_stat], basin_name)
        iris.std_names.STD_NAMES[standard_name] = {'canonical_units': zonal_cube.units}

        zonal_cube.standard_name = standard_name
        zonal_cube.long_name = standard_name.replace('_', ' ')
        zonal_cube.var_name = var_name   

        out_cubes.append(zonal_cube)

    out_cubes = iris.cube.CubeList(out_cubes)
    iris.save(out_cubes, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com

note:
  Calculate zonal mean surface forcing for each ocean basin

"""

    description=''
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input data files")
    parser.add_argument("var", type=str, help="Input variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--zonal_stat", type=str, choices=('mean', 'sum'), default='mean',
                        help="Zonal statistic")
    parser.add_argument("--area", type=str, default=False,
                        help="Multiply input data by area (give area file name or write auto if no area file available but infiles on regular lat/lon grid)")
    parser.add_argument("--basin", type=str, default=None,
                        help="Provide output for each ocean basin (give basin file name or write auto if no basin file available but infiles on regular lat/lon grid)")
    parser.add_argument("--regrid", action="store_true", default=False,
                        help="Regrid to a regular lat/lon grid")

    args = parser.parse_args()            
    main(args)
