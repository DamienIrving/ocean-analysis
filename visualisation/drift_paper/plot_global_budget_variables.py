"""
Filename:     plot_global_budget_variables.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot variables relevant for the global energy and water budget  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse
import itertools

import numpy
from matplotlib import gridspec
import matplotlib.pyplot as plt
import statsmodels.api as sm
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

processing_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(processing_dir)

import timeseries
import general_io as gio
import convenient_universal as uconv
import spatial_weights

import matplotlib as mpl
mpl.rcParams['axes.labelsize'] = 'large'
mpl.rcParams['axes.titlesize'] = 'x-large'
mpl.rcParams['xtick.labelsize'] = 'medium'
mpl.rcParams['ytick.labelsize'] = 'medium'
mpl.rcParams['legend.fontsize'] = 'large'


# Define functions 

processed_files = []
numbers_out_list = []

names = {'masso': 'sea_water_mass',
         'volo': 'sea_water_volume',
         'thetaoga': 'sea_water_potential_temperature',
         'soga': 'sea_water_salinity',
         'zosga': 'global_average_sea_level_change',
         'zostoga': 'global_average_thermosteric_sea_level_change',
         'zossga': 'global_average_steric_sea_level_change',
         'wfo': 'water_flux_into_sea_water',
         'wfonocorr': 'water_flux_into_sea_water_without_flux_correction',
         'wfcorr': 'water_flux_correction',
         'hfds': 'surface_downward_heat_flux_in_sea_water',
         'hfcorr': 'heat_flux_correction',
         'hfgeou' : 'upward_geothermal_heat_flux_at_sea_floor',
         'rsdt': 'toa_incoming_shortwave_flux',
         'rlut': 'toa_outgoing_longwave_flux',
         'rsut': 'toa_outgoing_shortwave_flux',
         'vsf': 'virtual_salt_flux_into_sea_water',
         'vsfcorr': 'virtual_salt_flux_correction'}

wfo_wrong_sign = ['MIROC-ESM-CHEM', 'MIROC-ESM', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                  'IPSL-CM5A-LR', 'IPSL-CM5A-MR', 'IPSL-CM5B-LR', 'IPSL-CM6A-LR',
                  'CMCC-CM', 'EC-Earth3', 'EC-Earth3-Veg']


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


def clef_search(model, variable, ensemble, project, experiment='piControl'):
    """Use Clef to search for data files"""

    if variable in ['areacello', 'areacella']:
        if project == 'cmip6' and variable == 'areacello':
            table = 'Ofx'
        else:
            table = 'fx'
    elif variable in ['rsdt', 'rsut', 'rlut']:
        table = 'Amon'
    else:
        table = 'Omon'

    constraints = {'variable': variable, 'model': model, 'table': table,
                   'experiment': experiment, 'ensemble': ensemble}

    results = clef.code.search(session, project=project, **constraints)
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


def read_global_variable(model, variable, ensemble, project, manual_file_dict,
                         ignore_list, time_constraint, experiment='piControl'):
    """Read data for a global variable"""

    if variable in ignore_list:
        file_list = []
    elif (variable, experiment) in manual_file_dict.keys():
        file_list = manual_file_dict[(variable, experiment)]
    else:
        file_list = clef_search(model, variable, ensemble, project, experiment=experiment) 
    
    if file_list:
        cube, history = gio.combine_files(file_list, names[variable])
        if variable == 'soga':
            cube = gio.salinity_unit_check(cube)
        cube = timeseries.convert_to_annual(cube)
        cube = time_check(cube)
        if time_constraint:
            cube = cube.extract(time_constraint)
        if numpy.isnan(cube.data[0]):
            cube.data[0] = 0.0
    else:
        cube = None

    return cube


def read_area(model, variable, ensemble, project, manual_file_dict):
    """Read area data."""

    if (variable, 'piControl') in manual_file_dict.keys():
        area_files = manual_file_dict[(variable, 'piControl')]
    else:
        area_run = 'r0i0p0' if project == 'cmip5' else ensemble
        area_files = clef_search(model, variable, area_run, project)
        if not area_files:
            area_files = clef_search(model, variable, area_run, project, experiment='historical')

    if area_files:
        cube = iris.load_cube(area_files[0])
    else:
        cube = None

    return cube


def read_spatial_flux(model, variable, ensemble, project, area_cube,
                      manual_file_dict, ignore_list, time_constraint,
                      chunk=False, ref_time_coord=None):
    """Read spatial flux data and convert to global value.

    Accounts for cases where spatial dimensions are unnamed
      e.g. coord_names = ['time', --, --]
    and/or where there is no time axis.

    """

    if variable in ignore_list:
        file_list = []
    elif (variable, 'piControl') in manual_file_dict.keys():
        file_list = manual_file_dict[(variable, 'piControl')]
    else:
        file_list = clef_search(model, variable, ensemble, project) 

    cube_list = iris.cube.CubeList([])
    for infile in file_list:
        cube = iris.load_cube(infile, gio.check_iris_var(names[variable]))
        cube = gio.check_time_units(cube)     
        coord_names = [coord.name() for coord in cube.dim_coords]

        if 'time' in coord_names:
            cube = timeseries.convert_to_annual(cube, chunk=chunk)
            cube = time_check(cube)
            
        if ('time' in coord_names) and area_cube:
            area_array = uconv.broadcast_array(area_cube.data, [1, area_cube.ndim], cube.shape)
        elif area_cube:
            area_array = area_cube.data
        else:
            assert variable in ['rsdt', 'rsut', 'rlut']
            area_array = spatial_weights.area_array(cube)

        units = str(cube.units)
        assert 'm-2' in units
        cube.units = units.replace('m-2', '')
        cube.data = cube.data * area_array
        if (variable == 'wfo') and (model in wfo_wrong_sign):
            cube.data = cube.data * -1

        cube_list.append(cube)

    if cube_list:    
        cube = gio.combine_cubes(cube_list)
        if 'time' in coord_names:
            global_sum = numpy.ma.sum(cube.data, axis=(1,2))
            cube = cube[:, 0, 0].copy()
            cube.data = global_sum
        else: 
            assert ref_time_coord
            global_sum = numpy.ma.sum(cube.data)
            data = numpy.ones(len(ref_time_coord.points)) * global_sum
            cube = iris.cube.Cube(data,
                                  standard_name=cube.standard_name,
                                  long_name=cube.long_name,
                                  var_name=cube.var_name,
                                  units=cube.units,
                                  attributes=cube.attributes,
                                  dim_coords_and_dims=[(ref_time_coord, 0)])
            cube = time_check(cube)
        cube = timeseries.flux_to_total(cube)
        if time_constraint:
            cube = cube.extract(time_constraint)
    else:
        cube = None
        
    return cube


def plot_global_variable(ax, data, long_name, units, color, label=None):
    """Plot a global variable."""

    ax.grid(linestyle=':')
    ax.plot(data, color=color, label=label)
    ax.set_title(long_name)
    ax.set_xlabel('year')
    ax.set_ylabel(units)
    ax.ticklabel_format(useOffset=False)
    ax.yaxis.major.formatter._useMathText = True


def get_start_year(branch_time, control_time_axis):
    """Get the start year for a forced simulation."""

    start_year, error = uconv.find_nearest(control_time_axis, float(branch_time) + 182.5, index=True)
    assert abs(error) < 200, 'check the branch time - something seems wrong'

    return start_year


def get_data_dict(inargs, manual_file_dict, branch_year_dict):
    """Get all the necessary data."""

    if inargs.time_bounds:
        time_constraint = gio.get_time_constraint(inargs.time_bounds)
    else:
        time_constraint = None

    cube_dict = {}

    cube_dict['areacella'] = read_area(inargs.model, 'areacella', inargs.run, inargs.project, manual_file_dict)
    cube_dict['areacello'] = read_area(inargs.model, 'areacello', inargs.run, inargs.project, manual_file_dict)

    cube_dict['masso'] = read_global_variable(inargs.model, 'masso', inargs.run, inargs.project,
                                              manual_file_dict, inargs.ignore_list, time_constraint)
    cube_dict['volo'] = read_global_variable(inargs.model, 'volo', inargs.run, inargs.project,
                                             manual_file_dict, inargs.ignore_list, time_constraint)
    cube_dict['thetaoga'] = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                                 manual_file_dict, inargs.ignore_list, time_constraint)
    cube_dict['thetaoga'] = gio.temperature_unit_check(cube_dict['thetaoga'], 'K')
    cube_dict['soga'] = read_global_variable(inargs.model, 'soga', inargs.run, inargs.project,
                                             manual_file_dict, inargs.ignore_list, time_constraint) 

    cube_dict['zostoga'] = read_global_variable(inargs.model, 'zostoga', inargs.run, inargs.project,
                                                manual_file_dict, inargs.ignore_list, time_constraint) 
    if inargs.project == 'cmip5':
        cube_dict['zosga'] = read_global_variable(inargs.model, 'zosga', inargs.run, inargs.project,
                                                  manual_file_dict, inargs.ignore_list, time_constraint) 
        cube_dict['zossga'] = read_global_variable(inargs.model, 'zossga', inargs.run, inargs.project,
                                                   manual_file_dict, inargs.ignore_list, time_constraint)
    else:
        cube_dict['zosga'] = cube_dict['zossga'] = None

    wfo_areavar = 'areacella' if 'wfo' in inargs.areacella else 'areacello'
    cube_dict['wfo'] = read_spatial_flux(inargs.model, 'wfo', inargs.run, inargs.project, cube_dict[wfo_areavar],
                                         manual_file_dict, inargs.ignore_list, time_constraint, chunk=inargs.chunk)
    cube_dict['wfonocorr'] = read_spatial_flux(inargs.model, 'wfonocorr', inargs.run, inargs.project, cube_dict['areacello'],
                                               manual_file_dict, inargs.ignore_list, time_constraint, chunk=inargs.chunk)
    cube_dict['wfcorr'] = read_spatial_flux(inargs.model, 'wfcorr', inargs.run, inargs.project, cube_dict['areacello'],
                                            manual_file_dict, inargs.ignore_list, time_constraint, chunk=inargs.chunk)

    hfds_areavar = 'areacella' if 'hfds' in inargs.areacella else 'areacello'
    cube_dict['hfds'] = read_spatial_flux(inargs.model, 'hfds', inargs.run, inargs.project, cube_dict[hfds_areavar],
                                          manual_file_dict, inargs.ignore_list, time_constraint, chunk=inargs.chunk)
    cube_dict['hfcorr'] = read_spatial_flux(inargs.model, 'hfcorr', inargs.run, inargs.project, cube_dict['areacello'],
                                            manual_file_dict, inargs.ignore_list, time_constraint, chunk=inargs.chunk)
    cube_dict['hfgeou'] = read_spatial_flux(inargs.model, 'hfgeou', inargs.run, inargs.project, cube_dict['areacello'],
                                            manual_file_dict, inargs.ignore_list, time_constraint, chunk=inargs.chunk,
                                            ref_time_coord=cube_dict['masso'].coord('time'))
    cube_dict['vsf'] = read_spatial_flux(inargs.model, 'vsf', inargs.run, inargs.project, cube_dict['areacello'],
                                         manual_file_dict, inargs.ignore_list, time_constraint, chunk=inargs.chunk)
    cube_dict['vsfcorr'] = read_spatial_flux(inargs.model, 'vsfcorr', inargs.run, inargs.project, cube_dict['areacello'],
                                             manual_file_dict, inargs.ignore_list, time_constraint, chunk=inargs.chunk)

    cube_dict['rsdt'] = read_spatial_flux(inargs.model, 'rsdt', inargs.run, inargs.project, cube_dict['areacella'],
                                          manual_file_dict, inargs.ignore_list, time_constraint)
    cube_dict['rlut'] = read_spatial_flux(inargs.model, 'rlut', inargs.run, inargs.project, cube_dict['areacella'],
                                          manual_file_dict, inargs.ignore_list, time_constraint)
    cube_dict['rsut'] = read_spatial_flux(inargs.model, 'rsut', inargs.run, inargs.project, cube_dict['areacella'],
                                          manual_file_dict, inargs.ignore_list, time_constraint)

    return cube_dict


def plot_raw(inargs, cube_dict, branch_year_dict, manual_file_dict):
    """Plot the raw budget variables."""

    fig = plt.figure(figsize=[15, 25])
    nrows = 5
    ncols = 2

    if cube_dict['masso']:
        ax1 = fig.add_subplot(nrows, ncols, 1)
        linestyles = itertools.cycle(('-', '--', ':', '-.'))
        for experiment, branch_year in branch_year_dict.items():
            cube = read_global_variable(inargs.model, 'masso', inargs.run, inargs.project,
                                        manual_file_dict, inargs.ignore_list, experiment=experiment)
            if cube:
                xdata = numpy.arange(branch_year, len(cube.data) + branch_year)
                ax1.plot(xdata, cube.data, color='limegreen', label=experiment, linestyle=next(linestyles))
        plot_global_variable(ax1, cube_dict['masso'].data, cube_dict['masso'].long_name,
                             cube_dict['masso'].units, 'green', label='piControl')
        ax1.legend()
    if cube_dict['volo']:
        ax2 = fig.add_subplot(nrows, ncols, 2)
        linestyles = itertools.cycle(('-', '--', ':', '-.'))
        for experiment, branch_year in branch_year_dict.items():
            cube = read_global_variable(inargs.model, 'volo', inargs.run, inargs.project,
                                        manual_file_dict, inargs.ignore_list, experiment=experiment)
            if cube:
                xdata = numpy.arange(branch_year, len(cube.data) + branch_year)
                ax2.plot(xdata, cube.data, color='tomato', label=experiment, linestyle=next(linestyles))
        plot_global_variable(ax2, cube_dict['volo'].data, cube_dict['volo'].long_name,
                            cube_dict['volo'].units, 'red', label='piControl')
        ax2.legend()
    if cube_dict['masso'] and cube_dict['volo']:
        ax3 = fig.add_subplot(nrows, ncols, 3)
        units = str(cube_dict['masso'].units) + ' / ' + str(cube_dict['volo'].units)
        plot_global_variable(ax3, cube_dict['masso'].data / cube_dict['volo'].data, 'Density', units, 'grey')
    if cube_dict['thetaoga']:
        ax4 = fig.add_subplot(nrows, ncols, 4)
        linestyles = itertools.cycle(('-', '--', ':', '-.'))
        for experiment, branch_year in branch_year_dict.items():
            cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                        manual_file_dict, inargs.ignore_list, experiment=experiment)
            if cube:
                cube = gio.temperature_unit_check(cube, 'K')
                xdata = numpy.arange(branch_year, len(cube.data) + branch_year)
                ax4.plot(xdata, cube.data, color='yellow', label=experiment, linestyle=next(linestyles))
        plot_global_variable(ax4, cube_dict['thetaoga'].data, cube_dict['thetaoga'].long_name,
                             cube_dict['thetaoga'].units, 'gold', label='piControl')
        ax4.legend()
    if cube_dict['soga']:
        ax5 = fig.add_subplot(nrows, ncols, 5)
        plot_global_variable(ax5, cube_dict['soga'].data, cube_dict['soga'].long_name, 'g/kg', 'orange')
    if cube_dict['zostoga']:
        ax6 = fig.add_subplot(nrows, ncols, 6)
        if cube_dict['zosga']:
            ax6.plot(cube_dict['zosga'].data, color='purple', label=cube_dict['zosga'].long_name, linestyle=':')
        if cube_dict['zossga']:
            ax6.plot(cube_dict['zossga'].data, color='purple', label=cube_dict['zossga'].long_name, linestyle='-.')
        plot_global_variable(ax6, cube_dict['zostoga'].data, 'Sea Level', cube_dict['zostoga'].units,
                             'purple', label=cube_dict['zostoga'].long_name)
        ax6.legend()
    if cube_dict['wfo']:
        ax7 = fig.add_subplot(nrows, ncols, 7)
        if cube_dict['wfcorr']:
            ax7.plot(cube_dict['wfcorr'].data, color='blue', label=cube_dict['wfcorr'].long_name, linestyle=':')
        if cube_dict['wfonocorr']:
            ax7.plot(cube_dict['wfonocorr'].data, color='blue', label=cube_dict['wfonocorr'].long_name, linestyle='-.')
        plot_global_variable(ax7, cube_dict['wfo'].data, 'Annual Water Flux Into Ocean', cube_dict['wfo'].units,
                             'blue', label=cube_dict['wfo'].long_name)
        ax7.legend()
    if cube_dict['hfds']:
        ax8 = fig.add_subplot(nrows, ncols, 8)
        if cube_dict['hfcorr']:
            ax8.plot(cube_dict['hfcorr'].data, color='teal', label=cube_dict['hfcorr'].long_name, linestyle=':')
        if cube_dict['hfgeou']:
            ax8.plot(cube_dict['hfgeou'].data, color='teal', label=cube_dict['hfgeou'].long_name, linestyle='-.')
        plot_global_variable(ax8, cube_dict['hfds'].data, 'Annual Heat Flux Into Ocean', cube_dict['hfds'].units,
                             'teal', label=cube_dict['hfds'].long_name)
        ax8.legend()
    if cube_dict['rsdt']:
        ax9 = fig.add_subplot(nrows, ncols, 9)
        ax9.plot(cube_dict['rsdt'].data, color='maroon', label=cube_dict['rsdt'].long_name, linestyle=':')
        ax9.plot(cube_dict['rsut'].data, color='maroon', label=cube_dict['rsut'].long_name, linestyle='-.')
        plot_global_variable(ax9, cube_dict['rlut'].data, 'Annual TOA Radiative Fluxes',
                             cube_dict['rlut'].units, 'maroon', label=cube_dict['rlut'].long_name)
        ax9.legend()
    if cube_dict['vsf'] or cube_dict['vsfcorr']:
        ax10 = fig.add_subplot(nrows, ncols, 10)
        if cube_dict['vsf']:
            plot_global_variable(ax10, cube_dict['vsf'].data, 'Annual Virtual Salt Fluxes',
                                 cube_dict['vsf'].units, 'orange', label=cube_dict['vsf'].long_name)
        if cube_dict['vsfcorr']:
            plot_global_variable(ax10, cube_dict['vsfcorr'].data, 'Annual Virtual Salt Fluxes',
                                cube_dict['vsfcorr'].units, 'yellow', label=cube_dict['vsfcorr'].long_name)

    plt.subplots_adjust(top=0.92)
    title = '%s (%s), %s, piControl'  %(inargs.model, inargs.project, inargs.run)
    plt.suptitle(title)
    plt.savefig(inargs.rawfile, bbox_inches='tight')


def delta_masso_from_soga(s_orig, s_new, m_orig):
    """Infer a change in mass from salinity"""

    delta_m = m_orig * ((s_orig / s_new) - 1)    
    
    return delta_m


def delta_soga_from_masso(m_orig, m_new, s_orig):
    """Infer a change in global average salinity from mass"""

    delta_s = s_orig * ((m_orig / m_new) - 1)    
    
    return delta_s


def calc_trend(data, name, units, outlier_threshold=None):
    """Calculate the linear trend."""

    time_axis = numpy.arange(0, len(data)) 
    trend = timeseries.linear_trend(data, time_axis, outlier_threshold)

    trend_text = 'trend, %s: %s %s/yr'  %(name, str(trend), units) 
    numbers_out_list.append(trend_text)


def calc_regression(x_data, y_data, label, decadal_mean=False):
    """Calculate the linear regression coefficient."""

    x_data = x_data.copy()
    y_data = y_data.copy()

    nx = len(x_data)
    ny = len(y_data)
    if nx > ny:
        x_data = x_data[0:ny]
    elif ny > nx:
        y_data = y_data[0:nx]
    
    if decadal_mean:
        x_data = timeseries.runmean(x_data, 10)
        y_data = timeseries.runmean(y_data, 10)

    if (x_data.max() == x_data.min()) or (y_data.max() == y_data.min()):
        regression_text = 'regression coefficient, %s: ERROR'  %(label)
    else:
        validation_coeff = numpy.ma.polyfit(x_data, y_data, 1)[0]

        x_data = sm.add_constant(x_data)
        model = sm.OLS(y_data, x_data)
        results = model.fit()
        coeff = results.params[-1]
        conf_lower, conf_upper = results.conf_int()[-1]
        assert validation_coeff < conf_upper
        assert validation_coeff > conf_lower

        stderr = results.bse[-1]
        n_orig = int(results.nobs)
        n_eff = uconv.effective_sample_size(y_data, n_orig)
        stderr_adjusted = (stderr * numpy.sqrt(n_orig)) / numpy.sqrt(n_eff)
    
        regression_text = 'regression coefficient, %s: %s [%s, %s] +- %s (or %s)'  %(label, str(coeff), str(conf_lower), str(conf_upper), str(stderr), str(stderr_adjusted))

    numbers_out_list.append(regression_text)


def dedrift_data(data, fit='cubic'):
    """Remove drift and plot."""
    
    assert fit in ['linear', 'cubic']
    deg = 3 if fit == 'cubic' else 1
    
    time_axis = numpy.arange(len(data))
    coefficients = timeseries.fit_polynomial(data, time_axis, deg, None)
    drift = numpy.polyval(coefficients, time_axis)
    dedrifted_data = data - drift

    return dedrifted_data
    

def plot_ohc(ax_top, ax_middle, masso_data, cp, cube_dict, ylim=None):
    """Plot the OHC timeseries and it's components"""

    assert cube_dict['thetaoga'].units == 'K'

    ohc_data = masso_data * cube_dict['thetaoga'].data * cp
    ohc_anomaly_data = ohc_data - ohc_data[0]

    thetaoga_anomaly_data = cube_dict['thetaoga'].data - cube_dict['thetaoga'].data[0]
    thermal_data = cp * masso_data[0] * thetaoga_anomaly_data

    masso_anomaly_data = masso_data - masso_data[0]
    barystatic_data = cp * cube_dict['thetaoga'].data[0] * masso_anomaly_data

    calc_trend(ohc_anomaly_data, 'OHC', 'J')
    calc_trend(thermal_data, 'thermal OHC', 'J')
    calc_trend(barystatic_data, 'barystatic OHC', 'J')

    ax_top.grid(linestyle=':')
    ax_top.plot(ohc_anomaly_data, color='purple', label='OHC ($H$)')
    ax_top.plot(thermal_data, color='red', label='thermal OHC ($H_T$)')
    ax_top.plot(barystatic_data, color='blue', label='barystatic OHC ($H_M$)')

    #ohc_anomaly_cubic_dedrifted = dedrift_data(ohc_anomaly_data, fit='cubic')
    #ax_bottom.plot(ohc_anomaly_cubic_dedrifted, color='black')

    thermal_data_linear_dedrifted = dedrift_data(thermal_data, fit='linear')
    thermal_data_cubic_dedrifted = dedrift_data(thermal_data, fit='cubic')
    ax_middle.grid(linestyle=':')
    ax_middle.plot(thermal_data_cubic_dedrifted, color='red', label='thermal OHC ($H_T$)')

    # Optional data

    if cube_dict['rsdt'] and cube_dict['rlut'] and cube_dict['rsut']:
        nettoa_data = cube_dict['rsdt'].data - cube_dict['rlut'].data - cube_dict['rsut'].data
        nettoa_cumsum_data = numpy.cumsum(nettoa_data)
        nettoa_cumsum_anomaly = nettoa_cumsum_data - nettoa_cumsum_data[0]
        calc_trend(nettoa_cumsum_anomaly, 'cumulative netTOA', 'J')
        ax_top.plot(nettoa_cumsum_anomaly, color='gold', label='cumulative netTOA ($Q_r$)')
        nettoa_linear_dedrifted = dedrift_data(nettoa_cumsum_anomaly, fit='linear')
        nettoa_cubic_dedrifted = dedrift_data(nettoa_cumsum_anomaly, fit='cubic')
        ax_middle.plot(nettoa_cubic_dedrifted, color='gold', label='cumulative netTOA ($Q_r$)')
        calc_regression(nettoa_cubic_dedrifted, thermal_data_cubic_dedrifted,
                        'cumulative netTOA radiative flux vs thermal OHC anomaly (cubic dedrift, annual mean)')
        calc_regression(nettoa_cubic_dedrifted, thermal_data_cubic_dedrifted,
                        'cumulative netTOA radiative flux vs thermal OHC anomaly (cubic dedrift, decadal mean)', decadal_mean=True)
        calc_regression(nettoa_linear_dedrifted, thermal_data_linear_dedrifted,
                        'cumulative netTOA radiative flux vs thermal OHC anomaly (linear dedrift, annual mean)')
        calc_regression(nettoa_linear_dedrifted, thermal_data_linear_dedrifted,
                        'cumulative netTOA radiative flux vs thermal OHC anomaly (linear dedrift, decadal mean)', decadal_mean=True)

    if cube_dict['hfds']:
        net_surface_heat_flux_data = cube_dict['hfds'].data
        if cube_dict['hfds'] and cube_dict['hfgeou']:
            net_surface_heat_flux_data = net_surface_heat_flux_data + cube_dict['hfgeou'].data
        if cube_dict['hfds'] and cube_dict['hfcorr']:
            net_surface_heat_flux_data = net_surface_heat_flux_data + cube_dict['hfcorr'].data
        hfds_cumsum_data = numpy.cumsum(net_surface_heat_flux_data)
        hfds_cumsum_anomaly = hfds_cumsum_data - hfds_cumsum_data[0]
        calc_trend(hfds_cumsum_anomaly, 'cumulative hfds', 'J')
        ax_top.plot(hfds_cumsum_anomaly, color='orange', label='cumulative ocean surface heat flux ($Q_h$)')
        hfds_linear_dedrifted = dedrift_data(hfds_cumsum_anomaly, fit='linear')
        hfds_cubic_dedrifted = dedrift_data(hfds_cumsum_anomaly, fit='cubic')
        ax_middle.plot(hfds_cubic_dedrifted, color='orange', label='cumulative ocean surface heat flux ($Q_h$)')
        calc_regression(hfds_cubic_dedrifted, thermal_data_cubic_dedrifted,
                        'cumulative surface heat flux vs thermal OHC anomaly (cubic dedrift, annual mean)')
        calc_regression(hfds_cubic_dedrifted, thermal_data_cubic_dedrifted,
                        'cumulative surface heat flux vs thermal OHC anomaly (cubic dedrift, decadal mean)', decadal_mean=True)
        calc_regression(hfds_linear_dedrifted, thermal_data_linear_dedrifted,
                        'cumulative surface heat flux vs thermal OHC anomaly (linear dedrift, annual mean)')
        calc_regression(hfds_linear_dedrifted, thermal_data_linear_dedrifted,
                        'cumulative surface heat flux vs thermal OHC anomaly (linear dedrift, decadal mean)', decadal_mean=True)
        if cube_dict['rsdt'] and cube_dict['rlut'] and cube_dict['rsut']:
            calc_regression(nettoa_cubic_dedrifted, hfds_cubic_dedrifted,
                            'cumulative netTOA radiative flux vs cumulative surface heat flux (cubic dedrift, annual mean)')
            calc_regression(nettoa_cubic_dedrifted, hfds_cubic_dedrifted,
                            'cumulative netTOA radiative flux vs cumulative surface heat flux (cubic dedrift, decadal mean)', decadal_mean=True)
            calc_regression(nettoa_linear_dedrifted, hfds_linear_dedrifted,
                            'cumulative netTOA radiative flux vs cumulative surface heat flux (linear dedrift, annual mean)')
            calc_regression(nettoa_linear_dedrifted, hfds_linear_dedrifted,
                            'cumulative netTOA radiative flux vs cumulative surface heat flux (linear dedrift, decadal mean)', decadal_mean=True)

