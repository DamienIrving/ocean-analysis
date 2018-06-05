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

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def read_data(infiles, variable, calc_annual=False, chunk=False):
    """Load the input data."""

    cube = iris.load(infiles, gio.check_iris_var(variable), callback=save_history)
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)

    if calc_annual:
        cube = timeseries.convert_to_annual(cube, chunk=chunk)

    coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    assert 'time' in coord_names
    assert len(coord_names) == 3
    grid_type = 'curvilinear' if aux_coord_names == ['latitude', 'longitude'] else 'latlon'

    infile_history = {}
    infile_history[infiles[0]] = history[0] 
    cube.attributes['history'] = gio.write_metadata(file_info=infile_history)

    return cube, coord_names, aux_coord_names, grid_type


def calc_spatial_agg(cube, coord_names, aux_coord_names, grid_type,
                     aggregation_method, area_cube,
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

    # Get area weights       
    if type(area_cube) == iris.cube.Cube:
        if grid_type == 'latlon' and lat_bounds:
            area_cube = grids.extract_latregion_rectilinear(area_cube, lat_bounds)
        area_weights = uconv.broadcast_array(area_cube.data, [1, 2], cube.shape)
    elif type(area_cube) == str:
        area_weights = spatial_weights.area_array(cube)
    else:
        area_weights = None

    # Calculate spatial aggregate
    coord_names.remove('time')
    if chunk:
        spatial_agg = uconv.chunked_collapse_by_time(cube, coord_names, aggregation_method, weights=area_weights)
    else: 
        spatial_agg = cube.collapsed(coord_names, aggregation_method, weights=area_weights)

    if area_cube and (aggregation_method == iris.analysis.SUM):
        units = str(spatial_agg.units)
        spatial_agg.units = units.replace('m-2', '')
    spatial_agg.remove_coord('latitude')
    spatial_agg.remove_coord('longitude')
    if grid_type == 'curvilinear':
        spatial_agg.remove_coord(coord_names[0])
        spatial_agg.remove_coord(coord_names[1])

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


def update_metadata(cube_list):
    """Create the cube list for output."""

    equalise_attributes(cube_list)

    for cube in cube_list:
        cube.data = numpy.array(cube.data)  #removes _FillValue attribute

    return cube_list


def cumsum(cube):
    """Calculate the cumulative sum."""
    
    cube.data = numpy.cumsum(cube.data)
    
    return cube


def main(inargs):
    """Run the program."""

    cube, coord_names, aux_coord_names, grid_type = read_data(inargs.infiles, inargs.variable, calc_annual=inargs.annual,
                                                              chunk=inargs.chunk)

    if inargs.area_file:
        area_cube = iris.load_cube(inargs.area_file, 'cell_area')
    else:
        area_cube = None
    
    agg_methods = {'sum': iris.analysis.SUM, 'mean': iris.analysis.MEAN}

    nh_agg = calc_spatial_agg(cube, coord_names, aux_coord_names, grid_type,
                              agg_methods[inargs.aggregation_method], area_cube,
                              lat_bounds=inargs.nh_lat_bounds, chunk=inargs.chunk)
    sh_agg = calc_spatial_agg(cube, coord_names, aux_coord_names, grid_type,
                              agg_methods[inargs.aggregation_method], area_cube,
                              lat_bounds=inargs.sh_lat_bounds, chunk=inargs.chunk)
    globe_agg = calc_spatial_agg(cube, coord_names, aux_coord_names, grid_type,
                                 agg_methods[inargs.aggregation_method], area_cube,
                                 chunk=inargs.chunk)   

    nh_agg = rename_cube(nh_agg, 'nh ' + inargs.aggregation_method)  
    sh_agg = rename_cube(sh_agg, 'sh ' + inargs.aggregation_method)
    globe_agg = rename_cube(globe_agg, 'globe ' + inargs.aggregation_method) 

    cube_list = iris.cube.CubeList([nh_agg, sh_agg, globe_agg])

    if inargs.metric == 'diff':
        metric = calc_diff(nh_agg, sh_agg, inargs.aggregation_method)
        cube_list.append(metric)
    elif inargs.metric == 'global-fraction':
        nh_metric = calc_frac(nh_agg, globe_agg, inargs.aggregation_method)
        sh_metric = calc_frac(sh_agg, globe_agg, inargs.aggregation_method)
        cube_list.append(nh_metric)
        cube_list.append(sh_metric)

    if inargs.cumsum:
        cube_list = iris.cube.CubeList(map(uconv.convert_to_joules, cube_list))
        cube_list = iris.cube.CubeList(map(cumsum, cube_list)) 

    cube_list = update_metadata(cube_list)
    iris.save(cube_list, inargs.outfile)


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
                        help="""Input area file (write 'calculate' to determine from grid info) [default = no area weighting]""")

    parser.add_argument("--aggregation_method", type=str, default='sum', choices=('mean', 'sum'),
                        help="calculate the hemispheric sum or mean")
    
    parser.add_argument("--metric", type=str, default=None, choices=('diff', 'global-fraction'),
                        help="output an additional metric")
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
