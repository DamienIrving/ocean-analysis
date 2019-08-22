# CMIP6

## Global access

* [ESMValTool](http://esmvaltool.org) is the global community tool for simple analysis
  * There is a [website](http://cmip-esmvaltool.dkrz.de/) to view ESMValTool results
  * The source code is on [GitHub](https://github.com/ESMValGroup/ESMValTool) (you can contribute indices/metrics)
* Model documentation, errata submission etc at [ES-DOC](https://es-doc.org/cmip6/)
  * At the [ES-DOC Search](https://search.es-doc.org/) page you can find detailed documentation about each of the models, including the values for static variables like `cpocean` and `rhozero`
* [FAFMIP website](http://www.fafmip.org/)

## NCI access
  
* Project oi10 on NCI
* Search and request data using the Climate Finder, [CleF](https://clef.readthedocs.io/en/latest/index.html)
  * At the moment `$ clef --request` sends to Paola Petrelli instead of NCI.
  * Instead, use the [data download online form](https://opus.nci.org.au/display/CMIP/Data+Download+Request) or send the output files from `$clef --request` (which are produced if you say no instead of yes at the end of the process) to help@nci.org.au

## Model issues

- CNRM-CM6-1 wfo is wrong sign.
