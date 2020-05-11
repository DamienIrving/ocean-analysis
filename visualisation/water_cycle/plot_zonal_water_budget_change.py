"""
Filename:     plot_zonal_water_budget_change.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  

"""

# Import general Python modules

import sys, os, pdb, glob
import argparse
import itertools
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn
import matplotlib as mpl


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
    import grids
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

aa_physics = {'CanESM2': 'p4', 'CCSM4': 'p10', 'CSIRO-Mk3-6-0': 'p4',
              'GFDL-CM3': 'p1', 'GISS-E2-H': 'p107', 'GISS-E2-R': 'p107', 'NorESM1-M': 'p1'}
titles = {'historical': 'historical', 'historical-rcp85': 'RCP 8.5', 'historicalGHG': 'GHG-only',
          'historicalMisc': 'AA-only', 'GHG+AA': 'GHG + AA',
          'hist-GHG+AA': 'historical - (GHG + AA)', '1pctCO2': '1pctCO2'}

panel_labels = {0: '(a)', 1: '(b)', 2: '(c)', 3: '(d)',
                4: '(e)', 5: '(f)', 6: '(g)', 7: '(h)'}

seaborn.set(style='whitegrid')

mpl.rcParams['axes.labelsize'] = 16
mpl.rcParams['axes.titlesize'] = 24
mpl.rcParams['xtick.labelsize'] = 20
mpl.rcParams['ytick.labelsize'] = 20
mpl.rcParams['legend.fontsize'] = 16


def inferred_wfo(s_orig, s_new, volume):
    """Calculate the inferred cumulative global total wfo for a given change in soga.
    
    wfo = net water flux into sea water
    soga = global mean sea water salinity
    v = volume of ocean (m3)
    
    """
    
    p = 1027  # kg/m3; average density of global ocean - could calculate from rhopoto data
    m_globe = volume * p
    
    delta_m = -1 * m_globe * (1 - (s_orig / s_new))    
    
    return delta_m


def ensemble_grid():
    """Make a dummy cube with desired grid."""
       
    lat_values = numpy.arange(-89.5, 90, 1.0)

    latitude = iris.coords.DimCoord(lat_values,
                                    var_name='lat',
                                    standard_name='latitude',
                                    long_name='latitude',
                                    units='degrees_north',
                                    coord_system=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS))

    dummy_data = numpy.zeros(len(lat_values))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0)])

    new_cube.coord('latitude').guess_bounds()

    return new_cube


def ensemble_mean(cube_list):
    """Calculate the ensemble mean."""

    if not cube_list:
        ensemble_mean = None
    elif len(cube_list) > 1:
        equalise_attributes(cube_list)
        ensemble_cube = cube_list.merge_cube()
        ensemble_mean = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)
    else:
        ensemble_mean = cube_list[0]

    return ensemble_mean


def calc_anomaly(cube, ref_cube=None):
    """Calculate the anomaly."""

    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    anomaly = anomaly[-1, ::]
    anomaly.remove_coord('time')

    return anomaly


def regrid(anomaly, ref_cube):
    """Regrid to reference cube, preserving the data sum"""

    lat_bounds = anomaly.coord('latitude').bounds
    lat_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, lat_bounds)
    anomaly_scaled = anomaly / lat_diffs

    ref_points = [('latitude', ref_cube.coord('latitude').points)]
    anomaly_regridded = anomaly_scaled.interpolate(ref_points, iris.analysis.Linear())         

    ref_lat_bounds = ref_cube.coord('latitude').bounds
    ref_lat_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, ref_lat_bounds)
    new_anomaly = anomaly_regridded * ref_lat_diffs

    return new_anomaly


def calc_ofm_anomaly(so_cube, m_orig):
    """Calculate the ocean freshwater mass anomaly."""

    s_orig = so_cube.data[0, :]
    s_new = so_cube.data[-1, :]
    ofm_anomaly_from_so = m_orig.data * ((s_orig / s_new) - 1) 
    
    anomaly = so_cube[0, :].copy()
    anomaly.remove_coord('time')
    anomaly.data = ofm_anomaly_from_so
    anomaly.units = 'kg'

    return anomaly


