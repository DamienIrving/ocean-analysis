
# Run susan_regrid.sh first

model=NorESM1-M
experiment=historical
rip=r1i1p1
variable=thetao

ua6_dir=/g/data/ua6/DRSv3/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

# Drift coefficients

coef_file=${r87_dir}/piControl/yr/ocean/r1i1p1/${variable}/latest/${variable}-coefficients_Oyr_${model}_piControl_r1i1p1_all_susan-grid.nc

coefficient_command="${python} ${script_dir}/calc_drift_coefficients.py ${r87_dir}/piControl/yr/ocean/r1i1p1/${variable}/latest/${variable}_Oyr_${model}_piControl_r1i1p1_??????-??????_susan-grid.nc sea_water_potential_temperature ${coef_file} --remove_outliers missing"

echo ${coefficient_command}
${coefficient_command}

# Drift removal

data_dir=${r87_dir}/${experiment}/yr/ocean/${rip}/${variable}/latest

dedrift_command="${python} ${script_dir}/remove_drift.py ${data_dir}/${variable}_Oyr_${model}_${experiment}_${rip}_??????-??????_susan-grid.nc sea_water_potential_temperature annual ${coef_file} ${data_dir}/dedrifted/ --no_parent_check --no_time_check"
# --branch_time 342005 (CCSM4) 29200 (CSIRO-Mk3-6-0) 175382.5 (FGOALS-g2) 0 (GISS-E2-R, E2-H)

echo ${dedrift_command}
${dedrift_command}

# Linear trend

trend_command="${python} ${script_dir}/calc_temporal_aggregate.py ${data_dir}/dedrifted/${variable}_Oyr_${model}_${experiment}_${rip}_??????-??????_susan-grid.nc sea_water_potential_temperature ${data_dir}/dedrifted/${variable}_Oyr_${model}_${experiment}_${rip}_1950-2005-trend_susan-grid.nc --aggregation trend --time_bounds 1950-01-01 2005-12-31 --remove_outliers missing" 

echo ${trend_command}
${trend_command}
