"""
Filename:     plot_lat_vs_depth.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot latitude versus depth data  

"""

# Import general Python modules

import sys
import os
import pdb
import re
import argparse

import numpy
import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import iris
import cmdline_provenance as cmdprov

import matplotlib as mpl
mpl.rcParams['axes.labelsize'] = 'large'
mpl.rcParams['axes.titlesize'] = 'x-large'
mpl.rcParams['xtick.labelsize'] = 'medium'
mpl.rcParams['ytick.labelsize'] = 'medium'
mpl.rcParams['legend.fontsize'] = 'large'

contour_width =  1
contour_color = '0.3'

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

# Define functions

def make_grid(depth_values, lat_values):
    """Make a dummy cube with desired grid."""
       
    depth = iris.coords.DimCoord(depth_values,
                                 standard_name='depth',
                                 units='m',
                                 long_name='ocean depth coordinate',
                                 var_name='lev')

    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS))

    dummy_data = numpy.zeros((len(depth_values), len(lat_values)))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(depth, 0), (latitude, 1)])

    new_cube.coord('depth').guess_bounds()
    new_cube.coord('latitude').guess_bounds()

    return new_cube


def regrid(cube, ref_cube):
    """Regrid to reference grid, preserving the data sum"""

    depth_bounds = cube.coord('depth').bounds
    depth_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, depth_bounds)
    cube_scaled = cube / uconv.broadcast_array(depth_diffs, 0, cube.shape)

    lat_bounds = cube.coord('latitude').bounds
    lat_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, lat_bounds)
    cube_scaled = cube_scaled / uconv.broadcast_array(lat_diffs, 1, cube.shape)

    ref_points = [('depth', ref_cube.coord('depth').points), ('latitude', ref_cube.coord('latitude').points)]
    cube_regridded = cube_scaled.interpolate(ref_points, iris.analysis.Linear())         

    ref_depth_bounds = ref_cube.coord('depth').bounds
    ref_depth_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, ref_depth_bounds)
    new_cube = cube_regridded * uconv.broadcast_array(ref_depth_diffs, 0, cube_regridded.shape)

    ref_lat_bounds = ref_cube.coord('latitude').bounds
    ref_lat_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, ref_lat_bounds)
    new_cube = cube_regridded * uconv.broadcast_array(ref_lat_diffs, 1, cube_regridded.shape)

    return new_cube


def set_units(cube, scale_factor=1, nyrs=1):
    """Set the units.
    Args:
      cube (iris.cube.Cube): Data cube
      scale_factor (int): Scale the data
        e.g. a scale factor of 3 will mean the data are 
        mutliplied by 10^3 (and units will be 10^-3)
      nyrs (int): Trend units is per nyrs
    """

    ajusted_data = cube.data * nyrs * 10**scale_factor
    
    unit_scale = ''
    if scale_factor != 0:
        if scale_factor > 0.0:
            unit_scale = '10^{-%i}'  %(scale_factor)
        else:
            unit_scale = '10^{%i}'  %(abs(scale_factor))

    units = str(cube.units)
    units = units.replace(" ", " \enspace ")

    if 'yr-1' in units:
        if nyrs == 1:
            units = units.replace("-1", "^{-1}")
            units = '$%s \enspace %s$'  %(unit_scale, units)
        else:
            units = units.replace("yr-1", "$per %s years" %(str(nyrs)))
            units = '$%s \enspace %s'  %(unit_scale, units)

    if rescale:
        units = '$' + units +  '\enspace m^{-1} \enspace lat^{-1}$'

    return adjusted_data, units


