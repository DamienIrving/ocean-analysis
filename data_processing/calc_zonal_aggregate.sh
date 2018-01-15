
model=CSIRO-Mk3-6-0

experiment=historicalGHG
rips=(r1i1p1)

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


for var in ohc; do

if [[ "${var}" == 'pr' ]] ; then
    standard_name='precipitation_flux'
    file_var='pr-ocean'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'evspsbl' ]] ; then
    standard_name='water_evaporation_flux'
    file_var='evspsbl-ocean'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'pe' ]] ; then
    standard_name='precipitation_minus_evaporation_flux'
    file_var='pe-ocean'
    realm='atmos'
    prefix='A'
    input_tscale='mon'
    temporal_agg='--annual'
elif [[ "${var}" == 'ohc' ]] ; then
    standard_name='ocean_heat_content'
    file_var='ohc'
    realm='ocean'
    prefix='O'
    input_tscale='yr'
    temporal_agg=' '
fi

for rip in "${rips[@]}"; do

mkdir -p /g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}/yr/${realm}/${rip}/${var}/latest/

input_file=${r87_dir}/${experiment}/${input_tscale}/${realm}/${rip}/${var}/latest/${file_var}_${prefix}${input_tscale}_${model}_${experiment}_${rip}_*.nc

output_file=${r87_dir}/${experiment}/yr/${realm}/${rip}/${var}/latest/${file_var}-zonal-mean_${prefix}yr_${model}_${experiment}_${rip}_all.nc

command="${python} ${script_dir}/calc_zonal_aggregate.py ${input_file} ${standard_name} mean ${output_file} ${temporal_agg}"


echo ${command}
${command}

done

done
