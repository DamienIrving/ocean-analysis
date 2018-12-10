#!/bin/bash
#
# Description: Run calc_annual.py over a bunch of files
#             

function usage {
    echo "USAGE: bash $0 infiles"
    echo "   infiles:      Input file names"
    exit 1
}

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

infiles=($@)

for infile in "${infiles[@]}"; do
 
    outfile=`echo ${infile} | sed s:ua6:r87/dbi599:`
    outfile=`echo ${outfile} | sed s:Omon:Oyr:`
    outfile=`echo ${outfile} | sed s:/mon/:/yr/:`
    command="${python} ${script_dir}/calc_annual.py ${infile} sea_water_potential_temperature ${outfile}"

    echo ${command}
    ${command}

done
