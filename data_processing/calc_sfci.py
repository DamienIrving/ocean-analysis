"""Calculate the (binned) total internal surface forcing."""

import sys
script_dir = sys.path[0]
import os
import pdb
import argparse

import numpy as np
import iris
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-1])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def main(inargs):
    """Run the program."""
 
    sfc_tbin_cube = iris.load_cube(inargs.sfc_file, 'total surface forcing binned by temperature')
    wfo_tbin_cube = iris.load_cube(inargs.wfo_file, 'Water Flux into Sea Water binned by temperature')
    cp = 3992.10322329649   #J kg-1 degC-1
    lower_thetao_bounds = sfc_tbin_cube.coord('sea_water_potential_temperature').bounds[:, 0]
    coord_names = [coord.name() for coord in sfc_tbin_cube.dim_coords]
    pdb.set_trace()
    theta = uconv.broadcast_array(lower_thetao_bounds, 1, sfc_tbin_cube.shape)
    sfci_tbin_cube = sfc_tbin_cube.copy()
    sfci_tbin_cube.data = sfc_tbin_cube.data - (cp * theta * wfo_tbin_cube.data)  # SFCI = SFC - Cp*THETA*SVF
    sfci_tbin_cube.var_name = 'sfci_tbin'
    sfci_tbin_cube.long_name = 'total internal surface forcing binned by temperature'
    metadata = {inargs.sfc_file: sfc_tbin_cube.attributes['history'],
                inargs.wfo_file: wfo_tbin_cube.attributes['history']}
    log = cmdprov.new_log(infile_history=metadata, git_repo=repo_dir)
    sfci_tbin_cube.attributes['history'] = log

    sfc_tsbin_cube = iris.load_cube(inargs.sfc_file, 'total surface forcing binned by temperature and salinity')
    wfo_tsbin_cube = iris.load_cube(inargs.wfo_file, 'Water Flux into Sea Water binned by temperature and salinity')
    theta = uconv.broadcast_array(lower_thetao_bounds, 2, sfc_tsbin_cube.shape)
    sfci_tsbin_cube = sfc_tsbin_cube.copy()
    sfci_tsbin_cube.data = sfc_tsbin_cube.data - (cp * theta * wfo_tsbin_cube.data)  # SFCI = SFC - Cp*THETA*SVF
    sfci_tsbin_cube.var_name = 'sfci_tsbin'
    sfci_tsbin_cube.long_name = 'total internal surface forcing binned by temperature and salinity'
    sfci_tsbin_cube.attributes['history'] = log

    cube_list = iris.cube.CubeList([sfci_tbin_cube, sfci_tsbin_cube])
    iris.save(cube_list, inargs.sfci_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sfc_file", type=str, help="Total surface forcing file")
    parser.add_argument("wfo_file", type=str, help="Surface freshwater flux file")
    parser.add_argument("sfci_file", type=str, help="Output file")
    args = parser.parse_args()            
    main(args)