def read_data(infile, var, metadata_dict, time_constraint, ensemble_number, ref_cube=False, m_orig=False):
    """Read data and calculate anomaly"""

    if infile:
        cube = iris.load_cube(infile, var & time_constraint)
        try:
            cube.remove_coord('longitude')
        except iris.exceptions.CoordinateNotFoundError:
            pass         
        metadata_dict[infile] = cube.attributes['history']

        if var == 'sea_water_salinity':
            assert m_orig
            anomaly = calc_ofm_anomaly(cube, m_orig)
        else:
            anomaly = calc_anomaly(cube)
        final_value = anomaly.data.sum()
        print(var, 'final global total:', final_value)

        if ref_cube:
            grid_match = ref_cube.coord('latitude') == cube.coord('latitude')
            if not grid_match:
                anomaly = regrid(anomaly, ref_cube)
                final_value = anomaly.data.sum()
                print(var, 'final global total (after regrid):', final_value)

            if ref_cube.standard_name:
                anomaly.replace_coord(ref_cube.coord('latitude'))
            else:
                if not anomaly.coord('latitude').has_bounds():
                    anomaly.coord('latitude').bounds = ref_cube.coord('latitude').bounds
        
        new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
        anomaly.add_aux_coord(new_aux_coord)
    else:
        cube = None
        anomaly = None
        final_value = None
    
    return cube, anomaly, metadata_dict


def get_anomalies(wfo_file, so_file, masscello_orig, time_constraint,
                  model_num, ensemble_ref_cube, anomaly_dict, metadata_dict):
    """Get the cumulative sum anomaly."""
    
    wfo_cube, wfo_anomaly, metadata_dict = read_data(wfo_file,
                                                     'water_flux_into_sea_water',
                                                      metadata_dict, time_constraint, 
                                                      model_num, 
                                                      ref_cube=ensemble_ref_cube)

    ref_cube = ensemble_ref_cube if ensemble_ref_cube else wfo_cube
  
    cube, so_anomaly, metadata_dict = read_data(so_file, 'sea_water_salinity',
                                                metadata_dict, time_constraint,
                                                model_num, ref_cube=ref_cube,
                                                m_orig=masscello_orig)

    ocean_convergence = so_anomaly - wfo_anomaly
    transport_inferred = ocean_convergence.copy()
    transport_inferred.data = numpy.ma.cumsum(-1 * ocean_convergence.data)

    experiment = cube.attributes['experiment_id']          
    anomaly_dict[('wfo', experiment)].append(wfo_anomaly)
    anomaly_dict[('so', experiment)].append(so_anomaly)
    anomaly_dict[('transport', experiment)].append(transport_inferred)

    return anomaly_dict, metadata_dict


def plot_uptake_storage(gs, wfo_anomaly, so_anomaly,
                        exp_num=None, linestyle='-', linewidth=None, 
                        decorate=True, title=None, ylim=True,
                        panel_label=None, legloc=1):
    """Plot the freshwater uptake and storage"""

    ax = plt.subplot(gs)
    plt.sca(ax)

    if title:
        plt.title(title)

    if decorate:
        labels = ['surface freshwater flux', 'ocean salinity']
    else:
        labels = [None, None]

    iplt.plot(wfo_anomaly, color='orange', label=labels[0],
              linestyle=linestyle, linewidth=linewidth)
    iplt.plot(so_anomaly, color='blue', label=labels[1],
              linestyle=linestyle, linewidth=linewidth)   

    if ylim:
        ylower, yupper = ylim
        plt.ylim(ylower * 1e22, yupper * 1e22)

    if panel_label:
        ax.text(0.91, 0.10, panel_label, transform=ax.transAxes,
                fontsize=32, va='top')

    if decorate:
        if exp_num == 0:
            plt.ylabel('Anomalous freshwater uptake/storage ($kg \; lat^{-1}$)')
        plt.xlim(-90, 90)

        #plt.axhline(y=0, color='0.5', linestyle='--')
        plt.legend(loc=legloc)

    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
    ax.yaxis.major.formatter._useMathText = True


