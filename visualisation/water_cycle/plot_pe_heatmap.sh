python=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
script=/home/599/dbi599/ocean-analysis/visualisation/water_cycle/plot_pe_heatmap.py
vars=(pe pr-pe evspsbl-pe)
stats=(mean median)
units=('--pct' '--scale_factor 16')

for var in "${vars[@]}"; do

if [[ "${var}" == "pe" ]] ; then
    var_dir='pe'
    var_long='precipitation_minus_evaporation_flux'
elif [[ "${var}" == "pr-pe" ]] ; then
    var_dir='pr'
    var_long='precipitation_flux'
elif [[ "${var}" == 'evspsbl-pe' ]] ; then
    var_dir='evspsbl'
    var_long='water_evapotranspiration_flux'
fi

for stat in "${stats[@]}"; do

hist_command="${python} ${script} /g/data/r87/dbi599/CMIP6/CMIP/CSIRO/ACCESS-ESM1-5/historical/r1i1p1f1/Ayr/${var_dir}/gn/v20191115/${var}-region-sum-anomaly_Ayr_ACCESS-ESM1-5_historical_r1i1p1f1_gn_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP6/CMIP/BCC/BCC-CSM2-MR/historical/r1i1p1f1/Ayr/${var_dir}/gn/v20181126/${var}-region-sum-anomaly_Ayr_BCC-CSM2-MR_historical_r1i1p1f1_gn_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP6/CMIP/CCCma/CanESM5/historical/r1i1p1f1/Ayr/${var_dir}/gn/v20190429/${var}-region-sum-anomaly_Ayr_CanESM5_historical_r1i1p1f1_gn_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP6/CMIP/NCAR/CESM2/historical/r1i1p1f1/Ayr/${var_dir}/gn/v20190308/${var}-region-sum-anomaly_Ayr_CESM2_historical_r1i1p1f1_gn_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP6/CMIP/NOAA-GFDL/GFDL-ESM4/historical/r1i1p1f1/Ayr/${var_dir}/gr1/v20190726/${var}-region-sum-anomaly_Ayr_GFDL-ESM4_historical_r1i1p1f1_gr1_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/historical/r1i1p1f1/Ayr/${var_dir}/gr/v20180803/${var}-region-sum-anomaly_Ayr_IPSL-CM6A-LR_historical_r1i1p1f1_gr_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP6/CMIP/MIROC/MIROC6/historical/r1i1p1f1/Ayr/${var_dir}/gn/v20181212/${var}-region-sum-anomaly_Ayr_MIROC6_historical_r1i1p1f1_gn_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/NCAR/CCSM4/historical/r1i1p1/Ayr/${var_dir}/gn/v20160829/${var}-region-sum-anomaly_Ayr_CCSM4_historical_r1i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/CSIRO-QCCCE/CSIRO-Mk3-6-0/historical/r1i1p1/Ayr/${var_dir}/gn/v20110518/${var}-region-sum-anomaly_Ayr_CSIRO-Mk3-6-0_historical_r1i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/CCCma/CanESM2/historical/r1i1p1/Ayr/${var_dir}/gn/v20120718/${var}-region-sum-anomaly_Ayr_CanESM2_historical_r1i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/LASG-CESS/FGOALS-g2/historical/r1i1p1/Ayr/${var_dir}/gn/v1/${var}-region-sum-anomaly_Ayr_FGOALS-g2_historical_r1i1p1_gn_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/NOAA-GFDL/GFDL-CM3/historical/r1i1p1/Ayr/${var_dir}/gn/v20120227/${var}-region-sum-anomaly_Ayr_GFDL-CM3_historical_r1i1p1_gn_186001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/NOAA-GFDL/GFDL-ESM2M/historical/r1i1p1/Ayr/${var_dir}/gn/v20111228/${var}-region-sum-anomaly_Ayr_GFDL-ESM2M_historical_r1i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/NASA-GISS/GISS-E2-H/historical/r1i1p1/Ayr/${var_dir}/gn/v20160426/${var}-region-sum-anomaly_Ayr_GISS-E2-H_historical_r1i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/IPSL/IPSL-CM5A-LR/historical/r1i1p1/Ayr/${var_dir}/gn/v20110406/${var}-region-sum-anomaly_Ayr_IPSL-CM5A-LR_historical_r1i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/CMIP/NCC/NorESM1-M/historical/r1i1p1/Ayr/${var_dir}/gn/v20110901/${var}-region-sum-anomaly_Ayr_NorESM1-M_historical_r1i1p1_gn_185001-200512-cumsum.nc ${var_long} cumulative_anomaly /g/data/r87/dbi599/figures/water-cycle/${var}-region-sum-anomaly_Ayr_ensemble-${stat}-heatmap_historical_r1_gn_1861-2005-cumsum.png --time_bounds 1861-01-01 2005-12-31 --scale_factor 17 --ensemble_stat ${stat} --experiment historical --vmax 4.5"

