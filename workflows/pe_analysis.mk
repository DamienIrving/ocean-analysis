# water_cycle_analysis.mk
#
# Description: Water cycle analysis
#
# To execute:
#   make all -n -B -f pe_analysis.mk  (-n is a dry run) (-B is a force make)
#

.PHONY : all pe-zrs pe-spatial pe-regions

include cmip_config.mk

# File definitions, CMIP6 models
 
PR_FILES_HIST := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Amon/pr/${GRID}/${ATMOS_HIST_VERSION}/pr*.nc))
EVAP_FILES_HIST := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Amon/evspsbl/${GRID}/${ATMOS_HIST_VERSION}/evspsbl*.nc))
WFO_FILES_HIST := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Omon/wfo/${GRID}/${HIST_VERSION}/wfo*.nc))
FLUX_FILES_HIST := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Amon/${FLUX_VAR}/${GRID}/${ATMOS_HIST_VERSION}/${FLUX_VAR}*.nc))
PR_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/pr/${GRID}/${ATMOS_CNTRL_VERSION}/pr*.nc))
EVAP_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/evspsbl/${GRID}/${ATMOS_CNTRL_VERSION}/evspsbl*.nc))
WFO_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/wfo/${GRID}/${CNTRL_VERSION}/wfo*.nc))
FLUX_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/${FLUX_VAR}/${GRID}/${ATMOS_CNTRL_VERSION}/${FLUX_VAR}*.nc))
AREACELLA_FILE=${AREACELLA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/fx/areacella/${GRID}/${FX_VERSION}/areacella_fx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
AREACELLO_FILE=${AREACELLO_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/areacello/${GRID}/${FX_VERSION}/areacello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
SFTLF_FILE=${AREACELLA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/fx/sftlf/${GRID}/${FX_VERSION}/sftlf_fx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
EVAP_VAR=water_evapotranspiration_flux

# File definitions, CMIP5 models

#PR_FILES_HIST := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/pr/pr*.nc))
#EVAP_FILES_HIST := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/evspsbl/evspsbl*.nc))
#PR_FILES_CNTRL := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/piControl/mon/atmos/Amon/${CNTRL_RUN}/${ATMOS_CNTRL_VERSION}/pr/pr*.nc))
#EVAP_FILES_CNTRL := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/piControl/mon/atmos/Amon/${CNTRL_RUN}/${ATMOS_CNTRL_VERSION}/evspsbl/evspsbl*.nc))

#EVAP_VAR=water_evaporation_flux

PR_FILE_HIST := $(firstword ${PR_FILES_HIST})
WFO_FILE_HIST := $(firstword ${WFO_FILES_HIST})

# Directories

PE_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/pe/${GRID}/${ATMOS_HIST_VERSION}
PE_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/pe/${GRID}/${ATMOS_CNTRL_VERSION}

WFO_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Oyr/wfo/${GRID}/${HIST_VERSION}
WFO_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Oyr/wfo/${GRID}/${CNTRL_VERSION}

PR_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/pr/${GRID}/${ATMOS_HIST_VERSION}
PR_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/pr/${GRID}/${ATMOS_CNTRL_VERSION}

EVAP_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/evspsbl/${GRID}/${ATMOS_HIST_VERSION}
EVAP_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/evspsbl/${GRID}/${ATMOS_CNTRL_VERSION}

FLUX_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/${FLUX_VAR}/${GRID}/${ATMOS_HIST_VERSION}
FLUX_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/${FLUX_VAR}/${GRID}/${ATMOS_CNTRL_VERSION}

AREA_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/areacella/${GRID}/${ATMOS_HIST_VERSION}
AREA_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/areacella/${GRID}/${ATMOS_CNTRL_VERSION}

# basin file

FX_BASIN_DIR=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${FX_RUN}/fx/basin/${GRID}/${HIST_VERSION}
FX_BASIN_FILE=${FX_BASIN_DIR}/basin_fx_${MODEL}_historical_${FX_RUN}_${GRID}.nc
${FX_BASIN_FILE} : ${PR_FILE_HIST} ${SFTLF_FILE}
	mkdir -p ${FX_BASIN_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin.py $< precipitation_flux $@ --sftlf_file $(word 2,$^) --land_threshold 50

BASIN_DIR=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${FX_RUN}/Ofx/basin/${GRID}/${HIST_VERSION}
BASIN_FILE=${BASIN_DIR}/basin_Ofx_${MODEL}_historical_${FX_RUN}_${GRID}.nc
${BASIN_FILE} : ${WFO_FILE_HIST}
	mkdir -p ${BASIN_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin.py $< water_flux_into_sea_water $@

# P-E

PE_MON_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Amon/pe/${GRID}/${ATMOS_HIST_VERSION}
PE_FILE_HIST=${PE_MON_DIR_HIST}/pe_Amon_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${PE_FILE_HIST} :
	mkdir -p ${PE_MON_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py $@ --pr_files ${PR_FILES_HIST} --evap_files ${EVAP_FILES_HIST}

PE_MON_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/pe/${GRID}/${ATMOS_CNTRL_VERSION}
PE_FILE_CNTRL=${PE_MON_DIR_CNTRL}/pe_Amon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${PE_FILE_CNTRL} :
	mkdir -p ${PE_MON_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py $@ --pr_files ${PR_FILES_CNTRL} --evap_files ${EVAP_FILES_CNTRL}

# P-E regions analysis

## raw timeseries

PE_REGIONS_FILE_CNTRL_TSERIES=${PE_YR_DIR_CNTRL}/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${PE_REGIONS_FILE_CNTRL_TSERIES}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${PE_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --annual

WFO_REGIONS_FILE_CNTRL_TSERIES=${WFO_YR_DIR_CNTRL}/wfo-region-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${WFO_REGIONS_FILE_CNTRL_TSERIES}: ${BASIN_FILE}
	mkdir -p ${WFO_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py ${WFO_FILES_CNTRL} $< $@ --annual --area_file ${AREACELLO_FILE}

## regional cumsum

### area (m2)

AREA_PE_REGIONS_FILE_HIST=${AREA_YR_DIR_HIST}/areacella-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${AREA_PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${FX_BASIN_FILE}
	mkdir -p ${AREA_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${AREACELLA_FILE} --data_var cell_area --annual --cumsum

AREA_PE_REGIONS_FILE_CNTRL=${AREA_YR_DIR_CNTRL}/areacella-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${AREA_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${AREA_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${AREACELLA_FILE} --data_var cell_area --annual --cumsum

### P-E (kg)

PE_REGIONS_FILE_HIST=${PE_YR_DIR_HIST}/pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${FX_BASIN_FILE}
	mkdir -p ${PE_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --annual --cumsum

PE_REGIONS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${PE_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --annual --cumsum

## P-E (kg m-2)

PE_PER_M2_REGIONS_FILE_HIST=${PE_YR_DIR_HIST}/pe-per-m2-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_PER_M2_REGIONS_FILE_HIST}: ${PE_REGIONS_FILE_HIST} ${AREA_PE_REGIONS_FILE_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_arithmetic.py $< precipitation_minus_evaporation_flux $(word 2,$^) cell_area division $@

PE_PER_M2_REGIONS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-per-m2-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_PER_M2_REGIONS_FILE_CNTRL}: ${PE_REGIONS_FILE_CNTRL} ${AREA_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_arithmetic.py $< precipitation_minus_evaporation_flux $(word 2,$^) cell_area division $@

### wfo (kg)

WFO_REGIONS_FILE_HIST=${WFO_YR_DIR_HIST}/wfo-region-sum_Oyr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${WFO_REGIONS_FILE_HIST}: ${BASIN_FILE}
	mkdir -p ${WFO_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py ${WFO_FILES_HIST} $< $@ --annual --cumsum --area_file ${AREACELLO_FILE}

WFO_REGIONS_FILE_CNTRL=${WFO_YR_DIR_CNTRL}/wfo-region-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${WFO_REGIONS_FILE_CNTRL}: ${BASIN_FILE}
	mkdir -p ${WFO_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py ${WFO_FILES_CNTRL} $< $@ --annual --cumsum --area_file ${AREACELLO_FILE}

### P (kg)

PR_PE_REGIONS_FILE_HIST=${PR_YR_DIR_HIST}/pr-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PR_PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${FX_BASIN_FILE}
	mkdir -p ${PR_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${PR_FILES_HIST} --data_var precipitation_flux --annual --cumsum

PR_PE_REGIONS_FILE_CNTRL=${PR_YR_DIR_CNTRL}/pr-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PR_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${PR_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${PR_FILES_CNTRL} --data_var precipitation_flux --annual --cumsum

### E (kg)

EVAP_PE_REGIONS_FILE_HIST=${EVAP_YR_DIR_HIST}/evspsbl-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${EVAP_PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${FX_BASIN_FILE}
	mkdir -p ${EVAP_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${EVAP_FILES_HIST} --data_var ${EVAP_VAR} --annual --cumsum

EVAP_PE_REGIONS_FILE_CNTRL=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${EVAP_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${EVAP_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${EVAP_FILES_CNTRL} --data_var ${EVAP_VAR} --annual --cumsum

### Flux (J)

FLUX_PE_REGIONS_FILE_HIST=${FLUX_YR_DIR_HIST}/${FLUX_VAR}-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${FLUX_PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${FX_BASIN_FILE}
	mkdir -p ${FLUX_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${FLUX_FILES_HIST} --data_var ${FLUX_NAME} --annual --cumsum

FLUX_PE_REGIONS_FILE_CNTRL=${FLUX_YR_DIR_CNTRL}/${FLUX_VAR}-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${FLUX_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${FLUX_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${FLUX_FILES_CNTRL} --data_var ${FLUX_NAME} --annual --cumsum

## cumulative anomaly

### P-E (kg)

PE_REGIONS_COEFFICIENTS=${PE_YR_DIR_CNTRL}/pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_REGIONS_COEFFICIENTS} : ${PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_minus_evaporation_flux $@

PE_REGIONS_ANOMALY_CUMSUM=${PE_YR_DIR_HIST}/pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_REGIONS_ANOMALY_CUMSUM} : ${PE_REGIONS_FILE_HIST} ${PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_minus_evaporation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

PE_REGIONS_DRIFT_PLOT=/g/data/r87/dbi599/temp/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${PE_REGIONS_DRIFT_PLOT} : ${PE_REGIONS_COEFFICIENTS} ${PE_REGIONS_FILE_CNTRL} ${PE_REGIONS_FILE_HIST} ${PE_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_minus_evaporation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

PE_REGIONS_HEATMAP=/g/data/r87/dbi599/figures/water-cycle/pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_gn_185001-201412-cumsum.png
${PE_REGIONS_HEATMAP} : ${PE_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/water_cycle/plot_pe_heatmap.py $< precipitation_minus_evaporation_flux cumulative_anomaly $@ --scale_factor 17 --time_bounds 1850-01-01 2014-12-31

PE_REGIONS_HEATMAP_CLIM=/g/data/r87/dbi599/figures/water-cycle/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_gn_${CNTRL_TIME}-clim.png
${PE_REGIONS_HEATMAP_CLIM} : ${PE_REGIONS_FILE_CNTRL_TSERIES}
	${PYTHON} ${VIZ_SCRIPT_DIR}/water_cycle/plot_pe_heatmap.py $< precipitation_minus_evaporation_flux climatology $@ --scale_factor 16

PE_REGIONS_HEATMAP_CLIM_PCT=/g/data/r87/dbi599/figures/water-cycle/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_gn_${CNTRL_TIME}-clim_pct.png
${PE_REGIONS_HEATMAP_CLIM} : ${PE_REGIONS_FILE_CNTRL_TSERIES}
	${PYTHON} ${VIZ_SCRIPT_DIR}/water_cycle/plot_pe_heatmap.py $< precipitation_minus_evaporation_flux climatology $@ --pct

### P-E (kg m-2)

PE_PER_M2_REGIONS_COEFFICIENTS=${PE_YR_DIR_CNTRL}/pe-per-m2-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_PER_M2_REGIONS_COEFFICIENTS} : ${PE_PER_M2_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_minus_evaporation_flux $@

PE_PER_M2_REGIONS_ANOMALY_CUMSUM=${PE_YR_DIR_HIST}/pe-per-m2-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_PER_M2_REGIONS_ANOMALY_CUMSUM} : ${PE_PER_M2_REGIONS_FILE_HIST} ${PE_PER_M2_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_minus_evaporation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

PE_PER_M2_REGIONS_DRIFT_PLOT=/g/data/r87/dbi599/temp/pe-per-m2-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${PE_PER_M2_REGIONS_DRIFT_PLOT} : ${PE_PER_M2_REGIONS_COEFFICIENTS} ${PE_PER_M2_REGIONS_FILE_CNTRL} ${PE_PER_M2_REGIONS_FILE_HIST} ${PE_PER_M2_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_minus_evaporation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### wfo (kg)

WFO_REGIONS_COEFFICIENTS=${WFO_YR_DIR_CNTRL}/wfo-region-sum-coefficients_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${WFO_REGIONS_COEFFICIENTS} : ${WFO_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< water_flux_into_sea_water $@

WFO_REGIONS_ANOMALY_CUMSUM=${WFO_YR_DIR_HIST}/wfo-region-sum-anomaly_Oyr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${WFO_REGIONS_ANOMALY_CUMSUM} : ${WFO_REGIONS_FILE_HIST} ${WFO_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< water_flux_into_sea_water annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

WFO_REGIONS_DRIFT_PLOT=/g/data/r87/dbi599/temp/wfo-region-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${WFO_REGIONS_DRIFT_PLOT} : ${WFO_REGIONS_COEFFICIENTS} ${WFO_REGIONS_FILE_CNTRL} ${WFO_REGIONS_FILE_HIST} ${WFO_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py water_flux_into_sea_water $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

WFO_REGIONS_HEATMAP=/g/data/r87/dbi599/figures/water-cycle/wfo-region-sum-anomaly_Oyr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_gn_185001-201412-cumsum.png
${WFO_REGIONS_HEATMAP} : ${WFO_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/water_cycle/plot_pe_heatmap.py $< water_flux_into_sea_water cumulative_anomaly $@ --scale_factor 17 --time_bounds 1850-01-01 2014-12-31

WFO_REGIONS_HEATMAP_CLIM=/g/data/r87/dbi599/figures/water-cycle/wfo-region-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_gn_${CNTRL_TIME}-clim.png
${WFO_REGIONS_HEATMAP_CLIM} : ${WFO_REGIONS_FILE_CNTRL_TSERIES}
	${PYTHON} ${VIZ_SCRIPT_DIR}/water_cycle/plot_pe_heatmap.py $< water_flux_into_sea_water climatology $@ --scale_factor 16

### P (kg)

PR_PE_REGIONS_COEFFICIENTS=${PR_YR_DIR_CNTRL}/pr-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PR_PE_REGIONS_COEFFICIENTS} : ${PR_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_flux $@

PR_PE_REGIONS_ANOMALY_CUMSUM=${PR_YR_DIR_HIST}/pr-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PR_PE_REGIONS_ANOMALY_CUMSUM} : ${PR_PE_REGIONS_FILE_HIST} ${PR_PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

PR_PE_REGIONS_PLOT=/g/data/r87/dbi599/temp/pr-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${PR_PE_REGIONS_PLOT} : ${PR_PE_REGIONS_COEFFICIENTS} ${PR_PE_REGIONS_FILE_CNTRL} ${PR_PE_REGIONS_FILE_HIST} ${PR_PE_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### E (kg)

EVAP_PE_REGIONS_COEFFICIENTS=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${EVAP_PE_REGIONS_COEFFICIENTS} : ${EVAP_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${EVAP_VAR} $@

EVAP_PE_REGIONS_ANOMALY_CUMSUM=${EVAP_YR_DIR_HIST}/evspsbl-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${EVAP_PE_REGIONS_ANOMALY_CUMSUM} : ${EVAP_PE_REGIONS_FILE_HIST} ${EVAP_PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< ${EVAP_VAR} annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

EVAP_PE_REGIONS_PLOT=/g/data/r87/dbi599/temp/evspsbl-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${EVAP_PE_REGIONS_PLOT} : ${EVAP_PE_REGIONS_COEFFICIENTS} ${EVAP_PE_REGIONS_FILE_CNTRL} ${EVAP_PE_REGIONS_FILE_HIST} ${EVAP_PE_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py ${EVAP_VAR} $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### E (kg m-2)

### Flux (J)

FLUX_PE_REGIONS_COEFFICIENTS=${FLUX_YR_DIR_CNTRL}/${FLUX_VAR}-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${FLUX_PE_REGIONS_COEFFICIENTS} : ${FLUX_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${FLUX_VAR} $@

FLUX_PE_REGIONS_ANOMALY_CUMSUM=${FLUX_YR_DIR_HIST}/${FLUX_VAR}-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${FLUX_PE_REGIONS_ANOMALY_CUMSUM} : ${FLUX_PE_REGIONS_FILE_HIST} ${FLUX_PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< ${FLUX_VAR} annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

FLUX_PE_REGIONS_PLOT=/g/data/r87/dbi599/temp/${FLUX_VAR}-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${FLUX_PE_REGIONS_PLOT} : ${FLUX_PE_REGIONS_COEFFICIENTS} ${FLUX_PE_REGIONS_FILE_CNTRL} ${FLUX_PE_REGIONS_FILE_HIST} ${FLUX_PE_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py ${FLUX_NAME} $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### area (m2)

AREA_PE_REGIONS_COEFFICIENTS=${AREA_YR_DIR_CNTRL}/areacella-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${AREA_PE_REGIONS_COEFFICIENTS} : ${AREA_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< cell_area $@

AREA_PE_REGIONS_ANOMALY_CUMSUM=${AREA_YR_DIR_HIST}/areacella-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${AREA_PE_REGIONS_ANOMALY_CUMSUM} : ${AREA_PE_REGIONS_FILE_HIST} ${AREA_PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< cell_area annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

AREA_PE_REGIONS_PLOT=/g/data/r87/dbi599/temp/areacella-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${AREA_PE_REGIONS_PLOT} : ${AREA_PE_REGIONS_COEFFICIENTS} ${AREA_PE_REGIONS_FILE_CNTRL} ${AREA_PE_REGIONS_FILE_HIST} ${AREA_PE_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py cell_area $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

# Spatial analysis

## cumulative sum

PE_CUMSUM_HIST=${PE_YR_DIR_HIST}/pe_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_CUMSUM_HIST} : ${PE_FILE_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@ --annual --flux_to_mag

PE_CUMSUM_CNTRL=${PE_YR_DIR_CNTRL}/pe_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_CUMSUM_CNTRL} : ${PE_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@ --annual --flux_to_mag

## cumulative anomaly

SPATIAL_COEFFICIENTS=${PE_YR_DIR_CNTRL}/pe-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${SPATIAL_COEFFICIENTS} : ${PE_CUMSUM_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_minus_evaporation_flux $@

PE_ANOMALY_CUMSUM=${PE_YR_DIR_HIST}/pe-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_ANOMALY_CUMSUM} : ${PE_CUMSUM_HIST} ${SPATIAL_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_minus_evaporation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check

SPATIAL_PLOT=/g/data/r87/dbi599/temp/pe_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_lat10-lon10.png
${SPATIAL_PLOT} : ${SPATIAL_COEFFICIENTS} ${PE_CUMSUM_CNTRL} ${PE_CUMSUM_HIST} ${PE_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_minus_evaporation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 10 10 ${BRANCH_TIME}

# targets 

pe-spatial : ${SPATIAL_PLOT}
pe-regions : ${PE_REGIONS_HEATMAP}
pe-regions-clim : ${PE_REGIONS_HEATMAP_CLIM} ${PE_REGIONS_HEATMAP_CLIM_PCT}
pe-per-m2-regions : ${PE_PER_M2_REGIONS_DRIFT_PLOT}
wfo-regions : ${WFO_REGIONS_HEATMAP}
wfo-regions-clim : ${WFO_REGIONS_HEATMAP_CLIM}
pr-regions : ${PR_PE_REGIONS_PLOT}
evap-regions : ${EVAP_PE_REGIONS_PLOT}
flux-regions : ${FLUX_PE_REGIONS_PLOT}
area-regions : ${AREA_PE_REGIONS_PLOT}
all : ${ZRS_PLOT} ${SPATIAL_PLOT} ${PE_REGIONS_PLOT} ${PR_PE_REGIONS_PLOT} ${EVAP_PE_REGIONS_PLOT} ${AREA_PE_REGIONS_PLOT}


