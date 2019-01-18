"""
Filename:     calc_ensemble_aggregate.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the ensemble aggregate

"""

# Import general Python modules

import sys, os, pdb, re
import argparse
import iris
from iris.experimental.equalise_cubes import equalise_attributes
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
    import timeseries
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def read_infiles(infiles, var, time_constraint, ensnum):
    """Combine multiple input files into one cube"""

    cube = iris.load(infiles, gio.check_iris_var(var))
    history = cube[0].attributes['history']
    atts = cube[0].attributes
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()

    cube = gio.check_time_units(cube)
    cube = cube.extract(time_constraint)
    cube = iris.util.squeeze(cube)

    new_aux_coord = iris.coords.AuxCoord(ensnum, long_name='ensemble_member', units='no_unit')
    cube.add_aux_coord(new_aux_coord)

    return cube, history


def unify_coordinates(cube_list):
    """Unify the coordinates across ensemble"""

    iris.util.unify_time_units(cube_list)
    coord_names = [coord.name() for coord in cube_list[0].dim_coords]
    for coord_name in coord_names:
        for cube in cube_list[1:]:
            cube.coord(coord_name).var_name = cube_list[0].coord(coord_name).var_name
            cube.coord(coord_name).long_name = cube_list[0].coord(coord_name).long_name
            cube.coord(coord_name).standard_name = cube_list[0].coord(coord_name).standard_name
            cube.coord(coord_name).units = cube_list[0].coord(coord_name).units
            cube.coord(coord_name).coord_system = cube_list[0].coord(coord_name).coord_system
            cube.replace_coord(cube_list[0].coord(coord_name))

    return cube_list


def calc_ensagg(cube_list):
    """Calculate the ensemble mean"""

    cube_list = unify_coordinates(cube_list)
    equalise_attributes(cube_list)
    ensemble_cube = cube_list.merge_cube()
    ensemble_mean = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)
    ensemble_mean.remove_coord('ensemble_member')

    return ensemble_mean


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time_bounds)
    ensemble_cube_list = iris.cube.CubeList([])
    for ensnum, ensemble_member in enumerate(inargs.ensemble_member):
        cube, history = read_infiles(ensemble_member, inargs.var, time_constraint, ensnum)
        ensemble_cube_list.append(cube)
    
    ensagg = calc_ensagg(ensemble_cube_list)

    log = cmdprov.new_log(infile_history={ensemble_member[0]: history}, git_repo=repo_dir)
    ensagg.attributes['history'] = log

    iris.save(ensagg, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the ensemble aggregate at each grid point'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file name (or directory if you want each of many input files processed separately")

    parser.add_argument("--ensemble_member", type=str, nargs='*', action='append',
                        help="Input files for a particular ensemble member")

    parser.add_argument("--time_bounds", type=str, nargs=2, default=None, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    args = parser.parse_args()            
    main(args)
