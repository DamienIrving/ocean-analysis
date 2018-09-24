"""
Filename:     plot_interhemispheric_heat_difference_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ensemble interhemispheric heat difference timeseries for OHC, hfds and rndt

"""

# Import general Python modules

import sys, os, pdb, glob
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec

import seaborn
import matplotlib as mpl

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

exp_labels = {'historical-rcp85': 'historical-rcp85', 'historicalGHG': 'GHG-only', 'historicalMisc': 'AA-only'}

var_colors = {'ohc': 'blue', 'hfds': 'orange', 'rndt': 'red'}
exp_colors = {'historical-rcp85': 'black', 'GHG-only': 'red', 'AA-only': 'blue'}

names = {'thetao': 'Sea Water Potential Temperature',
         'ohc': 'ocean heat content',
         'hfds': 'Downward Heat Flux at Sea Water Surface',
         'rndt': 'TOA Incoming Net Radiation'}

titles = ['netTOA', 'OHU', 'OHC', 'Average Ocean Temperature']

plot_variables = {'thetao': ' Average Ocean Temperature',
                  'ohc': 'OHC',
                  'hfds': 'OHU',
                  'rndt': 'netTOA'}

aa_physics = {'CanESM2': 'p4', 'CCSM4': 'p10', 'CSIRO-Mk3-6-0': 'p4',
              'GFDL-CM3': 'p1', 'GISS-E2-H': 'p107', 'GISS-E2-R': 'p107', 'NorESM1-M': 'p1'}

linestyles = {'historical-rcp85': 'solid', 'GHG-only': '--', 'AA-only': ':'}

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


def calc_interhemispheric_diff(nh_file, sh_file, var, time_constraint, ensemble_number):
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
        metric.data = nh_anomaly.data - sh_anomaly.data

    new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
    metric.add_aux_coord(new_aux_coord)
    metric.cell_methods = ()

    return metric


def get_file_pair(var, model, experiment):
    """Get a file pair of interest"""

    var = 'ohc' if var == 'ohc-adjusted' else var
    dir_experiment = 'rcp85' if experiment == 'historical-rcp85' else experiment 
    mip = 'r1i1' + aa_physics[model] if experiment == 'historicalMisc' else 'r1i1p1'
    time_info = 'all' if var in ['ohc', 'thetao'] else 'cumsum-all'
    tscale = 'Ayr' if var == 'rndt' else 'Oyr'
    realm = 'atmos' if var =='rndt' else 'ocean'
    var = 'ohc' if var == 'ohc-adjusted' else var
    agg = 'mean' if var == 'thetao' else 'sum'

    mydir = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/yr/%s/%s/%s/latest/dedrifted'  %(model, dir_experiment, realm, mip, var)
 
    output = {}
    for region in ['nh', 'sh']:
        file_start = '%s*%s-%s'  %(var, region, agg)
        files = glob.glob('%s/%s_*%s.nc' %(mydir, file_start, time_info))
        assert len(files) == 1, '%s/%s_*%s.nc' %(mydir, file_start, time_info)
        output[region] = files[0]
   
    return output['nh'], output['sh']


def set_plot_features(inargs, ax, plotnum):
    """ """
        
    if inargs.ylim_uptake and plotnum in [0, 1]:
        ylower, yupper = inargs.ylim_uptake
        plt.ylim(ylower * 1e24, yupper * 1e24)
    elif inargs.ylim_ohc and plotnum == 2:
        ylower, yupper = inargs.ylim_ohc
        plt.ylim(ylower * 1e24, yupper * 1e24)
    elif inargs.ylim_temperature and plotnum == 3:
        ylower, yupper = inargs.ylim_temperature
        plt.ylim(ylower, yupper)

    if plotnum in [2, 3]:
        ax.set_xlabel('Year')

    if plotnum in [0, 1, 2]:
        ax.set_ylabel('NH minus SH (Joules)')
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
        ax.yaxis.major.formatter._useMathText = True
    else:
        ax.set_ylabel('NH minus SH (K)')

    ax.tick_params(top='off') 

    if plotnum == 3:
        plt.legend(loc=2)
    else:
        plt.legend(loc=3)