def plot_transport(gs, transport,
                   exp_num=None, linewidth=None, linestyle='-',
                   decorate=True, ylim=None, panel_label=None, legloc=1):
    """Plot the northward freshwater transport"""

    ax = plt.subplot(gs)
    plt.sca(ax)

    if decorate:
        labels = ['ocean freshwater transport']
    else:
        labels = [None]

    iplt.plot(transport, color='green', label=labels[0],
              linestyle=linestyle, linewidth=linewidth)

    if ylim:
        ylower, yupper = ylim
        plt.ylim(ylower * 1e23, yupper * 1e23)

    if panel_label:
        ax.text(0.91, 0.1, panel_label, transform=ax.transAxes,
                fontsize=32, va='top')

    if decorate:
        plt.xlabel('Latitude')
        if exp_num == 0:
            plt.ylabel('Accumulated anomalous freshwater transport ($kg$)')
        plt.xlim(-90, 90)

        #plt.axhline(y=0, color='0.5', linestyle='--')
        plt.legend(loc=legloc)

    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
    ax.yaxis.major.formatter._useMathText = True


def get_time_text(time_bounds):
    """Time text for plot title"""

    start_year = time_bounds[0].split('-')[0]
    end_year = time_bounds[-1].split('-')[0]
    time_text = '%s-%s' %(start_year, end_year)

    return time_text


def get_nmodels(inargs):
    """Get the number of models"""

    nmodels = None
    for exp_files in [inargs.ghg_files, inargs.aa_files, inargs.hist_files, inargs.pctCO2_files]:
        if exp_files:
            if nmodels:
                assert nmodels == len(exp_files)
            nmodels = len(exp_files) 

    return nmodels


