"""
Filename:     plot_zonal_ensemble.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot zonal ensemble  

"""

# Import general Python modules

import sys, os, pdb
import argparse
from itertools import groupby
from  more_itertools import unique_everseen
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec
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
    import timeseries
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_colors = {'historical': 'purple', 'historicalGHG': 'red',
                     'historicalAA': 'blue', 'GHG + AA': 'green',
                     'piControl': '0.5'}


def make_zonal_grid():
    """Make a dummy cube with desired grid."""
    
    lat_values = numpy.arange(-90, 91.5, 1.5)   
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS))

    dummy_data = numpy.zeros((len(lat_values)))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0),])

    new_cube.coord('latitude').guess_bounds()

    return new_cube


def calc_trend_cube(cube):
    """Calculate trend and put into appropriate cube."""
    
    trend_array = timeseries.calc_trend(cube, per_yr=True)
    new_cube = cube[0,:].copy()
    new_cube.remove_coord('time')
    new_cube.data = trend_array
    
    return new_cube


def get_colors(family_list):
    """Define a color for each model/physics combo"""

    nfamilies = len(family_list)
    cm = plt.get_cmap('nipy_spectral')
    colors = [cm(1. * i / (nfamilies + 1)) for i in range(nfamilies + 1)]
    color_dict = {}
    count = 1  # skips the first color, which is black
    for family in family_list:
        color_dict[family] = colors[count]
        count = count + 1

    return color_dict


def get_ylabel(cube, time_agg, inargs):
    """get the y axis label"""

    if str(cube.units) == 'kg m-2 s-1':
        ylabel = '$kg \: m^{-2} \: s^{-1}' 
    else:
        ylabel = '$%s' %(str(cube.units))
    if inargs.perlat:
        ylabel = ylabel + ' \: lat^{-1}'
    if time_agg == 'trend':
        ylabel = ylabel + ' \: yr^{-1}'
    ylabel = time_agg + ' (' + ylabel + '$)'

    return ylabel


def get_line_width(realization, model):
    """Get the line width"""

    if model == 'FGOALS-g2':
        lw = 2.0
    else:
        lw = 2.0 if realization == 'r1' else 0.5

    return lw


def plot_individual(data_dict, color_dict):
    """Plot the individual model data"""

    for key, cube in data_dict.items():
        model, physics, realization = key
        if (realization == 'r1') or (model == 'FGOALS-g2'):
            label = model + ', ' + physics
        else:
            label = None
        lw = 0.5   #get_line_width(realization, model)
        iplt.plot(cube, label=label, color=color_dict[(model, physics)], linewidth=lw)


def plot_ensmean(data_dict, experiment, nexperiments,
                 single_run=False, linestyle='-', linewidth=2.0):
    """Plot the ensemble mean.

    If single_run is true, the ensemble is calculated using
      only the first run from each model/physics family.

    """

    target_grid = make_zonal_grid()
    regridded_cube_list = iris.cube.CubeList([])
    count = 0
    for key, cube in data_dict.items():
        model, physics, realization = key
        if not single_run or ((realization == 'r1') or (model == 'FGOALS-g2')):
            regridded_cube = grids.regrid_1D(cube, target_grid, 'latitude')
            new_aux_coord = iris.coords.AuxCoord(count, long_name='ensemble_member', units='no_unit')
            regridded_cube.add_aux_coord(new_aux_coord)
            regridded_cube.cell_methods = None
            regridded_cube.data = regridded_cube.data.astype(numpy.float64)
            regridded_cube_list.append(regridded_cube)
            count = count + 1

    if len(regridded_cube_list) > 1:
        equalise_attributes(regridded_cube_list)
        ensemble_cube = regridded_cube_list.merge_cube()
        ensemble_mean = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)
    else:
        ensemble_mean = regridded_cube_list[0]
   
    label, color = get_ensemble_label_color(experiment, nexperiments, count, single_run)
    iplt.plot(ensemble_mean, label=label, color=color, linestyle=linestyle, linewidth=linewidth)

    return ensemble_mean


def get_ensemble_label_color(experiment, nexperiments, ensemble_size, single_run):
    """Get the line label and color."""

    label = experiment
    color = experiment_colors[experiment]

    return label, color


def group_runs(data_dict):
    """Find unique model/physics groups"""

    all_info = data_dict.keys()

    model_physics_list = []
    for key, group in groupby(all_info, lambda x: x[0:2]):
        model_physics_list.append(key)

    family_list = list(unique_everseen(model_physics_list))

    return family_list


