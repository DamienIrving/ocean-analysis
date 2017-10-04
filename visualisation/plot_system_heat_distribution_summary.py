"""
Filename:     plot_system_heat_distribution_summary.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot a sumamry of the system heat distribution

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
iris.FUTURE.netcdf_promote = True
import matplotlib.pyplot as plt
import seaborn

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
    import timeseries
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_colors = {'historical': 'black',
                     'historicalGHG': 'red',
                     'historicalAA': 'blue',
                     'rcp85': 'orange',
                     'rcp26': 'green'}


def get_data(infile, var, agg_method, time_constraint, ohc=False, branch=None):
    """Read and temporally aggregate the data."""
    
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(infile, var & time_constraint)
        value = timeseries.calc_trend(cube, per_yr=True)
           
    return value
        

def set_title(infile):
    """Get the plot title."""

    cube = iris.load(infile)
    title = '%s trends, divided by global net radiative surface flux'  %(cube[0].attributes['model_id'])
    
    plt.suptitle(title, size='large')


def get_scale_factor(infile):
    """Get the scaling factor."""

    cube = iris.load_cube(infile, 'Surface Downwelling Net Radiation globe sum')
    trend = timeseries.calc_trend(cube, per_yr=True)

    return trend


def plot_data(ax, variable, trends_dict):
    """Plot the data."""

    xvals = [0, 1, 2, 3, 4]
    labels = ['', 'ssubpolar', 'stropics', 'ntropics', 'nsubpolar', 'arctic']

    for key, value in trends_dict.items():
        var, experiment, run = key
        if var == variable:
            label = experiment if run == 'r1' else None
            ax.plot(xvals, trends_dict[key], 'o-', color=experiment_colors[experiment], label=label)
 
    ax.set_xticklabels(labels)
    ax.set_ylabel('$W \: yr^{-1}$')
    ax.margins(0.1)
    ax.legend()
    ax.set_title(variable)


def get_regional_trends(infile, variable, time_constraints):
    """Calculate regional trends for a given variable"""

    if 'rcp' in infile:
        time_constraint = time_constraints['rcp']
    else:
        time_constraint = time_constraints['historical']

    trend_values = []
    for region in ['ssubpolar', 'stropics', 'ntropics', 'nsubpolar', 'arctic']:
        full_var = '%s %s ocean sum'  %(variable, region)
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(infile, full_var & time_constraint)
        trend_values.append(timeseries.calc_trend(cube, per_yr=True))

    history = cube.attributes['history']
    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']
    if experiment == 'historicalMisc':
        experiment = 'historicalAA'
    run = 'r' + str(cube.attributes['realization'])

    return trend_values, history, model, experiment, run


def get_time_constraint(time_bounds):
    """Get the iris time constraint for given time bounds."""

    if time_bounds:
        try:
            time_constraint = gio.get_time_constraint(time_bounds)
        except AttributeError:
            time_constraint = iris.Constraint()    
    else:
        time_constraint = iris.Constraint()

    return time_constraint

    
def main(inargs):
    """Run the program."""

    time_constraints = {}
    time_constraints['historical'] = get_time_constraint(inargs.hist_time)
    time_constraints['rcp'] = get_time_constraint(inargs.rcp_time)

    width=14
    height=10
    fig = plt.figure(figsize=(width, height))
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)
    axes_list = [ax1, ax2, ax3, ax4]

    variables = ['Surface Downwelling Net Radiation', 'Surface Upwelling Longwave Radiation', 'Surface Upward Latent Heat Flux', 'Downward Heat Flux at Sea Water Surface']
    if inargs.infer_hfds:
        variables[-1] = 'Inferred Downward Heat Flux at Sea Water Surface'
    trends_dict = {}
    for infile in inargs.infiles:
        for var in variables:
            trend, history, model, experiment, run = get_regional_trends(infile, var, time_constraints)
            trends_dict[(var, experiment, run)] = trend

    for ax, var in zip(axes_list, variables):
        plot_data(ax, var, trends_dict)

    title = '%s trends'  %(model)
    plt.suptitle(title, size='large')
    plt.subplots_adjust(top=0.90)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infiles[-1]: history})


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot a summary of the system heat distribution'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
               
    parser.add_argument("infiles", type=str, nargs='*', 
                        help="Input energy budget files generated from calc_system_heat_distribution.py")                                                    
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--hist_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = = all]")
    parser.add_argument("--rcp_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")
    parser.add_argument("--infer_hfds", action="store_true", default=False,
                        help="Use inferred hfds data")

    args = parser.parse_args()             
    main(args)
