"""
Filename:     cmip5_version_info.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Version number and tracking id information 
"""

# Import general Python modules

import sys, os, pdb
import argparse
import pandas
from ARCCSSive import CMIP5

cmip5 = CMIP5.DB.connect()

atmos_variables = ['rsdt', 'rsut', 'rlut', 'hfss', 'hfls', 'rsds', 'rsus', 'rlds', 'rlus']
ocean_variables = ['hfds', 'hfsithermds', 'thetao']
fx_variables = ['sftlf', 'areacella', 'volcello', 'areacello']
aero_variables = ['od550aer']

# Define functions

def get_results(data_rows, experiment, variable, mip, model, rip):
    """Print the results."""

    outputs = cmip5.outputs(experiment = experiment,
                            variable = variable,
                            mip = mip,
                            model = model,
                            ensemble = rip)

    for o in outputs:
        for version in o.versions:
            vtext = str(version.version)
            dataset_id = str(version.dataset_id)
            for track_id, data_file in zip(version.tracking_ids(), version.files):
                data_dict = {'file': str(data_file), 'version': vtext,
                             'track_id': str(track_id), 'dataset_id': dataset_id}
                data_rows.append(data_dict)

    return data_rows    


def main(inargs):
    """Run the program."""

    data_rows = []

    for var in atmos_variables:
        data_rows = get_results(data_rows, inargs.experiment, var, 'Amon', inargs.model, inargs.rip)
    
    for var in ocean_variables:
        data_rows = get_results(data_rows, inargs.experiment, var, 'Omon', inargs.model, inargs.rip)
    
    for var in fx_variables:
        data_rows = get_results(data_rows, inargs.experiment, var, 'fx', inargs.model, inargs.fx_rip)

    for var in aero_variables:
        data_rows = get_results(data_rows, inargs.experiment, var, 'aero', inargs.model, inargs.rip)

    df = pandas.DataFrame(data_rows)  
    df = df[['file', 'version', 'dataset_id', 'track_id']]
    df = df.sort_values(by=['file', 'version'])
    df = df.reset_index(drop=True)

    outfile = '%s/heat-budget-data-versions_%s_%s_%s.csv' %(inargs.outdir, inargs.model, inargs.experiment, inargs.rip)
    df.to_csv(outfile)
    print(outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
details:
    Uses the ARCCSSive package to get the version number and
    tracking id for the data used in global heat budget analysis
    https://arccssive.readthedocs.io/en/latest/
environment:
    vdi $ pip install --user ARCCSSive
    vdi $ export CMIP5_DB=sqlite:////g/data1/ua6/unofficial-ESG-replica/tmp/tree/cmip5_raijin_latest.db

"""

    description='Version number and tracking id information'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("model", type=str, help="model")
    parser.add_argument("experiment", type=str, help="experiment") 
    parser.add_argument("rip", type=str, help="run, intialisation, physics")
    
    parser.add_argument("--fx_rip", type=str, default='r0i0p0',
                        help="rip for fx variables") 
    parser.add_argument("--outdir", type=str, default='/g/data/r87/dbi599/data_version',
                        help="output file directory")

    args = parser.parse_args()             
    main(args)
