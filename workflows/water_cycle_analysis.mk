# water_cycle_analysis.mk
#
# Description: Water cycle analysis
#
# To execute:
#   make all -n -B -f water_cycle_analysis.mk  (-n is a dry run) (-B is a force make)
#

include cmip_config.mk
PR_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Amon/pr/${GRID}/${HIST_VERSION}/pr*.nc))
PR_FILE_HIST := $(firstword ${PR_FILES_HIST})
REF_FILE=--ref_file ${PR_FILE_HIST} precipitation_flux

#EXPERIMENT=historical
OFX_DIR=fx


# File definitions (path might be different for CMIP5 models)

AREACELLO_FILE=${AREACELLO_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/areacello/${GRID}/${VOLCELLO_VERSION}/areacello_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
VOLCELLO_FILE=${VOLCELLO_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/volcello/${GRID}/${VOLCELLO_VERSION}/volcello_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
WFO_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/wfo/${GRID}/${HIST_VERSION}/wfo*.nc))
WFO_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Omon/wfo/${GRID}/${CNTRL_VERSION}/wfo*.nc))
SALINITY_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/so/${GRID}/${HIST_VERSION}/so*.nc)) 
SALINITY_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Omon/so/${GRID}/${CNTRL_VERSION}/so*.nc)) 

# wfo

## historical zonal sum

WFO_DIR_HIST=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Oyr/wfo/${GRID}/${HIST_VERSION}
WFO_ZONAL_SUM_FILE_HIST=${WFO_DIR_HIST}/wfo-zonal-sum_Oyr_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${WFO_ZONAL_SUM_FILE_HIST} : ${AREACELLO_FILE}
	mkdir -p ${WFO_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${WFO_FILES_HIST} water_flux_into_sea_water zonal sum $@ --area $< --annual --cumsum --flux_to_mag ${REF_FILE}

## historical zonal sum

WFO_DIR_CNTRL=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Oyr/wfo/${GRID}/${CNTRL_VERSION}
WFO_ZONAL_SUM_FILE_CNTRL=${WFO_DIR_CNTRL}/wfo-zonal-sum_Oyr_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${WFO_ZONAL_SUM_FILE_CNTRL} : ${AREACELLO_FILE}
	mkdir -p ${WFO_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${WFO_FILES_CNTRL} water_flux_into_sea_water zonal sum $@ --area $< --annual --cumsum --flux_to_mag ${REF_FILE}

## cumulative anomaly

WFO_COEFFICIENTS=${WFO_DIR_CNTRL}/wfo-zonal-sum-coefficients_Oyr_${MODEL}_piControl_${RUN}_${GRID}_${CNTRL_TIME}-cumsum.nc
${WFO_COEFFICIENTS} : ${WFO_ZONAL_SUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< water_flux_into_sea_water $@

WFO_ANOMALY_CUMSUM=${WFO_DIR_HIST}/wfo-zonal-sum-anomaly_Oyr_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${WFO_ANOMALY_CUMSUM} : ${WFO_ZONAL_SUM_FILE_HIST} ${WFO_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< water_flux_into_sea_water annual $(word 2,$^) $@

# so

## volcello

MY_VOLCELLO_DIR=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/volcello/${GRID}/${VOLCELLO_VERSION}/
VOLCELLO_VERTICAL_SUM=${MY_VOLCELLO_DIR}/volcello-vertical-sum_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
${VOLCELLO_VERTICAL_SUM} : ${VOLCELLO_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_vertical_aggregate.py $< ocean_volume sum $@

VOLCELLO_VERTICAL_ZONAL_SUM=${MY_VOLCELLO_DIR}/volcello-vertical-zonal-sum_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
${VOLCELLO_VERTICAL_ZONAL_SUM} : ${VOLCELLO_VERTICAL_SUM}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py $< zonal sum $@

## historical vertical zonal mean

MY_SO_HIST_DIR=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Oyr/so/${GRID}/${HIST_VERSION}/
SO_VZM_HIST=${MY_SO_HIST_DIR}/so-vertical-zonal-mean_Oyr_${MODEL}_historical_${RUN}_${HIST_TIME}.nc
${SO_VZM_HIST} : ${VOLCELLO_VERTICAL_SUM}
	mkdir -p ${MY_SO_HIST_DIR}
	bash ${DATA_SCRIPT_DIR}/calc_vertical_aggregate.sh ${MY_SO_HIST_DIR} ${SALINITY_FILES_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${MY_SO_HIST_DIR}/so-vertical-mean_*.nc sea_water_salinity zonal mean $@ --weights $< ${REF_FILE}

## control vertical zonal mean

MY_SO_CNTRL_DIR=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Oyr/so/${GRID}/${CNTRL_VERSION}/
SO_VZM_CNTRL=${MY_SO_CNTRL_DIR}/so-vertical-zonal-mean_Oyr_${MODEL}_piControl_${RUN}_${CNTRL_TIME}.nc
${SO_VZM_CNTRL} : ${VOLCELLO_VERTICAL_SUM}
	mkdir -p ${MY_SO_CNTRL_DIR}
	bash ${DATA_SCRIPT_DIR}/calc_vertical_aggregate.sh ${MY_SO_CNTRL_DIR} ${SALINITY_FILES_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${MY_SO_CNTRL_DIR}/so-vertical-mean_*.nc sea_water_salinity zonal mean $@ --weights $< ${REF_FILE}


