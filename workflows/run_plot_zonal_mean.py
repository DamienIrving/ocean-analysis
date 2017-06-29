"""
Filename:     run_plot_zonal_mean.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create the command line entry to run plot_zonal_mean.py
              

"""

# Import general Python modules

import sys, os, pdb
import argparse
import pandas
import glob


# Define functions

def find_files(df, run, alt_experiment, experiment, var, model, tscale, match=0, fx_physics=None, fixed=False):
    """Define the file names."""
    
    if var == 'tas':
        file_start = 'tas-global-mean'
        file_end = 'all.nc'
    else:
        file_start = var
        file_end = '.nc'

    dir_end = 'latest/fixed' if fixed else 'latest'
        
    df_selection = df.loc[(df['model'] == model) & (df['alt_experiment'] == alt_experiment)]
    df_selection = df_selection[df_selection.run.str.contains(run+'i')]

    assert df_selection.shape[0] in [0, 1, 2]
    if df_selection.shape[0] == 2:
        row_index = match
    else:
        row_index = 0

    if df_selection.shape[0] == 0:
        files = ' '
    else:
        data_dir = df_selection[var].values[row_index]
        if data_dir in ['ua6', 'r87/dbi599']:
            run = df_selection['run'].values[row_index]
            if file_start == 'tas-global-mean':
                data_dir = 'r87/dbi599'
                realm = 'atmos'
            else:
                realm = 'ocean'
            if fx_physics:
                run = 'r0i0'+fx_physics
            file_list = glob.glob('/g/data/%s/DRSv2/CMIP5/%s/%s/%s/%s/%s/%s/%s/%s_*%s' %(data_dir, model, experiment, tscale, realm, run, var, dir_end, file_start, file_end))
            files = " ".join(file_list)
        else:
            files = ' '

    return files
    

