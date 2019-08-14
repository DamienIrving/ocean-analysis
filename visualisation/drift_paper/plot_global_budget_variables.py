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

processing_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(processing_dir)

import timeseries
import general_io as gio
import convenient_universal as uconv


# Define functions 

processed_files = []
trend_list = []

names = {'masso': 'sea_water_mass',
         'volo': 'sea_water_volume',
         'thetaoga': 'sea_water_potential_temperature',
         'soga': 'sea_water_salinity',
         'zosga': 'global_average_sea_level_change',
         'zostoga': 'global_average_thermosteric_sea_level_change',
         'zossga': 'global_average_steric_sea_level_change',
         'wfo': 'water_flux_into_sea_water',
         'wfcorr': 'water_flux_correction',
         'wfonocorr': 'water_flux_into_sea_water_without_flux_correction',
         'hfds': 'surface_downward_heat_flux_in_sea_water',
         'hfcorr': 'heat_flux_correction',
         'hfgeou' : 'upward_geothermal_heat_flux_at_sea_floor',
         'rsdt': 'toa_incoming_shortwave_flux',
         'rlut': 'toa_outgoing_longwave_flux',
         'rsut': 'toa_outgoing_shortwave_flux',
         'vsf': 'virtual_salt_flux_into_sea_water',
         'vsfcorr': 'virtual_salt_flux_correction'}


def get_latest(results):
    """Select the latest results"""

    if results:
        latest = results[0]
        for result in results[1:]:
            if float(result['version']) > float(latest['version']):
                latest = result
    else:
        latest = []    

    return latest


def clef_search(model, variable, ensemble, project, experiment='piControl'):
    """Use Clef to search for data files"""

    if variable in ['areacello', 'areacella']:
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


def read_global_variable(model, variable, ensemble, project, manual_file_dict, ignore_list):
    """Read data for a global variable"""

    if variable in ignore_list:
        file_list = []
    elif variable in manual_file_dict.keys():
        file_list = manual_file_dict[variable]
    else:
        file_list = clef_search(model, variable, ensemble, project) 
    
    if file_list:
        cube, history = gio.combine_files(file_list, names[variable])
        if variable == 'soga':
            cube = gio.salinity_unit_check(cube)
        cube = timeseries.convert_to_annual(cube)
        if numpy.isnan(cube.data[0]):
            cube.data[0] = 0.0
    else:
        cube = None

    return cube


def read_spatial_flux(model, variable, ensemble, project, manual_file_dict, ignore_list, chunk=False):
    """Read spatial flux data and convert to global value"""
    
    if variable in ignore_list:
        file_list = []
    elif variable in manual_file_dict.keys():
        file_list = manual_file_dict[variable]
    else:
        file_list = clef_search(model, variable, ensemble, project) 

    area_var = 'areacella' if variable in ['rsdt', 'rlut', 'rsut'] else 'areacello'
    area_file = clef_search(model, area_var, 'r0i0p0', project)
    if not area_file:
        area_file = clef_search(model, area_var, 'r0i0p0', project, experiment='historical')
    area_file = area_file[0]

    if file_list and area_file:
        cube, history = gio.combine_files(file_list, names[variable])
        cube = timeseries.convert_to_annual(cube, chunk=chunk)

        area_cube = iris.load_cube(area_file)
        area_array = uconv.broadcast_array(area_cube.data, [1, area_cube.ndim], cube.shape)

        units = str(cube.units)
        assert 'm-2' in units
        cube.units = units.replace('m-2', '')
        cube.data = cube.data * area_array

        # Calculate the global sum
        coord_names = [coord.name() for coord in cube.dim_coords]
        coord_names.remove('time')
        cube = cube.collapsed(coord_names, iris.analysis.SUM, weights=None)
        for coord in coord_names:
            cube.remove_coord(coord)

        # Remove the s-1
        cube = timeseries.flux_to_total(cube)
    
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


