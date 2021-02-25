"""Calculate tasga from tas"""

import sys
script_dir = sys.path[0]
import os
import pdb
import argparse

import iris
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
    import spatial_weights
    import timeseries
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def main(inargs):
    """Run the program."""

    tas_cube, history = gio.combine_files(inargs.tas_files, inargs.var)
    if inargs.annual:
        tas_cube = timeseries.convert_to_annual(tas_cube)
    area_data = spatial_weights.area_array(tas_cube)
    coord_names = [coord.name() for coord in tas_cube.dim_coords]
    tasga_cube = tas_cube.collapsed(coord_names[1:], iris.analysis.MEAN, weights=area_data)
    tasga_cube.remove_coord(coord_names[1])
    tasga_cube.remove_coord(coord_names[2])

    tasga_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)
    iris.save(tasga_cube, inargs.outfile)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("tas_files", type=str, nargs='*', help="Input tas files")
    parser.add_argument("var", type=str, help="variable standard name")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")

    args = parser.parse_args()
    main(args)
