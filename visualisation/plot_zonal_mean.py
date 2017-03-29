"""
Filename:     plot_zonal_mean.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import matplotlib.pyplot as plt
from matplotlib import gridspec
import iris
import iris.plot as iplt
import seaborn

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_colors = {}
experiment_colors['historical'] = 'green'
experiment_colors['piControl'] = 'black'
experiment_colors['historicalAA'] = 'blue'
experiment_colors['historicalGHG'] = 'red'
               

def scale_data(cube, var):
    """Scale data"""

    if var == 'precipitation_minus_evaporation_flux':
        cube.data = cube.data * 86400
        units = 'mm/day'
    else:
        units = cube.units

    return cube, units


def main(inargs):
    """Run the program."""

    if inargs.difference:
        fig = plt.figure(figsize=[10, 10])
        gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
        ax_main = plt.subplot(gs[0])
        plt.sca(ax_main)

    metadata_dict = {}
    data_dict = {}
    for filename, experiment in inargs.infile:
        assert experiment in experiment_colors.keys()

        cube = iris.load_cube(filename, gio.check_iris_var(inargs.var))
        cube, units = scale_data(cube, inargs.var)

        zonal_mean_cube = cube.collapsed('longitude', iris.analysis.MEAN)
        zonal_mean_cube.remove_coord('longitude')

        color = experiment_colors[experiment]
        iplt.plot(zonal_mean_cube, color=color, alpha=0.8, label=experiment)

        data_dict[experiment] = zonal_mean_cube   
        metadata_dict[filename] = cube.attributes['history']

    plt.legend(loc=inargs.legloc)
    plt.ylabel('Zonal mean %s (%s)' %(inargs.var.replace('_', ' '), units) )
    plt.title('%s (%s)' %(inargs.model, inargs.run.replace('_', ' ')))

    if inargs.difference:
        ax_diff = plt.subplot(gs[1])
        plt.sca(ax_diff)
        ghg_diff_cube = data_dict['historicalGHG'] - data_dict['piControl']
        aa_diff_cube = data_dict['historicalAA'] - data_dict['piControl']
        hist_diff_cube = data_dict['historical'] - data_dict['piControl']

        iplt.plot(ghg_diff_cube, color=experiment_colors['historicalGHG'], alpha=0.8)
        iplt.plot(aa_diff_cube, color=experiment_colors['historicalAA'], alpha=0.8)
        iplt.plot(hist_diff_cube, color=experiment_colors['historical'], alpha=0.8)
        plt.ylabel('Experiment - piControl')

    plt.xlabel('latitude')
        
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


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

    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("var", type=str, help="Variable standard_name")
    parser.add_argument("model", type=str, help="Model name")
    parser.add_argument("run", type=str, help="Run")
    parser.add_argument("--infile", type=str, action='append', default=[], nargs=2,
                        metavar=('FILENAME', 'EXPERIMENT'), help="Input file")

    parser.add_argument("--legloc", type=int, default=8,
                        help="Legend location")
    parser.add_argument("--difference", action="store_true", default=False,
                        help="Include a difference plot")
    
    args = parser.parse_args()            
    main(args)
