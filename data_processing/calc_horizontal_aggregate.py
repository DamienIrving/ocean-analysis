"""
Filename:     calc_horizontal_aggregate.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  calculate the horizontal (i.e. latitude or longitude) aggregate

"""

# Import general Python modules

import sys, os, pdb, re
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
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
    import timeseries
    import grids
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

aggregation_functions = {'mean': iris.analysis.MEAN,
                         'sum': iris.analysis.SUM}


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def cumsum(cube):
    """Calculate the cumulative sum."""

    cube.data = numpy.cumsum(cube.data, axis=0)
    
    return cube


def select_basin(cube, basin_cube, basin_name):
    """Select an ocean basin."""
    
    basins = {'atlantic': 2, 
              'pacific': 3,
              'indian': 5}

    assert basin_name in basins.keys()

    assert cube.ndim == 4
    basin_array = uconv.broadcast_array(basin_cube.data, [1, 3], cube.shape) 

    cube.data.mask = numpy.where((cube.data.mask == False) & (basin_array == basins[basin_name]), False, True)

    return cube


def multiply_by_area(cube, area_cube):
    """Multiply by cell area."""

    if area_cube:
        assert cube.ndim in [2, 3]
        if cube.ndim == 3:
            area_data = uconv.broadcast_array(area_cube.data, [1, 2], cube.shape)
        else:
            area_data = area_cube.data
    else:
        area_data = spatial_weights.area_array(cube)

    units = str(cube.units)
    cube.data = cube.data * area_data   
    cube.units = units.replace('m-2', '').replace("  ", " ")

    return cube


def horiz_aggregate(cube, coord_names, keep_coord, horiz_bounds, agg_method):
    """Calculate the horizontal aggregate for a given band."""

    horiz_cube = grids.extract_horizontal_region_curvilinear(cube, keep_coord, horiz_bounds)
    horiz_agg = horiz_cube.collapsed(coord_names[-2:], agg_method)
    horiz_agg.remove_coord('latitude')
    horiz_agg.remove_coord('longitude')
    
    for coord_name in coord_names[-2:]:
        try:
            horiz_agg.remove_coord(coord_name)
        except iris.exceptions.CoordinateNotFoundError:
            pass

    return horiz_agg


def curvilinear_agg(cube, ref_cube, keep_coord, agg_method, weights=None):
    """Horizontal aggregation for curvilinear data."""

    coord_names = [coord.name() for coord in cube.dim_coords]
    target_shape = []
    target_coords = []
    target_horiz_index = 0
    if cube.ndim >= 3:
        assert coord_names[0] == 'time'
        target_shape.append(cube.shape[0])
        target_coords.append((cube.coord('time'), 0))
        target_horiz_index = 1

    if cube.ndim == 4:
        assert coord_names[1] == 'depth'
        target_shape.append(cube.shape[1])
        target_coords.append((cube.coord('depth'), 1))
        target_horiz_index = 2

    new_horiz_bounds = ref_cube.coord(keep_coord).bounds
    nhoriz = len(new_horiz_bounds)
    target_shape.append(nhoriz)
    
    new_data = numpy.ma.zeros(target_shape)
    for horiz_index in range(0, nhoriz):
        horiz_agg = horiz_aggregate(cube, coord_names, keep_coord, new_horiz_bounds[horiz_index], agg_method)
        new_data[..., horiz_index] = horiz_agg.data

    target_coords.append((ref_cube.coord(keep_coord), target_horiz_index))
    new_cube = iris.cube.Cube(new_data,
                              standard_name=cube.standard_name,
                              long_name=cube.long_name,
                              var_name=cube.var_name,
                              units=cube.units,
                              attributes=cube.attributes,
                              dim_coords_and_dims=target_coords,)

    return new_cube


