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

column_number = {'sh': 0, 'nh': 1,
                 'ssubpolar': 0, 'stropics': 1, 'ntropics': 2, 'nsubpolar': 3, 'arctic': 4}

region_names = {2: ['sh', 'nh'],
                5: ['ssubpolar', 'stropics', 'ntropics', 'nsubpolar', 'arctic']}

ylabels = {'climatology': 'W', 'trend': '$W \: yr^{-1}$'}

def setup_plot(nregions):
    """Set the plot axes and headings."""

    rows = ['TOA / Atmosphere', 'Surface', 'Ocean']
    if nregions == 2:
        cols = ['Southern Hemisphere', 'Northern Hemisphere']
        height = 12
        width = 20
    elif nregions == 5:
        cols = ['southern sub-polar', 'southern tropics', 'northern tropics',
                'northern sub-polar', 'arctic ocean']
        height = 15
        width = 55  

    fig = plt.figure(figsize=(width, height))

    nrows = 3
    ncols = len(cols)
    if nregions == 2:
        axes11 = fig.add_subplot(nrows, ncols, 1)
        axes12 = fig.add_subplot(nrows, ncols, 2, sharey=axes11)
        axes21 = fig.add_subplot(nrows, ncols, 3)
        axes22 = fig.add_subplot(nrows, ncols, 4, sharey=axes21)
        axes31 = fig.add_subplot(nrows, ncols, 5)
        axes32 = fig.add_subplot(nrows, ncols, 6, sharey=axes31)
        axes = numpy.array([(axes11, axes12), (axes21, axes22), (axes31, axes32)])
    elif nregions == 5:
        axes11 = fig.add_subplot(nrows, ncols, 1)
        axes12 = fig.add_subplot(nrows, ncols, 2, sharey=axes11)
        axes13 = fig.add_subplot(nrows, ncols, 3, sharey=axes11)
        axes14 = fig.add_subplot(nrows, ncols, 4, sharey=axes11)
        axes15 = fig.add_subplot(nrows, ncols, 5, sharey=axes11)
        axes21 = fig.add_subplot(nrows, ncols, 6)
        axes22 = fig.add_subplot(nrows, ncols, 7, sharey=axes21)
        axes23 = fig.add_subplot(nrows, ncols, 8, sharey=axes21)
        axes24 = fig.add_subplot(nrows, ncols, 9, sharey=axes21)
        axes25 = fig.add_subplot(nrows, ncols, 10, sharey=axes21)
        axes31 = fig.add_subplot(nrows, ncols, 11)
        axes32 = fig.add_subplot(nrows, ncols, 12, sharey=axes31)
        axes33 = fig.add_subplot(nrows, ncols, 13, sharey=axes31)
        axes34 = fig.add_subplot(nrows, ncols, 14, sharey=axes31)
        axes35 = fig.add_subplot(nrows, ncols, 15, sharey=axes31)
        axes = numpy.array([(axes11, axes12, axes13, axes14, axes15),
                            (axes21, axes22, axes23, axes24, axes25),
                            (axes31, axes32, axes33, axes34, axes35)])

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

    
def plot_atmos(axes, infile, region, bar_width, agg_method, time_constraint, branch=None):
    """Plot TOA and atmosphere data."""

    rsdt_var = 'TOA Incident Shortwave Radiation '+region+' sum'
    rsut_var = 'TOA Outgoing Shortwave Radiation '+region+' sum'
    rsaa_var = 'Atmosphere Absorbed Shortwave Flux '+region+' sum'
    rlut_var = 'TOA Outgoing Longwave Radiation '+region+' sum'

    rsdt_value, rsdt_color = get_data(infile, rsdt_var, agg_method, time_constraint, branch=branch)
    rsut_value, rsut_color = get_data(infile, rsut_var, agg_method, time_constraint, branch=branch)
    rsaa_value, rsaa_color = get_data(infile, rsaa_var, agg_method, time_constraint, branch=branch)
    rlut_value, rlut_color = get_data(infile, rlut_var, agg_method, time_constraint, branch=branch)

    values = (rsdt_value, rsut_value, rsaa_value, rlut_value)
    edge_colors = (rsdt_color, rsut_color, rsaa_color, rlut_color)
    line_widths = (1.0, 1.0, 0.3, 1.0)

    ind = numpy.arange(len(values))  # the x locations for the groups
    col = column_number[region] 
    axes[0, col].bar(ind, values, bar_width,
                     color=['None', 'None', 'None', 'None'],
                     edgecolor=edge_colors,
                     tick_label=['rsdt', 'rsut', 'rsaa', 'rlut'],
                     linewidth=line_widths,
                     align='center')
    if col == 0:
        axes[0, col].set_ylabel(ylabels[agg_method])


