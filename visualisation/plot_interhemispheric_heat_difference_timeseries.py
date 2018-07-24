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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

var_colors = {'ohc': 'blue', 'hfds': 'orange', 'rndt': 'red'}
exp_colors = {'historical-rcp85': 'black', 'historicalGHG': 'red', 'historicalAA': 'blue'}

names = {'ohc': 'ocean heat content',
         'hfds': 'Downward Heat Flux at Sea Water Surface',
         'rndt': 'TOA Incoming Net Radiation'}

titles = ['netTOA', 'OHU', 'OHC']

plot_variables = {'ohc': 'OHC',
                  'hfds': 'OHU',
                  'rndt': 'netTOA'}

aa_physics = {'CanESM2': 'p4', 'CCSM4': 'p10', 'CSIRO-Mk3-6-0': 'p4',
              'GFDL-CM3': 'p1', 'GISS-E2-H': 'p107', 'GISS-E2-R': 'p107', 'NorESM1-M': 'p1'}

linestyles = {'historical-rcp85': 'solid', 'historicalGHG': '--', 'historicalAA': ':'}
#linestyles = {'rndt': 'solid', 'hfds': '--', 'ohc': ':'}


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
    else:
        ensemble_agg = cube_list[0]

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


def calc_interhemispheric_diff(nh_file, sh_file, var, time_constraint, ensemble_number):
    """Calculate the interhemispheric difference timeseries."""

    nh_name = names[var] + ' nh sum'
    nh_cube = iris.load_cube(nh_file, nh_name & time_constraint)
    nh_attributes = get_simulation_attributes(nh_cube)
    nh_anomaly = calc_anomaly(nh_cube)

    sh_name = names[var] + ' sh sum'
    sh_cube = iris.load_cube(sh_file, sh_name & time_constraint)
    sh_attributes = get_simulation_attributes(sh_cube)
    sh_anomaly = calc_anomaly(sh_cube)

    assert nh_attributes == sh_attributes 

    diff = nh_cube.copy()
    diff.data = nh_anomaly.data - sh_anomaly.data

    new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
    diff.add_aux_coord(new_aux_coord)

    diff.cell_methods = ()

    return diff


def get_file_pair(var, model, experiment):
    """Get a file pair of interest"""

    dir_experiment = 'rcp85' if experiment == 'historical-rcp85' else experiment 
    mip = 'r1i1' + aa_physics[model] if experiment == 'historicalMisc' else 'r1i1p1'
    time_info = 'all' if var == 'ohc' else 'cumsum-all'
    tscale = 'Ayr' if var == 'rndt' else 'Oyr'
    realm = 'atmos' if var =='rndt' else 'ocean'

    mydir = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/yr/%s/%s/%s/latest/dedrifted'  %(model, dir_experiment, realm, mip, var)
 
    output = {}
    for region in ['nh', 'sh']:
        file_start = '%s*%s-sum'  %(var, region)
        files = glob.glob('%s/%s_*.nc' %(mydir, file_start))
        assert len(files) == 1, 'File search failed for %s, %s, %s' %(var, model, experiment)
        output[region] = files[0]

    return output['nh'], output['sh']


def set_plot_features(inargs, ax):
    """ """

    if inargs.ylim:
        ylower, yupper = inargs.ylim
        plt.ylim(ylower * 1e24, yupper * 1e24)
  
    ax.set_ylabel('NH minus SH (Joules)')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
    ax.yaxis.major.formatter._useMathText = True
        
    plt.legend(loc=3)


def main(inargs):
    """Run the program."""

    #metadata_dict = {}
    #plt.axvline(x=0, color='0.5', linestyle='--')

    if inargs.plot_type == 'single':
        fig, ax = plt.subplots()
    else:
        fig = plt.figure(figsize=[30, 7])
        gs = gridspec.GridSpec(1, 3)
        axes = [plt.subplot(gs[0]), plt.subplot(gs[1]), plt.subplot(gs[2])]

    for experiment in inargs.experiments:
        plot_experiment = 'historicalAA' if experiment == 'historicalMisc' else experiment
        ensemble_dict = {}
        upper_time_bound = '2100-12-31' if experiment == 'historical-rcp85' else '2005-12-31'
        time_constraint = gio.get_time_constraint(['1861-01-01', upper_time_bound])
        for index, var in enumerate(['rndt', 'hfds', 'ohc']):
            cube_list = iris.cube.CubeList([])
            for file_num, model in enumerate(inargs.models):
                nh_file, sh_file = get_file_pair(var, model, experiment)
                diff = calc_interhemispheric_diff(nh_file, sh_file, var, time_constraint, file_num)
                cube_list.append(diff)
                if inargs.plot_type == 'panels' and inargs.individual:
                    plt.sca(axes[index])
                    iplt.plot(diff, color=exp_colors[plot_experiment], linewidth=0.3)

            ensemble_dict[var] = ensemble_aggregation(cube_list, inargs.ensagg)
            
            if inargs.plot_type == 'single':
                plot_label = plot_variables[var] if experiment == 'historical-rcp85' else None
                iplt.plot(ensemble_dict[var], label=plot_label, color=var_colors[var], linestyle=linestyles[plot_experiment])
            else:
                plt.sca(axes[index])
                iplt.plot(ensemble_dict[var], label=plot_experiment, color=exp_colors[plot_experiment])
                    
    if inargs.plot_type == 'single':
        plt.title('interhemispheric difference in accumulated heat')
        set_plot_features(inargs, ax)
    else:
        plt.suptitle('interhemispheric difference in accumulated heat')
        for index in range(3):
            plt.sca(axes[index])
            plt.title(titles[index])
            set_plot_features(inargs, axes[index])
            
            
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

    parser.add_argument("--ylim", type=float, nargs=2, default=None,
                        help="y limits for plots (x 10^24)")

    parser.add_argument("--experiments", type=str, nargs='*',
                        choices=('historical-rcp85', 'historicalGHG', 'historicalMisc'),
                        default=('historical-rcp85', 'historicalGHG', 'historicalMisc'),
                        help="experiments to plot")                               

    parser.add_argument("--ensagg", type=str, default='median', choices=('mean', 'median'),
                        help="Ensemble mean or median [default=median]")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    parser.add_argument("--individual", action="store_true", default=False,
                        help="Show curves for individual models [default=False]")

    args = parser.parse_args()             
    main(args)
