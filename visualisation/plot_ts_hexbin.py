"""
Filename:     plot_hexbin.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Make a hexagonal T-S binning plot  
"""

# Import general Python modules

import sys
import os
import re
import argparse
import pdb

import numpy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import iris
import cmdline_provenance as cmdprov

#import matplotlib as mpl
#mpl.rcParams['axes.labelsize'] = 'large'
#mpl.rcParams['axes.titlesize'] = 'x-large'
#mpl.rcParams['xtick.labelsize'] = 'medium'
#mpl.rcParams['ytick.labelsize'] = 'medium'
#mpl.rcParams['legend.fontsize'] = 'large'

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

cblabels = {'ocean_volume': 'Log of volume distribution (m3)',
            'ocean_heat_content': 'Excess heat storage (J)',
            'sea_water_potential_temperature': 'Temperature (C)'}


def main(inargs):
    """Run the program."""

    tcube = iris.load_cube(inargs.tfile, gio.check_iris_var(inargs.tvar))[-1, ::]
    scube = iris.load_cube(inargs.sfile, gio.check_iris_var(inargs.svar))[-1, ::]
    bcube = iris.load_cube(inargs.bfile, gio.check_iris_var(inargs.bvar))

    metadata_dict = {}
    metadata_dict[inargs.tfile] = tcube.attributes['history']
    metadata_dict[inargs.sfile] = scube.attributes['history']
    metadata_dict[inargs.bfile] = bcube.attributes['history']

    tcube.data = tcube.data - 273.15
    scube = gio.salinity_unit_check(scube)

    xdata = scube.data.flatten()
    ydata = tcube.data.flatten()
    bdata = bcube.data.flatten()

    fig = plt.figure(figsize=[9, 9])

    ax = fig.add_subplot(111, facecolor=cm.viridis(0))
    plt.hexbin(xdata, ydata, C=bdata, reduce_C_function=numpy.sum,
               gridsize=200, extent=(32, 38, -2, 30))  #mincnt=16  , bins='log'
    #plt.clim(vmax=0.5e15)

    #ax = fig.add_subplot(111, facecolor='white')
    #plt.hexbin(xdata, ydata, C=bdata, reduce_C_function=numpy.sum, cmap='RdBu_r',
    #           gridsize=200, extent=(32, 38, -2, 30))
    #vmin, vmax = plt.gci().get_clim()
    #if abs(vmin) > abs(vmax):
    #    vmax = abs(vmin)
    #else:
    #    vmin = -vmax
    #plt.clim(vmin=-200, vmax=200)

    cb = plt.colorbar()  # extend='min'
    plt.ylim(-2, 30)
    plt.xlim(32, 38)

    plt.xlabel('Salinity (g/kg)')
    plt.ylabel('Temperature (C)')
    cb.set_label(cblabels[inargs.bvar])

    # Save output
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
"""

    description = 'Make a hexagonal T-S binning plot'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("tfile", type=str, help="Temperature data file")
    parser.add_argument("tvar", type=str, help="Temperature variable")
    parser.add_argument("sfile", type=str, help="Salinity data file")
    parser.add_argument("svar", type=str, help="Salinity variable")
    parser.add_argument("bfile", type=str, help="Quantity for binning data file")
    parser.add_argument("bvar", type=str, help="Quantity for binning variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
main(args)
