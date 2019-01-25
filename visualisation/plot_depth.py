"""
Filename:     plot_depth.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot data that has a depth axis  

"""

# Import general Python modules

import sys
import os
import pdb
import re
import argparse

import numpy
import matplotlib.pyplot as plt
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

exp_colors = {'historical': 'black',
              'historicalGHG': 'red',
              'historicalMisc': 'blue'}

def make_grid(depth_values):
    """Make a dummy cube with desired grid."""
       
    depth = iris.coords.DimCoord(depth_values,
                                 standard_name='depth',
                                 units='m',
                                 long_name='ocean depth coordinate',
                                 var_name='lev')

    dummy_data = numpy.zeros(len(depth_values))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(depth, 0)])

    new_cube.coord('depth').guess_bounds()

    return new_cube


def regrid(cube, ref_cube):
    """Regrid to reference grid, preserving the data sum"""

    depth_bounds = cube.coord('depth').bounds
    depth_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, depth_bounds)
    cube_scaled = cube / depth_diffs

    ref_points = [('depth', ref_cube.coord('depth').points)]
    cube_regridded = cube_scaled.interpolate(ref_points, iris.analysis.Linear())         

    ref_depth_bounds = ref_cube.coord('depth').bounds
    ref_depth_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, ref_depth_bounds)
    new_cube = cube_regridded * ref_depth_diffs

    return new_cube


def collapse_dims(cube):
    """Collapse any non-depth coordinates."""

    coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    assert 'time' not in coord_names
    assert coord_names[0] == 'depth'
    if len(coord_names) > 1:
        depth_cube = cube.collapsed(coord_names[1:], iris.analysis.SUM)
        for coord in coord_names[1:]:
            depth_cube.remove_coord(coord)
        for coord in aux_coord_names:
            depth_cube.remove_coord(coord)

    return depth_cube


def plot_data(cube, experiment, label=False, linewidth=None):
    """Plot data for a single model/experiment"""

    ydata = cube.coord('depth').points
    xdata = cube.data
    color = exp_colors[experiment]
    label = experiment if label else None

    plt.plot(xdata, ydata, label=label, color=color, linewidth=linewidth)


def ensemble_mean(cube_list):
    """Calculate the ensemble mean."""

    equalise_attributes(cube_list)
    ensemble_cube = cube_list.merge_cube()
    ensemble_mean = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)

    return ensemble_mean


def main(inargs):
    """Run the program."""
    
    metadata_dict = {}
    ensemble_dict = {'historical': iris.cube.CubeList([]),
                     'historicalGHG': iris.cube.CubeList([]),
                     'historicalMisc': iris.cube.CubeList([])}
    depth_constraint = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    new_grid = make_grid(numpy.arange(inargs.min_depth + 0.5, inargs.max_depth, 1))
    experiment_list = []

    for infile in inargs.infiles:
        cube = iris.load_cube(infile, gio.check_iris_var(inargs.var) & depth_constraint)
        depth_cube = collapse_dims(cube)

        experiment = cube.attributes['experiment_id']
        experiment_list.append(experiment)

        ensemble_number = experiment_list.count(experiment)
        new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
        depth_cube.add_aux_coord(new_aux_coord)

        new_depth_cube = regrid(depth_cube, new_grid)
        ensemble_dict[experiment].append(new_depth_cube)

    fig = plt.figure(figsize=[10, 30])
    enswidth = 2.0
    ilinewidth = enswidth * 0.25 if inargs.ensmean else enswidth
    for experiment in ['historical', 'historicalGHG', 'historicalMisc']:
        for num, cube in enumerate(ensemble_dict[experiment]):
            label = experiment if (num == 1) and not inargs.ensmean else False 
            plot_data(cube, experiment, label=label, linewidth=ilinewidth)
        if inargs.ensmean:
            ensmean_cube = ensemble_mean(ensemble_dict[experiment])
            plot_data(ensmean_cube, experiment, label=experiment, linewidth=2.0)

    plt.gca().invert_yaxis()
    plt.ylim([inargs.max_depth, inargs.min_depth])
    plt.legend()
    #plt.xlim([-0.1e21, 0.2e21])
    plt.grid(True)
    plt.xlabel(str(cube.units))
    plt.ylabel('Depth (m)')
    plt.title('Excess heat storage, 1861-2005')

    # Save output
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot depth data'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", nargs='*', type=str, help="Input data files (one file per model/run/experiment)")
    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--min_depth", type=float, default=0,
                        help="Only include data below this vertical level")
    parser.add_argument("--max_depth", type=float, default=5500,
                        help="Only include data above this vertical level")

    parser.add_argument("--ensmean", action="store_true", default=False,
                        help="Plot an ensemble mean curve [default: False]")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)
