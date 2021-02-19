# water_cycle_analysis.mk
#
# Description: Water cycle analysis
#
# To execute:
#   make all -n -B -f pe_analysis.mk  (-n is a dry run) (-B is a force make)
#

.PHONY : all pe-zrs pe-spatial pe-regions

include cmip_config.mk

HEATMAP_START_YEAR=1850
HEATMAP_END_YEAR=2005

# File definitions
 
ifeq (${PROJECT}, CMIP6)          
PR_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Amon/pr/${GRID_SURFACE}/${ATMOS_EXP_VERSION_PR}/pr*.nc))
PR_FILES_FX := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Amon/pr/${GRID_SURFACE}/${REF_PR_VERSION}/pr*.nc))
EVAP_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Amon/evspsbl/${GRID_SURFACE}/${ATMOS_EXP_VERSION}/evspsbl*.nc))
WFO_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/wfo/${GRID_SURFACE}/${EXP_VERSION}/wfo*.nc))
FLUX_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Amon/${FLUX_VAR}/${GRID_SURFACE}/${ATMOS_EXP_VERSION}/${FLUX_VAR}*.nc))
PR_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/pr/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION_PR}/pr*.nc))
EVAP_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/evspsbl/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION}/evspsbl*.nc))
WFO_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/wfo/${GRID_SURFACE}/${CNTRL_VERSION}/wfo*.nc))
FLUX_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/${FLUX_VAR}/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION}/${FLUX_VAR}*.nc))
AREACELLA_FILE=${AREACELLA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/fx/areacella/${GRID_SURFACE}/${FX_VERSION}/areacella_fx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID_SURFACE}.nc
AREACELLO_FILE=${AREACELLO_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/Ofx/areacello/${GRID_SURFACE}/${FX_VERSION}/areacello_Ofx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID_SURFACE}.nc
ifeq (${SFTLF_DIR}, ${EMPTY})
SFTLF_FILE=${${MODEL}_SFTLF_FILE}
else
SFTLF_FILE=${SFTLF_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/${FX_EXP}/${FX_RUN}/fx/sftlf/${GRID_SURFACE}/${FX_VERSION}/sftlf_fx_${MODEL}_${FX_EXP}_${FX_RUN}_${GRID_SURFACE}.nc
endif

#EVAP_VAR=water_evapotranspiration_flux
# water_evapotranspiration_flux water_evaporation_flux
else
PR_FILES_EXP := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${ATMOS_EXP_RUN}/${ATMOS_EXP_VERSION_PR}/pr/pr*.nc))
EVAP_FILES_EXP := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/${EXPERIMENT}/mon/atmos/Amon/${ATMOS_EXP_RUN}/${ATMOS_EXP_VERSION}/evspsbl/evspsbl*.nc))
PR_FILES_CNTRL := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/piControl/mon/atmos/Amon/${CNTRL_RUN}/${ATMOS_CNTRL_VERSION_PR}/pr/pr*.nc))
EVAP_FILES_CNTRL := $(sort $(wildcard ${CMIP5_DATA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/piControl/mon/atmos/Amon/${CNTRL_RUN}/${ATMOS_CNTRL_VERSION}/evspsbl/evspsbl*.nc))
AREACELLA_FILE=${AREACELLA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/${FX_EXP}/fx/atmos/fx/${FX_RUN}/${FX_VERSION}/areacella/areacella*.nc
SFTLF_FILE=${AREACELLA_DIR}/${PROJECT}/combined/${INSTITUTION}/${MODEL}/${FX_EXP}/fx/atmos/fx/${FX_RUN}/${FX_VERSION}/sftlf/sftlf*.nc
#EVAP_VAR=water_evaporation_flux
endif

PR_FILE_FX := $(firstword ${PR_FILES_FX})

# Directories

PE_YR_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Ayr/pe/${GRID_SURFACE}/${ATMOS_EXP_VERSION_PR}
PE_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/pe/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION_PR}

WFO_YR_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Oyr/wfo/${GRID_SURFACE}/${EXP_VERSION}
WFO_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Oyr/wfo/${GRID_SURFACE}/${CNTRL_VERSION}

PR_YR_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Ayr/pr/${GRID_SURFACE}/${ATMOS_EXP_VERSION_PR}
PR_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/pr/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION_PR}

