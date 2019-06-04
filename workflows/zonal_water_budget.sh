def calc_anomaly(cube):
    """Calculate the anomaly."""
    
    anomaly = cube.copy()
    anomaly.data = anomaly.data - anomaly.data[0]
    anomaly = anomaly[-1, ::]
    anomaly.remove_coord('time')
    
    return anomaly



cube = iris.load_cube(infile, var & time_constraint)

anomaly = calc_anomaly(cube)

ocean_convergence = ohc_anomaly - hfds_anomaly
hfbasin_inferred = ocean_convergence.copy()
hfbasin_inferred.data = numpy.ma.cumsum(-1 * ocean_convergence.data)


iplt.plot(rndt_anomaly, color='red', label=labels[0],
linestyle=linestyle, linewidth=linewidth)


plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
ax.yaxis.major.formatter._useMathText = True


## wfo

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/data_processing/remove_drift.py /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historical/yr/ocean/r1i1p1/wfo/latest/wfo-zonal-sum_Oyr_NorESM1-M_historical_r1i1p1_cumsum-all.nc water_flux_into_sea_water annual /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-zonal-sum-coefficients_Oyr_NorESM1-M_piControl_r1i1p1_cumsum-all.nc /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historical/yr/ocean/r1i1p1/wfo/latest/dedrifted/wfo-zonal-sum_Oyr_NorESM1-M_historical_r1i1p1_cumsum-all.nc --no_data_check

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/data_processing/calc_drift_coefficients.py /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-zonal-sum_Oyr_NorESM1-M_piControl_r1i1p1_cumsum-all.nc  water_flux_into_sea_water /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-zonal-sum-coefficients_Oyr_NorESM1-M_piControl_r1i1p1_cumsum-all.nc

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/data_processing/calc_zonal_aggregate.py /g/data/ua6/DRSv3/CMIP5/NorESM1-M/historical/mon/ocean/r1i1p1/wfo/latest/wfo_Omon_NorESM1-M_historical_r1i1p1_??????-??????.nc water_flux_into_sea_water sum /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historical/yr/ocean/r1i1p1/wfo/latest/wfo-zonal-sum_Oyr_NorESM1-M_historical_r1i1p1_cumsum-all.nc --annual --ref_file /g/data/ua6/DRSv2/CMIP5/NorESM1-M/historical/mon/atmos/r1i1p1/rsdt/latest/rsdt_Amon_NorESM1-M_historical_r1i1p1_185001-200512.nc --cumsum --area /g/data/ua6/DRSv3/CMIP5/NorESM1-M/historical/fx/ocean/r0i0p0/areacello/latest/areacello_fx_NorESM1-M_historical_r0i0p0.nc --flux_to_mag

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/data_processing/calc_zonal_aggregate.py /g/data/ua6/DRSv3/CMIP5/NorESM1-M/piControl/mon/ocean/r1i1p1/wfo/latest/wfo_Omon_NorESM1-M_piControl_r1i1p1_??????-??????.nc water_flux_into_sea_water sum /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/wfo/latest/wfo-zonal-sum_Oyr_NorESM1-M_piControl_r1i1p1_cumsum-all.nc --annual --ref_file /g/data/ua6/DRSv2/CMIP5/NorESM1-M/historical/mon/atmos/r1i1p1/rsdt/latest/rsdt_Amon_NorESM1-M_historical_r1i1p1_185001-200512.nc toa_incoming_shortwave_flux --cumsum --area /g/data/ua6/DRSv3/CMIP5/NorESM1-M/historical/fx/ocean/r0i0p0/areacello/latest/areacello_fx_NorESM1-M_historical_r0i0p0.nc --flux_to_mag


## so

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/data_processing/remove_drift.py /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historical/yr/ocean/r1i1p1/so/latest/so-vertical-zonal-mean_Oyr_NorESM1-M_historical_r1i1p1_all.nc sea_water_salinity annual  /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/so/latest/so-vertical-zonal-mean-coefficients_Oyr_NorESM1-M_piControl_r1i1p1_all.nc 
/g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historical/yr/ocean/r1i1p1/so/latest/dedrifted/so-vertical-zonal-mean_Oyr_NorESM1-M_historical_r1i1p1_all.nc --no_data_check

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/data_processing/calc_drift_coefficients.py /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/so/latest/so-vertical-zonal-mean_Oyr_NorESM1-M_piControl_r1i1p1_all.nc sea_water_salinity /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/so/latest/so-vertical-zonal-mean-coefficients_Oyr_NorESM1-M_piControl_r1i1p1_all.nc 

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/data_processing/calc_zonal_aggregate.py /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historical/yr/ocean/r1i1p1/so/latest/so-vertical-mean_Oyr_NorESM1-M_historical_r1i1p1_??????-??????.nc sea_water_salinity mean /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/historical/yr/ocean/r1i1p1/so/latest/so-vertical-zonal-mean_Oyr_NorESM1-M_historical_r1i1p1_all.nc --ref_file /g/data/ua6/DRSv3/CMIP5/NorESM1-M/historical/mon/atmos/r1i1p1/rsdt/latest/rsdt_Amon_NorESM1-M_historical_r1i1p1_185001-200512.nc toa_incoming_shortwave_flux

/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python /home/599/dbi599/ocean-analysis/data_processing/calc_zonal_aggregate.py /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/so/latest/so-vertical-mean_Oyr_NorESM1-M_piControl_r1i1p1_??????-??????.nc sea_water_salinity mean /g/data/r87/dbi599/DRSv2/CMIP5/NorESM1-M/piControl/yr/ocean/r1i1p1/so/latest/so-vertical-zonal-mean_Oyr_NorESM1-M_piControl_r1i1p1_all.nc --ref_file /g/data/ua6/DRSv3/CMIP5/NorESM1-M/historical/mon/atmos/r1i1p1/rsdt/latest/rsdt_Amon_NorESM1-M_historical_r1i1p1_185001-200512.nc toa_incoming_shortwave_flux

bash /home/599/dbi599/ocean-analysis/data_processing/calc_vertical_aggregate.sh /g/data/ua6/DRSv3/CMIP5/NorESM1-M/historical/mon/ocean/r1i1p1/so/latest/so_Omon_NorESM1-M_historical_r1i1p1_??????-??????.nc

bash /home/599/dbi599/ocean-analysis/data_processing/calc_vertical_aggregate.sh /g/data/ua6/DRSv3/CMIP5/NorESM1-M/piControl/mon/ocean/r1i1p1/so/latest/so_Omon_NorESM1-M_piControl_r1i1p1_??????-??????.nc