#echo ${hist_command}
#${hist_command}

aa_command="${python} ${script} /g/data/r87/dbi599/CMIP6/DAMIP/CSIRO/ACCESS-ESM1-5/hist-aer/r1i1p1f1/Ayr/${var_dir}/gn/v20200615/${var}-region-sum-anomaly_Ayr_ACCESS-ESM1-5_hist-aer_r1i1p1f1_gn_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/BCC/BCC-CSM2-MR/hist-aer/r1i1p1f1/Ayr/${var_dir}/gn/v20190507/${var}-region-sum-anomaly_Ayr_BCC-CSM2-MR_hist-aer_r1i1p1f1_gn_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/CCCma/CanESM5/hist-aer/r1i1p1f1/Ayr/${var_dir}/gn/v20190429/${var}-region-sum-anomaly_Ayr_CanESM5_hist-aer_r1i1p1f1_gn_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/NCAR/CESM2/hist-aer/r1i1p1f1/Ayr/${var_dir}/gn/v20200206/${var}-region-sum-anomaly_Ayr_CESM2_hist-aer_r1i1p1f1_gn_185001-201412-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/NOAA-GFDL/GFDL-ESM4/hist-aer/r1i1p1f1/Ayr/${var_dir}/gr1/v20180701/${var}-region-sum-anomaly_Ayr_GFDL-ESM4_hist-aer_r1i1p1f1_gr1_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/IPSL/IPSL-CM6A-LR/hist-aer/r1i1p1f1/Ayr/${var_dir}/gr/v20180914/${var}-region-sum-anomaly_Ayr_IPSL-CM6A-LR_hist-aer_r1i1p1f1_gr_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/MIROC/MIROC6/hist-aer/r1i1p1f1/Ayr/${var_dir}/gn/v20190705/${var}-region-sum-anomaly_Ayr_MIROC6_hist-aer_r1i1p1f1_gn_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NCAR/CCSM4/historicalMisc/r1i1p10/Ayr/${var_dir}/gn/v20120604/${var}-region-sum-anomaly_Ayr_CCSM4_historicalMisc_r1i1p10_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/CSIRO-QCCCE/CSIRO-Mk3-6-0/historicalMisc/r1i1p4/Ayr/${var_dir}/gn/v20110518/${var}-region-sum-anomaly_Ayr_CSIRO-Mk3-6-0_historicalMisc_r1i1p4_gn_185001-201212-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/CCCma/CanESM2/historicalMisc/r1i1p4/Ayr/${var_dir}/gn/v20111028/${var}-region-sum-anomaly_Ayr_CanESM2_historicalMisc_r1i1p4_gn_185001-201212-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/LASG-CESS/FGOALS-g2/historicalMisc/r2i1p1/Ayr/${var_dir}/gn/v20161204/${var}-region-sum-anomaly_Ayr_FGOALS-g2_historicalMisc_r2i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NOAA-GFDL/GFDL-CM3/historicalMisc/r1i1p1/Ayr/${var_dir}/gn/v20120227/${var}-region-sum-anomaly_Ayr_GFDL-CM3_historicalMisc_r1i1p1_gn_186001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NOAA-GFDL/GFDL-ESM2M/historicalMisc/r1i1p5/Ayr/${var_dir}/gn/v20130214/${var}-region-sum-anomaly_Ayr_GFDL-ESM2M_historicalMisc_r1i1p5_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NASA-GISS/GISS-E2-H/historicalMisc/r1i1p107/Ayr/${var_dir}/gn/v20160427/${var}-region-sum-anomaly_Ayr_GISS-E2-H_historicalMisc_r1i1p107_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/IPSL/IPSL-CM5A-LR/historicalMisc/r1i1p3/Ayr/${var_dir}/gn/v20111119/${var}-region-sum-anomaly_Ayr_IPSL-CM5A-LR_historicalMisc_r1i1p3_gn_185001-201212-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NCC/NorESM1-M/historicalMisc/r1i1p1/Ayr/${var_dir}/gn/v20110918/${var}-region-sum-anomaly_Ayr_NorESM1-M_historicalMisc_r1i1p1_gn_185001-201212-cumsum.nc ${var_long} cumulative_anomaly /g/data/r87/dbi599/figures/water-cycle/${var}-region-sum-anomaly_Ayr_ensemble-${stat}-heatmap_hist-aer_r1_gn_1861-2005-cumsum.png --time_bounds 1861-01-01 2005-12-31 --scale_factor 17 --ensemble_stat ${stat} --experiment AA-only --vmax 4.5"

