"""
Filename:     plot_zonal_energy_check.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  corresponds to energy_budget_in_one_plot.ipynb

"""

# Import general Python modules

import sys, os, pdb, glob
import argparse
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

seaborn.set(style='whitegrid')

mpl.rcParams['axes.labelsize'] = 20
mpl.rcParams['axes.titlesize'] = 24
mpl.rcParams['xtick.labelsize'] = 20
mpl.rcParams['ytick.labelsize'] = 20
mpl.rcParams['legend.fontsize'] = 20


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

    if len(cube_list) > 1:
        equalise_attributes(cube_list)
        ensemble_cube = cube_list.merge_cube()
        ensemble_mean = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN)
    else:
        ensemble_mean = cube_list[0]

    return ensemble_mean


def calc_anomaly(cube):
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


def get_data(infile, var, metadata_dict, time_constraint, ensemble_number, ref_cube=False):
    """Get data"""

    if infile:
        cube = iris.load_cube(infile[0], var & time_constraint)
        metadata_dict[infile[0]] = cube.attributes['history']
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


def plot_uptake_storage(gs, ohc_anomaly, hfds_anomaly, rndt_anomaly,
                        exp_num=None, linestyle='-', linewidth=None, decorate=True, ylim=True):
    """Plot the heat uptake and storage"""

    ax = plt.subplot(gs)
    plt.sca(ax)

    if decorate:
        labels = ['netTOA', 'OHU', 'OHC']
    else:
        labels = [None, None, None]

    iplt.plot(rndt_anomaly, color='red', label=labels[0], linestyle=linestyle, linewidth=linewidth)
    iplt.plot(hfds_anomaly, color='orange', label=labels[1], linestyle=linestyle, linewidth=linewidth)
    iplt.plot(ohc_anomaly, color='blue', label=labels[2], linestyle=linestyle, linewidth=linewidth)    

    if ylim:
        ylower, yupper = ylim
        plt.ylim(ylower * 1e22, yupper * 1e22)

    if decorate:
        if exp_num == 0:
            plt.ylabel('Heat uptake/storage ($J \; lat^{-1}$)')
        plt.xlim(-90, 90)

        #plt.axhline(y=0, color='0.5', linestyle='--')
        plt.legend()

    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
    ax.yaxis.major.formatter._useMathText = True


def plot_transport(gs, hfbasin_data, hfbasin_inferred, hfatmos_inferred, hftotal_inferred,
                   exp_num=None, linewidth=None, linestyle='-', decorate=True, ylim=None):
    """Plot the northward heat transport"""

    ax = plt.subplot(gs)
    plt.sca(ax)

    if decorate:
        labels = ['northward AHT', 'northward OHT', 'total transport']
    else:
        labels = [None, None, None]

    #if hfbasin_data:
    #    iplt.plot(hfbasin_data, color='purple', label='northward OHT')

    iplt.plot(hfatmos_inferred, color='green', label=labels[0], linestyle=linestyle, linewidth=linewidth)
    iplt.plot(hfbasin_inferred, color='purple', label=labels[1], linestyle=linestyle, linewidth=linewidth)    
    iplt.plot(hftotal_inferred, color='black', label=labels[2], linestyle=linestyle, linewidth=linewidth)

    if ylim:
        ylower, yupper = ylim
        plt.ylim(ylower * 1e23, yupper * 1e23)

    if decorate:
        plt.xlabel('Latitude')
        if exp_num == 0:
            plt.ylabel('Heat transport ($J \; lat^{-1}$)')
        plt.xlim(-90, 90)

        #plt.axhline(y=0, color='0.5', linestyle='--')
        plt.legend()

    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
    ax.yaxis.major.formatter._useMathText = True


def get_time_text(time_bounds):
    """Time text for plot title"""

    start_year = time_bounds[0].split('-')[0]
    end_year = time_bounds[-1].split('-')[0]
    time_text = '%s-%s' %(start_year, end_year)

    return time_text


