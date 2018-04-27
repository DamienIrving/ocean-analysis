
model=GFDL-CM3

experiments=(historical historicalGHG historicalMisc)
rip=r1i1p1

control_rip=r1i1p1

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

for experiment in "${experiments[@]}"; do

command="${python} ${script_dir}/calc_ohc.py ${ua6_dir}/${experiment}/mon/ocean/${rip}/thetao/latest/thetao_Omon_${model}_${experiment}_${rip}_*.nc sea_water_potential_temperature --area_file ${ua6_dir}/${fx_experiment}/fx/ocean/${fx_rip}/areacello/latest/areacello_fx_${model}_${fx_experiment}_${fx_rip}.nc --annual"

control_file=${r87_dir}/piControl/yr/ocean/${control_rip}/ohc/latest/ohc-zonal-sum_Oyr_${model}_piControl_${control_rip}_all.nc
coefficient_file=${r87_dir}/piControl/yr/ocean/${control_rip}/ohc/latest/ohc-zonal-sum-coefficients_Oyr_${model}_piControl_${control_rip}_all.nc
experiment_dir=${r87_dir}/${experiment}/yr/ocean/${rip}/ohc/latest
experiment_name=ohc-zonal-sum_Oyr_${model}_${experiment}_${rip}_all.nc
experiment_file=${experiment_dir}/${experiment_name}
dedrifted_dir=${experiment_dir}/dedrifted
dedrifted_file=${dedrifted_dir}/${experiment_name}

coefficient_command="${python} ${script_dir}/calc_drift_coefficients.py ${control_file} ocean_heat_content ${coefficient_file}"
mkdir_command="mkdir ${dedrifted_dir}"
drift_command="${python} ${script_dir}/remove_drift.py ${experiment_file} ocean_heat_content annual ${coefficient_file} ${dedrifted_file}"
# --branch_time 342005 (CCSM4)

echo ${coefficient_command}
${coefficient_command}

echo ${mkdir_command}
${mkdir_command}

echo ${drift_command}
${drift_command}

done