def main(inargs):
    """Run the program."""

    keep_coord = 'latitude' if inargs.direction == 'zonal' else 'longitude'
    collapse_coord = 'longitude' if inargs.direction == 'zonal' else 'latitude'

    depth_constraint = gio.iris_vertical_constraint(None, inargs.max_depth)
    metadata_dict = {}

    if inargs.basin:
        basin_file, basin_name = inargs.basin
        basin_cube = iris.load_cube(basin_file, 'region' & depth_constraint)
        metadata_dict[basin_file] = basin_cube.attributes['history']
    else:
        basin_cube = None

    if inargs.area:
        area_cube = iris.load_cube(inargs.area, 'cell_area' & depth_constraint)
    else:
        area_cube = None

    if inargs.weights:
        weights_cube = iris.load_cube(inargs.weights)
        metadata_dict[inargs.weights] = weights_cube.attributes['history']

    if inargs.sftlf_file or inargs.realm:
        assert inargs.sftlf_file and inargs.realm, "Must give --realm and --sftlf_file"
        sftlf_cube = iris.load_cube(inargs.sftlf_file, 'land_area_fraction')

    if inargs.ref_file:
        ref_cube = iris.load_cube(inargs.ref_file[0], inargs.ref_file[1])
    else:
        ref_cube = None

    output_cubelist = iris.cube.CubeList([])
    for fnum, filename in enumerate(inargs.infiles):
        print(filename)
        cube = iris.load_cube(filename, gio.check_iris_var(inargs.var) & depth_constraint)

        if inargs.annual:
            cube = timeseries.convert_to_annual(cube)
    
        if basin_cube:
            cube = select_basin(cube, basin_cube, basin_name)        

        if args.multiply_by_area:
            cube = multiply_by_area(cube, area_cube) 

        if inargs.realm:
            cube = uconv.apply_land_ocean_mask(cube, sftlf_cube, inargs.realm)

        if inargs.weights:
            assert cube.ndim == 3
            broadcasted_weights = uconv.broadcast_array(weights_cube.data, [1, 2], cube.shape)
        else:
            broadcasted_weights = None
            
        aux_coord_names = [coord.name() for coord in cube.aux_coords]
        if 'latitude' in aux_coord_names:
            # curvilinear grid
            assert ref_cube
            horiz_aggregate = curvilinear_agg(cube, ref_cube, keep_coord, aggregation_functions[inargs.aggregation])     
            #TODO: Add weights=broadcasted_weights
        else:
            # rectilinear grid
            horiz_aggregate = cube.collapsed(collapse_coord, aggregation_functions[inargs.aggregation],
                                             weights=broadcasted_weights)
            horiz_aggregate.remove_coord(collapse_coord)

        if inargs.flux_to_mag:
            horiz_aggregate = uconv.flux_to_magnitude(horiz_aggregate)
            
        horiz_aggregate.data = horiz_aggregate.data.astype(numpy.float32)

        if inargs.outfile[-3:] == '.nc':
            output_cubelist.append(horiz_aggregate)
        elif inargs.outfile[-1] == '/': 
            if inargs.cumsum:
                horiz_aggregate = cumsum(horiz_aggregate)       
            infile = filename.split('/')[-1]
            infile = re.sub(cube.var_name + '_', cube.var_name + '-' + inargs.direction + '-' + inargs.aggregation + '_', infile)
            if inargs.annual:
                infile = re.sub('Omon', 'Oyr', infile)
                infile = re.sub('Amon', 'Ayr', infile)
       
            outfile = inargs.outfile + infile
            metadata_dict[filename] = cube.attributes['history'] 
            horiz_aggregate.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)

            iris.save(horiz_aggregate, outfile)
            print('output:', outfile)
            del horiz_aggregate

    if inargs.outfile[-3:] == '.nc':
        equalise_attributes(output_cubelist)
        iris.util.unify_time_units(output_cubelist)
        output_cubelist = output_cubelist.concatenate_cube()

        if inargs.cumsum:
            output_cubelist = cumsum(output_cubelist)

        metadata_dict[filename] = cube.attributes['history']
        output_cubelist.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
        iris.save(output_cubelist, inargs.outfile) 


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate the horizontal (i.e. latitude or longitude) aggregate'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("direction", type=str, choices=('zonal', 'meridional'), help="Calculate the zonal or meridional aggregate")
    parser.add_argument("aggregation", type=str, choices=('mean', 'sum'), help="Method for horizontal aggregation")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--ref_file", type=str, nargs=2, metavar=('FILE', 'VARIABLE'), default=None,
                        help="Reference grid for output (required for curvilinear data) - give file name and variable name")

    parser.add_argument("--realm", type=str, choices=('land', 'ocean'), default=None,
                        help="perform the aggregation over just the ocean or land")
    parser.add_argument("--sftlf_file", type=str, default=None,
                        help="Land fraction file (required if you select a realm")
    parser.add_argument("--basin", type=str, nargs=2, metavar=('BASIN_FILE', 'BASIN_NAME'), default=None,
                        help="indian, pacific or atlantic [default=globe]")
    parser.add_argument("--max_depth", type=float, default=None, 
                        help="Maximum depth selection")
    
    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")
    parser.add_argument("--multiply_by_area", action="store_true", default=False,
                        help="Multiply by area (calculated if necessary) [default=False]")
    parser.add_argument("--area", type=str, default=None, 
                        help="""Multiply data by area (using this file) [default = None]""")
    parser.add_argument("--weights", type=str, default=None, 
                        help="""Weights file for aggregation [default = None]""")

    parser.add_argument("--cumsum", action="store_true", default=False,
                        help="Output the cumulative sum [default: False]")
    parser.add_argument("--flux_to_mag", action="store_true", default=False,
                        help="Convert units from a flux to a magnitude [default: False]")

    args = parser.parse_args()
    if args.area:
        args.multiply_by_area = True
    assert bool(args.sftlf_file) == bool(args.realm), "To select a realm, specify --realm and --sftlf_file"             
    main(args)
