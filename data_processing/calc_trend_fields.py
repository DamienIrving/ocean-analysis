"""
Filename:     calc_trend_fields.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Take a 3D (time, lat, lon) variable and calculate the grid point and 
              zonal aggregate trends and climatology for a given time period.  

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
    import timeseries
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

aggregation_functions = {'mean': iris.analysis.MEAN,
                         'sum': iris.analysis.SUM}


def create_mask(mask_cube, target_shape, include_only):
    """Create mask from an sftlf (land surface fraction) file.

    There is no land when cell value == 0

    """

    target_ndim = len(target_shape)

    if include_only == 'land':
        mask_array = numpy.where(mask_cube.data > 50, False, True)
    elif include_only == 'ocean':
        mask_array = numpy.where(mask_cube.data < 50, False, True)

    mask = uconv.broadcast_array(mask_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    return mask


def calc_fields(cube, sftlf_cube, aggregation_method, realm=None, area=False):
    """Calculate the various output fields"""

    if sftlf_cube: 
        cube = mask_regrid_area(cube.copy(), sftlf_cube, realm=realm, area=area)

    assert aggregation_method in ['sum', 'mean']

    # Full field 
    full_trends = calc_trend_cube(cube.copy())
    rename_cube(full_trends, 'trend', None, None, realm)

    full_clim = cube.copy().collapsed('time', iris.analysis.MEAN)
    full_clim.remove_coord('time')
    rename_cube(full_clim, 'climatology', None, None, realm)
    
    # Zonal aggregate
    zonal_aggregate = cube.copy().collapsed('longitude', aggregation_functions[aggregation_method])
    zonal_aggregate.remove_coord('longitude')
    zonal_trends = calc_trend_cube(zonal_aggregate.copy())
    rename_cube(zonal_trends, 'trend', aggregation_method, 'zonal', realm)

    zonal_clim = zonal_aggregate.copy().collapsed('time', iris.analysis.MEAN)
    zonal_clim.remove_coord('time')
    rename_cube(zonal_clim, 'climatology', aggregation_method, 'zonal', realm)

    return full_trends, full_clim, zonal_trends, zonal_clim
    

def rename_cube(cube, temporal_method, aggregation_method, spatial_descriptor, realm):
    """Rename a cube according to the specifics of the analysis"""

    assert temporal_method in ['climatology', 'trend']
    assert aggregation_method in ['sum', 'mean', None]
    assert spatial_descriptor in ['zonal', None]
    assert realm in ['ocean', 'land', None]

    standard_name = cube.standard_name
    long_name = cube.long_name
    var_name = cube.var_name

    if spatial_descriptor:
        standard_name = standard_name + '_' + spatial_descriptor
        long_name = long_name + ' ' + spatial_descriptor
        var_name = var_name + '-' + spatial_descriptor

    if realm:
        standard_name = standard_name + '_' + realm
        long_name = long_name + ' ' + realm
        var_name = var_name + '-' + realm

    if aggregation_method:
        standard_name = standard_name + '_' + aggregation_method
        long_name = long_name + ' ' + aggregation_method
        var_name = var_name + '-' + aggregation_method

    standard_name = standard_name + '_' + temporal_method
    long_name = long_name + ' ' + temporal_method
    if temporal_method == 'climatology':
        var_name = var_name + '-' + 'clim'
    else:
        var_name = var_name + '-' + 'trend'

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': cube.units}
    cube.standard_name = standard_name
    cube.long_name = long_name
    cube.var_name = var_name


def calc_trend_cube(cube):
    """Calculate trend and put into appropriate cube."""
    
    trend_array = timeseries.calc_trend(cube, per_yr=True)
    new_cube = cube[0,:].copy()
    new_cube.remove_coord('time')
    new_cube.data = trend_array
    
    return new_cube


def multiply_by_area(cube):
    """Multiply by cell area."""

    if not cube.coord('latitude').has_bounds():
        cube.coord('latitude').guess_bounds()
    if not cube.coord('longitude').has_bounds():
        cube.coord('longitude').guess_bounds()
    area_weights = iris.analysis.cartography.area_weights(cube)

    units = str(cube.units)
    cube.data = cube.data * area_weights   
    cube.units = units.replace('m-2', '')

    return cube


def mask_regrid_area(cube, sftlf_cube, realm=None, area=False):
    """Mask, regrid and multiply data by area."""

    if realm:
        mask = create_mask(sftlf_cube, cube.shape, realm)
        cube.data = numpy.ma.asarray(cube.data)
        cube.data.mask = mask

    cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)
    if area:
        cube = multiply_by_area(cube)

    return cube


def main(inargs):
    """Run the program."""
 
    if inargs.sftlf_file:
        sftlf_cube = iris.load_cube(inargs.sftlf_file, 'land_area_fraction')
    else:
        sftlf_cube = None

    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()    

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load(inargs.infiles, gio.check_iris_var(inargs.var))
        history = cube[0].attributes['history']

        equalise_attributes(cube)
        iris.util.unify_time_units(cube)
        cube = cube.concatenate_cube()
        cube = gio.check_time_units(cube)
        cube = iris.util.squeeze(cube)
        cube.attributes['history'] = gio.write_metadata(file_info={inargs.infiles[0]: history}) 

        cube = cube.extract(time_constraint)

        cube = timeseries.convert_to_annual(cube, full_months=True)

    output = {}
    output['full'] = calc_fields(cube, sftlf_cube, inargs.aggregation, realm=None, area=inargs.area)
    if inargs.sftlf_file:
        for realm in ['ocean', 'land']:
            output[realm] = calc_fields(cube, sftlf_cube, inargs.aggregation, realm=realm, area=inargs.area)

    cube_list = iris.cube.CubeList()
    for realm, output_cubes in output.items():
        for cube in output_cubes:
            cube_list.append(cube)

    iris.FUTURE.netcdf_no_unlimited = True
    iris.save(cube_list, inargs.outfile, netcdf_format='NETCDF3_CLASSIC')

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Take a 3D (time, lat, lon) variable and calculate the grid point, zonal mean and hemispheric mean trends and climatology for a given time period'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file")                                     

    parser.add_argument("--sftlf_file", type=str, default=None,
                        help="File for calculating land only and ocean only results")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--aggregation", type=str, choices=('mean', 'sum'), default='mean',
                        help="Method for zonal and hemispheric aggregation")
    parser.add_argument("--area", action="store_true", default=False,
	                help="Multiply data by area")


    args = parser.parse_args()             
    main(args)
