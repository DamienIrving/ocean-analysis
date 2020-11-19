# water_mass_analysis.mk
#
# Description: Ocean water mass analysis
#
# To execute:
#   make all -n -B -f water_mass_analysis.mk  (-n is a dry run) (-B is a force make)
#
#   (Options besides all: volcello-tbin so-volcello-tbin thetao-volcello-tbin surface sf-anomaly)  

include cmip_config.mk


# File definitions

AREACELLO_FILE=${AREACELLO_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/areacello/${GRID}/${OFX_VERSION}/areacello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
VOLCELLO_FILE=${VOLCELLO_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID}/${OFX_VERSION}/volcello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
SALINITY_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/so/${GRID}/${EXP_VERSION}/so*.nc)) 
TEMPERATURE_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/thetao/${GRID}/${EXP_VERSION}/thetao*.nc))
TEMPERATURE_FILES_HIST := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${HIST_RUN}/Omon/thetao/${GRID}/${HIST_VERSION}/thetao*.nc))
TEMPERATURE_FILE_HIST := $(firstword ${TEMPERATURE_FILES_HIST})
TBIN_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/${TBIN_VAR}/${GRID}/${EXP_VERSION}/${TBIN_VAR}*.nc))
SBIN_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/${SBIN_VAR}/${GRID}/${EXP_VERSION}/${SBIN_VAR}*.nc))
SF_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/${SF_VAR}/${GRID}/${EXP_VERSION}/${SF_VAR}*.nc))
SALINITY_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/so/${GRID}/${CNTRL_VERSION}/so*.nc)) 
TEMPERATURE_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/thetao/${GRID}/${CNTRL_VERSION}/thetao*.nc))
TBIN_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/${TBIN_VAR}/${GRID}/${CNTRL_VERSION}/${TBIN_VAR}*.nc))
SBIN_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/${SBIN_VAR}/${GRID}/${CNTRL_VERSION}/${SBIN_VAR}*.nc))
SF_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/${SF_VAR}/${GRID}/${CNTRL_VERSION}/${SF_VAR}*.nc))


# basin file