def main(inargs):
    """Run the program."""

    #metadata_dict = {}
    #plt.axvline(x=0, color='0.5', linestyle='--')

    if inargs.plot_type == 'single':
        fig, ax = plt.subplots()
    else:
        fig = plt.figure(figsize=[22, 14])
        gs = gridspec.GridSpec(2, 2, wspace=0.27, hspace=0.25)
        axes = [plt.subplot(gs[0]), plt.subplot(gs[1]), plt.subplot(gs[2]), plt.subplot(gs[3])]

    for experiment in inargs.experiments:
        plot_experiment = exp_labels[experiment]
        ensemble_agg_dict = {}
        ensemble_spread_dict = {}
        upper_time_bound = '2100-12-31' if experiment == 'historical-rcp85' else '2005-12-31'
        time_constraint = gio.get_time_constraint(['1861-01-01', upper_time_bound])
        for index, var in enumerate(['rndt', 'hfds', 'ohc', 'thetao']):
            cube_list = iris.cube.CubeList([])
            for file_num, model in enumerate(inargs.models):
                nh_file, sh_file = get_file_pair(var, model, experiment)
                diff = calc_interhemispheric_diff(nh_file, sh_file, var, time_constraint, file_num)
                cube_list.append(diff)
                if inargs.plot_type == 'panels' and inargs.individual:
                    plt.sca(axes[index])
                    iplt.plot(diff, color=exp_colors[plot_experiment], linewidth=0.3)

            ensemble_agg_dict[var], ensemble_spread_dict[var] = ensemble_aggregation(cube_list, inargs.ensagg)
            
            if inargs.plot_type == 'single':
                plot_label = plot_variables[var] if experiment == 'historical-rcp85' else None
                iplt.plot(ensemble_agg_dict[var], label=plot_label, color=var_colors[var], linestyle=linestyles[plot_experiment])
            else:
                plt.sca(axes[index])
                iplt.plot(ensemble_agg_dict[var], label=plot_experiment, color=exp_colors[plot_experiment])
                if ensemble_spread_dict[var]:
                    time_values = ensemble_spread_dict[var][0, ::].coord('time').points - 54567.5    # ensemble_spread_dict[var][0, ::].coord('time').points[-7]
                    upper_bound = ensemble_spread_dict[var][0, ::].data
                    lower_bound = ensemble_spread_dict[var][-1, ::].data
                    iplt.plt.fill_between(time_values, upper_bound, lower_bound, facecolor=exp_colors[plot_experiment], alpha=0.15)
                    
    if inargs.plot_type == 'single':
        if inargs.title:
            plt.title('interhemispheric difference in accumulated heat')
        set_plot_features(inargs, ax)
    else:
        if inargs.title:
            plt.suptitle('interhemispheric difference in accumulated heat')
        for index in range(4):
            plt.sca(axes[index])
            plt.title(titles[index])
            set_plot_features(inargs, axes[index], index)
            
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)

    gio.write_metadata(inargs.outfile)


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

    parser.add_argument("models", type=str, nargs='*', help="models")
    parser.add_argument("plot_type", type=str, choices=('single', 'panels'), help="plot type")
    parser.add_argument("outfile", type=str, help="output file")

    parser.add_argument("--ylim_uptake", type=float, nargs=2, default=None,
                        help="y limits for netTOA and OHU plots (x 10^24)")
    parser.add_argument("--ylim_ohc", type=float, nargs=2, default=None,
                        help="y limits for OHC plots (x 10^24)")
    parser.add_argument("--ylim_temperature", type=float, nargs=2, default=None,
                        help="y limits for ocean temperature plots")

    parser.add_argument("--experiments", type=str, nargs='*',
                        choices=('historical-rcp85', 'historicalGHG', 'historicalMisc'),
                        default=('historical-rcp85', 'historicalGHG', 'historicalMisc'),
                        help="experiments to plot")                               

    parser.add_argument("--ensagg", type=str, default='median', choices=('mean', 'median'),
                        help="Ensemble mean or median [default=median]")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    parser.add_argument("--title", action="store_true", default=False,
                        help="Include a plot title [default=False]")
    parser.add_argument("--individual", action="store_true", default=False,
                        help="Show curves for individual models [default=False]")

    args = parser.parse_args()             
    main(args)
