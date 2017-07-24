# surface_metrics.mk
#
# Description: Workflow for producing surface metrics
#
# To execute:
#   1. copy name of target file from surface_metrics.mk 
#   2. paste it into surface_metrics_config.mk as the target variable  
#   3. $ make -n -B -f surface_metrics.mk  (-n is a dry run) (-B is a force make)


# Define marcos

include surface_metrics_config.mk
all : ${TARGET}

# Filenames

SO_FILE=$(wildcard ${ORIG_SO_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/so/latest/so_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_SO_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/so/latest
GLOBAL_MEAN_SO_FILE=${GLOBAL_SO_DIR}/so-global-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_GRIDDEV_SO_FILE=${GLOBAL_SO_DIR}/so-global-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

TAS_FILE=$(wildcard ${ORIG_TAS_DIR}/${MODEL}/${EXPERIMENT}/mon/atmos/${RUN}/tas/latest/tas_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_TAS_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/atmos/${RUN}/tas/latest
GLOBAL_MEAN_TAS_FILE=${GLOBAL_MEAN_TAS_DIR}/tas-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

OD_FILE=$(wildcard ${ORIG_OD_DIR}/${MODEL}/${EXPERIMENT}/mon/aerosol/${RUN}/od550aer/latest/od550aer_aero_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_OD_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/aerosol/${RUN}/od550aer/latest
GLOBAL_MEAN_OD_FILE=${GLOBAL_MEAN_OD_DIR}/od550aer-global-mean_aero_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
NH_MEAN_OD_FILE=${GLOBAL_MEAN_OD_DIR}/od550aer-nh-mean_aero_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
SH_MEAN_OD_FILE=${GLOBAL_MEAN_OD_DIR}/od550aer-sh-mean_aero_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

SOS_FILE=$(wildcard ${ORIG_SOS_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/sos/latest/sos_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_SOS_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/sos/latest
GLOBAL_GRIDDEV_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
NH_GRIDDEV_SOS_FILE=${GLOBAL_SOS_DIR}/sos-nh-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
SH_GRIDDEV_SOS_FILE=${GLOBAL_SOS_DIR}/sos-sh-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_BULKDEV_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-bulkdev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
SOS_CLIM_FILE=${GLOBAL_SOS_DIR}/sos-clim_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_MYAMP_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-myamp_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

PR_FILE=$(wildcard ${ORIG_PR_DIR}/${MODEL}/${EXPERIMENT}/mon/atmos/${RUN}/pr/latest/pr_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_PR_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/atmos/${RUN}/pr/latest
GLOBAL_MEAN_PR_FILE=${GLOBAL_MEAN_PR_DIR}/pr-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

EVSPSBL_DIR=${ORIG_EVSPSBL_DIR}/${MODEL}/${EXPERIMENT}/mon/atmos/${RUN}/evspsbl/latest
EVSPSBL_FILE=$(wildcard ${EVSPSBL_DIR}/evspsbl_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_EVSPSBL_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/atmos/${RUN}/evspsbl/latest
GLOBAL_MEAN_EVSPSBL_FILE=${GLOBAL_MEAN_EVSPSBL_DIR}/evspsbl-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

PE_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/mon/atmos/${RUN}/pe/latest
GLOBAL_PE_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/atmos/${RUN}/pe/latest
GLOBAL_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-global-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
NH_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-nh-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
SH_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-sh-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_BULKDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-global-bulkdev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OCEAN_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-ocean-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
LAND_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-land-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

SFTLF_FILE=${ORIG_SFTLF_DIR}/${MODEL}/${EXPERIMENT}/fx/atmos/${FX_RUN}/sftlf/latest/sftlf_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
BASIN_FILE=${ORIG_BASIN_DIR}/${MODEL}/${EXPERIMENT}/fx/ocean/${FX_RUN}/basin/latest/basin_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
ATMOS_AREA_FILE=${ORIG_AREAA_DIR}/${MODEL}/${EXPERIMENT}/fx/atmos/${FX_RUN}/areacella/latest/areacella_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
OCEAN_AREA_FILE=${ORIG_AREAO_DIR}/${MODEL}/${EXPERIMENT}/fx/ocean/${FX_RUN}/areacello/latest/areacello_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc

HFDS_FILE=$(wildcard ${ORIG_HFDS_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/hfds/latest/hfds_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
HFDS_ZONAL_SUM_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/hfds/latest
HFDS_ZONAL_SUM_FILE=${HFDS_ZONAL_SUM_DIR}/hfds-by-areacello-zs_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

HFBASIN_FILE=$(wildcard ${ORIG_HFBASIN_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/hfbasin/latest/hfbasin_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
HTC_FROM_HFBASIN_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/hfbasin/latest
HTC_FROM_HFBASIN_FILE=${HTC_FROM_HFBASIN_DIR}/hfbasin-convergence_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

HFY_FILE=$(wildcard ${ORIG_HFY_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/hfy/latest/hfy_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
HTC_FROM_HFY_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/hfy/latest
HTC_FROM_HFY_FILE=${HTC_FROM_HFY_DIR}/hfy-convergence_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

OHC_FILE=$(wildcard ${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/mon/ocean/${RUN}/ohc/latest/ohc_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
OHC_ZONAL_SUM_DIR=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/ohc/latest
OHC_ZONAL_SUM_FILE=${OHC_ZONAL_SUM_DIR}/ohc-zs_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

GLOBAL_METRICS=global_metrics
NUMMELIN_PLOT=/g/data/r87/dbi599/figures/heat-cycle/htc-hfds-ohc_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.png


# Global indicators

${PE_DIR} :
	mkdir -p $@
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py ${PR_FILE} precipitation_flux ${EVSPSBL_DIR} water_evaporation_flux $@

${GLOBAL_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${NH_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual --hemisphere nh

${SH_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual --hemisphere sh

${GLOBAL_BULKDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux bulk-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

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

${NH_GRIDDEV_SOS_FILE} :  
	mkdir -p ${GLOBAL_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${SOS_FILE} sea_surface_salinity grid-deviation $@ --area_file ${OCEAN_AREA_FILE} --smoothing annual --hemisphere nh

${SH_GRIDDEV_SOS_FILE} :  
	mkdir -p ${GLOBAL_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${SOS_FILE} sea_surface_salinity grid-deviation $@ --area_file ${OCEAN_AREA_FILE} --smoothing annual --hemisphere sh


${SOS_CLIM_FILE} :
	mkdir -p ${GLOBAL_BULKDEV_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climatology.py ${SOS_FILE} sea_surface_salinity $@

${GLOBAL_MEAN_TAS_FILE} :  
	mkdir -p ${GLOBAL_MEAN_TAS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${TAS_FILE} air_temperature mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${GLOBAL_MEAN_OD_FILE} :  
	mkdir -p ${GLOBAL_MEAN_OD_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${OD_FILE} atmosphere_optical_thickness_due_to_ambient_aerosol mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${NH_MEAN_OD_FILE} :  
	mkdir -p ${GLOBAL_MEAN_OD_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${OD_FILE} atmosphere_optical_thickness_due_to_ambient_aerosol mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual --hemisphere nh

${SH_MEAN_OD_FILE} :  
	mkdir -p ${GLOBAL_MEAN_OD_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${OD_FILE} atmosphere_optical_thickness_due_to_ambient_aerosol mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual --hemisphere sh

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

${GLOBAL_METRICS} : ${GLOBAL_MEAN_TAS_FILE} ${GLOBAL_GRIDDEV_PE_FILE} ${GLOBAL_BULKDEV_PE_FILE} ${GLOBAL_BULKDEV_SOS_FILE} 
	echo generate_delsole_command.py
	echo generate_global_indicator_command.py
	echo plot_comparison_timeseries.py


# Nummelin et al (2017) plot

${HFDS_ZONAL_SUM_FILE} : 
	mkdir -p ${HFDS_ZONAL_SUM_DIR}	
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_surface_forcing_maps.py ${HFDS_FILE} surface_downward_heat_flux_in_sea_water $@ --area ${OCEAN_AREA_FILE} --zonal_stat sum

${OHC_ZONAL_SUM_FILE} : 
	mkdir -p ${OHC_ZONAL_SUM_DIR}	
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_surface_forcing_maps.py ${OHC_FILE} ocean_heat_content $@ --zonal_stat sum

${HTC_FROM_HFBASIN_FILE} :
	mkdir -p ${HTC_FROM_HFBASIN_DIR} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ocean_heat_transport_convergence.py ${HFBASIN_FILE} northward_ocean_heat_transport ${MODEL} $@ 

${HTC_FROM_HFY_FILE} :
	mkdir -p ${HTC_FROM_HFY_DIR} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ocean_heat_transport_convergence.py ${HFY_FILE} ocean_heat_y_transport ${MODEL} $@ 

#${NUMMELIN_PLOT} : ${HTC_FROM_HFY_FILE} ${HFDS_ZONAL_SUM_FILE} ${OHC_ZONAL_SUM_FILE} 
#	${PYTHON} ${VIS_SCRIPT_DIR}/plot_heat_trends.py $@ --htc_file $< --hfds_file $(word 2,$^) --ohc_file $(word 3,$^)

${NUMMELIN_PLOT} : ${HTC_FROM_HFY_FILE} ${OHC_ZONAL_SUM_FILE} 
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_heat_trends.py $@ --htc_file $(word 1,$^) --ohc_file $(word 2,$^) 