#    if cube_dict['wfo']:
#        wfo_cumsum_data = numpy.cumsum(cube_dict['wfo'].data)
#        wfo_cumsum_anomaly = wfo_cumsum_data - wfo_cumsum_data[0]
#        wfo_inferred_barystatic = cp * cube_dict['thetaoga'].data[0] * wfo_cumsum_anomaly
#        ax_top.plot(wfo_inferred_barystatic, color='blue', linestyle='--', label='cumulative surface freshwater flux')

#    if cube_dict['hfds'] and cube_dict['wfo']:
#        total_surface_flux = hfds_cumsum_anomaly + wfo_inferred_barystatic
#        calc_trend(total_surface_flux, 'cumulative surface total flux', 'J')
#        ax_top.plot(total_surface_flux, color='black', linestyle='--', label='inferred OHC anomaly from suface fluxes')
#        surface_flux_cubic_dedrifted = dedrift_data(total_surface_flux, fit='cubic')
#        ax_bottom.plot(surface_flux_cubic_dedrifted, color='black', linestyle='--')

    if ylim:
        ax_top.set_ylim(ylim[0] * 1e24, ylim[1] * 1e24)

    ax_top.set_title('heat budget')
    ax_middle.set_title('heat budget (de-drifted)')
    ax_middle.set_xlabel('year')
