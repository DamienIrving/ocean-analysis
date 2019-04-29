
model=CSIRO-Mk3-6-0
aa_p=p4
basins=(indian south-pacific north-pacific south-atlantic north-atlantic)
# globe indian south-pacific north-pacific south-atlantic north-atlantic

python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
vis_dir=/home/599/dbi599/ocean-analysis/visualisation/water_mass
fig_dir=/g/data/r87/dbi599/figures/water_mass

ua6_dir=/g/data/ua6/DRSv3/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}


for basin in "${basins[@]}"; do

outfile=${fig_dir}/thetao-volume-dist_Oyr_CSIRO-Mk3-6-0_historical-GHG-AA_r1_${basin}_1861-2005.png

plot="${python} ${vis_dir}/plot_volume_distribution.py sea_water_potential_temperature /g/data/ua6/DRSv3/CMIP5/CSIRO-Mk3-6-0/historical/fx/ocean/r0i0p0/volcello/latest/volcello_fx_CSIRO-Mk3-6-0_historical_r0i0p0.nc /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historical/fx/ocean/r0i0p0/basin/latest/basin_fx_CSIRO-Mk3-6-0_historical_r0i0p0.nc ${outfile} --data_files /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historical/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_CSIRO-Mk3-6-0_historical_r1i1p1_??????-??????.nc --data_files /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalGHG/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_CSIRO-Mk3-6-0_historicalGHG_r1i1p1_??????-??????.nc --data_files /g/data/r87/dbi599/DRSv2/CMIP5/CSIRO-Mk3-6-0/historicalMisc/yr/ocean/r1i1${aa_p}/thetao/latest/dedrifted/thetao_Oyr_CSIRO-Mk3-6-0_historicalMisc_r1i1${aa_p}_??????-??????.nc --basin ${basin} --bin_bounds -2.5 35.5 --colors black red blue --labels historical GHG-only AA-only --time_bounds 1861-01-01 2005-12-31 --metrics dV/dT dVdT/dt dV/dt dVdt/dVdT --subplot_config 2 2"
# --ylim -0.006 0.006 3

echo ${plot}
${plot}

display ${outfile} &

done
