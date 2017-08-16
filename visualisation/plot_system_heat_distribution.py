"""
Filename:     plot_system_heat_distribution.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the system heat distribution

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_data(infile, var, agg_method, time_constraint):
    """Read and temporally aggregate the data."""
    
    try:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(infile, var & time_constraint)
            if agg_method == 'trend':
                value = timeseries.calc_trend(cube, per_yr=True)
            elif agg_method == 'climatology':
                value = cube.collapsed('time', iris.analysis.MEAN)
    except:
        value = None
        
    return value
        

def get_title(cube_dict):
    """Get the plot title."""

    for cube in cube_dict.values():
        if cube:
            run = 'r%si%sp%s'  %(cube.attributes['realization'], cube.attributes['initialization_method'], cube.attributes['physics_version'])
            title = 'Energy budget for %s, %s, %s'  %(cube.attributes['model_id'], cube.attributes['experiment'], run)
            break
    
    return title


def setup_plot():
    """Set the plot axes and headings."""

    cols = ['Southern Hemisphere', 'Northern Hemisphere']
    rows = ['TOA', 'Surface radiation', 'Surface heat', 'Ocean']

    fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(8, 12))
    pad = 5 # in points

    for ax, col in zip(axes[0], cols):
        ax.annotate(col, xy=(0.5, 1), xytext=(0, pad),
                    xycoords='axes fraction', textcoords='offset points',
                    size='large', ha='center', va='baseline')

    for ax, row in zip(axes[:,0], rows):
        ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
                    xycoords=ax.yaxis.label, textcoords='offset points',
                    size='large', ha='right', va='center', rotation='vertical')

    return fig, axes
    
    
def plot_toa(infile, hemisphere, bar_width, agg_method, time_constraint):
    """Plot TOA data."""

    rndt_var = 'TOA Incoming Net Flux '+hemisphere+' sum'
    rsdt_var = 'TOA Incident Shortwave Radiation '+hemisphere+' sum'
    rsut_var = 'TOA Outgoing Shortwave Radiation '+hemisphere+' sum'
    rlut_var = 'TOA Outgoing Longwave Radiation '+hemisphere+' sum'
    
    rndt_value = get_data(infile, rndt_var, agg_method, time_constraint)
    rsdt_value = get_data(infile, rsdt_var, agg_method, time_constraint)
    rsut_value = get_data(infile, rsut_var, agg_method, time_constraint)
    rlut_value = get_data(infile, rlut_var, agg_method, time_constraint)

    toa_values = (rndt_value, rsdt_value, rsut_value, rlut_value)

    ind = numpy.arange(len(toa_values))  # the x locations for the groups
    col = 0 if (hemisphere == 'sh') else 1 
    axes[0, col].bar(ind, toa_values, bar_width,
                     color=['r', 'None', 'None', 'None'],
                     edgecolor=['r', 'r', 'b', 'b'],
                     tick_label=['rndt', 'rsdt', 'rsut', 'rlut'],
                     linewidth=1.0)
    

def main(inargs):
    """Run the program."""
  
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()    

    fig, axes = setup_plot()
    bar_width = 0.7
    
    plot_toa(inargs.infile, 'sh', bar_width, inargs.aggregation, time_contraint)

    fig.tight_layout()
    fig.subplots_adjust(left=0.15, top=0.95)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot the system heat distribution'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                     
    parser.add_argument("infile", type=str, help="Input energy budget file generated from calc_system_heat_distribution.py")                                     
    parser.add_argument("outfile", type=str, help="Output file")                                     

    parser.add_argument("--aggregation", type=str, default='trend', choices=('trend', 'climatology'),
                        help="Method used to aggregate over time [default = trend]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")

    args = parser.parse_args()             
    main(args)
