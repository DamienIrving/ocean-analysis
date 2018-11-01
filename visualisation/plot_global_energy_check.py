"""
Filename:     plot_global_energy_check.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ohc, hfds and rndt

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
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


def get_title(cube, nexp):
    """Get the plot title."""

    if nexp == 1:
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

    else:
        title = None
        legloc = 2

    return title, legloc


def read_data(ohc_file, hfds_file, rndt_file, hemisphere, metadata_dict, time_constraint, ensemble_number, dedrifted=True):
    """Read the data files."""

    new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')

    ohc_var =  'ocean heat content %s sum'  %(hemisphere)
    ohc_cube = iris.load_cube(ohc_file, ohc_var & time_constraint)
    ohc_cube.cell_methods = ()
    ohc_cube.add_aux_coord(new_aux_coord)

    hfds_var = 'Downward Heat Flux at Sea Water Surface %s sum' %(hemisphere)
    hfds_cube = iris.load_cube(hfds_file, hfds_var & time_constraint)
    hfds_cube.cell_methods = ()
    hfds_cube.add_aux_coord(new_aux_coord)

    rndt_var = 'TOA Incoming Net Radiation %s sum' %(hemisphere)
    rndt_cube = iris.load_cube(rndt_file, rndt_var & time_constraint)
    rndt_cube.cell_methods = ()
    rndt_cube.add_aux_coord(new_aux_coord)
        
    ohc_anomaly = calc_anomaly(ohc_cube)
    hfds_anomaly = calc_anomaly(hfds_cube)
    rndt_anomaly = calc_anomaly(rndt_cube)
    
    if (ensemble_number == 0) and (hemisphere == 'globe'):
        metadata_dict[ohc_file] = ohc_cube.attributes['history']
        metadata_dict[hfds_file] = hfds_cube.attributes['history']
        metadata_dict[rndt_file] = rndt_cube.attributes['history']

    return ohc_anomaly, hfds_anomaly, rndt_anomaly, metadata_dict


def plot_data(ohc_anomaly, hfds_anomaly, rndt_anomaly, results_dict, hemisphere, dedrifted=True):
    """ """

    if dedrifted and (hemisphere == 'globe'):
        iplt.plot(ohc_anomaly, label='OHC', color='blue')
        iplt.plot(hfds_anomaly, label='OHU', color='orange')
        iplt.plot(rndt_anomaly, label='netTOA', color='red')
    elif dedrifted and (hemisphere == 'nh'):
        iplt.plot(ohc_anomaly, color='blue', linestyle=':')
        iplt.plot(hfds_anomaly, color='orange', linestyle=':')
        iplt.plot(rndt_anomaly, color='red', linestyle=':')
    elif dedrifted and (hemisphere == 'sh'):
        iplt.plot(ohc_anomaly, color='blue', linestyle='--')
        iplt.plot(hfds_anomaly, color='orange', linestyle='--')
        iplt.plot(rndt_anomaly, color='red', linestyle='--')
    else:
        iplt.plot(ohc_anomaly, color='blue', linestyle='--')
        iplt.plot(hfds_anomaly, color='orange', linestyle='--')
        iplt.plot(rndt_anomaly, color='red', linestyle='--')

    if dedrifted:
        results_dict[hemisphere + ' TOA net radiation, cumulative sum (last minus first):'] = rndt_anomaly[-1]
        results_dict[hemisphere + ' surface heat flux, cumulative (last minus first):'] = hfds_anomaly[-1]
        results_dict[hemisphere + ' ocean heat content change (last minus first):'] = ohc_anomaly[-1]

    return results_dict


def write_result(outfile, results_dict):
    """Write results to file"""
    
    fout = open(outfile.replace('.png', '.txt'), 'w')
    for label, value in results_dict.items():
        fout.write(label + ' ' + str(value.data) + '\n')
    fout.close()


def get_equatorial_transport(hfbasin_file, results_dict, metadata_dict, time_constraint):
    """Calculate the equatorial transport"""

    cube = iris.load_cube(hfbasin_file, 'northward_ocean_heat_transport' & time_constraint)
    metadata_dict[hfbasin_file] = cube.attributes['history']

    equator_cube = cube.extract(iris.Constraint(latitude=0))

    anomaly = calc_anomaly(equator_cube)
    results_dict['equatorial northward ocean heat transport, cumulative sum (last minus first):'] = anomaly[-1]

    return results_dict


def equalise_time_axes(cube_list):
    """Make all the time axes the same."""

    iris.util.unify_time_units(cube_list)
    reference_cube = cube_list[0]
    new_cube_list = iris.cube.CubeList([])
    for cube in cube_list:
        assert len(cube.coord('time').points) == len(reference_cube.coord('time').points)
        cube.coord('time').points = reference_cube.coord('time').points
        cube.coord('time').bounds = reference_cube.coord('time').bounds
        cube.coord('time').units = reference_cube.coord('time').units
        cube.coord('time').attributes = reference_cube.coord('time').attributes
        new_cube_list.append(cube)
    
    return new_cube_list


def ensemble_agg(cube_list):
    """Calculate the ensemble aggregate."""

    if len(cube_list) > 1:
        equalise_attributes(cube_list)
        cube_list = equalise_time_axes(cube_list)
        ensemble_cube = cube_list.merge_cube()
        ensemble_agg = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)
    else:
        ensemble_agg = cube_list[0]

    return ensemble_agg


def sort_inputs(inargs):
    """ """

    region_characteristics = []
    infiles = []
    region_options = [('globe', True), ('nh', True), ('sh', True), ('globe', False)]
    for index, file_group in enumerate([inargs.globe_files, inargs.nh_files, inargs.sh_files, inargs.orig_files]):
        if file_group:
            region_characteristics.append(region_options[index])
            infiles.append(file_group)

    return region_characteristics, infiles


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    metadata_dict = {}
    results_dict = {}
    fig, ax = plt.subplots()

    region_characteristics, infiles = sort_inputs(inargs)
    for region_index, region_group in enumerate(infiles):
        if region_group:
            hemisphere, dedrifted = region_characteristics[region_index]
            ohc_list = iris.cube.CubeList([])
            hfds_list = iris.cube.CubeList([])
            rndt_list = iris.cube.CubeList([])
            for model_index, model_group in enumerate(region_group):
                ohc_file, hfds_file, rndt_file = model_group
                ohc_anomaly, hfds_anomaly, rndt_anomaly, metadata_dict = read_data(ohc_file, hfds_file, rndt_file, hemisphere,
                                                                                   metadata_dict, time_constraint,
                                                                                   model_index, dedrifted=dedrifted)
                ohc_list.append(ohc_anomaly)
                hfds_list.append(hfds_anomaly)
                rndt_list.append(rndt_anomaly)

            ohc_ensemble = ensemble_agg(ohc_list)
            hfds_ensemble = ensemble_agg(hfds_list)
            rndt_ensemble = ensemble_agg(rndt_list)

            results_dict = plot_data(ohc_ensemble, hfds_ensemble, rndt_ensemble, results_dict, hemisphere, dedrifted=dedrifted)

    plt.ylabel(ohc_anomaly.units)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    ax.yaxis.major.formatter._useMathText = True

    if inargs.ylim:
        lower, upper = inargs.ylim
        plt.ylim(lower * 1e+23, upper * 1e+23)
    ymin, ymax = plt.ylim()
    print('ymin:', ymin)
    print('ymax:', ymax)

    title, legloc = get_title(ohc_anomaly, len(inargs.globe_files))
    if title:
        plt.title(title)
    plt.legend(loc=legloc)

    if inargs.hfbasin_file:
        results_dict = get_equatorial_transport(inargs.hfbasin_file, results_dict,
                                                metadata_dict, time_constraint)

    write_result(inargs.outfile, results_dict)
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

    parser.add_argument("outfile", type=str, help="output file")                               
    
    parser.add_argument("--globe_files", type=str, nargs=3, action='append', default=[],
                        help="globally integrated OHC file, hfds file and netTOA file (in that order) (dedrifted)")
    parser.add_argument("--nh_files", type=str, nargs=3, action='append', default=[],
                        help="NH integrated OHC file, hfds file and netTOA file (in that order) (dedrifted)")
    parser.add_argument("--sh_files", type=str, nargs=3, action='append', default=[],
                        help="SH integrated OHC file, hfds file and netTOA file (in that order) (dedrifted)")

    parser.add_argument("--hfbasin_file", type=str, default=None, 
                        help="hfbasin file (to include in text output)") 

    parser.add_argument("--orig_files", type=str, nargs=3, action='append', default=[], 
                        help="globally integrated OHC file, hfds file and netTOA file (in that order), non-dedrifted")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=None, help="Time bounds")
    parser.add_argument("--ylim", type=float, nargs=2, default=None,
                        help="y limits (x 10^23)")

    args = parser.parse_args()             
    main(args)