def plot_raw(inargs):
    """Plot the raw budget variables."""

    manual_file_dict = get_manual_file_dict(inargs.manual_files)
    masso_cube = read_global_variable(inargs.model, 'masso', inargs.run, inargs.project,
                                      manual_file_dict, inargs.ignore_list)
    volo_cube = read_global_variable(inargs.model, 'volo', inargs.run, inargs.project,
                                     manual_file_dict, inargs.ignore_list)
    thetaoga_cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                         manual_file_dict, inargs.ignore_list)
    soga_cube = read_global_variable(inargs.model, 'soga', inargs.run, inargs.project,
                                     manual_file_dict, inargs.ignore_list)  
    zostoga_cube = read_global_variable(inargs.model, 'zostoga', inargs.run, inargs.project,
                                        manual_file_dict, inargs.ignore_list) 
    if inargs.project == 'cmip5':
        zosga_cube = read_global_variable(inargs.model, 'zosga', inargs.run, inargs.project,
                                          manual_file_dict, inargs.ignore_list) 
        zossga_cube = read_global_variable(inargs.model, 'zossga', inargs.run, inargs.project,
                                           manual_file_dict, inargs.ignore_list)
    else:
        zosga_cube = zossga_cube = None
    wfo_cube = read_spatial_flux(inargs.model, 'wfo', inargs.run, inargs.project,
                                 manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)
    wfonocorr_cube = read_spatial_flux(inargs.model, 'wfonocorr', inargs.run, inargs.project,
                                       manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)
    wfcorr_cube = read_spatial_flux(inargs.model, 'wfcorr', inargs.run, inargs.project,
                                    manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)
    hfds_cube = read_spatial_flux(inargs.model, 'hfds', inargs.run, inargs.project,
                                  manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)
    hfcorr_cube = read_spatial_flux(inargs.model, 'hfcorr', inargs.run, inargs.project,
                                    manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)
    hfgeou_cube = read_spatial_flux(inargs.model, 'hfgeou', inargs.run, inargs.project,
                                    manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)
    rsdt_cube = read_spatial_flux(inargs.model, 'rsdt', inargs.run, inargs.project,
                                  manual_file_dict, inargs.ignore_list)
    rlut_cube = read_spatial_flux(inargs.model, 'rlut', inargs.run, inargs.project,
                                  manual_file_dict, inargs.ignore_list)
    rsut_cube = read_spatial_flux(inargs.model, 'rsut', inargs.run, inargs.project,
                                  manual_file_dict, inargs.ignore_list)
    vsf_cube = read_spatial_flux(inargs.model, 'vsf', inargs.run, inargs.project,
                                 manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)
    vsfcorr_cube = read_spatial_flux(inargs.model, 'vsfcorr', inargs.run, inargs.project,
                                     manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)

    fig = plt.figure(figsize=[15, 25])
    nrows = 5
    ncols = 2
    if masso_cube:
        ax1 = fig.add_subplot(nrows, ncols, 1)
        plot_global_variable(ax1, masso_cube.data, masso_cube.long_name, masso_cube.units, 'green')
    if volo_cube:
        ax2 = fig.add_subplot(nrows, ncols, 2)
        plot_global_variable(ax2, volo_cube.data, volo_cube.long_name, volo_cube.units, 'red')
    if masso_cube and volo_cube:
        ax3 = fig.add_subplot(nrows, ncols, 3)
        units = str(masso_cube.units) + ' / ' + str(volo_cube.units)
        plot_global_variable(ax3, masso_cube.data / volo_cube.data, 'Density', units, 'grey')
    if thetaoga_cube:
        ax4 = fig.add_subplot(nrows, ncols, 4)
        plot_global_variable(ax4, thetaoga_cube.data, thetaoga_cube.long_name, thetaoga_cube.units, 'gold')
    if soga_cube:
        ax5 = fig.add_subplot(nrows, ncols, 5)
        plot_global_variable(ax5, soga_cube.data, soga_cube.long_name, 'g/kg', 'orange')
    if zostoga_cube:
        ax6 = fig.add_subplot(nrows, ncols, 6)
        if zosga_cube:
            ax6.plot(zosga_cube.data, color='purple', label=zosga_cube.long_name, linestyle=':')
        if zossga_cube:
            ax6.plot(zossga_cube.data, color='purple', label=zossga_cube.long_name, linestyle='-.')
        plot_global_variable(ax6, zostoga_cube.data, 'Sea Level',
                             zostoga_cube.units, 'purple', label=zostoga_cube.long_name)
        ax6.legend()
    if wfo_cube:
        ax7 = fig.add_subplot(nrows, ncols, 7)
        if wfcorr_cube:
            ax7.plot(wfcorr_cube.data, color='blue', label=wfcorr_cube.long_name, linestyle=':')
        if wfonocorr_cube:
            ax7.plot(wfonocorr_cube.data, color='blue', label=wfonocorr_cube.long_name, linestyle='-.')
        plot_global_variable(ax7, wfo_cube.data, 'Annual Water Flux Into Ocean', wfo_cube.units, 'blue', label=wfo_cube.long_name)
        ax7.legend()
    if hfds_cube:
        ax8 = fig.add_subplot(nrows, ncols, 8)
        if hfcorr_cube:
            ax8.plot(hfcorr_cube.data, color='teal', label=hfcorr_cube.long_name, linestyle=':')
        if hfgeou_cube:
            ax8.plot(hfcorr_cube.data, color='teal', label=hfgeou_cube.long_name, linestyle='-.')
        plot_global_variable(ax8, hfds_cube.data, 'Annual Heat Flux Into Ocean', hfds_cube.units, 'teal', label=hfds_cube.long_name)
        ax8.legend()
    if rsdt_cube:
        ax9 = fig.add_subplot(nrows, ncols, 9)
        ax9.plot(rsdt_cube.data, color='maroon', label=rsdt_cube.long_name, linestyle=':')
        ax9.plot(rsut_cube.data, color='maroon', label=rlut_cube.long_name, linestyle='-.')
        plot_global_variable(ax9, rlut_cube.data, 'Annual TOA Radiative Fluxes', rlut_cube.units, 'maroon', label=rlut_cube.long_name)
        ax9.legend()
    if vsf_cube or vsfcorr_cube:
        ax10 = fig.add_subplot(nrows, ncols, 10)
        if vsf_cube:
            plot_global_variable(ax10, vsf_cube.data, 'Annual Virtual Salt Fluxes', vsf_cube.units, 'orange', label=vsf_cube.long_name)
        if vsfcorr_cube:
            plot_global_variable(ax10, vsfcorr_cube.data, 'Annual Virtual Salt Fluxes', vsfcorr_cube.units, 'yellow', label=vsfcorr_cube.long_name)


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

    trend_text = '%s: %s %s/yr'  %(name, str(trend), units) 
    trend_list.append(trend_text)


