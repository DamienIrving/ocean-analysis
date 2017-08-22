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

column_number = {'sh': 0, 'nh': 1}


def setup_plot(exclude_ocean=False):
    """Set the plot axes and headings."""

    cols = ['Southern Hemisphere', 'Northern Hemisphere']
    rows = ['TOA / Atmosphere', 'Surface']

    if exclude_ocean:
        height = 6
        nrows = 2
    else:
        rows.append('Ocean')
        height = 9
        nrows = 3

    fig = plt.figure(figsize=(14, 9))
    axes1 = fig.add_subplot(nrows, 2, 1)
    axes2 = fig.add_subplot(nrows, 2, 2, sharey=axes1)
    axes3 = fig.add_subplot(nrows, 2, 3)
    axes4 = fig.add_subplot(nrows, 2, 4, sharey=axes3)

    if exclude_ocean:
        axes = numpy.array([(axes1, axes2), (axes3, axes4)])
    else:
        axes5 = fig.add_subplot(nrows, 2, 5)
        axes6 = fig.add_subplot(nrows, 2, 6, sharey=axes5)
        axes = numpy.array([(axes1, axes2), (axes3, axes4), (axes5, axes6)])

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


def calc_dohc_dt(cube):
    """Calculate dOHC/dt.
    
    This value is comparable to the heat and radiative flux terms.
    
    """
    
    dohc = numpy.cumsum(cube.data - cube.data[0])
    dt = numpy.arange(0, 365.25 * len(dohc), 365.25) * 60 * 60 * 24
    dohc_dt = dohc[1:] / dt[1:]
    
    dohc_dt_cube = cube[1:].copy()
    dohc_dt_cube.data = dohc_dt   # temporary fix: * 60 * 60 * 24 * 365
    
    units = str(dohc_dt_cube.units)
    dohc_dt_cube.units = units.replace('J', 'W')
    
    return dohc_dt_cube


def get_data(infile, var, agg_method, time_constraint, ohc=False):
    """Read and temporally aggregate the data."""
    
    try:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(infile, var & time_constraint)
            
            if ohc:
                cube = calc_dohc_dt(cube)
            
            if agg_method == 'trend':
                value = timeseries.calc_trend(cube, per_yr=True)
            elif agg_method == 'climatology':
                value = float(cube.collapsed('time', iris.analysis.MEAN).data)
        if 'land' in var:
            color = 'green'
        elif 'ocean' in var:
            color = 'blue'
        else:
            color = 'black'
    except iris.exceptions.ConstraintMismatchError:
        value = 0
        color = '0.5'
        
    return value, color
        

#def get_title(cube_dict):
#    """Get the plot title."""
#
#    for cube in cube_dict.values():
#        if cube:
#            run = 'r%si%sp%s'  %(cube.attributes['realization'], cube.attributes['initialization_method'], cube.attributes['physics_version'])
#            title = 'Energy budget for %s, %s, %s'  %(cube.attributes['model_id'], cube.attributes['experiment'], run)
#            break
#    
#    return title

    
def plot_atmos(axes, infile, hemisphere, bar_width, agg_method, time_constraint):
    """Plot TOA and atmosphere data."""

    rsdt_var = 'TOA Incident Shortwave Radiation '+hemisphere+' sum'
    rsut_var = 'TOA Outgoing Shortwave Radiation '+hemisphere+' sum'
    rsaa_var = 'Atmosphere Absorbed Shortwave Flux '+hemisphere+' sum'
    rsns_var = 'Surface Net Shortwave Flux in Air '+hemisphere+' sum'

    rsdt_value, rsdt_color = get_data(infile, rsdt_var, agg_method, time_constraint)
    rsut_value, rsut_color = get_data(infile, rsut_var, agg_method, time_constraint)
    rsaa_value, rsaa_color = get_data(infile, rsaa_var, agg_method, time_constraint)
    rsns_value, rsns_color = get_data(infile, rsns_var, agg_method, time_constraint)

    values = (rsdt_value, rsut_value, rsaa_value, rsns_value)
    edge_colors = (rsdt_color, rsut_color, rsaa_color, rsns_color)

    ind = numpy.arange(len(values))  # the x locations for the groups
    col = column_number[hemisphere] 
    axes[0, col].bar(ind, values, bar_width,
                     color=['None', 'None', 'None', edge_colors[-1]],
                     edgecolor=edge_colors,
                     tick_label=['rsdt', 'rsut', 'rsaa', 'rsns'],
                     linewidth=1.0)