def main(inargs, basin, run):
    """Run the program."""

    command_list = ['/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python ../visualisation/plot_zonal_mean.py']
    aggregator = 'zi' if inargs.area else 'zm'
    command_list.append('/g/data/r87/dbi599/figures/%s-%s/%s-%s_Oyr_%s_piControl-historical-GHG-AA_%si1p%s_%s_clim-198601-200512_trend-all.png'  %(inargs.variable, aggregator, inargs.variable, aggregator, inargs.model, run, inargs.physics, basin))
    command_list.append(inargs.standard_name)
    command_list.append(inargs.model)
    command_list.append(run)
    command_list.append(basin)
    
    df = pandas.read_csv(inargs.data_locs)
    
    for alt_experiment in ['historical', 'historicalGHG', 'historicalAA', 'historicalnoAA', 'piControl']:
        if alt_experiment in ['historicalAA', 'historicalnoAA']:
            experiment = 'historicalMisc'
        else:
            experiment = alt_experiment
        
        if experiment == 'piControl':
            exp_run = 'r1'
        elif (experiment == 'historicalMisc') and (inargs.model == 'FGOALS-g2'):
            exp_run = 'r2' 
        else: 
            exp_run = run

        # Variable data files
        command_list.append('--' + alt_experiment.lower() + '_files')
        if inargs.variable in ['pe', 'uas', 'rsds', 'rsus', 'rlds', 'rlus', 'hfss', 'hfls']:
            if alt_experiment == 'historicalAA':
                physics = inargs.aa_physics
            elif alt_experiment == 'historicalnoAA':
                physics = inargs.noaa_physics
            elif (experiment == 'historicalGHG') and inargs.ghg_physics:
                physics = inargs.ghg_physics 
            else:
                physics = inargs.physics
            file_list = glob.glob('/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/mon/ocean/%si1p%s/%s/latest/%s_*.nc' %(inargs.model, experiment, exp_run, str(physics), inargs.variable, inargs.variable))
            files = " ".join(file_list)
        else:
            files = find_files(df, exp_run, alt_experiment, experiment, inargs.variable, inargs.model, 'mon', match=inargs.match, fixed=inargs.fixed)
        command_list.append(files)
        
        # Global mean temperature data files
        if alt_experiment != 'piControl':
            command_list.append('--' + alt_experiment.lower() + '_tas_file')
            tas_file = find_files(df, exp_run, alt_experiment, experiment, 'tas', inargs.model, 'yr', match=inargs.match)
            command_list.append(tas_file)        

        # Cell area and basin data files
        if alt_experiment == 'historicalAA' and inargs.model == 'CSIRO-Mk3-6-0':
            assert inargs.aa_physics, "Need to provie --aa_physics"
            fx_physics = 'p' + str(inargs.aa_physics)
        elif alt_experiment == 'historicalnoAA' and inargs.model == 'CSIRO-Mk3-6-0':
            assert inargs.noaa_physics, "Need to provie --noaa_physics"
            fx_physics = 'p' + str(inargs.noaa_physics)
        else:
            fx_physics = 'p0'

        if inargs.historical_fx:
            fx_alt_experiment = 'historical'
            fx_experiment = 'historical'
        else:
            fx_alt_experiment = alt_experiment
            fx_experiment = experiment

        if not inargs.exclude_area:
            area_file = find_files(df, exp_run, fx_alt_experiment, fx_experiment, 'areacello', inargs.model, 'fx', fx_physics=fx_physics)
            command_list.append('--' + alt_experiment.lower() + '_area_file')
            command_list.append(area_file)

        if not inargs.exclude_basin:
            basin_file = find_files(df, exp_run, fx_alt_experiment, fx_experiment, 'basin', inargs.model, 'fx', fx_physics=fx_physics)
            command_list.append('--' + alt_experiment.lower() + '_basin_file')
            command_list.append(basin_file)

    if inargs.legloc:
        legloc = inargs.legloc
    elif inargs.variable == 'hfds':
        legloc = 8
    elif inargs.variable == 'pe':
        legloc = 3
    elif inargs.variable in ['tauuo', 'uas']:
        legloc = 9
    else:
        legloc = 2 
    command_list.append('--legloc ' + str(legloc))

    if inargs.area:
        command_list.append('--area_adjust ')

    if (inargs.model == 'CCSM4') and (inargs.standard_name == 'surface_downward_x_stress'):
        command_list.append('--reverse_sign ')

    final_command = " ".join(command_list)
    print(final_command)
    if inargs.execute:
        os.system(final_command)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Create the command line entry to run plot_zonal_mean.py'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("data_locs", type=str, help="File detailing where the data is located at NCI")
    parser.add_argument("variable", type=str, help="Variable (e.g. hfds, tauuo)")
    parser.add_argument("standard_name", type=str, help="e.g. surface_downward_x_stress")
    parser.add_argument("model", type=str, help="Model to process")
    parser.add_argument("runs", type=str, nargs='*', help="Runs to process (e.g. r1 r2)")

    parser.add_argument("--execute", action="store_true", default=False,
                        help="Switch to have this script execute the final command rather than printing to screen")

    parser.add_argument("--exclude_basin", action="store_true", default=False,
                        help="Leave out basin files [default=False]")
    parser.add_argument("--exclude_area", action="store_true", default=False,
                        help="Leave out area files [default=False]")

    parser.add_argument("--historical_fx", action="store_true", default=False,
                        help="Use the historical areacello and basin files for GHG is AA too [default=False]")

    parser.add_argument("--legloc", type=int, default=None,
                        help="Legend location")
    parser.add_argument("--aa_physics", type=int, default=None,
                        help="Need to supply this for the P-E plot and CSIRO other plots")
    parser.add_argument("--noaa_physics", type=int, default=None,
                        help="Need to supply this for the P-E plot and CSIRO other plots")
    parser.add_argument("--ghg_physics", type=int, default=None,
                        help="Override the --physics option for historicalGHG (used for GISS-E2 models)")
    parser.add_argument("--physics", type=int, default=1,
                        help="physics")
    parser.add_argument("--match", type=int, default=0,
                        help="Pick the first (index 0) or second (index 1) match - useful for GISS models with two p runs")
    parser.add_argument("--area", action="store_true", default=False,
                        help="Add the area adjustment flag")

    parser.add_argument("--fixed", action="store_true", default=False,
                        help="Look for files in a directory labelled fixed")

    parser.add_argument("--basins", type=str, nargs='*', default=['globe'],
                        choices=('globe', 'atlantic', 'indian', 'pacific'),
                        help="Which basins to create plots for (default = globe only)")

    args = parser.parse_args()

    for basin in args.basins:
        for run in args.runs:
            main(args, basin, run)
