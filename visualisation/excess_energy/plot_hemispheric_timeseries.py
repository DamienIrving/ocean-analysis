"""
Filename:     plot_hemispheric_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ensemble aggregated  hemispheric timeseries

"""

# Import general Python modules

import sys, os, pdb, re
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import iris.plot as iplt
import matplotlib.pyplot as plt
import seaborn

import cmdline_provenance as cmdprov

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

colors = {'ohc': 'blue', 'hfds': 'orange', 'rndt': 'red'}

names = {'ohc': 'ocean heat content',
         'hfds': 'Downward Heat Flux at Sea Water Surface',
         'rndt': 'TOA Incoming Net Radiation'}


def ensemble_aggregate(cube_list, operator):
    """Calculate the ensemble mean."""

    aggregators = {'mean': iris.analysis.MEAN, 'median': iris.analysis.MEDIAN}

    var_name = cube_list[0].var_name
    for cube in cube_list:
        cube.var_name = var_name

    if len(cube_list) > 1:
        equalise_attributes(cube_list)
        timeseries.equalise_time_axes(cube_list)
        ensemble_cube = cube_list.merge_cube()
        ensemble_agg = ensemble_cube.collapsed('ensemble_member', aggregators[operator])
    else:
        ensemble_agg = cube_list[0]

    return ensemble_agg


def calc_anomaly(cube):
    """Calculate the anomaly."""
    
    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    
    return anomaly


def read_hemisphere_data(file_pairs, variable, time_constraint, ensagg):
    """Read the data for a particular variable."""
    
    hemispheres = ['nh', 'sh']
    cube_list = {'nh': iris.cube.CubeList([]), 'sh': iris.cube.CubeList([])}
    for ensnum, file_pair in enumerate(file_pairs):
        new_aux_coord = iris.coords.AuxCoord(ensnum, long_name='ensemble_member', units='no_unit')
        for hemnum, hemisphere in enumerate(hemispheres):
            infile = file_pair[hemnum]
            print(infile)
            var =  '%s %s sum' %(names[variable], hemisphere)
            cube = iris.load_cube(infile, var & time_constraint)
            if variable == 'ohc':
                cube = calc_anomaly(cube)
            cube.add_aux_coord(new_aux_coord)
            cube.cell_methods = ()
            cube_list[hemisphere].append(cube)

    ensagg_nh_cube = ensemble_aggregate(cube_list['nh'], ensagg)
    ensagg_sh_cube = ensemble_aggregate(cube_list['sh'], ensagg)

    return ensagg_nh_cube, ensagg_sh_cube


def read_guide_data(infiles, variable, time_constraint, ensagg):
    """Read the data for the guidelines."""
    
    cube_list = iris.cube.CubeList([])
    for ensnum, infile in enumerate(infiles):
        new_aux_coord = iris.coords.AuxCoord(ensnum, long_name='ensemble_member', units='no_unit')
        print(infile)
        var =  '%s globe sum' %(names[variable])
        cube = iris.load_cube(infile, var & time_constraint)
        if variable == 'ohc':
            cube = calc_anomaly(cube)
        cube.add_aux_coord(new_aux_coord)
        cube.cell_methods = ()
        cube_list.append(cube)

    ensagg_cube = ensemble_aggregate(cube_list, ensagg)
    nh_guide = ensagg_cube * 0.41
    sh_guide = ensagg_cube * 0.59

    return nh_guide, sh_guide


def main(inargs):
    """Run the program."""

    metadata_dict = {}
    time_constraint = gio.get_time_constraint([inargs.start_date, inargs.end_date])

    fig = plt.figure(figsize=[11, 10])

    if inargs.rndt_files:
        rndt_nh, rndt_sh = read_hemisphere_data(inargs.rndt_files, 'rndt', time_constraint, inargs.ensagg)
        iplt.plot(rndt_nh, label='netTOA, NH', color='red', linestyle='solid')
        iplt.plot(rndt_sh, label='netTOA, SH', color='red', linestyle='dashed')

    if inargs.hfds_files:
        hfds_nh, hfds_sh = read_hemisphere_data(inargs.hfds_files, 'hfds', time_constraint, inargs.ensagg)
        iplt.plot(hfds_nh, label='OHU, NH', color='orange', linestyle='solid')
        iplt.plot(hfds_sh, label='OHU, SH', color='orange', linestyle='dashed')

    if inargs.ohc_files:
        ohc_nh, ohc_sh = read_hemisphere_data(inargs.ohc_files, 'ohc', time_constraint, inargs.ensagg)
        iplt.plot(ohc_nh, label='OHC, NH', color='blue', linestyle='solid')
        iplt.plot(ohc_sh, label='OHC, SH', color='blue', linestyle='dashed')

    if inargs.ohc_guide_files:
        guide_nh, guide_sh = read_guide_data(inargs.ohc_guide_files, 'ohc', time_constraint, inargs.ensagg)
        iplt.plot(guide_nh, label='OHC guide, NH', color='0.5', linestyle='solid')
        iplt.plot(guide_sh, label='OHC guide, SH', color='0.5', linestyle='dashed')

    plt.legend()

    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)

    log_text = cmdprov.new_log(git_repo=repo_dir)  # infile_history={nh_file: history}
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot hemisperhic accumulation of OHC, hfds and rndt'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="output file")
    parser.add_argument("start_date", type=str, help="Start date (e.g. 1861-01-01)")
    parser.add_argument("end_date", type=str, help="End date (e.g. 2005-12-31)")

    parser.add_argument("--rndt_files", type=str, nargs=2, action='append', default=[],
                        help="netTOA file pair for a given model (NH, SH)")                     
    parser.add_argument("--hfds_files", type=str, nargs=2, action='append', default=[],
                        help="OHU file pair for a given model (NH, SH)")
    parser.add_argument("--ohc_files", type=str, nargs=2, action='append', default=[],
                        help="OHC file pair for a given model (NH, SH)")
                            
    parser.add_argument("--ohc_guide_files", type=str, nargs='*', default=None,
                        help="global files for OHC guidelines to be plotted")

    parser.add_argument("--ensagg", type=str, default='median', choices=('mean', 'median'),
                        help="Ensemble mean or median [default=median]")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")


    args = parser.parse_args()             
    main(args)
