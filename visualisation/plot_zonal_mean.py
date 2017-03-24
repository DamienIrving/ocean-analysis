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
               

def main(inargs):
    """Run the program."""

    metadata_dict = {}
    for filename, experiment in inargs.infile:
        assert experiment in experiment_colors.keys()
        cube = iris.load_cube(filename, inargs.var)

        zonal_mean_cube = cube.collapsed('longitude', iris.analysis.MEAN)
        zonal_mean_cube.remove_coord('longitude')

        color = experiment_colors[experiment]
        iplt.plot(zonal_mean_cube, color=color, alpha=0.8, label=experiment)
    
        metadata_dict[filename] = cube.attributes['history']

    #plt.xlim(-70, 70)
    plt.legend(loc=inargs.legloc)
    plt.ylabel('Zonal mean %s (%s)' %(inargs.var.replace('_', ' '), cube.units) )
    plt.xlabel('latitude')
    plt.title('%s (%s)' %(inargs.model, inargs.run.replace('_', ' ')))

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
    
    args = parser.parse_args()            
    main(args)