def plot_surface(axes, infile, region, bar_width, agg_method, time_constraint, branch=None):
    """Plot radiative surface fluxes."""

    values = []
    edge_colors = []
    fill_colors = []
    tick_labels = []
    line_widths = []
    ind = []
    for realm in ['', ' ocean', ' land']:
        rsds_var = 'Surface Downwelling Shortwave Radiation ' + region + realm + ' sum'
        rsus_var = 'Surface Upwelling Shortwave Radiation ' + region + realm + ' sum'
        rlds_var = 'Surface Downwelling Longwave Radiation ' + region + realm + ' sum'
        rlus_var = 'Surface Upwelling Longwave Radiation ' + region + realm + ' sum'
        rnds_var = 'Surface Downwelling Net Radiation ' + region + realm + ' sum'
        hfss_var = 'Surface Upward Sensible Heat Flux ' + region + realm + ' sum'
        hfls_var = 'Surface Upward Latent Heat Flux ' + region + realm + ' sum'
        if realm == '':
            hfds_var = 'Downward Heat Flux at Sea Water Surface ' + region + ' ocean sum'
            hfds_inferred_var = 'Inferred Downward Heat Flux at Sea Water Surface ' + region + ' ocean sum'
        else:
            hfds_var = 'Downward Heat Flux at Sea Water Surface ' + region + realm + ' sum'
            hfds_inferred_var = 'Inferred Downward Heat Flux at Sea Water Surface ' + region + realm + ' sum'
    
        rsds_value, rsds_color = get_data(infile, rsds_var, agg_method, time_constraint, branch=branch)
        rsus_value, rsus_color = get_data(infile, rsus_var, agg_method, time_constraint, branch=branch)
        rlds_value, rlds_color = get_data(infile, rlds_var, agg_method, time_constraint, branch=branch)
        rlus_value, rlus_color = get_data(infile, rlus_var, agg_method, time_constraint, branch=branch)
        rnds_value, rnds_color = get_data(infile, rnds_var, agg_method, time_constraint, branch=branch)
        hfss_value, hfss_color = get_data(infile, hfss_var, agg_method, time_constraint, branch=branch)
        hfls_value, hfls_color = get_data(infile, hfls_var, agg_method, time_constraint, branch=branch)
        hfds_value, hfds_color = get_data(infile, hfds_var, agg_method, time_constraint, branch=branch)
        hfds_inferred_value, hfds_inferred_color = get_data(infile, hfds_inferred_var, agg_method, time_constraint, branch=branch)

        if realm == '':
            hfds_output = hfds_value if hfds_value else hfds_inferred_value
        
        values.extend([rsds_value, rsus_value, rlds_value, rlus_value, rnds_value, hfss_value, hfls_value, hfds_value, hfds_inferred_value])
        edge_colors.extend([rsds_color, rsus_color, rlds_color, rlus_color, rnds_color, hfss_color, hfls_color, hfds_color, hfds_color])
        fill_colors.extend(['None', 'None', 'None', 'None', rnds_color, 'None', 'None', 'None', 'None'])
        tick_labels.extend(['rsds', 'rsus', 'rlds', 'rlus', 'rnds', 'hfss', 'hfls', '', 'hfds'])
        line_widths.extend([1.0 ,1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.3])
    
    ind = [0, 1, 2, 3, 4, 5, 6, 7, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 16, 17, 18, 19, 20, 21, 22, 23, 23]
    col = column_number[region] 
    axes[1, col].bar(ind, values, bar_width,
                     color=fill_colors,
                     edgecolor=edge_colors,
                     tick_label=tick_labels,
                     linewidth=line_widths,
                     align='center')
    if col == 0:
        axes[1, col].set_ylabel(ylabels[agg_method])

    return hfds_output
    

def get_ocean_values(infile, agg_method, time_constraint, hfds_values, nregions, branch=None, infer_ohc=False, infer_hfbasin=False):
    """Get the ocean values"""
    
    ohc_values = {}
    transport_values = {}
    ohc_inferred_values = {}
    for region in region_names[nregions]:
        ohc_var = 'ocean heat content ' + region + ' sum'
        ohc_values[region], color = get_data(infile, ohc_var, agg_method, time_constraint, ohc=True, branch=branch)

        transport_data_flag = False
        for direction in ['in', 'out']:
            hfbasin_var = 'Northward Ocean Heat Transport ' + region + ' ocean sum ' + direction
            transport_values[(region, direction)], color = get_data(infile, hfbasin_var, agg_method, time_constraint, branch=branch)
            if transport_values[(region, direction)]:
                transport_data_flag = True
                if direction == 'out':
                    transport_values[(region, direction)] = -1 * transport_values[(region, direction)]

        if infer_ohc and transport_data_flag:
            ohc_inferred_values[region] = hfds_values[region] + transport_values[(region, 'in')] + transport_values[(region, 'out')]

    transport_inferred_values = {}
    if infer_hfbasin:
        if nregions == 2:
            transport_inferred_values[('nh', 'in')] = ohc_values['nh'] - hfds_values['nh']
            transport_inferred_values[('sh', 'out')] = ohc_values['sh'] - hfds_values['sh']
        elif nregions == 5:
            transport_inferred_values[('ssubpolar', 'out')] = ohc_values['ssubpolar'] - hfds_values['ssubpolar']        
            transport_inferred_values[('stropics', 'in')] = -1 * transport_inferred_values[('ssubpolar', 'out')]
            transport_inferred_values[('stropics', 'out')] = ohc_values['stropics'] - hfds_values['stropics'] - transport_inferred_values[('stropics', 'in')]       
            transport_inferred_values[('ntropics', 'in')] = -1 * transport_inferred_values[('ssubpolar', 'out')]
            transport_inferred_values[('ntropics', 'out')] = ohc_values['ntropics'] - hfds_values['ntropics'] - transport_inferred_values[('ntropics', 'in')]       
            transport_inferred_values[('nsubpolar', 'in')] = -1 * transport_inferred_values[('ntropics', 'out')]
            transport_inferred_values[('nsubpolar', 'out')] = ohc_values['nsubpolar'] - hfds_values['nsubpolar'] - transport_inferred_values[('nsubpolar', 'in')]       
            transport_inferred_values[('arctic', 'in')] = -1 * transport_inferred_values[('nsubpolar', 'out')]

    return ohc_values, transport_values, ohc_inferred_values, transport_inferred_values


