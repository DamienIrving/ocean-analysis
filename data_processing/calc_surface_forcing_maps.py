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

basins = {'atlantic': 2, 
          'pacific': 3,
          'indian': 5}

aggregation_functions = {'mean': iris.analysis.MEAN,
                         'sum': iris.analysis.SUM}

aggregation_abbreviations = {'mean': 'zm',
                             'sum': 'zi'}


def get_history_attribute(data_file, data_cube, basin_file, basin_cube, area_file, area_cube):
    """Generate the history attribute for the output file."""

    history_dict = {data_file: data_cube.attributes['history']}
    if basin_file:
        history_dict[basin_file] = basin_cube.attributes['history']
    if area_file:
        history_dict[area_file] = area_cube.attributes['history']

    return history_dict
        

def main(inargs):
    """Run the program."""

    cube = iris.load(inargs.infiles, gio.check_iris_var(inargs.var))

    atts = cube[0].attributes
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)    

    cube.attributes = atts
    orig_long_name = cube.long_name
    orig_standard_name = cube.standard_name
    orig_var_name = cube.var_name

    # Temporal smoothing
    cube = timeseries.convert_to_annual(cube, full_months=True)

    # Mask marginal seas
    if inargs.basin_file:
        basin_cube = iris.load_cube(inargs.basin_file)
        cube = uconv.mask_marginal_seas(cube, basin_cube)
    else:
        basin_cube = None

    # Change units (remove m-2)
    if inargs.area_file:
        area_cube = iris.load_cube(inargs.area_file)        
        cube = cube * area_cube
        cube.attributes = atts
        cube.long_name = orig_long_name
        cube.standard_name = orig_standard_name
        cube.var_name = orig_var_name
    else:
        area_cube = None

    # History
    history_attribute = get_history_attribute(inargs.infiles[0], cube,
                                              inargs.basin_file, basin_cube,
                                              inargs.area_file, area_cube)
    cube.attributes['history'] = gio.write_metadata(file_info=history_attribute)

    # Regrid (if needed)
    cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)
    if inargs.basin_file and not regrid_status:
        ndim = cube.ndim
        basin_array = uconv.broadcast_array(basin_cube.data, [ndim - 2, ndim - 1], cube.shape) 
    else: 
        basin_array = uconv.create_basin_array(cube)

    # Calculate output for each basin
    out_cubes = []
    for basin_name in ['atlantic', 'pacific', 'indian', 'globe']:
        data_cube = cube.copy()
        if not basin_name == 'globe':            
            data_cube.data.mask = numpy.where((data_cube.data.mask == False) & (basin_array == basins[basin_name]), False, True)

        # Zonal statistic
        zonal_cube = data_cube.collapsed('longitude', aggregation_functions[inargs.zonal_stat])
        zonal_cube.remove_coord('longitude')

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

    parser.add_argument("--basin_file", type=str, default=None,
                        help="Cell basin file (for ocean input variables)")
    parser.add_argument("--area_file", type=str, default=None,
                        help="Cell area file (used to remove m-2 from units)")

    args = parser.parse_args()            
    main(args)
