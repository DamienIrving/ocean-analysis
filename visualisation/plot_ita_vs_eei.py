"""
Filename:     plot_ita_vs_eei.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the interhemispheric temperature asymmetry
              versus the planetary energy imbalance

"""

# Import general Python modules

import sys, os, pdb, re
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib as mpl
import seaborn

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

var_colors = {'ohc': 'blue', 'hfds': 'orange', 'rndt': 'red'}
exp_colors = {'historical-rcp85': 'black', 'historical': 'black', 'GHG-only': 'red',
              'AA-only': 'blue', '1pctCO2': 'orange'}

names = {'thetao': 'Sea Water Potential Temperature',
         'rndt': 'TOA Incoming Net Radiation'}

titles = {'rndt': 'netTOA', 'thetao': 'Average Ocean Temperature'}

plot_variables = {'thetao': ' Average Ocean Temperature',
                  'rndt': 'netTOA'}

seaborn.set(style='ticks')

mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['axes.titlesize'] = 28
mpl.rcParams['xtick.labelsize'] = 24
mpl.rcParams['ytick.labelsize'] = 24
mpl.rcParams['legend.fontsize'] = 20


def equalise_time_axes(cube_list):
    """Make all the time axes the same."""

    iris.util.unify_time_units(cube_list)
    reference_cube = cube_list[0]
    new_cube_list = iris.cube.CubeList([])
    for cube in cube_list:
        assert len(cube.coord('time').points) == len(reference_cube.coord('time').points)
        cube.coord('time').points = reference_cube.coord('time').points
        cube.coord('time').bounds = reference_cube.coord('time').bounds
        cube.coord('time').units = reference_cube.coord('time').units
        cube.coord('time').attributes = reference_cube.coord('time').attributes
        new_cube_list.append(cube)
    
    return new_cube_list


def ensemble_aggregation(cube_list, operator):
    """Calculate the ensemble aggregate."""

    assert operator in ['mean', 'median', 'percentile']

    if len(cube_list) > 1:
        equalise_attributes(cube_list)
        equalise_time_axes(cube_list)
        ensemble_cube = cube_list.merge_cube()
        if operator == 'mean':
            ensemble_agg = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)
        elif operator == 'median':
            ensemble_agg = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEDIAN)
        else:
            ensemble_agg = ensemble_cube.collapsed('ensemble_member', iris.analysis.PERCENTILE, percent=[25, 75])
    else:
        ensemble_agg = cube_list[0] if operator in ['mean', 'median'] else None

    return ensemble_agg


def calc_anomaly(cube):
    """Calculate the anomaly."""
    
    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    
    return anomaly


def get_simulation_attributes(cube):
    """Get model, experiment and mip information."""

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']
    physics = cube.attributes['physics_version']
    run = cube.attributes['realization']
    mip = 'r%si1p%s' %(run, physics)

    if experiment == 'historicalMisc':
        experiment = 'historicalAA'

    return model, experiment, mip


def calc_ita(sh_file, nh_file, time_constraint, ensemble_number):
    """Calculate the interhemispheric temperature asymmetry."""

    nh_name = names[var] + ' nh ' + agg
    nh_cube = iris.load_cube(nh_file, nh_name & time_constraint)
    nh_attributes = get_simulation_attributes(nh_cube)
    nh_anomaly = calc_anomaly(nh_cube)
    nh_anomaly.data = nh_anomaly.data.astype(numpy.float32)

    sh_name = names[var] + ' sh ' + agg
    sh_cube = iris.load_cube(sh_file, sh_name & time_constraint)
    sh_attributes = get_simulation_attributes(sh_cube)
    sh_anomaly = calc_anomaly(sh_cube)
    sh_anomaly.data = sh_anomaly.data.astype(numpy.float32)

    assert nh_attributes == sh_attributes 

    metric = nh_cube.copy()
    metric.data = nh_anomaly.data - sh_anomaly.data

    new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
    metric.add_aux_coord(new_aux_coord)
    metric.cell_methods = ()

    return metric, nh_cube.attributes['history']


def temporal_plot(ax, ensemble_agg, ensemble_spread, experiment):
    """Create the line graph with temporal x-axis"""

    plt.sca(ax)
    iplt.plot(ensemble_agg, label=experiment, color=exp_colors[experiment])
    if ensemble_spread:
        time_values = ensemble_spread[0, ::].coord('time').points - 54567.5  
        upper_bound = ensemble_spread_dict[var][0, ::].data
        lower_bound = ensemble_spread_dict[var][-1, ::].data
        iplt.plt.fill_between(time_values, upper_bound, lower_bound,
                              facecolor=exp_colors[experiment], alpha=0.15)


