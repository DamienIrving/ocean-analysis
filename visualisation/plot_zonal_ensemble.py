"""
Filename:     plot_zonal_ensemble.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot zonal mean for an ensemble of models  

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
from matplotlib import gridspec
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
    import grids
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def calc_trend_cube(cube):
    """Calculate trend and put into appropriate cube."""
    
    trend_array = timeseries.calc_trend(cube, per_yr=True)
    new_cube = cube[0,:].copy()
    new_cube.remove_coord('time')
    new_cube.data = trend_array
    
    return new_cube


def get_colors(infiles):
    """Define a color for each model"""

    models = []
    for infile in infiles:
        filename = infile.split('/')[-1]
        model = filename.split('_')[2]

        models.append(model) 
    
    nmodels = len(set(models))
    cm = plt.get_cmap('nipy_spectral')
    colors = [cm(1. * i / nmodels) for i in range(nmodels)]
    color_dict = {}
    count = 0
    for model in models:
        if not model in color_dict.keys():
            color_dict[model] = colors[count]
            count = count + 1

    return color_dict


def get_ylabel(cube, inargs):
    """get the y axis label"""

    ylabel = '$%s' %(str(cube.units))
    if inargs.perlat:
        ylabel = ylabel + ' \: lat^{-1}'
    if inargs.time_agg == 'trend':
        ylabel = ylabel + ' \: yr^{-1}'
    ylabel = ylabel + '$'

    return ylabel


def main(inargs):
    """Run the program."""
    
    time_constraint = gio.get_time_constraint(inargs.time)
    fig, ax = plt.subplots()
    plt.axhline(y=0, color='0.5', linestyle='--')
    color_dict = get_colors(inargs.infiles)
    
    legend_models = []
    for infile in inargs.infiles:
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(infile, gio.check_iris_var(inargs.var) & time_constraint)
        
        if inargs.perlat:
            grid_spacing = grids.get_grid_spacing(cube) 
            cube.data = cube.data / grid_spacing
 
        if inargs.time_agg == 'trend':
            agg_cube = calc_trend_cube(cube)
            plot_name = 'linear trend'
        elif inargs.time_agg == 'climatology':
            agg_cube = cube.collapsed('time', iris.analysis.MEAN)
            plot_name = 'climatology'

        model = cube.attributes['model_id']
        if model not in legend_models:
            label = model
            legend_models.append(model)
        else:
            label = None

        iplt.plot(agg_cube, label=label, color=color_dict[model])

    title = '%s, %s-%s' %(plot_name, inargs.time[0][0:4], inargs.time[1][0:4])
    plt.title(title)
    plt.xlim(-90, 90)
    ylabel = get_ylabel(cube, inargs)
    plt.ylabel(ylabel)
    plt.xlabel('latitude')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={infile: cube.attributes['history']})


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description = 'Plot zonal ensemble'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("var", type=str, help="Variable")
    parser.add_argument("time_agg", type=str, choices=('trend', 'climatology'), help="Temporal aggregation")
    parser.add_argument("outfile", type=str, help="Output file")                                     
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1861-01-01', '2005-12-31'),
                        help="Time period [default = entire]")
    parser.add_argument("--perlat", action="store_true", default=False,
                        help="Scale per latitude [default=False]")

    args = parser.parse_args()             
    main(args)
