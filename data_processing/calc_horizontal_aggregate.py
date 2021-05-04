"""calculate the horizontal (i.e. latitude or longitude) aggregate"""

import sys
script_dir = sys.path[0]
import os
import pdb
import re
import argparse
import numpy
import iris
import iris.util
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
    import convenient_universal as uconv
    import timeseries
    import grids
    import spatial_weights
except ImportError:
    raise ImportError('Script and modules in wrong directories')


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

    assert basin_cube.shape == cube.shape[-2:]
    basin_array = uconv.broadcast_array(basin_cube.data, [cube.ndim - 2, cube.ndim - 1], cube.shape) 
    assert basin_array.min() == 11
    assert basin_array.max() == 18

    basins = {'atlantic': basin_array <= 12,
              'indo-pacific': (basin_array >= 13) & (basin_array <= 15),
              'globe': basin_array <= 16}

    assert basin_name in basins.keys()

    cube.data.mask = numpy.where((cube.data.mask == False) & basins[basin_name], False, True)

    return cube


def horiz_aggregate(cube, coord_names, keep_coord, horiz_bounds, agg_method, weights):
    """Calculate the horizontal aggregate for a given band."""

    horiz_cube = grids.extract_horizontal_region_curvilinear(cube, keep_coord, horiz_bounds)
    if weights and (agg_method == 'mean'):
        extracted_weights_cube = grids.extract_horizontal_region_curvilinear(weights, keep_coord, horiz_bounds)
        extracted_weights_data = extracted_weights_cube.data
    else:
        extracted_weights_data = None
    horiz_agg = horiz_cube.collapsed(coord_names[-2:], agg_method, weights=extracted_weights_data)
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
    if coord_names[0] == 'time':
        assert cube.ndim >= 3
        target_shape.append(cube.shape[0])
        target_coords.append((cube.coord('time'), 0))
        target_horiz_index = 1
        if cube.ndim == 4:
            assert coord_names[1] == 'depth'
            target_shape.append(cube.shape[1])
            target_coords.append((cube.coord('depth'), 1))
            target_horiz_index = 2
    else:
        assert coord_names[0] == 'depth'
        assert cube.ndim == 3
        target_shape.append(cube.shape[0])
        target_coords.append((cube.coord('depth'), 0))
        target_horiz_index = 1
        
    new_horiz_bounds = ref_cube.coord(keep_coord).bounds
    nhoriz = len(new_horiz_bounds)
    target_shape.append(nhoriz)
    
    new_data = numpy.ma.zeros(target_shape)
    for horiz_index in range(0, nhoriz):
        horiz_agg = horiz_aggregate(cube, coord_names, keep_coord,
                                    new_horiz_bounds[horiz_index],
                                    agg_method, weights)
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

    #depth_constraint = gio.iris_vertical_constraint(None, inargs.max_depth)
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
        cube, history = gio.combine_files(filename, inargs.var, checks=True)  #& depth_constraint)

        if inargs.annual:
            cube = timeseries.convert_to_annual(cube)
    
        if basin_cube:
            cube = select_basin(cube, basin_cube, basin_name)
            if inargs.weights:
                weights_cube = select_basin(weights_cube, basin_cube, basin_name)        

        if args.multiply_by_area:
            cube = spatial_weights.multiply_by_area(cube, area_cube=area_cube) 

        if inargs.realm:
            cube = uconv.apply_land_ocean_mask(cube, sftlf_cube, inargs.realm)

        if inargs.weights:
            assert cube.ndim - weights_cube.ndim == 1
            broadcast_weights_cube = cube.copy()
            broadcast_weights_array = uconv.broadcast_array(weights_cube.data, [1, weights_cube.ndim], cube.shape)
            broadcast_weights_cube.data = broadcast_weights_array
        else:
            broadcast_weights_cube = None
            broadcast_weights_array = None
            
        aux_coord_names = [coord.name() for coord in cube.aux_coords]
        if 'latitude' in aux_coord_names:
            # curvilinear grid
            if not ref_cube:
                lats = numpy.arange(-89.5, 90, 1)
                lons = numpy.arange(0.5, 360, 1)
                ref_cube = grids.make_grid(lats, lons)
            horiz_aggregate = curvilinear_agg(cube, ref_cube, keep_coord,
                                              aggregation_functions[inargs.aggregation],
                                              weights=broadcast_weights_cube)
        else:
            # rectilinear grid
            horiz_aggregate = cube.collapsed(collapse_coord, aggregation_functions[inargs.aggregation],
                                             weights=broadcast_weights_array)
            horiz_aggregate.remove_coord(collapse_coord)

        if inargs.flux_to_mag:
            horiz_aggregate = uconv.flux_to_magnitude(horiz_aggregate)
            
        #horiz_aggregate.data = horiz_aggregate.data.astype(numpy.float32)
        output_cubelist.append(horiz_aggregate)

    iris.util.equalise_attributes(output_cubelist)
    iris.util.unify_time_units(output_cubelist)
    output_cubelist = output_cubelist.concatenate_cube()

    if inargs.cumsum:
        output_cubelist = cumsum(output_cubelist)

    metadata_dict[filename] = history[0]
    output_cubelist.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(output_cubelist, inargs.outfile) 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
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
                        help="indo-pacific, atlantic or globe")
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