def plot_surface(axes, infile, hemisphere, bar_width, agg_method, time_constraint):
    """Plot radiative surface fluxes."""

    values = []
    edge_colors = []
    fill_colors = []
    tick_labels = []
    for realm in ['', ' ocean', ' land']:
        rsns_var = 'Surface Net Shortwave Flux in Air ' + hemisphere + realm + ' sum'
        hfss_var = 'Surface Upward Sensible Heat Flux ' + hemisphere + realm + ' sum'
        hfls_var = 'Surface Upward Latent Heat Flux ' + hemisphere + realm + ' sum'
        rlns_var = 'Surface Net Longwave Flux in Air ' + hemisphere +realm + ' sum'
        if realm == '':
            hfds_var = 'Downward Heat Flux at Sea Water Surface ' + hemisphere + ' ocean sum'
        else:
            hfds_var = 'Downward Heat Flux at Sea Water Surface ' + hemisphere + realm + ' sum'
    
        rsns_value, rsns_color = get_data(infile, rsns_var, agg_method, time_constraint)
        hfss_value, hfss_color = get_data(infile, hfss_var, agg_method, time_constraint)
        hfls_value, hfls_color = get_data(infile, hfls_var, agg_method, time_constraint)
        hfds_value, hfds_color = get_data(infile, hfds_var, agg_method, time_constraint)
        rlns_value, rlns_color = get_data(infile, rlns_var, agg_method, time_constraint)

        values.extend([rsns_value, hfss_value, hfls_value, hfds_value, rlns_value])
        edge_colors.extend([rsns_color, hfss_color, hfls_color, hfds_color, rlns_color])
        fill_colors.extend([rsns_color, 'None', 'None', 'None', 'None'])
        tick_labels.extend(['rsns', 'hfss', 'hfls', 'hfds', 'rlns'])

    ind = numpy.arange(len(values))  # the x locations for the groups
    col = column_number[hemisphere] 
    axes[1, col].bar(ind, values, bar_width,
                     color=fill_colors,
                     edgecolor=edge_colors,
                     tick_label=tick_labels,
                     linewidth=1.0)


def plot_ocean(axes, infile, hemisphere, bar_width, agg_method, time_constraint):
    """Plot ocean data."""

    hfds_var = 'Downward Heat Flux at Sea Water Surface ' + hemisphere + ' ocean sum'
    ohc_var = 'ocean heat content ' + hemisphere + ' sum'
    
    hfds_value, hfds_color = get_data(infile, hfds_var, agg_method, time_constraint)
    ohc_value, ohc_color = get_data(infile, ohc_var, agg_method, time_constraint, ohc=True)

    values = (hfds_value, ohc_value)
    edge_colors = (hfds_color, ohc_color)

    ind = numpy.arange(len(values))  # the x locations for the groups
    col = column_number[hemisphere] 
    axes[2, col].bar(ind, values, bar_width,
                     color=[hfds_color, 'None'],
                     edgecolor=edge_colors,
                     tick_label=['hfds', 'dOHC/dt'],
                     linewidth=1.0)


def main(inargs):
    """Run the program."""

    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()    

    fig, axes = setup_plot(inargs.exclude_ocean)
    bar_width = 0.7
    
    for hemisphere in ['sh', 'nh']:
        plot_atmos(axes, inargs.infile, hemisphere, bar_width, inargs.aggregation, time_constraint)
        plot_surface(axes, inargs.infile, hemisphere, bar_width, inargs.aggregation, time_constraint)
        if not inargs.exclude_ocean:
            plot_ocean(axes, inargs.infile, hemisphere, bar_width, inargs.aggregation, time_constraint)

    fig.tight_layout()
    fig.subplots_adjust(left=0.15, top=0.95)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infile: iris.load(inargs.infile)[0].attributes['history']})


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
                                     
    parser.add_argument("infile", type=str, 
                        help="Input energy budget file generated from calc_system_heat_distribution.py")                                     
    parser.add_argument("outfile", type=str, help="Output file")                                     

    parser.add_argument("--aggregation", type=str, default='trend', choices=('trend', 'climatology'),
                        help="Method used to aggregate over time [default = trend]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1850-01-01', '2005-12-31'),
                        help="Time period [default = 1850-2005]")

    parser.add_argument("--exclude_ocean", action="store_true", default=False,
                        help="Leave out the ocean plot [default=False]")

    args = parser.parse_args()             
    main(args)
