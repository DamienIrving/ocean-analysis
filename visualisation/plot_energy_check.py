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

def convert_to_joules(cube):
    """Convert units to Joules"""
    
    assert 'W' in str(cube.units)
    assert 'days' in str(cube.coord('time').units)
    
    time_span_days = cube.coord('time').bounds[:, 1] - cube.coord('time').bounds[:, 0]
    time_span_seconds = time_span_days * 60 * 60 * 24
    
    cube.data = cube.data * uconv.broadcast_array(time_span_seconds, 0, cube.shape)
    cube.units = str(cube.units).replace('W', 'J')
    
    return cube


def calc_anomaly(cube):
    """Calculate the anomaly."""
    
    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    
    return anomaly


def calc_cumsum(cube):
    """Calculate the cumulative sum."""
    
    new_cube = cube.copy()
    new_cube.data = numpy.cumsum(new_cube.data)
    
    return new_cube


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


def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)
    metadata_dict = {}

    ohc_cube = iris.load_cube(inargs.ohc_file, 'ocean heat content globe sum' & time_constraint)
    metadata_dict[inargs.ohc_file] = ohc_cube.attributes['history']

    hfds_cube_W = iris.load_cube(inargs.hfds_file, 'Downward Heat Flux at Sea Water Surface globe sum' & time_constraint)
    metadata_dict[inargs.hfds_file] = hfds_cube_W.attributes['history']

    rndt_cube_W = iris.load_cube(inargs.rndt_file, 'TOA Incoming Net Radiation globe sum' & time_constraint)
    metadata_dict[inargs.rndt_file] = rndt_cube_W.attributes['history']
    
    hfds_cube_J = convert_to_joules(hfds_cube_W)
    rndt_cube_J = convert_to_joules(rndt_cube_W)
    
    ohc_anomaly = calc_anomaly(ohc_cube)
    hfds_anomaly = calc_anomaly(hfds_cube_J)
    rndt_anomaly = calc_anomaly(rndt_cube_J)

    hfds_cumsum = calc_cumsum(hfds_anomaly)
    rndt_cumsum = calc_cumsum(rndt_anomaly)    

    fig, ax = plt.subplots()

    hfds_label = get_hfds_label(inargs.hfds_file)
    iplt.plot(ohc_anomaly, label='ocean heat content')
    iplt.plot(hfds_cumsum, label=hfds_label)
    iplt.plot(rndt_cumsum, label='TOA net radiation, cumulative sum')

    plt.ylabel(ohc_cube.units)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True, useOffset=False)
    ax.yaxis.major.formatter._useMathText = True

    #plt.ylim(-6e+23, 8e+23)
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

    parser.add_argument("ohc_file", type=str, help="globally integrated OHC file")
    parser.add_argument("hfds_file", type=str, help="globally integrated ocean surface downward heat flux file")   
    parser.add_argument("rndt_file", type=str, help="globally integrated TOA net flux file")    
    parser.add_argument("outfile", type=str, help="output file")                               
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'),
                        help="Time bounds for historical period [default = 1861-2005]")

    args = parser.parse_args()             
    main(args)
