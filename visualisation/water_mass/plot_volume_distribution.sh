
model=CanESM2
aa_p=p4
basins=(globe)
# globe indian south-pacific north-pacific south-atlantic north-atlantic
var=so
#thetao so


python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
vis_dir=/home/599/dbi599/ocean-analysis/visualisation/water_mass
fig_dir=/g/data/r87/dbi599/figures/water_mass

ua6_dir=/g/data/ua6/DRSv3/CMIP5/${model}
r87_dir=/g/data/r87/dbi599/DRSv2/CMIP5/${model}

volfile=${r87_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello-inferred_fx_${model}_historical_r0i0p0.nc
# ${r87_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello-inferred_fx_${model}_historical_r0i0p0.nc
# ${ua6_dir}/historical/fx/ocean/r0i0p0/volcello/latest/volcello_fx_${model}_historical_r0i0p0.nc

if [[ "${var}" == "thetao" ]] ; then
    name=sea_water_potential_temperature
    bin_min=-2.5
    bin_max=35.5
    bin_width=1.0
elif [[ "${var}" == "so" ]] ; then
    name=sea_water_salinity
    bin_min=33
    bin_max=36
    bin_width=0.1
fi

for basin in "${basins[@]}"; do

outfile=${fig_dir}/${var}-volume-dist_Oyr_${model}_historical-GHG-AA_r1_${basin}_1861-2005.png

plot="${python} ${vis_dir}/plot_volume_distribution.py ${name} ${volfile} ${r87_dir}/historical/fx/ocean/r0i0p0/basin/latest/basin-inferred_fx_${model}_historical_r0i0p0.nc ${outfile} --data_files ${r87_dir}/historical/yr/ocean/r1i1p1/${var}/latest/dedrifted/${var}_Oyr_${model}_historical_r1i1p1_??????-??????.nc --data_files ${r87_dir}/historicalGHG/yr/ocean/r1i1p1/${var}/latest/dedrifted/${var}_Oyr_${model}_historicalGHG_r1i1p1_??????-??????.nc --data_files ${r87_dir}/historicalMisc/yr/ocean/r1i1${aa_p}/${var}/latest/dedrifted/${var}_Oyr_${model}_historicalMisc_r1i1${aa_p}_??????-??????.nc --basin ${basin} --bin_bounds ${bin_min} ${bin_max} --bin_width ${bin_width} --colors black red blue --labels historical GHG-only AA-only --time_bounds 1861-01-01 2005-12-31 --metrics dV/dT dVdT/dt dV/dt dVdt/dVdT --subplot_config 2 2"

echo ${plot}
${plot}

display ${outfile} &

done

#--ref_basin_file /g/data/r87/dbi599/data_en4/processed/basin-inferred_fx_EN4-g10.nc
#--ref_volume_file /g/data/r87/dbi599/data_en4/processed/volcello-inferred_fx_EN4-g10.nc
#--data_files ${r87_dir}/historical/yr/ocean/r1i1p1/${var}/latest/dedrifted/${var}_Oyr_${model}_historical_r1i1p1_??????-??????.nc
#--data_files ${r87_dir}/historicalGHG/yr/ocean/r1i1p1/${var}/latest/dedrifted/${var}_Oyr_${model}_historicalGHG_r1i1p1_??????-??????.nc
#--data_files ${r87_dir}/historicalMisc/yr/ocean/r1i1${aa_p}/${var}/latest/dedrifted/${var}_Oyr_${model}_historicalMisc_r1i1${aa_p}_??????-??????.nc


# 


# --data_files /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_185001-185912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_186001-186912_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_187001-187912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_188001-188912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_189001-189912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_190001-190912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_191001-191912_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_192001-192912_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_193001-193912_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_194001-194912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_195001-195912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_196001-196912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_197001-197912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_198001-198912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_199001-199912.nc /g/data/r87/dbi599/DRSv2/CMIP5/CCSM4/historicalMisc/yr/ocean/r1i1p10/thetao/latest/dedrifted/thetao_Oyr_CCSM4_historicalMisc_r1i1p10_200001-200512.nc

#--data_files /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_185001-185312.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_185401-185712_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_185801-186112.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_186201-186512.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_186601-186912.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_187001-187312.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_187401-187712.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_187801-188112.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_188201-188512.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_188601-188912.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_189001-189312.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_189401-189712.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_189801-190112_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_190201-190512.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_190601-190912.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_191001-191312.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_191401-191712.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_191801-192112_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_192201-192512.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_192601-192912.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_193001-193312_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_193401-193712.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_193801-194112.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_194201-194512.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_194601-194912.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_195001-195312.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_195401-195712_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_195801-196112.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_196201-196512.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_196601-196912.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_197001-197312.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_197401-197712.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_197801-198112.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_198201-198512.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_198601-198912_fixed.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_199001-199312.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_199401-199712.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_199801-200112.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historicalMisc/yr/ocean/r1i1p1/thetao/latest/dedrifted/thetao_Oyr_NorESM1-M_historicalMisc_r1i1p1_200201-200512.nc
