"""
Filename:     calc_heat_budget_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the timeseries for a number of ocean heat
              budget terms

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
    import convenient_universal as uconv
    import spatial_weights
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

region_bounds = {}
region_bounds['globe'] = None
region_bounds['nh'] = [0, 91]
region_bounds['sh'] = [-91, 0]
region_bounds['shext'] = [-91, -30]
region_bounds['tropics'] = [-30, 30]
region_bounds['nhext'] = [30, 91]


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def convert_to_joules(cube):
    """Convert units to Joules"""

    assert 'W' in str(cube.units)
    assert 'days' in str(cube.coord('time').units)
    
    time_span_days = cube.coord('time').bounds[:, 1] - cube.coord('time').bounds[:, 0]
    time_span_seconds = time_span_days * 60 * 60 * 24
    
    cube.data = cube.data * uconv.broadcast_array(time_span_seconds, 0, cube.shape)
    cube.units = str(cube.units).replace('W', 'J')
    
    return cube
    

def read_data(infiles, variable, time_constraint):
    """Load the input data."""

    cube = iris.load(infiles, gio.check_iris_var(variable), callback=save_history)
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)

    cube = cube.extract(time_constraint)  
    cube = timeseries.convert_to_annual(cube, aggregation='mean')  ## or sum??? 

    if str(cube.units) != 'J':
        cube = convert_to_joules(cube)
        
    coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    assert 'time' in coord_names
    assert len(coord_names) == 3
    grid_type = 'curvilinear' if aux_coord_names == ['latitude', 'longitude'] else 'latlon'

    return cube, coord_names, aux_coord_names, grid_type


def calc_region_sum(cube, coord_names, aux_coord_names, grid_type, area_cube, region):
    """Calculate the spatial sum."""

    cube = cube.copy() 
    coord_names = coord_names.copy()
    lat_bounds = region_bounds[region]

    # Extract region
    if lat_bounds:
        if grid_type == 'curvilinear':
            assert area_cube, "Must provide an area cube of curvilinear data"
            cube = extract_region_curvilinear(cube, lat_bounds)
        else:
            cube = extract_region_latlon(cube, lat_bounds)

    coord_names.remove('time')
    if 'm-2' in str(cube.units):
        # Get area weights       
        if area_cube:
            if grid_type == 'latlon' and lat_bounds:
                area_cube = extract_region_latlon(area_cube, lat_bounds)
            area_weights = uconv.broadcast_array(area_cube.data, [1, 2], cube.shape)
        else:
            area_weights = spatial_weights.area_array(cube)

        # Calculate spatial aggregate
        spatial_agg = cube.collapsed(coord_names, iris.analysis.SUM, weights=area_weights)
        units = str(spatial_agg.units)
        spatial_agg.units = units.replace('m-2', '')
    else:
        spatial_agg = cube.collapsed(coord_names, iris.analysis.SUM)
    
    spatial_agg.remove_coord('latitude')
    spatial_agg.remove_coord('longitude')
    if grid_type == 'curvilinear':
        spatial_agg.remove_coord(coord_names[0])
        spatial_agg.remove_coord(coord_names[1])

    return spatial_agg


def extract_region_curvilinear(cube, lat_bounds):
    """Extract region of interest from a curvilinear grid."""

    cube = cube.copy() 
 
    region_mask = create_region_mask(cube.coord('latitude').points, cube.shape, lat_bounds)
    land_ocean_mask = cube.data.mask
    complete_mask = region_mask + land_ocean_mask

    cube.data = numpy.ma.asarray(cube.data)
    cube.data.mask = complete_mask

    return cube


def extract_region_latlon(cube, lat_bounds):
    """Extract region of interest from a regular lat/lon grid."""

    southern_lat, northern_lat = lat_bounds
    lat_constraint = iris.Constraint(latitude=lambda cell: southern_lat <= cell < northern_lat)
    cube = cube.extract(lat_constraint)

    return cube

    
def create_region_mask(latitude_array, target_shape, lat_bounds):
    """Create mask from the latitude auxillary coordinate"""

    target_ndim = len(target_shape)

    southern_lat, northern_lat = lat_bounds
    mask_array = numpy.where((latitude_array >= southern_lat) & (latitude_array < northern_lat), False, True)

    mask = uconv.broadcast_array(mask_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    return mask


def rename_cube(cube, quantity):
    """Rename a cube according to the specifics of the analysis"""
    
    if cube.standard_name:
        standard_name = '_'.join([cube.standard_name, quantity.replace(' ', '_')])
    else:
        standard_name = '_'.join([cube.long_name.replace(' ', '_'), quantity.replace(' ', '_')])
    long_name = ' '.join([cube.long_name, quantity])  
    var_name = '-'.join([cube.var_name, quantity.replace(' ', '-')])

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': cube.units}
    cube.standard_name = standard_name
    cube.long_name = long_name
    cube.var_name = var_name
    
    return cube


def update_metadata(cube_list, infile_history):
    """Create the cube list for output."""

    equalise_attributes(cube_list)

    for cube in cube_list:
        cube.attributes['history'] = gio.write_metadata(file_info=infile_history)
        cube.data = numpy.array(cube.data)  #removes _FillValue attribute

    return cube_list


def calc_regional_values(infiles, variable, time_constraint, area_cube):
    """Integrate over each region of interest."""

    cube, coord_names, aux_coord_names, grid_type = read_data(infiles, variable, time_constraint)

    cube_list = iris.cube.CubeList([])
    for region in ['globe', 'nh', 'sh', 'nhext', 'tropics', 'shext']:
        region_sum = calc_region_sum(cube, coord_names, aux_coord_names, grid_type, area_cube, region)
        region_sum = rename_cube(region_sum, region + ' sum')
        cube_list.append(region_sum)

    return cube_list  

        
def main(inargs):
    """Run the program."""
 
    if inargs.area_file:
        area_cube = iris.load_cube(inargs.area_file, 'cell_area')
    else:
        area_cube = None

    time_constraint = gio.get_time_constraint(inargs.time)

    ohc_cube_list = calc_regional_values(inargs.ohc_files, 'ocean_heat_content', time_constraint, area_cube)
    hfds_cube_list = calc_regional_values(inargs.hfds_files, 'surface_downward_heat_flux_in_sea_water', time_constraint, area_cube)

    cube_list = ohc_cube_list + hfds_cube_list

    infile_history = {}
    infile_history[inargs.ohc_files[0]] = history[0] 
    infile_history[inargs.hfds_files[-1]] = history[-1]
    cube_list = update_metadata(cube_list, infile_history)

    iris.save(cube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

details:
    Calculates the annual mean surface heat flux and ocean heat content
    integrated over the following regions: globe, NH, SH, tropics, NH extratropics
    and SH extratropics. 

    Also gives the northward ocean heat trasport at the boundaries between these regions
    (30S, equator, 30N)
 
"""

    description = 'Calculate the timeseries for a number of ocean heat budget terms'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--ohc_files", type=str, nargs='*', required=True,
                        help="ocean heat content files (from calc_ohc.py)")
    parser.add_argument("--hfds_files", type=str, nargs='*', required=True,
                        help="surface downwarwd heat flux files (possibly from calc_hfds_inferred.py)")

    parser.add_argument("--area_file", type=str, default=None, 
                        help="Input area file [required for non lat/lon grids]")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
