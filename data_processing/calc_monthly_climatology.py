"""
Filename:     calc_monthly_climatology.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the monthly climatology

"""

# Import general Python modules

import sys, os, pdb
import argparse
import xarray as xr
import cmdline_provenance as cmdprov

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'ocean-analysis':
        break


# Define functions

def main(inargs):
    """Run the program."""

    dset = xr.open_mfdataset(inargs.infiles)
    if inargs.time_bounds:
        start, end = inargs.time_bounds
        dset = dset.sel(time=slice(start, end))
    clim_dset = dset.groupby('time.month').mean('time', keep_attrs=True)
    
    history = dset.attrs['history']
    log = cmdprov.new_log(infile_history={inargs.infiles[0]: history}, git_repo=repo_dir)
    clim_dset.attrs['history'] = log

    clim_dset.to_netcdf(inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the monthly climatology'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input files")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time_bounds", type=str, nargs=2, default=None, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    args = parser.parse_args()            
    main(args)