def plot_ohc(ax, masso_data, thetaoga_cube, wfo_cube, hfds_cube, nettoa_data, ylim=None):
    """Plot the OHC timeseries and it's components"""

    # Compulsory variables

    assert thetaoga_cube.units == 'K'
    cp = 4000

    ohc_data = masso_data * thetaoga_cube.data * cp
    ohc_anomaly_data = ohc_data - ohc_data[0]

    thetaoga_anomaly_data = thetaoga_cube.data - thetaoga_cube.data[0]
    thermal_data = cp * masso_data[0] * thetaoga_anomaly_data

    masso_anomaly_data = masso_data - masso_data[0]
    barystatic_data = cp * thetaoga_cube.data[0] * masso_anomaly_data

    nettoa_cumsum_data = numpy.cumsum(nettoa_data)
    nettoa_cumsum_anomaly = nettoa_cumsum_data - nettoa_cumsum_data[0]

    calc_trend(ohc_anomaly_data, 'OHC', 'J')
    calc_trend(thermal_data, 'thermal OHC', 'J')
    calc_trend(barystatic_data, 'barystatic OHC', 'J')
    calc_trend(nettoa_cumsum_anomaly, 'cumulative netTOA', 'J')

    ax.grid(linestyle=':')
    ax.plot(ohc_anomaly_data, color='black', label='OHC anomaly($\Delta H$)')
    ax.plot(thermal_data, color='red', label='thermal OHC anomaly ($c_p M_0 \Delta T$)')
    ax.plot(barystatic_data, color='blue', label='barystatic OHC anomaly ($c_p T_0 \Delta M$)')
    ax.plot(nettoa_cumsum_anomaly, color='gold', linestyle='--', label='cumulative net TOA radiative flux')

    # Optional data

    if hfds_cube:
        hfds_cumsum_data = numpy.cumsum(hfds_cube.data)
        hfds_cumsum_anomaly = hfds_cumsum_data - hfds_cumsum_data[0]
        calc_trend(hfds_cumsum_anomaly, 'cumulative hfds', 'J')
        ax.plot(hfds_cumsum_anomaly, color='red', linestyle='--', label='cumulative surface heat flux')

    if wfo_cube:
        wfo_cumsum_data = numpy.cumsum(wfo_cube.data)
        wfo_cumsum_anomaly = wfo_cumsum_data - wfo_cumsum_data[0]
        wfo_inferred_barystatic = cp * thetaoga_cube.data[0] * wfo_cumsum_anomaly
        ax.plot(wfo_inferred_barystatic, color='blue', linestyle='--', label='cumulative surface freshwater flux')
    
    if hfds_cube and wfo_cube:
        ax.plot(hfds_cumsum_anomaly + wfo_inferred_barystatic, color='black', linestyle='--', label='inferred OHC anomaly from suface fluxes')

    if ylim:
        ax.set_ylim(ylim[0] * 1e24, ylim[1] * 1e24)

    ax.set_title('Heat Budget')
    ax.set_xlabel('year')
    ax.set_ylabel('equivalent change in ocean heat content (J)')
    ax.yaxis.major.formatter._useMathText = True
    ax.legend()


