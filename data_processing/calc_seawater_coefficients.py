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

    temperature_cube, temperature_history = gio.combine_files(args.temperature_file, args.temperature_var, checks=True)
    salinity_cube, salinity_history = gio.combine_files(args.salinity_file, 'sea_water_salinity', checks=True)
   
    assert 'c' in str(temperature_cube.units).lower(), "Input temperature units must be in celsius"
#    if not 'C' in str(bigthetao_cube.units):
#        bigthetao_cube.data = bigthetao_cube.data - 273.15
#        data_median = np.ma.median(bigthetao_cube.data)
#        assert data_median < 100
#        assert data_median > -10
#        bigthetao_cube.units = 'C'

    target_shape = temperature_cube.shape[1:]
    depth = temperature_cube.coord('depth').points * -1
    broadcast_depth = uconv.broadcast_array(depth, 0, target_shape)
    broadcast_longitude = uconv.broadcast_array(temperature_cube.coord('longitude').points, [1, 2], target_shape)
    broadcast_latitude = uconv.broadcast_array(temperature_cube.coord('latitude').points, [1, 2], target_shape)
    pressure = gsw.p_from_z(broadcast_depth, broadcast_latitude)

    absolute_salinity = gsw.SA_from_SP(so_cube.data, pressure, broadcast_longitude, broadcast_latitude)
    if args.temperature_var == 'sea_water_conservative_temperature':
        conservative_temperature = temperature_cube.data
    elif args.temperature_var == 'sea_water_potential_temperature':  
        conservative_temperature = gsw.CT_from_pt(absolute_salinity, temperature_cube.data)
    else:
        raise ValueError('Invalid temperature variable')

    if args.coefficient == 'alpha':
        coefficient_data = gsw.alpha(absolute_salinity, conservative_temperature, pressure)
        var_name = 'alpha'
        standard_name = 'thermal_expansion_coefficient'
        long_name = 'thermal expansion coefficient'
        units = '1/K'
    elif args.coefficient == 'beta':
        coefficient_data = gsw.beta(absolute_salinity, conservative_temperature, pressure)
        var_name = 'beta'
        standard_name = 'saline_contraction_coefficient'
        long_name = 'saline contraction coefficient'
        units = 'kg/g'
    else:
        raise ValueError('Coefficient must be alpha or beta')

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}
    coefficient_cube = temperature_cube.copy()
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

    parser.add_argument("salinity_file", type=str, help="Input seawater salinity file")                                     
    parser.add_argument("temperature_file", type=str, help="Input seawater temperature file")
    parser.add_argument("temperature_var", type=str, help="Input seawater temperature variable",
                        choices=('sea_water_conservative_temperature', 'sea_water_potential_temperature'))
    parser.add_argument("coefficient", type=str, choices=('alpha', 'beta'),
                        help='Calculate thermal expansion (alpha) or saline contraction (beta) coefficient')
    parser.add_argument("outfile", type=str, help="Output file")
    
    args = parser.parse_args()
    _main(args)
    
