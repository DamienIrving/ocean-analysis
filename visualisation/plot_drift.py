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
import cf_units
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

def get_title(infile, var, index_list):
    """Get the plot title."""

    cube = iris.load_cube(infile, gio.check_iris_var(var))
    title = ''
    coord_names = [coord.name() for coord in cube.dim_coords]
    for posnum, index in enumerate(index_list):
        point_name = coord_names[posnum + 1]
        point_value = cube.coord(point_name).points[index]
        title = f"{title} {point_name}: {point_value};"

    return title


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
    if grid_point:  
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


def main(inargs):
    """Run the program."""

    metadata_dict = {}

    # Read data
    control_cube, control_history = read_data(inargs.control_files, inargs.variable,
                                              inargs.grid_point, convert_to_annual=inargs.annual)
    metadata_dict[inargs.control_files[0]] = control_history
    coord_names = [coord.name() for coord in control_cube.dim_coords]
    time_var = coord_names[0]
    assert time_var in ['time', 'year']

    experiment_cube, experiment_history = read_data(inargs.experiment_files, inargs.variable,
                                                    inargs.grid_point, convert_to_annual=inargs.annual)
    metadata_dict[inargs.experiment_files[0]] = experiment_history

    if inargs.dedrifted_files:
        dedrifted_cube, dedrifted_history = read_data(inargs.dedrifted_files, inargs.variable,
                                                      inargs.grid_point, convert_to_annual=inargs.annual)
        metadata_dict[inargs.dedrifted_files[0]] = dedrifted_history   

    if inargs.coefficient_file:
        cubic_data, a_cube = cubic_fit(inargs.coefficient_file, inargs.grid_point,
                                       control_cube.coord(time_var).points)
        #TODO: coeff metadata    

    # Time axis adjustment
    if time_var == 'time':
        first_data_cube = iris.load_cube(inargs.experiment_files[0], gio.check_iris_var(inargs.variable))
        if inargs.grid_point:
            first_data_cube = select_point(first_data_cube, inargs.grid_point, timeseries=True)
        if inargs.annual:
            first_data_cube = timeseries.convert_to_annual(first_data_cube)
        time_diff, branch_time, new_time_unit = remove_drift.time_adjustment(first_data_cube, control_cube, 'annual',
                                                                             branch_time=inargs.branch_time)
        print(f'branch time: {branch_time - 182.5}')
        time_coord = experiment_cube.coord('time')
        time_coord.convert_units(new_time_unit)
        experiment_time_values = time_coord.points.astype(numpy.float32) - time_diff
    elif time_var == 'year':
        if inargs.branch_year:
            branch_year = inargs.branch_year
        else:
            control_time_units = gio.fix_time_descriptor(experiment_cube.attributes['parent_time_units'])
            branch_time = experiment_cube.attributes['branch_time_in_parent']
            branch_datetime = cf_units.num2date(branch_time, control_time_units, cf_units.CALENDAR_STANDARD)
            branch_year = branch_datetime.year
        print(f'branch year: {branch_year}')
        experiment_time_values = numpy.arange(branch_year, branch_year + experiment_cube.shape[0])

    # Plot
    fig = plt.figure(figsize=[14, 7])
    plt.plot(control_cube.coord(time_var).points, control_cube.data, label='control')
    plt.plot(experiment_time_values, experiment_cube.data, label='experiment')
    if inargs.dedrifted_files:
        plt.plot(experiment_time_values, dedrifted_cube.data, label='dedrifted')
    if inargs.coefficient_file:
        plt.plot(control_cube.coord(time_var).points, cubic_data, label='cubic fit')
    if inargs.outlier_threshold:
        data, outlier_idx = timeseries.outlier_removal(control_cube.data, inargs.outlier_threshold)
        plt.plot(control_cube.coord(time_var).points[outlier_idx], control_cube.data[outlier_idx],
                 marker='o', linestyle='none', color='r', alpha=0.3)
    if inargs.ylim:
        ymin, ymax = inargs.ylim
        plt.ylim(ymin, ymax)
    plt.ylabel(f"{gio.check_iris_var(inargs.variable)} ({control_cube.units})")
    if time_var == 'time':
        plt.xlabel(str(new_time_unit))
    else:
        plt.xlabel('control run year')
    plt.legend()
    if inargs.grid_point:
        title = get_title(inargs.control_files, inargs.variable, inargs.grid_point)
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
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--control_files", nargs='*', type=str, required=True,
                        help="control data files")
    parser.add_argument("--experiment_files", nargs='*', type=str, required=True,
                        help="experiment data files")

    parser.add_argument("--coefficient_file", type=str, default=None,
                        help="Drift coefficient file name")
    parser.add_argument("--dedrifted_files", nargs='*', type=str, default=None,
                        help="dedrifted experiment data files")

    parser.add_argument("--outlier_threshold", type=float, default=None,
                        help="Indicate points that were removed from control in drift calculation [default: None]")

    parser.add_argument("--grid_point", type=int, nargs='*', default=None,
                        help="Array indexes for grid point to plot (e.g. 0 58 35)")

    parser.add_argument("--ylim", type=float, nargs=2, metavar=('MIN', 'MAX'), default=None,
                        help="limits for y axis")
    
    parser.add_argument("--branch_year", type=int, default=None, help="override metadata")
    parser.add_argument("--branch_time", type=float, default=None, help="override metadata")

    parser.add_argument("--annual", action="store_true", default=False,
                        help="Apply annual smoothing [default=False]")

    args = parser.parse_args()             
    main(args)
