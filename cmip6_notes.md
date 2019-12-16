# CMIP6

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
* [Geophysical Fluid Dynamics Laboratory](https://agupubs.onlinelibrary.wiley.com/doi/toc/10.1002/(ISSN)1942-2466.CMIPMOD1) (GFDL-CM4)


| Model | Information | Ocean model | Ocean model characteristics | Issues |
| ---   | ---         | ---         | ---                         | ---    |
| BCC-CSM2-MR | Website, [Reference](https://www.geosci-model-dev.net/12/1573/2019/), ES-DOC | MOM 4 | BO, *FS*, *FWF* | |
| BCC-ESM1 | Website, [Reference](https://www.geosci-model-dev.net/12/1573/2019/), ES-DOC | MOM 4 | BO, *FS*, *FWF* | |
| CanESM5 | Website, [Reference](https://www.geosci-model-dev-discuss.net/gmd-2019-177/), ES-DOC | | |
| CESM2-WACCM | Website, [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017MS001232), ES-DOC | | |
| CNRM-CM6-1 | [Website](http://www.umr-cnrm.fr/cmip6/spip.php?rubrique8), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019MS001683), ES-DOC | NEMO 3.6 | BO, *FS*, *FWF* | wfo wrong sign; masso is not volo * rhozero; missing dimension coordinates for x and y |
| CNRM-ESM2-1 | [Website](http://www.umr-cnrm.fr/cmip6/spip.php?rubrique8), Reference, ES-DOC | NEMO 3.6 | BO, *FS*, *FWF* | wfo wrong sign; masso is not volo * rhozero |
| EC-Earth3 | [Website](http://www.ec-earth.org/cmip6/ec-earth-in-cmip6/),  Reference, ES-DOC | NEMO v? | BO, *FS*, *FWF* | missing years in control thetaoga data |
| EC-Earth3-Veg | [Website](http://www.ec-earth.org/cmip6/ec-earth-in-cmip6/),  Reference, ES-DOC | NEMO v? | BO, *FS*, *FWF* | missing years in control thetaoga data |
| GFDL-CM4 | [Website](https://www.gfdl.noaa.gov/coupled-physical-model-cm4/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2019MS001829), ES-DOC | MOM 6 | BO, *FS*, *FWF* | Branch time issues. |
| HadGEM3-GC31-LL | [Website](https://ukesm.ac.uk/cmip6/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017MS001115), [ES-DOC](https://explore.es-doc.org/cmip6/models/mohc/hadgem3-gc31-ll) | NEMO 3.6 | BO, *FS*, *FWF* | |
| IPSL-CM6A-LR | [Website](http://forge.ipsl.jussieu.fr/igcmg/wiki/IPSLCMIP6), Reference, ES-DOC | NEMO 3.2 | BO, *FS*, *FWF* | wfo wrong sign; masso is not volo * rhozero; missing dimension coordinates for x and y |
| MIROC6 | Website, [Reference](https://www.geosci-model-dev.net/12/2727/2019/), ES-DOC | | | |
| MIROC-ES2L | Website, [Reference](https://www.geosci-model-dev-discuss.net/gmd-2019-275/), ES-DOC | | | |
| SAM0-UNICON | Website, [Reference](https://journals.ametsoc.org/doi/full/10.1175/JCLI-D-18-0796.1), ES-DOC | POP2 | BO, FS, *FWF* | Constant wfo?? |
| UKESM1-0-LL | [Website](https://ukesm.ac.uk/cmip6/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2019MS001739), [ES-DOC](https://explore.es-doc.org/cmip6/models/snu/sam0-unicon) | NEMO 3.6 | BO, *FS*, *FWF* | constant wfo; no volo |



*Assumed characteristics.*
