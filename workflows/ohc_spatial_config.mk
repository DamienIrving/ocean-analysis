# ohc_spatial_config.mk

# System configuration

PYTHON=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python

MY_DATA_DIR=/g/data/r87/dbi599
UA6_DATA_DIR=/g/data/ua6
CMIP5_DIR_START=/DRSv2/CMIP5
MY_CMIP5_DIR=${MY_DATA_DIR}${CMIP5_DIR_START}
UA6_CMIP5_DIR=${UA6_DATA_DIR}${CMIP5_DIR_START}

DATA_SCRIPT_DIR=~/ocean-analysis/data_processing
VIS_SCRIPT_DIR=~/ocean-analysis/visualisation

FIG_TYPE=png

# Analysis details (broad)

ORIG_THETAO_DIR=${UA6_CMIP5_DIR}
ORIG_AREAO_DIR=${UA6_CMIP5_DIR}
ORIG_VOL_DIR=${UA6_CMIP5_DIR}

MODEL=GISS-E2-R
EXPERIMENT=historicalGHG
RUN=r1i1p1
FX_EXPERIMENT=historical
FX_RUN=r0i0p0

# Analysis details (specific)

TARGET=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_1850-2005.nc
#${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/ohc/latest/dedrifted
#${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/ohc/latest/dedrifted/ohc-trend-wrt-tropics_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_1850-2005.nc
