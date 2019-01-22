
model=CanESM2
experiment=historical
rip=r1i1p1
variable=thetao
var_long=sea_water_potential_temperature

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing


# Step 1: Drift coefficients #

coef_file=${r87_dir}/piControl/yr/ocean/${rip}/${variable}/latest/${variable}-coefficients_Oyr_${model}_piControl_${rip}_all.nc

coefficient_command="${python} ${script_dir}/calc_drift_coefficients.py ${ua6_dir}/piControl/mon/ocean/${rip}/${variable}/latest/${variable}_Omon_${model}_piControl_${rip}_*.nc ${var_long} ${coef_file} --annual"

echo ${coefficient_command}
${coefficient_command}


# Step 2: Remove drift #

data_dir=${ua6_dir}/${experiment}/mon/ocean/${rip}/${variable}/latest
dedrift_dir=${r87_dir}/${experiment}/yr/ocean/${rip}/${variable}/latest/dedrifted/

dedrift_command="${python} ${script_dir}/remove_drift.py ${ua6_dir}/${experiment}/mon/ocean/${rip}/${variable}/latest/${variable}_Omon_${model}_${experiment}_${rip}_*.nc ${var_long} annual ${coef_file} ${dedrift_dir} --annual"
# --branch_time 342005 (CCSM4) 29200 (CSIRO-Mk3-6-0) 175382.5 (FGOALS-g2) 0 (GISS-E2-R, E2-H) --no_parent_check --no_time_check

echo ${dedrift_command}
${dedrift_command}


# Step 3: Time difference #

diff_file=${dedrift_dir}/${variable}-diff_Oyr_${model}_${experiment}_${rip}_1861-1880_1986-2005.nc

diff_command="${python} ${script_dir}/calc_time_diff.py ${dedrift_dir}/${variable}_Oyr_${model}_${experiment}_${rip}_*.nc ${var_long} 1861-01-01 1880-12-31 1986-01-01 2005-12-31 ${diff_file}"

echo ${diff_command}
${diff_command}


# Step 4: Calculate OHC #

ohc_file=${r87_dir}/${experiment}/yr/ocean/${rip}/ohc/latest/dedrifted/ohc-diff_Oyr_${model}_${experiment}_${rip}_1861-1880_1986-2005.nc
volume_file=${ua6_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello_fx_${model}_historical_r0i0p0.nc

ohc_command="${python} ${script_dir}/calc_ohc.py ${diff_file} ${var_long} ${ohc_file} --volume_file ${volume_file}"

echo ${ohc_command}
${ohc_command}


