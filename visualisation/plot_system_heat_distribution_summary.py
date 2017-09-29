"""
Filename:     plot_system_heat_distribution_summary.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot a sumamry of the system heat distribution

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

def get_data(infile, var, agg_method, time_constraint, ohc=False, branch=None):
    """Read and temporally aggregate the data."""
    
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(infile, var & time_constraint)
        value = timeseries.calc_trend(cube, per_yr=True)
           
    return value
        

def set_title(infile):
    """Get the plot title."""

    cube = iris.load(infile)
    title = '%s trends, divided by global net radiative surface flux'  %(cube[0].attributes['model_id'])
    
    plt.suptitle(title, size='large')


def get_scale_factor(infile):
    """Get the scaling factor."""

    cube = iris.load_cube(infile, 'Surface Downwelling Net Radiation globe sum')
    trend = timeseries.calc_trend(cube, per_yr=True)
    history = cube.attributes['history']
    model = cube.attributes['model_id']

    return trend, history, model


def plot_data(ax, variable, aa_trends_dict, ghg_trends_dict, aa_files, ghg_files):
    """Plot the data."""

    xvals = [0, 1, 2, 3, 4]
    labels = ['', 'ssubpolar', 'stropics', 'ntropics', 'nsubpolar', 'arctic']

    first = True
    for aa_file, ghg_file in zip(aa_files, ghg_files):
        aa_label = 'AA' if first else None
        ghg_label = 'GHG' if first else None
        ax.plot(xvals, aa_trends_dict[(variable, aa_file)], 'o-', color='blue', label=aa_label)
        ax.plot(xvals, ghg_trends_dict[(variable, ghg_file)], 'o-', color='red', label=ghg_label)
        first = False

    ax.set_xticklabels(labels)
    ax.set_ylabel('$W \: yr^{-1}$')
    ax.margins(0.1)
    ax.legend()
    ax.set_title(variable)


def get_regional_trends(infile, variable, scale_factor):
    """Calculate regional trends for a given variable"""

    trend_values = []
    for region in ['ssubpolar', 'stropics', 'ntropics', 'nsubpolar', 'arctic']:
        full_var = '%s %s ocean sum'  %(variable, region)
        cube = iris.load_cube(infile, full_var)
        trend_values.append(timeseries.calc_trend(cube, per_yr=True) / scale_factor)

    return trend_values

    
def main(inargs):
    """Run the program."""

    if inargs.time:
        try:
            time_constraint = gio.get_time_constraint(inargs.time)
        except AttributeError:
            time_constraint = iris.Constraint()    
    else:
        time_constraint = iris.Constraint()

    width=20
    height=5
    fig = plt.figure(figsize=(width, height))
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)
    axes_list = [ax1, ax2, ax3]

    assert len(inargs.ghg_files) == len(inargs.aa_files)

    variables = ['Surface Upwelling Longwave Radiation', 'Surface Upward Latent Heat Flux', 'Downward Heat Flux at Sea Water Surface']
    ghg_trends_dict = {}
    aa_trends_dict = {}
    for ghg_file, aa_file in zip(inargs.ghg_files, inargs.aa_files):
        ghg_rnds_globe_trend, ghg_history, model = get_scale_factor(ghg_file)
        aa_rnds_globe_trend, aa_history, model = get_scale_factor(aa_file)
        print('Trend in global rnds, GHG / AA:', ghg_rnds_globe_trend / aa_rnds_globe_trend)    

        for var in variables:
            ghg_trends_dict[(var, ghg_file)] = get_regional_trends(ghg_file, var, ghg_rnds_globe_trend)
            aa_trends_dict[(var, aa_file)] = get_regional_trends(aa_file, var, aa_rnds_globe_trend)

    for ax, var in zip(axes_list, variables):
        plot_data(ax, var, aa_trends_dict, ghg_trends_dict, inargs.aa_files, inargs.ghg_files)

    title = '%s trends, divided by global net radiative surface flux'  %(model)
    plt.suptitle(title, size='large')
    plt.subplots_adjust(top=0.85)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={ghg_file: ghg_history,
                                                  aa_file: aa_history})


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
                                                                   
    parser.add_argument("outfile", type=str, help="Output file")  
  
    parser.add_argument("--ghg_files", type=str, nargs='*', default=None, 
                        help="Input historicalGHG energy budget file generated from calc_system_heat_distribution.py")      
    parser.add_argument("--aa_files", type=str, nargs='*', default=None,
                        help="Input historicalAA energy budget file generated from calc_system_heat_distribution.py")                                  

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = 1850-2005]")

    args = parser.parse_args()             
    main(args)
