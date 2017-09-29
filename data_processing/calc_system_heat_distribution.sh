# Script for running the calc_system_heat_distributiuon.py script

# Might have to calculate OHC first:
#
# e.g. python calc_ohc.py /g/data/ua6/DRSv2_legacy/CMIP5/CSIRO-Mk3-6-0/historicalMisc/mon/ocean/r1i1p4/thetao/latest/thetao_Omon_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_*.nc 
#      sea_water_potential_temperature --annual

# Then afterwards plot:
#
# e.g. python plot_system_heat_distribution.py /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/all/r1i1p4/energy-budget/latest/energy-budget_yr_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_all.nc 
#      /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/all/r1i1p4/energy-budget/latest/energy-budget-trends_yr_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_1850-2005.png 
#      --aggregation trend --time 1850-01-01 2005-12-31 --infer_ohc --infer_hfbasin  # --branch_time  29200 156

execute=false
model=CanESM2

experiment=historicalGHG
mip=r1i1p1

fx_mip=r0i0p0
fx_experiment=historicalGHG

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing
vis_dir=/home/599/dbi599/ocean-analysis/visualisation

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}/${experiment}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}/${experiment}

# Calculate OHC

thetao_files=${ua6_dir}/mon/ocean/${mip}/thetao/latest/thetao_Omon_${model}_${experiment}_${mip}_*.nc

ohc_command="${python} ${script_dir}/calc_ohc.py ${thetao_files} sea_water_potential_temperature --annual"
echo ${ohc_command}
if [[ ${execute} == true ]] ; then
    ${ohc_command}
fi

# Calculate system heat distribution

energy_dir=${r87_dir}/yr/all/${mip}/energy-budget/latest
energy_file=${energy_dir}/energy-budget_yr_${model}_${experiment}_${mip}_all.nc

sftlf_file=${ua6_dir}/fx/atmos/${fx_mip}/sftlf/latest/sftlf_fx_${model}_${fx_experiment}_${fx_mip}.nc

rsdt_files="--rsdt_files ${ua6_dir}/mon/atmos/${mip}/rsdt/latest/rsdt_Amon_${model}_${experiment}_${mip}_*.nc"
rsut_files="--rsut_files ${ua6_dir}/mon/atmos/${mip}/rsut/latest/rsut_Amon_${model}_${experiment}_${mip}_*.nc"
rlut_files="--rlut_files ${ua6_dir}/mon/atmos/${mip}/rlut/latest/rlut_Amon_${model}_${experiment}_${mip}_*.nc"
rsds_files="--rsds_files ${ua6_dir}/mon/atmos/${mip}/rsds/latest/rsds_Amon_${model}_${experiment}_${mip}_*.nc"
rsus_files="--rsus_files ${ua6_dir}/mon/atmos/${mip}/rsus/latest/rsus_Amon_${model}_${experiment}_${mip}_*.nc"
rlds_files="--rlds_files ${ua6_dir}/mon/atmos/${mip}/rlds/latest/rlds_Amon_${model}_${experiment}_${mip}_*.nc"
rlus_files="--rlus_files ${ua6_dir}/mon/atmos/${mip}/rlus/latest/rlus_Amon_${model}_${experiment}_${mip}_*.nc"

hfss_files="--hfss_files ${ua6_dir}/mon/atmos/${mip}/hfss/latest/hfss_Amon_${model}_${experiment}_${mip}_*.nc"
hfls_files="--hfls_files ${ua6_dir}/mon/atmos/${mip}/hfls/latest/hfls_Amon_${model}_${experiment}_${mip}_*.nc"
hfds_files="--hfds_files ${ua6_dir}/mon/ocean/${mip}/hfds/latest/hfds_Omon_${model}_${experiment}_${mip}_*.nc"
hfbasin_files="--hfbasin_files ${ua6_dir}/mon/ocean/${mip}/hfbasin/latest/hfbasin_Omon_${model}_${experiment}_${mip}_*.nc"
hfy_files="--hfy_files ${ua6_dir}/mon/ocean/${mip}/hfy/latest/hfy_Omon_${model}_${experiment}_${mip}_*.nc"

ohc_files="--ohc_files ${r87_dir}/yr/ocean/${mip}/ohc/latest/ohc_Oyr_${model}_${experiment}_${mip}_*.nc"


command="${python} ${script_dir}/calc_system_heat_distribution.py ${sftlf_file} ${energy_file} ${rsdt_files} ${rsut_files} ${rlut_files} ${rsds_files} ${rsus_files} ${rlds_files} ${rlus_files} ${hfss_files} ${hfls_files} --hfrealm atmos ${ohc_files}"
# ${hfbasin_files} ${hfy_files} ${hfds_files}

echo ${command}
if [[ ${execute} == true ]] ; then
    ${command}
    echo ${outfile}
fi

# Plot system heat distribution

energy_2plot=${energy_dir}/energy-budget_yr_${model}_${experiment}_${mip}_all_2panel.png
energy_5plot=${energy_dir}/energy-budget_yr_${model}_${experiment}_${mip}_all_5panel.png

plot2_command="${python} ${vis_dir}/plot_system_heat_distribution.py ${energy_file} ${energy_2plot} --aggregation trend --time 1850-01-01 2005-12-31 --infer_ohc --infer_hfbasin --nregions 2"
echo ${plot2_command}
if [[ ${execute} == true ]] ; then
    ${plot2_command}
    echo ${energy_2plot}
fi

plot5_command="${python} ${vis_dir}/plot_system_heat_distribution.py ${energy_file} ${energy_5plot} --aggregation trend --time 1850-01-01 2005-12-31 --infer_ohc --infer_hfbasin --nregions 5"
echo ${plot5_command}
if [[ ${execute} == true ]] ; then
    ${plot5_command}
    echo ${energy_5plot}
fi

# Plot summary heat distribution

# python plot_system_heat_distribution_summary.py /g/data/r87/dbi599/figures/energy-budget/energy-budget-summary_yr_CSIRO-Mk3-6-0_historicalGHG-AA_r1_all.png --ghg_files /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/all/r1i1p1/energy-budget/latest/energy-budget_yr_CSIRO-Mk3-6-0_historicalGHG_r1i1p1_all.nc --aa_files /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/all/r1i1p4/energy-budget/latest/energy-budget_yr_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_all.nc 


