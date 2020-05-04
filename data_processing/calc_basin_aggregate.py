"""
Filename:     calc_basin_aggregate.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the horizontal basin aggregate
"""

# Import general Python modules

import sys, os, pdb, re
import argparse
import numpy
import iris
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def main(inargs):
    """Run the program."""

    metadata_dict = {}
    
    cube, history = gio.combine_files(inargs.infiles, inargs.var, checks=True)
    assert cube.ndim in [3, 4]
    metadata_dict[inargs.infiles[0]] = history[0]
    coord_names = [coord.name() for coord in cube.dim_coords]
    if inargs.annual:
        cube = timeseries.convert_to_annual(cube)
    
    basin_cube = iris.load_cube(inargs.basin_file, 'region')
    assert basin_cube.shape == cube.shape[-2:]
    assert basin_cube.data.min() == 11
    assert basin_cube.data.max() == 17
    basin_numbers = numpy.array([11, 12, 13, 14, 15, 16, 17, 18])
    metadata_dict[inargs.basin_file] = basin_cube.attributes['history']
    basin_array = uconv.broadcast_array(basin_cube.data, [cube.ndim - 2, cube.ndim - 1], cube.shape)

    if inargs.weights:
        weights_cube = iris.load_cube(inargs.weights)
        assert weights_cube.shape == cube.shape[-3:]
        metadata_dict[inargs.weights] = weights_cube.attributes['history']
        if cube.ndim == 4:
            weights_array = uconv.broadcast_array(weights_cube.data, [1, 3], cube.shape)
        else:
            weights_array = weights_cube.data
    else:
        weights_array = None

    agg_functions = {'mean': iris.analysis.MEAN, 'sum': iris.analysis.SUM}
    if cube.ndim == 3:
        outdata = numpy.ma.zeros([cube.shape[0], len(basin_numbers)])
    else:
        outdata = numpy.ma.zeros([cube.shape[0], cube.shape[1], len(basin_numbers)])

    for basin_index, basin_number in enumerate(basin_numbers):
        temp_cube = cube.copy()
        if basin_number == 18:
            temp_cube.data = numpy.ma.masked_where(basin_array == 17, temp_cube.data)
        else:
            temp_cube.data = numpy.ma.masked_where(basin_array != basin_number, temp_cube.data)
        horiz_agg = temp_cube.collapsed(coord_names[-2:], agg_functions[inargs.agg], weights=weights_array)
        if outdata.ndim == 2:
            outdata[:, basin_index] = horiz_agg.data
        else:
            outdata[:, :, basin_index] = horiz_agg.data

    flag_values = basin_cube.attributes['flag_values'] + ' 18'
    flag_meanings = basin_cube.attributes['flag_meanings'] + ' globe'
    basin_coord = iris.coords.DimCoord(basin_numbers,
                                       standard_name=basin_cube.standard_name,
                                       long_name=basin_cube.long_name,
                                       var_name=basin_cube.var_name,
                                       units=basin_cube.units,
                                       attributes={'flag_values': flag_values,
                                                   'flag_meanings': flag_meanings})

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

    log = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    outcube.attributes['history'] = log

    iris.save(outcube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
"""

    description = 'Calculate the horizontal basin aggregate'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
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

    args = parser.parse_args()
    main(args)
