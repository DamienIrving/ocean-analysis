"""
Filename:     plot_optical_depth.py
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
experiment_colors['historicalAA'] = 'blue'
experiment_colors['historicalGHG'] = 'red'
experiment_colors['historicalnoAA'] = 'orange'

region_styles = {}
region_styles['sh'] = 'dashed'
region_styles['nh'] = 'dashdot'
region_styles['global'] = 'solid'
               
def get_file_info(infile):
    """Strip information from the file name."""

    file_components = infile.split('/')
    fname = file_components[-1]
    metric, realm, model, experiment, mip, time = fname.split('_')
    assert 'historical' in experiment
    var, region, aggregator = metric.split('-')
    assert region in region_styles.keys()

    if experiment == 'historicalMisc':
        experiment = 'historicalAA'

    return experiment, model, region, mip


def main(inargs):
    """Run the program."""

    fig = plt.figure(figsize=[10, 10])
    for infile in inargs.infiles:
        cube = iris.load_cube(infile)
        experiment, model, region, mip = get_file_info(infile)

        color = experiment_colors[experiment]
        style = region_styles[region]
        iplt.plot(cube, color=color, linestyle=style, label=experiment+', '+region)
        plt.title(model + ', ' + mip[0:2])

    plt.legend()
    plt.ylabel('Aerosol optical depth at 550nm')
    plt.xlabel('Year')
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
 
    parser.add_argument("--legloc", type=int, default=8,
                        help="Legend location")
    
    args = parser.parse_args()            
    main(args)
