"""
Filename:     plot_simple_boxwhisker.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot a simple box and whisker type plot (i.e. dots, not the actual box)

"""

# Import general Python modules

import os, sys, pdb

import numpy
import argparse

import iris

import matplotlib
import matplotlib.pyplot as plt

import seaborn
seaborn.set_context('talk')


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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


def get_run_details(cube):
    """Get the model, experiment and mip details for a given cube."""

    model = cube.attributes['model_id']
    if model == 'FGOALS_g2':
        model = 'FGOALS-g2'

    experiment = cube.attributes['experiment_id']
    
    realization = cube.attributes['realization']
    initialization = cube.attributes['initialization_method']
    physics = cube.attributes['physics_version']
    
    rip = 'r%si%sp%s' %(realization, initialization, physics)

    return model, experiment, rip, int(physics)


def get_colors(infiles):
    """Define a color for each model"""

    models = []
    experiments = []
    for infile in infiles:
        filename = infile.split('/')[-1]
        model = filename.split('_')[2]
        experiment = filename.split('_')[3]

        models.append(model)
        experiments.append(experiment) 
    
    experiments = sorted(experiments)
    experiment_list = list(set(experiments))
    
    models = sorted(models)
    nmodels = len(set(models))
    cm = plt.get_cmap('nipy_spectral')
    colors = [cm(1. * i / nmodels) for i in range(nmodels)]
    color_dict = {}
    count = 0
    for model in models:
        if not model in color_dict.keys():
            color_dict[model] = colors[count]
            count = count + 1

    return color_dict, column_dict


def load_data(infile, var, time_constraint):
    """Load the data"""

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(infile, gio.check_iris_var(var) & time_constraint)
    model, experiment, rip, physics = get_run_details(cube)
    trend = timeseries.calc_trend(cube, per_yr=True)

    return cube, trend, model, experiment, rip


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    fig, ax = plt.subplots()
    plt.axhline(y=0, color='0.5', linestyle='--')
    color_dict, experiment_list = get_colors(inargs.xfiles)

    column_dict = {}
    for index, experiment in enumerate(experiment_list):
        column_dict[experiment] = index + 1

    values = {}
    for infile in inargs.infiles:
        cube, trend, model, experiment = load_data(infile, inargs.var, time_constraint)
        label = model if experiment == 'historical' else None
        plt.plot(column_dict[experiment], trend, 'o', label=model, color=color_dict[model])

    title = 'linear trend in %s, %s-%s' %(inargs.var.replace('_', ' '), inargs.time[0][0:4], inargs.time[1][0:4])
    plt.title(title)

    if inargs.ylabel:
        plt.ylabel(ylabel)
    else:
        plt.ylabel(str(cube.units) + '/ year')

    nexperiments = len(experiment_list)
    ax.set_xticks(numpy.arange(1, nexperiments + 1))
    ax.set_xticklabels(experiment_list)
    ax.set_xlim((0, nexperiments + 1))

    ymin, ymax = ax.get_ylim()  
    ybuffer = (ymax - ymin) * 0.05
    ax.set_ylim((ymin - ybuffer, ymax + ybuffer))

    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(inargs.outfile, bbox_inches='tight')
    metadata_dict = {inargs.infiles[-1]: cube.attributes['history']}
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate metric trend for each model and plot scatter points'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--ylabel", type=str, default=None,
                        help="y axis label")

    args = parser.parse_args()            

    main(args)
