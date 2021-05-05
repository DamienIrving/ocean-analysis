# ocean_depth_analysis.mk
#
# Description: Ocean depth analysis
#
# To execute (e.g.):
#   make all -n -B -f ocean_depth_analysis.mk MODEL=ACCESS-CM2 EXPERIMENT=historical BASIN=atlantic
#   (BASIN must be atlantic or indo-pacific or globe)
#   (-n is a dry run) (-B is a force make)
#

include cmip_config.mk


# File definitions

VOLCELLO_FILE=${VOLCELLO_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/volcello/${GRID_OCEAN}/${OFX_VERSION_VOLCELLO}/volcello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID_OCEAN}.nc
BASIN_FILE_OCEAN=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${BASIN_RUN}/Ofx/basin/${GRID_OCEAN}/${BASIN_VERSION}/basin_Ofx_${MODEL}_historical_${BASIN_RUN}_${GRID_OCEAN}.nc
SALINITY_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/so/${GRID_OCEAN}/${EXP_VERSION}/so*.nc))
SALINITY_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/so/${GRID_OCEAN}/${CNTRL_VERSION}/so*${CNTRL_FILE_END}))
SURFACE_SALINITY_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/${SURFACE_SBIN_VAR}/${GRID_SURFACE}/${EXP_VERSION}/${SURFACE_SBIN_VAR}*.nc))

# calculate aggregate

SALINITY_MEAN_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Oyr/so/${GRID_OCEAN}/${EXP_VERSION}
SALINITY_MEAN_FILE_EXP=${SALINITY_MEAN_DIR_EXP}/so-${BASIN}-zonal-mean_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID_OCEAN}_${EXP_TIME}.nc
${SALINITY_MEAN_FILE_EXP} : ${BASIN_FILE_OCEAN} ${VOLCELLO_FILE}
	mkdir -p ${SALINITY_MEAN_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${SALINITY_FILES_EXP} sea_water_salinity zonal mean $@ --basin $< ${BASIN} --weights $(word 2,$^) --annual ${CHUNK_ANNUAL}

SALINITY_MEAN_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Oyr/so/${GRID_OCEAN}/${CNTRL_VERSION}
SALINITY_MEAN_FILE_CNTRL=${SALINITY_MEAN_DIR_CNTRL}/so-${BASIN}-zonal-mean_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_OCEAN}_${CNTRL_TIME}.nc
${SALINITY_MEAN_FILE_CNTRL} : ${BASIN_FILE_OCEAN} ${VOLCELLO_FILE}
	mkdir -p ${SALINITY_MEAN_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${SALINITY_FILES_CNTRL} sea_water_salinity zonal mean $@ --basin $< ${BASIN} --weights $(word 2,$^) --annual ${CHUNK_ANNUAL}

# remove drift

DRIFT_COEFFICIENT_FILE=${SALINITY_MEAN_DIR_CNTRL}/so-${BASIN}-zonal-mean-coefficients_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_OCEAN}_${CNTRL_TIME}.nc
${DRIFT_COEFFICIENT_FILE} : ${SALINITY_MEAN_FILE_CNTRL}
	${PYTHON}  ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< sea_water_salinity $@

SALINITY_MEAN_DEDRIFTED_FILE=${SALINITY_MEAN_DIR_EXP}/so-${BASIN}-zonal-mean-dedrifted_Oyr_${MODEL}_historical_${EXP_RUN}_${GRID_OCEAN}_${EXP_TIME}.nc
${SALINITY_MEAN_DEDRIFTED_FILE} : ${SALINITY_MEAN_FILE_EXP} ${DRIFT_COEFFICIENT_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< sea_water_salinity annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_time_check

SALINITY_MEAN_PLOT_FILE=/g/data/r87/dbi599/temp/SALINITY-${BASIN}-zonal-mean-dedrifted_Oyr_${MODEL}_piControl_${EXP_RUN}_${GRID_OCEAN}_${CNTRL_TIME}_depth-index-15.png
${SALINITY_MEAN_PLOT_FILE} : ${DRIFT_COEFFICIENT_FILE} ${SALINITY_MEAN_FILE_CNTRL} ${SALINITY_MEAN_FILE_EXP} ${SALINITY_MEAN_DEDRIFTED_FILE}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py sea_water_salinity $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 15 -1 ${BRANCH_TIME}

# remap

SALINITY_MEAN_DEDRIFTED_REMAPPED_FILE=${SALINITY_MEAN_DIR_EXP}/so-${BASIN}-zonal-mean-dedrifted_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_taimoor-grid_${EXP_TIME}.nc
${SALINITY_MEAN_DEDRIFTED_REMAPPED_FILE} : ${SALINITY_MEAN_DEDRIFTED_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/regrid.py $< sea_water_salinity $@ --depth_bnds 0 1 5 10 20 30 40 50 60 70 80 90 100 120 140 160 180 200 250 300 350 400 450 500 550 600 650 700 750 800 850 900 1000 1100 1200 1300 1400 1500 1600 1700 1800 2000 2270.01685 2548.92432 2833.92603 3123.33130 3415.88281 3710.66357 4007.01538 4304.46924 4602.69482 4901.45898 5200.59863 5500

SURFACE_SALINITY_REMAPPED_DIR=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Oyr/sos/${GRID_SURFACE}/${EXP_VERSION}
SURFACE_SALINITY_REMAPPED_FILE=${SURFACE_SALINITY_REMAPPED_DIR}/sos_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_x360y180_${EXP_TIME}.nc
${SURFACE_SALINITY_REMAPPED_FILE} :
	mkdir -p ${SURFACE_SALINITY_REMAPPED_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/regrid.py ${SURFACE_SALINITY_FILES_EXP} ${SURFACE_SBIN_VAR} $@ --annual --lats -89.5 89.5 1 --lons 0.5 359.5 1 --surface

# targets

full-depth : ${SALINITY_MEAN_PLOT_FILE} ${SALINITY_MEAN_DEDRIFTED_REMAPPED_FILE}
surface : ${SURFACE_SALINITY_REMAPPED_FILE}
	

