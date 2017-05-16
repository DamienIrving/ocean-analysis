"""
Filename:     calc_convergence_maps.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate zonal mean ocean heat transport convergence for each ocean basin

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
    assert numpy.max(lat_diffs) == numpy.min(lat_diffs)
    lat_spacing = lat_diffs[0]

    convergence_cube = cube[:, 0:-1].copy()
    convergence_cube.data = numpy.diff(cube.data, axis=1)

    new_lat_coord = convergence_cube.coord('latitude') + (lat_spacing / 2.0)
    convergence_cube.coord('latitude').points = new_lat_coord.points
    convergence_cube.coord('latitude').bounds = new_lat_coord.bounds

    return convergence_cube


def get_history_attribute(data_file, data_cube, basin_file, basin_cube):
    """Generate the history attribute for the output file."""

    history_dict = {data_file: data_cube.attributes['history']}
    if basin_file:
        history_dict[basin_file] = basin_cube.attributes['history']

    return history_dict
        

def read_data(infile_list, var):
    """Read the data files."""

    cube = iris.load(infile_list, gio.check_iris_var(var))

    if var == 'northward_ocean_heat_transport':
        cube = cube.extract(iris.Constraint(region='global_ocean'))
        hfbasin_flag = True
    else:
        hfbasin_flag = False

    return cube, hfbasin_flag


def main(inargs):
    """Run the program."""

    cube, hfbasin_flag = read_data(inargs.infiles, inargs.var)

    atts = cube[0].attributes
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)
    cube.attributes = atts

    orig_standard_name = cube.standard_name
    orig_var_name = cube.var_name

    # Temporal smoothing
    cube = timeseries.convert_to_annual(cube, full_months=True)

    # Mask marginal seas
    if inargs.basin_file and not hfbasin_flag:
        basin_cube = iris.load_cube(inargs.basin_file)
        cube = uconv.mask_marginal_seas(cube, basin_cube)
    else:
        basin_cube = None
        inargs.basin_file = None

    # History
    history_attribute = get_history_attribute(inargs.infiles[0], cube, inargs.basin_file, basin_cube)
    cube.attributes['history'] = gio.write_metadata(file_info=history_attribute)

    # Regrid (if needed)
    if not hfbasin_flag:
        basin_list = ['atlantic', 'pacific', 'indian', 'globe']
        cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)
        if inargs.basin_file and not regrid_status:
            ndim = cube.ndim
            basin_array = uconv.broadcast_array(basin_cube.data, [ndim - 2, ndim - 1], cube.shape) 
        else: 
            basin_array = uconv.create_basin_array(cube)
    else:
        basin_list = ['globe']
        
    # Calculate output for each basin
    out_cubes = []
    for basin_name in basin_list:
        data_cube = cube.copy()
        if not basin_name == 'globe':            
            data_cube.data.mask = numpy.where((data_cube.data.mask == False) & (basin_array == basins[basin_name]), False, True)

        # Zonal mean
        if hfbasin_flag:
            zonal_cube = data_cube
        else:
            zonal_cube = data_cube.collapsed('longitude', iris.analysis.SUM)
            zonal_cube.remove_coord('longitude')

        # Convergence 
        zonal_cube = convergence(zonal_cube)

        # Attributes
        standard_name = 'zonal_integral_%s_convergence_%s' %(orig_standard_name, basin_name)
        var_name = '%s_czi_%s'   %(orig_var_name, basin_name)
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
    
    parser.add_argument("--basin_file", type=str, default=None,
                        help="Cell basin file (for ocean input variables)")

    args = parser.parse_args()            
    main(args)
