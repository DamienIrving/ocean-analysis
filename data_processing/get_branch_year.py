"""Get the branch year."""

import sys
script_dir = sys.path[0]
import os
import pdb
import argparse

import iris

import remove_drift_year_axis as rdya


def main(inargs):
    """Run the program."""

    exp_cube = iris.load(inargs.experiment_file)[0]
    cntrl_cube = iris.load(inargs.control_file)[0]

    if inargs.branch_year:
        branch_year = inargs.branch_year
    else:
        branch_year = rdya.get_branch_year(exp_cube)
    branch_index = list(cntrl_cube.coord('year').points).index(branch_year)
    print(f'Branch index: {branch_index}')
 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("experiment_file", type=str)
    parser.add_argument("control_file", type=str)
    parser.add_argument("--branch_year", type=int, default=None, help="override metadata")
    args = parser.parse_args()             
    main(args)
