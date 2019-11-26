#!/bin/bash
#
# Description: Run calc_water_mass_components.py over a bunch of files
#             

function usage {
    echo "USAGE: bash $0 volume_file basin_file temperature_files"
    echo "  Remember to us mkdir -p to make the output directory first"
    echo "  e.g. mkdir -p /g/data/r87/dbi599/CMIP6/CMIP/MPI-M/MPI-ESM1-2-HR/"
    echo "                historical/r1i1p1f1/Omon/water-mass/gn/v20190710/"
    exit 1
}

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

vfile=$1
shift
bfile=$1
shift
tfiles=($@)

for tfile in "${tfiles[@]}"; do
 
    outfile=`echo ${tfile} | sed s:data1b/oi10/replicas:data/r87/dbi599:`
    outfile=`echo ${outfile} | sed s:thetao:water-mass:g`

    sfile=`echo ${tfile} | sed s:thetao:so:g`

    command="${python} ${script_dir}/calc_water_mass_components.py ${vfile} ${bfile} ${outfile} --salinity_files ${sfile} --temperature_files ${tfile}"

    echo ${command}
    ${command}
    echo ${outfile}

done
