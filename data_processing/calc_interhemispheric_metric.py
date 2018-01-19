"""
Filename:     calc_interhemispheric_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the interhemispheric timeseries for a general input variable

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
iris.FUTURE.netcdf_promote = True

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

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def calc_agg(infiles, variable, area_cube, lat_bounds=None):
    """Load the infiles and calculate the hemispheric mean value."""
    
    # Read data
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load(infiles, variable, callback=save_history)
        equalise_attributes(cube)
        iris.util.unify_time_units(cube)
        cube = cube.concatenate_cube()
        cube = gio.check_time_units(cube)
        cube = timeseries.convert_to_annual(cube) 
    
    # Extract region
    cube, grid_type = extract_region(cube, lat_bounds)
    if grid_type == 'curvilinear':
        assert area_cube, "Must provide an area cube of curvilinear data"
    if area_cube:
        if grid_type == 'latlon':
            area_cube = extract_region(area_cube, lat_bounds)
        area_weights = area_cube.data
    else:
        area_weights = spatial_weights.area_array(cube)

    agg = cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=area_weights)
    agg.remove_coord('longitude')
    agg.remove_coord('latitude')

    return agg


def extract_region(cube, lat_bounds):
    """Extract region of interest."""

    cube = cube.copy() 
    coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]

    if aux_coord_names == ['latitude', 'longitude']:
        assert 'time' in coord_names
        assert len(coord_names) == 3
        region_mask = create_region_mask(cube.coord('latitude').points, cube.shape, lat_bounds)
        land_ocean_mask = cube.data.mask
        complete_mask = region_mask + land_ocean_mask

        cube.data = numpy.ma.asarray(cube.data)
        cube.data.mask = complete_mask

        grid_type = 'curvilinear'
    else:
        southern_lat, northern_lat = lat_bounds
        lat_constraint = iris.Constraint(latitude=lambda cell: southern_lat <= cell < northern_lat)
        cube = cube.extract(lat_constraint)
        grid_type = 'latlon'

    return cube, grid

    
def create_region_mask(latitude_array, target_shape, lat_bounds):
    """Create mask from the latitude auxillary coordinate"""

    target_ndim = len(target_shape)

    southern_lat, northern_lat = lat_bounds
    mask_array = numpy.where((latitude_array >= southern_lat) & (latitude_array < northern_lat), False, True)

    mask = uconv.broadcast_array(mask_array, [target_ndim - 2, target_ndim - 1], target_shape)
    assert mask.shape == target_shape 

    return mask


def update_history(cube, infiles):
    """Update the history attribute"""
    
    infile_history = {}
    infile_history[infiles[0]] = history[0] 
 
    cube.attributes['history'] = gio.write_metadata(file_info=infile_history)

    return cube


def calc_metric(nh_mean, sh_mean):
    """Calculate the metric"""
    
    metric = nh_mean.copy()
    metric.data = nh_mean.data - sh_mean.data
    
    return metric




def main(inargs):
    """Run the program."""

    if inargs.area_file:
        area_cube = iris.load_cube(inargs.area_file, 'cell_area')
    else:
        area_cube = None

    nh_lower, nh_upper = inargs.nh_lat_bounds
    nh_constraint = iris.Constraint(latitude=lambda cell: nh_lower <= cell < nh_upper)

    sh_lower, sh_upper = inargs.sh_lat_bounds
    sh_constraint = iris.Constraint(latitude=lambda cell: sh_lower <= cell < sh_upper)

    global_constraint = iris.Constraint()

    nh_agg = calc_agg(inargs.infiles, inargs.variable, area_cube, lat_bounds=inargs.nh_lat_bounds)
    sh_agg = calc_agg(inargs.infiles, inargs.variable, area_cube, lat_bounds=inargs.sh_lat_bounds)
    global_agg = calc_agg(inargs.infiles, inargs.variable, area_cube)     

    pdb.set_trace()

    #metric = calc_metric(nh_agg, sh_agg)    
    #metric = update_history(metric, inargs.infiles)

    #iris.save(metric, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate the interhemispheric timeseries for a general input variable'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")            
    parser.add_argument("variable", type=str, help="Input variable")                                                 
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--area_file", type=str, default=None, 
                        help="Input area file [required for non lat/lon grids]")

    parser.add_argument("--aggregation_method", type=str, default='sum', choices=('mean', 'sum'),
                        help="calculate the hemispheric sum or mean")

    parser.add_argument("--nh_lat_bounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=(0.0, 91.0),
                        help="Northern Hemisphere latitude bounds [default = entire hemisphere]")
    parser.add_argument("--sh_lat_bounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=(-91.0, 0.0),
                        help="Southern Hemisphere latitude bounds [default = entire hemisphere]")

    args = parser.parse_args()             
    main(args)
