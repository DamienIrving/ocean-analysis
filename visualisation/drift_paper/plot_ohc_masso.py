"""
Filename:     plot_ohc_masso.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot time series relevant for the global energy and water budget  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse
import yaml
import glob

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
import convenient_universal as uconv

# Define functions 

names = {'masso': 'sea_water_mass',
         'volo': 'sea_water_volume',
         'thetaoga': 'sea_water_potential_temperature',
         'massa': 'atmosphere_mass_content_of_water_vapor'}

extra_log = []


def dedrift_data(data, fit='linear'):
    """Remove drift and plot."""
    
    assert fit in ['linear', 'cubic']
    deg = 3 if fit == 'cubic' else 1
    
    time_axis = numpy.arange(len(data))
    coefficients = timeseries.fit_polynomial(data, time_axis, deg, None)
    drift = numpy.polyval(coefficients, time_axis)
    dedrifted_data = data - drift

    return dedrifted_data


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


def file_match(file_dict, target_model, target_variable, target_ensemble):
    """Find matching file in list of files."""

    key = '%s_%s_%s'  %(target_model, target_ensemble, target_variable)
    match = file_dict.get(key, None)
    files = glob.glob(match) if match else None
    
    return files


def read_global_variable(model, variable, ensemble, manual_files):
    """Read data for a global variable"""

    manual = file_match(manual_files, model, variable, ensemble)
    if manual or variable == 'massa':
        file_list = manual
    else:
        file_list = clef_search(model, variable, ensemble) 

    if file_list:
        cube, history = gio.combine_files(file_list, names[variable])
        cube = timeseries.convert_to_annual(cube)
        cube = time_check(cube)
        extra_log.append(file_list)
    else:
        cube = None

    return cube


def get_log_text(extra_log):
    """Write the metadata to file."""

    flat_list = [item for sublist in extra_log for item in sublist]
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
  

def plot_reference_eei(ax, eei, max_time):
    """Plot a reference line corresponding to particular planetary energy imbalance (in W m-2)."""

    global_surface_area = 5.1e14 #m2
    sec_in_year = 365.25 * 24 * 60 * 60

    joules_per_year = eei * global_surface_area * sec_in_year
    ref_eei_timeseries = joules_per_year * numpy.arange(max_time)

    ymin, ymax = ax.get_ylim()
    ax.plot(ref_eei_timeseries, color='black', linestyle=':', linewidth=0.25)
    ax.set_ylim(ymin, ymax)


def plot_reference_mass(ax, sea_level_trend, max_time):
    """Plot a reference line corresponding to particular rate of sea level rise (in m/year).

    For reference from Cazenave et al (2018) https://www.earth-syst-sci-data.net/10/1551/2018/
    - Sea level rise since 2005 is 3.1 mm/year, 42% of which is steric
      (i.e. 0.0018 m/year is barystatic) 

    """

    ocean_area = 3.611e14 #m2
    density = 1027 # kg/m3

    kg_per_year = sea_level_trend * ocean_area * density
    ref_mass_timeseries = kg_per_year * numpy.arange(max_time)

    ymin, ymax = ax.get_ylim()
    ax.plot(ref_mass_timeseries, color='black', linestyle=':', linewidth=0.25)
    ax.set_ylim(ymin, ymax)


def record_trend(data, label, units):
    """Print the linear trend to the screen"""

    time_axis = numpy.arange(len(data))
    trend = timeseries.linear_trend(data, time_axis, None)
    extra_log.append(['%s: %f %s' %(label, trend, units)])


def main(inargs):
    """Run the program."""

    volo_models = ['CNRM-CM6-1', 'CNRM-ESM2-1', 'E3SM-1-0', 'E3SM-1-1', 'EC-Earth3', 'EC-Earth3-Veg', 'IPSL-CM6A-LR']
    cpocean_dict = {'HadGEM3-GC31-LL': 3991.867957, 'UKESM1-0-LL': 3991.867957}
    rhozero_dict = {'HadGEM3-GC31-LL': 1026, 'UKESM1-0-LL': 1026}
    if inargs.colors:
        colors = iter(inargs.colors)
    else:
        colors=iter(plt.cm.rainbow(numpy.linspace(0, 1, len(inargs.models))))

    if inargs.linestyles:
        styles = iter(inargs.linestyles)
    else:
        styles = iter(['-', '--', ':', '-', '--', ':', '-', '--', ':', '-', '--', ':', '-', '--', ':'])

    if inargs.manual_files:
        with open(inargs.manual_files, 'r') as reader:
            manual_files = yaml.load(reader)
    else:
        manual_files = {}

    fig = plt.figure(figsize=[14, 8])
    nrows = 2
    ncols = 2
    ax_ohc = fig.add_subplot(nrows, ncols, 1)
    ax_ohcd = fig.add_subplot(nrows, ncols, 2)
    ax_masso = fig.add_subplot(nrows, ncols, 3)
    ax_massod = fig.add_subplot(nrows, ncols, 4)
    #ax_massa = fig.add_subplot(nrows, ncols, 5)
    #ax_massad = fig.add_subplot(nrows, ncols, 6)

    max_time = 0
    count = 0
    for model, run in zip(inargs.models, inargs.runs):
        print(model, run)
        extra_log.append(['# ' + model + ', ' + run])
        
        # OHC and masso
        if model in volo_models:
            volo = read_global_variable(model, 'volo', run, manual_files)
            rhozero = 1026
            masso = volo * rhozero
        else:
            masso = read_global_variable(model, 'masso', run, manual_files)
       
        thetaoga = read_global_variable(model, 'thetaoga', run, manual_files)
        thetaoga = gio.temperature_unit_check(thetaoga, 'K')

        masso, thetaoga = common_time_period(masso, thetaoga)

        cp = cpocean_dict[model] if model in cpocean_dict.keys() else 4000
        ohc = masso.data * thetaoga.data * cp
        if inargs.ohc_outlier:
            ohc, outlier_idx = timeseries.outlier_removal(ohc, inargs.ohc_outlier)
            if outlier_idx:
                print('%s (%s) outliers:' %(model, run), outlier_idx)

        if inargs.runmean_window:
            ohc = timeseries.runmean(ohc, inargs.runmean_window)
            masso = timeseries.runmean(masso.data, inargs.runmean_window)

        ohc_anomaly = ohc - ohc[0]
        masso_anomaly = masso - masso[0]
        
        ohc_dedrifted = dedrift_data(ohc_anomaly)
        masso_dedrifted = dedrift_data(masso_anomaly)
        ohc_dedrifted_anomaly = ohc_dedrifted - ohc_dedrifted[0]
        masso_dedrifted_anomaly = masso_dedrifted - masso_dedrifted[0]

        label = model   #'%s (%s)' %(model, run)
        color = next(colors)
        style = next(styles)
        
        ax_ohc.plot(ohc_anomaly, color=color, label=label, linestyle=style)
        record_trend(ohc_anomaly, 'OHC linear trend', 'C/yr')
        ax_ohcd.plot(ohc_dedrifted_anomaly, color=color, label=label, linestyle=style)

        ax_masso.plot(masso_anomaly, color=color, label=label, linestyle=style)
        record_trend(masso_anomaly, 'Mass linear trend', 'kg/yr')
        ax_massod.plot(masso_dedrifted_anomaly, color=color, label=label, linestyle=style)

        if len(ohc) > max_time:
            max_time = len(ohc)

        # massa
        #massa = read_global_variable(model, 'massa', run, manual_files)
        #if inargs.runmean_window:
        #    massa = timeseries.runmean(massa.data, inargs.runmean_window)
        #massa_anomaly = massa - massa[0]
        #massa_dedrifted = dedrift_data(massa_anomaly)
        #massa_dedrifted_anomaly = massa_dedrifted - massa_dedrifted[0]
        #ax_massa.plot(massa_anomaly, color=color, label=label, linestyle=style)
        #record_trend(massa_anomaly, 'Atmospheric water mass linear trend', 'kg/yr')
        #ax_massad.plot(massa_dedrifted_anomaly, color=color, label=label, linestyle=style)

    ax_ohc.plot()

    ax_ohc.set_title('(a) OHC')
    ax_ohc.set_ylabel('OHC anomaly (J)')
    ax_ohc.grid(linestyle=':')
    ax_ohc.ticklabel_format(useOffset=False)
    ax_ohc.yaxis.major.formatter._useMathText = True
    plot_reference_eei(ax_ohc, 0.4, max_time)
    plot_reference_eei(ax_ohc, 0.2, max_time)
    plot_reference_eei(ax_ohc, 0.1, max_time)
    plot_reference_eei(ax_ohc, -0.4, max_time)
    plot_reference_eei(ax_ohc, -0.2, max_time)
    plot_reference_eei(ax_ohc, -0.1, max_time)

    ax_ohcd.set_title('(b) OHC (linear trend removed)')
    ax_ohcd.set_ylabel('OHC anomaly (J)')
    ax_ohcd.grid(linestyle=':')
    ax_ohcd.ticklabel_format(useOffset=False)
    ax_ohcd.yaxis.major.formatter._useMathText = True

    ax_masso.set_title('(c) ocean mass')
    ax_masso.set_xlabel('year')
    ax_masso.set_ylabel('ocean mass anomaly (kg)')
    ax_masso.grid(linestyle=':')
    ax_masso.ticklabel_format(useOffset=False)
    ax_masso.yaxis.major.formatter._useMathText = True
    plot_reference_mass(ax_masso, 0.0018, max_time)
    plot_reference_mass(ax_masso, 0.0009, max_time)
    plot_reference_mass(ax_masso, 0.00045, max_time)
    plot_reference_mass(ax_masso, -0.0018, max_time)
    plot_reference_mass(ax_masso, -0.0009, max_time)
    plot_reference_mass(ax_masso, -0.00045, max_time)

    ax_massod.set_title('(d) ocean mass (linear trend removed)')
    ax_massod.set_xlabel('year')
    ax_massod.set_ylabel('ocean mass anomaly (kg)')
    ax_massod.grid(linestyle=':')
    ax_massod.ticklabel_format(useOffset=False)
    ax_massod.yaxis.major.formatter._useMathText = True
    ax_massod.legend(loc='center left', bbox_to_anchor=(1, 1))

    #ax_massa.set_title('(e) atmos water mass')
    #ax_massa.set_xlabel('year')
    #ax_massa.set_ylabel('kg')
    #ax_massa.grid(linestyle=':')
    #ax_massa.ticklabel_format(useOffset=False)
    #ax_massa.yaxis.major.formatter._useMathText = True

    #ax_massad.set_title('(f) atmos water mass (linear trend removed)')
    #ax_massad.set_xlabel('year')
    #ax_massad.set_ylabel('kg')
    #ax_massad.grid(linestyle=':')
    #ax_massad.ticklabel_format(useOffset=False)
    #ax_massad.yaxis.major.formatter._useMathText = True

    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    log_text = get_log_text(extra_log)
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

    parser.add_argument("--linestyles", type=str, nargs='*', help="Line styles",
                        choices=('solid', 'dashed', 'dashdot', 'dotted'))
    parser.add_argument("--colors", type=str, nargs='*', help="colors",
                        choices=('tab:blue', 'tab:orange', 'tab:green', 'tab:red',
                                 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
                                 'tab:olive', 'tab:cyan', 'black'))
    parser.add_argument("--ohc_outlier", type=float, default=None,
                        help="threshold for an OHC outlier (e.g. 1e24")  
    parser.add_argument("--runmean_window", type=int, default=None,
                        help="window for running mean") 
    parser.add_argument("--manual_files", type=str, default=None,
                        help="YAML file with manually entered files instead of the clef search. Keys: model_ripf_var")    
    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()  
    assert len(args.models) == len(args.runs)
    if args.linestyles:
        assert len(args.models) == len(args.linestyles)
    if args.colors:
        assert len(args.models) == len(args.colors)
           
    main(args)
