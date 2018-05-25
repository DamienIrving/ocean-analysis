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


def plot_files(ohc_file, hfds_file, rndt_file, hemisphere, 
               metadata_dict, results_dict, time_constraint, dedrifted=True):
    """ """

    ohc_var =  'ocean heat content %s sum'  %(hemisphere)
    ohc_cube = iris.load_cube(ohc_file, ohc_var & time_constraint)
    metadata_dict[ohc_file] = ohc_cube.attributes['history']

    hfds_var = 'Downward Heat Flux at Sea Water Surface %s sum' %(hemisphere)
    hfds_cube = iris.load_cube(hfds_file, hfds_var & time_constraint)
    metadata_dict[hfds_file] = hfds_cube.attributes['history']

    rndt_var = 'TOA Incoming Net Radiation %s sum' %(hemisphere)
    rndt_cube = iris.load_cube(rndt_file, rndt_var & time_constraint)
    metadata_dict[rndt_file] = rndt_cube.attributes['history']
        
    ohc_anomaly = calc_anomaly(ohc_cube)
    hfds_anomaly = calc_anomaly(hfds_cube)
    rndt_anomaly = calc_anomaly(rndt_cube)

    hfds_label = get_hfds_label(hfds_file)
    if dedrifted and (hemisphere == 'globe'):
        iplt.plot(ohc_anomaly, label='ocean heat content', color='blue')
        iplt.plot(hfds_anomaly, label=hfds_label, color='orange')
        iplt.plot(rndt_anomaly, label='TOA net radiation, cumulative sum', color='red')
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
        results_dict[hemisphere + ' ' + hfds_label + ' change (last minus first):'] = hfds_anomaly[-1]
        results_dict[hemisphere + ' ocean heat content change (last minus first):'] = ohc_anomaly[-1]

    return metadata_dict, results_dict, ohc_cube


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


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    metadata_dict = {}
    results_dict = {}
    fig, ax = plt.subplots()

    group_characteristics = [('globe', True), ('nh', True), ('sh', True), ('globe', False)]
    infiles = [inargs.globe_files, inargs.nh_files, inargs.sh_files, inargs.orig_files]
    for index, file_group in enumerate(infiles):
        if file_group:
            hemisphere, dedrifted = group_characteristics[index]
            ohc_file, hfds_file, rndt_file = file_group
            metadata_dict, results_dict, ohc_cube = plot_files(ohc_file, hfds_file, rndt_file, hemisphere,
                                                               metadata_dict, results_dict, time_constraint,
                                                               dedrifted=dedrifted)

    plt.ylabel(ohc_cube.units)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    ax.yaxis.major.formatter._useMathText = True

    #plt.ylim(-1e+23, 7e+23)
    ymin, ymax = plt.ylim()
    print('ymin:', ymin)
    print('ymax:', ymax)

    title, legloc = get_title(ohc_cube)
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
    
    parser.add_argument("--globe_files", type=str, nargs=3, default=None, 
                        help="globally integrated OHC file, hfds file and netTOA file (in that order) (dedrifted)")
    parser.add_argument("--nh_files", type=str, nargs=3, default=None, 
                        help="NH integrated OHC file, hfds file and netTOA file (in that order) (dedrifted)")
    parser.add_argument("--sh_files", type=str, nargs=3, default=None, 
                        help="SH integrated OHC file, hfds file and netTOA file (in that order) (dedrifted)")

    parser.add_argument("--hfbasin_file", type=str, default=None, 
                        help="hfbasin file (to include in text output)") 

    parser.add_argument("--orig_files", type=str, nargs=3, default=None, 
                        help="globally integrated OHC file, hfds file and netTOA file (in that order), non-dedrifted")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=None, help="Time bounds")

    args = parser.parse_args()             
    main(args)
