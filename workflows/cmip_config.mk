# System configuration

PYTHON=/g/data/r87/dbi599/miniconda3/envs/ocean/bin/python
DATA_SCRIPT_DIR=/home/599/dbi599/ocean-analysis/data_processing
VIZ_SCRIPT_DIR=/home/599/dbi599/ocean-analysis/visualisation
MY_DATA_DIR=/g/data/r87/dbi599/CMIP6/CMIP

#defaults
TOS_VAR=tos
TOS_LONG_NAME=sea_surface_temperature

# ACCESS-CM2
#
#MODEL=ACCESS-CM2
#INSTITUTION=CSIRO-ARCCSS
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20191108
#HIST_VERSION=v20191108
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191112
#CNTRL_TIME=095001-144912
#NCI_DATA_DIR=/g/data/fs38/publications/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


# ACCESS-ESM1-5
#
#MODEL=ACCESS-ESM1-5
#INSTITUTION=CSIRO
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20191115
#HIST_VERSION=v20191115
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191214
#CNTRL_TIME=010101-100012
#NCI_DATA_DIR=/g/data/fs38/publications/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# BCC-CSM2-MR
#
#MODEL=BCC-CSM2-MR
#INSTITUTION=BCC
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20181126
#HIST_VERSION=v20181126
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20181015
#CNTRL_TIME=185001-244912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# CanESM5
#
#MODEL=CanESM5
#INSTITUTION=CCCma
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190429
#HIST_VERSION=v20190429
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190429
#CNTRL_TIME=520101-620012
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# CAS-ESM2-0
#
#MODEL=CAS-ESM2-0
#INSTITUTION=CAS
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20200306
#HIST_VERSION=v20200306
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20200307
#CNTRL_TIME=000101-050912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${MY_DATA_DIR}
#FX_EXP=historical
#BRANCH_YEAR=--branch_year 80

# CNRM-CM6-1
#
#MODEL=CNRM-CM6-1
#INSTITUTION=CNRM-CERFACS
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20180917
#HIST_VERSION=v20180917
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20180814
#CNTRL_TIME=185001-234912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# CNRM-CM6-1-HR
#
#MODEL=CNRM-CM6-1-HR
#INSTITUTION=CNRM-CERFACS
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20191021
#HIST_VERSION=v20191021
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191021
#CNTRL_TIME=185001-214912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# CNRM-ESM2-1
#
#MODEL=CNRM-ESM2-1
#INSTITUTION=CNRM-CERFACS
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20181206
#HIST_VERSION=v20181206
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20181115
#CNTRL_TIME=185001-234912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# E3SM-1-0
# 
# MY_DATA_DIR for thetao and so because have to correct mask
#
#MODEL=E3SM-1-0
#INSTITUTION=E3SM-Project
#RUN=r1i1p1f1
#GRID=gr
#VOLCELLO_VERSION=v20190826
#HIST_VERSION=v20190826
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191007
#CNTRL_TIME=000101-050012
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# E3SM-1-1
# 
#MODEL=E3SM-1-1
#INSTITUTION=E3SM-Project
#RUN=r1i1p1f1
#GRID=gr
#VOLCELLO_VERSION=v20191212
#HIST_VERSION=v20191204
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191028
#CNTRL_TIME=185001-201412
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# EC-Earth3
#
#MODEL=EC-Earth3
#INSTITUTION=EC-Earth-Consortium
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20200310
#HIST_VERSION=v20200310
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20200203
#CNTRL_TIME=225901-275912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# EC-Earth3-Veg
#
#MODEL=EC-Earth3-Veg
#INSTITUTION=EC-Earth-Consortium
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190605
#HIST_VERSION=v20200225
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20200226
##v20190619
#CNTRL_TIME=185001-234912
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical
#BRANCH_YEAR=--branch_year 1930
#TOS_VAR=thetao
#TOS_LONG_NAME=sea_water_potential_temperature

