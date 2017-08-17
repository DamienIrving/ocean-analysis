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
                value = float(cube.collapsed('time', iris.analysis.MEAN).data)
        color = 'red'
    except iris.exceptions.ConstraintMismatchError:
        value = 0
        color = 'black'
        
    return value, color
        

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
    
    
def plot_toa(axes, infile, hemisphere, bar_width, agg_method, time_constraint):
    """Plot TOA data."""

    rndt_var = 'TOA Incoming Net Flux '+hemisphere+' sum'
    rsdt_var = 'TOA Incident Shortwave Radiation '+hemisphere+' sum'
    rsut_var = 'TOA Outgoing Shortwave Radiation '+hemisphere+' sum'
    rlut_var = 'TOA Outgoing Longwave Radiation '+hemisphere+' sum'
    
    rndt_value, rndt_color = get_data(infile, rndt_var, agg_method, time_constraint)
    rsdt_value, rsdt_color = get_data(infile, rsdt_var, agg_method, time_constraint)
    rsut_value, rsut_color = get_data(infile, rsut_var, agg_method, time_constraint)
    rlut_value, rlut_color = get_data(infile, rlut_var, agg_method, time_constraint)

    values = (rndt_value, rsdt_value, rsut_value, rlut_value)
    edge_colors = (rndt_color, rsdt_color, rsut_color, rlut_color)

    ind = numpy.arange(len(values))  # the x locations for the groups
    col = 0 if (hemisphere == 'sh') else 1 
    axes[0, col].bar(ind, values, bar_width,
                     color=[edge_colors[0], 'None', 'None', 'None'],
                     edgecolor=edge_colors,
                     tick_label=['rndt', 'rsdt', 'rsut', 'rlut'],
                     linewidth=1.0)


def plot_atmos(axes, infile, hemisphere, bar_width, agg_method, time_constraint):
    """Plot radiative surface fluxes over the ocean."""

    ## FIXME: Change the input file so it gives net shortwave and longwave

    rns_var = 'Surface Net Radiation in Air '+hemisphere+' ocean sum'
    rsns_var = 'Surface Net Shortwave Radiation in Air '+hemisphere+' ocean sum'
    rlus_var = 'Surface Net Longwave Radiation in Air '+hemisphere+' ocean sum'
    
    rns_value, rns_color = get_data(infile, rns_var, agg_method, time_constraint)
    rsns_value, rsns_color = get_data(infile, rsns_var, agg_method, time_constraint)
    rlus_value, rlus_color = get_data(infile, rlus_var, agg_method, time_constraint)

    values = (rns_value, rsns_value, rlus_value)
    edge_colors = (rns_color, rsns_color, rlus_color)

    ind = numpy.arange(len(values))  # the x locations for the groups
    col = 0 if (hemisphere == 'sh') else 1 
    axes[1, col].bar(ind, values, bar_width,
                     color=[edge_colors[0], 'None', 'None'],
                     edgecolor=edge_colors,
                     tick_label=['rns', 'rsns', 'rlus'],
                     linewidth=1.0)



def main(inargs):
    """Run the program."""
  
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()    

    fig, axes = setup_plot()
    bar_width = 0.7
    
    plot_toa(axes, inargs.infile, 'sh', bar_width, inargs.aggregation, time_constraint)
    plot_toa(axes, inargs.infile, 'nh', bar_width, inargs.aggregation, time_constraint)

    plot_atmos(axes, inargs.infile, 'sh', bar_width, inargs.aggregation, time_constraint)
    plot_atmos(axes, inargs.infile, 'nh', bar_width, inargs.aggregation, time_constraint)

    fig.tight_layout()
    fig.subplots_adjust(left=0.15, top=0.95)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile)    #, file_info=metadata_dict)


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
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1850-01-01', '2005-12-31'),
                        help="Time period [default = 1850-2005]")

    args = parser.parse_args()             
    main(args)
