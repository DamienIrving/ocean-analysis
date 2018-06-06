"""
Filename:     plot_interhemispheric_heat_difference.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ensemble interhemispheric heat difference timeseries for OHC, hfds and rndt

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import pandas
import iris
import matplotlib.pyplot as plt
import seaborn
seaborn.set_context('talk')

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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions


names = {'ohc': 'ocean heat content',
         'hfds': 'Downward Heat Flux at Sea Water Surface',
         'rndt': 'TOA Incoming Net Radiation'}


def calc_anomaly(cube):
    """Calculate the anomaly."""
    
    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    
    return anomaly


def get_simulation_attributes(cube):
    """Get model. experiment and mip information."""

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']
    physics = cube.attributes['physics_version']
    run = cube.attributes['realization']
    mip = 'r%si1p%s' %(run, physics)

    return model, experiment, mip


def generate_data_dict(diff, model, mip, variable):
    """Generate dict that will form a row of a pandas dataframe."""

    data_dict = {'model': model, 'mip': mip}
    for var in ['rndt', 'hfds', 'ohc']:
        if var == variable:
            data_dict[var] = diff
        else:
            data_dict[var] = numpy.nan
    
    return data_dict


def calc_interhemispheric_diff(nh_file, sh_file, var, time_constraint, ref_experiment):
    """Calculate the interhemispheric difference timeseries."""

    nh_name = names[var] + ' nh sum'
    nh_cube = iris.load_cube(nh_file, nh_name & time_constraint)
    nh_attributes = get_simulation_attributes(nh_cube)
    nh_anomaly = calc_anomaly(nh_cube)

    sh_name = names[var] + ' sh sum'
    sh_cube = iris.load_cube(sh_file, sh_name & time_constraint)
    sh_attributes = get_simulation_attributes(sh_cube)
    sh_anomaly = calc_anomaly(sh_cube)

    assert nh_attributes == sh_attributes
    model, experiment, mip = nh_attributes 
    if ref_experiment:
        assert experiment == ref_experiment 

    diff = nh_anomaly.data[-1] - sh_anomaly.data[-1]
 
    return diff, model, experiment, mip


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    #metadata_dict = {}
    fig, ax = plt.subplots()
    plt.axvline(x=0, color='0.5', linestyle='--')

    data_list = []
    experiment = None
    for nh_file, sh_file in inargs.rndt_files:
        diff, model, experiment, mip = calc_interhemispheric_diff(nh_file, sh_file, 'rndt', time_constraint, experiment)
        data_list.append(generate_data_dict(diff, model, mip, 'rndt'))
        
    for nh_file, sh_file in inargs.hfds_files:
        diff, model, experiment, mip = calc_interhemispheric_diff(nh_file, sh_file, 'hfds', time_constraint, experiment)
        data_list.append(generate_data_dict(diff, model, mip, 'hfds'))

    for nh_file, sh_file in inargs.ohc_files:
        diff, model, experiment, mip = calc_interhemispheric_diff(nh_file, sh_file, 'ohc', time_constraint, experiment)
        data_list.append(generate_data_dict(diff, model, mip, 'ohc'))

    data_df = pandas.DataFrame(data_list)   
    data_df.rename(columns={'rndt': 'netTOA'}, inplace=True)    
    seaborn.boxplot(data=data_df[['model', 'mip', 'netTOA', 'hfds', 'ohc']], orient="h", palette=['red', 'yellow', 'blue'])

    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0), useMathText=True)
    ax.xaxis.major.formatter._useMathText = True
    ax.set_xlabel('Northern Hemisphere minus Southern Hemisphere (Joules)')

    plt.title('Interhemispheric difference in accumulated heat, 1861-2005 (%s)' %(experiment))
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot ensemble interhemispheric heat difference timeseries for OHC, hfds and rndt'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="output file")                               
    
    parser.add_argument("--rndt_files", type=str, nargs=2, action='append', 
                        help="NH and SH integrated netTOA file, in that order (dedrifted)")
    parser.add_argument("--hfds_files", type=str, nargs=2, action='append', 
                        help="NH and SH integrated hfds file, in that order (dedrifted)")
    parser.add_argument("--ohc_files", type=str, nargs=2, action='append', 
                        help="NH and SH OHC file, in that order (dedrifted)")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=['1861-01-01', '2005-12-31'], help="Time bounds")

    args = parser.parse_args()             
    main(args)
