"""
Filename:     plot_hemispheric_heat_barchart.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot barchart comparing heat uptake/storage in either hemisphere

"""

# Import general Python modules

import sys, os, pdb
import re
import argparse
import itertools
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

experiment_names = {'historical': 'historical',
                    'historicalGHG': 'GHG-only',
                    'historicalMisc': 'AA-only',
                    'historical-rcp85': 'historical-rcp85',
                    '1pctCO2': '1pctCO2'}
variable_names = {'rndt': 'netTOA', 'hfds': 'OHU', 'ohc': 'OHC'}
region_names = {'sh': 'SH', 'nh': 'NH', 'globe': 'Globe'}

def calc_hemispheric_heat(file_group, regions, var, experiment, time_constraint):
    """Calculate the interhemispheric difference timeseries."""

    names = {'ohc': 'ocean heat content',
             'hfds': 'Downward Heat Flux at Sea Water Surface',
             'rndt': 'TOA Incoming Net Radiation',
             'thetao': 'Sea Water Potential Temperature'}

    values = []
    for filenum, region in enumerate(regions):
        var_name = '%s %s sum'  %(names[var], region)
        print(file_group[filenum])
        cube = iris.load_cube(file_group[filenum], var_name & time_constraint)
        values.append(cube.data[-1] - cube.data[0])
    
        assert experiment == cube.attributes['experiment_id']
    
    model = cube.attributes['model_id']
    history = cube.attributes['history']
    
    return values, model, history


def generate_heat_row_dicts(column_list, values, regions, model, experiment, var, ylabel):
    """Generate dict that will form a row of a pandas dataframe."""
    
    for index, value in enumerate(values):
        row_dict = {'model': model,
                    'experiment': experiment_names[experiment],
                    'hemisphere': region_names[regions[index]],
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
        ylabel = 'change in OHC (J)'

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


def write_values(df, ylabel, variables, experiments, hemispheres, outfile, figtype):
    """Write values to file"""

    fout = open(outfile.replace(figtype, '.txt'), 'w')
    for variable, experiment, hemisphere in itertools.product(variables, experiments, hemispheres):
        variable = variable_names[variable]
        experiment = experiment_names[experiment]
        hemisphere = region_names[hemisphere]
        selection = df.loc[(df['experiment'] == experiment) & (df['hemisphere'] == hemisphere) & (df['variable'] == variable)]
        ave = selection[ylabel].mean()
        label = '%s, %s, %s:'  %(variable, experiment, hemisphere)
        fout.write(label + ' ' + str(ave) + '\n')
    fout.close()


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
    nregions = len(inargs.regions)
    figtype = '.' + inargs.outfile.split('.')[-1]    

    for var_index, var_files in enumerate([inargs.toa_files, inargs.ohu_files, inargs.ohc_files]):
        var = file_variables[var_index]
        for model_files in var_files:
            for exp_index, file_group in enumerate([model_files[i:i + nregions] for i in range(0, len(model_files), nregions)]):
                experiment = inargs.experiments[exp_index]
                time_constraint = time_constraints[experiment]  
                values, model, history = calc_hemispheric_heat(file_group, inargs.regions, var, experiment, time_constraint)
                column_list = generate_heat_row_dicts(column_list, values, inargs.regions, model, experiment, var, ylabel)
    heat_df = pandas.DataFrame(column_list)

    write_values(heat_df, ylabel, file_variables, inargs.experiments, inargs.regions, inargs.outfile, figtype)

    color_list = get_colors(inargs.experiments)
    seaborn.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(16,10))
    g = seaborn.catplot(x="hemisphere", y=ylabel,
                        hue="experiment", col="variable",
                        data=heat_df, kind="bar",
                        palette=color_list)
    g.set_titles("{col_name}")

    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
    ax.yaxis.major.formatter._useMathText = True

    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)

    log_text = cmdprov.new_log(infile_history={file_group[-1]: history}, git_repo=repo_dir)
    log_file = re.sub(figtype, '.met', inargs.outfile)
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
                        help="netTOA files in this order: exp1 globe, exp1 NH, exp1 SH, exp2 globe, exp2 NH, exp2 SH, etc")                     
    parser.add_argument("--ohu_files", type=str, nargs='*', action='append', default=[],
                        help="OHU files in this order: exp1 globe, exp1 NH, exp1 SH, exp2 globe, exp2 NH, exp2 SH, etc")
    parser.add_argument("--ohc_files", type=str, nargs='*', action='append', default=[],
                        help="OHC files in this order: exp1 globe, exp1 NH, exp1 SH, exp2 globe, exp2 NH, exp2 SH, etc")

    parser.add_argument("--experiments", type=str, nargs='*',
                        choices=('historical', 'historical-rcp85', 'historicalGHG', 'historicalMisc', '1pctCO2'),
                        help="experiments to plot")
    parser.add_argument("--regions", type=str, nargs='*',
                        choices=('globe', 'sh', 'nh'),
                        help="regions to plot (in order Globe, SH, NH)")

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
