"""
Filename:     plot_stc_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot metrics for the subtropical cells

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
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
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

experiment_colors = {'historical': 'orange',
                     'historicalGHG': 'red',
                     'historicalAA': 'blue',
                     'rcp26': '#16DB65',
                     'rcp45': '#058C42',
                     'rcp60': '#04471C',
                     'rcp85': '#0D2818'}

basin_index = {'pacific': 0,
               'atlantic': 1,
               'globe': 2}


def plot_total(ax, tropics_metric, experiment):
    """Plot total STC metric."""
    
    plt.sca(ax)
    
    iplt.plot(tropics_metric, label=experiment,
              color=experiment_colors[experiment])
    plt.legend()
 

def plot_diff(ax, nmetric, smetric, filenum):
    """Plot interhemispheric difference."""
    
    plt.sca(ax)
    
    iplt.plot(nmetric, color='red', label='NH')
    iplt.plot(-1 * smetric, color='blue', label='SH')
    if filenum == 0:
        plt.legend()


def calc_metrics(sh_cube, nh_cube):
    """Calculate the metrics."""
    
    dim_coord_names = [coord.name() for coord in sh_cube.dim_coords]
    vert_extents = spatial_weights.calc_vertical_weights_1D(sh_cube.coord('depth'),
                                                            dim_coord_names,
                                                            sh_cube.shape)
    
    nh_cube.data = numpy.where(nh_cube.data > 0, nh_cube.data, 0)
    sh_cube.data = numpy.where(sh_cube.data < 0, sh_cube.data, 0)
    
    nh_metric = nh_cube.collapsed(['depth', 'latitude'], iris.analysis.SUM, weights=vert_extents)
    sh_metric = sh_cube.collapsed(['depth', 'latitude'], iris.analysis.SUM, weights=vert_extents)
    
    tropics_metric = nh_metric - sh_metric

    return tropics_metric, sh_metric, nh_metric
    

def load_data(infile, basin):
    """Load, temporally aggregate and spatially slice input data"""
    
    cube = iris.load_cube(infile, 'ocean_meridional_overturning_mass_streamfunction')
    cube = cube[:, basin_index[basin], : ,:]
    cube = timeseries.convert_to_annual(cube)
    experiment = cube.attributes['experiment_id']
    
    depth_constraint = iris.Constraint(depth= lambda cell: cell <= 250)
    sh_constraint = iris.Constraint(latitude=lambda cell: -30.0 <= cell < 0.0)
    nh_constraint = iris.Constraint(latitude=lambda cell: 0.0 < cell <= 30.0)

    sh_cube = cube.extract(depth_constraint & sh_constraint)
    nh_cube = cube.extract(depth_constraint & nh_constraint)
    
    return sh_cube, nh_cube, experiment

    
def main(inargs):
    """Run the program."""

    time_constraints = {}
    time_constraints['historical'] = gio.get_time_constraint(inargs.hist_time)
    time_constraints['rcp'] = gio.get_time_constraint(inargs.rcp_time)

    width=10
    height=15
    fig = plt.figure(figsize=(width, height))
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    for filenum, infile in enumerate(inargs.infiles):
        sh_cube, nh_cube, experiment = load_data(infile, inargs.basin)
        tropics_metric, sh_metric, nh_metric = calc_metrics(sh_cube, nh_cube)
        plot_total(ax1, tropics_metric, experiment)
        plot_diff(ax2, nh_metric, sh_metric, filenum)

    title = '%s'  %(sh_cube.attributes['model_id'])
    plt.suptitle(title, size='large')
#    plt.subplots_adjust(top=0.90)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infiles[-1]: sh_cube.attributes['history']})


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
               
    parser.add_argument("infiles", type=str, nargs='*', 
                        help="Input msftmyz files")                                                    
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--basin", type=str, choices=('atlantic', 'pacific', 'globe'), default='globe',
                        help="Ocean basin")

    parser.add_argument("--hist_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")
    parser.add_argument("--rcp_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")

    args = parser.parse_args()             
    main(args)
