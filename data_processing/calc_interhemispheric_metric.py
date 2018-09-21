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
import dask
dask.set_options(get=dask.get) 
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
    import timeseries
    import grids
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def read_data(infile, variable, calc_annual=False, chunk=False):
    """Load the input data."""

    cube = iris.load_cube(infile, gio.check_iris_var(variable))
    cube = gio.check_time_units(cube)

    if calc_annual:
        cube = timeseries.convert_to_annual(cube, chunk=chunk)

    coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    assert 'time' in coord_names
    grid_type = 'curvilinear' if aux_coord_names == ['latitude', 'longitude'] else 'latlon'

    return cube, coord_names, aux_coord_names, grid_type


def calc_spatial_agg(cube, coord_names, aux_coord_names, grid_type,
                     aggregation_method, weights_cube,
                     lat_bounds=None, chunk=False):
    """Load the infiles and calculate the spatial aggregate (sum or mean)."""

    cube = cube.copy() 
    coord_names = coord_names.copy()

    # Extract region
    if lat_bounds:
        if grid_type == 'curvilinear':
            cube = grids.extract_latregion_curvilinear(cube, lat_bounds)
        else:
            cube = grids.extract_latregion_rectilinear(cube, lat_bounds)

    # Get weights       
    if type(weights_cube) == iris.cube.Cube:
        if grid_type == 'latlon' and lat_bounds:
            weights_cube = grids.extract_latregion_rectilinear(weights_cube, lat_bounds)
        weights_array = uconv.broadcast_array(weights_cube.data, [1, weights_cube.ndim], cube.shape)
    elif type(weights_cube) == str:
        assert weights_cube.ndim == 2
        weights_array = spatial_weights.area_array(cube)
    else:
        weights_array = None

    # Calculate spatial aggregate
    coord_names.remove('time')
    if chunk:
        spatial_agg = uconv.chunked_collapse_by_time(cube, coord_names, aggregation_method, weights=weights_array)
    else: 
        spatial_agg = cube.collapsed(coord_names, aggregation_method, weights=weights_array)

    if weights_cube and (aggregation_method == iris.analysis.SUM):
        units = str(spatial_agg.units)
        if weights_cube.ndim == 2:
            spatial_agg.units = units.replace('m-2', '')

    spatial_agg.remove_coord('latitude')
    spatial_agg.remove_coord('longitude')
    try:
        spatial_agg.remove_coord('depth')
    except iris.exceptions.CoordinateNotFoundError:
        pass
    if grid_type == 'curvilinear':
        spatial_agg.remove_coord(coord_names[-2])
        spatial_agg.remove_coord(coord_names[-1])

    return spatial_agg


def rename_cube(cube, quantity):
    """Rename a cube according to the specifics of the analysis"""

    assert quantity in ['globe sum', 'nh sum', 'sh sum', 'minus sh sum', 'div globe sum',
                        'globe mean', 'nh mean', 'sh mean', 'minus sh mean', 'div globe mean',]
    
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


def calc_diff(nh_cube, sh_cube, agg_method):
    """Calculate the difference metric"""
    
    metric = nh_cube.copy()
    metric.data = nh_cube.data - sh_cube.data
    metric = rename_cube(metric, 'minus sh ' + agg_method)  
    
    return metric


def calc_frac(h_cube, globe_cube, agg_method):
    """Calculate the global fraction metric"""

    metric = h_cube.copy()
    metric.data = (h_cube.data / globe_cube.data) * 100
    metric = rename_cube(metric, 'div globe ' + agg_method)  

    metric.units = '%'

    return metric


def update_metadata(cube_list, new_log):
    """Create the cube list for output."""

    for cube in cube_list:
        cube.data = numpy.array(cube.data)  #removes _FillValue attribute
        cube.attributes['history'] = new_log

    return cube_list


def cumsum(cube):
    """Calculate the cumulative sum."""
    
    cube.data = numpy.cumsum(cube.data)
    
    return cube


