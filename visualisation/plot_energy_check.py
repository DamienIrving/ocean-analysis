"""
Filename:     plot_energy_check.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ohc, hfds and rndt

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
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
    import timeseries
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def calc_anomaly(cube):
    """Calculate the anomaly."""
    
    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    
    return anomaly


def get_title(cube):
    """Get the plot title."""

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']
    physics = cube.attributes['physics_version']
    run = cube.attributes['realization']
    mip = 'r%si1p%s' %(run, physics)

    title = '%s, %s (%s)'  %(model, experiment, mip)
    
    if experiment == 'historicalMisc':
        legloc = 3
    else:
        legloc = 2

    return title, legloc


def get_hfds_label(filename):
    """Get the hfds legend label"""

    if 'inferred' in filename:
        label = 'ocean surface heat flux (inferred), cumulative sum'
    else:
        label = 'ocean surface heat flux, cumulative sum'

    return label


def plot_files(ohc_file, hfds_file, rndt_file, metadata_dict, time_constraint, dedrifted=True):
    """ """

    ohc_cube = iris.load_cube(ohc_file, 'ocean heat content globe sum' & time_constraint)
    metadata_dict[ohc_file] = ohc_cube.attributes['history']

    hfds_cube = iris.load_cube(hfds_file, 'Downward Heat Flux at Sea Water Surface globe sum' & time_constraint)
    metadata_dict[hfds_file] = hfds_cube.attributes['history']

    rndt_cube = iris.load_cube(rndt_file, 'TOA Incoming Net Radiation globe sum' & time_constraint)
    metadata_dict[rndt_file] = rndt_cube.attributes['history']
        
    ohc_anomaly = calc_anomaly(ohc_cube)
    hfds_anomaly = calc_anomaly(hfds_cube)
    rndt_anomaly = calc_anomaly(rndt_cube)

    hfds_label = get_hfds_label(hfds_file)
    if dedrifted:
        iplt.plot(ohc_anomaly, label='ocean heat content', color='blue')
        iplt.plot(hfds_anomaly, label=hfds_label, color='orange')
        iplt.plot(rndt_anomaly, label='TOA net radiation, cumulative sum', color='red')
    else:
        iplt.plot(ohc_anomaly, color='blue', linestyle='--')
        iplt.plot(hfds_anomaly, color='orange', linestyle='--')
        iplt.plot(rndt_anomaly, color='red', linestyle='--')

    return metadata_dict, ohc_cube


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    metadata_dict = {}
    fig, ax = plt.subplots()

    metadata_dict, ohc_cube = plot_files(inargs.ohc_file, inargs.hfds_file, inargs.rndt_file,
                                         metadata_dict, time_constraint, dedrifted=True)
    if inargs.orig_ohc_file and inargs.orig_hfds_file and inargs.orig_rndt_file:
        metadata_dict, ohc_cube = plot_files(inargs.orig_ohc_file, inargs.orig_hfds_file, inargs.orig_rndt_file,
                                             metadata_dict, time_constraint, dedrifted=False)

    plt.ylabel(ohc_cube.units)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    ax.yaxis.major.formatter._useMathText = True

    #plt.ylim(-1e+24, 1e+24)
    ymin, ymax = plt.ylim()
    print('ymin:', ymin)
    print('ymax:', ymax)

    title, legloc = get_title(ohc_cube)
    plt.title(title)
    plt.legend(loc=legloc)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot ensemble timeseries'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("ohc_file", type=str, help="globally integrated OHC file (dedrifted)")
    parser.add_argument("hfds_file", type=str, help="globally integrated ocean surface downward heat flux file (dedrifted)")   
    parser.add_argument("rndt_file", type=str, help="globally integrated TOA net flux file (dedrifted)")    
    parser.add_argument("outfile", type=str, help="output file")                               
    
    parser.add_argument("--orig_ohc_file", type=str, default=None,
                        help="globally integrated OHC file (original, non-dedrifted)")
    parser.add_argument("--orig_hfds_file", type=str, default=None,
                        help="globally integrated ocean surface downward heat flux file (original, non-dedrifted)")   
    parser.add_argument("--orig_rndt_file", type=str, default=None,
                        help="globally integrated TOA net flux file (original, non-dedrifted)")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=None, help="Time bounds")

    args = parser.parse_args()             
    main(args)
