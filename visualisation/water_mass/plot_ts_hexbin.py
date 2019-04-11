"""
Filename:     plot_ts_hexbin.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot ocean volume distribution in T-S space  

"""

# Import general Python modules

import sys
import os
import re
import pdb
import argparse

import numpy
import pandas
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')



# Define functions

ocean_names = {0: 'land', 1: 'southern_ocean', 2: 'atlantic', 
               3: 'pacific', 4: 'arctic', 5: 'indian', 
               6: 'mediterranean', 7: 'black_sea', 8: 'hudson_bay',
               9: 'baltic_sea', 10: 'red_sea'}

def get_ocean_name(ocean_num):
    return ocean_names[ocean_num]


def select_basin(df, basin_name):
    """Select basin"""

    if not basin_name == 'globe':
        df['basin'] = df['basin'].apply(get_ocean_name)
        basin_components = basin_name.split('_')
        if len(basin_components) == 1:
            ocean = basin_components[0]
            hemisphere = None
        else:
            hemisphere, ocean = basin_components

        df = df[(df.basin == ocean)]
        if hemisphere == 'north':
            df = df[(df.latitude > 0)]
        elif hemisphere == 'south':
            df = df[(df.latitude < 0)]

    return df


def create_df(tcube, scube, vcube, bcube, basin):
    """Create DataFrame"""

    tcube = gio.temperature_unit_check(tcube, convert_to_celsius=True)
    scube = gio.salinity_unit_check(scube)

    assert tcube.ndim == 3
    assert scube.ndim == 3
    lats = uconv.broadcast_array(tcube.coord('latitude').points, [1, 2], tcube.shape)
    lons = uconv.broadcast_array(tcube.coord('longitude').points, [1, 2], tcube.shape)
    levs = uconv.broadcast_array(tcube.coord('depth').points, 0, tcube.shape)

    sdata = scube.data.flatten()
    tdata = tcube.data.flatten()
    vdata = vcube.data.flatten()
    bdata = bcube.data.flatten()
    lat_data = lats.flatten()
    lon_data = lons.flatten()
    depth_data = levs.flatten()

    df = pandas.DataFrame(index=range(tdata.shape[0]))
    df['temperature'] = tdata.filled(fill_value=5000)
    df['salinity'] = sdata.filled(fill_value=5000)
    df['volume'] = vdata.filled(fill_value=5000)
    df['basin'] = bdata.filled(fill_value=5000)
    df['latitude'] = lat_data.filled(fill_value=5000)
    df['longitude'] = lon_data.filled(fill_value=5000)
    df['depth'] = depth_data

    df = df[df.temperature != 5000]
    df = df[df.temperature != -273.15]

    if basin:
        df = select_basin(df, basin)

    return df


def get_title(cube, basin):
    """Get the plot title."""

    model = cube.attributes['model_id']
    basin = basin.replace('_', ' ').title()
    title = '%s volume distribution, %s model' %(basin, model) 

    return title


def main(inargs):
    """Run the program."""
    
    metadata_dict = {}

    vcube = iris.load_cube(inargs.volume_file)
    bcube = iris.load_cube(inargs.basin_file)

    fig, ax = plt.subplots(figsize=(9, 9))
    legend_elements = []
    nplots = len(inargs.temperature_files) - 1
    plotnum = 0
    for tfile, sfile in zip(inargs.temperature_files, inargs.salinity_files):
        tcube = iris.load_cube(tfile)
        scube = iris.load_cube(sfile)

        df = create_df(tcube, scube, vcube, bcube, basin=inargs.basin)
   
        smin, smax = inargs.salinity_bounds
        tmin, tmax = inargs.temperature_bounds
        vmin, vmax = inargs.colorbar_bounds
        plt.hexbin(df['salinity'].values, df['temperature'].values,
                   C=df['volume'].values, reduce_C_function=numpy.sum,
                   gridsize=400, bins='log', alpha=inargs.alphas[plotnum],
                   extent=(smin, smax, tmin, tmax),
                   cmap=inargs.colors[plotnum],
                   vmin=vmin, vmax=vmax)
        if plotnum == 0:
            cb = plt.colorbar()
        if inargs.labels:
            color = inargs.colors[plotnum][0:-1].lower()
            legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=color,
                                   label=inargs.labels[plotnum], alpha=inargs.alphas[plotnum]))
        plotnum = plotnum + 1

    title = get_title(tcube, inargs.basin) 
    plt.title(title)
    plt.ylabel('temperature ($C$)')
    plt.xlabel('salinity ($g kg^{-1}$)')
    cb.set_label('log(volume) ($m^3$)')
    if legend_elements:
        ax.legend(handles=legend_elements, loc=4)

    # Save output
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    
    # Metadata
    metadata_dict = {inargs.basin_file: bcube.attributes['history'],
                     inargs.volume_file: vcube.attributes['history'],
                     tfile: tcube.attributes['history'],
                     sfile: scube.attributes['history']}
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot ocean volume distribution in T-S space.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("volume_file", type=str, help="Volume file name")
    parser.add_argument("basin_file", type=str, help="Basin file name")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--temperature_files", nargs='*', type=str, help="Temperature files") 
    parser.add_argument("--salinity_files", nargs='*', type=str, help="Salinity files")
    parser.add_argument("--colors", nargs='*', type=str,
                        choices=('Greys', 'Reds', 'Blues', 'Greens', 'Oranges', 'Purples', 'viridis'), 
                        help="Color for each temperature/salinity file pair")
    parser.add_argument("--alphas", nargs='*', type=float, 
                        help="Transparency for each temperature/salinity pair")
    parser.add_argument("--labels", nargs='*', type=str, default=None, 
                        help="Label for each temperature/salinity pair")

    parser.add_argument("--basin", type=str, default='globe',
                        choices=('globe', 'indian', 'north_atlantic', 'south_atlantic', 'north_pacific', 'south_pacific'),
                        help='ocean basin to plot')

    parser.add_argument("--salinity_bounds", type=float, nargs=2, default=(32, 37.5),
                        help='bounds for the salinity (X) axis')
    parser.add_argument("--temperature_bounds", type=float, nargs=2, default=(-2, 30),
                        help='bounds for the temperature (Y) axis')
    parser.add_argument("--colorbar_bounds", type=float, nargs=2, default=(9.8, 16.6),
                        help='bounds for the colorbar')

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             

    assert len(args.temperature_files) == len(args.salinity_files) == len(args.colors)
    main(args)