def read_data(inargs, infiles, ref_cube=None):
    """Read data."""

    clim_dict = {}
    trend_dict = {}
    for filenum, infile in enumerate(infiles):
        cube = iris.load_cube(infile, gio.check_iris_var(inargs.var))
        if ref_cube:
            branch_time = None if inargs.branch_times[filenum] == 'default' else str(inargs.branch_times[filenum])
            time_constraint = timeseries.get_control_time_constraint(cube, ref_cube, inargs.time, branch_time=branch_time)
            cube = cube.extract(time_constraint)
            iris.util.unify_time_units([ref_cube, cube])
            cube.coord('time').units = ref_cube.coord('time').units
            cube.replace_coord(ref_cube.coord('time'))
        else:
            time_constraint = gio.get_time_constraint(inargs.time)
            cube = cube.extract(time_constraint)

        #cube = uconv.convert_to_joules(cube)

        if inargs.perlat:
            grid_spacing = grids.get_grid_spacing(cube) 
            cube.data = cube.data / grid_spacing
 
        trend_cube = calc_trend_cube(cube.copy())
        
        clim_cube = cube.collapsed('time', iris.analysis.MEAN)
        clim_cube.remove_coord('time')

        model = cube.attributes['model_id']
        realization = 'r' + str(cube.attributes['realization'])
        physics = 'p' + str(cube.attributes['physics_version'])

        key = (model, physics, realization)
        trend_dict[key] = trend_cube
        clim_dict[key] = clim_cube

    experiment = cube.attributes['experiment_id']
    experiment = 'historicalAA' if experiment == "historicalMisc" else experiment    
    trend_ylabel = get_ylabel(cube, 'trend', inargs)
    clim_ylabel = get_ylabel(cube, 'climatology', inargs)

    metadata_dict = {infile: cube.attributes['history']}
    
    return cube, trend_dict, clim_dict, experiment, trend_ylabel, clim_ylabel, metadata_dict


def get_title(standard_name, time_list, experiment, nexperiments):
    """Get the plot title"""

    title = '%s, %s-%s' %(gio.var_names[standard_name],
                          time_list[0][0:4],
                          time_list[1][0:4])

    if nexperiments == 1:
        title = title + ', ' + experiment

    return title


def correct_y_lim(ax, data_cube):   
   """Adjust the y limits after changing x limit 

   x: data for entire x-axes
   y: data for entire y-axes

   """

   x_data = data_cube.coord('latitude').points
   y_data = data_cube.data

   lims = ax.get_xlim()
   i = numpy.where( (x_data > lims[0]) & (x_data < lims[1]) )[0]

   plt.ylim( y_data[i].min(), y_data[i].max() ) 


def align_yaxis(ax1, ax2):
    """Align zeros of the two axes, zooming them out by same ratio

    Taken from: https://stackoverflow.com/questions/10481990/matplotlib-axis-with-two-scales-shared-origin

    """
    axes = (ax1, ax2)
    extrema = [ax.get_ylim() for ax in axes]
    tops = [extr[1] / (extr[1] - extr[0]) for extr in extrema]
    # Ensure that plots (intervals) are ordered bottom to top:
    if tops[0] > tops[1]:
        axes, extrema, tops = [list(reversed(l)) for l in (axes, extrema, tops)]

    # How much would the plot overflow if we kept current zoom levels?
    tot_span = tops[1] + 1 - tops[0]

    b_new_t = extrema[0][0] + tot_span * (extrema[0][1] - extrema[0][0])
    t_new_b = extrema[1][1] - tot_span * (extrema[1][1] - extrema[1][0])
    axes[0].set_ylim(extrema[0][0], b_new_t)
    axes[1].set_ylim(t_new_b, extrema[1][1])


def plot_files(ax, ax2, infiles, inargs, nexperiments, ref_cube=None):
    """Plot a list of files corresponding to a particular experiment."""

    cube, trend_dict, clim_dict, experiment, trend_ylabel, clim_ylabel, metadata_dict = read_data(inargs, infiles, ref_cube=ref_cube)
    model_family_list = group_runs(trend_dict)
    color_dict = get_colors(model_family_list)

    if inargs.time_agg == 'trend':
        target_dict = trend_dict
        target_ylabel = trend_ylabel
    else:
        target_dict = clim_dict
        target_ylabel = clim_ylabel

    if nexperiments == 1:
        plot_individual(target_dict, color_dict)
    if inargs.ensmean:
        ensemble_mean = plot_ensmean(target_dict, experiment, nexperiments,
                                     single_run=inargs.single_run)
    else:
        ensemble_mean = None

    if inargs.clim and ((nexperiments == 1) or (experiment == 'historical')):
        ax2 = ax.twinx()
        plot_ensmean(clim_dict, experiment, nexperiments,
                     single_run=inargs.single_run, linestyle='--', linewidth=1.0)
        plt.sca(ax)

    return cube, metadata_dict, ensemble_mean, target_ylabel, clim_ylabel, experiment, ax2


