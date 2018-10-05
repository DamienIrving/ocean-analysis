"""
Filename:     plot_interhemispheric_heat_difference_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ensemble interhemispheric heat difference timeseries for OHC, hfds and rndt

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
exp_colors = {'historical-rcp85': 'black', 'GHG-only': 'red', 'AA-only': 'blue'}
exp_start = {'historical-rcp85': 0, 'GHG-only': 2, 'AA-only': 4}

names = {'thetao': 'Sea Water Potential Temperature',
         'ohc': 'ocean heat content',
         'hfds': 'Downward Heat Flux at Sea Water Surface',
         'rndt': 'TOA Incoming Net Radiation'}

titles = {'rndt': 'netTOA', 'hfds': 'OHU', 'ohc': 'OHC', 'thetao': 'Average Ocean Temperature'}

plot_variables = {'thetao': ' Average Ocean Temperature',
                  'ohc': 'OHC',
                  'hfds': 'OHU',
                  'rndt': 'netTOA'}

linestyles = {'historical-rcp85': 'solid', 'GHG-only': '--', 'AA-only': ':'}

grid_configs = {1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (2, 2)} 

seaborn.set(style='ticks')

mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['axes.titlesize'] = 28
mpl.rcParams['xtick.labelsize'] = 24
mpl.rcParams['ytick.labelsize'] = 24
mpl.rcParams['legend.fontsize'] = 24


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
    """Calculate the ensemble mean."""

    aggregators = {'mean': iris.analysis.MEAN, 'median': iris.analysis.MEDIAN}

    if len(cube_list) > 1:
        equalise_attributes(cube_list)
        equalise_time_axes(cube_list)
        ensemble_cube = cube_list.merge_cube()
        ensemble_agg = ensemble_cube.collapsed('ensemble_member', aggregators[operator])
        ensemble_spread = ensemble_cube.collapsed('ensemble_member', iris.analysis.PERCENTILE, percent=[25, 75])
    else:
        ensemble_agg = cube_list[0]
        ensemble_spread = None

    return ensemble_agg, ensemble_spread


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


def calc_hemispheric_value(sh_file, nh_file, val_type, var, time_constraint, ensemble_number):
    """Calculate the interhemispheric difference timeseries."""

    agg = 'mean' if var =='thetao' else 'sum'

    nh_name = names[var] + ' nh ' + agg
    nh_cube = iris.load_cube(nh_file, nh_name & time_constraint)
    nh_attributes = get_simulation_attributes(nh_cube)
    nh_anomaly = calc_anomaly(nh_cube)

    sh_name = names[var] + ' sh ' + agg
    sh_cube = iris.load_cube(sh_file, sh_name & time_constraint)
    sh_attributes = get_simulation_attributes(sh_cube)
    sh_anomaly = calc_anomaly(sh_cube)

    assert nh_attributes == sh_attributes 

    metric = nh_cube.copy()
    if var == 'ohc-adjusted':
        globe_data = nh_cube.data + sh_cube.data
        globe_anomaly = sh_anomaly.data + nh_anomaly.data
        nh_mean = nh_cube.data.mean()
        globe_mean = globe_data.mean()
        constant = 1 - 2*(nh_mean/globe_mean)
        diff = nh_anomaly.data - sh_anomaly.data
        metric.data = diff + (globe_anomaly * constant)  
    else:
        if val_type == 'diff':
            metric.data = nh_anomaly.data - sh_anomaly.data
        elif val_type == 'sh':
            metric.data = sh_anomaly.data
        elif val_type == 'nh': 
            metric.data = nh_anomaly.data

    new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
    metric.add_aux_coord(new_aux_coord)
    metric.cell_methods = ()

    return metric, nh_cube.attributes['history']


def set_plot_features(inargs, ax, plotnum, var, nvars):
    """ """
        
    if inargs.ylim_uptake and var in ['rndt', 'hfds']:
        ylower, yupper = inargs.ylim_uptake
        plt.ylim(ylower * 1e24, yupper * 1e24)
    elif inargs.ylim_ohc and var == 'ohc':
        ylower, yupper = inargs.ylim_ohc
        plt.ylim(ylower * 1e24, yupper * 1e24)
    elif inargs.ylim_temperature and var == 'thetao':
        ylower, yupper = inargs.ylim_temperature
        plt.ylim(ylower, yupper)

    if not (nvars == 4 and plotnum in [0, 1]):
        ax.set_xlabel('Year')

    if var in ['rndt', 'hfds', 'ohc']:
        ax.set_ylabel('NH minus SH (Joules)')
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
        ax.yaxis.major.formatter._useMathText = True
    else:
        ax.set_ylabel('NH minus SH (K)')

    ax.tick_params(top='off') 

    if nvars > 1:
        panel_labels = {0: '(a)', 1: '(b)', 2: '(c)', 3: '(d)'}
        ax.text(0.93, 0.97, panel_labels[plotnum], transform=ax.transAxes,
                fontsize=24, va='top')

    if var == 'thetao' or inargs.metric in ['sh', 'nh']:
        plt.legend(loc=2)
    else:
        plt.legend(loc=3)

    if inargs.metric in ['sh', 'nh']:
        ax.axhline(y=0, color='0.5', linestyle='--', linewidth=0.5)


def get_plot_vars(inargs):
    """Count the number of variables to plot"""
    
    vars = ['rndt', 'hfds', 'ohc', 'thetao']
    plot_vars = []
    plot_files = []
    for var_index, file_list in enumerate([inargs.toa_files, inargs.ohu_files, inargs.ohc_files, inargs.thetao_files]):
        if file_list:
            plot_vars.append(vars[var_index])
            plot_files.append(file_list)
            
    return plot_vars, plot_files


def main(inargs):
    """Run the program."""

    plot_vars, plot_files = get_plot_vars(inargs)
    nvars = len(plot_vars)
    nrows, ncols = grid_configs[nvars]

    fig = plt.figure(figsize=[11 * ncols, 7 * nrows])
    gs = gridspec.GridSpec(nrows, ncols, wspace=0.27, hspace=0.25)
    axes = []
    for index in range(nvars):
        axes.append(plt.subplot(gs[index]))

    time_constraints = {'historical-rcp85': gio.get_time_constraint(inargs.rcp_time),
                        'GHG-only': gio.get_time_constraint(inargs.historical_time),
                        'AA-only': gio.get_time_constraint(inargs.historical_time)}

    for experiment in ['historical-rcp85', 'GHG-only', 'AA-only']:
        time_constraint = time_constraints[experiment]
        ensemble_agg_dict = {}
        ensemble_spread_dict = {}
        for var_index, var_files in enumerate(plot_files):
            var = plot_vars[var_index]
            cube_list = iris.cube.CubeList([])
            for model_num, model_files in enumerate(var_files):
                start = exp_start[experiment]
                sh_file, nh_file = model_files[start: start+2]
                value, history = calc_hemispheric_value(sh_file, nh_file, inargs.metric, var, time_constraint, model_num)
                cube_list.append(value)
                if inargs.individual:
                    plt.sca(axes[var_index])
                    iplt.plot(value, color=exp_colors[experiment], linewidth=0.3)

            ensemble_agg_dict[var], ensemble_spread_dict[var] = ensemble_aggregation(cube_list, inargs.ensagg)
            
            plt.sca(axes[var_index])
            iplt.plot(ensemble_agg_dict[var], label=experiment, color=exp_colors[experiment])
            if ensemble_spread_dict[var]:
                time_values = ensemble_spread_dict[var][0, ::].coord('time').points - 54567.5 
                            # ensemble_spread_dict[var][0, ::].coord('time').points[-7]
                upper_bound = ensemble_spread_dict[var][0, ::].data
                lower_bound = ensemble_spread_dict[var][-1, ::].data
                iplt.plt.fill_between(time_values, upper_bound, lower_bound, facecolor=exp_colors[experiment], alpha=0.15)
                    
    if inargs.title:
        plt.suptitle('interhemispheric difference in accumulated heat')
    for index, var in enumerate(plot_vars):
        plt.sca(axes[index])
        if nvars > 1:
            plt.title(titles[var])
        set_plot_features(inargs, axes[index], index, var, nvars)
            
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)

    log_text = cmdprov.new_log(infile_history={nh_file: history}, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot ensemble interhemispheric heat difference boxplot for OHC, hfds and rndt'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="output file")

    parser.add_argument("--metric", type=str, default='diff', choices=('diff', 'nh', 'sh'),
                        help="Metric to plot (hemispheric values or difference) [default=diff]")

    parser.add_argument("--toa_files", type=str, nargs=6, action='append', default=[],
                        help="netTOA files in this order: hist-rcp NH, hist-rcp SH, GHG NH, GHG SH, AA NH, AA SH")                     
    parser.add_argument("--ohu_files", type=str, nargs=6, action='append', default=[],
                        help="OHU files in this order: hist-rcp NH, hist-rcp SH, GHG NH, GHG SH, AA NH, AA SH")
    parser.add_argument("--ohc_files", type=str, nargs=6, action='append', default=[],
                        help="OHC files in this order: hist-rcp NH, hist-rcp SH, GHG NH, GHG SH, AA NH, AA SH")
    parser.add_argument("--thetao_files", type=str, nargs=6, action='append', default=[],
                        help="thetao files in this order: hist-rcp NH, hist-rcp SH, GHG NH, GHG SH, AA NH, AA SH")

    parser.add_argument("--ylim_uptake", type=float, nargs=2, default=None,
                        help="y limits for netTOA and OHU plots (x 10^24)")
    parser.add_argument("--ylim_ohc", type=float, nargs=2, default=None,
                        help="y limits for OHC plots (x 10^24)")
    parser.add_argument("--ylim_temperature", type=float, nargs=2, default=None,
                        help="y limits for ocean temperature plots")                              

    parser.add_argument("--ensagg", type=str, default='median', choices=('mean', 'median'),
                        help="Ensemble mean or median [default=median]")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    parser.add_argument("--title", action="store_true", default=False,
                        help="Include a plot title [default=False]")
    parser.add_argument("--individual", action="store_true", default=False,
                        help="Show curves for individual models [default=False]")

    parser.add_argument("--historical_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'),
                        help="Time period [default = entire]")
    parser.add_argument("--rcp_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2100-12-31'),
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