def main(inargs):
    """Run program"""

    nmodels = get_nmodels(inargs)
    ensemble_ref_cube = ensemble_grid() if nmodels > 1 else None

    var_list = ['wfo', 'so', 'transport']
    exp_list = ['historicalGHG', 'historicalMisc', 'historical', 'GHG+AA', 'hist-GHG+AA', '1pctCO2', 'historical-rcp85']
    time_constraint = gio.get_time_constraint(inargs.time)

    anomaly_dict = {}
    for combo in itertools.product(var_list, exp_list):
        anomaly_dict[combo] = iris.cube.CubeList([])

    # Get data for the experiments
    volcello_vzsum = gio.get_ocean_weights(inargs.volcello_file)
    masscello_orig = volcello_vzsum * inargs.density

    for exp_files in [inargs.ghg_files, inargs.aa_files, inargs.hist_files, inargs.pctCO2_files]:
        for model_num, model_files in enumerate(exp_files):
            wfo_file, so_file = model_files
            metadata_dict = {}
            anomaly_dict, metadata_dict = get_anomalies(wfo_file, so_file, masscello_orig,
                                                        time_constraint, model_num,
                                                        ensemble_ref_cube, anomaly_dict,
                                                        metadata_dict)
            
    # Calculate the GHG + AA variables
    if inargs.ghg_files and inargs.aa_files:
        for mod_num in range(nmodels):
            for var in var_list:
                data_sum = anomaly_dict[(var, 'historicalGHG')][mod_num] + \
                           anomaly_dict[(var, 'historicalMisc')][mod_num]
                data_diff = anomaly_dict[(var, 'historical')][mod_num] - data_sum        
                anomaly_dict[(var, 'GHG+AA')].append(data_sum)
                anomaly_dict[(var, 'hist-GHG+AA')].append(data_diff)
        
    # Plot individual model data
    nexp = len(inargs.experiments)
    fig = plt.figure(figsize=[11 * nexp, 14])
    gs = gridspec.GridSpec(2, nexp)
    if nmodels > 1:
        for plot_index, exp in enumerate(inargs.experiments):    
            for mod_num in range(nmodels):    
                plot_uptake_storage(gs[plot_index],
                                    anomaly_dict[('wfo', exp)][mod_num],
                                    anomaly_dict[('so', exp)][mod_num],
                                    linewidth=0.8, linestyle='--',
                                    decorate=False, ylim=inargs.ylim_storage)
                plot_transport(gs[plot_index + nexp],
                               anomaly_dict[('transport', exp)][mod_num],
                               linewidth=0.8, linestyle='--',
                               decorate=False, ylim=inargs.ylim_transport) 

    # Plot ensemble data
    ensemble_dict = {}
    for combo in itertools.product(var_list, exp_list):
        cube_list = iris.cube.CubeList(filter(None, anomaly_dict[combo]))
        ensemble_dict[combo] = ensemble_mean(cube_list)

    linewidth = None if nmodels == 1 else 5.0
    for plot_index, exp in enumerate(inargs.experiments):
        storage_letter = panel_labels[plot_index] if inargs.panel_letters else None
        plot_uptake_storage(gs[plot_index],
                            ensemble_dict[('wfo', exp)],
                            ensemble_dict[('so', exp)],
                            linewidth=linewidth, title=titles[exp],
                            exp_num=plot_index, ylim=inargs.ylim_storage,
                            panel_label=storage_letter,
                            legloc=inargs.legloc_storage)
        transport_letter = panel_labels[plot_index + nexp] if inargs.panel_letters else None
        plot_transport(gs[plot_index + nexp],
                       ensemble_dict[('transport', exp)],
                       linewidth=linewidth,
                       exp_num=plot_index, ylim=inargs.ylim_transport,
                       panel_label=transport_letter,
                       legloc=inargs.legloc_transport) 
    
    if not inargs.no_title:
        time_text = get_time_text(inargs.time)
        fig.suptitle('zonally integrated change in fresh water, ' + time_text, fontsize='large')

    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot the zonally integrated water budget change '
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="name of output file")
    parser.add_argument("volcello_file", type=str, help="volcello-vertical-zonal-sum")

    parser.add_argument("--density", type=float, default=1026,
                        help="Reference density in kg / m3")

    parser.add_argument("--hist_files", type=str, nargs=2, action='append', default=[],
                        help="historical experiment wfo and so files for a given model (in that order)")
    parser.add_argument("--ghg_files", type=str, nargs=2, action='append', default=[],
                        help="historicalGHG experiment wfo and so files for a given model (in that order)")
    parser.add_argument("--aa_files", type=str, nargs=2, action='append', default=[],
                        help="historicalAA experiment wfo and so files for a given model (in that order)")
    parser.add_argument("--pctCO2_files", type=str, nargs=2, action='append', default=[],
                        help="1pctCO2 experiment wfo and so files for a given model (in that order)")

    parser.add_argument("--experiments", type=str, nargs='*',
                        choices=('historical', 'historical-rcp85', 'historicalGHG', 'historicalMisc',
                                 'GHG+AA', 'hist-GHG+AA', '1pctCO2'),
                        help="experiments to plot")                                  

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=('1861-01-01', '2005-12-31'),
                        help="Time period [default = 1861-2005]")

    parser.add_argument("--ylim_storage", type=float, nargs=2, default=None,
                        help="y limits for storage plots (x 10^22)")
    parser.add_argument("--ylim_transport", type=float, nargs=2, default=None,
                        help="y limits for transport plots (x 10^23)")
    parser.add_argument("--no_title", action="store_true", default=False,
                        help="switch for turning off plot title [default: False]")

    parser.add_argument("--panel_letters", action="store_true", default=False,
                        help="include a letter on each panel [default: False]")

    parser.add_argument("--legloc_storage", type=int, default=1,
                        help="legend location for storage plots")
    parser.add_argument("--legloc_transport", type=int, default=1,
                        help="legend location for transport plots")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)
