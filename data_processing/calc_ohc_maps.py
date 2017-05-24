"""
Filename:     calc_ohc_maps.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate heat content

"""

# Import general Python modules

import sys, os, pdb
import argparse, math
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
    import convenient_universal as uconv
    import spatial_weights
    import grids
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

agg_abbrevs = {'zm': 'zonal_mean',
               'zs': 'zonal_sum'}


def add_metadata(orig_atts, new_cube, inargs, aggregation=None):
    """Add metadata to the output cube."""

    standard_name = 'ocean_heat_content'
    long_name = 'ocean heat content'
    var_name = 'ohc'
    units = 'J'
    if aggregation:
        assert aggregation in ['zs', 'zm']
        standard_name = standard_name + '_' + agg_abbrevs[aggregation]
        long_name = standard_name.replace('_', ' ')
        var_name = var_name + '_' + aggregation

    if inargs.scaling:
        units = '10^%d %s' %(inargs.scaling, units)
    if not inargs.area_file:
        units = units + ' m-2'
    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}

    new_cube.standard_name = standard_name
    new_cube.long_name = long_name
    new_cube.var_name = var_name
    new_cube.units = units
    new_cube.attributes = orig_atts  

    return new_cube


def calc_ohc_vertical_integral(cube, weights, inargs):
    """Calculate the ohc vertical integral.

    Output: dims = (time, latitude, longitude)

    """

    integral = cube.collapsed('depth', iris.analysis.SUM, weights=weights)
    ohc = (integral * inargs.density * inargs.specific_heat) 
    ohc.remove_coord('depth')
    if inargs.scaling:
        ohc = ohc / (10**inargs.scaling)

    return ohc


def read_climatology(climatology_file, variable, level_subset):
    """Read the optional climatology data."""

    if climatology_file:
        with iris.FUTURE.context(cell_datetime_objects=True):
            climatology_cube = iris.load_cube(climatology_file, variable & level_subset)
    else:
        climatology_cube = None

    return climatology_cube


def read_area(area_file):
    """Read optional areacello file."""

    if area_file:
        area_cube = iris.load_cube(area_file)
    else:
        area_cube = None

    return area_cube      


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def set_attributes(inargs, temperature_cube, climatology_cube, area_cube):
    """Set the attributes for the output cube."""
    
    atts = temperature_cube.attributes

    lev_coord = temperature_cube.coord('depth')
    bounds_info = gio.vertical_bounds_text(lev_coord.points, inargs.min_depth, inargs.max_depth)
    depth_text = 'OHC integrated over %s' %(bounds_info)
    atts['depth_bounds'] = depth_text

    infile_history = {}
    infile_history[inargs.temperature_files[0]] = history[0]
    if climatology_cube:                  
        infile_history[inargs.climatology_file] = climatology_cube.attributes['history']
    if area_cube:
        infile_history[inargs.area_file] = area_cube.attributes['history']

    atts['history'] = gio.write_metadata(file_info=infile_history)

    return atts


def main(inargs):
    """Run the program."""

    level_subset = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    climatology_cube = read_climatology(inargs.climatology_file, inargs.temperature_var, level_subset)
    area_cube = read_area(inargs.area_file)
    temperature_cubes = iris.load(inargs.temperature_files, inargs.temperature_var & level_subset, callback=save_history)
    equalise_attributes(temperature_cubes)
    iris.util.unify_time_units(temperature_cubes)
    atts = set_attributes(inargs, temperature_cubes[0], climatology_cube, area_cube)

    out_cubes = []
    for temperature_cube in temperature_cubes:

        if climatology_cube:
            temperature_cube = temperature_cube - climatology_cube
        if area_cube:
            temperature_cube = temperature_cube * area_cube
        temperature_cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(temperature_cube)

        assert coord_names == ['time', 'depth', 'latitude', 'longitude']
    
        depth_axis = temperature_cube.coord('depth')
        assert depth_axis.units in ['m', 'dbar'], "Unrecognised depth axis units"

        # Calculate heat content
        if depth_axis.units == 'm':
            vertical_weights = spatial_weights.calc_vertical_weights_1D(depth_axis, coord_names, temperature_cube.shape)
        elif depth_axis.units == 'dbar':
            vertical_weights = spatial_weights.calc_vertical_weights_2D(depth_axis, temperature_cube.coord('latitude'), coord_names, temperature_cube.shape)

        ohc_3D = calc_ohc_vertical_integral(temperature_cube, vertical_weights.astype(numpy.float32), inargs)
        ohc_zonal_sum = ohc_3D.collapsed('longitude', iris.analysis.SUM)
        ohc_zonal_sum.remove_coord('longitude')
        ohc_zonal_mean = ohc_3D.collapsed('longitude', iris.analysis.MEAN)
        ohc_zonal_mean.remove_coord('longitude')

        # Create the cube
        ohc_3D.data = ohc_3D.data.astype(numpy.float32)
        ohc_zonal_sum.data = ohc_zonal_sum.data.astype(numpy.float32)
        ohc_zonal_mean.data = ohc_zonal_mean.data.astype(numpy.float32)

        ohc_3D = add_metadata(atts, ohc_3D, inargs)
        ohc_zonal_sum = add_metadata(atts, ohc_zonal_sum, inargs, aggregation='zs')
        ohc_zonal_mean = add_metadata(atts, ohc_zonal_mean, inargs, aggregation='zm')

        ohc_list = iris.cube.CubeList([ohc_3D, ohc_zonal_sum, ohc_zonal_mean])
        out_cubes.append(ohc_list.concatenate())

    cube_list = []
    for var_index in range(len(ohc_list)):
        temp_list = []
        for infile_index in range(len(inargs.temperature_files)):
            temp_list.append(out_cubes[infile_index][var_index])
        
        temp_list = iris.cube.CubeList(temp_list)     
        cube_list.append(temp_list.concatenate_cube())
    
    cube_list = iris.cube.CubeList(cube_list)
    assert cube_list[0].data.dtype == numpy.float32
    iris.save(cube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    The default density and specific heat of seawater are from:
    Hobbs et al (2016). Journal of Climate, 29(5), 1639-1653. doi:10.1175/JCLI-D-15-0477.1

"""

    description='Calculate ocean heat content for a region of interest'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("temperature_files", type=str, nargs='*', help="Input temperature data files")
    parser.add_argument("temperature_var", type=str, help="Input temperature variable name (the standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--climatology_file", type=str, default=None, 
                        help="Input temperature climatology file (required if input data not already anomaly)")

    parser.add_argument("--area_file", type=str, default=None,
                        help="Cell area file (used to remove m-2 from units)")
    
    parser.add_argument("--min_depth", type=float, default=None,
                        help="Only include data below this vertical level")
    parser.add_argument("--max_depth", type=float, default=None,
                        help="Only include data above this vertical level")

    parser.add_argument("--density", type=float, default=1023,
                        help="Density of seawater (in kg.m-3). Default of 1023 kg.m-3 from Hobbs2016.")
    parser.add_argument("--specific_heat", type=float, default=4000,
                        help="Specific heat of seawater (in J / kg.K). Default of 4000 J/kg.K from Hobbs2016")
    
    parser.add_argument("--scaling", type=int, default=None,
                        help="Factor by which to scale heat content (e.g. value of 9 gives units of 10^9 J m-2 or 10^9 J)")

    args = parser.parse_args()             
    main(args)
