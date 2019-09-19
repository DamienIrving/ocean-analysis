"""
Filename:     plot_ohc_masso.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot variables relevant for the global energy and water budget  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import numpy
import matplotlib.pyplot as plt
import iris
import cmdline_provenance as cmdprov

import clef.code
db = clef.code.connect()
session = clef.code.Session()

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

import timeseries
import general_io as gio


# Define functions 

names = {'masso': 'sea_water_mass',
         'volo': 'sea_water_volume',
         'thetaoga': 'sea_water_potential_temperature'}

processed_files = []


def get_latest(results):
    """Select the latest results"""

    if results:
        latest = results[0]
        for result in results[1:]:
            current_version = result['version'][1:] if 'v' in result['version'] else result['version']
            latest_version = latest['version'][1:] if 'v' in latest['version'] else latest['version']
            if float(current_version) > float(latest_version):
                latest = result
    else:
        latest = []    

    return latest


def clef_search(model, variable, ensemble):
    """Use Clef to search for data files"""

    constraints = {'variable': variable, 'model': model, 'table': 'Omon',
                   'experiment': 'piControl', 'ensemble': ensemble}

    results = clef.code.search(session, project='cmip6', **constraints)
    results = get_latest(results)
    if results:
        filenames = results['filenames']
        filenames.sort()
        filedir = results['pdir']
        file_list = [filedir + '/' + filename for filename in filenames]
        version = results['version']
        file_version_list = [filedir + '/' + filename + ', ' + str(version) for filename in filenames]
        processed_files.append(file_version_list)
    else:
        file_list = []

    print(file_list)
    return file_list


def time_check(cube):
    """Check the time axis for annual data."""

    iris.coord_categorisation.add_year(cube, 'time')
    year_list = cube.coord('year').points        
    diffs = numpy.diff(year_list)
    if diffs.size > 0:
        assert diffs.max() == 1, "Gaps in time axis, %s" %(cube.long_name)
        assert diffs.min() == 1, "Duplicate annual values in time axis. %s" %(cube.long_name)

    return cube


def read_global_variable(model, variable, ensemble):
    """Read data for a global variable"""

    file_list = clef_search(model, variable, ensemble) 
    
    if file_list:
        cube, history = gio.combine_files(file_list, names[variable])
        cube = timeseries.convert_to_annual(cube)
        cube = time_check(cube)
    else:
        cube = None

    return cube


def get_log_text(file_list):
    """Write the metadata to file."""

    flat_list = [item for sublist in file_list for item in sublist]
    flat_list = list(set(flat_list))
    flat_list.sort()
    log_text = cmdprov.new_log(git_repo=repo_dir, extra_notes=flat_list)

    return log_text


def common_time_period(mass_cube, thetaoga_cube):
    """Get the common time period for comparison."""

    mass_years = mass_cube.coord('year').points
    mass_nyrs = len(mass_years)

    thetaoga_years = thetaoga_cube.coord('year').points
    thetaoga_nyrs = len(thetaoga_years)

    if mass_nyrs > thetaoga_nyrs:
        mass_cube = mass_cube[0:thetaoga_nyrs]
    elif mass_nyrs < thetaoga_nyrs:
        thetaoga_cube = thetaoga_cube[0:mass_nyrs]
        
    return mass_cube, thetaoga_cube
  

def main(inargs):
    """Run the program."""

    volo_models = ['CNRM-CM6-1', 'CNRM-ESM2-1', 'IPSL-CM6A-LR']
    cpocean_dict = {'HadGEM3-GC31-LL': 3991.867957, 'UKESM1-0-LL': 3991.867957}
    rhozero_dict = {'HadGEM3-GC31-LL': 1026, 'UKESM1-0-LL': 1026}

    fig = plt.figure(figsize=[14, 5])
    nrows = 1
    ncols = 2
    ax1 = fig.add_subplot(nrows, ncols, 1)
    ax2 = fig.add_subplot(nrows, ncols, 2)

    for model, run in zip(inargs.models, inargs.runs):
        if model in volo_models:
            volo = read_global_variable(model, 'volo', run)
            rhozero = 1026
            masso = volo * rhozero
        else:
            masso = read_global_variable(model, 'masso', run)

        thetaoga = read_global_variable(model, 'thetaoga', run)
        thetaoga = gio.temperature_unit_check(thetaoga, 'K')

        masso, thetaoga = common_time_period(masso, thetaoga)

        cp = cpocean_dict[model] if model in cpocean_dict.keys() else 4000
        ohc = masso.data * thetaoga.data * cp
        ohc_anomaly = ohc - ohc[0]
        masso_anomaly = masso.data - masso.data[0]

        label = '%s (%s)' %(model, run)
        ax1.plot(ohc_anomaly, color='red')
        ax2.plot(masso_anomaly, color='red', label=label)


    ax1.set_title('ocean heat content anomaly')
    ax1.set_xlabel('year')
    ax1.set_ylabel('J')
    ax1.grid(linestyle=':')
    ax1.ticklabel_format(useOffset=False)
    ax1.yaxis.major.formatter._useMathText = True

    ax2.set_title('ocean mass anomaly')
    ax2.set_xlabel('year')
    ax2.set_ylabel('kg')
    ax2.grid(linestyle=':')
    ax2.ticklabel_format(useOffset=False)
    ax2.yaxis.major.formatter._useMathText = True
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(inargs.outfile, bbox_inches='tight')  # dpi=400
    log_text = get_log_text(processed_files)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot OHC and masso timeseries'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, default=None, help="Output file name")

    parser.add_argument("--models", type=str, nargs='*', required=True, help="Models to plot")
    parser.add_argument("--runs", type=str, nargs='*', required=True, help="Run (e.g. r1i1p1)")

    parser.add_argument("--manual_files", type=str, action="append", nargs='*', default=[],
                        help="Use these manually entered files instead of the clef search")    

    args = parser.parse_args()  
    assert len(args.models) == len(args.runs)           
    main(args)
