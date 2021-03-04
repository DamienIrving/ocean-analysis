"""Plot spatial P-E"""

import sys
script_dir = sys.path[0]
import os
import pdb
import argparse

import numpy as np
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import cartopy.crs as ccrs
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-2])
module_dir = repo_dir + '/modules'
sys.path.append(module_dir)
try:
    import general_io as gio
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def main(args):
    """Run the program."""

    clim_cube, clim_history = gio.combine_files(args.control_file, args.var)
    clim_cube = clim_cube.collapsed('time', iris.analysis.MEAN)
    clim_cube.remove_coord('time')
    clim_cube.data = clim_cube.data * 86400
    clim_cube.units = 'mm/day'

    anom_cube, anom_history = gio.combine_files(args.cumulative_anomaly_file, args.var)
    time_constraint = gio.get_time_constraint(args.time_bounds)   
    anom_cube = anom_cube.extract(time_constraint)
    start_data = anom_cube.data[0, ::]
    anom_cube = anom_cube[-1, ::] 
    anom_cube.data = anom_cube.data - start_data 

    fig = plt.figure(figsize=(20, 8))
                
    plt.subplot(2, 1, 1, projection=ccrs.PlateCarree(central_longitude=180.0))
    iplt.contourf(clim_cube,
                  levels=np.arange(-7, 8, 1),
                  extend="both",
                  cmap='BrBG')
    cbar = plt.colorbar()
    cbar.set_label('mm/day')  #, rotation=270)
    plt.gca().coastlines()
    lons = np.arange(-180, 180, 0.5)
    lats_sh = np.repeat(-20, len(lons))
    lats_nh = np.repeat(20, len(lons))
    plt.plot(lons, lats_sh, color='0.5') # linestyle, linewidth
    plt.plot(lons, lats_nh, color='0.5')
    plt.title('P-E climatology')
    plt1_ax = plt.gca()

    plt.subplot(2, 1, 2, projection=ccrs.PlateCarree(central_longitude=180.0))
    iplt.contourf(anom_cube,
                  levels=np.arange(-11000, 11050, 1100),
                  extend="both",
                  cmap='RdBu')
    cbar = plt.colorbar()
    cbar.set_label(anom_cube.units)  #, rotation=270)
    plt.gca().coastlines()
    plt.title('Time integrated P-E anomaly (1861-2005)')
    plt2_ax = plt.gca()

    #try:
    #    model = cube.attributes['model_id']
    #except KeyError:
    #    model = cube.attributes['source_id']

    plt.savefig(args.outfile, bbox_inches='tight')

    #metadata_dict = {area_bar_files[0]: area_bar_history[0],
    #                 area_dashed_files[0]: area_dashed_integral_history[0]}
    #log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    #log_file = re.sub('.png', '.met', args.outfile)
    #cmdprov.write_log(log_file, log_text)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("cumulative_anomaly_file", type=str, help="cumulative anomaly file")
    parser.add_argument("control_file", type=str, help="control experiment file for climatology plot")
    parser.add_argument("var", type=str, help="variable")
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
