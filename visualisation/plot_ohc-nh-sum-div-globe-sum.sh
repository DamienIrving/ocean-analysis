
model=GISS-E2-R
aa_mip=r1i1p107

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script_dir=/home/599/dbi599/ocean-analysis/visualisation



raw_outfile=/g/data/r87/dbi599/figures/ohc-zi/ohc-nh-sum-div-globe-sum_Oyr_${model}_historicalGHGAApiControl_r1_all.png

raw_command="${python} ${script_dir}/plot_temporal_ensemble.py ocean_heat_content_nh_sum_div_globe_sum ${raw_outfile} --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historicalGHG/yr/ocean/r1i1p1/ohc/latest/ohc-sum-hemispheric-metrics_Oyr_${model}_historicalGHG_r1i1p1_all.nc --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/yr/ocean/r1i1p1/ohc/latest/ohc-sum-hemispheric-metrics_Oyr_${model}_historical_r1i1p1_all.nc --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historicalMisc/yr/ocean/${aa_mip}/ohc/latest/ohc-sum-hemispheric-metrics_Oyr_${model}_historicalMisc_${aa_mip}_all.nc --control_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/piControl/yr/ocean/r1i1p1/ohc/latest/ohc-sum-hemispheric-metrics_Oyr_${model}_piControl_r1i1p1_all.nc --ensagg mean --single_run --ylabel % --branch_time 0"
# --branch_time 342005 (CCSM4) 175382.5 (FGOALS-g2) 0 (GISS-E2-R)

full_outfile=/g/data/r87/dbi599/figures/ohc-zi/ohc-nh-sum-div-globe-sum_Oyr_${model}_historicalGHGAAfullpiControl_r1_all.png

raw_full_command="${python} ${script_dir}/plot_temporal_ensemble.py ocean_heat_content_nh_sum_div_globe_sum ${full_outfile} --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historicalGHG/yr/ocean/r1i1p1/ohc/latest/ohc-sum-hemispheric-metrics_Oyr_${model}_historicalGHG_r1i1p1_all.nc --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/yr/ocean/r1i1p1/ohc/latest/ohc-sum-hemispheric-metrics_Oyr_${model}_historical_r1i1p1_all.nc --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historicalMisc/yr/ocean/${aa_mip}/ohc/latest/ohc-sum-hemispheric-metrics_Oyr_${model}_historicalMisc_${aa_mip}_all.nc --control_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/piControl/yr/ocean/r1i1p1/ohc/latest/ohc-sum-hemispheric-metrics_Oyr_${model}_piControl_r1i1p1_all.nc --ensagg mean --single_run --ylabel % --full_control --branch_time 0"
# --branch_time 342005 (CCSM4) 175382.5 (FGOALS-g2) 0 (GISS-E2-R)

dedrift_outfile=/g/data/r87/dbi599/figures/ohc-zi/ohc-nh-sum-div-globe-sum-dedrifted_Oyr_${model}_historicalGHGAA_r1_all.png

dedrifted_command="${python} ${script_dir}/plot_temporal_ensemble.py ocean_heat_content_nh_sum_div_globe_sum ${dedrift_outfile} --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historicalGHG/yr/ocean/r1i1p1/ohc/latest/dedrifted/ohc-nh-sum-div-globe-sum_Oyr_${model}_historicalGHG_r1i1p1_all.nc --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historical/yr/ocean/r1i1p1/ohc/latest/dedrifted/ohc-nh-sum-div-globe-sum_Oyr_${model}_historical_r1i1p1_all.nc --hist_files /g/data/r87/dbi599/DRSv2/CMIP5/${model}/historicalMisc/yr/ocean/${aa_mip}/ohc/latest/dedrifted/ohc-nh-sum-div-globe-sum_Oyr_${model}_historicalMisc_${aa_mip}_all.nc --ensagg mean --single_run --ylabel %"


echo ${raw_command}
${raw_command}

echo ${raw_full_command}
${raw_full_command}

echo ${dedrifted_command}
${dedrifted_command}

display ${raw_outfile} &
display ${full_outfile} &
display ${dedrift_outfile} &



