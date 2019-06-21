"""
Filename:     plot_drift.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Visualise the de-drifting process  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import numpy
import matplotlib.pyplot as plt

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

processing_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(processing_dir)

import timeseries
import remove_drift
import general_io as gio


# Define functions 

def select_point(cube, index_list, timeseries=False):
    """Select a given grid point."""

    if timeseries:
        assert len(index_list) == cube.ndim - 1
    else:
        assert len(index_list) == cube.ndim

    if len(index_list) == 1:
        a = index_list[0]
        point = cube[:, a] if timeseries else cube[a]
    elif len(index_list) == 2:
        a, b = index_list
        point = cube[:, a, b] if timeseries else cube[a, b]
    elif len(index_list) == 3:
        a, b, c = index_list
        point = cube[:, a, b, c] if timeseries else cube[a, b, c]

    return point
 

def read_data(file_list, var, grid_point, convert_to_annual=False):
    """Read input data."""

    cube, history = gio.combine_files(file_list, var)   
    cube = select_point(cube, grid_point, timeseries=True)

    if convert_to_annual:
        cube = timeseries.convert_to_annual(cube)
    
    return cube, history[0]


def cubic_fit(infile, grid_point, time_axis):
    """Get the cubic polynomial."""

    a_cube = iris.load_cube(infile, 'coefficient a')
    a_cube = select_point(a_cube, grid_point) 
    b_cube = iris.load_cube(infile, 'coefficient b')
    b_cube = select_point(b_cube, grid_point)
    c_cube = iris.load_cube(infile, 'coefficient c')
    c_cube = select_point(c_cube, grid_point)
    d_cube = iris.load_cube(infile, 'coefficient d')
    d_cube = select_point(d_cube, grid_point)

    numpy_poly = numpy.poly1d([float(d_cube.data), 
                               float(c_cube.data),
                               float(b_cube.data),
                               float(a_cube.data)])
    cubic_data = numpy_poly(time_axis)

    return cubic_data, a_cube


def get_title(grid_point):
    """Get the plot title."""

    title = "Grid point: "
    for index in grid_point:
        title = title + str(index) + " "

    return title


def main(inargs):
    """Run the program."""

    metadata_dict = {}

    # Read data
    control_cube, control_history = read_data(inargs.control_files, inargs.variable,
                                              inargs.grid_point, convert_to_annual=True)
    experiment_cube, experiment_history = read_data(inargs.experiment_files, inargs.variable,
                                                    inargs.grid_point, convert_to_annual=True)
    dedrifted_cube, dedrifted_history = read_data(inargs.dedrifted_files, inargs.variable,
                                                  inargs.grid_point, convert_to_annual=False)

    metadata_dict[inargs.control_files[0]] = control_history
    metadata_dict[inargs.experiment_files[0]] = experiment_history
    metadata_dict[inargs.dedrifted_files[0]] = dedrifted_history

    cubic_data, a_cube = cubic_fit(inargs.coefficient_file, inargs.grid_point,
                                   control_cube.coord('time').points)
    #TODO: coeff metadata    

    # Time axis adjustment
    first_data_cube = iris.load_cube(inargs.experiment_files[0], inargs.variable)
    first_data_cube = select_point(first_data_cube, inargs.grid_point, timeseries=True)
    first_data_cube = timeseries.convert_to_annual(first_data_cube)
    time_diff, branch_time, new_time_unit = remove_drift.time_adjustment(first_data_cube, a_cube, 'annual')

    time_coord = experiment_cube.coord('time')
    time_coord.convert_units(new_time_unit)
    experiment_time_values = time_coord.points.astype(numpy.float32) - time_diff

    # Plot
    fig = plt.figure(figsize=[14, 7])
    plt.plot(control_cube.coord('time').points, control_cube.data, label='control')
    plt.plot(experiment_time_values, experiment_cube.data, label='experiment')
    plt.plot(experiment_time_values, dedrifted_cube.data, label='dedrifted')
    plt.plot(control_cube.coord('time').points, cubic_data, label='cubic fit')
    if inargs.ylim:
        ymin, ymax = inargs.ylim
        plt.ylim(ymin, ymax)
    plt.ylabel(inargs.variable)
    plt.xlabel(str(new_time_unit))
    plt.legend()
    title = get_title(inargs.grid_point)
    plt.title(title)

    # Save output
    plt.savefig(inargs.outfile, bbox_inches='tight')
    
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Visualise the de-drifting process'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
 
    parser.add_argument("variable", type=str, help="Variable")
    parser.add_argument("coefficient_file", type=str, help="Drift coefficient file name")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--control_files", nargs='*', type=str,
                        help="control data files")
    parser.add_argument("--experiment_files", nargs='*', type=str,
                        help="experiment data files")
    parser.add_argument("--dedrifted_files", nargs='*', type=str,
                        help="dedrifted experiment data files")

    parser.add_argument("--grid_point", type=int, nargs='*',
                        help="Array indexes for grid point to plot (e.g. 0 58 35)")

    parser.add_argument("--ylim", type=float, nargs=2, metavar=('MIN', 'MAX'), default=None,
                        help="limits for y axis")

    args = parser.parse_args()             
    main(args)