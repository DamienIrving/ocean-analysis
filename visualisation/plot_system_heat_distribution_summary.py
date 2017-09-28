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

# '$W \: yr^{-1}$'


def get_data(infile, var, agg_method, time_constraint, ohc=False, branch=None):
    """Read and temporally aggregate the data."""
    
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(infile, var & time_constraint)
        value = timeseries.calc_trend(cube, per_yr=True)
           
    return value
        

def set_title(infile):
    """Get the plot title."""

    cube = iris.load(infile)
    title = 'Summary energy budget for %s, %s, %s'  %(cube[0].attributes['model_id'])
    
    plt.suptitle(title, size='x-large')


def get_scale_factor(infile)
    """Get the scaling factor."""

    cube = iris.load_cube(infile, 'Surface Downwelling Net Radiation globe sum')
    trend = timeseries.calc_trend(cube, per_yr=True)

    return trend


def get_regional_trends(infile, variable, scale_factor)
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
    height=10
    fig = plt.figure(figsize=(width, height))
    axes1 = fig.add_subplot(1, 3, 1)
    axes2 = fig.add_subplot(1, 3, 2)
    axes3 = fig.add_subplot(1, 3, 3)

    ghg_rnds_globe_trend = get_scale_factor(inargs.ghg_file)
    aa_rnds_globe_trend = get_scale_factor(inargs.aa_file)
    print('Trend in global rnds, GHG / AA:', ghg_rnds_globe_trend / aa_rnds_globe_trend)    

    variables = ['Surface Upwelling Longwave Radiation', 'Surface Upward Latent Heat Flux', 'Downward Heat Flux at Sea Water Surface']
    for var in varibales:
        

    set_title(inargs.infile)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infile: iris.load(inargs.infile)[0].attributes['history']})


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
                                     
    parser.add_argument("ghg_file", type=str, help="Input historicalGHG energy budget file generated from calc_system_heat_distribution.py")      
    parser.add_argument("aa_file", type=str, help="Input historicalAA energy budget file generated from calc_system_heat_distribution.py")                               
    parser.add_argument("outfile", type=str, help="Output file")                                     

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = 1850-2005]")

    args = parser.parse_args()             
    main(args)
