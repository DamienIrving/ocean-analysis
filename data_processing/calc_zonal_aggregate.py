"""
Filename:     calc_zonal_aggregate.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  calculate the zonal aggregate

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
    import convenient_universal as uconv
    import timeseries
    import grids
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

aggregation_functions = {'mean': iris.analysis.MEAN,
                         'sum': iris.analysis.SUM}


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def multiply_by_area(cube):
    """Multiply by cell area."""

    if not cube.coord('latitude').has_bounds():
        cube.coord('latitude').guess_bounds()
    if not cube.coord('longitude').has_bounds():
        cube.coord('longitude').guess_bounds()
    area_weights = iris.analysis.cartography.area_weights(cube)

    units = str(cube.units)
    cube.data = cube.data * area_weights   
    cube.units = units.replace('m-2', '')

    return cube


def main(inargs):
    """Run the program."""

    cube = iris.load(inargs.infiles, gio.check_iris_var(inargs.var), callback=save_history)
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)

    if inargs.annual:
        cube = timeseries.convert_to_annual(cube, full_months=True)

    cube, coord_names, regrid_status = grids.curvilinear_to_rectilinear(cube)

    if inargs.area:
        cube = multiply_by_area(cube) 

    zonal_aggregate = cube.collapsed('longitude', aggregation_functions[inargs.aggregation])
    zonal_aggregate.remove_coord('longitude')

    zonal_aggregate.attributes['history'] = gio.write_metadata(file_info={inargs.infiles[0]: history[0]}) 
    iris.save(zonal_aggregate, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Calculate the zonal aggregate'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infiles", type=str, nargs='*', help="Input file")
    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("aggregation", type=str, choices=('mean', 'sum'), help="Method for zonal aggregation")
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Output annual mean [default=False]")
    parser.add_argument("--area", action='store_true', default=False,
                        help="Multiply by area [default=False]")

    args = parser.parse_args()             
    main(args)