def main(inargs):
    """Run the program."""
    
    seaborn.set_context(inargs.context)

    fig, ax = plt.subplots()   # figsize=[14, 7]
    ax2 = None
    nexperiments = len(inargs.hist_files)
    if inargs.control_files:
        nexperiments = nexperiments + len(inargs.control_files)

    # Plot historical data
    for infiles in inargs.hist_files:
        cube, metadata_dict, ensemble_mean, ylabel, clim_ylabel, experiment, ax2 = plot_files(ax, ax2, infiles, inargs, nexperiments)
    
    # Titles and labels
    if inargs.title:
        title = inargs.title
    else:
        title = get_title(inargs.var, inargs.time, experiment, nexperiments)
    plt.title(title)

    if inargs.scientific:
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
        ax.yaxis.major.formatter._useMathText = True        
    if inargs.ylabel:
        ylabel = inargs.ylabel
    ax.set_ylabel(ylabel)
    ax.set_xlabel('latitude')

    # Plot control data
    if inargs.control_files:
        assert inargs.hist_files, 'Control plot requires branch time information from historical files'
        ref_cube = cube
        for infiles in inargs.control_files:
            cube, metadata_dict, ensemble_mean, ylabel, clim_ylabel, epxeriment, ax2 = plot_files(ax, ax2, infiles, inargs, nexperiments, ref_cube=ref_cube)

    # Ticks and axis limits
    plt.xticks(numpy.arange(-75, 90, 15))
    plt.xlim(inargs.xlim[0], inargs.xlim[1])
    if not inargs.xlim == (-90, 90):
        correct_y_lim(ax, ensemble_mean)

    if inargs.clim:
        align_yaxis(ax, ax2)
        ax2.grid(None)
        ax2.set_ylabel(clim_ylabel)
        ax2.yaxis.major.formatter._useMathText = True

    # Guidelines and legend
    if inargs.zeroline:
        plt.axhline(y=0, color='0.5', linestyle='--')

    if inargs.legloc:
        ax.legend(loc=inargs.legloc)
    else:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        if inargs.clim:
            ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            legend_x_pos = 1.1
        else:
            legend_x_pos = 1.0
        ax.legend(loc='center left', bbox_to_anchor=(legend_x_pos, 0.5))

    # Save output
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot zonal ensemble'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("time_agg", type=str, choices=('trend', 'climatology'), help="Temporal aggregation")
    parser.add_argument("outfile", type=str, help="Output file")                                     
    
    parser.add_argument("--hist_files", type=str, action='append', nargs='*',
                        help="Input files for a given historical experiment")
    parser.add_argument("--control_files", type=str, action='append', nargs='*', default=[],
                        help="Input files for a control experiment")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'),
                        help="Time bounds [default = 1861-2005]")

    parser.add_argument("--branch_times", type=str, nargs='*', default=None,
                        help="Need value for each control file (write default to use metadata)")

    parser.add_argument("--perlat", action="store_true", default=False,
                        help="Scale per latitude [default=False]")
    parser.add_argument("--single_run", action="store_true", default=False,
                        help="Only use run 1 in the ensemble mean [default=False]")
    parser.add_argument("--ensmean", action="store_true", default=False,
                        help="Plot an ensemble mean curve [default=False]")
    parser.add_argument("--clim", action="store_true", default=False,
                        help="Plot a climatology curve behind the trend curve [default=False]")
    parser.add_argument("--legloc", type=int, default=None,
                        help="Legend location [default = off plot]")
    parser.add_argument("--scientific", action="store_true", default=False,
                        help="Use scientific notation for the y axis scale [default=False]")
    parser.add_argument("--zeroline", action="store_true", default=False,
                        help="Plot a dashed guideline at y=0 [default=False]")
    parser.add_argument("--title", type=str, default=None,
                        help="plot title [default: None]")
    parser.add_argument("--ylabel", type=str, default=None,
                        help="Override the default y axis label")

    parser.add_argument("--xlim", type=float, nargs=2, metavar=('SOUTHERN_LIMIT', 'NORTHERN LIMIT'), default=(-90, 90),
                        help="x-axis limits [default = entire]")
    #parser.add_argument("--ylim", type=float, nargs=2, metavar=('LOWER_LIMIT', 'UPPER_LIMIT'), default=None,
    #                    help="y-axis limits [default = auto]")

    parser.add_argument("--context", type=str, default='talk', choices=('paper', 'talk'),
                        help="Context for plot [default=talk]")
    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)