EVAP_YR_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Ayr/evspsbl/${GRID_SURFACE}/${ATMOS_EXP_VERSION}
EVAP_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/evspsbl/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION}

FLUX_YR_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Ayr/${FLUX_VAR}/${GRID_SURFACE}/${ATMOS_EXP_VERSION}
FLUX_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/${FLUX_VAR}/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION}

AREA_YR_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Ayr/areacella/${GRID_SURFACE}/${ATMOS_EXP_VERSION}
AREA_YR_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Ayr/areacella/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION}

# basin file

FX_BASIN_DIR=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${FX_RUN}/fx/basin/${GRID_SURFACE}/${FX_VERSION}
FX_BASIN_FILE=${FX_BASIN_DIR}/basin_fx_${MODEL}_historical_${FX_RUN}_${GRID_SURFACE}.nc
${FX_BASIN_FILE} : ${PR_FILE_FX} ${SFTLF_FILE}
	mkdir -p ${FX_BASIN_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin.py $< precipitation_flux $@ --sftlf_file $(word 2,$^) --land_threshold 50

BASIN_DIR=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/historical/${FX_RUN}/Ofx/basin/${GRID_SURFACE}/${EXP_VERSION}
BASIN_FILE=${BASIN_DIR}/basin_Ofx_${MODEL}_historical_${FX_RUN}_${GRID_SURFACE}.nc
${BASIN_FILE} : ${WFO_FILE_EXP}
	mkdir -p ${BASIN_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_basin.py $< water_flux_into_sea_water $@

# P-E

PE_MON_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${ATMOS_EXP_RUN}/Amon/pe/${GRID_SURFACE}/${ATMOS_EXP_VERSION_PR}
PE_FILE_EXP=${PE_MON_DIR_EXP}/pe_Amon_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${PE_FILE_EXP} :
	mkdir -p ${PE_MON_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py $@ --pr_files ${PR_FILES_EXP} --evap_files ${EVAP_FILES_EXP}

PE_MON_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Amon/pe/${GRID_SURFACE}/${ATMOS_CNTRL_VERSION}
PE_FILE_CNTRL=${PE_MON_DIR_CNTRL}/pe_Amon_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${PE_FILE_CNTRL} :
	mkdir -p ${PE_MON_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py $@ --pr_files ${PR_FILES_CNTRL} --evap_files ${EVAP_FILES_CNTRL}

# P-E regions analysis

## raw timeseries

WFO_REGIONS_FILE_CNTRL_TSERIES=${WFO_YR_DIR_CNTRL}/wfo-region-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${WFO_REGIONS_FILE_CNTRL_TSERIES}: ${BASIN_FILE}
	mkdir -p ${WFO_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py ${WFO_FILES_CNTRL} $< sum $@ --annual --area --area_file ${AREACELLO_FILE}

## regional cumsum

### area (m2)

AREA_PE_REGIONS_FILE_EXP=${AREA_YR_DIR_EXP}/areacella-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${AREA_PE_REGIONS_FILE_EXP}: ${PE_FILE_EXP} ${FX_BASIN_FILE}
	mkdir -p ${AREA_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --data_files ${AREACELLA_FILE} --data_var cell_area --annual

AREA_PE_REGIONS_CUMSUM_FILE_EXP=${AREA_YR_DIR_EXP}/areacella-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${AREA_PE_REGIONS_CUMSUM_FILE_EXP}: ${AREA_PE_REGIONS_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< cell_area $@

AREA_PE_REGIONS_FILE_CNTRL=${AREA_YR_DIR_CNTRL}/areacella-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${AREA_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${AREA_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --data_files ${AREACELLA_FILE} --data_var cell_area --annual ${CHUNK_ANNUAL}
	
AREA_PE_REGIONS_CUMSUM_FILE_CNTRL=${AREA_YR_DIR_CNTRL}/areacella-pe-region-sum_Ayr_${MODEL}_piControl_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${AREA_PE_REGIONS_CUMSUM_FILE_CNTRL}: ${AREA_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< cell_area $@

### P-E (kg)

PE_REGIONS_FILE_EXP=${PE_YR_DIR_EXP}/pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${PE_REGIONS_FILE_EXP}: ${PE_FILE_EXP} ${FX_BASIN_FILE}
	mkdir -p ${PE_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --annual --area

PE_REGIONS_CUMSUM_FILE_EXP=${PE_YR_DIR_EXP}/pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PE_REGIONS_CUMSUM_FILE_EXP} : ${PE_REGIONS_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@

PE_REGIONS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${PE_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --annual --area ${CHUNK_ANNUAL}

PE_REGIONS_CUMSUM_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PE_REGIONS_CUMSUM_FILE_CNTRL} : ${PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@

## P-E (kg m-2)

PE_PER_M2_REGIONS_FILE_EXP=${PE_YR_DIR_EXP}/pe-region-mean_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${PE_PER_M2_REGIONS_FILE_EXP}: ${PE_FILE_EXP} ${FX_BASIN_FILE}
	mkdir -p ${PE_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) mean $@ --annual

PE_PER_M2_REGIONS_CUMSUM_FILE_EXP=${PE_YR_DIR_EXP}/pe-region-mean_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PE_PER_M2_REGIONS_CUMSUM_FILE_EXP} : ${PE_PER_M2_REGIONS_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@

PE_PER_M2_REGIONS_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${PE_PER_M2_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${PE_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) mean $@ --annual ${CHUNK_ANNUAL}

PE_PER_M2_REGIONS_CUMSUM_FILE_CNTRL=${PE_YR_DIR_CNTRL}/pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PE_PER_M2_REGIONS_CUMSUM_FILE_CNTRL} : ${PE_PER_M2_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@

### wfo (kg)

WFO_REGIONS_FILE_EXP=${WFO_YR_DIR_EXP}/wfo-region-sum_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${WFO_REGIONS_FILE_EXP}: ${BASIN_FILE}
	mkdir -p ${WFO_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py ${WFO_FILES_EXP} $< sum $@ --annual --area --area_file ${AREACELLO_FILE}

WFO_REGIONS_CUMSUM_FILE_EXP=${WFO_YR_DIR_EXP}/wfo-region-sum_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${WFO_REGIONS_CUMSUM_FILE_EXP}: ${WFO_REGIONS_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${STD_NAME_wfo} $@

WFO_REGIONS_FILE_CNTRL=${WFO_YR_DIR_CNTRL}/wfo-region-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${WFO_REGIONS_FILE_CNTRL}: ${BASIN_FILE}
	mkdir -p ${WFO_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py ${WFO_FILES_CNTRL} $< sum $@ --annual --area --area_file ${AREACELLO_FILE} ${CHUNK_ANNUAL}

WFO_REGIONS_CUMSUM_FILE_CNTRL=${WFO_YR_DIR_CNTRL}/wfo-region-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${WFO_REGIONS_CUMSUM_FILE_CNTRL}: ${WFO_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${STD_NAME_wfo} $@

### P (kg)

PR_PE_REGIONS_FILE_EXP=${PR_YR_DIR_EXP}/pr-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${PR_PE_REGIONS_FILE_EXP}: ${PE_FILE_EXP} ${FX_BASIN_FILE}
	mkdir -p ${PR_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --data_files ${PR_FILES_EXP} --data_var precipitation_flux --annual --area

PR_PE_REGIONS_CUMSUM_FILE_EXP=${PR_YR_DIR_EXP}/pr-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PR_PE_REGIONS_CUMSUM_FILE_EXP}: ${PR_PE_REGIONS_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_flux $@

PR_PE_REGIONS_FILE_CNTRL=${PR_YR_DIR_CNTRL}/pr-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${PR_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${PR_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --data_files ${PR_FILES_CNTRL} --data_var precipitation_flux --annual --area ${CHUNK_ANNUAL}

PR_PE_REGIONS_CUMSUM_FILE_CNTRL=${PR_YR_DIR_CNTRL}/pr-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PR_PE_REGIONS_CUMSUM_FILE_CNTRL}: ${PR_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_flux $@
	
## P (kg m-2)

PR_PER_M2_PE_REGIONS_FILE_EXP=${PR_YR_DIR_EXP}/pr-pe-region-mean_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${PR_PER_M2_PE_REGIONS_FILE_EXP}: ${PE_FILE_EXP} ${FX_BASIN_FILE}
	mkdir -p ${PR_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) mean $@ --data_files ${PR_FILES_EXP} --data_var precipitation_flux --annual

PR_PER_M2_PE_REGIONS_CUMSUM_FILE_EXP=${PR_YR_DIR_EXP}/pr-pe-region-mean_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PR_PER_M2_PE_REGIONS_CUMSUM_FILE_EXP} : ${PR_PER_M2_PE_REGIONS_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_flux $@

PR_PER_M2_PE_REGIONS_FILE_CNTRL=${PR_YR_DIR_CNTRL}/pr-pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${PR_PER_M2_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${PR_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) mean $@ --data_files ${PR_FILES_CNTRL} --data_var precipitation_flux --annual ${CHUNK_ANNUAL}

PR_PER_M2_PE_REGIONS_CUMSUM_FILE_CNTRL=${PR_YR_DIR_CNTRL}/pr-pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PR_PER_M2_PE_REGIONS_CUMSUM_FILE_CNTRL} : ${PR_PER_M2_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_flux $@

### E (kg)

EVAP_PE_REGIONS_FILE_EXP=${EVAP_YR_DIR_EXP}/evspsbl-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${EVAP_PE_REGIONS_FILE_EXP}: ${PE_FILE_EXP} ${FX_BASIN_FILE}
	mkdir -p ${EVAP_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --data_files ${EVAP_FILES_EXP} --data_var ${EVAP_VAR} --annual --area

EVAP_PE_REGIONS_CUMSUM_FILE_EXP=${EVAP_YR_DIR_EXP}/evspsbl-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${EVAP_PE_REGIONS_CUMSUM_FILE_EXP}: ${EVAP_PE_REGIONS_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${EVAP_VAR} $@

EVAP_PE_REGIONS_FILE_CNTRL=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${EVAP_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${EVAP_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --data_files ${EVAP_FILES_CNTRL} --data_var ${EVAP_VAR} --annual --area ${CHUNK_ANNUAL}

EVAP_PE_REGIONS_CUMSUM_FILE_CNTRL=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${EVAP_PE_REGIONS_CUMSUM_FILE_CNTRL}: ${EVAP_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${EVAP_VAR} $@

## E (kg m-2)

EVAP_PER_M2_PE_REGIONS_FILE_EXP=${EVAP_YR_DIR_EXP}/evspsbl-pe-region-mean_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}.nc
${EVAP_PER_M2_PE_REGIONS_FILE_EXP}: ${PE_FILE_EXP} ${FX_BASIN_FILE}
	mkdir -p ${EVAP_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) mean $@ --data_files ${EVAP_FILES_EXP} --data_var ${EVAP_VAR} --annual

EVAP_PER_M2_PE_REGIONS_CUMSUM_FILE_EXP=${EVAP_YR_DIR_EXP}/evspsbl-pe-region-mean_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${EVAP_PER_M2_PE_REGIONS_CUMSUM_FILE_EXP} : ${EVAP_PER_M2_PE_REGIONS_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${EVAP_VAR} $@

EVAP_PER_M2_PE_REGIONS_FILE_CNTRL=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}.nc
${EVAP_PER_M2_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${EVAP_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) mean $@ --data_files ${EVAP_FILES_CNTRL} --data_var ${EVAP_VAR} --annual ${CHUNK_ANNUAL}

EVAP_PER_M2_PE_REGIONS_CUMSUM_FILE_CNTRL=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${EVAP_PER_M2_PE_REGIONS_CUMSUM_FILE_CNTRL} : ${EVAP_PER_M2_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< ${EVAP_VAR} $@


### Flux (J)

FLUX_PE_REGIONS_FILE_EXP=${FLUX_YR_DIR_EXP}/${FLUX_VAR}-pe-region-sum_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${FLUX_PE_REGIONS_FILE_EXP}: ${PE_FILE_EXP} ${FX_BASIN_FILE}
	mkdir -p ${FLUX_YR_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --data_files ${FLUX_FILES_EXP} --data_var ${FLUX_NAME} --annual --cumsum

FLUX_PE_REGIONS_FILE_CNTRL=${FLUX_YR_DIR_CNTRL}/${FLUX_VAR}-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${FLUX_PE_REGIONS_FILE_CNTRL}: ${PE_FILE_CNTRL} ${FX_BASIN_FILE}
	mkdir -p ${FLUX_YR_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe_spatial_totals.py $< $(word 2,$^) sum $@ --data_files ${FLUX_FILES_CNTRL} --data_var ${FLUX_NAME} --annual --cumsum ${CHUNK_ANNUAL}

## cumulative anomaly

### P-E (kg)

PE_REGIONS_CUMSUM_COEFFICIENTS=${PE_YR_DIR_CNTRL}/pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PE_REGIONS_CUMSUM_COEFFICIENTS} : ${PE_REGIONS_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_minus_evaporation_flux $@

PE_REGIONS_CUMSUM_ANOMALY=${PE_YR_DIR_EXP}/pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PE_REGIONS_CUMSUM_ANOMALY} : ${PE_REGIONS_CUMSUM_FILE_EXP} ${PE_REGIONS_CUMSUM_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_minus_evaporation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

PE_REGIONS_CUMSUM_DRIFT_PLOT=/g/data/e14/dbi599/temp/pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${PE_REGIONS_CUMSUM_DRIFT_PLOT} : ${PE_REGIONS_CUMSUM_COEFFICIENTS} ${PE_REGIONS_CUMSUM_FILE_CNTRL} ${PE_REGIONS_CUMSUM_FILE_EXP} ${PE_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_minus_evaporation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### P-E (kg m-2)

PE_PER_M2_REGIONS_CUMSUM_COEFFICIENTS=${PE_YR_DIR_CNTRL}/pe-region-mean-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PE_PER_M2_REGIONS_CUMSUM_COEFFICIENTS} : ${PE_PER_M2_REGIONS_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_minus_evaporation_flux $@

PE_PER_M2_REGIONS_CUMSUM_ANOMALY=${PE_YR_DIR_EXP}/pe-region-mean-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PE_PER_M2_REGIONS_CUMSUM_ANOMALY} : ${PE_PER_M2_REGIONS_CUMSUM_FILE_EXP} ${PE_PER_M2_REGIONS_CUMSUM_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_minus_evaporation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

PE_PER_M2_REGIONS_CUMSUM_DRIFT_PLOT=/g/data/e14/dbi599/temp/pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${PE_PER_M2_REGIONS_CUMSUM_DRIFT_PLOT} : ${PE_PER_M2_REGIONS_CUMSUM_COEFFICIENTS} ${PE_PER_M2_REGIONS_CUMSUM_FILE_CNTRL} ${PE_PER_M2_REGIONS_CUMSUM_FILE_EXP} ${PE_PER_M2_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_minus_evaporation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### wfo (kg)

WFO_REGIONS_COEFFICIENTS=${WFO_YR_DIR_CNTRL}/wfo-region-sum-coefficients_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${WFO_REGIONS_COEFFICIENTS} : ${WFO_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< water_flux_into_sea_water $@

WFO_REGIONS_CUMSUM_ANOMALY=${WFO_YR_DIR_EXP}/wfo-region-sum-anomaly_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${WFO_REGIONS_CUMSUM_ANOMALY} : ${WFO_REGIONS_FILE_EXP} ${WFO_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< water_flux_into_sea_water annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

WFO_REGIONS_DRIFT_PLOT=/g/data/e14/dbi599/temp/wfo-region-sum_Oyr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${WFO_REGIONS_DRIFT_PLOT} : ${WFO_REGIONS_COEFFICIENTS} ${WFO_REGIONS_FILE_CNTRL} ${WFO_REGIONS_FILE_EXP} ${WFO_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py water_flux_into_sea_water $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### P (kg)

PR_PE_REGIONS_CUMSUM_COEFFICIENTS=${PR_YR_DIR_CNTRL}/pr-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PR_PE_REGIONS_CUMSUM_COEFFICIENTS} : ${PR_PE_REGIONS_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_flux $@

PR_PE_REGIONS_CUMSUM_ANOMALY=${PR_YR_DIR_EXP}/pr-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PR_PE_REGIONS_CUMSUM_ANOMALY} : ${PR_PE_REGIONS_CUMSUM_FILE_EXP} ${PR_PE_REGIONS_CUMSUM_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

PR_PE_REGIONS_CUMSUM_PLOT=/g/data/e14/dbi599/temp/pr-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${PR_PE_REGIONS_CUMSUM_PLOT} : ${PR_PE_REGIONS_CUMSUM_COEFFICIENTS} ${PR_PE_REGIONS_CUMSUM_FILE_CNTRL} ${PR_PE_REGIONS_CUMSUM_FILE_EXP} ${PR_PE_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### P (kg m-2)

PR_PER_M2_PE_REGIONS_CUMSUM_COEFFICIENTS=${PR_YR_DIR_CNTRL}/pr-pe-region-mean-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PR_PER_M2_PE_REGIONS_CUMSUM_COEFFICIENTS} : ${PR_PER_M2_PE_REGIONS_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_flux $@

PR_PER_M2_PE_REGIONS_CUMSUM_ANOMALY=${PR_YR_DIR_EXP}/pr-pe-region-mean-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PR_PER_M2_PE_REGIONS_CUMSUM_ANOMALY} : ${PR_PER_M2_PE_REGIONS_CUMSUM_FILE_EXP} ${PR_PER_M2_PE_REGIONS_CUMSUM_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

PR_PER_M2_PE_REGIONS_CUMSUM_PLOT=/g/data/e14/dbi599/temp/pr-pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${PR_PER_M2_PE_REGIONS_CUMSUM_PLOT} : ${PR_PER_M2_PE_REGIONS_CUMSUM_COEFFICIENTS} ${PR_PER_M2_PE_REGIONS_CUMSUM_FILE_CNTRL} ${PR_PER_M2_PE_REGIONS_CUMSUM_FILE_EXP} ${PR_PER_M2_PE_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### E (kg)

EVAP_PE_REGIONS_CUMSUM_COEFFICIENTS=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${EVAP_PE_REGIONS_CUMSUM_COEFFICIENTS} : ${EVAP_PE_REGIONS_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${EVAP_VAR} $@

EVAP_PE_REGIONS_CUMSUM_ANOMALY=${EVAP_YR_DIR_EXP}/evspsbl-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${EVAP_PE_REGIONS_CUMSUM_ANOMALY} : ${EVAP_PE_REGIONS_CUMSUM_FILE_EXP} ${EVAP_PE_REGIONS_CUMSUM_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< ${EVAP_VAR} annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

EVAP_PE_REGIONS_CUMSUM_PLOT=/g/data/e14/dbi599/temp/evspsbl-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${EVAP_PE_REGIONS_CUMSUM_PLOT} : ${EVAP_PE_REGIONS_CUMSUM_COEFFICIENTS} ${EVAP_PE_REGIONS_CUMSUM_FILE_CNTRL} ${EVAP_PE_REGIONS_CUMSUM_FILE_EXP} ${EVAP_PE_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py ${EVAP_VAR} $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### E (kg m-2)

EVAP_PER_M2_PE_REGIONS_CUMSUM_COEFFICIENTS=${EVAP_YR_DIR_CNTRL}/evspsbl-pe-region-mean-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${EVAP_PER_M2_PE_REGIONS_CUMSUM_COEFFICIENTS} : ${EVAP_PER_M2_PE_REGIONS_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${EVAP_VAR} $@

EVAP_PER_M2_PE_REGIONS_CUMSUM_ANOMALY=${EVAP_YR_DIR_EXP}/evspsbl-pe-region-mean-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${EVAP_PER_M2_PE_REGIONS_CUMSUM_ANOMALY} : ${EVAP_PER_M2_PE_REGIONS_CUMSUM_FILE_EXP} ${EVAP_PER_M2_PE_REGIONS_CUMSUM_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< ${EVAP_VAR} annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

EVAP_PER_M2_PE_REGIONS_CUMSUM_PLOT=/g/data/e14/dbi599/temp/evspsbl-pe-region-mean_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${EVAP_PER_M2_PE_REGIONS_CUMSUM_PLOT} : ${EVAP_PER_M2_PE_REGIONS_CUMSUM_COEFFICIENTS} ${EVAP_PER_M2_PE_REGIONS_CUMSUM_FILE_CNTRL} ${EVAP_PER_M2_PE_REGIONS_CUMSUM_FILE_EXP} ${EVAP_PER_M2_PE_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py ${EVAP_VAR} $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### Flux (J)

FLUX_PE_REGIONS_COEFFICIENTS=${FLUX_YR_DIR_CNTRL}/${FLUX_VAR}-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${FLUX_PE_REGIONS_COEFFICIENTS} : ${FLUX_PE_REGIONS_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< ${FLUX_VAR} $@

FLUX_PE_REGIONS_CUMSUM_ANOMALY=${FLUX_YR_DIR_EXP}/${FLUX_VAR}-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${FLUX_PE_REGIONS_CUMSUM_ANOMALY} : ${FLUX_PE_REGIONS_FILE_EXP} ${FLUX_PE_REGIONS_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< ${FLUX_VAR} annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

FLUX_PE_REGIONS_PLOT=/g/data/e14/dbi599/temp/${FLUX_VAR}-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${FLUX_PE_REGIONS_PLOT} : ${FLUX_PE_REGIONS_COEFFICIENTS} ${FLUX_PE_REGIONS_FILE_CNTRL} ${FLUX_PE_REGIONS_FILE_EXP} ${FLUX_PE_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py ${FLUX_NAME} $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

### area (m2)

AREA_PE_REGIONS_CUMSUM_COEFFICIENTS=${AREA_YR_DIR_CNTRL}/areacella-pe-region-sum-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${AREA_PE_REGIONS_CUMSUM_COEFFICIENTS} : ${AREA_PE_REGIONS_CUMSUM_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< cell_area $@

AREA_PE_REGIONS_CUMSUM_ANOMALY=${AREA_YR_DIR_EXP}/areacella-pe-region-sum-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${AREA_PE_REGIONS_CUMSUM_ANOMALY} : ${AREA_PE_REGIONS_CUMSUM_FILE_EXP} ${AREA_PE_REGIONS_CUMSUM_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< cell_area annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check --no_data_check

AREA_PE_REGIONS_CUMSUM_PLOT=/g/data/e14/dbi599/temp/areacella-pe-region-sum_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_shprecip-atlantic.png
${AREA_PE_REGIONS_CUMSUM_PLOT} : ${AREA_PE_REGIONS_CUMSUM_COEFFICIENTS} ${AREA_PE_REGIONS_CUMSUM_FILE_CNTRL} ${AREA_PE_REGIONS_CUMSUM_FILE_EXP} ${AREA_PE_REGIONS_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py cell_area $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 0 0 ${BRANCH_TIME}

# Spatial analysis

## cumulative sum

PE_CUMSUM_HIST=${PE_YR_DIR_EXP}/pe_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PE_CUMSUM_HIST} : ${PE_FILE_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@ --annual --flux_to_mag

PE_CUMSUM_CNTRL=${PE_YR_DIR_CNTRL}/pe_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${PE_CUMSUM_CNTRL} : ${PE_FILE_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_cumsum.py $< precipitation_minus_evaporation_flux $@ --annual --flux_to_mag

## cumulative anomaly

SPATIAL_COEFFICIENTS=${PE_YR_DIR_CNTRL}/pe-coefficients_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum.nc
${SPATIAL_COEFFICIENTS} : ${PE_CUMSUM_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< precipitation_minus_evaporation_flux $@

PE_CUMSUM_ANOMALY=${PE_YR_DIR_EXP}/pe-anomaly_Ayr_${MODEL}_${EXPERIMENT}_${ATMOS_EXP_RUN}_${GRID_SURFACE}_${EXP_TIME}-cumsum.nc
${PE_CUMSUM_ANOMALY} : ${PE_CUMSUM_HIST} ${SPATIAL_COEFFICIENTS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py $< precipitation_minus_evaporation_flux annual $(word 2,$^) $@ ${BRANCH_TIME} --no_parent_check

SPATIAL_PLOT=/g/data/e14/dbi599/temp/pe_Ayr_${MODEL}_piControl_${CNTRL_RUN}_${GRID_SURFACE}_${CNTRL_TIME}-cumsum_lat10-lon10.png
${SPATIAL_PLOT} : ${SPATIAL_COEFFICIENTS} ${PE_CUMSUM_CNTRL} ${PE_CUMSUM_HIST} ${PE_CUMSUM_ANOMALY}
	${PYTHON} ${VIZ_SCRIPT_DIR}/plot_drift.py precipitation_minus_evaporation_flux $@ --coefficient_file $< --control_files $(word 2,$^) --experiment_files $(word 3,$^) --dedrifted_files $(word 4,$^) --grid_point 10 10 ${BRANCH_TIME}

# targets 

pe-spatial : ${SPATIAL_PLOT}
pe-regions : ${PE_REGIONS_CUMSUM_DRIFT_PLOT}
pe-per-m2-regions : ${PE_PER_M2_REGIONS_CUMSUM_DRIFT_PLOT}
wfo-regions : ${WFO_REGIONS_CUMSUM_DRIFT_PLOT}
pr-regions : ${PR_PE_REGIONS_CUMSUM_PLOT}
pr-per-m2-regions : ${PR_PER_M2_PE_REGIONS_CUMSUM_PLOT}
evap-regions : ${EVAP_PE_REGIONS_CUMSUM_PLOT}
evap-per-m2-regions : ${EVAP_PER_M2_PE_REGIONS_CUMSUM_PLOT}
flux-regions : ${FLUX_PE_REGIONS_PLOT}
area-regions : ${AREA_PE_REGIONS_CUMSUM_PLOT}

all : ${PE_REGIONS_CUMSUM_DRIFT_PLOT} ${PE_PER_M2_REGIONS_CUMSUM_DRIFT_PLOT} ${PR_PE_REGIONS_CUMSUM_PLOT} ${PR_PER_M2_PE_REGIONS_CUMSUM_PLOT} ${EVAP_PE_REGIONS_CUMSUM_PLOT} ${EVAP_PER_M2_PE_REGIONS_CUMSUM_PLOT} ${AREA_PE_REGIONS_CUMSUM_PLOT}
	@echo ${EVAP_PE_REGIONS_CUMSUM_ANOMALY}
	@echo ${EVAP_PER_M2_PE_REGIONS_FILE_CNTRL}
	@echo ${EVAP_PER_M2_PE_REGIONS_CUMSUM_ANOMALY}
	@echo ${PR_PE_REGIONS_CUMSUM_ANOMALY}
	@echo ${PR_PER_M2_PE_REGIONS_FILE_CNTRL}
	@echo ${PR_PER_M2_PE_REGIONS_CUMSUM_ANOMALY}
	@echo ${PE_REGIONS_CUMSUM_ANOMALY}
	@echo ${PE_PER_M2_REGIONS_FILE_CNTRL}
	@echo ${PE_PER_M2_REGIONS_CUMSUM_ANOMALY}
	@echo ${AREA_PE_REGIONS_FILE_CNTRL}
	@echo ${AREA_PE_REGIONS_CUMSUM_ANOMALY}