#echo ${aa_command}
#${aa_command}


ghg_command="${python} ${script} /g/data/r87/dbi599/CMIP6/DAMIP/CSIRO/ACCESS-ESM1-5/hist-GHG/r1i1p1f1/Ayr/${var_dir}/gn/v20200615/${var}-region-sum-anomaly_Ayr_ACCESS-ESM1-5_hist-GHG_r1i1p1f1_gn_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/BCC/BCC-CSM2-MR/hist-GHG/r1i1p1f1/Ayr/${var_dir}/gn/v20190426/${var}-region-sum-anomaly_Ayr_BCC-CSM2-MR_hist-GHG_r1i1p1f1_gn_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/CCCma/CanESM5/hist-GHG/r10i1p1f1/Ayr/${var_dir}/gn/v20190429/${var}-region-sum-anomaly_Ayr_CanESM5_hist-GHG_r10i1p1f1_gn_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/NCAR/CESM2/hist-GHG/r1i1p1f1/Ayr/${var_dir}/gn/v20190730/${var}-region-sum-anomaly_Ayr_CESM2_hist-GHG_r1i1p1f1_gn_185001-201506-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/NOAA-GFDL/GFDL-ESM4/hist-GHG/r1i1p1f1/Ayr/${var_dir}/gr1/v20180701/${var}-region-sum-anomaly_Ayr_GFDL-ESM4_hist-GHG_r1i1p1f1_gr1_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/IPSL/IPSL-CM6A-LR/hist-GHG/r1i1p1f1/Ayr/${var_dir}/gr/v20180914/${var}-region-sum-anomaly_Ayr_IPSL-CM6A-LR_hist-GHG_r1i1p1f1_gr_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP6/DAMIP/MIROC/MIROC6/hist-GHG/r1i1p1f1/Ayr/${var_dir}/gn/v20190705/${var}-region-sum-anomaly_Ayr_MIROC6_hist-GHG_r1i1p1f1_gn_185001-202012-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NCAR/CCSM4/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20120604/${var}-region-sum-anomaly_Ayr_CCSM4_historicalGHG_r1i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/CSIRO-QCCCE/CSIRO-Mk3-6-0/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20110518/${var}-region-sum-anomaly_Ayr_CSIRO-Mk3-6-0_historicalGHG_r1i1p1_gn_185001-201212-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/CCCma/CanESM2/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20111027/${var}-region-sum-anomaly_Ayr_CanESM2_historicalGHG_r1i1p1_gn_185001-201212-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/LASG-CESS/FGOALS-g2/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20161204/${var}-region-sum-anomaly_Ayr_FGOALS-g2_historicalGHG_r1i1p1_gn_185001-200912-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NOAA-GFDL/GFDL-CM3/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20120227/${var}-region-sum-anomaly_Ayr_GFDL-CM3_historicalGHG_r1i1p1_gn_186001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NOAA-GFDL/GFDL-ESM2M/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20130214/${var}-region-sum-anomaly_Ayr_GFDL-ESM2M_historicalGHG_r1i1p1_gn_185001-200512-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NASA-GISS/GISS-E2-H/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20160426/${var}-region-sum-anomaly_Ayr_GISS-E2-H_historicalGHG_r1i1p1_gn_185001-201212-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/IPSL/IPSL-CM5A-LR/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20120526/${var}-region-sum-anomaly_Ayr_IPSL-CM5A-LR_historicalGHG_r1i1p1_gn_185001-201212-cumsum.nc /g/data/r87/dbi599/CMIP5/DAMIP/NCC/NorESM1-M/historicalGHG/r1i1p1/Ayr/${var_dir}/gn/v20110918/${var}-region-sum-anomaly_Ayr_NorESM1-M_historicalGHG_r1i1p1_gn_185001-201212-cumsum.nc ${var_long} cumulative_anomaly /g/data/r87/dbi599/figures/water-cycle/${var}-region-sum-anomaly_Ayr_ensemble-${stat}-heatmap_hist-GHG_r1_gn_1861-2005-cumsum.png --time_bounds 1861-01-01 2005-12-31 --scale_factor 17 --ensemble_stat ${stat} --experiment GHG-only --vmax 4.5"

