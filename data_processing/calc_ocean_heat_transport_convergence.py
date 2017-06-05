"""
Filename:     calc_ocean_heat_transport_convergence.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate zonal mean ocean heat transport convergence for each ocean basin.
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

basins = {'atlantic': 2, 
          'pacific': 3,
          'indian': 5}

def convergence(cube):
    """Calculate convergence and adjust latitude axis accordingly."""

    lat_points = cube.coord('latitude').points
    lat_diffs = numpy.diff(lat_points)

    assert numpy.abs(numpy.max(lat_diffs) - numpy.min(lat_diffs)) < 0.1
    lat_spacing = numpy.mean(lat_diffs)

    convergence_cube = cube[:, 0:-1].copy()
    convergence_cube.data = numpy.diff(cube.data, axis=1) * -1

    new_lat_coord = convergence_cube.coord('latitude') + (lat_spacing / 2.0)
    convergence_cube.coord('latitude').points = new_lat_coord.points
    convergence_cube.coord('latitude').bounds = new_lat_coord.bounds

    return convergence_cube


def get_history_attribute(y_files, y_cube, x_files, x_cube, basin_file, basin_cube):
    """Generate the history attribute for the output file."""

    history_dict = {y_files[0]: y_cube.attributes['history']}
    if x_files:
        history_dict[x_files[0]] = x_cube.attributes['history']
    if basin_file:
        history_dict[basin_file] = basin_cube.attributes['history']

    return history_dict
        

def read_data(infile_list, var, model, basin_cube):
    """Read the data files.

    The CSIRO-Mk3-6-0 model seems to be formatted incorrectly
      and you can't select the "global_ocean" by name

    """
    cube = iris.load(infile_list, gio.check_iris_var(var))
    atts = cube[0].attributes
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)
    cube.attributes = atts

    if var == 'northward_ocean_heat_transport':
        if model == 'CSIRO-Mk3-6-0':
            cube = cube[:, 2, :]
        else:
            cube = cube.extract(iris.Constraint(region='global_ocean'))

    cube = timeseries.convert_to_annual(cube, full_months=True)

    if basin_cube:
        cube = uconv.mask_marginal_seas(cube, basin_cube)

    return cube


def reorient_data(x_cube, y_cube):
    """Orient the x and y data to a regular lat/lon grid."""

    target_grid = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
    new_x_cube, new_y_cube = iris.analysis.cartography.rotate_winds(x_cube, y_cube, target_grid)

    new_x_cube.remove_coord('projection_x_coordinate')
    new_x_cube.remove_coord('projection_y_coordinate')
    new_y_cube.remove_coord('projection_x_coordinate')
    new_y_cube.remove_coord('projection_y_coordinate')

    return new_x_cube, new_y_cube


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
    y_cube = read_data(inargs.infiles, inargs.var, inargs.model, basin_cube)
    orig_standard_name = y_cube.standard_name
    orig_var_name = y_cube.var_name

    x_cube = read_data(inargs.hfx_files, 'ocean_heat_x_transport', basin_cube) if inargs.hfx_files else None
    # Quick fix for NorESM1-m (lat and lon don't match)
    #x_cube.coord('longitude').points = y_cube.coord('longitude').points
    #x_cube.coord('longitude').bounds = y_cube.coord('longitude').bounds
    #x_cube.coord('latitude').points = y_cube.coord('latitude').points
    #x_cube.coord('latitude').bounds = y_cube.coord('latitude').bounds
  
    history_attribute = get_history_attribute(inargs.infiles, y_cube, inargs.hfx_files, x_cube, inargs.basin_file, basin_cube)
    y_cube.attributes['history'] = gio.write_metadata(file_info=history_attribute)

    # Regrid (if needed)
    if not hfbasin:
        if inargs.hfx_files:
            x_cube, y_cube = reorient_data(x_cube, y_cube)
        y_cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(y_cube)

        if inargs.basin_file and not regrid_status:
            ndim = cube.ndim
            basin_array = uconv.broadcast_array(basin_cube.data, [ndim - 2, ndim - 1], cube.shape) 
        else: 
            basin_array = uconv.create_basin_array(y_cube)
        basin_list = ['atlantic', 'pacific', 'indian', 'globe']
    else:
        basin_list = ['globe']
        
    # Calculate output for each basin
    out_cubes = []
    for basin_name in basin_list:
        data_cube = y_cube.copy()
        if not basin_name == 'globe':            
            data_cube.data.mask = numpy.where((data_cube.data.mask == False) & (basin_array == basins[basin_name]), False, True)

        # Zonal mean
        if hfbasin:
            zonal_cube = data_cube
        else:
            zonal_cube = data_cube.collapsed('longitude', iris.analysis.SUM)
            zonal_cube.remove_coord('longitude')

        # Convergence 
        zonal_cube = convergence(zonal_cube)

        # Attributes
        standard_name = 'zonal_sum_%s_convergence_%s' %(orig_standard_name, basin_name)
        var_name = '%s_czs_%s'   %(orig_var_name, basin_name)
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
  The hfx/hfy functionality is still under development.

"""

    description='Calculate zonal mean ocean heat transport convergence for each ocean basin'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input data files")
    parser.add_argument("var", type=str, help="Input variable standard_name")
    parser.add_argument("model", type=str, help="model_id")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--hfx_files", type=str, nargs='*', default=None,
                        help="Required to calculate heat transport if curvilinear grid")
    parser.add_argument("--basin_file", type=str, default=None,
                        help="Cell basin file (for ocean input variables)")

    args = parser.parse_args()            
    main(args)