#    ax_bottom.set_title('De-drifted total OHC comparison')
#    ax_bottom.set_xlabel('year')
    ax_top.set_ylabel('equivalent change in OHC (J)')
    ax_middle.set_ylabel('equivalent change in OHC (J)')
#    ax_bottom.set_ylabel('equivalent change in OHC (J)')
    ax_top.yaxis.major.formatter._useMathText = True
    ax_middle.yaxis.major.formatter._useMathText = True
#    ax_bottom.yaxis.major.formatter._useMathText = True
    ax_top.legend()
#    ax_middle.legend()


def plot_sea_level(ax_top, ax_middle, masso_data, cube_dict, ocean_area, density, ylim=None):
    """Plot the sea level timeseries and it's components"""

    # Compulsory variables

    s_orig = numpy.ones(cube_dict['soga'].data.shape[0]) * cube_dict['soga'].data[0]
    m_orig = numpy.ones(masso_data.shape[0]) * masso_data[0]
    masso_from_soga = numpy.fromiter(map(delta_masso_from_soga, s_orig, cube_dict['soga'].data, m_orig), float)
    soga_from_masso = numpy.fromiter(map(delta_soga_from_masso, m_orig, masso_data, s_orig), float) 

    calc_trend(soga_from_masso, 'global ocean mass', 'g/kg')
    calc_trend(cube_dict['soga'].data, 'global mean salinity', 'g/kg')

    masso_anomaly_data = masso_data - masso_data[0]
    calc_trend(masso_anomaly_data, 'global ocean mass', 'kg')

    if ocean_area:
        sea_level_anomaly_from_masso = sea_level_from_mass(masso_anomaly_data, ocean_area, density)
        sea_level_anomaly_from_soga = sea_level_from_mass(masso_from_soga, ocean_area, density)
        calc_trend(sea_level_anomaly_from_masso, 'global ocean mass', 'm')

        ax_top.grid(linestyle=':')
        ax_top.plot(sea_level_anomaly_from_masso, color='blue', label='ocean mass ($M$)')
        ax_top.plot(sea_level_anomaly_from_soga, color='teal', label='ocean salinity ($S$)')

        masso_linear_dedrifted = dedrift_data(sea_level_anomaly_from_masso, fit='linear')
        masso_cubic_dedrifted = dedrift_data(sea_level_anomaly_from_masso, fit='cubic')
        ax_middle.grid(linestyle=':')
        ax_middle.plot(masso_cubic_dedrifted, color='blue', label='ocean mass ($M$)')

        soga_linear_dedrifted = dedrift_data(sea_level_anomaly_from_soga, fit='linear')
        soga_cubic_dedrifted = dedrift_data(sea_level_anomaly_from_soga, fit='cubic')
        ax_middle.plot(soga_cubic_dedrifted, color='teal', label='ocean salinity ($S$)')
        calc_regression(masso_cubic_dedrifted, soga_cubic_dedrifted,
                        'change in global ocean mass vs global mean salinity anomaly (cubic dedrift, annual mean)')
        calc_regression(masso_cubic_dedrifted, soga_cubic_dedrifted,
                        'change in global ocean mass vs global mean salinity anomaly (cubic dedrift, decadal mean)', decadal_mean=True)
        calc_regression(masso_linear_dedrifted, soga_linear_dedrifted,
                        'change in global ocean mass vs global mean salinity anomaly (linear dedrift, annual mean)')
        calc_regression(masso_linear_dedrifted, soga_linear_dedrifted,
                        'change in global ocean mass vs global mean salinity anomaly (linear dedrift, decadal mean)', decadal_mean=True)

    # Optional variables
    if cube_dict['wfonocorr'] and ocean_area:
        wfonocorr_cumsum_data = numpy.cumsum(cube_dict['wfonocorr'].data)
        wfonocorr_cumsum_anomaly = wfonocorr_cumsum_data - wfonocorr_cumsum_data[0]
        sea_level_anomaly_from_wfonocorr = sea_level_from_mass(wfonocorr_cumsum_anomaly, ocean_area, density)
        ax_top.plot(sea_level_anomaly_from_wfonocorr, color='lightslategray', linestyle=':',
                    label='cumulative surface freshwater flux (no flux correction)')

    if cube_dict['wfo'] and ocean_area:
        wfo_cumsum_data = numpy.cumsum(cube_dict['wfo'].data)
        wfo_cumsum_anomaly = wfo_cumsum_data - wfo_cumsum_data[0]
        sea_level_anomaly_from_wfo = sea_level_from_mass(wfo_cumsum_anomaly, ocean_area, density)
        calc_trend(wfo_cumsum_anomaly, 'cumulative wfo', 'kg')
        ax_top.plot(sea_level_anomaly_from_wfo, color='lightslategray',
                    label='cumulative freshwater flux ($Q_m$)')

        wfo_linear_dedrifted = dedrift_data(sea_level_anomaly_from_wfo, fit='linear')
        wfo_cubic_dedrifted = dedrift_data(sea_level_anomaly_from_wfo, fit='cubic')
        ax_middle.plot(wfo_cubic_dedrifted, color='lightslategray',
                       label='cumulative freshwater flux ($Q_m$)')
        
        calc_regression(wfo_cubic_dedrifted, masso_cubic_dedrifted,
                        'cumulative surface freshwater flux vs change in global ocean mass (cubic dedrift, annual mean)')
        calc_regression(wfo_cubic_dedrifted, masso_cubic_dedrifted,
                        'cumulative surface freshwater flux vs change in global ocean mass (cubic dedrift, decadal mean)', decadal_mean=True)
        calc_regression(wfo_linear_dedrifted, masso_linear_dedrifted,
                        'cumulative surface freshwater flux vs change in global ocean mass (linear dedrift, annual mean)')
        calc_regression(wfo_linear_dedrifted, masso_linear_dedrifted,
                        'cumulative surface freshwater flux vs change in global ocean mass (linear dedrift, decadal mean)', decadal_mean=True)
        
        calc_regression(wfo_cubic_dedrifted, soga_cubic_dedrifted,
                        'cumulative surface freshwater flux vs global mean salinity anomaly (cubic dedrift, annual mean)')
        calc_regression(wfo_cubic_dedrifted, soga_cubic_dedrifted,
                        'cumulative surface freshwater flux vs global mean salinity anomaly (cubic dedrift, decadal mean)', decadal_mean=True)
        calc_regression(wfo_linear_dedrifted, soga_linear_dedrifted,
                        'cumulative surface freshwater flux vs global mean salinity anomaly (linear dedrift, annual mean)')
        calc_regression(wfo_linear_dedrifted, soga_linear_dedrifted,
                        'cumulative surface freshwater flux vs global mean salinity anomaly (linear dedrift, decadal mean)', decadal_mean=True)

