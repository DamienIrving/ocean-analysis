#!/bin/bash
#
# Description: Run calc_basin_aggregate.py over a bunch of files
#             

function usage {
    echo "USAGE: bash $0 basin_file weight_file infiles"
    echo "   basin_file:       Basin file"
    echo "   weight_file:      Weight file"
    echo "   infiles:          Input file names"
    exit 1
}

python=/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

basin_file=$1
shift
weight_file=$1
shift
infiles=($@)

for infile in "${infiles[@]}"; do
 
    outfile=`echo ${infile} | sed s:oi10/replicas:r87/dbi599:`
    outfile=`echo ${outfile} | sed s:Omon:Oyr:g`
    outfile=`echo ${outfile} | sed s:thetao_:thetao-basin-mean_:`
    command="${python} ${script_dir}/calc_basin_aggregate.py ${infile} sea_water_potential_temperature mean ${basin_file} ${outfile} --weights ${weight_file} --annual --chunk"

    echo ${command}
    ${command}

done

