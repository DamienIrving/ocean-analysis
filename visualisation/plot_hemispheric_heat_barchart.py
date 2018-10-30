"""
Filename:     plot_hemispheric_heat_barchart.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot barchart comparing heat uptake/storage in either hemisphere

"""

# Import general Python modules

import sys, os, pdb
import re
import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as tkr
import seaborn
import pandas
import iris
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

mpl.rcParams['axes.labelsize'] = 16
mpl.rcParams['axes.titlesize'] = 20
mpl.rcParams['xtick.labelsize'] = 16
mpl.rcParams['ytick.labelsize'] = 16
mpl.rcParams['legend.fontsize'] = 16


def calc_hemispheric_heat(sh_file, nh_file, var, experiment, time_constraint):
    """Calculate the interhemispheric difference timeseries."""

    names = {'ohc': 'ocean heat content',
             'hfds': 'Downward Heat Flux at Sea Water Surface',
             'rndt': 'TOA Incoming Net Radiation',
             'thetao': 'Sea Water Potential Temperature'}

    sh_name = names[var] + ' sh sum'
    sh_cube = iris.load_cube(sh_file, sh_name & time_constraint)
    sh_value = sh_cube.data[-1] - sh_cube.data[0]

    nh_name = names[var] + ' nh sum'
    nh_cube = iris.load_cube(nh_file, nh_name & time_constraint)
    nh_value = nh_cube.data[-1] - nh_cube.data[0]
    
    assert experiment == nh_cube.attributes['experiment_id']
    model = nh_cube.attributes['model_id']
    history = nh_cube.attributes['history']
    
    return sh_value, nh_value, model, history


def generate_heat_row_dicts(column_list, sh_value, nh_value, model, experiment, var, ylabel):
    """Generate dict that will form a row of a pandas dataframe."""

    experiment_names = {'historical': 'historical',
                        'historicalGHG': 'GHG-only',
                        'historicalMisc': 'AA-only',
                        'historical-rcp85': 'historical-rcp85',
                        '1pctCO2': '1pctCO2'}
    variable_names = {'rndt': 'netTOA', 'hfds': 'OHU', 'ohc': 'OHC'}
    hemispheres = ['SH', 'NH']
    
    for index, value in enumerate([sh_value, nh_value]):
        row_dict = {'model': model,
                    'experiment': experiment_names[experiment],
                    'hemisphere': hemispheres[index],
                    'variable': variable_names[var],
                    ylabel: value}
        column_list.append(row_dict)
        
    return column_list


def get_ylabel(toa_files, ohu_files, ohc_files):
    """Get the label for the yaxis"""
    
    toa_plot = False if toa_files == [] else True
    ohu_plot = False if ohu_files == [] else True
    ohc_plot = False if ohc_files == [] else True

    ylabel = 'heat uptake/storage (J)'
    if not ohc_plot:
        ylabel = 'heat uptake (J)'
    elif not (toa_plot or ohu_plot):
        ylabel = 'heat storage (J)'

    return ylabel


def get_colors(exp_list):
    """Get bar colors."""

    colors = {'historical': '0.5',
              'historical-rcp85': '0.5',
              'historicalGHG': 'red',
              'historicalMisc': 'blue',
              '1pctCO2': 'orange'}

    color_list = []
    for experiment in exp_list:
        color_list.append(colors[experiment])

    return color_list


def main(inargs):
    """Run the program."""

    time_constraints = {'historical': gio.get_time_constraint(inargs.hist_time),
                        'historical-rcp85': gio.get_time_constraint(inargs.hist_time),
                        'historicalGHG': gio.get_time_constraint(inargs.hist_time),
                        'historicalMisc': gio.get_time_constraint(inargs.hist_time),
                        '1pctCO2': gio.get_time_constraint(inargs.pctCO2_time)}

    file_variables = ['rndt', 'hfds', 'ohc']
    column_list = []
    ylabel = get_ylabel(inargs.toa_files, inargs.ohu_files, inargs.ohc_files)
    
    for var_index, var_files in enumerate([inargs.toa_files, inargs.ohu_files, inargs.ohc_files]):
        var = file_variables[var_index]
        for model_files in var_files:
            for exp_index, file_pair in enumerate([model_files[i:i + 2] for i in range(0, len(model_files), 2)]):
                experiment = inargs.experiment_list[exp_index]
                time_constraint = time_constraints[experiment]
                sh_file, nh_file = file_pair  
                sh_value, nh_value, model, history = calc_hemispheric_heat(sh_file, nh_file, var, experiment, time_constraint)
                column_list = generate_heat_row_dicts(column_list, sh_value, nh_value, model, experiment, var, ylabel)
    heat_df = pandas.DataFrame(column_list)

    color_list = get_colors(inargs.experiment_list)
    seaborn.set_style("whitegrid")
    g = seaborn.catplot(x="hemisphere", y=ylabel,
                        hue="experiment", col="variable",
                        data=heat_df, kind="bar",
                        palette=color_list)
    g.set_titles("{col_name}")

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

    description = 'Plot barchart comparing heat uptake/storage in either hemisphere'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="output file")

    parser.add_argument("--toa_files", type=str, nargs='*', action='append', default=[],
                        help="netTOA files in this order: exp1 NH, exp1 SH, exp2 NH, exp2 SH, etc")                     
    parser.add_argument("--ohu_files", type=str, nargs='*', action='append', default=[],
                        help="OHU files in this order: exp1 NH, exp1 SH, exp2 NH, exp2 SH, etc")
    parser.add_argument("--ohc_files", type=str, nargs='*', action='append', default=[],
                        help="OHC files in this order: exp1 NH, exp1 SH, exp2 NH, exp2 SH, etc")

    parser.add_argument("--experiment_list", type=str, nargs='*',
                        choices=('historical', 'historical-rcp85', 'historicalGHG', 'historicalMisc', '1pctCO2'),
                        help="experiments to plot")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    parser.add_argument("--hist_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'),
                        help="Time period for historical experiments [default = 1861-2005]")
    parser.add_argument("--pctCO2_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2000-12-31'),
                        help="Time period for 1pctCO2 experiment [default = 1861-2000]")


    args = parser.parse_args()             
    main(args)
