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

def find_files(df, inargs, alt_experiment, experiment, tas=False):
    """Define the file names."""
    
    if tas:
        var = 'tas'
        file_start = 'tas-global-mean'
    else:
        var = inargs.variable
        file_start = var
    
    df_selection = df.loc[(df['model'] == inargs.model) & (df['alt_experiment'] == alt_experiment)]

    if experiment == 'piControl':
        df_selection = df_selection[df_selection.run.str.contains('r1i1')]
        
    else:
        df_selection = df_selection[df_selection.run.str.contains(inargs.run+'i1')]
    
    assert df_selection.shape[0] in [0, 1]
    if df_selection.shape[0] == 0:
        files = ' '
    else:
        data_dir = df_selection[var].values[0]
        if data_dir in ['ua6', 'r87/dbi59']:
            run = df_selection['run'].values[0]
            if file_start == 'tas-global-mean':
                data_dir = 'r87/dbi599'
                tscale = 'yr'
                realm = 'atmos'
            else:
                tscale = 'mon'
                realm = 'ocean'
            file_list = glob.glob('/g/data/%s/DRSv2/CMIP5/%s/%s/%s/%s/%s/%s/latest/%s_*.nc' %(data_dir, inargs.model, experiment, tscale, realm, run, var, file_start))
            files = " ".join(file_list)
        else:
            files = ' '

    return files
    

def main(inargs):
    """Run the program."""

    command_list = ['python ../visualisation/plot_zonal_mean.py']
    command_list.append('/g/data/r87/dbi599/figures/%s-zm/%s-zm_Oyr_%s_piControl-historical-GHG-AA_%s_198601-200512.png'  %(inargs.variable, inargs.variable, inargs.model, inargs.run))
    command_list.append(inargs.standard_name)
    command_list.append(inargs.model)
    command_list.append(inargs.run)
    
    df = pandas.read_csv(inargs.data_locs)
    
    for alt_experiment in ['historical', 'historicalGHG', 'historicalAA', 'piControl']:
        if alt_experiment == 'historicalAA':
            experiment = 'historicalMisc'
        else:
            experiment = alt_experiment

        command_list.append('--' + alt_experiment.lower() + '_files')
        files = find_files(df, inargs, alt_experiment, experiment, tas=False)
        command_list.append(files)
        
        if alt_experiment != 'piControl':
            command_list.append('--' + alt_experiment.lower() + '_tas_file')
            tas_file = find_files(df, inargs, alt_experiment, experiment, tas=True)
            command_list.append(tas_file)        

    command_list.append('--legloc ' + str(inargs.legloc))
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
    parser.add_argument("run", type=str, help="Run to process (e.g. r1)")

    parser.add_argument("--execute", action="store_true", default=False,
                        help="Switch to have this script execute the make command rather than printing to screen")

    parser.add_argument("--legloc", type=int, default=8,
                        help="Legend location")
    args = parser.parse_args()            
    main(args)
