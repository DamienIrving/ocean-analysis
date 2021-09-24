"""Calculate seawater coefficientts."""

import sys
script_dir = sys.path[0]
repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.insert(1, module_dir)

import pdb
import argparse

import numpy as np
import gsw
import iris
import cmdline_provenance as cmdprov

import general_io as gio
import convenient_universal as uconv


def _main(args):
    """Run the command line program."""

    bigthetao_cube, bigthetao_history = gio.combine_files(args.temperature_file, 'sea_water_conservative_temperature', checks=True)
    so_cube, so_history = gio.combine_files(args.salinity_file, 'sea_water_salinity', checks=True)

    target_shape = bigthetao_cube.shape[1:]
    depth = bigthetao_cube.coord('depth').points * -1
    broadcast_depth = uconv.broadcast_array(depth, 0, target_shape)
    broadcast_latitude = uconv.broadcast_array(bigthetao_cube.coord('latitude').points, [1, 2], target_shape)
    pressure = gsw.p_from_z(broadcast_depth, broadcast_latitude)

    if args.coefficient == 'alpha':
        coefficient_data = gsw.alpha(bigthetao_cube.data, so_cube.data, pressure)
        var_name = 'alpha'
        standard_name = 'thermal_expansion_coefficient'
        long_name = 'thermal expansion coefficient'
        units = '1/K'
    elif args.coefficient == 'beta':
        coefficient_data = gsw.beta(bigthetao_cube.data, so_cube.data, pressure)
        var_name = 'beta'
        standard_name = 'saline_contraction_coefficient'
        long_name = 'saline contraction coefficient'
        units = 'kg/g'
    else:
        raise ValueError('Coefficient must be alpha or beta')

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}
    coefficient_cube = bigthetao_cube.copy()
    coefficient_cube.data = coefficient_data
    coefficient_cube.standard_name = standard_name    
    coefficient_cube.long_name = long_name
    coefficient_cube.var_name = var_name
    coefficient_cube.units = units

    coefficient_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)
    iris.save(coefficient_cube, args.outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("temperature_file", type=str, help="Input seawater temperature file")
    parser.add_argument("salinity_file", type=str, help="Input seawater salinity file")
    parser.add_argument("coefficient", type=str, choices=('alpha', 'beta'),
                        help='Calculate thermal expansion (alpha) or saline contraction (beta) coefficient')
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--dask_config", type=str,
                        help="YAML file specifying dask client configuration")
    
    args = parser.parse_args()
    _main(args)
    
