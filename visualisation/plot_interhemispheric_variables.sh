# Script for creating the various interhemispheric comparison plots
#
# Might have to calculate energy bugdet terms first: calc_system_heat_distribution.sh
#

execute=true
model=CanESM2

aa_physics=p4

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/data_processing
vis_dir=/home/599/dbi599/ocean-analysis/visualisation

ua6_dir=/g/data/ua6/DRSv2/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

# Energy plots

hist_energy_file=${r87_dir}/historical/yr/all/r1i1p1/energy-budget/latest/energy-budget_yr_${model}_historical_r1i1p1_all.nc
aa_energy_file=${r87_dir}/historicalMisc/yr/all/r1i1${aa_physics}/energy-budget/latest/energy-budget_yr_${model}_historicalMisc_r1i1${aa_physics}_all.nc
ghg_energy_file=${r87_dir}/historicalGHG/yr/all/r1i1p1/energy-budget/latest/energy-budget_yr_${model}_historicalGHG_r1i1p1_all.nc
rcp85_energy_file=${r87_dir}/rcp85/yr/all/r1i1p1/energy-budget/latest/energy-budget_yr_${model}_rcp85_r1i1p1_all.nc

hist_energy_outfile=/g/data/r87/dbi599/figures/energy-budget/energy-budget-interhemispheric-comparison_yr_${model}_historical_r1i1p1_all.png
rcp_energy_outfile=/g/data/r87/dbi599/figures/energy-budget/energy-budget-interhemispheric-comparison_yr_${model}_historical-rcp_r1i1p1_all.png

hist_energy_command="${python} ${vis_dir}/plot_interhemispheric_energy_timeseries.py ${hist_energy_file} ${aa_energy_file} ${ghg_energy_file} ${hist_energy_outfile}"
echo ${hist_energy_command}
if [[ ${execute} == true ]] ; then
    ${hist_energy_command}
fi

rcp_energy_command="${python} ${vis_dir}/plot_interhemispheric_energy_timeseries.py ${hist_energy_file} ${aa_energy_file} ${ghg_energy_file} ${rcp85_energy_file} ${rcp_energy_outfile}"
echo ${rcp_energy_command}
if [[ ${execute} == true ]] ; then
    ${rcp_energy_command}
fi

# Mass streamfunction

hist_msftmyz_file=${ua6_dir}/historical/mon/ocean/r1i1p1/msftmyz/latest/msftmyz_Omon_${model}_historical_r1i1p1_*.nc
ghg_msftmyz_file=${ua6_dir}/historicalGHG/mon/ocean/r1i1p1/msftmyz/latest/msftmyz_Omon_${model}_historicalGHG_r1i1p1_*.nc
aa_msftmyz_file=${ua6_dir}/historicalMisc/mon/ocean/r1i1${aa_physics}/msftmyz/latest/msftmyz_Omon_${model}_historicalMisc_r1i1${aa_physics}_*.nc
rcp85_msftmyz_file=${ua6_dir}/rcp85/mon/ocean/r1i1p1/msftmyz/latest/msftmyz_Omon_${model}_rcp85_r1i1p1_*.nc

spatial_msftmyz_outdir=${r87_dir}/historical/mon/ocean/r1i1p1/msftmyz/latest/
spatial_msftmyz_outfile=${spatial_msftmyz_outdir}/msftmyz-clim_Omon_${model}_historical_r1i1p1_all.png
spatial_msftmyz_command="${python} ${vis_dir}/plot_stc_spatial.py ${hist_msftmyz_file} ${spatial_msftmyz_outfile}"
echo ${spatial_msftmyz_command}
if [[ ${execute} == true ]] ; then
    mkdir -p ${spatial_msftmyz_outdir}
    ${spatial_msftmyz_command}
fi

temporal_msftmyz_outfile=/g/data/r87/dbi599/figures/msft/msftmyz-metric_Omon_${model}_historical-rcp_r1i1p1_1850-2100.png
temporal_msftmyz_command="${python} ${vis_dir}/plot_stc_metric.py ${hist_msftmyz_file} ${ghg_msftmyz_file} ${aa_msftmyz_file} ${rcp85_msftmyz_file} ${temporal_msftmyz_outfile}"
echo ${temporal_msftmyz_command}
if [[ ${execute} == true ]] ; then
    ${temporal_msftmyz_command}
