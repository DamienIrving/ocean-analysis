"""
Filename:     plot_zonal_toa_breakdown.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  

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
                    anomaly.coord('latitude').bounds = ref_cube.coord('latitude').bounds

        new_aux_coord = iris.coords.AuxCoord(ensemble_number, long_name='ensemble_member', units='no_unit')
        anomaly.add_aux_coord(new_aux_coord)
    else:
        cube = None
        anomaly = None
        final_value = None
    
    return cube, anomaly, metadata_dict


def plot_breakdown(gs, rndt_anomaly, rsdt_anomaly, rsut_anomaly, rlut_anomaly, linewidth=None, decorate=True, ylim=True):
    """Plot netTOA and its component parts"""

    ax = plt.subplot(gs)
    plt.sca(ax)

    if decorate:
        labels = ['netTOA', 'rsdt', 'rsut', 'rlut']
    else:
        labels = [None, None, None, None]

    iplt.plot(rndt_anomaly, color='black', label=labels[0], linewidth=linewidth)
    iplt.plot(rsdt_anomaly, color='yellow', label=labels[1], linewidth=linewidth)
    iplt.plot(rsut_anomaly * -1, color='orange', label=labels[2], linewidth=linewidth)
    iplt.plot(rlut_anomaly * -1, color='purple', label=labels[3], linewidth=linewidth)

    if ylim:
        ylower, yupper = ylim
        plt.ylim(ylower * 1e22, yupper * 1e22)

    if decorate:
        plt.ylabel('$J \; lat^{-1}$')
        plt.xlim(-90, 90)

        plt.axhline(y=0, color='0.5', linestyle='--')
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
    fig = plt.figure(figsize=[11 * nexp, 14])
    gs = gridspec.GridSpec(2, nexp)

    nmodels = len(inargs.models)
    ensemble_ref_cube = ensemble_grid() if nmodels > 1 else None

    var_list = ['rndt', 'rsdt', 'rsut', 'rlut']
    plot_index = 0
    time_constraint = gio.get_time_constraint(inargs.time)
    time_text = get_time_text(inargs.time)
    ensemble_dict = {}
    for experiment in inargs.experiments:
        data_dict = {}
        for var in var_list:
            data_dict[var] = iris.cube.CubeList([])
 
        for index, model in enumerate(inargs.models):
            mip = 'r1i1' + aa_physics[model] if experiment == 'historicalMisc' else 'r1i1p1'
            dir_exp = experiment.split('-')[-1]
            file_exp = 'historical-' + experiment if experiment[0:3] == 'rcp' else experiment

            mydir = '/g/data/r87/dbi599/DRSv2/CMIP5/%s/%s/yr'  %(model, dir_exp)

            rndt_file = glob.glob('%s/atmos/%s/rndt/latest/dedrifted/rndt-zonal-sum_Ayr_%s_%s_%s_cumsum-all.nc' %(mydir, mip, model, file_exp, mip))
            rsdt_file = glob.glob('%s/atmos/%s/rsdt/latest/dedrifted/rsdt-zonal-sum_Ayr_%s_%s_%s_cumsum-all.nc' %(mydir, mip, model, file_exp, mip))
            rsut_file = glob.glob('%s/atmos/%s/rsut/latest/dedrifted/rsut-zonal-sum_Ayr_%s_%s_%s_cumsum-all.nc' %(mydir, mip, model, file_exp, mip))
            rlut_file = glob.glob('%s/atmos/%s/rlut/latest/dedrifted/rlut-zonal-sum_Ayr_%s_%s_%s_cumsum-all.nc' %(mydir, mip, model, file_exp, mip))
    
            anomaly_dict = {}
            metadata_dict = {}

            rndt_cube, anomaly_dict['rndt'], metadata_dict = get_data(rndt_file, 'TOA Incoming Net Radiation', metadata_dict, time_constraint, index, ref_cube=ensemble_ref_cube)
            rsdt_cube, anomaly_dict['rsdt'], metadata_dict = get_data(rsdt_file, 'toa_incoming_shortwave_flux', metadata_dict, time_constraint, index, ref_cube=ensemble_ref_cube)
            rsut_cube, anomaly_dict['rsut'], metadata_dict = get_data(rsut_file, 'toa_outgoing_shortwave_flux', metadata_dict, time_constraint, index, ref_cube=ensemble_ref_cube)
            rlut_cube, anomaly_dict['rlut'], metadata_dict = get_data(rlut_file, 'toa_outgoing_longwave_flux', metadata_dict, time_constraint, index, ref_cube=ensemble_ref_cube)

            if nmodels > 1:
                plot_breakdown(gs[plot_index], anomaly_dict['rndt'], anomaly_dict['rsdt'], anomaly_dict['rsut'], anomaly_dict['rlut'],
                               linewidth=0.3, decorate=False, ylim=inargs.ylim)

            for var in var_list:
                data_dict[var].append(anomaly_dict[var])

        ensemble_dict[experiment] = {}
        for var in var_list:
            cube_list = iris.cube.CubeList(filter(None, data_dict[var]))
            ensemble_dict[experiment][var] = ensemble_mean(cube_list)

        linewidth = None if nmodels == 1 else 4.0
        model_label = 'ensemble' if nmodels > 1 else inargs.models[0]
        experiment_label = 'historicalAA' if experiment == 'historicalMisc' else experiment  

        plot_breakdown(gs[plot_index], ensemble_dict[experiment]['rndt'], ensemble_dict[experiment]['rsdt'],
                       ensemble_dict[experiment]['rsut'], ensemble_dict[experiment]['rlut'], ylim=inargs.ylim)
        plt.title(experiment_label)

        plot_index = plot_index + 1
        
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

    parser.add_argument("--ylim", type=float, nargs=2, default=None,
                        help="y limits for plots (x 10^22)")
 

    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()             
    main(args)
