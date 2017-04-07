# surface_metric_config.mk

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

ORIG_BASIN_DIR=${UA6_CMIP5_DIR}
ORIG_DEPTH_DIR=${UA6_CMIP5_DIR}
ORIG_AREAA_DIR=${UA6_CMIP5_DIR}
ORIG_AREAO_DIR=${UA6_CMIP5_DIR}
ORIG_SFTLF_DIR=${UA6_CMIP5_DIR}
ORIG_TAS_DIR=${UA6_CMIP5_DIR}
ORIG_SOS_DIR=${UA6_CMIP5_DIR}
ORIG_SO_DIR=${UA6_CMIP5_DIR}
ORIG_PR_DIR=${UA6_CMIP5_DIR}
ORIG_EVSPSBL_DIR=${UA6_CMIP5_DIR}

MODEL=CanESM2
EXPERIMENT=historicalMisc
RUN=r1i1p4
FX_RUN=r0i0p0

# Analysis details (specific)

START_DATE=1950-01-01
END_DATE=2000-12-31

TARGET=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/mon/atmos/${RUN}/pe/latest
#global_metrics.nc
#${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/so/latest/so-global-abs_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