def temporal_plot_features(ax):
    """Set the temporal plot features"""

    ax.legend(loc=2)
    ax.set_xlabel('Year')
    ax.set_ylabel('NH minus SH (K)')
    ax.tick_params(top='off') 
    ax.text(0.93, 0.97, '(a)', transform=ax.transAxes, fontsize=24, va='top')
    ax.axhline(y=0, color='0.5', linestyle='--', linewidth=0.5)


def eei_plot(ax, eei_cube, ita_cube, experiment):
    """Create the scatter plot with EEI x-axis"""
    
    plt.sca(ax)
    x_data = eei_cube.data
    y_data = ita_cube.data
    plt.scatter(x, y, c=exp_colors[experiment])

def eei_plot_features(ax):
    """Set the scatter plot features"""

    ax.legend(loc=2)
    ax.set_xlabel('EEI (Joules)')
    ax.set_ylabel('NH minus SH (K)') 
    ax.text(0.93, 0.97, '(b)', transform=ax.transAxes, fontsize=24, va='top')


def main(inargs):
    """Run the program."""

    time_constraints = {'historical-rcp85': gio.get_time_constraint(inargs.rcp_time),
                        'historical': gio.get_time_constraint(inargs.historical_time),
                        'GHG-only': gio.get_time_constraint(inargs.historical_time),
                        'AA-only': gio.get_time_constraint(inargs.historical_time),
                        '1pctCO2': gio.get_time_constraint(inargs.pctCO2_time)}

    fig = plt.figure(figsize=[20, 7])
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    for experiment_num, experiment in enumerate(inargs.experiment_list):
        time_constraint = time_constraints[experiment]
        ita_cube_list = iris.cube.CubeList([])
        eei_cube_list = iris.cube.CubeList([])
        for model_num in range(0, len(inargs.toa_files)):
            toa_file = inargs.toa_files[model_num]
            thetao_sh_file = inargs.thetao_sh_files[model_num]
            thetao_nh_file = inargs.thetao_nh_files[model_num]

            ita_cube, ita_history = calc_hemispheric_value(thetao_sh_file, thetao_nh_file, time_constraint, model_num)
            ita_cube_list.append(ita_cube)
            eei_cube = iris.load_cube(toa_file, time_constraint)
            eei_history = eei_cube.attributes['history']
            eei_cube_list.append(eei_cube) 

        ita_ensemble_agg = ensemble_aggregation(ita_cube_list, inargs.ensagg)
        ita_ensemble_spread = ensemble_aggregation(ita_cube_list, 'percentile')    
        eei_ensemble_agg = ensemble_aggregation(eei_cube_list, inargs.ensagg)
    
        temporal_plot(ax1, ita_ensemble_agg, ita_ensemble_spread, experiment)
        eei_plot(ax2, eei_ensemble_agg, ita_ensemble_agg, experiment)   

    temporal_plot_features(ax1)
    eei_plot_features(ax2)
    
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)

    infile_metadata = {thetao_nh_file: ita_history, toa_file: eei_history}
    log_text = cmdprov.new_log(infile_history=infile_metadata, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot the interhemispheric temperature asymmetry versus the planetary energy imbalance'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="output file")
    parser.add_argument("experiment_list", type=str, nargs='*',
                        choices=('historical', 'historical-rcp85', 'GHG-only', 'AA-only', '1pctCO2'),
                        help="experiments to plot")

    parser.add_argument("--toa_files", type=str, nargs='*', action='append',
                        help="global sum netTOA files for a given experiment")                     
    parser.add_argument("--thetao_sh_files", type=str, nargs='*', action='append',
                        help="SH mean thetao files for a given experiment")
    parser.add_argument("--thetao_sh_files", type=str, nargs='*', action='append',
                        help="NH mean thetao files for a given experiment")

    parser.add_argument("--ensagg", type=str, default='median', choices=('mean', 'median'),
                        help="Ensemble mean or median [default=median]")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    parser.add_argument("--historical_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'),
                        help="Time period for historical experiments [default = entire]")
    parser.add_argument("--rcp_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2100-12-31'),
                        help="Time period for rcp experiments [default = entire]")
    parser.add_argument("--pctCO2_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2000-12-31'),
                        help="Time period for 1pctCO2 experiment [default = entire]")

    args = parser.parse_args() 
    
    nexp = len(args.experiment_list)
    assert len(args.toa_files) == nexp
    assert len(args.thetao_nh_files) == nexp
    assert len(args.thetao_sh_files) == nexp
     
    main(args)
