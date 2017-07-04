# Script for running the plot_atmos_heat_budget.py script
# May need to run apply_mask.sh first to apply ocean mask to atmos data

model=CSIRO-Mk3-6-0
mip=r1i1p1
experiment=historicalGHG

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/visualisation

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${experiment}/mon
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}/mon

outfile=/g/data/r87/dbi599/figures/heat-cycle/atmos-heat-budget_Oyr_${model}_${experiment}_${mip}_all.png
rsds_files="--rsds_files ${r87_dir}/ocean/${mip}/rsds/latest/rsds_Omon_${model}_${experiment}_${mip}_*.nc"
rsus_files="--rsus_files ${r87_dir}/ocean/${mip}/rsus/latest/rsus_Omon_${model}_${experiment}_${mip}_*.nc"
rlds_files="--rlds_files ${r87_dir}/ocean/${mip}/rlds/latest/rlds_Omon_${model}_${experiment}_${mip}_*.nc"
rlus_files="--rlus_files ${r87_dir}/ocean/${mip}/rlus/latest/rlus_Omon_${model}_${experiment}_${mip}_*.nc"
hfss_files="--hfss_files ${r87_dir}/ocean/${mip}/hfss/latest/hfss_Omon_${model}_${experiment}_${mip}_*.nc"
hfls_files="--hfls_files ${r87_dir}/ocean/${mip}/hfls/latest/hfls_Omon_${model}_${experiment}_${mip}_*.nc"
hfds_files="--hfds_files ${ua6_dir}/ocean/${mip}/hfds/latest/hfds_Omon_${model}_${experiment}_${mip}_*.nc"
hfsithermds_files="--hfsithermds_files ${ua6_dir}/ocean/${mip}/hfsithermds/latest/hfsithermds_Omon_${model}_${experiment}_${mip}_*.nc"

command="${python} ${script_dir}/plot_atmos_heat_budget.py ${outfile} ${rsds_files} ${rsus_files} ${rlds_files} ${rlus_files} ${hfss_files} ${hfls_files} ${hfds_files} --area"

echo ${command}
${command}
echo ${outfile}
