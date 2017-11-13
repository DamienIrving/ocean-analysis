"""
Filename:     plot_global_mean_tas.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  

"""

# Import general Python modules

import sys, os, pdb
import argparse
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import seaborn
import numpy

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
               
def get_file_info(infile):
    """Strip information from the file name.

    e.g. tas-global-mean_Ayr_GFDL-CM3_historical_r1i1p1_all.nc

    """

    file_components = infile.split('/')
    fname = file_components[-1]
    metric, realm, model, experiment, mip, time = fname.split('_')
    assert realm == 'Ayr'

    if experiment == 'historicalMisc':
        experiment = 'historicalAA'
    assert experiment in ['historical', 'historicalGHG', 'historicalAA']

    if metric == 'tas-ita':
        metric_name = 'interhemispheric surface temperature asymmetry'
    elif metric == 'tas-global-mean':
        metric_name = 'global mean surface temperature'

    return experiment, model, metric_name


def sort_list(old_list):
    """Sort a list alphabetically"""

    unique = set(old_list)
    new_list = sorted(unique, key=str.lower)

    return new_list


def append_data(data_list, data_dict, model, experiment):
    """Append data to an experiment list."""

    try:
        data_list.append(data_dict[(model, experiment)])        
    except KeyError:
        data_list.append(0)

    return data_list


def order_data(trend_dict, models):
    """Order the data and put in experiment groups."""

    hist_data_list = []
    ghg_data_list = []
    aa_data_list = []
    for model in models:
        append_data(hist_data_list, trend_dict, model, 'historical')
        append_data(ghg_data_list, trend_dict, model, 'historicalGHG')
        append_data(aa_data_list, trend_dict, model, 'historicalAA')

    return hist_data_list, ghg_data_list, aa_data_list      


def main(inargs):
    """Run the program."""

    trend_dict = {}
    models = []
    for infile in inargs.infiles:
        cube = iris.load_cube(infile)
        experiment, model, metric_name = get_file_info(infile)
        trend_dict[(model, experiment)] = timeseries.calc_trend(cube, per_yr=True)
        models.append(model)
        
    models = sort_list(models)    
    hist_data, ghg_data, aa_data = order_data(trend_dict, models)
    ant_data = numpy.array(ghg_data) + numpy.array(aa_data)

    ind = numpy.arange(len(hist_data))  # the x locations for the groups
    width = 0.2       # the width of the bars

    fig, ax = plt.subplots(figsize=(20, 8))
    rects1 = ax.bar(ind, ghg_data, width, color='red')
    rects2 = ax.bar(ind + width, aa_data, width, color='blue')
    rects3 = ax.bar(ind + 2 * width, ant_data, width, color='purple')
    rects4 = ax.bar(ind + 3 * width, hist_data, width, color='green')

    ax.set_ylabel('$K yr^{-1}$')
    ax.set_title('Trend in %s, 1850-2005' %(metric_name))
    ax.set_xticks(ind + 1.5 * width)
    ax.set_xticklabels(models)
    ax.legend((rects1[0], rects2[0], rects3[0], rects4[0]), ('historicalGHG', 'historicalAA', 'GHG + AA', 'historical'), loc=1)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={infile: cube.attributes['history']})


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com

note:
   
"""

    description=''
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input file names")
    parser.add_argument("outfile", type=str, help="Output file name")

    args = parser.parse_args()            
    main(args)
