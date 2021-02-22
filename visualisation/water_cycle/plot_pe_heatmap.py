"""Plot heatmap using output from calc_pe_spatial_totals.py"""

import sys
script_dir = sys.path[0]
import os
import pdb
import argparse
import re

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import iris
import cmdline_provenance as cmdprov

repo_dir = '/'.join(script_dir.split('/')[:-2])
module_dir = repo_dir + '/modules'
script_dir = repo_dir + '/data_processing'
sys.path.append(module_dir)
sys.path.append(script_dir)
try:
    import general_io as gio
    import calc_ensemble_aggregate as ensagg
except ImportError:
    raise ImportError('Script and modules in wrong directories')


def get_data(infiles, var, data_type, time_constraint, agg_method, pct=False):
    """Get the data for a particular model"""
    
    cube_list = iris.cube.CubeList([])
    for ensnum, infile in enumerate(infiles):
        cube, history = gio.combine_files(infile, var, new_calendar='365_day')
        assert cube.units == 'kg', f'{infile} units not kg'
        if time_constraint:
            cube = cube.extract(time_constraint)
        if data_type == 'cumulative_anomaly':
            cube.data = cube.data - cube.data[0, ::]
            cube = cube[-1, ::]
        elif data_type == 'climatology':
            cube = cube.collapsed('time', iris.analysis.MEAN)
        cube.remove_coord('time')
        new_aux_coord = iris.coords.AuxCoord(ensnum, long_name='ensemble_member', units='no_unit')
        cube.add_aux_coord(new_aux_coord)
        cube_list.append(cube)

    if len(cube_list) > 1:
        ens_cube = ensagg.calc_ensagg(cube_list, operator=agg_method)
    else:
        ens_cube = cube_list[0]

    basins = ['Atlantic', 'Pacific', 'Indian', 'Arctic', 'Marginal Seas', 'Land', 'Ocean', 'Globe']
    pe_regions = ['SH-P', 'SH-E', 'T-P', 'NH-E', 'NH-P', 'Globe']
    df = pd.DataFrame(ens_cube.data, columns=basins, index=pe_regions)
    #df.loc['Globe', 'Globe'] = np.nan
    df = df.iloc[::-1]
    if pct:
        if var in ['precipitation_minus_evaporation_flux', 'water_flux_into_sea_water']:
            total_pos= df['Globe']['NH Precip'] + df['Globe']['Tropical Precip'] + df['Globe']['SH Precip']
            total_neg = abs(df['Globe']['NH Evap'] + df['Globe']['SH Evap'])
            df = df / max(total_pos, total_neg)
        else:
            df = df / df['Globe']['Globe']
        
    return df, history


def get_labels(data_type, time_bounds, var_abbrev, ensemble_stat,
               experiment, scale_factor, nfiles, pct):
    """Get title and colorbar label for plot."""

    if data_type == 'cumulative_anomaly':
        label = 'time integrated anomaly'
        title = f'time-integrated {var_abbrev} anomaly'
        if time_bounds:
            start_year = time_bounds[0].split('-')[0]
            end_year = time_bounds[1].split('-')[0]
            title = f'{title}, {start_year}-{end_year}'
    elif data_type == 'climatology':
        label = 'annual total'
        title = f'annual {var_abbrev}'

    if nfiles > 1:
        title = f'ensemble {ensemble_stat} {title}'

    if experiment:
        title = f'{title}, {experiment} experiment'

    if pct:
        fmt = '.0%'
        label = 'fraction of total'
    else:
        fmt='.2g'
        if scale_factor:
            label = label + ' ($10^{%s}$ kg)'  %(str(scale_factor))
        else:
            label = label + ' (kg)'
    
    letter_dict = {'piControl': '(a)',
                   'GHG-only': '(b)',
                   'AA-only': '(c)',
                   'historical': '(d)'}
    title = letter_dict[experiment] + ' ' + title

    return title, label, fmt


