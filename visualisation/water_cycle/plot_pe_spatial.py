"""Plot spatial P-E"""

import re
import sys
script_dir = sys.path[0]
import os
import pdb
import argparse

import numpy as np
import matplotlib.pyplot as plt
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import cartopy.crs as ccrs
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-2])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
    import timeseries
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def regrid(cube):
    """Define the sample points for interpolation"""

    lats = list(np.arange(-89, 90, 2))
    lons = list(np.arange(1, 360, 2))
    
    sample_points = []
    coord_names = [coord.name() for coord in cube.dim_coords]
    if 'time' in coord_names:
        coord_names.remove('time')

    for coord in coord_names:
        if 'lat' in coord:
            sample_points.append((coord, lats))
        elif 'lon' in coord:
            sample_points.append((coord, lons))

    cube = cube.interpolate(sample_points, iris.analysis.Linear())
    cube.coord('latitude').guess_bounds()
    cube.coord('longitude').guess_bounds()
    
    cube.coord('latitude').standard_name = 'latitude'
    cube.coord('latitude').long_name = 'latitude'
    cube.coord('latitude').var_name = 'lat'
    cube.coord('latitude').units = 'degrees_north'
    cube.coord('latitude').attributes = {}
                               
    cube.coord('longitude').standard_name = 'longitude'
    cube.coord('longitude').long_name = 'longitude'
    cube.coord('longitude').var_name = 'lon'
    cube.coord('longitude').units = 'degrees_east'
    cube.coord('longitude').circular = True
    cube.coord('longitude').attributes = {}
        
    return cube


def get_cube_list(infiles, agg, time_bounds=None):
    """Read and process data."""

    assert agg in ['clim', 'anom']
    
    ensemble_cube_list = iris.cube.CubeList([])
    for ensnum, ensemble_member in enumerate(infiles):
        print(ensemble_member)
        cube, history = gio.combine_files(ensemble_member,
                                          'precipitation_minus_evaporation_flux',
                                          new_calendar='365_day')
        cube = gio.check_time_units(cube)
        if time_bounds:
            time_constraint = gio.get_time_constraint(time_bounds) 
            cube = cube.extract(time_constraint)
        if agg == 'clim':
            cube = timeseries.convert_to_annual(cube, aggregation='mean', days_in_month=True)
            cube = cube.collapsed('time', iris.analysis.MEAN)
        elif agg == 'anom':
            start_data = cube.data[0, ::]
            cube = cube[-1, ::]
            cube.data = cube.data - start_data 
        cube.remove_coord('time') 
        cube = regrid(cube)
        new_aux_coord = iris.coords.AuxCoord(ensnum, long_name='ensemble_member', units='no_unit')
        cube.add_aux_coord(new_aux_coord)
        cube.cell_methods = ()
        ensemble_cube_list.append(cube)
        print("Total number of models:", len(ensemble_cube_list))
    
    return ensemble_cube_list


def ensemble_stats(cube_list):
    """Get the ensemble mean and sign agreement"""
    
    equalise_attributes(cube_list)
    ensemble_cube = cube_list.merge_cube()
    
    ensemble_mean = ensemble_cube.collapsed('ensemble_member', iris.analysis.MEAN, mdtol=0)
    ensemble_mean.remove_coord('ensemble_member')
    
    ensemble_agreement = ensemble_mean.copy()
    nmodels = ensemble_cube.shape[0]
    pos_data = ensemble_cube.data > 0.0
    ensemble_agreement.data = pos_data.sum(axis=0) / nmodels
    
    return ensemble_mean, ensemble_agreement


def plot_data(ax, ensemble_mean, ensemble_agreement, agg,
              agreement_bounds=None, clim=None):
    """Plot ensemble data"""

    assert agg in ['clim', 'anom']
    inproj = ccrs.PlateCarree()                  
                       
    plt.sca(ax)
    plt.gca().set_global()
    if agg == 'clim':
        cmap = 'BrBG'
        levels = np.arange(-7, 8, 1)
        cbar_label = 'Annual mean P-E (mm/day)'
        title = 'Climatology' 
    else:
        cmap = 'RdBu'
        levels = np.arange(-11000, 11050, 1100)
        cbar_label = 'Time-integrated anomaly (kg m-2)'
        title = "Time-integrated anomaly"
        
    x = ensemble_mean.coord('longitude').points
    y = ensemble_mean.coord('latitude').points
    cf = ax.contourf(x, y, ensemble_mean.data,
                     transform=inproj,  
                     cmap=cmap,
                     levels=levels,
                     extend='both')

    if agreement_bounds:
        hatch_data = ensemble_agreement.data
        ax.contourf(x, y, hatch_data,
                    transform=inproj, 
                    colors='none',
                    levels=agreement_bounds,
                    hatches=['\\\\'],) # # '.', '/', '\\', '\\\\', '*'
    
    if clim:
        ce = ax.contour(x, y, clim.data,
                        transform=inproj,
                        colors=['goldenrod', 'black', 'green'],
                        levels=np.array([-2, 0, 2]))
        
    cbar = plt.colorbar(cf)
    cbar.set_label(cbar_label)   #, fontsize=label_size)
    # cbar.ax.tick_params(labelsize=number_size)
    plt.gca().coastlines()
    ax.set_title(title)
    if agg == 'clim':
        lons = np.arange(-180, 180, 0.5)
        lats_sh = np.repeat(-20, len(lons))
        lats_nh = np.repeat(20, len(lons))
        plt.plot(lons, lats_sh, color='0.5') # linestyle, linewidth
        plt.plot(lons, lats_nh, color='0.5')


def main(args):
    """Run the program."""

    anom_cube_list = get_cube_list(args.anom_files, 'anom', time_bounds=['1861-01-01', '2005-12-31'])
    anom_ensemble_mean, anom_ensemble_agreement = ensemble_stats(anom_cube_list)

    clim_cube_list = get_cube_list(args.clim_files, 'clim')
    clim_ensemble_mean, clim_ensemble_agreement = ensemble_stats(clim_cube_list)
    clim_ensemble_mean.data = clim_ensemble_mean.data * 86400

    nrows = 2
    ncols = 1
    fig = plt.figure(figsize=[30, 6])
    outproj = ccrs.PlateCarree(central_longitude=180.0) 

    ax1 = plt.subplot(nrows, ncols, 1, projection=outproj)
    plot_data(ax1,
              clim_ensemble_mean,
              clim_ensemble_agreement,
              'clim',
              agreement_bounds=[0.33, 0.66])

    ax2 = plt.subplot(nrows, ncols, 2, projection=outproj)
    plot_data(ax2,
              anom_ensemble_mean,
              anom_ensemble_agreement,
              'anom',
              agreement_bounds=[0.33, 0.66],
              clim=clim_ensemble_mean)

    plt.savefig(args.outfile, bbox_inches='tight')

    metadata_dict = {args.cumulative_anomaly_file: anom_history,
                     args.control_file: clim_history}
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', args.outfile)
    cmdprov.write_log(log_file, log_text)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--anom_files", type=str, nargs='*', help="time-integrated anomaly files")
    parser.add_argument("--clim_files", type=str, nargs='*', help="climatology files")

#    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
#                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
