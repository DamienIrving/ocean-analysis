# ocean_depth_analysis.mk
#
# Description: Ocean depth analysis
#
# To execute (e.g.):
#   make full-depth -n -B -f ocean_depth_analysis.mk MODEL=ACCESS-CM2 EXPERIMENT=historical BASIN=atlantic VAR=so
#   (BASIN must be atlantic or indo-pacific or globe)
#   (VAR must be so or thetao)
#   (-n is a dry run) (-B is a force make)
#

include cmip_config.mk

VAR_STD_NAME=${STD_NAME_${VAR}}
ifeq (${VAR}, thetao)
  SURFACE_VAR=${SURFACE_TBIN_VAR}
  SURFACE_OUTVAR=tos
else
  SURFACE_VAR=${SURFACE_SBIN_VAR}
  SURFACE_OUTVAR=sos
endif
SURFACE_VAR_STD_NAME=${STD_NAME_${SURFACE_VAR}}


# File definitions

VOLCELLO_FILE=${VOLCELLO_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID_OCEAN}/${OFX_VERSION_VOLCELLO}/volcello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID_OCEAN}.nc
BASIN_FILE_OCEAN=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${BASIN_RUN}/Ofx/basin/${GRID_OCEAN}/${BASIN_VERSION}/basin_Ofx_${MODEL}_historical_${BASIN_RUN}_${GRID_OCEAN}.nc
VAR_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/${VAR}/${GRID_OCEAN}/${EXP_VERSION}/${VAR}*.nc))
VAR_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/${VAR}/${GRID_OCEAN}/${CNTRL_VERSION}/${VAR}*${CNTRL_FILE_END}))
SURFACE_VAR_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/${SURFACE_VAR}/${GRID_SURFACE}/${EXP_VERSION}/${SURFACE_VAR}*.nc))

# calculate aggregate

VAR_MEAN_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Oyr/${VAR}/${GRID_OCEAN}/${EXP_VERSION}
VAR_MEAN_FILE_EXP=${VAR_MEAN_DIR_EXP}/${VAR}-${BASIN}-zonal-mean_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID_OCEAN}_${EXP_TIME}.nc
${VAR_MEAN_FILE_EXP} : ${BASIN_FILE_OCEAN} ${VOLCELLO_FILE}
	mkdir -p ${VAR_MEAN_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${VAR_FILES_EXP} ${VAR_STD_NAME} zonal mean $@ --basin $< ${BASIN} --weights $(word 2,$^) --annual ${CHUNK_ANNUAL}

VAR_MEAN_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Oyr/${VAR}/${GRID_OCEAN}/${CNTRL_VERSION}
VAR_MEAN_FILE_CNTRL=${VAR_MEAN_DIR_CNTRL}/${VAR}-${BASIN}-zonal-mean_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_OCEAN}_${CNTRL_TIME}.nc
${VAR_MEAN_FILE_CNTRL} : ${BASIN_FILE_OCEAN} ${VOLCELLO_FILE}
	mkdir -p ${VAR_MEAN_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${VAR_FILES_CNTRL} ${VAR_STD_NAME} zonal mean $@ --basin $< ${BASIN} --weights $(word 2,$^) --annual ${CHUNK_ANNUAL}

# remove drift

DRIFT_COEFFICIENT_FILE=${VAR_MEAN_DIR_CNTRL}/${VAR}-${BASIN}-zonal-mean-coefficients_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_OCEAN}_${CNTRL_TIME}.nc
${DRIFT_COEFFICIENT_FILE} : ${VAR_MEAN_FILE_CNTRL}
	${PYTHON}  ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${VAR_STD_NAME} $@

VAR_MEAN_DEDRIFTED_FILE=${VAR_MEAN_DIR_EXP}/${VAR}-${BASIN}-zonal-mean-dedrifted_Oyr_${MODEL}_historical_${EXP_RUN}_${GRID_OCEAN}_${EXP_TIME}.nc
${VAR_MEAN_DEDRIFTED_FILE} : ${VAR_MEAN_FILE_EXP} ${DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< ${VAR_STD_NAME} annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_time_check 

VAR_MEAN_PLOT_FILE=${MY_DATA_DIR}/temp/${VAR}-${BASIN}-zonal-mean-dedrifted_Oyr_${MODEL}_piControl_${EXP_RUN}_${GRID_OCEAN}_${CNTRL_TIME}_depth-index-15.png
${VAR_MEAN_PLOT_FILE} : ${DRIFT_COEFFICIENT_FILE} ${VAR_MEAN_FILE_CNTRL} ${VAR_MEAN_FILE_EXP} ${VAR_MEAN_DEDRIFTED_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py ${VAR_STD_NAME} $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 15 30 ${BRANCH_TIME}

# remap

VAR_MEAN_DEDRIFTED_REMAPPED_FILE=${VAR_MEAN_DIR_EXP}/${VAR}-${BASIN}-zonal-mean-dedrifted_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_taimoor-grid_${EXP_TIME}.nc
${VAR_MEAN_DEDRIFTED_REMAPPED_FILE} : ${VAR_MEAN_DEDRIFTED_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/regrid.py $< ${VAR_STD_NAME} $@ --depth_bnds 0 1 5 10 20 30 40 50 60 70 80 90 100 120 140 160 180 200 250 300 350 400 450 500 550 600 650 700 750 800 850 900 1000 1100 1200 1300 1400 1500 1600 1700 1800 2000 2270.01685 2548.92432 2833.92603 3123.33130 3415.88281 3710.66357 4007.01538 4304.46924 4602.69482 4901.45898 5200.59863 5500

# surface

SURFACE_VAR_REMAPPED_DIR=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Oyr/${SURFACE_OUTVAR}/${GRID_SURFACE}/${EXP_VERSION}
SURFACE_VAR_REMAPPED_FILE=${SURFACE_VAR_REMAPPED_DIR}/${SURFACE_OUTVAR}_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_x360y180_${EXP_TIME}.nc
${SURFACE_VAR_REMAPPED_FILE} :
	mkdir -p ${SURFACE_VAR_REMAPPED_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/regrid.py ${SURFACE_VAR_FILES_EXP} ${SURFACE_VAR_STD_NAME} $@ --annual --lats -89.5 89.5 1 --lons 0.5 359.5 1 --surface

# targets

full-depth : ${VAR_MEAN_PLOT_FILE} ${VAR_MEAN_DEDRIFTED_REMAPPED_FILE}
surface : ${SURFACE_VAR_REMAPPED_FILE}
	