#    if cube_dict['zostoga']:
#        zostoga_anomaly = cube_dict['zostoga'].data - cube_dict['zostoga'].data[0]
#        calc_trend(zostoga_anomaly, 'thermosteric sea level', 'm')
#        ax_top.plot(zostoga_anomaly, color='purple', linestyle='--', label='change in thermosteric sea level')
#
#    if cube_dict['zosga'] and cube_dict['zossga']:
#        zosga_anomaly = cube_dict['zosga'].data - cube_dict['zosga'].data[0]
#        zossga_anomaly = cube_dict['zossga'].data - cube_dict['zossga'].data[0]
#        zosbary_anomaly = zosga_anomaly - zossga_anomaly
#        calc_trend(zosbary_anomaly, 'barystatic sea level', 'm')
#        ax_top.plot(zosbary_anomaly, color='purple', label='change in barystatic sea level')
#        zosbary_cubic_dedrifted = dedrift_data(zosbary_anomaly, fit='cubic')
#        ax_middle.plot(zosbary_cubic_dedrifted, color='purple')
    
    if ylim:
        ax_top.set_ylim(ylim[0], ylim[1])

    ax_top.set_title('mass budget')
    ax_middle.set_title('mass budget (de-drifted)')
    ax_middle.set_xlabel('year')
    ax_top.set_ylabel('equivalent change in global sea level (m)')
    ax_middle.set_ylabel('equivalent change in global sea level (m)')
    ax_top.yaxis.major.formatter._useMathText = True
    ax_middle.yaxis.major.formatter._useMathText = True
    ax_top.legend()
    #ax_middle.legend(loc=2)    


