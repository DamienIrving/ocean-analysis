#!/bin/bash
#
# Description: Run calc_global_sum.py for precip data files
#             

function usage {
    echo "USAGE: bash $0 file_path"
    exit 1
}


file_path=$1

institution=`echo ${file_path} | cut -d '/' -f 8`
model=`echo ${file_path} | cut -d '/' -f 9`
experiment=`echo ${file_path} | cut -d '/' -f 10`
run=`echo ${file_path} | cut -d '/' -f 11`
grid=`echo ${file_path} | cut -d '/' -f 14`
version=`echo ${file_path} | cut -d '/' -f 15`

outdir="/g/data/r87/dbi599/CMIP6/CMIP/${institution}/${model}/${experiment}/${run}/Ayr/pr/${grid}/${version}"
outfile="pr-global-sum_Ayr_${model}_${experiment}_${run}_${grid}_185001-201412.nc"
python=/g/data/r87/dbi599/miniconda3/envs/ocean3/bin/python

mkdir -p ${outdir}
command="${python} /home/599/dbi599/ocean-analysis/data_processing/calc_global_sum.py ${file_path}/*.nc precipitation_flux ${outdir}/${outfile}"
echo ${command}
${command}