BASIN_DIR=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${HIST_RUN}/Ofx/basin/${GRID}/${HIST_VERSION}
BASIN_FILE=${BASIN_DIR}/basin_Ofx_${MODEL}_historical_${HIST_RUN}_${GRID}.nc
${BASIN_FILE} : ${TEMPERATURE_FILE_HIST}
	mkdir -p ${BASIN_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin.py $< sea_water_potential_temperature $@


# surface_flux(year, tos, so, basin)

SF_BINNED_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/${SF_VAR}/${GRID}/${EXP_VERSION}
SF_BINNED_FILE_EXP=${SF_BINNED_DIR_EXP}/${SF_VAR}-${TBIN_VAR}-${SBIN_VAR}-binned_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${SF_BINNED_FILE_EXP} : ${BASIN_FILE} ${AREACELLO_FILE}
	mkdir -p ${SF_BINNED_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/water_mass_binning.py ${SF_FILES_EXP} ${SF_STD_NAME} $< $@ --temperature_files ${TBIN_FILES_EXP} --temperature_var ${TBIN_STD_NAME} --salinity_files ${SBIN_FILES_EXP} --salinity_var ${SBIN_STD_NAME} --area_file $(word 2,$^)

SF_BINNED_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/${SF_VAR}/${GRID}/${CNTRL_VERSION}
SF_BINNED_FILE_CNTRL=${SF_BINNED_DIR_CNTRL}/${SF_VAR}-${TBIN_VAR}-${SBIN_VAR}-binned_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${SF_BINNED_FILE_CNTRL} : ${BASIN_FILE} ${AREACELLO_FILE} 
	mkdir -p ${SF_BINNED_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/water_mass_binning.py ${SF_FILES_CNTRL} ${SF_STD_NAME} $< $@ --temperature_files ${TBIN_FILES_CNTRL} --temperature_var ${TBIN_STD_NAME} --salinity_files ${SBIN_FILES_CNTRL} --salinity_var ${SBIN_STD_NAME} --area_file $(word 2,$^)

## cumulative sum

SF_TBINNED_CUMSUM_FILE_EXP=${SF_BINNED_DIR_EXP}/${SF_VAR}-${TBIN_VAR}-binned_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}-cumsum.nc
${SF_TBINNED_CUMSUM_FILE_EXP} : ${SF_BINNED_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${SF_LONG_NAME}_binned_by_temperature $@ --flux_to_mag

SF_SBINNED_CUMSUM_FILE_EXP=${SF_BINNED_DIR_EXP}/${SF_VAR}-${SBIN_VAR}-binned_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}-cumsum.nc
${SF_SBINNED_CUMSUM_FILE_EXP} : ${SF_BINNED_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${SF_LONG_NAME}_binned_by_salinity $@ --flux_to_mag

SF_TSBINNED_CUMSUM_FILE_EXP=${SF_BINNED_DIR_EXP}/${SF_VAR}-${TBIN_VAR}-${SBIN_VAR}-binned_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}-cumsum.nc
${SF_TSBINNED_CUMSUM_FILE_EXP} : ${SF_BINNED_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${SF_LONG_NAME}_binned_by_temperature_and_salinity $@ --flux_to_mag

SF_TBINNED_CUMSUM_FILE_CNTRL=${SF_BINNED_DIR_CNTRL}/${SF_VAR}-${TBIN_VAR}-binned_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${SF_TBINNED_CUMSUM_FILE_CNTRL} : ${SF_BINNED_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${SF_LONG_NAME}_binned_by_temperature $@ --flux_to_mag

SF_SBINNED_CUMSUM_FILE_CNTRL=${SF_BINNED_DIR_CNTRL}/${SF_VAR}-${SBIN_VAR}-binned_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${SF_SBINNED_CUMSUM_FILE_CNTRL} : ${SF_BINNED_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${SF_LONG_NAME}_binned_by_salinity $@ --flux_to_mag

SF_TSBINNED_CUMSUM_FILE_CNTRL=${SF_BINNED_DIR_CNTRL}/${SF_VAR}-${TBIN_VAR}-${SBIN_VAR}-binned_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${SF_TSBINNED_CUMSUM_FILE_CNTRL} : ${SF_BINNED_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${SF_LONG_NAME}_binned_by_temperature_and_salinity $@ --flux_to_mag

## remove drift / calculate anomaly

SF_TBINNED_CUMSUM_COEFFICIENT_FILE=${SF_BINNED_DIR_CNTRL}/${SF_VAR}-${TBIN_VAR}-binned-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${SF_TBINNED_CUMSUM_COEFFICIENT_FILE} : ${SF_TBINNED_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${SF_LONG_NAME}_binned_by_temperature $@ --no_data_check

SF_SBINNED_CUMSUM_COEFFICIENT_FILE=${SF_BINNED_DIR_CNTRL}/${SF_VAR}-${SBIN_VAR}-binned-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${SF_SBINNED_CUMSUM_COEFFICIENT_FILE} : ${SF_SBINNED_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${SF_LONG_NAME}_binned_by_salinity $@ --no_data_check

SF_TSBINNED_CUMSUM_COEFFICIENT_FILE=${SF_BINNED_DIR_CNTRL}/${SF_VAR}-${TBIN_VAR}-${SBIN_VAR}-binned-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${SF_TSBINNED_CUMSUM_COEFFICIENT_FILE} : ${SF_TSBINNED_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${SF_LONG_NAME}_binned_by_temperature_and_salinity $@ --no_data_check

SF_ANOMALY_TBINNED_CUMSUM_FILE=${SF_BINNED_DIR_EXP}/${SF_VAR}-anomaly-${TBIN_VAR}-binned_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}-cumsum.nc
${SF_ANOMALY_TBINNED_CUMSUM_FILE} : ${SF_TBINNED_CUMSUM_FILE_EXP} ${SF_TBINNED_CUMSUM_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< ${SF_LONG_NAME}_binned_by_temperature $(word 2,$^) $@ ${BRANCH_YEAR}

SF_ANOMALY_SBINNED_CUMSUM_FILE=${SF_BINNED_DIR_EXP}/${SF_VAR}-anomaly-${SBIN_VAR}-binned_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}-cumsum.nc
${SF_ANOMALY_SBINNED_CUMSUM_FILE} : ${SF_SBINNED_CUMSUM_FILE_EXP} ${SF_SBINNED_CUMSUM_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< ${SF_LONG_NAME}_binned_by_salinity $(word 2,$^) $@ ${BRANCH_YEAR}

SF_ANOMALY_TSBINNED_CUMSUM_FILE=${SF_BINNED_DIR_EXP}/${SF_VAR}-anomaly-${TBIN_VAR}-${SBIN_VAR}-binned_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}-cumsum.nc
${SF_ANOMALY_TSBINNED_CUMSUM_FILE} : ${SF_TSBINNED_CUMSUM_FILE_EXP} ${SF_TSBINNED_CUMSUM_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< ${SF_LONG_NAME}_binned_by_temperature_and_salinity $(word 2,$^) $@ ${BRANCH_YEAR}

## plot

SF_ANOMALY_TBINNED_CUMSUM_PLOT=/g/data/r87/dbi599/temp/${SF_VAR}-anomaly-${TBIN_VAR}-binned_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}-cumsum_bin34.png
${SF_ANOMALY_TBINNED_CUMSUM_PLOT} : ${SF_TBINNED_CUMSUM_FILE_CNTRL} ${SF_TBINNED_CUMSUM_FILE_EXP} ${SF_ANOMALY_TBINNED_CUMSUM_FILE} ${SF_TBINNED_CUMSUM_COEFFICIENT_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py ${SF_LONG_NAME}_binned_by_temperature $@ --control_files $< --experiment_files $(word 2,$^) --dedrifted_files $(word 3,$^) --coefficient_file $(word 4,$^) --grid_point 34 -1 ${BRANCH_YEAR}

sf-anomaly : ${SF_ANOMALY_TBINNED_CUMSUM_PLOT} ${SF_ANOMALY_SBINNED_CUMSUM_FILE} ${SF_ANOMALY_TSBINNED_CUMSUM_FILE}

# water mass files

WATER_MASS_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/water-mass/${GRID}/${EXP_VERSION}
WATER_MASS_FILE_EXP=${WATER_MASS_DIR_EXP}/water-mass_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${WATER_MASS_FILE_EXP} : ${VOLCELLO_FILE} ${BASIN_FILE}
	mkdir -p ${WATER_MASS_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/water_mass_binning.py $< ocean_volume $(word 2,$^) $@ --salinity_files ${SALINITY_FILES_EXP} --salinity_var sea_water_salinity --temperature_files ${TEMPERATURE_FILES_EXP} --temperature_var sea_water_potential_temperature

WATER_MASS_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/water-mass/${GRID}/${CNTRL_VERSION}
WATER_MASS_FILE_CNTRL=${WATER_MASS_DIR_CNTRL}/water-mass_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${WATER_MASS_FILE_CNTRL} : ${VOLCELLO_FILE} ${BASIN_FILE}
	mkdir -p ${WATER_MASS_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/water_mass_binning.py $< ocean_volume $(word 2,$^) $@ --salinity_files ${SALINITY_FILES_CNTRL} --salinity_var sea_water_salinity --temperature_files ${TEMPERATURE_FILES_CNTRL} --temperature_var sea_water_potential_temperature

## drift removal for volcello_tbin(year, thetao, basin)

VOL_TBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/volcello-tbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${VOL_TBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Ocean_Grid-Cell_Volume_binned_by_temperature $@

VOL_TBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/volcello-tbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${VOL_TBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${VOL_TBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Ocean_Grid-Cell_Volume_binned_by_temperature $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for volcello_sbin(year, so, basin)

VOL_SBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/volcello-sbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${VOL_SBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON}  ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Ocean_Grid-Cell_Volume_binned_by_salinity $@

VOL_SBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/volcello-sbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${VOL_SBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${VOL_SBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Ocean_Grid-Cell_Volume_binned_by_salinity $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for volcello_tsbin(year, thetao, so, basin)

VOL_TSBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/volcello-tsbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${VOL_TSBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Ocean_Grid-Cell_Volume_binned_by_temperature_and_salinity $@

VOL_TSBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/volcello-tsbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${VOL_TSBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${VOL_TSBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Ocean_Grid-Cell_Volume_binned_by_temperature_and_salinity $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for so_volcello_tbin(year, thetao, basin)

SOVOL_TBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/so-volcello-tbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${SOVOL_TBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature $@ --no_data_check

SOVOL_TBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/so-volcello-tbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${SOVOL_TBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${SOVOL_TBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for so_volcello_sbin(year, so, basin)

SOVOL_SBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/so-volcello-sbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${SOVOL_SBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_salinity $@ --no_data_check

SOVOL_SBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/so-volcello-sbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${SOVOL_SBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${SOVOL_SBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_salinity $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for so_volcello_tsbin(year, thetao, so, basin)

SOVOL_TSBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/so-volcello-tsbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${SOVOL_TSBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature_and_salinity $@ --no_data_check

SOVOL_TSBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/so-volcello-tsbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${SOVOL_TSBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${SOVOL_TSBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Sea_Water_Salinity_times_Ocean_Grid-Cell_Volume_binned_by_temperature_and_salinity $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for thetao_volcello_tbin(year, thetao, basin)

TVOL_TBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/thetao-volcello-tbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${TVOL_TBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_temperature $@ --no_data_check

TVOL_TBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/thetao-volcello-tbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${TVOL_TBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${TVOL_TBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_temperature $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for thetao_volcello_sbin(year, so, basin)

TVOL_SBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/thetao-volcello-sbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${TVOL_SBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_salinity $@ --no_data_check

TVOL_SBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/thetao-volcello-sbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${TVOL_SBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${TVOL_SBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_salinity $(word 2,$^) $@ ${BRANCH_YEAR}

## drift removal for thetao_volcello_tsbin(year, thetao, so, basin)

TVOL_TSBIN_DRIFT_COEFFICIENT_FILE=${WATER_MASS_DIR_CNTRL}/thetao-volcello-tsbin-coefficients_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${TVOL_TSBIN_DRIFT_COEFFICIENT_FILE} : ${WATER_MASS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_temperature_and_salinity $@ --no_data_check

TVOL_TSBIN_DEDRIFTED_FILE=${WATER_MASS_DIR_EXP}/thetao-volcello-tsbin-dedrifted_Omon_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID}_${EXP_TIME}.nc
${TVOL_TSBIN_DEDRIFTED_FILE} : ${WATER_MASS_FILE_EXP} ${TVOL_TSBIN_DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift_year_axis.py $< Sea_Water_Potential_Temperature_times_Ocean_Grid-Cell_Volume_binned_by_temperature_and_salinity $(word 2,$^) $@ ${BRANCH_YEAR}

## plots

VOL_TBIN_PLOT_FILE=/g/data/r87/dbi599/temp/volcello-tbin-dedrifted_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}_bin6.png
${VOL_TBIN_PLOT_FILE} : ${VOL_TBIN_DRIFT_COEFFICIENT_FILE} ${WATER_MASS_FILE_CNTRL} ${WATER_MASS_FILE_EXP} ${VOL_TBIN_DEDRIFTED_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py Ocean_Grid-Cell_Volume_binned_by_temperature $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 6 -1 ${BRANCH_YEAR}

VOL_SBIN_PLOT_FILE=/g/data/r87/dbi599/temp/volcello-sbin-dedrifted_Omon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}_bin6.png
${VOL_SBIN_PLOT_FILE} : ${VOL_SBIN_DRIFT_COEFFICIENT_FILE} ${WATER_MASS_FILE_CNTRL} ${WATER_MASS_FILE_EXP} ${VOL_SBIN_DEDRIFTED_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py Ocean_Grid-Cell_Volume_binned_by_salinity $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 6 -1 ${BRANCH_YEAR}

volcello-tbin : ${VOL_TBIN_PLOT_FILE}
volcello-sbin : ${VOL_SBIN_PLOT_FILE}
volcello-tsbin : ${VOL_TSBIN_DEDRIFTED_FILE}
so-volcello-tbin : ${SOVOL_TBIN_DEDRIFTED_FILE}
so-volcello-sbin : ${SOVOL_SBIN_DEDRIFTED_FILE}
so-volcello-tsbin : ${SOVOL_TSBIN_DEDRIFTED_FILE}
thetao-volcello-tbin : ${SOVOL_TBIN_DEDRIFTED_FILE}
thetao-volcello-sbin : ${SOVOL_SBIN_DEDRIFTED_FILE}
thetao-volcello-tsbin : ${SOVOL_TSBIN_DEDRIFTED_FILE}

# targets

all : sf-anomaly volcello-tbin volcello-sbin volcello-tsbin so-volcello-tbin so-volcello-sbin so-volcello-tsbin thetao-volcello-tbin thetao-volcello-sbin thetao-volcello-tsbin
	echo ${SF_ANOMALY_BINNED_CUMSUM_PLOT}
	echo ${VOL_TBIN_PLOT_FILE}
	echo ${VOL_SBIN_PLOT_FILE}
	echo ${VOL_TSBIN_DEDRIFTED_FILE}
	echo ${SOVOL_TBIN_DEDRIFTED_FILE}
	echo ${SOVOL_SBIN_DEDRIFTED_FILE}
	echo ${SOVOL_TSBIN_DEDRIFTED_FILE}
	echo ${SOVOL_TBIN_DEDRIFTED_FILE}
	echo ${SOVOL_SBIN_DEDRIFTED_FILE}
	echo ${SOVOL_TSBIN_DEDRIFTED_FILE}


	

