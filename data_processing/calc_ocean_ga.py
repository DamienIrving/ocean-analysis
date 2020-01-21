"""
Filename:     calc_ocean_ga.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  calculate thetoga or soga from thetao or so data

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

    standard_names = {'thetao': 'sea_water_potential_temperature',
                      'so': 'sea_water_salinity'}
    volume_data, volume_var, volume_atts, volume_obj = gio.get_ocean_weights(inargs.volfile)
    output_cubelist = iris.cube.CubeList([])
    for infile in inargs.infiles:
        cube = iris.load_cube(infile, standard_names[inargs.invar])
        weights = uconv.broadcast_array(volume_data, [1, 3], cube.shape)
        coord_names = [coord.name() for coord in cube.dim_coords]
        aux_coord_names = [coord.name() for coord in cube.aux_coords]
        ga = cube.collapsed(coord_names[1:], iris.analysis.MEAN, weights=weights)
        for coord in coord_names[1:] + aux_coord_names:
            ga.remove_coord(coord)
        ga.var_name = inargs.invar + 'ga'
        output_cubelist.append(ga)
        print(infile)

    outcube = gio.combine_cubes(output_cubelist)
    metadata_dict = {}
    metadata_dict[infile] = cube.attributes['history'] 
    metadata_dict[inargs.volfile] = volume_atts['history'] 
    outcube.attributes['history'] = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    iris.save(outcube, inargs.outfile)
        

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate thetaoga or soga from thetao or so data'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input thetao or so files")
    parser.add_argument("invar", type=str, choices=('thetao', 'so'), help="Input variable")
    parser.add_argument("volfile", type=str, help="Volume file")
    parser.add_argument("outfile", type=str, help="Output file")

    args = parser.parse_args()
    main(args)