def sea_level_from_mass(mass_anomaly_data, ocean_area, density):
    """Infer a change in sea level from change in mass"""
    
    volume_anomaly_data = mass_anomaly_data / density
    sea_level_anomaly_data = volume_anomaly_data / ocean_area     
        
    return sea_level_anomaly_data


def get_manual_file_dict(file_list):
    """Put the manually entered files into a dict"""

    file_dict = {}
    for files in file_list:
        variable = files[0].split('/')[-1].split('_')[0]
        experiment = files[0].split('/')[-1].split('_')[3]
        file_dict[(variable, experiment)] = files

    return file_dict 


def common_time_period(cube_dict):
    """Get the common time period for comparison."""

    # Find the common time period
    ref_years = cube_dict['masso'].coord('year').points
    minlen = len(ref_years)
    for var, cube in cube_dict.items():
        if cube and var not in ['masso', 'areacello', 'areacella']:
            years = cube.coord('year').points
            nyrs = len(years)
            if nyrs < minlen:
                assert ref_years[0:nyrs][0] == years[0], 'mismatch in time axes'
                assert ref_years[0:nyrs][-1] == years[-1], 'mismatch in time axes'
                ref_years = years
                minlen = len(years)

    for var, cube in cube_dict.items():
        if cube and var not in ['areacello', 'areacella']:
            cube_dict[var] = cube[0: minlen]

    return cube_dict
  

