
model=GISS-E2-R

experiment=historical
rips=(r2i1p1)

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


for var in pe; do

if [[ "${var}" == 'pr' ]] ; then
    standard_name='precipitation_flux'
elif [[ "${var}" == 'evspsbl' ]] ; then
    standard_name='water_evaporation_flux'
elif [[ "${var}" == 'pe' ]] ; then
    standard_name='precipitation_minus_evaporation_flux'
fi

for rip in "${rips[@]}"; do

mkdir -p /g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}/yr/atmos/${rip}/${var}/latest/

input_file=${r87_dir}/${experiment}/mon/atmos/${rip}/${var}/latest/${var}-ocean_Amon_${model}_${experiment}_${rip}_*.nc

output_file=${r87_dir}/${experiment}/yr/atmos/${rip}/${var}/latest/${var}-ocean-zonal-mean_Ayr_${model}_${experiment}_${rip}_all.nc

command="${python} ${script_dir}/calc_zonal_aggregate.py ${input_file} ${standard_name} mean ${output_file} --annual"

echo ${command}
${command}

done

done
