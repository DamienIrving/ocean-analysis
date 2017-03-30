"""
Filename:     run_ocean_workflow.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create the command line entry to run one of the ocean makefiles

"""

# Import general Python modules

import sys, os, pdb
import argparse
import pandas


# Define functions

def directory_tree(owner):
    """Insert owner into directory structure."""
    
    valid_owners = ['ua6', 'r87/dbi599']
    
    if owner in valid_owners:
        full_dir = "/g/data/%s/drstree/CMIP5/GCM" %(owner)
    else:
        full_dir = 'no_data'
        
    return full_dir


def add_subsurface_row_commands(df, command_list, row, variable):
    """Add row-specific commands."""
    
    command_list.append('ORIG_VARIABLE_DIR=' + directory_tree(row[variable]))
    command_list.append('ORGANISATION=' + row['organisation'])
    command_list.append('RUN=' + row['run'])
    command_list.append('ORIG_VOL_DIR=' + directory_tree(row['volcello']))  
    command_list.append('ORIG_BASIN_DIR=' + directory_tree(row['basin']))  
    command_list.append('ORIG_DEPTH_DIR=' + directory_tree(row['depth'])) 
    command_list.append('ORIG_AREAA_DIR=' + directory_tree(row['areacella']))  
    command_list.append('ORIG_AREAO_DIR=' + directory_tree(row['areacello']))  
    command_list.append('ORIG_TAS_DIR=' + directory_tree(row['tas']))
    command_list = add_subsurface_row_exceptions(df, command_list, row, variable)
    
    return command_list


def add_subsurface_row_exceptions(df, command_list, row, variable):
    """Set the subsurface makfile variables that can be weird."""
    
    fxrun = 'r0i0p0'
    if (row['model'] == 'CSIRO-Mk3-6-0') & (row['experiment'] == 'historicalMisc'):
        fx_run = 'r0io' + run['run'][-2:]

    control_run = 'r1i1p1'
    if (row['model'] == 'IPSL-CM5A-LR') & (row['run'] == 'r1i1p4'):
        control_run == 'r2i1p1'
    elif ('GISS-E2' in row['model']) & ('p3' in row['run']):
        control_run = 'r1i1p3'
        
    control_selection = df.loc[(df['model'] == row['model']) & (df['experiment'] == 'piControl') & (df['run'] == control_run)]
    assert control_selection.shape[0] == 1
    orig_control_dir = control_selection.iloc[0][variable]
    
    command_list.append('FX_RUN=' + fxrun)
    command_list.append('CONTROL_RUN=' + control_run)
    command_list.append('ORIG_CONTROL_DIR=' + directory_tree(orig_control_dir))
    
    return command_list


def run_subsurface(df, command_list, variables, models, experiments, user_runs=None, execute=False):
    """Run the subsurface_oceanmk workflow."""
    
    command_list.append('subsurface_ocean.mk')
    for variable in variables:
        for experiment in experiments:
            for model in models:
                if user_runs == None:
                    runs = df.loc[(df['model'] == model) & (df['alt_experiment'] == experiment)]['run'].values
                else:
                    runs = user_runs
                for run in runs:
                    current_command_list = command_list.copy()
    
                    if variable == 'so':
                        current_command_list.append('VAR=%s LONG_NAME=sea_water_salinity' %(variable))
                        current_command_list.append('ZM_TICK_MAX=3.5 ZM_TICK_STEP=0.5')
                        current_command_list.append('VM_TICK_MAX=10 VM_TICK_STEP=2')
                        current_command_list.append('SCALE_FACTOR=3')
                        current_command_list.append('PALETTE=BrBG_r')
                    elif variable == 'thetao':
                        current_command_list.append('LONG_NAME=sea_water_potential_temperature')
                        current_command_list.append('ZM_TICK_MAX=15 ZM_TICK_STEP=3')
                        current_command_list.append('VM_TICK_MAX=25 VM_TICK_STEP=5')
                        current_command_list.append('SCALE_FACTOR=3')
                        current_command_list.append('PALETTE=RdBu_r')

                    df_selection = df.loc[(df['model'] == model) & (df['alt_experiment'] == experiment) & (df['run'] == run)]                
                    assert df_selection.shape[0] == 1
                    row = df_selection.iloc[0]
                    current_command_list = add_subsurface_row_commands(df, current_command_list, row, variable)

                    current_command_list.append('MODEL=' + model)
                    current_command_list.append('EXPERIMENT=' + row['experiment'])

                    subsurface_command = " ".join(current_command_list)
                    if execute:
                        os.system(subsurface_command)
                    print(subsurface_command)


def main(inargs):
    """Run the program."""

    command_list = ['make']
    if inargs.dry_run:
        command_list.append('-n')
    if inargs.force:
        command_list.append('-B')
    command_list.append('-f')
    
    assert inargs.models, "Must specify which models"
    assert inargs.experiments, "Must specify which experiments"
    
    df = pandas.read_csv(inargs.data_locs)
    
    if inargs.subsurface_workflow:
        run_subsurface(df, command_list, 
                       inargs.subsurface_workflow,
                       inargs.models,
                       inargs.experiments,
                       user_runs=inargs.runs,
                       execute=inargs.execute) 


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Create the command line entry to run one of the ocean makefiles'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("data_locs", type=str, help="File detailing where the data is located at NCI")

    parser.add_argument("--subsurface_workflow", type=str, nargs='*', choices=('thetao', 'so'), default=None,
                        help="Run the subsurface ocean workflow for the listed variables")
    parser.add_argument("--surface_workflow", type=str, nargs='*', choices=('hfds', 'hfy', 'tauuo', 'tauvo', 'pe'), default=None,
                        help="Run the surface ocean workflow")
    parser.add_argument("--metric_workflow", action="store_true", default=False,
                        help="Run the metric workflow")

    parser.add_argument("--models", type=str, nargs='*', default=None,
                        help="Models to process [Must give at least one]")
    parser.add_argument("--experiments", type=str, nargs='*', default=None,
                        help="Experiments to process [Must give at least one]. Use historicalAA etc, not historicalMisc.")
    parser.add_argument("--runs", type=str, nargs='*', default=None,
                        help="Runs to process [default=all]")

    parser.add_argument("-n", "--dry_run", action="store_true", default=False,
                        help="Have the make command do a dry run")
    parser.add_argument("-B", "--force", action="store_true", default=False,
                        help="Force make (i.e. execute every command back to start of workflow")

    parser.add_argument("--execute", action="store_true", default=False,
                        help="Switch to have this script execute the make command rather than printing to screen")

    args = parser.parse_args()            
    main(args)