fi


# Wind stress

hist_tauuo_file=${ua6_dir}/historical/mon/ocean/r1i1p1/tauuo/latest/tauuo_Omon_${model}_historical_r1i1p1_*.nc
ghg_tauuo_file=${ua6_dir}/historicalGHG/mon/ocean/r1i1p1/tauuo/latest/tauuo_Omon_${model}_historicalGHG_r1i1p1_*.nc
aa_tauuo_file=${ua6_dir}/historicalMisc/mon/ocean/r1i1${aa_physics}/tauuo/latest/tauuo_Omon_${model}_historicalMisc_r1i1${aa_physics}_*.nc
rcp85_tauuo_file=${ua6_dir}/rcp85/mon/ocean/r1i1p1/tauuo/latest/tauuo_Omon_${model}_rcp85_r1i1p1_*.nc

basin_file="--basin_file ${ua6_dir}/historical/fx/ocean/r0i0p0/basin/latest/basin_fx_${model}_historical_r0i0p0.nc"

tauuo_outfile=/g/data/r87/dbi599/figures/wind_stress/tauuo-metrics_Omon_${model}_historical-rcp_r1i1p1_1850-2100.png
tauuo_command="${python} ${vis_dir}/plot_wind_stress_metric.py ${hist_tauuo_file} ${ghg_tauuo_file} ${aa_tauuo_file} ${rcp85_tauuo_file} ${tauuo_outfile} ${basin_file}"
echo ${tauuo_command}
if [[ ${execute} == true ]] ; then
    ${tauuo_command}
fi


# Surface temperature

hist_tas_file=${ua6_dir}/historical/mon/atmos/r1i1p1/tas/latest/tas_Amon_${model}_historical_r1i1p1_*.nc
ghg_tas_file=${ua6_dir}/historicalGHG/mon/atmos/r1i1p1/tas/latest/tas_Amon_${model}_historicalGHG_r1i1p1_*.nc
aa_tas_file=${ua6_dir}/historicalMisc/mon/atmos/r1i1${aa_physics}/tas/latest/tas_Amon_${model}_historicalMisc_r1i1${aa_physics}_*.nc
rcp85_tas_file=${ua6_dir}/rcp85/mon/atmos/r1i1p1/tas/latest/tas_Amon_${model}_rcp85_r1i1p1_*.nc

tas_outfile=/g/data/r87/dbi599/figures/tas-interhemispheric/tas_Amon_${model}_historical-rcp_r1i1p1_1850-2100.png
tas_command="${python} ${vis_dir}/plot_interhemispheric_general_timeseries.py ${hist_tas_file} ${ghg_tas_file} ${aa_tas_file} ${rcp85_tas_file} air_temperature ${tas_outfile}"
echo ${tas_command}
if [[ ${execute} == true ]] ; then
    ${tas_command}
fi


# ITCZ

hist_pr_file=${ua6_dir}/historical/mon/atmos/r1i1p1/pr/latest/pr_Amon_${model}_historical_r1i1p1_*.nc
ghg_pr_file=${ua6_dir}/historicalGHG/mon/atmos/r1i1p1/pr/latest/pr_Amon_${model}_historicalGHG_r1i1p1_*.nc
aa_pr_file=${ua6_dir}/historicalMisc/mon/atmos/r1i1${aa_physics}/pr/latest/pr_Amon_${model}_historicalMisc_r1i1${aa_physics}_*.nc
rcp85_pr_file=${ua6_dir}/rcp85/mon/atmos/r1i1p1/pr/latest/pr_Amon_${model}_rcp85_r1i1p1_*.nc

pr_outfile=/g/data/r87/dbi599/figures/pr-interhemispheric/pr_Amon_${model}_historical-rcp_r1i1p1_1850-2100.png
pr_command="${python} ${vis_dir}/plot_interhemispheric_general_timeseries.py ${hist_pr_file} ${ghg_pr_file} ${aa_pr_file} ${rcp85_pr_file} precipitation_flux ${pr_outfile} --nh_lat_bounds 0 20 --sh_lat_bounds -20 0"
echo ${pr_command}
if [[ ${execute} == true ]] ; then
    ${pr_command}
fi






