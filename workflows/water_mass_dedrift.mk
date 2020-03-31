# water_mass_dedrift.mk
#
# Description: De-drift the ocean volume binned by temperature
#
# To execute:
#   make -n -B -f water_mass_dedrift.mk  (-n is a dry run) (-B is a force make)

all : ${TARGET}

# System configuration

PYTHON=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
DATA_SCRIPT_DIR=/home/599/dbi599/ocean-analysis/data_processing

# Analysis configuration

MODEL = ACCESS-CM2
INSTITUTION = CSIRO-ARCCSS
RUN = r1i1p1f1
GRID = gn
HIST_VERSION = v20191108
HIST_TIME = 185001-201412
CNTRL_VERSION = v20191112
NCI_DATA_DIR = /g/data/fs38/publications/CMIP6/CMIP
MY_DATA_DIR = /g/data/r87/dbi599/CMIP6/CMIP

VOLCELLO_FILE = ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Ofx/volcello/${GRID}/${HIST_VERSION}/volcello_Ofx_${MODEL}_historical_${RUN}_${GRID}.nc
BASIN_FILE = ${MY_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Ofx/basin/${GRID}/${HIST_VERSION}/basin_Ofx_${MODEL}_historical_${RUN}_${GRID}.nc
SALINITY_FILES := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/so/${GRID}/${HIST_VERSION}/so*.nc) 
TEMPERATURE_FILES := $(wildcard ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/thetao/${GRID}/${HIST_VERSION}/thetao*.nc)

${WATER_MASS_FILE_HIST} = ${NCI_DATA_DIR}/${INSTITUTION}/${MODEL}/historical/${RUN}/Omon/water-mass/${GRID}/${HIST_VERSION}/water-mass_Omon_${MODEL}_historical_${RUN}_${GRID}_${HIST_TIME}.nc
${WATER_MASS_FILE_HIST} : ${VOLCELLO_FILE} ${BASIN_FILE} ${SALINITY_FILES} ${TEMPERATURE_FILES}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_water_mass_components.py $< $(word 2,$^) $@ --salinity_files $(word 3,$^) --temperature_files $(word 4,$^) 
	