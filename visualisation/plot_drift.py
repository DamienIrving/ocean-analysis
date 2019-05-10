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

#def index_text(index_list, time_axis=False):
#    """Generate the text for the index selection."""
#
#    text =  '[:,' if time_axis else '['
#    for count, index in enumerate(index_list):
#        if count == 0:
#            text = text + str(index)
#        else:
#            text = text + ', ' + str(index)
#
#    return text + ']'  
    

def read_data(file_list, var, grid_point, convert_to_annual=False):
    """Read input data."""

    z, i, j = grid_point
    cube, history = gio.combine_files(file_list, var)   
    cube = cube[:, z, i, j]

    if convert_to_annual:
        cube = timeseries.convert_to_annual(cube)
    
    return cube, history[0]


def cubic_fit(infile, grid_point, time_axis):
    """Get the cubic polynomial."""
    
    z, i, j = grid_point
    a_cube = iris.load_cube(infile, 'coefficient a')[z, i, j] 
    b_cube = iris.load_cube(infile, 'coefficient b')[z, i, j]
    c_cube = iris.load_cube(infile, 'coefficient c')[z, i, j]
    d_cube = iris.load_cube(infile, 'coefficient d')[z, i, j]

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
    z, i, j = inargs.grid_point
    first_data_cube = iris.load_cube(inargs.experiment_files[0], 'sea_water_potential_temperature')[:, z, i, j]
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
    plt.ylabel(inargs.variable)
    plt.xlabel(str(new_time_unit))
    plt.legend()

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

    parser.add_argument("--grid_point", type=int, nargs=3,
                        help="Array indexes for grid point to plot (e.g. 0 58 35)")

    args = parser.parse_args()             
    main(args)
