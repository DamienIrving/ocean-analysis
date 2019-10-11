"""
Filename:     calc_thetaoga.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  calculate thetoga from thetao

"""

# Import general Python modules

import sys, os, pdb, re
import argparse
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


def main(inargs):
    """Run the program."""

    volume_cube = iris.load_cube(inargs.volfile, 'ocean_volume')
    output_cubelist = iris.cube.CubeList([])
    for infile in inargs.infiles:
        cube = iris.load_cube(infile, 'sea_water_potential_temperature')
        weights = uconv.broadcast_array(volume_cube.data, [1, 3], cube.shape)
        coord_names = [coord.name() for coord in cube.dim_coords]
        thetaoga = cube.collapsed(coord_names[1:], iris.analysis.MEAN, weights=weights)
        thetaoga.var_name = 'thetaoga'
        output_cubelist.append(thetaoga)
        print(infile)

    outcube = gio.combine_cubes(output_cubelist)
    metadata_dict = {}
    metadata_dict[infile] = cube.attributes['history'] 
    metadata_dict[inargs.volfile] = volume_cube.attributes['history'] 
    outcube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(outcube, inargs.outfile)
        

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate thetaoga from thetao'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input thetao files")
    parser.add_argument("volfile", type=str, help="Volume file")
    parser.add_argument("outfile", type=str, help="Output file")

    args = parser.parse_args()
    main(args)
