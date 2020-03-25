#!/bin/bash
#
# Description: Run calc_vertical_aggregate.py over a bunch of files
#             

function usage {
    echo "USAGE: bash $0 outfile infiles"
    echo "   outdir:       Output directory"
    echo "   infiles:      Input file names"
    exit 1
}

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing
outdir=$1
shift
infiles=($@)

for infile in "${infiles[@]}"; do
 
    filename=`echo ${infile} | rev | cut -d / -f 1 | rev`
    outfile=`echo ${filename} | sed s:Omon:Oyr:`
    outfile=`echo ${outfile} | sed s:so_:so-vertical-mean_:`
    command="${python} ${script_dir}/calc_vertical_aggregate.py ${infile} sea_water_salinity mean ${outdir}/${outfile} --annual"

    echo ${command}
    ${command}
    echo ${outdir}/${outfile}

done
