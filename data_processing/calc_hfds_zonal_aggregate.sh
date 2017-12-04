
model=NorESM1-M

experiment=historical
rips=(r1i1p1)

fx_rip=r0i0p0
fx_experiment=historical

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


for rip in "${rips[@]}"; do

## Inferred hfds

sftlf_file=${ua6_dir}/${fx_experiment}/fx/atmos/${fx_rip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_r0i0p0.nc

rsds_files="--rsds_files ${ua6_dir}/${experiment}/mon/atmos/${rip}/rsds/latest/rsds_Amon_${model}_${experiment}_${rip}_*.nc"
rsus_files="--rsus_files ${ua6_dir}/${experiment}/mon/atmos/${rip}/rsus/latest/rsus_Amon_${model}_${experiment}_${rip}_*.nc"
rlds_files="--rlds_files ${ua6_dir}/${experiment}/mon/atmos/${rip}/rlds/latest/rlds_Amon_${model}_${experiment}_${rip}_*.nc"
rlus_files="--rlus_files ${ua6_dir}/${experiment}/mon/atmos/${rip}/rlus/latest/rlus_Amon_${model}_${experiment}_${rip}_*.nc"
hfss_files="--hfss_files ${ua6_dir}/${experiment}/mon/atmos/${rip}/hfss/latest/hfss_Amon_${model}_${experiment}_${rip}_*.nc"
hfls_files="--hfls_files ${ua6_dir}/${experiment}/mon/atmos/${rip}/hfls/latest/hfls_Amon_${model}_${experiment}_${rip}_*.nc"
hfds_files="--hfds_files ${ua6_dir}/${experiment}/mon/ocean/${rip}/hfds/latest/hfds_Omon_${model}_${experiment}_${rip}_*.nc"
hfsithermds_files="--hfsithermds_files ${ua6_dir}/${experiment}/mon/ocean/${rip}/hfsithermds/latest/hfsithermds_Omon_${model}_${experiment}_${rip}_*.nc"

command="${python} ${script_dir}/calc_inferred_hfds.py ${sftlf_file} ${rsds_files} ${rsus_files} ${rlds_files} ${rlus_files} ${hfss_files} ${hfls_files}"
# ${hfsithermds_files}

#echo ${command}
#${command}
#echo ${outfile}

mkdir -p /g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}/yr/ocean/${rip}/hfds/latest/

#hfds_file=${r87_dir}/${experiment}/mon/ocean/${rip}/hfds/latest/hfds-inferred_Omon_${model}_${experiment}_${rip}_*.nc
#hfds_zs_file=${r87_dir}/${experiment}/yr/ocean/${rip}/hfds/latest/hfds-inferred-zonal-sum_Oyr_${model}_${experiment}_${rip}_all.nc

hfds_file=${ua6_dir}/${experiment}/mon/ocean/${rip}/hfds/latest/hfds_Omon_${model}_${experiment}_${rip}_*.nc
hfds_zs_file=${r87_dir}/${experiment}/yr/ocean/${rip}/hfds/latest/hfds-zonal-sum_Oyr_${model}_${experiment}_${rip}_all.nc

zs_command="${python} ${script_dir}/calc_zonal_aggregate.py ${hfds_file} surface_downward_heat_flux_in_sea_water sum ${hfds_zs_file} --annual --area"

echo ${zs_command}
${zs_command}

done
