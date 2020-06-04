# ocean_depth_analysis.mk
#
# Description: Ocean depth analysis
#
# To execute:
#   make all -n -B -f ocean_depth_analysis.mk  (-n is a dry run) (-B is a force make)
#

include cmip_config.mk


# File definitions

VOLCELLO_FILE=${VOLCELLO_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID}/${OFX_VERSION}/volcello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
TEMPERATURE_FILES_HIST := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/historical/${HIST_RUN}/Omon/thetao/${GRID}/${HIST_VERSION}/thetao_*.nc))
TEMPERATURE_FILE_HIST := $(firstword ${TEMPERATURE_FILES_HIST})
TEMPERATURE_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/thetao/${GRID}/${CNTRL_VERSION}/thetao_*.nc))

# basin file

BASIN_DIR=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${HIST_RUN}/Ofx/basin/${GRID}/${HIST_VERSION}
BASIN_FILE=${BASIN_DIR}/basin_Ofx_${MODEL}_historical_${HIST_RUN}_${GRID}.nc
${BASIN_FILE} : ${TEMPERATURE_FILE_HIST}
	mkdir -p ${BASIN_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin.py $< sea_water_potential_temperature $@

# volume(depth, basin)

VOLCELLO_SUM_DIR=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID}/${OFX_VERSION}
VOLCELLO_SUM_FILE=${VOLCELLO_SUM_DIR}/volcello-basin-sum_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID}.nc
${VOLCELLO_SUM_FILE} : ${VOLCELLO_FILE} ${BASIN_FILE}
	mkdir -p ${VOLCELLO_SUM_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin_aggregate.py $< ocean_volume sum $(word 2,$^) $@

# thetao(year, depth, basin)

TEMPERATURE_MEAN_DIR_HIST=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/historical/${HIST_RUN}/Oyr/thetao/${GRID}/${HIST_VERSION}
TEMPERATURE_MEAN_FILE_HIST=${TEMPERATURE_MEAN_DIR_HIST}/thetao-basin-mean_Oyr_${MODEL}_historical_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${TEMPERATURE_MEAN_FILE_HIST} : ${BASIN_FILE} ${VOLCELLO_FILE}
	mkdir -p ${TEMPERATURE_MEAN_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin_aggregate.py ${TEMPERATURE_FILES_HIST} sea_water_potential_temperature mean $< $@ --weights $(word 2,$^) --annual ${CHUNK_ANNUAL}

TEMPERATURE_MEAN_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Oyr/thetao/${GRID}/${CNTRL_VERSION}
TEMPERATURE_MEAN_FILE_CNTRL=${TEMPERATURE_MEAN_DIR_CNTRL}/thetao-basin-mean_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${TEMPERATURE_MEAN_FILE_CNTRL} : ${BASIN_FILE} ${VOLCELLO_FILE}
	mkdir -p ${TEMPERATURE_MEAN_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin_aggregate.py ${TEMPERATURE_FILES_CNTRL} sea_water_potential_temperature mean $< $@ --weights $(word 2,$^) --annual ${CHUNK_ANNUAL}

# remove drift

DRIFT_COEFFICIENT_FILE=${TEMPERATURE_MEAN_DIR_CNTRL}/thetao-basin-mean-coefficients_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID}_${CNTRL_TIME}.nc
${DRIFT_COEFFICIENT_FILE} : ${TEMPERATURE_MEAN_FILE_CNTRL}
	${PYTHON}  ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< sea_water_potential_temperature $@

TEMPERATURE_MEAN_DEDRIFTED_FILE=${TEMPERATURE_MEAN_DIR_HIST}/thetao-basin-mean-dedrifted_Oyr_${MODEL}_historical_${HIST_RUN}_${GRID}_${HIST_TIME}.nc
${TEMPERATURE_MEAN_DEDRIFTED_FILE} : ${TEMPERATURE_MEAN_FILE_HIST} ${DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< sea_water_potential_temperature annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_time_check

TEMPERATURE_MEAN_PLOT_FILE=/g/data/r87/dbi599/temp/temperature-basin-mean-dedrifted_Oyr_${MODEL}_piControl_${HIST_RUN}_${GRID}_${CNTRL_TIME}_depth-index-20.png
${TEMPERATURE_MEAN_PLOT_FILE} : ${DRIFT_COEFFICIENT_FILE} ${TEMPERATURE_MEAN_FILE_CNTRL} ${TEMPERATURE_MEAN_FILE_HIST} ${TEMPERATURE_MEAN_DEDRIFTED_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py sea_water_potential_temperature $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 20 -1 ${BRANCH_TIME}



# targets

all : ${TEMPERATURE_MEAN_PLOT_FILE} ${VOLCELLO_SUM_FILE}
	

