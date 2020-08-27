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
PR_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/pr/${GRID}/${ATMOS_CNTRL_VERSION}/pr*.nc))
EVAP_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/evspsbl/${GRID}/${ATMOS_CNTRL_VERSION}/evspsbl*.nc))
AREACELLA_FILE=${AREACELLA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/fx/areacella/${GRID}/${FX_VERSION}/areacella_fx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
SFTLF_FILE=${AREACELLA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/fx/sftlf/${GRID}/${FX_VERSION}/sftlf_fx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
EVAP_VAR=water_evapotranspiration_flux

# File definitions, CMIP5 models

#PR_FILES_HIST := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/pr/pr*.nc))
#EVAP_FILES_HIST := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/evspsbl/evspsbl*.nc))
#PR_FILES_CNTRL := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/piControl/mon/atmos/Amon/${CNTRL_RUN}/${ATMOS_CNTRL_VERSION}/pr/pr*.nc))
#EVAP_FILES_CNTRL := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/piControl/mon/atmos/Amon/${CNTRL_RUN}/${ATMOS_CNTRL_VERSION}/evspsbl/evspsbl*.nc))

#EVAP_VAR=water_evaporation_flux

PR_FILE_HIST := $(firstword ${PR_FILES_HIST})

# Directories

PE_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/pe/${GRID}/${ATMOS_HIST_VERSION}
PE_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/pe/${GRID}/${ATMOS_CNTRL_VERSION}

PR_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/pr/${GRID}/${ATMOS_HIST_VERSION}
PR_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/pr/${GRID}/${ATMOS_CNTRL_VERSION}

EVAP_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/evspsbl/${GRID}/${ATMOS_HIST_VERSION}
EVAP_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/evspsbl/${GRID}/${ATMOS_CNTRL_VERSION}

AREA_YR_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/areacella/${GRID}/${ATMOS_HIST_VERSION}
AREA_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/areacella/${GRID}/${ATMOS_CNTRL_VERSION}

# basin file

BASIN_DIR=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${FX_RUN}/fx/basin/${GRID}/${HIST_VERSION}
BASIN_FILE=${BASIN_DIR}/basin_fx_${MODEL}_historical_${FX_RUN}_${GRID}.nc
${BASIN_FILE} : ${PR_FILE_HIST} ${SFTLF_FILE}
	mkdir -p ${BASIN_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin.py $< precipitation_flux $@ --sftlf_file $(word 2,$^) --land_threshold 50

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


# Zonal sum regional analysis

## zonal sum

PE_ZS_FILE_HIST=${PE_YR_DIR_HIST}/pe-zonal-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${PE_ZS_FILE_HIST} : ${PE_FILE_HIST}
	mkdir -p ${PE_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py $< precipitation_minus_evaporation_flux zonal sum $@ --multiply_by_area --annual --flux_to_mag

PE_ZS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-zonal-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${PE_ZS_FILE_CNTRL} : ${PE_FILE_CNTRL}
	mkdir -p ${PE_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py $< precipitation_minus_evaporation_flux zonal sum $@ --multiply_by_area --annual --flux_to_mag

## regional totals

PE_ZRS_FILE_HIST=${PE_YR_DIR_HIST}/pe-zonal-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_ZRS_FILE_HIST} : ${PE_ZS_FILE_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_zonal_sum_regional_totals.py $< $@ --cumsum

PE_ZRS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-zonal-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_ZRS_FILE_CNTRL} : ${PE_ZS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_zonal_sum_regional_totals.py $< $@ --cumsum

## cumulative anomaly

ZRS_COEFFICIENTS=${PE_YR_DIR_CNTRL}/pe-zonal-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${ZRS_COEFFICIENTS} : ${PE_ZRS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_minus_evaporation_flux $@

PE_ZRS_ANOMALY_CUMSUM=${PE_YR_DIR_HIST}/pe-zonal-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_ZRS_ANOMALY_CUMSUM} : ${PE_ZRS_FILE_HIST} ${ZRS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_minus_evaporation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check

ZRS_PLOT=/g/data/r87/dbi599/temp/pe-zonal-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_region-2.png
${ZRS_PLOT} : ${ZRS_COEFFICIENTS} ${PE_ZRS_FILE_CNTRL} ${PE_ZRS_FILE_HIST} ${PE_ZRS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_minus_evaporation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 2 ${BRANCH_TIME}


# Spatial regions analysis

## raw timeseries

PE_REGIONS_FILE_HIST_TSERIES=${PE_YR_DIR_HIST}/pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${PE_REGIONS_FILE_HIST_TSERIES}: ${PE_FILE_HIST} ${BASIN_FILE}
	mkdir -p ${PE_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --annual

## regional cumsum

### P-E

PE_REGIONS_FILE_HIST=${PE_YR_DIR_HIST}/pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${BASIN_FILE}
	mkdir -p ${PE_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --annual --cumsum

PE_REGIONS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${BASIN_FILE}
	mkdir -p ${PE_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --annual --cumsum

### P

PR_PE_REGIONS_FILE_HIST=${PR_YR_DIR_HIST}/pr-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PR_PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${BASIN_FILE}
	mkdir -p ${PR_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${PR_FILES_HIST} --data_var precipitation_flux --annual --cumsum

PR_PE_REGIONS_FILE_CNTRL=${PR_YR_DIR_CNTRL}/pr-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PR_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${BASIN_FILE}
	mkdir -p ${PR_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${PR_FILES_CNTRL} --data_var precipitation_flux --annual --cumsum

### E

EVAP_PE_REGIONS_FILE_HIST=${EVAP_YR_DIR_HIST}/evspsbl-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${EVAP_PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${BASIN_FILE}
	mkdir -p ${EVAP_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${EVAP_FILES_HIST} --data_var ${EVAP_VAR} --annual --cumsum

EVAP_PE_REGIONS_FILE_CNTRL=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${EVAP_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${BASIN_FILE}
	mkdir -p ${EVAP_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${EVAP_FILES_CNTRL} --data_var ${EVAP_VAR} --annual --cumsum

### area

AREA_PE_REGIONS_FILE_HIST=${AREA_YR_DIR_HIST}/areacella-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${AREA_PE_REGIONS_FILE_HIST}: ${PE_FILE_HIST} ${BASIN_FILE}
	mkdir -p ${AREA_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${AREACELLA_FILE} --data_var cell_area --annual

AREA_PE_REGIONS_FILE_CNTRL=${AREA_YR_DIR_CNTRL}/areacella-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${AREA_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${BASIN_FILE}
	mkdir -p ${AREA_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) $@ --data_files ${AREACELLA_FILE} --data_var cell_area --annual

## cumulative anomaly

### P-E

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
	${PYTHON} ${VIZ_SCRIPT_DIR}/water_cycle/plot_pe_heatmap.py $< precipitation_minus_evaporation_flux cumulative_anomaly $@ --scale_factor 17

PE_REGIONS_HEATMAP_CLIM=/g/data/r87/dbi599/figures/water-cycle/pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_gn_185001-201412_pct.png
${PE_REGIONS_HEATMAP_CLIM} : ${PE_REGIONS_FILE_HIST_TSERIES}
	${PYTHON} ${VIZ_SCRIPT_DIR}/water_cycle/plot_pe_heatmap.py $< precipitation_minus_evaporation_flux climatology $@ --pct


### P

PR_PE_REGIONS_COEFFICIENTS=${PR_YR_DIR_CNTRL}/pr-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PR_PE_REGIONS_COEFFICIENTS} : ${PR_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_flux $@

PR_PE_REGIONS_ANOMALY_CUMSUM=${PR_YR_DIR_HIST}/pr-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PR_PE_REGIONS_ANOMALY_CUMSUM} : ${PR_PE_REGIONS_FILE_HIST} ${PR_PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

PR_PE_REGIONS_PLOT=/g/data/r87/dbi599/temp/pr-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${PR_PE_REGIONS_PLOT} : ${PR_PE_REGIONS_COEFFICIENTS} ${PR_PE_REGIONS_FILE_CNTRL} ${PR_PE_REGIONS_FILE_HIST} ${PR_PE_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### E

EVAP_PE_REGIONS_COEFFICIENTS=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${EVAP_PE_REGIONS_COEFFICIENTS} : ${EVAP_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${EVAP_VAR} $@

EVAP_PE_REGIONS_ANOMALY_CUMSUM=${EVAP_YR_DIR_HIST}/evspsbl-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${EVAP_PE_REGIONS_ANOMALY_CUMSUM} : ${EVAP_PE_REGIONS_FILE_HIST} ${EVAP_PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< ${EVAP_VAR} annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

EVAP_PE_REGIONS_PLOT=/g/data/r87/dbi599/temp/evspsbl-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${EVAP_PE_REGIONS_PLOT} : ${EVAP_PE_REGIONS_COEFFICIENTS} ${EVAP_PE_REGIONS_FILE_CNTRL} ${EVAP_PE_REGIONS_FILE_HIST} ${EVAP_PE_REGIONS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py ${EVAP_VAR} $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### area

AREA_PE_REGIONS_COEFFICIENTS=${AREA_YR_DIR_CNTRL}/areacella-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${AREA_PE_REGIONS_COEFFICIENTS} : ${AREA_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< cell_area $@

AREA_PE_REGIONS_DEDRIFTED=${AREA_YR_DIR_HIST}/areacella-pe-region-sum-dedrifted_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${AREA_PE_REGIONS_DEDRIFTED} : ${AREA_PE_REGIONS_FILE_HIST} ${AREA_PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< cell_area annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

AREA_PE_REGIONS_PLOT=/g/data/r87/dbi599/temp/areacella-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}_shprecip-atlantic.png
${AREA_PE_REGIONS_PLOT} : ${AREA_PE_REGIONS_COEFFICIENTS} ${AREA_PE_REGIONS_FILE_CNTRL} ${AREA_PE_REGIONS_FILE_HIST} ${AREA_PE_REGIONS_DEDRIFTED}
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

pe-zrs : ${ZRS_PLOT}
pe-spatial : ${SPATIAL_PLOT}
pe-regions : ${PE_REGIONS_HEATMAP}
pe-regions-clim : ${PE_REGIONS_HEATMAP_CLIM}
pr-regions : ${PR_PE_REGIONS_PLOT}
evap-regions : ${EVAP_PE_REGIONS_PLOT}
area-regions : ${AREA_PE_REGIONS_PLOT}
all : ${ZRS_PLOT} ${SPATIAL_PLOT} ${PE_REGIONS_PLOT} ${PR_PE_REGIONS_PLOT} ${EVAP_PE_REGIONS_PLOT} ${AREA_PE_REGIONS_PLOT}


