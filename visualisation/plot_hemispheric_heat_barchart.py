"""
Filename:     plot_hemispheric_heat_barchart.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot barchart comparing heat uptake/storage in either hemisphere

"""

# Import general Python modules

import sys, os, pdb
import argparse
import iris
import matplotlib.pyplot as plt
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

mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['axes.titlesize'] = 28
mpl.rcParams['xtick.labelsize'] = 24
mpl.rcParams['ytick.labelsize'] = 24
mpl.rcParams['legend.fontsize'] = 24


def calc_hemispheric_heat(nh_file, sh_file, var, time_constraint):
    """Calculate the interhemispheric difference timeseries."""

    nh_name = names[var] + ' nh sum'
    nh_cube = iris.load_cube(nh_file, nh_name & time_constraint)
    nh_value = nh_cube.data[-1] - nh_cube.data[0]
 
    sh_name = names[var] + ' sh sum'
    sh_cube = iris.load_cube(sh_file, sh_name & time_constraint)
    sh_value = sh_cube.data[-1] - sh_cube.data[0]
    
    experiment = nh_cube.attributes['experiment_id']
    model = nh_cube.attributes['model_id']
    history = nh_cube.attributes['history']
    
    return sh_value, nh_value, experiment, history


def generate_heat_row_dicts(column_list, sh_value, nh_value, model, experiment, var, ylabel):
    """Generate dict that will form a row of a pandas dataframe."""

    experiment_names = {'historical': 'historical',
                        'historicalGHG': 'GHG-only',
                        'historicalMisc': 'AA-only'}
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
    
    if (toa_files or ohu_files) and ohc_files:
        ylabel = 'heat uptake/storage (J)'
    elif not ohc_files:
        ylabel = 'heat uptake (J)'
    else:
        ylabel = 'heat storage (J)'


def main(inargs):
    """Run the program."""

    file_variables = ['rndt', 'hfds', 'ohc']
    time_constraint = gio.get_time_constraint(inargs.time)
    column_list = []
    ylabel = get_ylabel(inargs.toa_files, inargs.ohu_files, inargs.ohc_files)
    
    for var_index, var_files in enumerate([inargs.toa_files, inargs.ohu_files, inargs.ohc_files]):
        var = file_variables[var_index]
        for model_files in var_files:
            for file_pair in [model_files[i:i + 2] for i in range(0, len(model_files), 2)]:
                sh_file, nh_file = file_pair  
                sh_value, nh_value, experiment, model, history = calc_hemispheric_heat(nh_file, sh_file, var, time_constraint)
                column_list = generate_heat_row_dicts(column_list, sh_value, nh_value, model, experiment, var, ylabel)
    heat_df = pandas.DataFrame(column_list)

    g = sns.catplot(x="hemisphere", y=ylabel,
                   hue="experiment", col="variable",
                   data=hemisphere_df, kind="bar",
                   palette=['0.5', 'red', 'blue'])
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

    parser.add_argument("--toa_files", type=str, nargs=6, action='append', default=[],
                        help="netTOA files in this order: hist NH, hist SH, GHG NH, GHG SH, AA NH, AA SH")                     
    parser.add_argument("--ohu_files", type=str, nargs=6, action='append', default=[],
                        help="OHU files in this order: hist NH, hist SH, GHG NH, GHG SH, AA NH, AA SH")
    parser.add_argument("--ohc_files", type=str, nargs=6, action='append', default=[],
                        help="OHC files in this order: hist NH, hist SH, GHG NH, GHG SH, AA NH, AA SH")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'),
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