def plot_ocean(axes, region, bar_width, agg_method, hfds_values, ohc_values, transport_values, ohc_inferred_values, transport_inferred_values):
    """Plot ocean data."""

    left_regions = ['sh', 'ssubpolar']
    right_regions = ['nh', 'arctic']

    values = [transport_values[(region, 'in')], hfds_values[region], ohc_values[region], transport_values[(region, 'out')]]
    colors = ['None', 'None', 'None', 'None']
    edge_colors = 'blue'
    line_widths = [1.0, 1.0, 1.0, 1.0]
    ind = [0, 1, 2, 3]
    labels = ['hf-in', 'hfds', 'dOHC/dt', 'hf-out']

    if region in left_regions:
        values = [hfds_values[region], ohc_values[region], transport_values[(region, 'out')]]
        colors = colors[1:]
        line_widths = line_widths[1:]
        ind = [0, 1, 2]
        labels = labels[1:]
    elif region in right_regions:
        values = [transport_values[(region, 'in')], hfds_values[region], ohc_values[region]]
        colors = colors[:-1]
        line_widths = line_widths[:-1]
        ind = [0, 1, 2]
        labels = labels[:-1]

    try:
        ohc_index = labels.index('dOHC/dt')
        values.insert(ohc_index, ohc_inferred_values[region])
        colors.insert(ohc_index, 'None')
        line_widths.insert(ohc_index, 0.3)
        ind.insert(ohc_index, ind[ohc_index])
        labels.insert(ohc_index, '')
    except KeyError:
        pass    

    try:
        values.insert(0, transport_inferred_values[(region, 'in')])
        colors.insert(0, 'None')
        line_widths.insert(0, 0.3)
        ind.insert(0, ind[0])
        labels.insert(0, '')
    except KeyError:
        pass    
    
    try:
        values.insert(-1, transport_inferred_values[(region, 'out')])
        colors.insert(-1, 'None')
        line_widths.insert(-1, 0.3)
        ind.insert(-1, ind[-1])
        labels.insert(-1, '')
    except KeyError:
        pass

    col = column_number[region] 
    axes[2, col].bar(ind, values, bar_width,
                     color=colors,
                     edgecolor=edge_colors,
                     tick_label=labels,
                     linewidth=line_widths,
                     align='center')
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

    fig, axes = setup_plot(inargs.nregions)
    bar_width = 0.7
    
    hfds_values = {}
    for region in region_names[inargs.nregions]:
        plot_atmos(axes, inargs.infile, region, bar_width, inargs.aggregation, time_constraint, branch=inargs.branch_time)
        hfds_values[region] = plot_surface(axes, inargs.infile, region, bar_width, inargs.aggregation, time_constraint, branch=inargs.branch_time)

    ohc_values, transport_values, ohc_inferred_values, transport_inferred_values = get_ocean_values(inargs.infile, inargs.aggregation, time_constraint,
                                                                                                    hfds_values, inargs.nregions, branch=inargs.branch_time, 
                                                                                                    infer_ohc=inargs.infer_ohc, infer_hfbasin=inargs.infer_hfbasin)
    for region in region_names[inargs.nregions]:
        plot_ocean(axes, region, bar_width, inargs.aggregation, hfds_values, ohc_values, transport_values, ohc_inferred_values, transport_inferred_values)

    set_title(inargs.infile)
    fig.tight_layout(rect=[0, 0, 1, 0.93])   # (left, bottom, right, top) 

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

    parser.add_argument("--nregions", type=int, choices=(2, 5), default=2,
                        help="Number of regions to split the globe into [default=2]")

    parser.add_argument("--branch_time", type=float, nargs=2, metavar=('BRANCH_TIME', 'NYEARS'), default=None,
                        help="For piControl data, specify branch time and number of years of corresponding historical experiment [default = trend]")

    args = parser.parse_args()             
    main(args)
