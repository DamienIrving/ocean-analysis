"""
Filename:     calc_massa.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  calculate massa (global mass of atmospheric water vapor) from prw

"""

# Import general Python modules

import sys, os, pdb
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

def main(inargs):
    """Run the program."""

    area_cube = iris.load_cube(inargs.area_file, 'cell_area')
    prw_cube, history = gio.combine_files(inargs.prw_files, 'atmosphere_mass_content_of_water_vapor')
    weights = uconv.broadcast_array(area_cube.data, [1, 2], prw_cube.shape)
    coord_names = [coord.name() for coord in prw_cube.dim_coords]
    massa_cube = prw_cube.collapsed(coord_names[1:], iris.analysis.SUM, weights=weights)
    units = str(massa_cube.units)
    massa_cube.units = units.replace('m-2', '')
    massa_cube.remove_coord(coord_names[1])
    massa_cube.remove_coord(coord_names[2])

    massa_cube.attributes['history'] = cmdprov.new_log(git_repo=repo_dir)
    iris.save(massa_cube, inargs.outfile)
        

if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate massa from prw'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("prw_files", type=str, nargs='*', help="Input prw files")
    parser.add_argument("area_file", type=str, help="areacella file")
    parser.add_argument("outfile", type=str, help="Output file")

    args = parser.parse_args()
    main(args)
