"""
Filename:     plot_stc_spatial.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot metrics for the subtropical cells

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
from iris.experimental.equalise_cubes import equalise_attributes
import matplotlib.pyplot as plt

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

basin_index = {'pacific': 1,
               'atlantic': 0,
               'globe': 2}
    

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def load_data(infiles, basin):
    """Load, temporally aggregate and spatially slice input data"""
    
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load(infiles, 'ocean_meridional_overturning_mass_streamfunction', callback=save_history)
        equalise_attributes(cube)
        cube = cube.concatenate_cube()
        cube = gio.check_time_units(cube)

        cube = cube[:, basin_index[basin], : ,:]
        cube = timeseries.convert_to_annual(cube)

    assert str(cube.units) == 'kg s-1'
    cube.data = (cube.data / 1023) / 1e+6
    cube.units = 'Sv'

    experiment = cube.attributes['experiment_id']
    
    #depth_constraint = iris.Constraint(depth=lambda cell: cell <= 250)
    #lat_constraint = iris.Constraint(latitude=lambda cell: -30.0 <= cell < 30.0)
    #cube = cube.extract(depth_constraint & lat_constraint)
    
    return cube, experiment


def plot_data(ax, cube, basin):
    """Create the spatial plot."""

    plt.sca(ax)

    clim_cube = cube.collapsed('time', iris.analysis.MEAN)
    #if basin == 'atlantic':
    #    levels = [-1.25e+10, -1.0e+10, -7.5e+9, -5.0e+9, -2.5e+9, 0, 2.5e+9, 5.0e+9, 7.5e+9, 1.0e+10, 1.25e+10]
    #else:
    #    levels = [-5e+10, -4e+10, -3e+10, -2e+10, -1e+10, 0, 1e+10, 2e+10, 3e+10, 4e+10, 5e+10]

    levels = [-16, -14, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16]
    iplt.contourf(clim_cube, cmap='RdBu_r', levels=levels, extend='both')

    cbar = plt.colorbar(orientation='horizontal')
    cbar.set_label(str(clim_cube.units))

    plt.ylabel('depth (%s)' %(cube.coord('depth').units))
    plt.xlabel('latitude')    

    plt.title(basin.title())

    
def main(inargs):
    """Run the program."""

    time_constraint = gio.get_time_constraint(inargs.time)

    width=30
    height=8
    fig = plt.figure(figsize=(width, height))
    ax_dict = {}
    ax_dict['atlantic'] = fig.add_subplot(1, 3, 1)
    ax_dict['pacific'] = fig.add_subplot(1, 3, 2)
    ax_dict['globe'] = fig.add_subplot(1, 3, 3)
    for basin in ['atlantic', 'pacific', 'globe']:
        cube, experiment = load_data(inargs.infiles, basin)
        plot_data(ax_dict[basin], cube, basin)

    title = 'Meridional Overturning Mass Streamfunction, Annual Climatology, %s (%s)'  %(cube.attributes['model_id'], experiment)
    plt.suptitle(title, size='large')
#    plt.subplots_adjust(top=0.90)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infiles[0]: history[0]})


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot a summary of the system heat distribution'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
               
    parser.add_argument("infiles", type=str, nargs='*', help="Input msftmyz files (for a single model/run/experiment)")                                                    
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")

    args = parser.parse_args()             
    main(args)