def main(inargs):
    """Run program"""

    nexp = len(inargs.experiments)
    if inargs.sum_only:
        nexp = 1
    elif inargs.sum:
        nexp = nexp + 1
    fig = plt.figure(figsize=[11 * nexp, 14])
    gs = gridspec.GridSpec(2, nexp)

    nmodels = len(inargs.models)
    ensemble_ref_cube = ensemble_grid() if nmodels > 1 else None

    var_list = ['rndt', 'hfds', 'ohc', 'hfbasin-inferred', 'hfatmos-inferred', 'hftotal-inferred']
    plot_index = 0
    time_constraint = gio.get_time_constraint(inargs.time)
    time_text = get_time_text(inargs.time)
    ensemble_dict = {}
    for exp_num, experiment in enumerate(['historicalGHG', 'historicalMisc', 'historical']):
        data_dict = {}
        for var in var_list:
            data_dict[var] = iris.cube.CubeList([])
 
        for model_num, model in enumerate(inargs.models):
            mip = 'r1i1' + aa_physics[model] if experiment == 'historicalMisc' else 'r1i1p1'
            dir_exp = experiment.split('-')[-1]
            file_exp = 'historical-' + experiment if experiment[0:3] == 'rcp' else experiment

            mydir = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/yr'  %(model, dir_exp)

            rndt_file = glob.glob('%s/atmos/%s/rndt/latest/dedrifted/rndt-zonal-sum_Ayr_%s_%s_%s_cumsum-all.nc' %(mydir, mip, model, file_exp, mip))
            hfds_file = glob.glob('%s/ocean/%s/hfds/latest/dedrifted/hfds-zonal-sum_Oyr_%s_%s_%s_cumsum-all.nc' %(mydir, mip, model, file_exp, mip))
            ohc_file = glob.glob('%s/ocean/%s/ohc/latest/dedrifted/ohc-zonal-sum_Oyr_%s_%s_%s_all.nc' %(mydir, mip, model, file_exp, mip))
            #hfbasin_file = glob.glob('%s/ocean/%s/hfbasin/latest/dedrifted/hfbasin-global_Oyr_%s_%s_%s_cumsum-all.nc' %(mydir, inargs.mip, model, file_exp, inargs.mip))
    
            anomaly_dict = {}
            metadata_dict = {}

            rndt_cube, anomaly_dict['rndt'], metadata_dict = get_data(rndt_file, 'TOA Incoming Net Radiation',
                                                                      metadata_dict, time_constraint, model_num, ref_cube=ensemble_ref_cube)

            ref_cube = ensemble_ref_cube if ensemble_ref_cube else rndt_cube
  
            cube, anomaly_dict['hfds'], metadata_dict = get_data(hfds_file, 'surface_downward_heat_flux_in_sea_water',
                                                                 metadata_dict, time_constraint, model_num, ref_cube=ref_cube)
            cube, anomaly_dict['ohc'], metadata_dict = get_data(ohc_file, 'ocean heat content',
                                                                metadata_dict, time_constraint, model_num, ref_cube=ref_cube)
            #cube, anomaly_dict['hfbasin'], metadata_dict = get_data(hfbasin_file, 'northward_ocean_heat_transport',
            #                                                        metadata_dict, time_constraint, model_num)     

            ocean_convergence = anomaly_dict['ohc'] - anomaly_dict['hfds']
            anomaly_dict['hfbasin-inferred'] = ocean_convergence.copy()
            anomaly_dict['hfbasin-inferred'].data = numpy.ma.cumsum(-1 * ocean_convergence.data)
    
            atmos_convergence = anomaly_dict['hfds'] - anomaly_dict['rndt']
            anomaly_dict['hfatmos-inferred'] = atmos_convergence.copy()
            anomaly_dict['hfatmos-inferred'].data = numpy.ma.cumsum(-1 * atmos_convergence.data)

            total_convergence = anomaly_dict['ohc'] - anomaly_dict['rndt']
            anomaly_dict['hftotal-inferred'] = total_convergence.copy()
            anomaly_dict['hftotal-inferred'].data = numpy.ma.cumsum(-1 * total_convergence.data)
            
            if experiment in inargs.experiments:
                if nmodels > 1:
                    plot_uptake_storage(gs[plot_index], anomaly_dict['ohc'], anomaly_dict['hfds'], anomaly_dict['rndt'],
                                        linewidth=0.8, linestyle='--', decorate=False, ylim=inargs.ylim_storage)
                    plot_transport(gs[plot_index + nexp], None, anomaly_dict['hfbasin-inferred'], anomaly_dict['hfatmos-inferred'],
                                   anomaly_dict['hftotal-inferred'], linewidth=0.8, linestyle='--', decorate=False, ylim=inargs.ylim_transport) 

            for var in var_list:
                data_dict[var].append(anomaly_dict[var])

        ensemble_dict[experiment] = {}
        for var in var_list:
            cube_list = iris.cube.CubeList(filter(None, data_dict[var]))
            ensemble_dict[experiment][var] = ensemble_mean(cube_list)

        linewidth = None if nmodels == 1 else 3.0
        model_label = 'ensemble' if nmodels > 1 else inargs.models[0]
        experiment_label = 'historicalAA' if experiment == 'historicalMisc' else experiment  

        if experiment in inargs.experiments:
            plot_uptake_storage(gs[plot_index], ensemble_dict[experiment]['ohc'], ensemble_dict[experiment]['hfds'],
                                ensemble_dict[experiment]['rndt'], exp_num=exp_num, linewidth=linewidth, ylim=inargs.ylim_storage)
            plt.title(experiment_label)
            plot_transport(gs[plot_index + nexp], None, ensemble_dict[experiment]['hfbasin-inferred'], ensemble_dict[experiment]['hfatmos-inferred'],
                           ensemble_dict[experiment]['hftotal-inferred'], exp_num=exp_num, linewidth=linewidth, ylim=inargs.ylim_transport) #ensemble_dict[experiment]['hfbasin']

            plot_index = plot_index + 1

    if inargs.sum:
        exp1, exp2 = inargs.sum

        ohc_sum = ensemble_dict[exp1]['ohc'] + ensemble_dict[exp2]['ohc']
        hfds_sum = ensemble_dict[exp1]['hfds'] + ensemble_dict[exp2]['hfds']
        rndt_sum = ensemble_dict[exp1]['rndt'] + ensemble_dict[exp2]['rndt']
        plot_uptake_storage(gs[plot_index], ohc_sum, hfds_sum, rndt_sum, ylim=inargs.ylim_storage)

        exp1_label = 'historicalAA' if exp1 == 'historicalMisc' else exp1 
        exp2_label = 'historicalAA' if exp2 == 'historicalMisc' else exp2 
        plt.title(exp1_label + ' + ' + exp2_label)

        hfbasin_sum = ensemble_dict[exp1]['hfbasin-inferred'] + ensemble_dict[exp2]['hfbasin-inferred']
        hfatmos_sum = ensemble_dict[exp1]['hfatmos-inferred'] + ensemble_dict[exp2]['hfatmos-inferred']
        hftotal_sum = ensemble_dict[exp1]['hftotal-inferred'] + ensemble_dict[exp2]['hftotal-inferred']
        plot_transport(gs[plot_index + nexp], None, hfbasin_sum, hfatmos_sum, hftotal_sum, linewidth=linewidth, ylim=inargs.ylim_transport)
    
    if not inargs.no_title:
        fig.suptitle('zonally integrated heat accumulation, ' + time_text, fontsize='large')
    dpi = inargs.dpi if inargs.dpi else plt.savefig.__globals__['rcParams']['figure.dpi']
    print('dpi =', dpi)
    plt.savefig(inargs.outfile, bbox_inches='tight', dpi=dpi)
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

    parser.add_argument("outfile", type=str, help="name of output file. e.g. /g/data/r87/dbi599/figures/energy-check-zonal/energy-check-zonal_yr_model_experiment_mip_1861-2005.png")
    parser.add_argument("--models", type=str, nargs='*', help="models")
    parser.add_argument("--experiments", type=str, nargs='*', choices=('historical', 'historicalGHG', 'historicalMisc', 'historical-rcp85', 'rcp85'), help="experiments")                                  

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1861-01-01', '2005-12-31'),
                        help="Time period [default = 1861-2005]")

    parser.add_argument("--ylim_storage", type=float, nargs=2, default=None,
                        help="y limits for storage plots (x 10^22)")
    parser.add_argument("--ylim_transport", type=float, nargs=2, default=None,
                        help="y limits for transport plots (x 10^23)")
    parser.add_argument("--no_title", action="store_true", default=False,
                        help="switch for turning off plot title [default: False]")
    parser.add_argument("--sum", type=str, nargs=2, default=None,
                        help="add an extra plot with the sum of these two experiments")

    parser.add_argument("--sum_only", action='store_true', default=False,
                        help="include the sum plot only")

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)
