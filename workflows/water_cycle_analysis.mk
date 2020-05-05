# water_cycle_analysis.mk
#
# Description: Water cycle analysis
#
# To execute:
#   make all -n -B -f water_cycle_analysis.mk  (-n is a dry run) (-B is a force make)
#

include cmip_config.mk


# File definitions

AREACELLO_FILE=${AREACELLO_DIR}/${INSTITUTION}/${MODEL}/${FX_EXP}/${RUN}/Ofx/areacello/${GRID}/${VOLCELLO_VERSION}/areacello_Ofx_${MODEL}_${FX_EXP}_${RUN}_${GRID}.nc
WFO_FILES_HIST := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/wfo/${GRID}/${HIST_VERSION}/wfo*.nc))
WFO_FILES_CNTRL := $(sort $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/piControl/${RUN}/Omon/wfo/${GRID}/${CNTRL_VERSION}/wfo*.nc))


# wfo

## historical zonal sum

WFO_DIR_HIST=${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Oyr/wfo/${GRID}/${HIST_VERSION}
WFO_ZONAL_SUM_FILE_HIST=${WFO_DIR_HIST}/wfo-zonal-sum_Oyr_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}-cumsum.nc
${WFO_ZONAL_SUM_FILE_HIST} : ${AREACELLO_FILE}
	mkdir -p ${WFO_DIR_HIST}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_horizontal_aggregate.py ${WFO_FILES_HIST} water_flux_into_sea_water zonal sum $@ --area $< --annual --cumsum --flux_to_mag 
#--ref_file /g/data1/rr3/publications/CMIP5/output1/CSIRO-QCCCE/CSIRO-Mk3-6-0/historical/mon/atmos/Amon/r1i1p1/v20110518/pr/pr_Amon_CSIRO-Mk3-6-0_historical_r1i1p1_185001-200512.nc precipitation_flux


