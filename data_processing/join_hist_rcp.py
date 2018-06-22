"""
Filename:     join_hist_rcp.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Join an historical and RCP data file

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def clean_attributes(cube):
    """Remove attributes that might cause problems with merge."""

    cube.cell_methods = ()

    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    for aux_coord in aux_coord_names:
        cube.remove_coord(aux_coord)

    return cube

     
def main(inargs):
    """Run the program."""

    hist_time_constraint = gio.get_time_constraint(['1850-01-01', '2005-12-31'])
    outcubes = iris.cube.CubeList([])
    for var in inargs.variables:
        metadata_dict = {}
        hist_cube = iris.load_cube(inargs.hist_file, gio.check_iris_var(var) & hist_time_constraint)
        hist_cube = clean_attributes(hist_cube)
        branch_time = hist_cube.attributes['branch_time']
        history = hist_cube.attributes['history']
        
        rcp_cube = iris.load_cube(inargs.rcp_file, gio.check_iris_var(var))
        rcp_cube = clean_attributes(rcp_cube)
        rcp_experiment = rcp_cube.attributes['experiment_id']

        if inargs.cumsum:
            rcp_cube.data = rcp_cube.data + hist_cube.data[-1]

        cube_list = iris.cube.CubeList([hist_cube, rcp_cube])
        equalise_attributes(cube_list)
        iris.util.unify_time_units(cube_list)
        cube = cube_list.concatenate_cube()
        cube.attributes['branch_time'] = branch_time
        cube.attributes['experiment_id'] = 'historical-' + rcp_experiment

        outcubes.append(cube.copy())

    for cube in outcubes:
        cube.attributes['history'] = gio.write_metadata(file_info={inargs.hist_file: history})
    equalise_attributes(outcubes)

    iris.save(outcubes, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Join an historical and RCP data file'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("hist_file", type=str, help="Input historical file")
    parser.add_argument("rcp_file", type=str, help="Input RCP file")
    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("variables", nargs='*', type=str, help="variables")

    parser.add_argument("--cumsum", action="store_true", default=False,
                        help="The data is a cumulative sum [default: False]")

    args = parser.parse_args()
    main(args)

