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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

column_number = {'sh': 0, 'nh': 1}
ylabels = {'climatology': 'W', 'trend': '$W \: yr^{-1}$'}

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

    fig = plt.figure(figsize=(14, 10))  # width, height
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


def calc_dohc_dt(ohc_cube):
    """Calculate dOHC/dt.
    
    This value is comparable to the heat and radiative flux terms.
    
    Estimate is calculated by taking derivative of fitted polynomial.
      (This seems to work better than dividing the OHC anomaly 
      timeseries by dt, which is something that was noted by
      Nummelin et al (2016))

    I've gone with a cubic polynomial, but you get exactly the same
      end result (i.e. trend in dOHC/dt) using a quadratic, which
      is what Nummelin did.

    polyfit returns [d, c, b, a] corresponding to y = a + bt + ct^2 + dt^3
      (the derviative is then dy/dt = b + 2ct + 3dt^2)

    """

    time_axis = timeseries.convert_to_seconds(ohc_cube.coord('time')).points
    
    coef_d, coef_c, coef_b, coef_a = numpy.ma.polyfit(time_axis, ohc_cube.data, 3)
    dohc_dt_data = coef_b + (2 * coef_c * time_axis) + (3 * coef_d * time_axis**2)
        
    dohc_dt_cube = ohc_cube.copy()
    dohc_dt_cube.data = dohc_dt_data

    units = str(dohc_dt_cube.units)
    dohc_dt_cube.units = units.replace('J', 'W')
    
    return dohc_dt_cube


def select_control_segment(cube, branch_time, nyears):
    """Select the right time segment of the control run.

    Assumes annual timescale data (and that the branch times are expressed in months)

    The branch time represents the start of the year, while the first data time mid-year.
      Hence the adjustment by 182.5

    """

    assert cube.attributes['experiment_id'] == 'piControl'
    time_values = cube.coord('time').points - 182.5 
    start_index, error = uconv.find_nearest(time_values, branch_time, index=True)

    cube = cube[start_index : int(start_index + nyears)]

    return cube


def get_data(infile, var, agg_method, time_constraint, ohc=False, branch=None):
    """Read and temporally aggregate the data."""
    
    try:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(infile, var & time_constraint)
 
            if branch:
                branch_time, nyears = branch
                cube = select_control_segment(cube, branch_time, nyears)
                         
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
        

def set_title(infile):
    """Get the plot title."""

    cube = iris.load(infile)
    run = 'r%si%sp%s'  %(cube[0].attributes['realization'], cube[0].attributes['initialization_method'], cube[0].attributes['physics_version'])
    title = 'Energy budget for %s, %s, %s'  %(cube[0].attributes['model_id'], cube[0].attributes['experiment'], run)
    
    plt.suptitle(title, size='x-large')

    
def plot_atmos(axes, infile, hemisphere, bar_width, agg_method, time_constraint, branch=None):
    """Plot TOA and atmosphere data."""

    rsdt_var = 'TOA Incident Shortwave Radiation '+hemisphere+' sum'
    rsut_var = 'TOA Outgoing Shortwave Radiation '+hemisphere+' sum'
    rsaa_var = 'Atmosphere Absorbed Shortwave Flux '+hemisphere+' sum'
    rsns_var = 'Surface Net Shortwave Flux in Air '+hemisphere+' sum'

    rsdt_value, rsdt_color = get_data(infile, rsdt_var, agg_method, time_constraint, branch=branch)
    rsut_value, rsut_color = get_data(infile, rsut_var, agg_method, time_constraint, branch=branch)
    rsaa_value, rsaa_color = get_data(infile, rsaa_var, agg_method, time_constraint, branch=branch)
    rsns_value, rsns_color = get_data(infile, rsns_var, agg_method, time_constraint, branch=branch)

    values = (rsdt_value, rsut_value, rsaa_value, rsns_value)
    edge_colors = (rsdt_color, rsut_color, rsaa_color, rsns_color)
    line_widths = (1.0, 1.0, 0.3, 1.0)

    ind = numpy.arange(len(values))  # the x locations for the groups
    col = column_number[hemisphere] 
    axes[0, col].bar(ind, values, bar_width,
                     color=['None', 'None', 'None', edge_colors[-1]],
                     edgecolor=edge_colors,
                     tick_label=['rsdt', 'rsut', 'rsaa', 'rsns'],
                     linewidth=line_widths)
    if col == 0:
        axes[0, col].set_ylabel(ylabels[agg_method])


