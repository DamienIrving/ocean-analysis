"""Calculate the horizontal basin aggregate"""

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
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def main(inargs):
    """Run the program."""

    agg_functions = {'mean': iris.analysis.MEAN, 'sum': iris.analysis.SUM}
    metadata_dict = {}
    
    basin_cube = iris.load_cube(inargs.basin_file, 'region')
    assert basin_cube.data.min() == 11
    assert basin_cube.data.max() == 18
    basin_numbers = numpy.array([1, 2, 3])
    metadata_dict[inargs.basin_file] = basin_cube.attributes['history']

    flag_values = '0 1 2'
    flag_meanings = 'atlantic indo-pacific globe'
    basin_coord = iris.coords.DimCoord(basin_numbers,
                                       standard_name=basin_cube.standard_name,
                                       long_name=basin_cube.long_name,
                                       var_name=basin_cube.var_name,
                                       units=basin_cube.units,
                                       attributes={'flag_values': flag_values,
                                                   'flag_meanings': flag_meanings})

    if inargs.weights:
        weights_cube = gio.get_ocean_weights(inargs.weights)
        metadata_dict[inargs.weights] = weights_cube.attributes['history']        

    output_cubelist = iris.cube.CubeList([])
    for infile in inargs.infiles:
        print(infile)

        if inargs.var == 'ocean_volume':
            cube = gio.get_ocean_weights(infile)
            history = [cube.attributes['history']]
        else:
            cube, history = gio.combine_files(infile, inargs.var, checks=True)

        assert cube.ndim in [3, 4]
        coord_names = [coord.name() for coord in cube.dim_coords]

        if inargs.annual:
            cube = timeseries.convert_to_annual(cube, chunk=inargs.chunk)   

        assert basin_cube.shape == cube.shape[-2:]
        basin_array = uconv.broadcast_array(basin_cube.data, [cube.ndim - 2, cube.ndim - 1], cube.shape)
        basin_masks = {'atlantic': basin_array > 12,
                       'indo-pacific': (basin_array < 13) | (basin_array > 15),
                       'globe': basin_array > 16}

        if inargs.weights:
            assert weights_cube.data.shape == cube.shape[-3:]
            if cube.ndim == 4:
                weights_array = uconv.broadcast_array(weights_cube.data, [1, 3], cube.shape)
            else:
                weights_array = weights_cube.data
        else:
            weights_array = None

        if cube.ndim == 3:
            outdata = numpy.ma.zeros([cube.shape[0], len(basin_numbers)])
        else:
            outdata = numpy.ma.zeros([cube.shape[0], cube.shape[1], len(basin_numbers)])

        for basin_index, basin_name in enumerate(['atlantic', 'indo-pacific', 'globe']):
            temp_cube = cube.copy()
            mask = basin_masks[basin_name]
            temp_cube.data = numpy.ma.masked_where(mask, temp_cube.data)
            if len(coord_names) == cube.ndim:
                horiz_agg = temp_cube.collapsed(coord_names[-2:], agg_functions[inargs.agg], weights=weights_array).data
            elif inargs.agg == 'mean':
                horiz_agg = numpy.ma.average(temp_cube.data, axis=(-2,-1), weights=weights_array)
            elif inargs.agg == 'sum':
                horiz_agg = numpy.ma.sum(temp_cube.data, axis=(-2,-1))
            if outdata.ndim == 2:
                outdata[:, basin_index] = horiz_agg
            else:
                outdata[:, :, basin_index] = horiz_agg

        coord_list = [(cube.dim_coords[0], 0)]
        if cube.ndim == 4:
            coord_list.append((cube.dim_coords[1], 1))
            coord_list.append((basin_coord, 2))
        else:
            coord_list.append((basin_coord, 1))
        outcube = iris.cube.Cube(outdata,
                                 standard_name=cube.standard_name,
                                 long_name=cube.long_name,
                                 var_name=cube.var_name,
                                 units=cube.units,
                                 attributes=cube.attributes,
                                 dim_coords_and_dims=coord_list)
        output_cubelist.append(outcube)

    iris.util.equalise_attributes(output_cubelist)
    iris.util.unify_time_units(output_cubelist)
    outcube = output_cubelist.concatenate_cube()
    if history:
        metadata_dict[inargs.infiles[-1]] = history[0]
    outcube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(outcube, inargs.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input file")
    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("agg", type=str, choices=('mean', 'sum'), help="Method for horizontal aggregation")
    parser.add_argument("basin_file", type=str, help="Output file")
    parser.add_argument("outfile", type=str, help="Output file")
    
    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")
    parser.add_argument("--weights", type=str, default=None, 
                        help="Weights file for aggregation [default = None]")
    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Perform annual smoothing by year to avoid memory errors [default: False]")

    args = parser.parse_args()
    main(args)
