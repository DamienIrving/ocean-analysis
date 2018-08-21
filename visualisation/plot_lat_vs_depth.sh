# Worflow for creating latitude versus depth plots showing thetao trend and climatology
#
# Prior step:
#   calc_zonal_aggregate.sh (for globe, atlantic, pacific, indian)
#   - historical piControl historicalGHG, historicalAA
#

model=NorESM1-M

experiment=historical
rip=r1i1p1

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing
vis_dir=/home/599/dbi599/ocean-analysis/visualisation
fig_dir=/g/data/r87/dbi599/figures/thetao-zm

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

drift_command="${python} ${script_dir}/calc_drift_coefficients.py ${r87_dir}/piControl/yr/ocean/r1i1p1/thetao/latest/thetao-zonal-mean_Oyr_${model}_piControl_r1i1p1_*.nc sea_water_potential_temperature ${r87_dir}/piControl/yr/ocean/r1i1p1/thetao/latest/thetao-zonal-mean-coefficients_Oyr_${model}_piControl_r1i1p1_all.nc"
echo ${drift_command}

dedrift_dir=${r87_dir}/${experiment}/yr/ocean/${rip}/thetao/latest/dedrifted
mkdir -p ${dedrift_dir}

dedrift_command="${python} ${script_dir}/remove_drift.py ${r87_dir}/${experiment}/yr/ocean/${rip}/thetao/latest/thetao-zonal-mean_Oyr_${model}_${experiment}_${rip}_*.nc sea_water_potential_temperature annual ${r87_dir}/piControl/yr/ocean/r1i1p1/thetao/latest/thetao-zonal-mean-coefficients_Oyr_${model}_piControl_r1i1p1_all.nc ${dedrift_dir}/thetao-zonal-mean_Oyr_${model}_${experiment}_${rip}_all.nc"  
# --no_parent_check --no_time_check --branch_time 0
echo ${dedrift_command}

trend_command="${python} ${script_dir}/calc_temporal_aggregate.py ${dedrift_dir}/thetao-zonal-mean_Oyr_${model}_${experiment}_${rip}_all.nc sea_water_potential_temperature trend ${dedrift_dir}/thetao-zonal-mean_Oyr_${model}_${experiment}_${rip}_1950-2000-trend.nc --time_bounds 1950-01-01 2000-12-31"
echo ${trend_command}

clim_command="${python} ${script_dir}/calc_temporal_aggregate.py ${dedrift_dir}/thetao-zonal-mean_Oyr_${model}_${experiment}_${rip}_all.nc sea_water_potential_temperature clim ${dedrift_dir}/thetao-zonal-mean_Oyr_${model}_${experiment}${rip}_1950-2000-clim.nc --time_bounds 1950-01-01 2000-12-31"
echo ${clim_command}

plot_command="${python} ${vis_dir}/plot_lat_vs_depth.py ${dedrift_dir}/thetao-zonal-mean_Oyr_${model}_${experiment}_${rip}_1950-2000-trend.nc sea_water_potential_temperature ${fig_dir}/thetao-zonal-mean_Oyr_${model}_${experiment}_${rip}_1950-2000-trend.png --contour_file ${dedrift_dir}/thetao-zonal-mean_Oyr_${model}_${experiment}_${rip}_1950-2000-clim.nc"
echo ${plot_command}
