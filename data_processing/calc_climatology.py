"""
Filename:     calc_climatology.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the climatology 

"""

# Import general Python modules

import sys, os, pdb
import argparse, copy
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
    import grids
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

history = []

def scale_data(cube, scale_factor):
    """Scale a cube."""

    cube.data = cube.data * 10 ** scale_factor

    scale_label = '10^%s '   %(scale_factor)
    cube.units = scale_label + str(cube.units)
    
    return cube


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.

    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  

    """ 

    history.append(cube.attributes['history'])


def main(inargs):
    """Run the program."""

    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load(inargs.infiles, gio.check_iris_var(inargs.var) & time_constraint, callback=save_history)
    equalise_attributes(cube)
    cube = cube.concatenate_cube()

    annual_climatology = cube.collapsed('time', iris.analysis.MEAN)

    if inargs.regrid:
        annual_climatology, coord_names, regrid_status = grids.curvilinear_to_rectilinear(annual_climatology)

    if inargs.scale_factor:
        annual_climatology = scale_data(annual_climatology, inargs.scale_factor)

    annual_climatology.attributes['history'] = gio.write_metadata(file_info={inargs.infiles[0]: history[0]}) 
    iris.save(annual_climatology, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com  

"""

    description='Calculate the climatology'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input file names")
    parser.add_argument("var", type=str, help="Input file variable (standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    parser.add_argument("--regrid", action="store_true", default=False,
                        help="Regrid the data from curvilinear to rectilinear grid")
    parser.add_argument("--scale_factor", type=int, default=None,
                        help="Scale factor (i.e. multiple data by 10^scale_factor [default = entire]")

    args = parser.parse_args()
    main(args)

