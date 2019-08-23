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

## Models

| Model | Information | Ocean model | Ocean model characteristics | Issues |
| ---   | ---         | ---         | ---                         | ---    |
| CNRM-CM6-1 | [Website](http://www.umr-cnrm.fr/cmip6/spip.php?rubrique8), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019MS001683), ES-DOC (missing) | NEMO 3.6 | BO, *FS*, *FWF* | wfo wrong sign; masso is not volo * rhozero |
| CNRM-ESM2-1 | [Website](http://www.umr-cnrm.fr/cmip6/spip.php?rubrique8), Reference (to come), ES-DOC (missing) | NEMO 3.6 | BO, *FS*, *FWF* | wfo wrong sign; masso is not volo * rhozero |
| EC-Earth3 | [Website](http://www.ec-earth.org/cmip6/ec-earth-in-cmip6/),  Reference (to come), ES-DOC (missing) | NEMO v? | BO, *FS*, *FWF* | |
| HadGEM3-GC31-LL | [Website](https://ukesm.ac.uk/cmip6/), [Reference](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2017MS001115), ES-DOC (complete) | NEMO 3.6 | BO, *FS*, *FWF* | |
| SAM0-UNICON | Website (none), [Reference](https://journals.ametsoc.org/doi/full/10.1175/JCLI-D-18-0796.1), ES-DOC (complete) | POP2 | BO, FS, *FWF* | Constant wfo?? |

*Assumed characteristics.*
