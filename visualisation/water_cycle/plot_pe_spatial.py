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


def get_cube_list(infiles, agg, time_bounds=None, quick=False):
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
        elif quick:
            cube = cube[0:120, ::]
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
    
    return ensemble_cube_list, history


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


def plot_data(ax, ensemble_mean, ensemble_agreement, agg, title,
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
    else:
        cmap = 'RdBu'
        levels = np.arange(-9000, 9100, 1500)
        cbar_label = 'Time-integrated P-E anomaly, 1861-2005 (kg m-2)'
        
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

    clim_cube_list, clim_history = get_cube_list(args.clim_files, 'clim', quick=args.quick)
    clim_ensemble_mean, clim_ensemble_agreement = ensemble_stats(clim_cube_list)
    clim_ensemble_mean.data = clim_ensemble_mean.data * 86400

    ghg_cube_list, ghg_history = get_cube_list(args.ghg_files, 'anom', time_bounds=args.time_bounds)
    ghg_ensemble_mean, ghg_ensemble_agreement = ensemble_stats(ghg_cube_list)

    aa_cube_list, aa_history = get_cube_list(args.aa_files, 'anom', time_bounds=args.time_bounds)
    aa_ensemble_mean, aa_ensemble_agreement = ensemble_stats(aa_cube_list)

    hist_cube_list, hist_history = get_cube_list(args.hist_files, 'anom', time_bounds=args.time_bounds)
    hist_ensemble_mean, hist_ensemble_agreement = ensemble_stats(hist_cube_list)

    width = 25
    height = 10
    fig = plt.figure(figsize=[width, height])
    outproj = ccrs.PlateCarree(central_longitude=180.0) 

    nrows = 2
    ncols = 2
    ax1 = plt.subplot(nrows, ncols, 1, projection=outproj)
    plot_data(ax1,
              clim_ensemble_mean,
              clim_ensemble_agreement,
              'clim',
              '(a) piControl',
              agreement_bounds=[0.33, 0.66])

    ax2 = plt.subplot(nrows, ncols, 2, projection=outproj)
    plot_data(ax2,
              ghg_ensemble_mean,
              ghg_ensemble_agreement,
              'anom',
              '(b) GHG-only',
              agreement_bounds=[0.33, 0.66],
              clim=clim_ensemble_mean)

    ax3 = plt.subplot(nrows, ncols, 3, projection=outproj)
    plot_data(ax3,
              aa_ensemble_mean,
              aa_ensemble_agreement,
              'anom',
              '(c) AA-only',
              agreement_bounds=[0.33, 0.66],
              clim=clim_ensemble_mean)

    ax4 = plt.subplot(nrows, ncols, 4, projection=outproj)
    plot_data(ax4,
              hist_ensemble_mean,
              hist_ensemble_agreement,
              'anom',
              '(d) historical',
              agreement_bounds=[0.33, 0.66],
              clim=clim_ensemble_mean)

    fig.tight_layout()
    fig.subplots_adjust(wspace=-0.15, hspace=0.2)
    plt.savefig(args.outfile, bbox_inches='tight', dpi=300)
    metadata_dict = {args.ghg_files[-1]: ghg_history[-1],
                     args.clim_files[-1]: clim_history[-1]}
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', args.outfile)
    cmdprov.write_log(log_file, log_text)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--clim_files", type=str, nargs='*', help="climatology files")
    parser.add_argument("--ghg_files", type=str, nargs='*', help="time-integrated anomaly files for GHG-only experiment")
    parser.add_argument("--aa_files", type=str, nargs='*', help="time-integrated anomaly files for AA-only experiment")
    parser.add_argument("--hist_files", type=str, nargs='*', help="time-integrated anomaly files for historical experiment")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        default=['1861-01-01', '2005-12-31'],
                        help="Time period")
    parser.add_argument("--quick", action="store_true", default=False,
                        help="Use only first 10 years of clim files")

    args = parser.parse_args()             
    main(args)
