"""
Filename:     plot_trend_scatter.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate metric trend for each model and plot scatter points

"""

# Import general Python modules

import os, sys, pdb

import numpy
import argparse

import iris

import matplotlib
import matplotlib.pyplot as plt

import seaborn
#seaborn.set_context('paper')


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
    experiment = cube.attributes['experiment_id']
    
    realization = cube.attributes['realization']
    initialization = cube.attributes['initialization_method']
    physics = cube.attributes['physics_version']
    
    rip = 'r%si%sp%s' %(realization, initialization, physics)

    return model, experiment, rip


def set_axis_labels(inargs, xunits, yunits):
    """Set the x and y axis labels."""

    if inargs.xlabel:
        xname = inargs.xlabel.replace('_', ' ')
    else:
        xname = inargs.xvar.replace('_', ' ')
    xlabel = '%s (%s/yr)' %(xname, xunits)


    if inargs.ylabel:
        yname = inargs.ylabel.replace('_', ' ')
    else:
        yname = inargs.yvar.replace('_', ' ')
    ylabel = '%s (%s/yr)' %(yname, yunits)

    return xlabel, ylabel


def main(inargs):
    """Run the program."""

    assert len(inargs.xfiles) == len(inargs.yfiles)

    time_constraint = gio.get_time_constraint(inargs.time)
    fig = plt.figure()
    for xfile, yfile in zip(inargs.xfiles, inargs.yfiles):
        with iris.FUTURE.context(cell_datetime_objects=True):
            xcube = iris.load_cube(xfile, gio.check_iris_var(inargs.xvar) & time_constraint)
            ycube = iris.load_cube(yfile, gio.check_iris_var(inargs.yvar) & time_constraint)

        assert get_run_details(xcube) == get_run_details(ycube)
        model, experiment, rip = get_run_details(xcube)

        xtrend = timeseries.calc_trend(xcube, per_yr=True)
        ytrend = timeseries.calc_trend(ycube, per_yr=True) 

        label = '%s, %s' %(model, rip)
        plt.plot(xtrend, ytrend, 'o', label=label)

    title = '%s trend, %s-%s' %(experiment, inargs.time[0][0:4], inargs.time[1][0:4])
    plt.title(title)
    xlabel, ylabel = set_axis_labels(inargs, xcube.units, ycube.units)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.savefig(inargs.outfile, bbox_inches='tight')

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

    parser.add_argument("xvar", type=str, help="Independent variable standard_name")
    parser.add_argument("yvar", type=str, help="Dependent variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--xfiles", type=str, nargs='*', required=True, 
                        help="Independent variable data files")
    parser.add_argument("--yfiles", type=str, nargs='*', required=True, 
                        help="Dependent variable data files")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--xlabel", type=str, default=None,
                        help="Override the default x axis label")
    parser.add_argument("--ylabel", type=str, default=None,
                        help="Override the default y axis label")

    args = parser.parse_args()            

    main(args)
