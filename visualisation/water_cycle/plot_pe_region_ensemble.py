"""
Filename:     plot_pe_region_ensemble.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot output from calc_pe_zonal_sum_regional_totals.py or calc_pe_spatial_totals.py
"""

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


def get_data(infile, var, time_constraint):
    """Get the data for a particular model"""
    
    cube, history = gio.combine_files([infile], var, new_calendar='365_day')
    cube = cube.extract(time_constraint)
    iris.coord_categorisation.add_year(cube, 'time')
    start_data = cube.data[0, 0:-1, -1] 
    anomaly_data = cube.data[:, 0:-1, -1] - start_data
    
    return cube, anomaly_data, start_data


def plot_ensemble_lines(df, var, model_list, experiment):
    """Plot regional changes for each model as a line graph"""

    xvals = np.array([1, 2, 3, 4, 5])
    fig, axes = plt.subplots(2, 2, figsize=[18, 12])
    axes = axes.flatten()    

    var_list = ['cumulative_change_sign_fix', 'percentage_change',
                'cumulative_change_anomaly', 'percentage_change_anomaly']
    titles = {'cumulative_change_sign_fix': 'Raw values',
              'percentage_change': 'Raw values (percentage change)',
              'cumulative_change_anomaly': 'Spatial anomaly (i.e. global mean subtracted)',
              'percentage_change_anomaly': 'Spatial anomaly (local % change minus global % change)'} 

    for plot_num, var_name in enumerate(var_list):
        for model_num, model_name in enumerate(model_list):
            yvals = df[(df['model'] == model_name)][var_name].values[1:]
            linestyle = '-' if model_num < 10 else '--'
            axes[plot_num].plot(xvals, yvals, label=model_name, marker='o', linestyle=linestyle)
        short_name = names[var]
        ylabel = f'Accumulated {short_name} anomaly (kg)' if 'cumulative' in var_name else f'Change in {short_name} (%)'
        axes[plot_num].set_ylabel(ylabel)
        axes[plot_num].set_xticks(xvals)
        axes[plot_num].set_xticklabels(['SH precip', 'SH evap', 'trop precip', 'NH evap', 'NH precip'])
        axes[plot_num].set_title(titles[var_name])
        axes[plot_num].axhline(0, color='0.8')
    
    #axes[plot_num].set_ylim(lower_ylim, upper_ylim)
     
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
    for infile in inargs.infiles:
        cube, anomaly_data, start = get_data(infile, inargs.var, time_constraint)
        model = cube.attributes['source_id'] if 'source_id' in cube.attributes else cube.attributes['model_id']
        cum_change = anomaly_data[-1, :]
        ntimes = anomaly_data.shape[0]
        pct_change = ((cum_change / ntimes) / start) * 100
        if inargs.var == 'precipitation_minus_evaporation_flux':
            mean_cum_change = cum_change[0::2].mean()
            total_cum_change = cum_change[0::2].sum()
            total_start = start[0::2].sum()
            cum_change_anomaly = (cum_change * np.array([1, -1, 1, -1, 1])) - mean_cum_change
        else:
            mean_cum_change = cum_change.mean()
            total_cum_change = cum_change.sum()
            total_start = start.sum()
            cum_change_anomaly = cum_change - mean_cum_change

        total_pct_change = ((total_cum_change / ntimes) / total_start) * 100
        pct_change_anomaly = pct_change - total_pct_change

        model_list.append(model)
        data.append([model, 'globe precip', total_start,
                     total_cum_change, None, total_pct_change, None])
        for region in range(5):
            data.append([model, region_names[region], start[region],
                         cum_change[region], cum_change_anomaly[region],
                         pct_change[region], pct_change_anomaly[region]])
    
    df = pd.DataFrame(data, columns = ['model', 'region', 'start',
                                       'cumulative_change', 'cumulative_change_anomaly',
                                       'percentage_change', 'percentage_change_anomaly'])

    if inargs.var == 'precipitation_minus_evaporation_flux':
        df['cumulative_change_sign_fix'] = df['cumulative_change'].where((df['region'] == 'SH precip') | \
                                          (df['region'] == 'tropical precip') | (df['region'] == 'NH precip') | \
                                          (df['region'] == 'globe precip'), df['cumulative_change'] * -1)
    else:
        df['cumulative_change_sign_fix'] = df['cumulative_change']

    model_list.sort()
    experiment = cube.attributes['experiment_id']
    plot_ensemble_lines(df, inargs.var, model_list, experiment)

    plt.savefig(inargs.outfile, bbox_inches='tight')

    log_file = re.sub('.png', '.met', inargs.outfile)
    log_text = cmdprov.new_log(infile_history={inargs.infiles[-1]: cube.attributes['history']}, git_repo=repo_dir)
    cmdprov.write_log(log_file, log_text)

    csv_file = re.sub('.png', '.csv', inargs.outfile)
    df.to_csv(csv_file)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

example:
    python plot_pe_region_ensemble.py
    /g/data/r87/dbi599/CMIP*/CMIP/*/*/historical/*/Ayr/pe/*/*/pe-region-sum-anomaly_Ayr_*cumsum.nc
    /g/data/r87/dbi599/figures/water-cycle/pe-region-sum-anomaly_Ayr_ensemble_historical_r1_gn_1861-2005-cumsum.png 

"""

    description = 'Plot ensemble data for the five P-E regions'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="files for a particular experiment")
    parser.add_argument("var", type=str, help="Variable name",
                        choices=('precipitation_minus_evaporation_flux', 'precipitation_flux',
                                 'water_evapotranspiration_flux', 'cell_area'))
    parser.add_argument("outfile", type=str, help="Output file")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'), help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
