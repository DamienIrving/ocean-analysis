#!/bin/bash
#
# Description: Run calc_vertical_aggregate.py over a bunch of files
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
    outfile=`echo ${outfile} | sed s:DRSv3:DRSv2:`
    outfile=`echo ${outfile} | sed s:Omon:Oyr:`
    outfile=`echo ${outfile} | sed s:/mon/:/yr/:`
    outfile=`echo ${outfile} | sed s:so_:so-vertical-mean_:`
    command="${python} ${script_dir}/calc_vertical_aggregate.py ${infile} sea_water_salinity mean ${outfile} --annual"

    echo ${command}
    ${command}
    echo ${outfile}

done
