# water_cycle_analysis.mk
#
# Description: Water cycle analysis
#
# To execute:
#   make all -n -B -f water_cycle_analysis.mk  (-n is a dry run) (-B is a force make)
#

include cmip_config.mk


# File definitions, CMIP6 models

#FX_RUN=${HIST_RUN}
#AREACELLO_FILE=${AREACELLO_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/areacello/${GRID}/${VOLCELLO_VERSION}/areacello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
#VOLCELLO_FILE=${VOLCELLO_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID}/${VOLCELLO_VERSION}/volcello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
#WFO_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Omon/wfo/${GRID}/${HIST_VERSION}/wfo*.nc))
#WFO_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/wfo/${GRID}/${CNTRL_VERSION}/wfo*.nc))
#SALINITY_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Omon/so/${GRID}/${HIST_VERSION}/so*.nc)) 
#SALINITY_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/so/${GRID}/${CNTRL_VERSION}/so*.nc)) 
#PR_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Amon/pr/${GRID}/${HIST_VERSION}/pr*.nc))

# File definitions, CMIP5 models

WFO_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/ocean/Omon/${HIST_RUN}/${HIST_VERSION}/wfo/wfo*.nc))
WFO_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/mon/ocean/Omon/${CNTRL_RUN}/${CNTRL_VERSION}/wfo/wfo*.nc))
SALINITY_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/ocean/Omon/${HIST_RUN}/${HIST_VERSION}/so/so*.nc))
SALINITY_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/mon/ocean/Omon/${CNTRL_RUN}/${CNTRL_VERSION}/so/so*.nc))
#PR_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${HIST_RUN}/${HIST_VERSION}/pr/pr*.nc))

#PR_FILE_HIST := $(firstword ${PR_FILES_HIST})
#REF_FILE=--ref_file ${PR_FILE_HIST} precipitation_flux

# wfo

## experiment zonal sum

WFO_DIR_HIST=${MY_EXP_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Oyr/wfo/${GRID}/${HIST_VERSION}
WFO_ZONAL_SUM_FILE_HIST=${WFO_DIR_HIST}/wfo-zonal-sum_Oyr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${WFO_ZONAL_SUM_FILE_HIST} : ${AREACELLO_FILE}
	mkdir -p ${WFO_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${WFO_FILES_HIST} water_flux_into_sea_water zonal sum $@ --area $< --annual --cumsum --flux_to_mag ${REF_FILE}

## control zonal sum

WFO_DIR_CNTRL=${MY_EXP_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Oyr/wfo/${GRID}/${CNTRL_VERSION}
WFO_ZONAL_SUM_FILE_CNTRL=${WFO_DIR_CNTRL}/wfo-zonal-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${WFO_ZONAL_SUM_FILE_CNTRL} : ${AREACELLO_FILE}
	mkdir -p ${WFO_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${WFO_FILES_CNTRL} water_flux_into_sea_water zonal sum $@ --area $< --annual --cumsum --flux_to_mag ${REF_FILE}

## cumulative anomaly

WFO_COEFFICIENTS=${WFO_DIR_CNTRL}/wfo-zonal-sum-coefficients_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${WFO_COEFFICIENTS} : ${WFO_ZONAL_SUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< water_flux_into_sea_water $@

WFO_ANOMALY_CUMSUM=${WFO_DIR_HIST}/wfo-zonal-sum-anomaly_Oyr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${WFO_ANOMALY_CUMSUM} : ${WFO_ZONAL_SUM_FILE_HIST} ${WFO_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< water_flux_into_sea_water annual $(word 2,$^) $@


# so

## volcello

MY_VOLCELLO_DIR=${MY_FX_DATA_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID}/${VOLCELLO_VERSION}
VOLCELLO_VS=${MY_VOLCELLO_DIR}/volcello-vertical-sum_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
${VOLCELLO_VS} : ${VOLCELLO_FILE}
	mkdir -p ${MY_VOLCELLO_DIR}	
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_vertical_aggregate.py $< ocean_volume sum $@

VOLCELLO_VZS=${MY_VOLCELLO_DIR}/volcello-vertical-zonal-sum_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
${VOLCELLO_VZS} : ${VOLCELLO_VS}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py $< ocean_volume zonal sum $@

## experiment vertical zonal mean

SO_DIR_HIST=${MY_EXP_DATA_DIR}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${HIST_RUN}/Oyr/so/${GRID}/${HIST_VERSION}
SO_VZM_HIST=${SO_DIR_HIST}/so-vertical-zonal-mean_Oyr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${SO_VZM_HIST} : ${VOLCELLO_VS}
	mkdir -p ${SO_DIR_HIST}
	bash ${DATA_SCRIPT_DIR}/calc_vertical_aggregate.sh ${SO_DIR_HIST} ${SALINITY_FILES_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${SO_DIR_HIST}/so-vertical-mean_*.nc sea_water_salinity zonal mean $@ --weights $< ${REF_FILE}

## control vertical zonal mean

SO_DIR_CNTRL=${MY_EXP_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Oyr/so/${GRID}/${CNTRL_VERSION}
SO_VZM_CNTRL=${SO_DIR_CNTRL}/so-vertical-zonal-mean_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${SO_VZM_CNTRL} : ${VOLCELLO_VS}
	mkdir -p ${SO_DIR_CNTRL}
	bash ${DATA_SCRIPT_DIR}/calc_vertical_aggregate.sh ${SO_DIR_CNTRL} ${SALINITY_FILES_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${SO_DIR_CNTRL}/so-vertical-mean_*.nc sea_water_salinity zonal mean $@ --weights $< ${REF_FILE}

## dedrifting

SO_COEFFICIENTS=${SO_DIR_CNTRL}/so-vertical-zonal-mean-coefficients_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${SO_COEFFICIENTS} : ${SO_VZM_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< sea_water_salinity $@ --outlier_threshold 0.01

SO_VZM_HIST_DEDRIFTED=${SO_DIR_HIST}/so-vertical-zonal-mean-dedrifted_Oyr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${SO_VZM_HIST_DEDRIFTED} : ${SO_VZM_HIST} ${SO_COEFFICIENTS}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< sea_water_salinity annual $(word 2,$^) $@

SO_VZM_PLOT=/g/data/r87/dbi599/temp/so-vertical-zonal-mean-dedrifted_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}_grid-point-50.png
${SO_VZM_PLOT} : ${SO_COEFFICIENTS} ${SO_VZM_CNTRL} ${SO_VZM_HIST} ${SO_VZM_HIST_DEDRIFTED}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py sea_water_salinity $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 50 --outlier_threshold 0.01 ${BRANCH_TIME}


# final plot

FINAL_PLOT=/g/data/r87/dbi599/temp/water-cycle-change_Oyr_${MODEL}_${EXPERIMENT}_${HIST_RUN}_${GRID}_${HIST_TIME}.png
${FINAL_PLOT} : ${VOLCELLO_VZS} ${WFO_ANOMALY_CUMSUM} ${SO_VZM_HIST_DEDRIFTED}
	${PYTHON} ${VIZ_SCRIPT_DIR}/water_cycle/plot_zonal_water_budget_change.py $@ $< --hist_files $(word 2,$^) $(word 3,$^) --experiments ${EXPERIMENT} 

# targets

all : ${FINAL_PLOT} ${SO_VZM_PLOT}