def plot_data(ax, file_list, inargs, experiment, var_abbrev,
              time_constraint, scale_factor, basins_to_plot, cmap):
    """Create one panel of the subplot."""

    data_type = 'climatology' if experiment == 'piControl' else 'cumulative_anomaly'
    pct = False

    df, history = get_data(file_list, inargs.var, data_type,
                           time_constraint, inargs.ensemble_stat, pct=pct)     
    if not pct:
        df = df / 10**scale_factor

    nfiles = len(file_list)
    title, label, fmt = get_labels(data_type, inargs.time_bounds, var_abbrev, inargs.ensemble_stat,
                                   experiment, scale_factor, nfiles, pct)
    
    if inargs.vmax and not experiment == 'piControl':
        vmax = inargs.vmax
    else:
        vmax = df[basins_to_plot].abs().max().max() * 1.05

    g = sns.heatmap(df[basins_to_plot],
                    annot=True,
                    cmap=cmap,
                    linewidths=.5,
                    ax=ax,
                    vmin=-vmax,
                    vmax=vmax,
                    fmt=fmt,
                    cbar_kws={'label': label}
                   )
    g.set_yticklabels(g.get_yticklabels(), rotation=0)
    ax.set_title(title)

    return history
  

def main(inargs):
    """Run the program."""

    assert inargs.var in ['precipitation_minus_evaporation_flux', 'water_flux_into_sea_water',
                          'water_evapotranspiration_flux', 'precipitation_flux']
    cmap = 'BrBG'
    basins_to_plot = ['Atlantic', 'Indian', 'Pacific', 'Land', 'Ocean', 'Globe']
    if inargs.var == 'precipitation_minus_evaporation_flux':
        var_abbrev = 'P-E'   
    elif inargs.var == 'water_evapotranspiration_flux':
        var_abbrev = 'evaporation'
        cmap = 'BrBG_r'
    elif inargs.var == 'precipitation_flux':
        var_abbrev = 'precipitation'
    elif inargs.var == 'water_flux_into_sea_water':
        var_abbrev = 'net mositure import/export (i.e. P-E+R)'
        basins_to_plot = ['Atlantic', 'Indian', 'Pacific', 'Arctic', 'Globe']

    time_constraint = gio.get_time_constraint(inargs.time_bounds)
    input_files = [inargs.control_files,
                   inargs.ghg_files,
                   inargs.aa_files,
                   inargs.hist_files]
    experiments = ['piControl', 'GHG-only', 'AA-only', 'historical']
    
    metadata_dict = {}
    fig, axes = plt.subplots(2, 2, figsize=(24, 12))
    axes = axes.flatten()
    for plotnum, exp_files in enumerate(input_files):
        if exp_files:
            print(f"Number of models = {len(exp_files)}")
            experiment = experiments[plotnum]
            time_selector = None if experiment == 'piControl' else time_constraint
            file_history = plot_data(axes[plotnum], exp_files, inargs,
                                     experiment, var_abbrev, time_selector,
                                     inargs.scale_factor[plotnum], basins_to_plot, cmap)
            metadata_dict[exp_files[0]] = file_history[0]   

    plt.savefig(inargs.outfile, bbox_inches='tight')
    log_text = cmdprov.new_log(infile_history=metadata_dict, git_repo=repo_dir)
    log_file = re.sub('.png', '.met', inargs.outfile)
    cmdprov.write_log(log_file, log_text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
                                    
    parser.add_argument("var", type=str, help="variable")
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--control_files", type=str, nargs='*', default=None,
                        help="piControl files for climatology")
    parser.add_argument("--ghg_files", type=str, nargs='*', default=None,
                        help="hist-GHG files")
    parser.add_argument("--aa_files", type=str, nargs='*', default=None,
                        help="hist-aer files")
    parser.add_argument("--hist_files", type=str, nargs='*', default=None,
                        help="historical files")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")
    parser.add_argument("--scale_factor", type=int, nargs=4, default=(16, 17, 17, 17),
                        help="Scale factor for each experiment (e.g. scale factor of 17 will divide data by 10^17")
    parser.add_argument("--vmax", type=float, default=None,
                        help="Colorbar maximum value (* 10^17)")
    parser.add_argument("--ensemble_stat", type=str, choices=('median', 'mean'), default='mean',
                        help="Ensemble statistic if multiple input files")

    args = parser.parse_args()             
    main(args)