def plot_comparison(inargs, cube_dict, branch_year_dict):
    """Plot the budget comparisons."""
    
    cube_dict = common_time_period(cube_dict)

    if inargs.volo:
        masso_data = cube_dict['volo'].data * inargs.density
    else:
        masso_data = cube_dict['masso'].data

    if cube_dict['areacello']:
        ocean_area = cube_dict['areacello'].data.sum()
        area_text = 'ocean surface area: %s %s'  %(str(ocean_area), cube_dict['areacello'].units) 
    else:
        ocean_area = None
        area_text = 'ocean surface area: nan'

    numbers_out_list.append(area_text)

    fig = plt.figure(figsize=[20, 12])
    gs = gridspec.GridSpec(3, 2)
    ax1 = plt.subplot(gs[0:2, 0])
    ax2 = plt.subplot(gs[0:2, 1])
    ax3 = plt.subplot(gs[2, 0])
    ax4 = plt.subplot(gs[2, 1])
#    ax5 = plt.subplot(gs[3, 0])

    linestyles = itertools.cycle(('-', '-', '--', '--', ':', ':', '-.', '-.'))
    for experiment, branch_year in branch_year_dict.items():
        ax1.axvline(branch_year, linestyle=next(linestyles), color='0.5', alpha=0.5, label=experiment+' branch time')
        ax2.axvline(branch_year, linestyle=next(linestyles), color='0.5', alpha=0.5, label=experiment+' branch time')

    plot_ohc(ax1, ax3, masso_data, inargs.cpocean, cube_dict, ylim=inargs.ohc_ylim)
    plot_sea_level(ax2, ax4, masso_data, cube_dict, ocean_area, inargs.density, ylim=inargs.sealevel_ylim)

    plt.subplots_adjust(top=0.92)
    ax1.text(0.03, 0.08, '(a)', transform=ax1.transAxes, fontsize=22, va='top')
    ax2.text(0.03, 0.08, '(b)', transform=ax2.transAxes, fontsize=22, va='top')
    ax3.text(0.03, 0.15, '(c)', transform=ax3.transAxes, fontsize=22, va='top')
    ax4.text(0.03, 0.15, '(d)', transform=ax4.transAxes, fontsize=22, va='top')

    if inargs.title:
        title = '%s, %s, piControl'  %(inargs.model, inargs.run)
        plt.suptitle(title)

    plt.savefig(inargs.compfile, bbox_inches='tight')


