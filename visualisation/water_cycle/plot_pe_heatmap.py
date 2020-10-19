"""
Filename:     plot_pe_heatmap.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot heatmap using output from calc_pe_spatial_totals.py
"""

# Import general Python modules

import sys, os, pdb
import argparse
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import iris

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
script_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(script_dir)
try:
    import general_io as gio
    import calc_ensemble_aggregate as ensagg
except ImportError:
    raise ImportError('Must run this script from anywhere within the ocean-analysis git repo')


# Define functions

def get_data(infiles, var, data_type, time_constraint, agg_method, pct=False):
    """Get the data for a particular model"""
    
    cube_list = iris.cube.CubeList([])
    for ensnum, infile in enumerate(infiles):
        cube, history = gio.combine_files(infile, var, new_calendar='365_day')
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
    pe_regions = ['SH Precip', 'SH Evap', 'Tropical Precip', 'NH Evap', 'NH Precip', 'Globe']
    df = pd.DataFrame(ens_cube.data, columns=basins, index=pe_regions)
    df.loc['Globe', 'Globe'] = np.nan
    df = df.iloc[::-1]
    if pct:
        total_pos = df[df['Globe'] > 0]['Globe'].sum()
        total_neg = abs(df[df['Globe'] < 0]['Globe'].sum())
        df = df / max(total_pos, total_neg)
        
    return df, history


def main(inargs):
    """Run the program."""

    assert inargs.var in ['precipitation_minus_evaporation_flux', 'water_flux_into_sea_water',
                          'water_evapotranspiration_flux']
    cmap = 'BrBG'
    basins_to_plot = ['Atlantic', 'Indian', 'Pacific', 'Arctic', 'Land', 'Ocean', 'Globe']
    if inargs.var == 'precipitation_minus_evaporation_flux':
        var_abbrev = 'net mositure import/export (i.e. P-E)'   
    elif inargs.var == 'water_evapotranspiration_flux':
        var_abbrev = 'evaporation'
        cmap = 'BrBG_r'
    elif inargs.var == 'water_flux_into_sea_water':
        var_abbrev = 'net mositure import/export (i.e. P-E+R)'
        basins_to_plot = ['Atlantic', 'Indian', 'Pacific', 'Arctic', 'Globe']

    time_constraint = gio.get_time_constraint(inargs.time_bounds)
    df, history = get_data(inargs.infiles, inargs.var, inargs.data_type,
                           time_constraint, inargs.ensemble_stat, pct=inargs.pct)     
    if inargs.scale_factor:
        assert not inargs.pct
        df = df / 10**inargs.scale_factor

    if inargs.data_type == 'cumulative_anomaly':
        title = f'Time-integrated {var_abbrev} anomaly'
        if inargs.time_bounds:
            start_year = inargs.time_bounds[0].split('-')[0]
            end_year = inargs.time_bounds[1].split('-')[0]
            title = title + f', {start_year}-{end_year}'
    elif inargs.data_type == 'climatology':
        title = f'Annual mean {var_abbrev}'

    if inargs.pct:
        fmt = '.0%'
        label = 'fraction of total import/export'
    else:
        fmt='.2g'
        if inargs.scale_factor:
            label = 'time-integrated anomaly ($10^{%s}$ kg)'  %(str(inargs.scale_factor))
        else:
            label = 'time-integrated anomaly (kg)'

    vmax = inargs.vmax if inargs.vmax else df[basins_to_plot].abs().max().max() * 1.05

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(df[basins_to_plot], annot=True, cmap=cmap, linewidths=.5, ax=ax,
                vmin=-vmax, vmax=vmax, fmt=fmt,
                cbar_kws={'label': label})
    plt.title(title)
  
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.infiles[-1]: history})


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

example:

"""

    description = 'Plot heatmap using output from calc_pe_spatial_totals.py'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="input files")                                    
    parser.add_argument("var", type=str, help="variable")
    parser.add_argument("data_type", type=str, choices=('cumulative_anomaly', 'climatology'), help="type of data")
    parser.add_argument("outfile", type=str, help="output file") 

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")
    parser.add_argument("--pct", action="store_true", default=False,
                        help="Change output units to percentage of total net import/export")
    parser.add_argument("--scale_factor", type=int, default=None,
                        help="Scale factor (e.g. scale factor of 17 will divide data by 10^17")
    parser.add_argument("--vmax", type=float, default=None,
                        help="Colorbar maximum value")
    parser.add_argument("--ensemble_stat", type=str, choices=('median', 'mean'), default='mean',
                        help="Ensemble statistic if multiple input files")

    args = parser.parse_args()             
    main(args)
