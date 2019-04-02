# run calc_interhemispheric_metric.sh first

model=GFDL-ESM2M
experiments=(historicalGHG 1pctCO2 historicalMisc rcp85)
aa_rip='r1i1p5'
regions=('sh' 'nh')

python="/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python -W ignore"
script_dir=/home/599/dbi599/ocean-analysis/data_processing

r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


# Join historical and RCP 8.5

join_command="${python} ${script_dir}/join_hist_rcp.py ${r87_dir}/historical/yr/ocean/r1i1p1/thetao/latest/thetao-mean-hemispheric-metrics_Oyr_${model}_historical_r1i1p1_all.nc ${r87_dir}/rcp85/yr/ocean/r1i1p1/thetao/latest/thetao-mean-hemispheric-metrics_Oyr_${model}_rcp85_r1i1p1_all.nc ${r87_dir}/rcp85/yr/ocean/r1i1p1/thetao/latest/thetao-mean-hemispheric-metrics_Oyr_${model}_historical-rcp85_r1i1p1_all.nc Sea_Water_Potential_Temperature_nh_mean Sea_Water_Potential_Temperature_sh_mean Sea_Water_Potential_Temperature_globe_mean"

echo ${join_command}
${join_command}


# Drift coefficients

for region in "${regions[@]}"; do

drift_command="${python} ${script_dir}/calc_drift_coefficients.py ${r87_dir}/piControl/yr/ocean/r1i1p1/thetao/latest/thetao-mean-hemispheric-metrics_Oyr_${model}_piControl_r1i1p1_all.nc Sea_Water_Potential_Temperature_${region}_mean ${r87_dir}/piControl/yr/ocean/r1i1p1/thetao/latest/thetao-${region}-mean-coefficients_Oyr_${model}_piControl_r1i1p1_all.nc"

#echo ${drift_command}
#${drift_command}

done


# Remove drift

for experiment in "${experiments[@]}"; do
for region in "${regions[@]}"; do

if [[ "${experiment}" == "historicalMisc" ]] ; then
    exp_rip=${aa_rip}
else
    exp_rip='r1i1p1'
fi

if [[ "${experiment}" == "rcp85" ]] ; then
    file_exp='historical-rcp85'
else
    file_exp=${experiment}
fi

newdir="${r87_dir}/${experiment}/yr/ocean/${exp_rip}/thetao/latest/dedrifted"
mkdir -p ${newdir}

dedrift_command="${python} ${script_dir}/remove_drift.py ${r87_dir}/${experiment}/yr/ocean/${exp_rip}/thetao/latest/thetao-mean-hemispheric-metrics_Oyr_${model}_${file_exp}_${exp_rip}_all.nc Sea_Water_Potential_Temperature_${region}_mean annual ${r87_dir}/piControl/yr/ocean/r1i1p1/thetao/latest/thetao-${region}-mean-coefficients_Oyr_${model}_piControl_r1i1p1_all.nc ${newdir}/thetao-${region}-mean_Oyr_${model}_${file_exp}_${exp_rip}_all.nc --no_parent_check --no_time_check"
# --branch_time 342005 (CCSM4) 29200 (CSIRO-Mk3-6-0) 175382.5 (FGOALS-g2) 0 (GISS-E2-R, E2-H)

echo ${dedrift_command}
${dedrift_command}

done
done


# Replace 1pctCO2 time axis

for region in "${regions[@]}"; do

time_command="${python} ${script_dir}/replace_time_axis.py ${r87_dir}/1pctCO2/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-${region}-mean_Oyr_${model}_1pctCO2_r1i1p1_all.nc ${r87_dir}/rcp85/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-${region}-mean_Oyr_${model}_historical-rcp85_r1i1p1_all.nc ${r87_dir}/1pctCO2/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-${region}-mean_Oyr_${model}_1pctCO2_r1i1p1_all-wrt-1861.nc --start_date 1861-01-01"

echo ${time_command}
${time_command}

done


# Plot

plot_file="/g/data/r87/dbi599/figures/energy-check-global/thetao-nh-sh-timeseries_yr_${model}_historicalGHGAA1pctCO2-rcp85_r1i1p1_1861-2100_uncertainty.png"

plot_command="${python} /home/599/dbi599/ocean-analysis/visualisation/excess_energy/plot_interhemispheric_heat_difference_timeseries.py ${plot_file} historical-rcp85 GHG-only AA-only 1pctCO2 --thetao_files ${r87_dir}/rcp85/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-sh-mean_Oyr_${model}_historical-rcp85_r1i1p1_all.nc ${r87_dir}/rcp85/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-nh-mean_Oyr_${model}_historical-rcp85_r1i1p1_all.nc ${r87_dir}/historicalGHG/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-sh-mean_Oyr_${model}_historicalGHG_r1i1p1_all.nc ${r87_dir}/historicalGHG/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-nh-mean_Oyr_${model}_historicalGHG_r1i1p1_all.nc ${r87_dir}/historicalMisc/yr/ocean/${aa_rip}/thetao/latest/dedrifted/thetao-sh-mean_Oyr_${model}_historicalMisc_${aa_rip}_all.nc ${r87_dir}/historicalMisc/yr/ocean/${aa_rip}/thetao/latest/dedrifted/thetao-nh-mean_Oyr_${model}_historicalMisc_${aa_rip}_all.nc ${r87_dir}/1pctCO2/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-sh-mean_Oyr_${model}_1pctCO2_r1i1p1_all-wrt-1861.nc ${r87_dir}/1pctCO2/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao-nh-mean_Oyr_${model}_1pctCO2_r1i1p1_all-wrt-1861.nc --metric diff --hline"


echo ${plot_command}
${plot_command}

echo ${plot_file}





