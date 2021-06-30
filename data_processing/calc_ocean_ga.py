"""Calculate thetaoga or soga from thetao or so data"""

import sys
script_dir = sys.path[0]
import os
import pdb
import re
import argparse

import iris
import iris.util
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

    standard_names = {'thetao': 'sea_water_potential_temperature',
                      'so': 'sea_water_salinity'}
    volume_cube = gio.get_ocean_weights(inargs.volfile)
    output_cubelist = iris.cube.CubeList([])

    cube, history = gio.combine_files(inargs.infiles, standard_names[inargs.invar], checks=True)
    ntsteps = cube.shape[0]
    for tstep, cube_slice in enumerate(cube.slices_over('time')):
        print(f'time step {tstep + 1} of {ntsteps}')
        coord_names = [coord.name() for coord in cube.dim_coords]
        aux_coord_names = [coord.name() for coord in cube.aux_coords]
        ga = cube_slice.collapsed(coord_names[1:], iris.analysis.MEAN, weights=volume_cube.data)
        for coord in coord_names[1:] + aux_coord_names:
            ga.remove_coord(coord)
            ga.var_name = inargs.invar + 'ga'
        output_cubelist.append(ga)
    outcube = output_cubelist.merge()[0]
    metadata_dict = {}
    metadata_dict[inargs.infiles[0]] = history 
    metadata_dict[inargs.volfile] = volume_cube.attributes['history'] 
    outcube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(outcube, inargs.outfile)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input thetao or so files")
    parser.add_argument("invar", type=str, choices=('thetao', 'so'), help="Input variable")
    parser.add_argument("volfile", type=str, help="Volume file")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--time", type=str, nargs=2, default=None, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    args = parser.parse_args()
    main(args)