def plot_sea_level(ax, zostoga_cube, zosga_cube, zossga_cube, masso_data,
                   wfo_cube, masso_from_soga, ocean_area, density=1035, ylim=None):
    """Plot the sea level timeseries and it's components"""

    # Compulsory variables

    masso_anomaly_data = masso_data - masso_data[0]
    sea_level_anomaly_from_masso = sea_level_from_mass(masso_anomaly_data, ocean_area, density)
    sea_level_anomaly_from_soga = sea_level_from_mass(masso_from_soga, ocean_area, density)

    calc_trend(masso_anomaly_data, 'global ocean mass', 'kg')
    calc_trend(sea_level_anomaly_from_masso, 'global ocean mass', 'm')

    ax.grid(linestyle=':')
    ax.plot(sea_level_anomaly_from_masso, color='blue', label='change in global ocean mass')
    ax.plot(sea_level_anomaly_from_soga, color='teal', linestyle=':', label='global mean salinity anomaly')

    # Optional variables
    if wfo_cube:
        wfo_cumsum_data = numpy.cumsum(wfo_cube.data)
        wfo_cumsum_anomaly = wfo_cumsum_data - wfo_cumsum_data[0]
        sea_level_anomaly_from_wfo = sea_level_from_mass(wfo_cumsum_anomaly, ocean_area, density)
        calc_trend(wfo_cumsum_anomaly, 'cumulative wfo', 'kg')
        ax.plot(sea_level_anomaly_from_wfo, color='blue', linestyle='--', label='cumulative surface freshwater flux')

    if zostoga_cube:
        zostoga_anomaly = zostoga_cube.data - zostoga_cube.data[0]
        calc_trend(zostoga_anomaly, 'thermosteric sea level', 'm')
        ax.plot(zostoga_anomaly, color='purple', linestyle='--', label='change in thermosteric sea level')

    if zosga_cube and zossga_cube:
        zosga_anomaly = zosga_cube.data - zosga_cube.data[0]
        zossga_anomaly = zossga_cube.data - zossga_cube.data[0]
        zosbary_anomaly = zosga_anomaly - zossga_anomaly
        calc_trend(zosbary_anomaly, 'barystatic sea level', 'm')
        ax.plot(zosbary_anomaly, color='purple', label='change in barystatic sea level')
    
    if ylim:
        ax.set_ylim(ylim[0], ylim[1])

    ax.set_title('Water Budget')
    ax.set_xlabel('year')
    ax.set_ylabel('equivalent change in global sea level (m)')
    ax.yaxis.major.formatter._useMathText = True
    ax.legend()    


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
        file_dict[variable] = files

    return file_dict 


