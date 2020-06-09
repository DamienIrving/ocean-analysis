# water_cycle_analysis.mk
#
# Description: Water cycle analysis
#
# To execute:
#   make all -n -B -f pe_analysis.mk  (-n is a dry run) (-B is a force make)
#

include cmip_config.mk


# File definitions, CMIP6 models
 
PR_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Amon/pr/${GRID}/${ATMOS_HIST_VERSION}/pr*.nc))
EVAP_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Amon/evspsbl/${GRID}/${ATMOS_HIST_VERSION}/evspsbl*.nc))
PR_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/pr/${GRID}/${ATMOS_CNTRL_VERSION}/pr*.nc))
EVAP_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/evspsbl/${GRID}/${ATMOS_CNTRL_VERSION}/evspsbl*.nc))

# File definitions, CMIP5 models

#PR_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/pr/pr*.nc))
#EVAP_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${ATMOS_HIST_VERSION}/evspsbl/evspsbl*.nc))
#PR_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/mon/atmos/Amon/${CNTRL_RUN}/${ATMOS_CNTRL_VERSION}/pr/pr*.nc))
#EVAP_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/mon/atmos/Amon/${CNTRL_RUN}/${ATMOS_CNTRL_VERSION}/evspsbl/evspsbl*.nc))

# P-E

PE_MON_DIR_HIST=${MY_EXP_DATA_DIR}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Amon/pe/${GRID}/${ATMOS_HIST_VERSION}
PE_FILE_HIST=${PE_MON_DIR_HIST}/pe_Amon_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${PE_FILE_HIST} :
	mkdir -p ${PE_MON_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py $@ --pr_files ${PR_FILES_HIST} --evap_files ${EVAP_FILES_HIST}

PE_MON_DIR_CNTRL=${MY_CNTRL_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/pe/${GRID}/${ATMOS_CNTRL_VERSION}
PE_FILE_CNTRL=${PE_MON_DIR_CNTRL}/pe_Amon_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${PE_FILE_CNTRL} :
	mkdir -p ${PE_MON_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py $@ --pr_files ${PR_FILES_CNTRL} --evap_files ${EVAP_FILES_CNTRL}

# Regional analysis

## zonal sum

PE_YR_DIR_HIST=${MY_EXP_DATA_DIR}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Ayr/pe/${GRID}/${ATMOS_HIST_VERSION}
PE_ZS_FILE_HIST=${PE_YR_DIR_HIST}/pe-zonal-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${PE_ZS_FILE_HIST} : ${PE_FILE_HIST}
	mkdir -p ${PE_YR_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py $< precipitation_minus_evaporation_flux zonal sum $@ --multiply_by_area --annual --flux_to_mag

PE_YR_DIR_CNTRL=${MY_CNTRL_DATA_DIR}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/pe/${GRID}/${ATMOS_CNTRL_VERSION}
PE_ZS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-zonal-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${PE_ZS_FILE_CNTRL} : ${PE_FILE_CNTRL}
	mkdir -p ${PE_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py $< precipitation_minus_evaporation_flux zonal sum $@ --multiply_by_area --annual --flux_to_mag

## regional totals

PE_ZRS_FILE_HIST=${PE_YR_DIR_HIST}/pe-zonal-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_ZRS_FILE_HIST} : ${PE_ZS_FILE_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_regional_totals.py $< $@ --cumsum

PE_ZRS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-zonal-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_ZRS_FILE_CNTRL} : ${PE_ZS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_regional_totals.py $< $@ --cumsum

## cumulative anomaly

COEFFICIENTS=${PE_YR_DIR_CNTRL}/pe-zonal-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${COEFFICIENTS} : ${PE_ZRS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_minus_evaporation_flux $@

PE_ZRS_ANOMALY_CUMSUM=${PE_YR_DIR_HIST}/pe-zonal-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_ZRS_ANOMALY_CUMSUM} : ${PE_ZRS_FILE_HIST} ${COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_minus_evaporation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check

REGIONAL_PLOT=/g/data/r87/dbi599/temp/pe-zonal-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum_region-2.png
${REGIONAL_PLOT} : ${COEFFICIENTS} ${PE_ZRS_FILE_CNTRL} ${PE_ZRS_FILE_HIST} ${PE_ZRS_ANOMALY_CUMSUM}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_minus_evaporation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 2 ${BRANCH_TIME}


# Spatial analysis

## cumulative sum

PE_CUMSUM_HIST=${PE_YR_DIR_HIST}/pe_Ayr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${PE_CUMSUM_HIST} : ${PE_FILE_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@ --annual --flux_to_mag

PE_CUMSUM_CNTRL=${PE_YR_DIR_CNTRL}/pe_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${PE_CUMSUM_HIST} : ${PE_FILE_HIST}
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

pe-regional : ${REGIONAL_PLOT}
pe-spatial : ${SPATIAL_PLOT}
all : ${REGIONAL_PLOT} ${SPATIAL_PLOT}


