#!/bin/bash
#
# Description: Calculate sea level rise coefficients for a bunch of files
#             

function usage {
    echo "USAGE: bash $0 temperature_files"
    echo "   temperature_files:      Input temperature files"
    exit 1
}

python=/g/data/xv83/dbi599/miniconda3/envs/cmip/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

temperature_files=($@)
coefficients=(alpha beta)
temperature_var=`basename $1 | cut -d _ -f1`

if [ "${temperature_var}" == "bigthetao" ]; then
    long_name=sea_water_conservative_temperature
else
    long_name=sea_water_potential_temperature
fi

for temperature_file in "${temperature_files[@]}"; do
    salinity_file=`echo ${temperature_file} | sed s:${temperature_var}:so:g`

    for coefficient in "${coefficients[@]}"; do
        coefficient_file=`echo ${temperature_file} | sed s:${temperature_var}:${coefficient}:g`
        coefficient_file=`echo ${coefficient_file} | sed s:fs38/publications:e14/dbi599:`
        directory=`dirname ${coefficient_file}`

    command1="mkdir -p ${directory}" 
    command2="${python} ${script_dir}/calc_seawater_coefficients.py ${salinity_file} ${temperature_file} ${long_name} ${coefficient} ${coefficient_file}"

    echo ${command1}
    echo ${command2}
    ${command1}
    ${command2}

done
done

