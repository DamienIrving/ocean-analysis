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
ORIG_OD_DIR=${UA6_CMIP5_DIR}
ORIG_SOS_DIR=${UA6_CMIP5_DIR}
ORIG_SO_DIR=${UA6_CMIP5_DIR}
ORIG_PR_DIR=${UA6_CMIP5_DIR}
ORIG_EVSPSBL_DIR=${UA6_CMIP5_DIR}
ORIG_HFDS_DIR=${UA6_CMIP5_DIR}
ORIG_HFBASIN_DIR=${UA6_CMIP5_DIR}
ORIG_HFY_DIR=${UA6_CMIP5_DIR}

MODEL=NorESM1-M
EXPERIMENT=historical
RUN=r1i1p1
FX_RUN=r0i0p0

TARGET=${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/sos/latest/sos-global-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

#${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/atmos/${RUN}/pe/latest/pe-nh-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

#${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/mon/atmos/${RUN}/pe/latest
#global_metrics

#${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/aerosol/${RUN}/od550aer/latest/od550aer-global-mean_aero_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
#${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/atmos/${RUN}/tas/latest/tas-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

#${MY_CMIP5_DIR}/${MODEL}/${EXPERIMENT}/yr/ocean/${RUN}/so/latest/so-global-abs_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

