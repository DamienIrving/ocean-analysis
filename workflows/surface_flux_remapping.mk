# surface_flux_remapping.mk
#
# Description: Remap wfo or hfds data
#
# To execute (e.g.):
#   make all -n -B -f surface_flux_remapping.mk MODEL=ACCESS-CM2 EXPERIMENT=historical VAR=hfds
#   (VAR must be wfo or hfds)
#   (-n is a dry run) (-B is a force make)
#

include cmip_config.mk


FLUX_FILES_EXP := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Omon/${VAR}/${GRID_SURFACE}/${EXP_VERSION}/${VAR}*.nc))
FLUX_FILES_CNTRL := $(sort $(wildcard ${CMIP6_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Omon/${VAR}/${GRID_SURFACE}/${CNTRL_VERSION}/${VAR}*${CNTRL_FILE_END}))

FLUX_STD_NAME=${STD_NAME_${VAR}}

# experiment

FLUX_REMAPPED_DIR_EXP=${MY_DATA_DIR}/${PROJECT}/${MIP}/${INSTITUTION}/${MODEL}/${EXPERIMENT}/${EXP_RUN}/Oyr/${VAR}/${GRID_SURFACE}/${EXP_VERSION}
FLUX_REMAPPED_FILE_EXP=${FLUX_REMAPPED_DIR_EXP}/${VAR}_Oyr_${MODEL}_${EXPERIMENT}_${EXP_RUN}_x360y180_${EXP_TIME}.nc
${FLUX_REMAPPED_FILE_EXP} :
	mkdir -p ${FLUX_REMAPPED_DIR_EXP}
	${PYTHON} ${DATA_SCRIPT_DIR}/regrid.py ${FLUX_FILES_EXP} ${FLUX_STD_NAME} $@ --annual --lats -89.5 89.5 1 --lons 0.5 359.5 1

# control

FLUX_REMAPPED_DIR_CNTRL=${MY_DATA_DIR}/${PROJECT}/CMIP/${INSTITUTION}/${MODEL}/piControl/${CNTRL_RUN}/Oyr/${VAR}/${GRID_SURFACE}/${CNTRL_VERSION}
FLUX_REMAPPED_FILE_CNTRL=${FLUX_REMAPPED_DIR_CNTRL}/${VAR}_Oyr_${MODEL}_piControl_${CNTRL_RUN}_x360y180_${CNTRL_TIME}.nc
${FLUX_REMAPPED_FILE_CNTRL} :
	mkdir -p ${FLUX_REMAPPED_DIR_CNTRL}
	${PYTHON} ${DATA_SCRIPT_DIR}/regrid.py ${FLUX_FILES_CNTRL} ${FLUX_STD_NAME} $@ --annual --lats -89.5 89.5 1 --lons 0.5 359.5 1

# targets

all : ${FLUX_REMAPPED_FILE_EXP} ${FLUX_REMAPPED_FILE_CNTRL}