# FGOALS-f3-L
#
#MODEL=FGOALS-f3-L
#INSTITUTION=CAS
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190918
#HIST_VERSION=v20191007
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191028
#CNTRL_TIME=060001-109912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${MY_DATA_DIR}
#FX_EXP=historical

# GISS-E2-1-G

#MODEL=GISS-E2-1-G
#INSTITUTION=NASA-GISS
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20180824
#HIST_VERSION=v20180827
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20180824
#CNTRL_TIME=415001-500012
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=piControl
#BRANCH_YEAR=--branch_year 4150
#TOS_VAR=thetao
#TOS_LONG_NAME=sea_water_potential_temperature

# GISS-E2-1-G-CC
#
#MODEL=GISS-E2-1-G-CC
#INSTITUTION=NASA-GISS
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190325
#HIST_VERSION=v20190815
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190815
#CNTRL_TIME=185001-201412
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=piControl
#TOS_VAR=thetao
#TOS_LONG_NAME=sea_water_potential_temperature

# IPSL-CM6A-LR
#
#MODEL=IPSL-CM6A-LR
#INSTITUTION=IPSL
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20180803
#HIST_VERSION=v20180803
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20181123
##v20200326
#CNTRL_TIME=185001-304912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# MIROC-ES2L
#
#MODEL=MIROC-ES2L
#INSTITUTION=MIROC
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20190823
#HIST_VERSION=v20190823
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190823
#CNTRL_TIME=185001-234912
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# MPI-ESM-1-2-HAM
#
#MODEL=MPI-ESM-1-2-HAM
#INSTITUTION=HAMMOZ-Consortium
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190627
#HIST_VERSION=v20190627
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190627
#CNTRL_TIME=185001-262912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# MPI-ESM1-2-HR
#
#MODEL=MPI-ESM1-2-HR
#INSTITUTION=MPI-M
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190710
#HIST_VERSION=v20190710
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190710
#CNTRL_TIME=185001-234912
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# MPI-ESM1-2-LR
#
#MODEL=MPI-ESM1-2-LR
#INSTITUTION=MPI-M
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190710
#HIST_VERSION=v20190710
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190710
#CNTRL_TIME=185001-284912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# MRI-ESM2-0
#
#MODEL=MRI-ESM2-0
#INSTITUTION=MRI
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20191205  # problem when calculating global volume
#HIST_VERSION=v20191205
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191224
#CNTRL_TIME=185001-255012
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical


# NorESM2-LM
#
# gn for surface and wfo anomaly, gr for water mass 
#
#MODEL=NorESM2-LM
#INSTITUTION=NCC
#RUN=r1i1p1f1
#GRID=gr
#VOLCELLO_VERSION=v20190815
#HIST_VERSION=v20190815
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190920
#CNTRL_TIME=160001-210012
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# NorESM2-MM
#
# gn for surface and wfo anomaly, gr for water mass 
#
#MODEL=NorESM2-MM
#INSTITUTION=NCC
#RUN=r1i1p1f1
#GRID=gr
#VOLCELLO_VERSION=v20191108
#HIST_VERSION=v20191108
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20191108
#CNTRL_TIME=120001-169912
#NCI_DATA_DIR=/g/data/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${NCI_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# SAM0-UNICON
#
#MODEL=SAM0-UNICON
#INSTITUTION=SNU
#RUN=r1i1p1f1
#GRID=gn
#VOLCELLO_VERSION=v20190323
#HIST_VERSION=v20190323
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190910
#CNTRL_TIME=000101-070012
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=historical

# UKESM1-0-LL
#
#MODEL=UKESM1-0-LL
#INSTITUTION=MOHC
#RUN=r1i1p1f2
#GRID=gn
#VOLCELLO_VERSION=v20190705
#HIST_VERSION=v20190627
#HIST_TIME=185001-201412
#CNTRL_VERSION=v20190827
#CNTRL_TIME=196001-305912
#NCI_DATA_DIR=/g/data1b/oi10/replicas/CMIP6/CMIP
#VOLCELLO_DIR=${MY_DATA_DIR}
#AREACELLO_DIR=${NCI_DATA_DIR}
#FX_EXP=piControl