def create_plot(gs, cbar_ax, contourf_cube, contour_cube, scale_factor, nyrs, title,
                ticks=None, rescale=False):
    """Create the plot."""
    
    axMain = plt.subplot(gs)
    plt.sca(axMain)

    cmap = plt.cm.RdBu_r 
    #cmocean.cm.balance

    lats = contourf_cube.coord('latitude').points
    levs = contourf_cube.coord('depth').points 
    
    contourf_data, units = set_units(contourf_cube, scale_factor=scale_factor,
                                     nyrs=nyrs, rescale=rescale)           
    contourf_ticks = ticks if ticks else [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]

    cf = axMain.contourf(lats, levs, contourf_data,
                         cmap=cmap, extend='both', levels=contourf_ticks)

    if contour_cube:
        contour_data = contour_cube.data
        contour_levels = numpy.arange(0.0, 350.0, 2.5)

        cplot_main = axMain.contour(lats, levs, contour_data, colors=contour_color,
                                    linewidths=contour_width, levels=contour_levels)
        #plt.clabel(cplot_main, contour_levels[0::2], fmt='%2.1f', colors=contour_color, fontsize=8)
        plt.clabel(cplot_main, fmt='%2.1f', colors=contour_color, fontsize=8)

    # Deep section
    axMain.set_ylim((500.0, 2000.0))
    axMain.invert_yaxis()
    axMain.set_xlim((-75, 75))
    axMain.xaxis.set_ticks_position('bottom')
    axMain.set_xticks([-80, -60, -40, -20, 0, 20, 40, 60, 80])
    plt.ylabel('Depth (m)')
    plt.xlabel('Latitude')
    axMain.get_yaxis().set_label_coords(-0.11, 1.1)

    # Shallow section
    divider = make_axes_locatable(axMain)
    axShallow = divider.append_axes("top", size="70%", pad=0.2, sharex=axMain)
    axShallow.contourf(lats, levs, contourf_data,
                       cmap=cmap, extend='both', levels=contourf_ticks)

    if contour_cube:
        cplot_shallow = axShallow.contour(lats, levs, contour_data, colors=contour_color,
                                          linewidths=contour_width, levels=contour_levels)
        #plt.clabel(cplot_shallow, contour_levels[0::2], fmt='%2.1f', colors=contour_color, fontsize=8)
        plt.clabel(cplot_shallow, fmt='%2.1f', colors=contour_color, fontsize=8)

    axShallow.set_ylim((0.0, 500.0))
    axShallow.set_xlim((-75, 75))
    axShallow.invert_yaxis()
    plt.setp(axShallow.get_xticklabels(), visible=False)

    cbar = plt.colorbar(cf, cbar_ax)  #, orientation='horizontal')
    cbar.set_label(units)

    if title:
        axShallow.set_title(title)


def grid_config(nplots):
    """Determine the grid configuration."""

    assert nplots in [1, 4]
    if nplots == 1:
        fig = plt.figure()
        gs = gridspec.GridSpec(1, 1)
        cbar_ax = fig.add_axes([0.93, 0.2, 0.02, 0.65])
    else:
        fig = plt.figure(figsize=[18, 18])
        gs = gridspec.GridSpec(2, 2)
        fig.subplots_adjust(right=0.85)
        cbar_ax = fig.add_axes([0.9, 0.2, 0.02, 0.6])

    return fig, cbar_ax, gs


def main(inargs):
    """Run the program."""
    
    metadata_dict = {}
    nplots = len(inargs.contourf_files)
    if inargs.contour_files:
        assert len(inargs.contour_files) == nplots

    fig, cbar_ax, gs = grid_config(nplots)

    for pnum in range(nplots): 
        contourf_cube = iris.load_cube(inargs.contourf_files[pnum], inargs.variable)
        metadata_dict[inargs.contourf_files[pnum]] = contourf_cube.attributes['history']

        if inargs.rescale:
            depth_values = numpy.arange(0.5, 5500, 1)
            lat_values = numpy.arange(-89.5, 90.5, 1)
            ref_cube = make_grid(depth_values, lat_values)
            contourf_cube = regrid(contourf_cube, ref_cube)
    
        if inargs.contour_files:
            contour_cube = iris.load_cube(inargs.contour_files[pnum], inargs.variable)
            metadata_dict[inargs.contour_files[pnum]] = contour_cube.attributes['history']
        else:
            contour_cube = None

        title = inargs.titles[pnum] if inargs.titles else None 
        create_plot(gs[pnum], cbar_ax, contourf_cube, contour_cube, inargs.scale_factor,
                    inargs.nyrs, title, ticks=inargs.ticks, rescale=inargs.rescale)

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

    description = 'Plot latitude versus depth data'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("contourf_files", nargs='*', type=str, help="Filled contour data file") 
    parser.add_argument("variable", type=str, help="Variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--contour_files", nargs='*', type=str, default=None,
                        help="unfilled contour data file")

    parser.add_argument("--titles", nargs='*', type=str, default=None,
                        help="plot titles")

    parser.add_argument("--scale_factor", type=int, default=3,
                        help="Scale factor (e.g. scale factor of 3 will multiply trends by 10^3 [default=1]")
    parser.add_argument("--nyrs", type=int, default=1,
                        help="Trend is presented per number of years [default=1]")

    parser.add_argument("--ticks", type=float, nargs='*', default=None,
                        help="list of contour levels to plot [default = auto]")

    parser.add_argument("--rescale", action="store_true", default=False,
                        help="Rescale so the output is m-1 lat-1")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)
