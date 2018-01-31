"""
Filename:     plot_trend_boxwhisker.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the trend in a given metric for numerous data files
              and display the result in box and whisker format

"""

# Import general Python modules

import os, sys, pdb

import numpy
import argparse

import iris

import matplotlib
import matplotlib.pyplot as plt

import pandas

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



def get_experiment_colors(experiment_list):
    """Create color list for given experiment list."""

    experiment_colors = {'historical': 'white',
                         'historicalGHG': 'red',
                         'historicalMisc': 'blue'}
    color_list = []
    for experiment in experiment_list:
        color_list.append(experiment_colors[experiment])

    return color_list


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
    for infile in infiles:
        filename = infile.split('/')[-1]
        model = filename.split('_')[2]
        experiment = filename.split('_')[3]
        models.append(model)
    
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

    return color_dict


def load_data(infile, var, time_constraint):
    """Load the data"""

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(infile, gio.check_iris_var(var) & time_constraint)
        cube.data = cube.data * 100
    model, experiment, rip, physics = get_run_details(cube)
    trend = timeseries.calc_trend(cube, per_yr=True)

    return cube, trend, model, experiment, rip


def generate_data_dict(trend, model, experiment, rip, all_experiments):
    """Generate dict that will form a row of a pandas dataframe."""

    data_dict = {'model': model, 'rip': rip}
    for exp in all_experiments:
        if exp == experiment:
            data_dict[exp] = trend
        else:
            data_dict[exp] = numpy.nan
    
    return data_dict
    

def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    fig, ax = plt.subplots()
    plt.axhline(y=0, color='0.5', linestyle='--')

    color_dict = get_colors(inargs.infiles)

    column_dict = {}
    for index, experiment in enumerate(inargs.experiments):
        column_dict[experiment] = index + 1

    data_list = []
    for infile in inargs.infiles:
        cube, trend, model, experiment, rip = load_data(infile, inargs.var, time_constraint)
        label = model if experiment == 'historical' else None
        if inargs.points:
            plt.plot(column_dict[experiment], trend, 'o', label=label, color=color_dict[model])
        else:
            data_list.append(generate_data_dict(trend, model, experiment, rip, inargs.experiments))
 
    if not inargs.points:
        data_df = pandas.DataFrame(data_list)
        if 'historicalMisc' in inargs.experiments:
            data_df.rename(columns={'historicalMisc': 'historicalAA'}, inplace=True)
        experiment_colors = get_experiment_colors(inargs.experiments)
        seaborn.boxplot(data=data_df, palette=experiment_colors)

    if inargs.title:
        title = inargs.title.replace("_", " ")
    else:
        title = 'linear trend in %s, %s-%s' %(cube.var_name.replace('-', ' '), inargs.time[0][0:4], inargs.time[1][0:4])
    plt.title(title)

    if inargs.ylabel:
        ax.set_ylabel(inargs.ylabel)
    else:
        ax.set_ylabel(str(cube.units) + ' / year')

    if inargs.points:
        nexperiments = len(inargs.experiments)
        ax.set_xticks(numpy.arange(1, nexperiments + 1))
        ax.set_xticklabels(inargs.experiments)
        ax.set_xlim((0, nexperiments + 1))

        ymin, ymax = ax.get_ylim()  
        ybuffer = (ymax - ymin) * 0.05
        ax.set_ylim((ymin - ybuffer, ymax + ybuffer))

        handles, labels = ax.get_legend_handles_labels()
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))

    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
    ax.yaxis.major.formatter._useMathText = True

    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight')
    metadata_dict = {inargs.infiles[-1]: cube.attributes['history']}
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate trends for each input file and display in box and whisker format'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--experiments", type=str, required=True, nargs='*',
                        help="experiments in the order they should appear")

    parser.add_argument("--title", type=str, default=None,
                        help="plot title [default: None]")
    parser.add_argument("--ylabel", type=str, default=None,
                        help="y axis label")

    parser.add_argument("--points", action="store_true", default=False,
	                help="Plot individual data points instead of box and whiskers")
    
    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()            

    main(args)
