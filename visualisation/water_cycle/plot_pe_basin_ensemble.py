"""Plot ensemble P-E region data files for the basins"""

# Import general Python modules

import sys, os, pdb, re
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import iris
import iris.coord_categorisation
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

names = {'precipitation_minus_evaporation_flux': 'P-E',
         'precipitation_flux': 'precipitation',
         'water_evapotranspiration_flux': 'evaporation',
        }


def get_data(infile, var, time_constraint):
    """Get the data for a particular model"""
    
    cube, history = gio.combine_files(infile, var, new_calendar='365_day')
    cube = cube.extract(time_constraint)
    iris.coord_categorisation.add_year(cube, 'time')
    assert cube.shape[-1] == 8
    data_array = np.zeros([cube.shape[0], 4])
    data_array[:, 0] = cube.data[:, -1, 0]  #atlantic
    data_array[:, 1] = cube.data[:, -1, 2]  #indian
    data_array[:, 2] = cube.data[:, -1, 1]  #pacific
    data_array[:, 3] = cube.data[:, -1, 5]  #land
    
    start_data = data_array[0, :] 
    anomaly_data = data_array - start_data
    
    return cube, anomaly_data, start_data


def get_axis_label(data_var, calculated_var, units):
    """Define axis label"""

    short_name = names[data_var]
    label = f'Time-integrated {short_name} anomaly '
    if not 'cumulative' in calculated_var:
        units = '% change'

    label = label + f'({units})'

    return label


def plot_ensemble_lines(df, var, model_list, experiment, units, ylim_list):
    """Plot regional changes for each model as a line graph"""

    xvals = np.array([1, 2, 3, 4])
    fig, axes = plt.subplots(2, 2, figsize=[20, 14])
    axes = axes.flatten()    

    var_list = ['start', 'cumulative_change', 'percentage_change', 'percentage_change_anomaly']
    titles = {'start': 'starting value',
              'cumulative_change': 'Raw values',
              'percentage_change': 'Percentage change',
              'percentage_change_anomaly': 'Local % change minus global % change'} 

    for plot_num, var_name in enumerate(var_list):
        for model_num, model_name in enumerate(model_list):
            yvals = df[(df['model'] == model_name)][var_name].values
            linestyle = '-' if model_num < 10 else '--'
            axes[plot_num].plot(xvals, yvals, label=model_name, marker='o', linestyle=linestyle)
        short_name = names[var]
        ylabel = get_axis_label(var, var_name, units)
        axes[plot_num].set_ylabel(ylabel)
        axes[plot_num].set_xticks(xvals)
        axes[plot_num].set_xticklabels(['atlantic', 'indian', 'pacific', 'land'])
        axes[plot_num].set_title(titles[var_name])
        axes[plot_num].axhline(0, color='0.8')
    
    for plot_num, ymax in ylim_list:
        axes[int(plot_num)].set_ylim(-1 * ymax, ymax)
     
    plt.suptitle(f'Time-integrated anomaly, 1861-2005, {experiment} experiment')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='center left', bbox_to_anchor=(0.815, 0.5))
    plt.tight_layout(rect=(0, 0, 0.8, 1))
    fig.subplots_adjust(top=0.92)


def main(inargs):
    """Run the program."""
  
    time_constraint = gio.get_time_constraint(inargs.time_bounds)
    basin_names = ['atlantic', 'indian', 'pacific', 'land']
    anomaly_data = {}
    start_data = {}
    data = []
    model_list = []
    for filenum, infile in enumerate(inargs.infiles):
        cube, anomaly_data, start = get_data(infile, inargs.var, time_constraint)
        units = cube.units
        cum_change = anomaly_data[-1, :]
        model = cube.attributes['source_id'] if 'source_id' in cube.attributes else cube.attributes['model_id'] 
        ntimes = anomaly_data.shape[0]
        pct_change = ((cum_change / ntimes) / np.absolute(start)) * 100
        total_cum_change = cum_change.sum()
        total_start = start.sum()
        total_pct_change = ((total_cum_change / ntimes) / total_start) * 100
        pct_change_anomaly = pct_change - total_pct_change

        model_list.append(model)
        for basin in range(4):
            data.append([model, basin_names[basin], start[basin],
                         cum_change[basin], pct_change[basin], pct_change_anomaly[basin]])
    
    df = pd.DataFrame(data, columns = ['model', 'basin', 'start',
                                       'cumulative_change', 'percentage_change', 'percentage_change_anomaly'])

    model_list.sort()
    experiment = cube.attributes['experiment_id']
    plot_ensemble_lines(df, inargs.var, model_list, experiment, str(units), inargs.ymax)

    plt.savefig(inargs.outfile, bbox_inches='tight')

    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(infile_history={inargs.infiles[-1]: cube.attributes['history']}, git_repo=repo_dir)
    cmdprov.write_log(log_file, log_text)

    csv_file = re.sub('.png', '.csv', inargs.outfile)
    df.to_csv(csv_file)


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description=__doc__, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Files for a particular experiment (one file per model)")
    parser.add_argument("var", type=str, help="Variable name",
                        choices=('precipitation_minus_evaporation_flux', 'precipitation_flux',
                                 'water_evapotranspiration_flux', 'cell_area'))
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'), help="Time period [default = entire]")
    parser.add_argument("--ymax", type=float, default=[],
                        help='y axis limit')

    args = parser.parse_args()
    main(args)
