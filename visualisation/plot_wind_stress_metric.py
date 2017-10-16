"""
Filename:     plot_wind_stress_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot wind stress metrics

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
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
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_colors = {'historical': 'orange',
                     'historicalGHG': 'red',
                     'historicalAA': 'blue',
                     'rcp26': '#16DB65',
                     'rcp45': '#058C42',
                     'rcp60': '#04471C',
                     'rcp85': '#0D2818'}


def load_data(infile):
    """Load, temporally aggregate and spatially slice input data"""
    
    cube = iris.load_cube(infile, 'surface_downward_x_stress')
    cube = timeseries.convert_to_annual(cube)
    experiment = cube.attributes['experiment_id']
    
    sh_constraint = iris.Constraint(latitude=lambda cell: -30.0 <= cell < 0.0)
    nh_constraint = iris.Constraint(latitude=lambda cell: 0.0 < cell <= 30.0)
    scrit_constraint = iris.Constraint(latitude=lambda cell: -17.0 <= cell < -13.0)
    ncrit_constraint = iris.Constraint(latitude=lambda cell: 13.0 < cell <= 17.0)

    sh_cube = cube.extract(sh_constraint)
    nh_cube = cube.extract(nh_constraint)
    scrit_cube = cube.extract(scrit_constraint)
    ncrit_cube = cube.extract(ncrit_constraint)
    
    sh_mean = sh_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN)
    nh_mean = nh_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN)
    scrit_mean = scrit_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN)
    ncrit_mean = ncrit_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN)

    return sh_mean, nh_mean, scrit_mean, ncrit_mean, experiment


def plot_data(ax, sh_cube, nh_cube, experiment, previous_experiments, crit=False):
    """Plot the various wind stress metrics."""

    plt.sca(ax)
    
    iplt.plot(nh_cube, color=experiment_colors[experiment], label=experiment+', NH')
    iplt.plot(sh_cube, color=experiment_colors[experiment], label=experiment+', SH', linestyle='--')

    if not experiment in previous_experiments:
        plt.legend(ncol=2)
    plt.ylabel(str(nh_cube.units))
    plt.xlabel('Year')

    if crit:
        plt.title('Critical latitude (15N/S)')
    else:
        plt.title('Tropics (0-30N/S)')

    
def main(inargs):
    """Run the program."""

    time_constraints = {}
    time_constraints['historical'] = gio.get_time_constraint(inargs.hist_time)
    time_constraints['rcp'] = gio.get_time_constraint(inargs.rcp_time)

    width=15
    height=7
    fig = plt.figure(figsize=(width, height))
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
 
    previous_experiments = []
    for filenum, infile in enumerate(inargs.infiles):
        sh_mean, nh_mean, scrit_mean, ncrit_mean, experiment = load_data(infile)
        plot_data(ax1, sh_mean, nh_mean, experiment, previous_experiments, crit=False)
        plot_data(ax2, scrit_mean, ncrit_mean, experiment, previous_experiments, crit=True)
        previous_experiments.append(experiment)

    title = 'Annual Mean Surface Downward X Stress, %s'  %(sh_mean.attributes['model_id'])
    plt.suptitle(title, size='large')
#    plt.subplots_adjust(top=0.90)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infiles[-1]: sh_mean.attributes['history']})


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot wind stress metrics'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
               
    parser.add_argument("infiles", type=str, nargs='*', 
                        help="Input wind stress files")                                                    
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--hist_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")
    parser.add_argument("--rcp_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")

    args = parser.parse_args()             
    main(args)