def combine_cubes(cube_list):
    """Combine two like cubes"""

    equalise_attributes(cube_list)
    iris.util.unify_time_units(cube_list)
    cube = cube_list.concatenate_cube()
    cube = gio.check_time_units(cube)

    return cube


def main(inargs):
    """Run the program."""

    if inargs.weights_file:
        weights_cube = iris.load_cube(inargs.weights_file)
    else:
        weights_cube = None

    agg_methods = {'sum': iris.analysis.SUM, 'mean': iris.analysis.MEAN}
    for file_number, infile in enumerate(inargs.infiles):
        print(infile)
        cube, coord_names, aux_coord_names, grid_type = read_data(infile, inargs.variable, calc_annual=inargs.annual,
                                                                  chunk=inargs.chunk)

        nh_agg = calc_spatial_agg(cube, coord_names, aux_coord_names, grid_type,
                                  agg_methods[inargs.aggregation_method], weights_cube,
                                  lat_bounds=inargs.nh_lat_bounds, chunk=inargs.chunk)
        sh_agg = calc_spatial_agg(cube, coord_names, aux_coord_names, grid_type,
                                  agg_methods[inargs.aggregation_method], weights_cube,
                                  lat_bounds=inargs.sh_lat_bounds, chunk=inargs.chunk)
        globe_agg = calc_spatial_agg(cube, coord_names, aux_coord_names, grid_type,
                                     agg_methods[inargs.aggregation_method], weights_cube,
                                     chunk=inargs.chunk)   

        nh_agg = rename_cube(nh_agg, 'nh ' + inargs.aggregation_method)  
        sh_agg = rename_cube(sh_agg, 'sh ' + inargs.aggregation_method)
        globe_agg = rename_cube(globe_agg, 'globe ' + inargs.aggregation_method) 

        cube_list = iris.cube.CubeList([nh_agg, sh_agg, globe_agg])

        if 'diff' in inargs.metric:
            metric = calc_diff(nh_agg, sh_agg, inargs.aggregation_method)
            cube_list.append(metric)
        if 'global-fraction' in inargs.metric:
            nh_metric = calc_frac(nh_agg, globe_agg, inargs.aggregation_method)
            sh_metric = calc_frac(sh_agg, globe_agg, inargs.aggregation_method)
            cube_list.append(nh_metric)
            cube_list.append(sh_metric)

        if inargs.cumsum:
            cube_list = iris.cube.CubeList(map(uconv.convert_to_joules, cube_list))
            cube_list = iris.cube.CubeList(map(cumsum, cube_list)) 

        if file_number == 0:
            final_cube_list = cube_list
        else:
            for var_num in range(len(cube_list)):
                cube_pair = iris.cube.CubeList([final_cube_list[var_num], cube_list[var_num]])
                final_cube_list[var_num] = combine_cubes(cube_pair)

    new_log = cmdprov.new_log(infile_history={infile: cube.attributes['history']}, git_repo=repo_dir)
    final_cube_list = update_metadata(final_cube_list, new_log)
    iris.save(final_cube_list, inargs.outfile)


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

    parser.add_argument("--weights_file", type=str, default=None, 
                        help="""Input weights file (write 'calculate' to determine from grid info) [default = no weighting]""")

    parser.add_argument("--aggregation_method", type=str, default='sum', choices=('mean', 'sum'),
                        help="calculate the hemispheric sum or mean")
    
    parser.add_argument("--metric", type=str, default=[], nargs='*', choices=('diff', 'global-fraction'),
                        help="output additional metrics")
    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")

    parser.add_argument("--nh_lat_bounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=(0.0, 91.0),
                        help="Northern Hemisphere latitude bounds [default = entire hemisphere]")
    parser.add_argument("--sh_lat_bounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=(-91.0, 0.0),
                        help="Southern Hemisphere latitude bounds [default = entire hemisphere]")

    parser.add_argument("--cumsum", action="store_true", default=False,
                        help="Output the cumulative sum [default: False]")

    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Split input files on time axis to avoid memory errors [default: False]")

    args = parser.parse_args()             
    main(args)
