
model=CSIRO-Mk3-6-0
experiment=historical
#rip=r1i1p1

direction='meridional'
# zonal meridional

python="/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python -W ignore"
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv3/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

outlier_threshold="--outlier_threshold 0.01"

area_file=${ua6_dir}/historical/fx/ocean/r0i0p0/areacello/latest/areacello_fx_${model}_historical_r0i0p0.nc
volume_file=${ua6_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello_fx_${model}_historical_r0i0p0.nc
ref_file=" "
# " " if already lat/lon
# --ref_file ${ua6_dir}/${experiment}/mon/atmos/r1i1p1/rsdt/latest/rsdt_Amon_${model}_${experiment}_r1i1p1_185001-200512.nc toa_incoming_shortwave_flux


## wfo

### Control horizontal cumsum
control_dir=${r87_dir}/piControl/yr/ocean/r1i1p1/wfo/latest
mkdir -p ${control_dir}

control_horizontal_sum_file=${control_dir}/wfo-${direction}-sum_Oyr_${model}_piControl_r1i1p1_cumsum-all.nc
control_horizontal_sum_command="${python} ${script_dir}/calc_horizontal_aggregate.py ${ua6_dir}/piControl/mon/ocean/r1i1p1/wfo/latest/wfo_Omon_${model}_piControl_r1i1p1_??????-??????.nc water_flux_into_sea_water ${direction} sum ${control_horizontal_sum_file} --annual ${ref_file} --cumsum --area ${area_file} --flux_to_mag"

#echo ${control_horizontal_sum_command}
#${control_horizontal_sum_command}

### Experiment horizontal cumsum
experiment_horizontal_cumsum_file=${r87_dir}/${experiment}/yr/ocean/r1i1p1/wfo/latest/wfo-${direction}-sum_Oyr_${model}_${experiment}_r1i1p1_cumsum-all.nc
experiment_horizontal_cumsum_command="${python} ${script_dir}/calc_horizontal_aggregate.py ${ua6_dir}/${experiment}/mon/ocean/r1i1p1/wfo/latest/wfo_Omon_${model}_${experiment}_r1i1p1_??????-??????.nc water_flux_into_sea_water ${direction} sum ${experiment_horizontal_cumsum_file} --annual ${ref_file} --cumsum --area ${area_file} --flux_to_mag"

#echo ${experiment_horizontal_cumsum_command}
#${experiment_horizontal_cumsum_command}

### Experiment horizontal sum
experiment_horizontal_sum_file=${r87_dir}/${experiment}/yr/ocean/r1i1p1/wfo/latest/wfo-${direction}-sum_Oyr_${model}_${experiment}_r1i1p1_all.nc
experiment_horizontal_sum_command="${python} ${script_dir}/calc_horizontal_aggregate.py ${ua6_dir}/${experiment}/mon/ocean/r1i1p1/wfo/latest/wfo_Omon_${model}_${experiment}_r1i1p1_??????-??????.nc water_flux_into_sea_water ${direction} sum ${experiment_horizontal_sum_file} --annual ${ref_file} --area ${area_file} --flux_to_mag"

echo ${experiment_horizontal_sum_command}
${experiment_horizontal_sum_command}


### Drift coefficients
wfo_coefficient_file=${r87_dir}/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-${direction}-sum-coefficients_Oyr_${model}_piControl_r1i1p1_cumsum-all.nc
wfo_coefficient_command="${python} ${script_dir}/calc_drift_coefficients.py ${control_horizontal_sum_file} water_flux_into_sea_water ${wfo_coefficient_file}"

#echo ${wfo_coefficient_command}
#${wfo_coefficient_command}

### Remove drift
wfo_drift_command="${python} ${script_dir}/remove_drift.py ${experiment_horizontal_sum_file} water_flux_into_sea_water annual ${wfo_coefficient_file} ${r87_dir}/${experiment}/yr/ocean/r1i1p1/wfo/latest/dedrifted/wfo-${direction}-sum_Oyr_${model}_${experiment}_r1i1p1_cumsum-all.nc --no_data_check"

#echo ${wfo_drift_command}
#${wfo_drift_command}


## so

### Vertical aggregation
#bash ${script_dir}/calc_vertical_aggregate.sh ${ua6_dir}/${experiment}/mon/ocean/r1i1p1/so/latest/so_Omon_${model}_${experiment}_r1i1p1_??????-??????.nc
#bash ${script_dir}/calc_vertical_aggregate.sh ${ua6_dir}/piControl/mon/ocean/r1i1p1/so/latest/so_Omon_${model}_piControl_r1i1p1_??????-??????.nc

vol_dir=${r87_dir}/historical/fx/ocean/r0i0p0/volcello/latest
mkdir -p ${vol_dir}

weights_file=${r87_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello-vertical-sum_fx_${model}_historical_r0i0p0.nc
volint_command="${python} ${script_dir}/calc_vertical_aggregate.py ${volume_file} ocean_volume sum  ${weights_file}"

#echo ${volint_command}
#${volint_command}


### Control horizontal mean
control_dir=${r87_dir}/piControl/yr/ocean/r1i1p1/so/latest
mkdir -p ${control_dir}

control_horizontal_mean_file=${control_dir}/so-vertical-${direction}-mean_Oyr_${model}_piControl_r1i1p1_all.nc
control_horizontal_mean_command="${python} ${script_dir}/calc_horizontal_aggregate.py ${r87_dir}/piControl/yr/ocean/r1i1p1/so/latest/so-vertical-mean_Oyr_${model}_piControl_r1i1p1_??????-??????.nc sea_water_salinity ${direction} mean ${control_horizontal_mean_file} --weights ${weights_file} ${ref_file}"

#echo ${control_horizontal_mean_command}
#${control_horizontal_mean_command}

### Experiment horizontal mean
experiment_horizontal_mean_file=${r87_dir}/${experiment}/yr/ocean/r1i1p1/so/latest/so-vertical-${direction}-mean_Oyr_${model}_${experiment}_r1i1p1_all.nc
experiment_horizontal_mean_command="${python} ${script_dir}/calc_horizontal_aggregate.py ${r87_dir}/${experiment}/yr/ocean/r1i1p1/so/latest/so-vertical-mean_Oyr_${model}_${experiment}_r1i1p1_??????-??????.nc sea_water_salinity ${direction} mean ${experiment_horizontal_mean_file} --weights ${weights_file} ${ref_file}"

#$echo ${experiment_horizontal_mean_command}
#${experiment_horizontal_mean_command}

### Drift coefficients
so_coefficient_file=${r87_dir}/piControl/yr/ocean/r1i1p1/so/latest/so-vertical-${direction}-mean-coefficients_Oyr_${model}_piControl_r1i1p1_all.nc
so_coefficient_command="${python} ${script_dir}/calc_drift_coefficients.py ${control_horizontal_mean_file} sea_water_salinity ${so_coefficient_file} ${outlier_threshold}"

#echo ${so_coefficient_command}
#${so_coefficient_command}

### Remove drift
so_drift_command="${python} ${script_dir}/remove_drift.py ${experiment_horizontal_mean_file} sea_water_salinity annual ${so_coefficient_file} ${r87_dir}/${experiment}/yr/ocean/r1i1p1/so/latest/dedrifted/so-vertical-${direction}-mean_Oyr_${model}_${experiment}_r1i1p1_all.nc --no_data_check"

#echo ${so_drift_command}
#${so_drift_command}