def plot_surface(axes, infile, hemisphere, bar_width, agg_method, time_constraint, branch=None):
    """Plot radiative surface fluxes."""

    values = []
    edge_colors = []
    fill_colors = []
    tick_labels = []
    line_widths = []
    ind = []
    for realm in ['', ' ocean', ' land']:
        rsns_var = 'Surface Net Shortwave Flux in Air ' + hemisphere + realm + ' sum'
        hfss_var = 'Surface Upward Sensible Heat Flux ' + hemisphere + realm + ' sum'
        hfls_var = 'Surface Upward Latent Heat Flux ' + hemisphere + realm + ' sum'
        rlns_var = 'Surface Net Longwave Flux in Air ' + hemisphere +realm + ' sum'
        if realm == '':
            hfds_var = 'Downward Heat Flux at Sea Water Surface ' + hemisphere + ' ocean sum'
        else:
            hfds_var = 'Downward Heat Flux at Sea Water Surface ' + hemisphere + realm + ' sum'
    
        rsns_value, rsns_color = get_data(infile, rsns_var, agg_method, time_constraint, branch=branch)
        hfss_value, hfss_color = get_data(infile, hfss_var, agg_method, time_constraint, branch=branch)
        hfls_value, hfls_color = get_data(infile, hfls_var, agg_method, time_constraint, branch=branch)
        hfds_value, hfds_color = get_data(infile, hfds_var, agg_method, time_constraint, branch=branch)
        rlns_value, rlns_color = get_data(infile, rlns_var, agg_method, time_constraint, branch=branch)

        hfds_inferred_value = rsns_value - hfss_value - hfls_value - rlns_value

        if realm == '':
            hfds_output = hfds_value if hfds_value else hfds_inferred_value
        
        values.extend([rsns_value, hfss_value, hfls_value, hfds_value, hfds_inferred_value, rlns_value])
        edge_colors.extend([rsns_color, hfss_color, hfls_color, hfds_color, hfds_color, rlns_color])
        fill_colors.extend([rsns_color, 'None', 'None', 'None', 'None', 'None'])
        tick_labels.extend(['rsns', 'hfss', 'hfls', '', 'hfds', 'rlns'])
        line_widths.extend([1.0, 1.0, 1.0, 1.0, 0.3, 1.0])
    
    ind = [0, 1, 2, 3, 3, 4, 5, 6, 7 ,8, 8, 9, 10, 11, 12, 13, 13, 14]
    col = column_number[hemisphere] 
    axes[1, col].bar(ind, values, bar_width,
                     color=fill_colors,
                     edgecolor=edge_colors,
                     tick_label=tick_labels,
                     linewidth=line_widths)
    if col == 0:
        axes[1, col].set_ylabel(ylabels[agg_method])

    return hfds_output
    

def plot_ocean(axes, infile, hemisphere, bar_width, agg_method, time_constraint, hfds_value, branch=None, infer_ohc=False, infer_hfbasin=False):
    """Plot ocean data.

    hfds value is passed to this function because it might have been derived from surface values

    """

    hfbasin_var = 'Northward Ocean Heat Transport ' + hemisphere + ' ocean sum'
    ohc_var = 'ocean heat content ' + hemisphere + ' sum'

    hfbasin_value, hfbasin_color = get_data(infile, hfbasin_var, agg_method, time_constraint, branch=branch)
    ohc_value, ohc_color = get_data(infile, ohc_var, agg_method, time_constraint, ohc=True, branch=branch)

    values = [hfds_value, ohc_value, hfbasin_value]
    colors = ['None', 'None', 'None']
    edge_colors = ['blue', ohc_color, hfbasin_color]
    line_widths = [1.0, 1.0, 1.0]
    ind = [0, 1, 2]
    labels = ['hfds', 'dOHC/dt', 'hfbasin']
    if infer_ohc and hfbasin_value:
        ohc_inferred_value = hfds_value + hfbasin_value
        values.insert(2, ohc_inferred_value)
        colors.insert(2, 'None')
        edge_colors.insert(2, 'blue')
        line_widths.insert(2, 0.3)
        ind.insert(2, 1)
        labels.insert(2, '')
    
    if infer_hfbasin:
        hfbasin_inferred_value = ohc_value - hfds_value        
        values.insert(-1, hfbasin_inferred_value)
        colors.insert(-1, 'None')
        edge_colors.insert(-1, 'blue')
        line_widths.insert(-1, 0.3)
        ind.insert(-1, 2)
        labels.insert(-1, '')
        
    col = column_number[hemisphere] 
    axes[2, col].bar(ind, values, bar_width,
                     color=colors,
                     edgecolor=edge_colors,
                     tick_label=labels,
                     linewidth=line_widths)
    if col == 0:
        axes[2, col].set_ylabel(ylabels[agg_method])


def main(inargs):
    """Run the program."""

    if inargs.time:
        try:
            time_constraint = gio.get_time_constraint(inargs.time)
        except AttributeError:
            time_constraint = iris.Constraint()    
    else:
        time_constraint = iris.Constraint()

    fig, axes = setup_plot(inargs.exclude_ocean)
    bar_width = 0.7
    
    for hemisphere in ['sh', 'nh']:
        plot_atmos(axes, inargs.infile, hemisphere, bar_width, inargs.aggregation, time_constraint, branch=inargs.branch_time)
        hfds_value = plot_surface(axes, inargs.infile, hemisphere, bar_width, inargs.aggregation, time_constraint, branch=inargs.branch_time)
        if not inargs.exclude_ocean:
            plot_ocean(axes, inargs.infile, hemisphere, bar_width, inargs.aggregation, time_constraint, hfds_value, branch=inargs.branch_time,
                       infer_ohc=inargs.infer_ohc, infer_hfbasin=inargs.infer_hfbasin)

    set_title(inargs.infile)
    fig.tight_layout(rect=[0, 0, 1, 0.93])   # (left, bottom, right, top) 
    #fig.subplots_adjust(left=0.15, top=0.95)

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
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = 1850-2005]")

    parser.add_argument("--infer_ohc", action="store_true", default=False,
                        help="Infer OHC from hfds and hfbasin [default=False]")
    parser.add_argument("--infer_hfbasin", action="store_true", default=False,
                        help="Infer hfbasin from hfds and ohc [default=False]")

    parser.add_argument("--exclude_ocean", action="store_true", default=False,
                        help="Leave out the ocean plot [default=False]")


    parser.add_argument("--branch_time", type=float, nargs=2, metavar=('BRANCH_TIME', 'NYEARS'), default=None,
                        help="For piControl data, specify branch time and number of years of corresponding historical experiment [default = trend]")

    args = parser.parse_args()             
    main(args)
