#!/bin/bash
#
# Description: Run correct_mask.py over a bunch of files
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
 
    outfile=`echo ${infile} | sed s:oi10/replicas:r87/dbi599:`
    command="${python} ${script_dir}/correct_mask.py ${infile} sea_water_potential_temperature ${outfile} --mask_value 1.0"

    echo ${command}
    #${command}

done
