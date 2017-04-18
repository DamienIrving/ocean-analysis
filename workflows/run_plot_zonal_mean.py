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

def find_files(df, run, alt_experiment, experiment, var, model, tscale, match=0, fx_physics=None):
    """Define the file names."""
    
    if var == 'tas':
        file_start = 'tas-global-mean'
        end = 'all.nc'
    else:
        file_start = var
        end = '.nc'

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
            file_list = glob.glob('/g/data/%s/DRSv2/CMIP5/%s/%s/%s/%s/%s/%s/latest/%s_*%s' %(data_dir, model, experiment, tscale, realm, run, var, file_start, end))
            files = " ".join(file_list)
        else:
            files = ' '

    return files
    

def main(inargs, run):
    """Run the program."""

    command_list = ['python ../visualisation/plot_zonal_mean.py']
    aggregator = 'zi' if inargs.area else 'zm'
    command_list.append('/g/data/r87/dbi599/figures/%s-%s/%s-%s_Oyr_%s_piControl-historical-GHG-AA_%s_198601-200512.png'  %(inargs.variable, aggregator, inargs.variable, aggregator, inargs.model, run))
    command_list.append(inargs.standard_name)
    command_list.append(inargs.model)
    command_list.append(run)
    
    df = pandas.read_csv(inargs.data_locs)
    
    for alt_experiment in ['historical', 'historicalGHG', 'historicalAA', 'historicalnoAA', 'piControl']:
        if alt_experiment in ['historicalAA', 'historicalnoAA']:
            experiment = 'historicalMisc'
        else:
            experiment = alt_experiment

        exp_run = 'r1' if (experiment == 'piControl') else run

        # Variable data files
        command_list.append('--' + alt_experiment.lower() + '_files')
        if inargs.variable == 'pe':
            if alt_experiment == 'historicalAA':
                physics = inargs.aa_physics
            elif alt_experiment == 'historicalnoAA':
                physics = inargs.noaa_physics
            else:
                physics = 1
            file_list = glob.glob('/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/mon/atmos/%si1p%s/pe/latest/pe_*.nc' %(inargs.model, experiment, exp_run, str(physics)))
            files = " ".join(file_list)
        else:
            files = find_files(df, exp_run, alt_experiment, experiment, inargs.variable, inargs.model, 'mon', match=inargs.match)
        command_list.append(files)
        
        # Global mean temperature data files
        if alt_experiment != 'piControl':
            command_list.append('--' + alt_experiment.lower() + '_tas_file')
            tas_file = find_files(df, exp_run, alt_experiment, experiment, 'tas', inargs.model, 'yr', match=inargs.match)
            command_list.append(tas_file)        

        # Cell area data files
        command_list.append('--' + alt_experiment.lower() + '_area_file')
        if alt_experiment == 'historicalAA' and inargs.model == 'CSIRO-Mk3-6-0':
            fx_physics = 'p' + str(inargs.aa_physics)
        elif alt_experiment == 'historicalnoAA' and inargs.model == 'CSIRO-Mk3-6-0':
            fx_physics = 'p' + str(inargs.noaa_physics)
        else:
            fx_physics = 'p0'
        area_file = find_files(df, exp_run, alt_experiment, experiment, 'areacello', inargs.model, 'fx', fx_physics=fx_physics)
        command_list.append(area_file)        

    if inargs.legloc:
        legloc = inargs.legloc
    elif inargs.variable == 'hfds':
        legloc = 8
    elif inargs.variable == 'pe':
        legloc = 2
    elif inargs.variable == 'tauuo':
        legloc = 9
    else:
        legloc = 2 
    command_list.append('--legloc ' + str(legloc))

    if inargs.area:
        command_list.append('--area_adjust ')

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
                        help="Switch to have this script execute the make command rather than printing to screen")

    parser.add_argument("--legloc", type=int, default=8,
                        help="Legend location")
    parser.add_argument("--aa_physics", type=int, default=None,
                        help="Need to supply this for the P-E plot and CSIRO other plots")
    parser.add_argument("--noaa_physics", type=int, default=None,
                        help="Need to supply this for the P-E plot and CSIRO other plots")
    parser.add_argument("--match", type=int, default=0,
                        help="Pick the first (index 0) or second (index 1) match - useful for GISS models with two p runs")
    parser.add_argument("--area", action="store_true", default=False,
                        help="Add the area adjustment flag")

    args = parser.parse_args()
    for run in args.runs:
        main(args, run)
