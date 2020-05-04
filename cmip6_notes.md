# CMIP6

## Citation

Get the dataset DOI from the [lookup tables](https://redmine.dkrz.de/projects/cmip6-lta-and-data-citation/wiki/CMIP6_Data_References).

The [recommended acknowledgement](https://pcmdi.llnl.gov/CMIP6/TermsOfUse/TermsOfUse6-1.html) when using CMIP6 data:

"We acknowledge the World Climate Research Programme, which, through its Working Group on Coupled Modelling, coordinated and promoted CMIP6. We thank the climate modeling groups for producing and making available their model output, the Earth System Grid Federation (ESGF) for archiving the data and providing access, and the multiple funding agencies who support CMIP6 and ESGF."

## Resources

* [ESMValTool](http://esmvaltool.org) is the global community tool for simple analysis
  * There is a [website](http://cmip-esmvaltool.dkrz.de/) to view ESMValTool results
  * The source code is on [GitHub](https://github.com/ESMValGroup/ESMValTool) (you can contribute indices/metrics)
* Model documentation, errata submission etc at [ES-DOC](https://es-doc.org/cmip6/)
  * At the [ES-DOC Search](https://search.es-doc.org/) page you can find detailed documentation about each of the models, including the values for static variables like `cpocean` and `rhozero`
* [FAFMIP website](http://www.fafmip.org/)
* [CLEX CMS team CMIP6 quality checks repository](https://github.com/coecms/QCmip6)

## Data access at NCI
  
* Project oi10 on NCI
* Search and request data using the Climate Finder, [CleF](https://clef.readthedocs.io/en/latest/index.html)
  * At the moment `$ clef --request` sends to Paola Petrelli instead of NCI.
  * Instead, use the [data download online form](https://opus.nci.org.au/display/CMIP/Data+Download+Request) or send the output files from `$clef --request` (which are produced if you say no instead of yes at the end of the process) to help@nci.org.au

## Downloading data directly

The wget scripts need to be run with a `-H` option. That makes it ask for your ESGF login credentials.
```
$ bash wget.sh -H
```

## Models

A number of modelling centres have 
[collections](https://agupubs.onlinelibrary.wiley.com/topic/vi-categories-19422466/earth-system-modeling-2018-2020/19422466) 
published with the The Journal of Advances in Modeling Earth Systems, which document various aspects of their CMIP6 models:

* [Chinese Academy of Sciences](https://agupubs.onlinelibrary.wiley.com/doi/toc/10.1002/(ISSN)2169-8996.CASFGOALSESM1) (CAS-FGOALS, CAS-ESM)
* [Centre National de Recherches Météorologiques](https://agupubs.onlinelibrary.wiley.com/doi/toc/10.1002/(ISSN)1942-2466.CNRMCLIMATE) (CNRM-CM6-1, CNRM-ESM2-1)
* [Community Earth System Model](https://agupubs.onlinelibrary.wiley.com/doi/toc/10.1002/(ISSN)1942-2466.CESM2) (CESM2, CESM2-WACCM)
* [UK Earth System Models](https://agupubs.onlinelibrary.wiley.com/doi/toc/10.1002/(ISSN)1942-2466.UKESM1) (HadGEM3-GC3, UKESM1)
* [Energy Exascale Earth System Model](https://agupubs.onlinelibrary.wiley.com/doi/toc/10.1002/(ISSN)2169-8996.ENERGY1) (E3SM-1-0)
* [Max Planck Institute for Meteorology Earth System Model](https://agupubs.onlinelibrary.wiley.com/doi/toc/10.1002/(ISSN)1942-2466.MPIESM1) (MPI-ESM)
* [Geophysical Fluid Dynamics Laboratory](https://agupubs.onlinelibrary.wiley.com/doi/toc/10.1002/(ISSN)1942-2466.CMIPMOD1) (GFDL-CM4, GFDL-ESM4)


| Model | Information | Ocean model | Ocean model characteristics | Issues |
| ---   | ---         | ---         | ---                         | ---    |
| ACCESS-CM2 | Website, Reference, ES-DOC |  |  |  |
| ACCESS-ESM1-5 | Website, Reference, ES-DOC |  |  |  |
| AWI-CM-1-1-MR | Website, Reference, ES-DOC | FESOM (unstructured grid) |  |  |
| BCC-CSM2-MR | Website, [Reference](https://www.geosci-model-dev.net/12/1573/2019/), ES-DOC | MOM 4 | BO, *FS*, *FWF* | 1. has two lat and lon coordinates (remove auxillary coords with `fix_bcc_models.sh`) |
| BCC-ESM1 | Website, [Reference](https://www.geosci-model-dev.net/12/1573/2019/), ES-DOC | MOM 4 | BO, *FS*, *FWF* | 1. has two lat and lon coordinates (remove auxillary coords with `fix_bcc_models.sh`) <br> 2. from sometime in 1930s onwards time values are zero in the `so` historical data files |
| CAMS-CSM1-0 | Website, Reference, ES-DOC |  |  | 1. curvilinear ocean grid and no `Ofx` data, so must be regridded using `regrid.py` first |
| CanESM5 | Website, [Reference](https://www.geosci-model-dev-discuss.net/gmd-2019-177/), ES-DOC |  |  |  |
| CAS-ESM2-0 | Website, Reference, ES-DOC |  |  | 1. The surface ocean variables are split over two versions, e.g. `/g/data/oi10/replicas/CMIP6/CMIP/CAS/CAS-ESM2-0/piControl/r1i1p1f1/Omon/wfo/gn/v2020030[6,7]/` <br> 2. `wfo` wrong sign (I think) and fluxes are way too small in magnitude |
| CESM2 | Website, Reference, [ES-DOC](https://explore.es-doc.org/cmip6/models/ncar/cesm2) |  |  |  |
| CESM2-WACCM | Website, [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017MS001232), ES-DOC |  |  |  |
| CNRM-CM6-1 | [Website](http://www.umr-cnrm.fr/cmip6/spip.php?rubrique8), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019MS001683), ES-DOC | NEMO 3.6 | BO, *FS*, *FWF* | 1. `wfo` wrong sign <br> 2. `masso` is not `volo` * `rhozero` <br> 3. missing dimension coordinates for x and y <br> 4. `so` and `thetao` files use different time chunks |
| CNRM-ESM2-1 | [Website](http://www.umr-cnrm.fr/cmip6/spip.php?rubrique8), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2019MS001791), ES-DOC | NEMO 3.6 | BO, *FS*, *FWF* | 1. `wfo` wrong sign <br> 2. `masso` is not `volo` * `rhozero` <br> 3. `so` and `thetao` files use different time chunks |
| E3SM-1-0 | [Website](https://e3sm.org/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018MS001603), ES-DOC |  |  | 1. the missing value for land in `so` and `thetao` files (and possibly others) is 1.0 <br> 2. the historical experiment data doesn't span 1850-2014 |
| EC-Earth3 | [Website](http://www.ec-earth.org/cmip6/ec-earth-in-cmip6/),  Reference, ES-DOC | NEMO v? | BO, *FS*, *FWF* | 1. missing years in piControl `thetaoga` data <br>  2. `masso` is not `volo` * `rhozero` <br> 3. `wfo` wrong sign |
| EC-Earth3-Veg | [Website](http://www.ec-earth.org/cmip6/ec-earth-in-cmip6/),  Reference, ES-DOC | NEMO v? | BO, *FS*, *FWF* | 1. missing years in control `thetaoga` data <br> 2. `wfo` does not equal `wfonocorr` <br> 3. `masso` is not `volo` * `rhozero` <br> 4. `wfo` wrong sign <br> 5. The `branch_time` is listed as the year 2030 when it should be 1930 <br> 6. Bogus netCDF format for `v20200226/tos_Omon_EC-Earth3-Veg_piControl_r1i1p1f1_gn_188601-188612.nc` |
| FGOALS-f3-L | Website, Reference, ES-DOC |  |  | 1. Bogus `volcello` file (global volume is 1.9e+18 m3, typical value is 1.3e+18 m3) <br> 2. Masked points are 1e35 in `areacello` file (but when fixed can be used to create correct `volcello`) <br> `wfo` wrong sign | 
| GFDL-CM4 | [Website](https://www.gfdl.noaa.gov/coupled-physical-model-cm4/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2019MS001829), ES-DOC | MOM 6 | BO, *FS*, *FWF* | 1. branch time issues. |
| GFDL-ESM4 | [Website](https://www.gfdl.noaa.gov/earth-system-esm4/), Reference, ES-DOC | | | 1. `sos` data missing for ssp585 |
| GISS-E2-1-G | [Website](https://data.giss.nasa.gov/modelE/cmip6/), Reference, ES-DOC | | | 1. `wfo` wrong sign |
| GISS-E2-1-G-CC | [Website](https://data.giss.nasa.gov/modelE/cmip6/), Reference, ES-DOC | | | 1. `wfo` wrong sign |
| GISS-E2-1-H | [Website](https://data.giss.nasa.gov/modelE/cmip6/), Reference, ES-DOC | | | |
| HadGEM3-GC31-LL | [Website](https://ukesm.ac.uk/cmip6/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017MS001115), [ES-DOC](https://explore.es-doc.org/cmip6/models/mohc/hadgem3-gc31-ll) | NEMO 3.6 | BO, *FS*, *FWF* | |
| IPSL-CM6A-LR | [Website](http://forge.ipsl.jussieu.fr/igcmg/wiki/IPSLCMIP6), Reference, [ES-DOC](https://explore.es-doc.org/cmip6/models/ipsl/ipsl-cm6a-lr) | NEMO 3.2 | BO, *FS*, *FWF* | 1. `wfo` wrong sign <br> 2. `masso` is not `volo` * `rhozero` <br> 3. missing dimension coordinates for x and y |
| MCM-UA-1-0 | Website, Reference, ES-DOC |  |  | 1. global ocean volume (from `volcello`) is way too small |
| MIROC6 | Website, [Reference](https://www.geosci-model-dev.net/12/2727/2019/), [ES-DOC](https://explore.es-doc.org/cmip6/models/miroc/miroc6) | | | |
| MIROC-ES2L | Website, [Reference](https://www.geosci-model-dev-discuss.net/gmd-2019-275/), [ES-DOC](https://explore.es-doc.org/cmip6/models/miroc/miroc-es2l) | | | |
| MPI-ESM1-2-HR | [Website](https://www.mpimet.mpg.de/en/science/projects/integrated-activities/cmip6/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018MS001400), ES-DOC |  |  |  |
| MPI-ESM1-2-LR | [Website](https://www.mpimet.mpg.de/en/science/projects/integrated-activities/cmip6/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2018MS001400@10.1002/(ISSN)1942-2466.MPIESM1-2), ES-DOC |  |  |  |
| MRI-ESM2-0 | Website, Reference, ES-DOC | | | 1. No gn `volcello` and when calculated get global value which is slightly too high to be realistic |
| NESM3 | Website, [Reference](https://www.geosci-model-dev.net/11/2975/2018/), ES-DOC |  |  | 1. historical data doesn't go beyond 1999 <br> 2. curvilinear ocean grid and no `Ofx` data, so must be regridded using `regrid.py` first | 
| NorCPM1 | [Website](https://wiki.uib.no/norcpm/index.php/Norwegian_Climate_Prediction_Model), Reference, ES-DOC | | | 1. can use the gn `areacello` data (which has depth coord in metres) with gr data |
| NorESM2-LM | Website, Reference, ES-DOC | | | 1. bogus gn `volcello` data (so use gr data) |
| NorESM2-MM | Website, Reference, ES-DOC | | | 1. no gn `volcello` data (so use gr data) <br> 2. `Omon`, `piControl` data has both `145001-145012` and `145002-145912` files. Need latter so use `*912.nc` |
| SAM0-UNICON | Website, [Reference](https://journals.ametsoc.org/doi/full/10.1175/JCLI-D-18-0796.1), [ES-DOC](https://explore.es-doc.org/cmip6/models/snu/sam0-unicon) | POP2 | BO, FS, *FWF* | 1. `wfo` values are zero everywhere |
| UKESM1-0-LL | [Website](https://ukesm.ac.uk/cmip6/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2019MS001739), [ES-DOC](https://explore.es-doc.org/cmip6/models/mohc/ukesm1-0-ll) | NEMO 3.6 | BO, *FS*, *FWF* | 1. constant `wfo` |

*Assumed characteristics.*
