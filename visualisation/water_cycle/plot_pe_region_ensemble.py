"""Plot ensemble data for the five P-E regions"""

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
         'cell_area': 'area'}


def get_scaling_data(infile, var, data_model, data_units):
    """Get the scaling data for a particular model"""
    
    cube, history = gio.combine_files(infile, var, new_calendar='365_day')
    scaling_model = cube.attributes['source_id'] if 'source_id' in cube.attributes else cube.attributes['model_id']
    assert data_model == scaling_model
    scale_data = cube.data[0, 0:-1, -1]
    units = data_units * cube.units 
    
    return scale_data, units


def get_data(infile, var, time_constraint):
    """Get the data for a particular model"""
    
    cube, history = gio.combine_files(infile, var, new_calendar='365_day')
    cube = cube.extract(time_constraint)
    iris.coord_categorisation.add_year(cube, 'time')
    start_data = cube.data[0, 0:-1, -1] 
    anomaly_data = cube.data[:, 0:-1, -1] - start_data
    
    return cube, anomaly_data, start_data


def get_axis_label(data_var, calculated_var, scaling_var, units):
    """Define axis label"""

    short_name = names[data_var]
    label = f'Time-integrated {short_name} anomaly '
    if not 'cumulative' in calculated_var:
        units = '% change'

    if scaling_var:
        scale_name = names[scaling_var]
        label = label + f'times mean {scale_name} '

    label = label + f'({units})'

    return label


def plot_ensemble_lines(df, var, model_list, experiment, units, scaling_var, ylim_list,
                        evap_sign_switch=False):
    """Plot regional changes for each model as a line graph"""

    xvals = np.array([1, 2, 3, 4, 5])
    fig, axes = plt.subplots(1, 3, figsize=[30, 7])
    axes = axes.flatten()    

    var_list = ['cumulative_change', 'percentage_change', 'percentage_change_anomaly']
    titles = {'cumulative_change': 'Raw values',
              'percentage_change': 'Percentage change',
              'percentage_change_anomaly': 'Local % change minus global % change'} 

    for plot_num, var_name in enumerate(var_list):
        for model_num, model_name in enumerate(model_list):
            yvals = df[(df['model'] == model_name)][var_name].values[1:]
            if evap_sign_switch:
                yvals = yvals * np.array([1, -1, 1, -1, 1])
            linestyle = '-' if model_num < 10 else '--'
            axes[plot_num].plot(xvals, yvals, label=model_name, marker='o', linestyle=linestyle)
        short_name = names[var]
        ylabel = get_axis_label(var, var_name, scaling_var, units)
        axes[plot_num].set_ylabel(ylabel)
        axes[plot_num].set_xticks(xvals)
        axes[plot_num].set_xticklabels(['SH precip', 'SH evap', 'trop precip', 'NH evap', 'NH precip'])
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
    region_names = ['SH precip', 'SH evap', 'tropical precip', 'NH evap', 'NH precip']
    anomaly_data = {}
    start_data = {}
    data = []
    model_list = []
    for filenum, infile in enumerate(inargs.infiles):
        cube, anomaly_data, start = get_data(infile, inargs.var, time_constraint)
        units = cube.units
        cum_change = anomaly_data[-1, :]
        model = cube.attributes['source_id'] if 'source_id' in cube.attributes else cube.attributes['model_id']
        if inargs.scaling_files:
            scale_file = inargs.scaling_files[filenum]
            scale_factor, units = get_scaling_data(scale_file, inargs.scaling_var, model, units)
            cum_change = cum_change * scale_factor
            start = start * scale_factor  
        ntimes = anomaly_data.shape[0]
        pct_change = ((cum_change / ntimes) / np.absolute(start)) * 100
        if inargs.var == 'precipitation_minus_evaporation_flux':
            total_cum_change = np.sum(cum_change * np.array([1, -1, 1, -1, 1]))
            total_start = np.sum(start * np.array([1, -1, 1, -1, 1]))
            total_pct_change = ((total_cum_change / ntimes) / total_start) * 100
            pct_change_anomaly = pct_change - (total_pct_change * np.array([1, -1, 1, -1, 1]))
        else:
            total_cum_change = cum_change.sum()
            total_start = start.sum()
            total_pct_change = ((total_cum_change / ntimes) / total_start) * 100
            pct_change_anomaly = pct_change - total_pct_change

        model_list.append(model)
        data.append([model, 'globe precip', total_start,
                     total_cum_change, total_pct_change, None])
        for region in range(5):
            data.append([model, region_names[region], start[region],
                         cum_change[region], pct_change[region], pct_change_anomaly[region]])
    
    df = pd.DataFrame(data, columns = ['model', 'region', 'start',
                                       'cumulative_change', 'percentage_change', 'percentage_change_anomaly'])

    model_list.sort()
    experiment = cube.attributes['experiment_id']
    plot_ensemble_lines(df, inargs.var, model_list, experiment, str(units),
                        inargs.scaling_var, inargs.ymax, evap_sign_switch=inargs.evap_sign_switch)

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

    parser.add_argument("--scaling_files", type=str, nargs='*', default=None,
                        help="File for scaling the input data (one file per model)")
    parser.add_argument("--scaling_var", type=str, default=None,
                        help="Variable for scaling the input data")
    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'), help="Time period [default = entire]")
    parser.add_argument("--ymax", type=float, nargs=2, action='append', metavar=('PLOTNUM', 'YMAX'), default=[],
                        help='y axis limit (give plot number)')
    parser.add_argument("--evap_sign_switch", action="store_true", default=False,
                        help="Multiply the evap region values by -1")

    args = parser.parse_args()
    if args.scaling_files:
        assert len(args.infiles) == len(args.scaling_files)

    main(args)
