# surface_metrics.mk
#
# Description: Workflow for producing surface metrics
#
# To execute:
#   1. copy name of target file from surface_metrics.mk 
#   2. paste it into surface_config.mk as the target variable  
#   3. $ make -n -B -f surface_metrics.mk  (-n is a dry run) (-B is a force make)


# Define marcos

include surface_config.mk
all : ${TARGET}

# Filenames

SO_FILE=$(wildcard ${ORIG_SO_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/so/${RUN}/so_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_SO_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/so/${RUN}
GLOBAL_MEAN_SO_FILE=${GLOBAL_SO_DIR}/so-global-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_GRIDDEV_SO_FILE=${GLOBAL_SO_DIR}/so-global-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

TAS_FILE=$(wildcard ${ORIG_TAS_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/atmos/tas/${RUN}/tas_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_TAS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/atmos/tas/${RUN}
GLOBAL_MEAN_TAS_FILE=${GLOBAL_MEAN_TAS_DIR}/tas-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

SOS_FILE=$(wildcard ${ORIG_SOS_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/sos/${RUN}/sos_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_SOS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/sos/${RUN}
GLOBAL_GRIDDEV_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_BULKDEV_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-bulkdev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
SOS_CLIM_FILE=${GLOBAL_SOS_DIR}/sos-clim_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_MYAMP_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-myamp_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

PR_FILE=$(wildcard ${ORIG_PR_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/atmos/pr/${RUN}/pr_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_PR_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/atmos/pr/${RUN}
GLOBAL_MEAN_PR_FILE=${GLOBAL_MEAN_PR_DIR}/pr-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

EVSPSBL_DIR=${ORIG_EVSPSBL_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/atmos/evspsbl/${RUN}
EVSPSBL_FILE=$(wildcard ${EVSPSBL_DIR}/evspsbl_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_EVSPSBL_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/atmos/evspsbl/${RUN}
GLOBAL_MEAN_EVSPSBL_FILE=${GLOBAL_MEAN_EVSPSBL_DIR}/evspsbl-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

PE_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/atmos/pe/${RUN}
GLOBAL_PE_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/atmos/pe/${RUN}
GLOBAL_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-global-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OCEAN_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-ocean-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
LAND_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-land-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

SFTLF_FILE=${ORIG_SFTLF_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/atmos/sftlf/${FX_RUN}/sftlf_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
BASIN_FILE=${ORIG_BASIN_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/basin/${FX_RUN}/basin_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
ATMOS_AREA_FILE=${ORIG_AREAA_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/atmos/areacella/${FX_RUN}/areacella_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
OCEAN_AREA_FILE=${ORIG_AREAO_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/areacello/${FX_RUN}/areacello_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc

GLOBAL_METRICS=global_metrics.nc


# Global indicators

${PE_DIR} :
	mkdir -p $@
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py ${PR_FILE} precipitation_flux ${EVSPSBL_DIR} water_evaporation_flux $@

${GLOBAL_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${OCEAN_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual --sftlf_file ${SFTLF_FILE} ocean

${LAND_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual --sftlf_file ${SFTLF_FILE} land

${GLOBAL_BULKDEV_SOS_FILE} :
	mkdir -p ${GLOBAL_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${SOS_FILE} sea_surface_salinity bulk-deviation $@ --area_file ${OCEAN_AREA_FILE} --smoothing annual

${GLOBAL_GRIDDEV_SOS_FILE} :  
	mkdir -p ${GLOBAL_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${SOS_FILE} sea_surface_salinity grid-deviation $@ --area_file ${OCEAN_AREA_FILE} --smoothing annual

${SOS_CLIM_FILE} :
	mkdir -p ${GLOBAL_BULKDEV_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climatology.py ${SOS_FILE} sea_surface_salinity $@

${GLOBAL_MEAN_TAS_FILE} :  
	mkdir -p ${GLOBAL_MEAN_TAS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${TAS_FILE} air_temperature mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${GLOBAL_MYAMP_SOS_FILE} : ${SOS_CLIM_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_my_salinity_amp.py ${SOS_FILE} sea_surface_salinity $< $@ --area_file ${OCEAN_AREA_FILE} --smoothing annual

${GLOBAL_MEAN_PR_FILE} :  
	mkdir -p ${GLOBAL_MEAN_PR_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${PR_FILE} precipitation_flux mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${GLOBAL_MEAN_EVSPSBL_FILE} :  
	mkdir -p ${GLOBAL_MEAN_EVSPSBL_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${EVSPSBL_FILE} water_evaporation_flux mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${GLOBAL_MEAN_SO_FILE} :  
	mkdir -p ${GLOBAL_SO_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_3D_metric.py ${DEDRIFTED_VARIABLE_FILES} sea_water_salinity mean $@ --volume_file ${VOLUME_FILE} --smoothing annual

${GLOBAL_GRIDDEV_SO_FILE} :  
	mkdir -p ${GLOBAL_SO_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_3D_metric.py ${DEDRIFTED_VARIABLE_FILES} sea_water_salinity grid-deviation $@ --volume_file ${VOLUME_FILE} --smoothing annual

${GLOBAL_METRICS} : ${GLOBAL_MEAN_TAS_FILE} ${GLOBAL_MEAN_PR_FILE} ${GLOBAL_MEAN_EVSPSBL_FILE} ${GLOBAL_BULKDEV_SOS_FILE} ${GLOBAL_GRIDDEV_SOS_FILE} ${GLOBAL_GRIDDEV_PE_FILE} ${OCEAN_GRIDDEV_PE_FILE} ${LAND_GRIDDEV_PE_FILE}
	echo generate_delsole_command.py
	echo generate_global_indicator_command.py
	echo plot_comparison_timeseries.py