def plot_comparison(inargs):
    """Plot the budget comparisons."""

    fig = plt.figure(figsize=[16, 8])
    nrows = 1
    ncols = 2

    manual_file_dict = get_manual_file_dict(inargs.manual_files)
    masso_cube = read_global_variable(inargs.model, 'masso', inargs.run, inargs.project,
                                      manual_file_dict, inargs.ignore_list)
    volo_cube = read_global_variable(inargs.model, 'volo', inargs.run, inargs.project,
                                     manual_file_dict, inargs.ignore_list)
    if inargs.volo:
        masso_data = volo_cube.data * 1035
    else:
        masso_data = masso_cube.data

    thetaoga_cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project,
                                         manual_file_dict, inargs.ignore_list)
    zostoga_cube = read_global_variable(inargs.model, 'zostoga', inargs.run, inargs.project,
                                        manual_file_dict, inargs.ignore_list)
    if inargs.project == 'cmip5':
        zosga_cube = read_global_variable(inargs.model, 'zosga', inargs.run, inargs.project,
                                          manual_file_dict, inargs.ignore_list)
        zossga_cube = read_global_variable(inargs.model, 'zossga', inargs.run, inargs.project,
                                           manual_file_dict, inargs.ignore_list) 
    else:
        zosga_cube = zossga_cube = None

    soga_cube = read_global_variable(inargs.model, 'soga', inargs.run, inargs.project,
                                     manual_file_dict, inargs.ignore_list)
    s_orig = numpy.ones(soga_cube.data.shape[0]) * soga_cube.data[0]
    m_orig = numpy.ones(masso_data.shape[0]) * masso_data[0]
    masso_from_soga = numpy.fromiter(map(delta_masso_from_soga, s_orig, soga_cube.data, m_orig), float)
    soga_from_masso = numpy.fromiter(map(delta_soga_from_masso, m_orig, masso_data, s_orig), float) 
    calc_trend(soga_from_masso, 'global ocean mass', 'g/kg')
    calc_trend(soga_cube.data, 'global mean salinity', 'g/kg')

    wfo_cube = read_spatial_flux(inargs.model, 'wfo', inargs.run, inargs.project,
                                 manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)
    hfds_cube = read_spatial_flux(inargs.model, 'hfds', inargs.run, inargs.project,
                                  manual_file_dict, inargs.ignore_list, chunk=inargs.chunk)

    rsdt_cube = read_spatial_flux(inargs.model, 'rsdt', inargs.run, inargs.project,
                                  manual_file_dict, inargs.ignore_list)
    rlut_cube = read_spatial_flux(inargs.model, 'rlut', inargs.run, inargs.project,
                                  manual_file_dict, inargs.ignore_list)
    rsut_cube = read_spatial_flux(inargs.model, 'rsut', inargs.run, inargs.project,
                                  manual_file_dict, inargs.ignore_list)
    nettoa_data = rsdt_cube.data - rlut_cube.data - rsut_cube.data

    area_file = clef_search(inargs.model, 'areacello', 'r0i0p0', inargs.project)
    if not area_file:
        area_file = clef_search(inargs.model, 'areacello', 'r0i0p0', inargs.project, experiment='historical')
    areacello_cube = iris.load_cube(area_file[0])
    ocean_area = areacello_cube.data.sum()

    ax1 = fig.add_subplot(nrows, ncols, 1)
    plot_ohc(ax1, masso_data, thetaoga_cube, wfo_cube, hfds_cube, nettoa_data, ylim=inargs.ohc_ylim)

    ax2 = fig.add_subplot(nrows, ncols, 2)
    plot_sea_level(ax2, zostoga_cube, zosga_cube, zossga_cube, masso_data, wfo_cube,
                   masso_from_soga, ocean_area, ylim=inargs.sealevel_ylim)


def main(inargs):
    """Run the program."""

    if inargs.plot_type == 'raw':
        plot_raw(inargs)
    else:
        plot_comparison(inargs)

    plt.subplots_adjust(top=0.92)
    title = '%s (%s), %s, piControl'  %(inargs.model, inargs.project, inargs.run)
    plt.suptitle(title)
    plt.savefig(inargs.outfile, bbox_inches='tight')
    
    processed_files.append(trend_list)
    flat_list = [item for sublist in processed_files for item in sublist]
    flat_list = list(set(flat_list))
    flat_list.sort()
    log_text = cmdprov.new_log(git_repo=repo_dir, extra_notes=flat_list)
    log_file = re.sub('.png', '.met', inargs.outfile)
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

    parser.add_argument("plot_type", type=str, choices=('raw', 'comparison'), help="Plot type")
    parser.add_argument("model", type=str, help="Model (use dots not dashes between numbers in model names)")
    parser.add_argument("run", type=str, help="Run (e.g. r1i1p1)")
    parser.add_argument("project", type=str, choices=('cmip5', 'cmip6'), help="Project")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--volo", action="store_true", default=False,
                        help="Use volo to calculate masso (useful for boussinesq models)")
    parser.add_argument("--chunk", action="store_true", default=False,
                        help="Chunk annual mean calculation for spatial variables (useful for boussinesq models)")

    parser.add_argument("--manual_files", type=str, action="append", nargs='*', default=[],
                        help="Use these manually entered files instead of the clef search")
    parser.add_argument("--ignore_list", type=str, nargs='*', default=[],
                        choices=('rsdt', 'rsut', 'rlut'),
                        help="Variables to ignore")
    parser.add_argument("--ohc_ylim", type=float, nargs=2, metavar=('LOWER_LIMIT', 'UPPER_LIMIT'), default=None,
                        help="y-axis limits for OHC plot (*1e24) [default = auto]")
    parser.add_argument("--sealevel_ylim", type=float, nargs=2, metavar=('LOWER_LIMIT', 'UPPER_LIMIT'), default=None,
                        help="y-axis limits for sea level plot [default = auto]")
    

    args = parser.parse_args()             
    main(args)
