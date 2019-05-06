
model=GISS-E2-R
aa_p=p107
basins=(globe indian south-pacific north-pacific south-atlantic north-atlantic)
# globe indian south-pacific north-pacific south-atlantic north-atlantic

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
vis_dir=/home/599/dbi599/ocean-analysis/visualisation/water_mass
fig_dir=/g/data/r87/dbi599/figures/water_mass

ua6_dir=/g/data/ua6/DRSv3/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

volfile=${r87_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello-inferred_fx_${model}_historical_r0i0p0.nc
# ${r87_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello-inferred_fx_${model}_historical_r0i0p0.nc
# ${ua6_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello_fx_${model}_historical_r0i0p0.nc

for basin in "${basins[@]}"; do

outfile=${fig_dir}/thetao-volume-dist_Oyr_${model}_historical-GHG-AA_r1_${basin}_1861-2005.png

plot="${python} ${vis_dir}/plot_volume_distribution.py sea_water_potential_temperature ${volfile} ${r87_dir}/historical/fx/ocean/r0i0p0/basin/latest/basin-inferred_fx_${model}_historical_r0i0p0.nc ${outfile} --data_files /g/data/r87/dbi599/data_en4/processed/thetao_Oyr_EN4-g10_????-????.nc --data_files ${r87_dir}/historical/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_${model}_historical_r1i1p1_??????-??????.nc --data_files ${r87_dir}/historicalGHG/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_${model}_historicalGHG_r1i1p1_??????-??????.nc --data_files ${r87_dir}/historicalMisc/yr/ocean/r1i1${aa_p}/thetao/latest/dedrifted/thetao_Oyr_${model}_historicalMisc_r1i1${aa_p}_??????-??????.nc --ref_volume_file /g/data/r87/dbi599/data_en4/processed/volcello-inferred_fx_EN4-g10.nc --ref_basin_file /g/data/r87/dbi599/data_en4/processed/basin-inferred_fx_EN4-g10.nc --basin ${basin} --bin_bounds -2.5 35.5 --colors grey black red blue --labels EN4 historical GHG-only AA-only --time_bounds 1861-01-01 2005-12-31  --metrics dV/dT dVdT/dt dV/dt dVdt/dVdT --subplot_config 2 2"
# --ylim -0.006 0.006 3

echo ${plot}
${plot}

display ${outfile} &

done