def get_branch_years(inargs, manual_file_dict, manual_branch_time):
    """Get the branch year for various experiments"""

    thetaoga_cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                         manual_file_dict, inargs.ignore_list)
    control_time_axis = thetaoga_cube.coord('time').points
    branch_years = {}
    for experiment in ['historical', '1pctCO2']:
        cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                    manual_file_dict, inargs.ignore_list, experiment=experiment)
        if cube:
            if manual_branch_time:
                branch_time = manual_branch_time
            else:
                try:
                    branch_time = cube.attributes['branch_time']
                except KeyError:
                    branch_time = cube.attributes['branch_time_in_parent']
            branch_years[experiment] = get_start_year(branch_time, control_time_axis)
    
    return branch_years


def get_log_text(extra_notes_list):
    """Write the metadata to file."""

    flat_list = [item for sublist in extra_notes_list for item in sublist]
    flat_list = list(set(flat_list))
    flat_list.sort()
    log_text = cmdprov.new_log(git_repo=repo_dir, extra_notes=flat_list)

    return log_text


def main(inargs):
    """Run the program."""

    manual_file_dict = get_manual_file_dict(inargs.manual_files)
    if inargs.forced_experiments:
        branch_year_dict = get_branch_years(inargs, manual_file_dict, inargs.branch_time)
    else:
        branch_year_dict = {}

    cube_dict = get_data_dict(inargs, manual_file_dict, branch_year_dict)

    if inargs.rawfile:
        plot_raw(inargs, cube_dict, branch_year_dict, manual_file_dict)
        log_text = get_log_text(processed_files)
        log_file = re.sub('.png', '.met', inargs.rawfile)
        cmdprov.write_log(log_file, log_text)

    if inargs.compfile:
        plot_comparison(inargs, cube_dict, branch_year_dict)
        processed_files.append(numbers_out_list)
        log_text = get_log_text(processed_files)
        log_file = re.sub('.png', '.met', inargs.compfile)
        cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot variables relevant for the global energy and water budget'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("model", type=str, help="Model (use dots not dashes between numbers in model names)")
    parser.add_argument("run", type=str, help="Run (e.g. r1i1p1)")
    parser.add_argument("project", type=str, choices=('cmip5', 'cmip6'), help="Project")

    parser.add_argument("--rawfile", type=str, default=None, help="Output raw data file name")
    parser.add_argument("--compfile", type=str, default=None, help="Output comparison data file name")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")

    parser.add_argument("--volo", action="store_true", default=False,
                        help="Use volo to calculate masso (useful for boussinesq models)")
    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Chunk annual mean calculation for spatial variables (useful for boussinesq models)")
    parser.add_argument("--forced_experiments", action="store_true", default=False,
                        help="Plot the forced experiments (raw) or their branch time (comparison)")
    parser.add_argument("--areacella", type=str, nargs='*', default=[],
                        help="ocean surface fluxes on an atmosphere grid")

    parser.add_argument("--cpocean", type=float, default=4000,
                        help="Specific heat in ocean in J/(kg K)")
    parser.add_argument("--density", type=float, default=1026,
                        help="Reference density in kg / m3")

    parser.add_argument("--branch_time", type=float, default=None,
                        help="Override branch time from file attributes with this one")
    parser.add_argument("--manual_files", type=str, action="append", nargs='*', default=[],
                        help="Use these manually entered files instead of the clef search")
    parser.add_argument("--ignore_list", type=str, nargs='*', default=[],
                        help="Variables to ignore")
    parser.add_argument("--ohc_ylim", type=float, nargs=2, metavar=('LOWER_LIMIT', 'UPPER_LIMIT'), default=None,
                        help="y-axis limits for OHC plot (*1e24) [default = auto]")
    parser.add_argument("--sealevel_ylim", type=float, nargs=2, metavar=('LOWER_LIMIT', 'UPPER_LIMIT'), default=None,
                        help="y-axis limits for sea level plot [default = auto]")
    
    parser.add_argument("--title", action="store_true", default=False,
                        help="Include a plot title [default=False]")

    args = parser.parse_args()             
    main(args)
