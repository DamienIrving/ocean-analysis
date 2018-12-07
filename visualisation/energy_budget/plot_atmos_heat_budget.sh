# Script for running the plot_atmos_heat_budget.py script

model=FGOALS-g2
mip=r2i1p1
experiment=historicalMisc

fx_mip=r0i0p0
fx_experiment=historicalMisc

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/visualisation

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${experiment}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}
fx_ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${fx_experiment}
fx_r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${fx_experiment}

sftlf_file=${fx_ua6_dir}/fx/atmos/${fx_mip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_${fx_mip}.nc

outfile=/g/data/r87/dbi599/figures/heat-cycle/atmos-heat-budget_Oyr_${model}_${experiment}_${mip}_all.png   #_hf-atmos
rsds_files="--rsds_files ${ua6_dir}/mon/atmos/${mip}/rsds/latest/rsds_Amon_${model}_${experiment}_${mip}_*.nc"
rsus_files="--rsus_files ${ua6_dir}/mon/atmos/${mip}/rsus/latest/rsus_Amon_${model}_${experiment}_${mip}_*.nc"
rlds_files="--rlds_files ${ua6_dir}/mon/atmos/${mip}/rlds/latest/rlds_Amon_${model}_${experiment}_${mip}_*.nc"
rlus_files="--rlus_files ${ua6_dir}/mon/atmos/${mip}/rlus/latest/rlus_Amon_${model}_${experiment}_${mip}_*.nc"
hfss_files="--hfss_files ${ua6_dir}/mon/atmos/${mip}/hfss/latest/hfss_Amon_${model}_${experiment}_${mip}_*.nc"
hfls_files="--hfls_files ${ua6_dir}/mon/atmos/${mip}/hfls/latest/hfls_Amon_${model}_${experiment}_${mip}_*.nc"
hfds_files="--hfds_files ${ua6_dir}/mon/ocean/${mip}/hfds/latest/hfds_Omon_${model}_${experiment}_${mip}_*.nc"
hfsithermds_files="--hfsithermds_files ${ua6_dir}/mon/ocean/${mip}/hfsithermds/latest/hfsithermds_Omon_${model}_${experiment}_${mip}_*.nc"

command="${python} ${script_dir}/plot_atmos_heat_budget.py ${sftlf_file} ${outfile} ${rsds_files} ${rsus_files} ${rlds_files} ${rlus_files} ${hfss_files} ${hfls_files} ${hfds_files} --time 1850-01-01 2005-12-31"
# ${hfsithermds_files} ${hfds_files} --hfrealm ocean --plot_realm land 

echo ${command}
${command}
echo ${outfile}
