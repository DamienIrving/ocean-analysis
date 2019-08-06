"""
Filename:     plot_global_budget_variables.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot variables relevant for the global energy and water budget  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import numpy
import matplotlib.pyplot as plt
import cmdline_provenance as cmdprov

import clef.code
db = clef.code.connect()
session = clef.code.Session()

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
import general_io as gio


# Define functions 

names = {'masso': 'sea_water_mass', 'volo': 'sea_water_volume'}

def read_global_variable(model, variable, ensemble, project):
    """Read data for a global variable"""
    
    constraints = {'variable': variable, 'model': model, 'table': 'Omon',
                   'experiment': 'piControl', 'ensemble': ensemble}

    results = clef.code.search(session, project=project, **constraints)
    assert len(results) == 1
    filenames = results[0]['filenames']
    filenames.sort()
    filedir = results[0]['pdir']
    file_list = [filedir + '/' + filename for filename in filenames] 
    
    if file_list:
        cube, history = gio.combine_files(file_list, names[variable])
        cube = timeseries.convert_to_annual(cube)
    else:
        cube = None
        
    return cube


def plot_global_variable(ax, data, long_name, units, color):
    """Plot a global variable."""

    ax.plot(data, color=color)
    ax.set_title(long_name)
    ax.set_xlabel('year')
    ax.set_ylabel(units)
    ax.ticklabel_format(useOffset=False)


def main(inargs):
    """Run the program."""

    masso_cube = read_global_variable(inargs.model, 'masso', inargs.run, inargs.project)
    volo_cube = read_global_variable(inargs.model, 'volo', inargs.run, inargs.project)  

    fig = plt.figure(figsize=[16, 15])
    if masso_cube:
        ax1 = fig.add_subplot(3, 2, 1)
        plot_global_variable(ax1, masso_cube.data, masso_cube.long_name, masso_cube.units, 'green')
    if volo_cube:
        ax2 = fig.add_subplot(3, 2, 2)
        plot_global_variable(ax2, volo_cube.data, volo_cube.long_name, volo_cube.units, 'red')
    if masso_cube and volo_cube:
        ax3 = fig.add_subplot(3, 2, 3)
        units = str(masso_cube.units) + ' / ' + str(volo_cube.units)
        plot_global_variable(ax3, masso_cube.data / volo_cube.data, 'density', units, 'grey')


    # Save output
    plt.savefig(inargs.outfile, bbox_inches='tight')
    
    #log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    #log_file = re.sub('.png', '.met', inargs.outfile)
    #cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot variables relevant for the global energy and water budget'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
 
    parser.add_argument("model", type=str, help="Model (use dots not dashes between numbers in model names)")
    parser.add_argument("run", type=str, help="Run (e.g. r1i1p1)")
    parser.add_argument("project", type=str, choices=('cmip5', 'cmip6'), help="Project")
    parser.add_argument("outfile", type=str, help="Output file name")



    args = parser.parse_args()             
    main(args)
