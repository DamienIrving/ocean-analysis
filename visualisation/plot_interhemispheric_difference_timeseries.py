"""
Filename:     plot_interhemispheric_difference_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the interhemispheric difference timeseries for various variables

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
iris.FUTURE.netcdf_promote = True
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

experiment_colors = {'historical': 'orange',
                     'historicalGHG': 'red',
                     'historicalAA': 'blue',
                     'rcp26': '#16DB65',
                     'rcp45': '#058C42',
                     'rcp60': '#04471C',
                     'rcp85': '#0D2818'}

        
def set_title(infile):
    """Get the plot title."""

    cube = iris.load(infile)
    title = '%s interhemispheric difference'  %(cube[0].attributes['model_id'])
    
    plt.suptitle(title, size='large')


def plot_data(diff_dict, ax, variable, region, realm, runmean):
    """Plot the data."""

    plt.sca(ax)
    for experiment in experiment_colors.keys():
        try:
            cube = diff_dict[(variable, experiment)]
        except KeyError:
            continue
        
        iplt.plot(cube, label=experiment, color=experiment_colors[experiment])
        if runmean:   
            smooth_cube = cube.rolling_window('time', iris.analysis.MEAN, runmean)   
            iplt.plot(smooth_cube, color=experiment_colors[experiment], linewidth=2)   
           
    title = 'Annual Mean %s' %(variable)
    ax.set_title(title)
    ax.legend()
    ax.set_xlabel('year')

    ylabel = 'northern %s - south %s, over %s'  %(region, region, get_realm_title(realm))
    ax.set_ylabel(ylabel)


def get_realm_label(realm, var):
    """Insert a space in the realm name."""

    if 'Downward Heat Flux at Sea Water Surface' in var:
        realm_label = ' ocean'
    elif realm == 'all':
        realm_label = ''
    else:
        realm_label = ' ' + realm
       
    return realm_label
   
   
def get_realm_title(realm):
    """Realm name for plot title."""
    
    if realm == 'all':
        realm_title = 'land & ocean'
    else:
        realm_title = realm
        
    return realm_title
        

def get_diff(infile, variable, region, realm, time_constraints):
    """Calculate interhemispheric difference for a given variable"""

    if 'rcp' in infile:
        time_constraint = time_constraints['rcp']
    else:
        time_constraint = time_constraints['historical']

    svar =  '%s s%s%s mean' %(variable, region, get_realm_label(realm, variable))
    nvar =  '%s n%s%s mean' %(variable, region, get_realm_label(realm, variable)) 

    with iris.FUTURE.context(cell_datetime_objects=True):
        s_cube = iris.load_cube(infile, svar & time_constraint)
        n_cube = iris.load_cube(infile, nvar & time_constraint)
    diff_cube = n_cube - s_cube

    history = s_cube.attributes['history']
    model = s_cube.attributes['model_id']
    experiment = s_cube.attributes['experiment_id']
    if experiment == 'historicalMisc':
        experiment = 'historicalAA'
    run = 'r' + str(s_cube.attributes['realization'])

    return diff_cube, history, model, experiment, run


def get_time_constraint(time_bounds):
    """Get the iris time constraint for given time bounds."""

    if time_bounds:
        try:
            time_constraint = gio.get_time_constraint(time_bounds)
        except AttributeError:
            time_constraint = iris.Constraint()    
    else:
        time_constraint = iris.Constraint()

    return time_constraint


def get_dict(input_list, variable_list):
    """Create region or realm dictionary from argparse input."""
    
    out_dict = {}
    for input, variable in zip(input_list, variable_list):
        out_dict[variable] = input
    
    return out_dict
    
    
def main(inargs):
    """Run the program."""

    time_constraints = {}
    time_constraints['historical'] = get_time_constraint(inargs.hist_time)
    time_constraints['rcp'] = get_time_constraint(inargs.rcp_time)

    variables = ['Surface Downwelling Net Radiation', 'Surface Upwelling Longwave Radiation',
                 'Surface Upward Latent Heat Flux', 'Downward Heat Flux at Sea Water Surface']
    region_dict = get_dict(inargs.regions, variables)
    realm_dict = get_dict(inargs.realms, variables)

    if inargs.infer_hfds:
        variables[-1] = 'Inferred Downward Heat Flux at Sea Water Surface'
    diff_dict = {}
    for infile in inargs.energy_infiles:
        for var in variables:
            print(infile, var)
            diff_cube, history, model, experiment, run = get_diff(infile, var, region_dict[var],
                                                                  realm_dict[var], time_constraints)
            diff_dict[(var, experiment)] = diff_cube

    width=16
    height=10
    fig = plt.figure(figsize=(width, height))
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)
    axes_list = [ax1, ax2, ax3, ax4]
    plotnum = 0
    for ax, var in zip(axes_list, variables):
        plot_data(diff_dict, ax, var, region_dict[var], realm_dict[var], inargs.runmean)

    title = '%s interhemispheric difference'  %(model)
    plt.suptitle(title, size='large')
    plt.subplots_adjust(top=0.90)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.energy_infiles[-1]: history})


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
               
    parser.add_argument("energy_infiles", type=str, nargs='*', 
                        help="Input energy budget files generated from calc_system_heat_distribution.py")                                                    
    parser.add_argument("outfile", type=str, help="Output file")  

    parser.add_argument("--regions", type=str, nargs=4, choices=('tropics', 'h'),
                        default=('h', 'h', 'tropics', 'tropics'),
                        help="Region used for rnds, rlus, hfls & hfds respectively")
    parser.add_argument("--realms", type=str, nargs=4, choices=('ocean', 'land', 'all'),
                        default=('all', 'all', 'ocean', 'ocean'),
                        help="Realms used for rnds, rlus, hfls & hfds respectively")

    parser.add_argument("--runmean", type=int, default=None,
                        help="Window for running mean [default = None]")

    parser.add_argument("--hist_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")
    parser.add_argument("--rcp_time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = all]")
    parser.add_argument("--infer_hfds", action="store_true", default=False,
                        help="Use inferred hfds data")

    args = parser.parse_args()             
    main(args)