#echo ${ghg_command}
#${ghg_command}

done

for unit in "${units[@]}"; do

end='clim'
if [[ "${unit}" == "--pct" ]] ; then
    end='clim-pct'
fi

clim_command="${python} ${script} /g/data/r87/dbi599/CMIP6/CMIP/BCC/BCC-CSM2-MR/piControl/r1i1p1f1/Ayr/${var_dir}/gn/v20181016/${var}-region-sum_Ayr_BCC-CSM2-MR_piControl_r1i1p1f1_gn_185001-244912.nc /g/data/r87/dbi599/CMIP6/CMIP/CSIRO/ACCESS-ESM1-5/piControl/r1i1p1f1/Ayr/${var_dir}/gn/v20191214/${var}-region-sum_Ayr_ACCESS-ESM1-5_piControl_r1i1p1f1_gn_010101-100012.nc ${var_long} climatology /g/data/r87/dbi599/figures/water-cycle/${var}-region-sum_Ayr_ensemble-mean-heatmap_piControl_r1_gn_${end}.png --experiment piControl ${unit}"

echo ${clim_command}
${clim_command}

done
done



#/g/data/r87/dbi599/CMIP5/CMIP/CCCma/CanESM2/piControl/r1i1p1/Ayr/pe/gn/v20120623/pe-region-sum_Ayr_CanESM2_piControl_r1i1p1_gn_201501-301012-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/CSIRO-QCCCE/CSIRO-Mk3-6-0/piControl/r1i1p1/Ayr/pe/gn/v20110518/pe-region-sum_Ayr_CSIRO-Mk3-6-0_piControl_r1i1p1_gn_000101-050012-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/IPSL/IPSL-CM5A-LR/piControl/r1i1p1/Ayr/pe/gn/v20130506/pe-region-sum_Ayr_IPSL-CM5A-LR_piControl_r1i1p1_gn_180001-279912-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/LASG-CESS/FGOALS-g2/piControl/r1i1p1/Ayr/pe/gn/v20161204/pe-region-sum_Ayr_FGOALS-g2_piControl_r1i1p1_gn_020101-090012-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/NASA-GISS/GISS-E2-H/piControl/r1i1p1/Ayr/pe/gn/v20160511/pe-region-sum_Ayr_GISS-E2-H_piControl_r1i1p1_gn_241001-294912-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/NASA-GISS/GISS-E2-R/piControl/r1i1p1/Ayr/pe/gn/v20161004/pe-region-sum_Ayr_GISS-E2-R_piControl_r1i1p1_gn_398101-453012-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/NCAR/CCSM4/piControl/r1i1p1/Ayr/pe/gn/v20160829/pe-region-sum_Ayr_CCSM4_piControl_r1i1p1_gn_025001-130012-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/NCC/NorESM1-M/piControl/r1i1p1/Ayr/pe/gn/v20110901/pe-region-sum_Ayr_NorESM1-M_piControl_r1i1p1_gn_070001-120012-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/NOAA-GFDL/GFDL-CM3/piControl/r1i1p1/Ayr/pe/gn/v20120227/pe-region-sum_Ayr_GFDL-CM3_piControl_r1i1p1_gn_000101-050012-cumsum.nc
#/g/data/r87/dbi599/CMIP5/CMIP/NOAA-GFDL/GFDL-ESM2M/piControl/r1i1p1/Ayr/pe/gn/v20130214/pe-region-sum_Ayr_GFDL-ESM2M_piControl_r1i1p1_gn_000101-050012-cumsum.nc
#/g/data/r87/dbi599/CMIP6/CMIP/CAS/FGOALS-g3/piControl/r1i1p1f1/Ayr/pe/gn/v20190818/pe-region-sum_Ayr_FGOALS-g3_piControl_r1i1p1f1_gn_060001-116012-cumsum.nc
#/g/data/r87/dbi599/CMIP6/CMIP/CCCma/CanESM5/piControl/r1i1p1f1/Ayr/pe/gn/v20190429/pe-region-sum_Ayr_CanESM5_piControl_r1i1p1f1_gn_520101-620012-cumsum.nc
#/g/data/r87/dbi599/CMIP6/CMIP/CSIRO/ACCESS-ESM1-5/piControl/r1i1p1f1/Ayr/pe/gn/v20191214/pe-region-sum_Ayr_ACCESS-ESM1-5_piControl_r1i1p1f1_gn_010101-100012-cumsum.nc
#/g/data/r87/dbi599/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/piControl/r1i1p1f1/Ayr/pe/gr/v20200326/pe-region-sum_Ayr_IPSL-CM6A-LR_piControl_r1i1p1f1_gr_185001-384912-cumsum.nc
#/g/data/r87/dbi599/CMIP6/CMIP/MIROC/MIROC6/piControl/r1i1p1f1/Ayr/pe/gn/v20181212/pe-region-sum_Ayr_MIROC6_piControl_r1i1p1f1_gn_320001-399912-cumsum.nc
#/g/data/r87/dbi599/CMIP6/CMIP/NCAR/CESM2/piControl/r1i1p1f1/Ayr/pe/gn/v20190320/pe-region-sum_Ayr_CESM2_piControl_r1i1p1f1_gn_000101-120012-cumsum.nc
#/g/data/r87/dbi599/CMIP6/CMIP/NOAA-GFDL/GFDL-ESM4/piControl/r1i1p1f1/Ayr/pe/gr1/v20180701/pe-region-sum_Ayr_GFDL-ESM4_piControl_r1i1p1f1_gr1_000101-050012-cumsum.nc

#ls /g/data/r87/dbi599/figures/water-cycle/*-region-sum-anomaly_Ayr_ensemble-*-heatmap_*_r1_gn_1861-2005-cumsum.png

