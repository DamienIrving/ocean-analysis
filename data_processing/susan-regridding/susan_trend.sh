
# Run regrid.sh first

model=CanESM2
experiment=historicalGHG
rip=r1i1p1
variable=thetao

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

# Drift coefficients

coef_file=${r87_dir}/piControl/yr/ocean/r1i1p1/${variable}/latest/${variable}-coefficients_Oyr_${model}_piControl_${rip}_all_susan-grid.nc

coefficient_command="${python} ${script_dir}/calc_drift_coefficients.py ${r87_dir}/piControl/yr/ocean/r1i1p1/${variable}/latest/${variable}_Oyr_${model}_piControl_${rip}_??????-??????_susan-grid.nc sea_water_potential_temperature ${coef_file} --remove_outliers"

#echo ${coefficient_command}
#${coefficient_command}

# Drift removal

data_dir=${r87_dir}/${experiment}/yr/ocean/r1i1p1/${variable}/latest

dedrift_command="${python} ${script_dir}/remove_drift.py ${data_dir}/${variable}_Oyr_${model}_${experiment}_${rip}_??????-??????_susan-grid.nc sea_water_potential_temperature annual ${coef_file} ${data_dir}/dedrifted/"
# --branch_time 342005 (CCSM4)

#echo ${dedrift_command}
#${dedrift_command}

# Linear trend

trend_command="${python} ${script_dir}/calc_temporal_aggregate.py ${data_dir}/dedrifted/${variable}_Oyr_${model}_${experiment}_${rip}_??????-??????_susan-grid.nc sea_water_potential_temperature ${data_dir}/dedrifted/${variable}_Oyr_${model}_${experiment}_${rip}_1950-2005-trend_susan-grid.nc --aggregation trend --time_bounds 1950-01-01 2005-12-31" 

echo ${trend_command}
${trend_command}
