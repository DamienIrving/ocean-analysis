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
seaborn.set_context('talk')

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
                    anomaly.coord('latitude').guess_bounds()
        
        new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
        anomaly.add_aux_coord(new_aux_coord)
    else:
        cube = None
        anomaly = None
        final_value = None
    
    return cube, anomaly, metadata_dict


def plot_uptake_storage(gs, ohc_anomaly, hfds_anomaly, rndt_anomaly, linewidth=None, decorate=True):
    """Plot the heat uptake and storage"""

    ax = plt.subplot(gs)
    plt.sca(ax)

    if decorate:
        labels = ['OHC', 'hfds', 'netTOA']
    else:
        labels = [None, None, None]

    iplt.plot(ohc_anomaly, color='blue', label=labels[0], linewidth=linewidth)
    iplt.plot(hfds_anomaly, color='orange', label=labels[1], linewidth=linewidth)
    iplt.plot(rndt_anomaly, color='red', label=labels[2], linewidth=linewidth)

    if decorate:
        plt.ylabel('J')
        plt.xlim(-90, 90)

        plt.axhline(y=0, color='0.5', linestyle='--')
        plt.legend()


def plot_transport(gs, hfbasin_data, hfbasin_inferred, hfatmos_inferred, linewidth=None, decorate=True):
    """Plot the northward heat transport"""

    ax = plt.subplot(gs)
    plt.sca(ax)

    if decorate:
        labels = ['inferred northward OHT', 'inferred northward AHT']
    else:
        labels = [None, None]

    #if hfbasin_data:
    #    iplt.plot(hfbasin_data, color='purple', label='northward OHT')

    iplt.plot(hfbasin_inferred, color='purple', linestyle='--', label=labels[0], linewidth=linewidth)
    iplt.plot(hfatmos_inferred, color='green', linestyle='--', label=labels[1], linewidth=linewidth)

    if decorate:
        plt.xlabel('latitude')
        plt.ylabel('J')
        plt.xlim(-90, 90)

        plt.axhline(y=0, color='0.5', linestyle='--')

        plt.legend()


def main(inargs):
    """Run program"""

    nexp = len(inargs.experiments)

    fig = plt.figure(figsize=[12 * nexp, 14])
    gs = gridspec.GridSpec(2, nexp)

    nmodels = len(inargs.models)
    ensemble_ref_cube = ensemble_grid() if nmodels > 1 else None

    var_list = ['rndt', 'hfds', 'ohc', 'hfbasin-inferred', 'hfatmos-inferred']
    plot_index = 0
    for experiment in inargs.experiments:
        data_dict = {}
        for var in var_list:
            data_dict[var] = iris.cube.CubeList([])
 
        for index, model in enumerate(inargs.models):
            mip = 'r1i1' + aa_physics[model] if experiment == 'historicalMisc' else 'r1i1p1' 
            mydir = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/yr'  %(model, experiment)

            rndt_file = glob.glob('%s/atmos/%s/rndt/latest/dedrifted/rndt-zonal-sum_Ayr_%s_%s_%s_cumsum-all.nc' %(mydir, mip, model, experiment, mip))
            hfds_file = glob.glob('%s/ocean/%s/hfds/latest/dedrifted/hfds-zonal-sum_Oyr_%s_%s_%s_cumsum-all.nc' %(mydir, mip, model, experiment, mip))
            ohc_file = glob.glob('%s/ocean/%s/ohc/latest/dedrifted/ohc-zonal-sum_Oyr_%s_%s_%s_all.nc' %(mydir, mip, model, experiment, mip))
            #hfbasin_file = glob.glob('%s/ocean/%s/hfbasin/latest/dedrifted/hfbasin-global_Oyr_%s_%s_%s_cumsum-all.nc' %(mydir, inargs.mip, model, experiment, inargs.mip))
    
            time_constraint = gio.get_time_constraint(['1861-01-01', '2005-12-31'])
            anomaly_dict = {}
            metadata_dict = {}

            rndt_cube, anomaly_dict['rndt'], metadata_dict = get_data(rndt_file, 'TOA Incoming Net Radiation',
                                                                      metadata_dict, time_constraint, index, ref_cube=ensemble_ref_cube)

            ref_cube = ensemble_ref_cube if ensemble_ref_cube else rndt_cube
  
            cube, anomaly_dict['hfds'], metadata_dict = get_data(hfds_file, 'surface_downward_heat_flux_in_sea_water',
                                                                 metadata_dict, time_constraint, index, ref_cube=ref_cube)
            cube, anomaly_dict['ohc'], metadata_dict = get_data(ohc_file, 'ocean heat content',
                                                                metadata_dict, time_constraint, index, ref_cube=ref_cube)
            #cube, anomaly_dict['hfbasin'], metadata_dict = get_data(hfbasin_file, 'northward_ocean_heat_transport',
            #                                                        metadata_dict, time_constraint, index)     

            ocean_convergence = anomaly_dict['ohc'] - anomaly_dict['hfds']
            anomaly_dict['hfbasin-inferred'] = ocean_convergence.copy()
            anomaly_dict['hfbasin-inferred'].data = numpy.ma.cumsum(-1 * ocean_convergence.data)
    
            atmos_convergence = anomaly_dict['hfds'] - anomaly_dict['rndt']
            anomaly_dict['hfatmos-inferred'] = atmos_convergence.copy()
            anomaly_dict['hfatmos-inferred'].data = numpy.ma.cumsum(-1 * atmos_convergence.data)

            if nmodels > 1:
                plot_uptake_storage(gs[plot_index], anomaly_dict['ohc'], anomaly_dict['hfds'], anomaly_dict['rndt'], linewidth=0.3, decorate=False)
                plot_transport(gs[plot_index + nexp], None, anomaly_dict['hfbasin-inferred'], anomaly_dict['hfatmos-inferred'], linewidth=0.3, decorate=False) 

            for var in var_list:
                data_dict[var].append(anomaly_dict[var])

        ensemble_dict = {}
        for var in var_list:
            cube_list = iris.cube.CubeList(filter(None, data_dict[var]))
            ensemble_dict[var] = ensemble_mean(cube_list)

        linewidth = None if nmodels == 1 else 4.0
        model_label = 'ensemble' if nmodels > 1 else inargs.models[0]
        experiment_label = 'historicalAA' if experiment == 'historicalMisc' else experiment 
        title = '%s, %s, %s'  %(model_label, experiment_label, mip) 

        plot_uptake_storage(gs[plot_index], ensemble_dict['ohc'], ensemble_dict['hfds'], ensemble_dict['rndt'])
        plt.title(title)
        plot_transport(gs[plot_index + nexp], None, ensemble_dict['hfbasin-inferred'], ensemble_dict['hfatmos-inferred'])   #ensemble_dict['hfbasin']

        plot_index = plot_index + 1

    fig.suptitle('zonally integrated heat accumulation, 1861-2005', fontsize='large')

    #outfile = '/g/data/r87/dbi599/figures/energy-check-zonal/energy-check-zonal_yr_%s_%s_%s_1861-2005.png' %(model_label, experiment_label, mip)
    outfile = 'test.png'
    plt.savefig(outfile, bbox_inches='tight')
    gio.write_metadata(outfile, file_info=metadata_dict)
    print(outfile)


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

    parser.add_argument("models", type=str, nargs='*', help="models")
    parser.add_argument("--experiments", type=str, nargs='*', choices=('historical', 'historicalGHG', 'historicalMisc'), help="experiments")                                  

    args = parser.parse_args()             
    main(args)
