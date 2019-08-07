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
         'hfgeou' : 'upward_geothermal_heat_flux_at_sea_floor'}


def clef_search(model, variable, ensemble, project):
    """Use Clef to search for data files"""

    table = 'fx' if variable == 'areacello' else 'Omon'
    constraints = {'variable': variable, 'model': model, 'table': table,
                   'experiment': 'piControl', 'ensemble': ensemble}

    results = clef.code.search(session, project=project, **constraints)
    assert len(results) < 2
    if len(results) == 1:
        filenames = results[0]['filenames']
        filenames.sort()
        filedir = results[0]['pdir']
        file_list = [filedir + '/' + filename for filename in filenames]
        version = results[0]['version']
        file_version_list = [filedir + '/' + filename + ', ' + str(version) for filename in filenames]
        processed_files.append(file_version_list)
    else:
        file_list = []

    return file_list


def read_global_variable(model, variable, ensemble, project):
    """Read data for a global variable"""
    
    file_list = clef_search(model, variable, ensemble, project) 
    
    if file_list:
        cube, history = gio.combine_files(file_list, names[variable])
        if variable == 'soga':
            cube = gio.salinity_unit_check(cube)
        cube = timeseries.convert_to_annual(cube)
    else:
        cube = None
        
    return cube


def read_spatial_flux(model, variable, ensemble, project):
    """Read spatial flux data and convert to global value"""
    
    file_list = clef_search(model, variable, ensemble, project)
    area_file = clef_search(model, 'areacello', 'r0i0p0', project)[0]
    
    if file_list and area_file:
        cube, history = gio.combine_files(file_list, names[variable])
        cube = timeseries.convert_to_annual(cube)

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

    ax.plot(data, color=color, label=label)
    ax.set_title(long_name)
    ax.set_xlabel('year')
    ax.set_ylabel(units)
    ax.ticklabel_format(useOffset=False)


def main(inargs):
    """Run the program."""

    masso_cube = read_global_variable(inargs.model, 'masso', inargs.run, inargs.project)
    volo_cube = read_global_variable(inargs.model, 'volo', inargs.run, inargs.project)
    thetaoga_cube = read_global_variable(inargs.model, 'thetaoga', inargs.run, inargs.project)
    soga_cube = read_global_variable(inargs.model, 'soga', inargs.run, inargs.project)  
    zostoga_cube = read_global_variable(inargs.model, 'zostoga', inargs.run, inargs.project) 
    if inargs.project == 'cmip5':
        zosga_cube = read_global_variable(inargs.model, 'zosga', inargs.run, inargs.project) 
        zossga_cube = read_global_variable(inargs.model, 'zossga', inargs.run, inargs.project)
    else:
        zosga_cube = zossga_cube = None
    wfo_cube = read_spatial_flux(inargs.model, 'wfo', inargs.run, inargs.project)
    wfonocorr_cube = read_spatial_flux(inargs.model, 'wfonocorr', inargs.run, inargs.project)
    wfcorr_cube = read_spatial_flux(inargs.model, 'wfcorr', inargs.run, inargs.project)
    hfds_cube = read_spatial_flux(inargs.model, 'hfds', inargs.run, inargs.project)
    hfcorr_cube = read_spatial_flux(inargs.model, 'hfcorr', inargs.run, inargs.project)
    hfgeou_cube = read_spatial_flux(inargs.model, 'hfgeou', inargs.run, inargs.project)

    fig = plt.figure(figsize=[15, 20])
    nrows = 4
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

    # Save output
    plt.subplots_adjust(top=0.95)
    title = '%s (%s), %s, piControl'  %(inargs.model, inargs.project, inargs.run)
    plt.suptitle(title)
    plt.savefig(inargs.outfile, bbox_inches='tight')
    
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
 
    parser.add_argument("model", type=str, help="Model (use dots not dashes between numbers in model names)")
    parser.add_argument("run", type=str, help="Run (e.g. r1i1p1)")
    parser.add_argument("project", type=str, choices=('cmip5', 'cmip6'), help="Project")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()             
    main(args)
