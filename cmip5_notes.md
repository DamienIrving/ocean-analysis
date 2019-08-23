# CMIP5 data

## Model documentation

* New [PCMDI website](http://pcmdi.github.io/)
* Old [guide to CMIP5](http://cmip-pcmdi.llnl.gov/cmip5/guide_to_cmip5.html)
    * HistoricalMisc abbreviations [document](http://cmip-pcmdi.llnl.gov/cmip5/docs/historical_Misc_forcing.pdf)
    * HistoricalMisc availability [document](http://cmip-pcmdi.llnl.gov/cmip5/docs/historical_Misc_forcing.pdf)
* [CMIP5 Models and Grid Resolution](https://portal.enes.org/data/enes-model-data/cmip5/resolution) 
* [CMIP5 errata page](https://pcmdi.llnl.gov/mips/cmip5/errata.html)  
* [ES-DOC](https://es-doc.org/) model documentation website (for CMIP5 and CMIP6 models)

## Global access

* OpenIDs (password usual with capital first and ! last):  
    * https://pcmdi.llnl.gov/esgf-idp/openid/damienirving (old)  
    * https://esgf.esrl.noaa.gov/esgf-idp/openid/damienirving (new)  
    * https://esgf-node.ipsl.upmc.fr/esgf-idp/openid/damienirving (new)  

## NCI access

* [Data download process/online form](https://opus.nci.org.au/display/CMIP/Data+Download+Request)
* The CoE data search tool (ARCCSSive) is documented [here](http://arccssive.readthedocs.io/en/latest/index.html)  
    * At the [GitHub repo](https://github.com/coecms/ARCCSSive) there are extra scripts `compare_ESGF.py` and `search_cmip5.py`   
    * The download requests go to: `/g/data1/ua6/unofficial-ESG-replica/tmp/pxp581/requests/`  
* NCI `/g/data/` [FAQs](http://nci.org.au/services-support/getting-help/gdata-faqs-2/)  
* [NCI training page](https://training.nci.org.au/)  
* [NCI ARCCSS training notes](https://training.nci.org.au/course/view.php?id=18)  
* [ARCCSS CMIP wiki](http://climate-cms.unsw.wikispaces.net/CMIP5+data)
* [NCI CMIP community page](https://opus.nci.org.au/display/CMIP/CMIP+Community+Home)
* To request access to different groups on NCI use [this page](https://my.nci.org.au/mancini)
* Help: climate_help@nf.nci.org.au, [ARCCSS Slack](https://arccss.slack.com)
* Example locations at NCI:
    * `/g/data/ua6/drstree/CMIP5/GCM/CSIRO-QCCCE/CSIRO-Mk3-6-0/historicalMisc/mon/ocean/so/r9i1p6/so_Omon_CSIRO-Mk3-6-0_historicalMisc_r9i1p6_185001-185912.nc` (old DRS)   
    * `/g/data/ua6/DRSv2/CMIP5/CSIRO-Mk3-6-0/historical/mon/atmos/r1i1p1/tas/latest/tas_Amon_CSIRO-Mk3-6-0_historical_r1i1p1_185001-200512.nc` (new DRS)
    * The CMIP5 replica Will eventually be moved from `ua6` to `al33`. The CMIP5 Australian data is at `rr3`.

## Runs

* piControl (pre-industrial control): pre-industrial control run (>500 years)
* historical (historical): similation of recent past (1850-2005)
* historicalNat (natural-only): historical simulation but with natural forcing only (volcanoes, solar variability)
* historicalGHG (GHG-only): historical simultaion but with GHG forcing only
* historicalExt (historical extension): extension of the historical simulation through 2012
* historicalMisc (various combinations of natural and anthropogenic forcings; abbreviations are included in the `forcing` global attribute)  
    * Nat (natural forcing; a combination, not explicitly defined, that might include, for example, solar and volcanic)
    * Ant (anthropogenic forcing; a mixture, not explicitly defined, that might include, for example, well-mixed greenhouse gases, aerosols, ozone, and land-use changes)
    * GHG (well mixed greenhouse gases; a mixture, not explicitly defined)
    * AA (anthropogenic aerosols; a mixture of aerosols, not explicitly defined)
    * SD (anthropogenic sulfate aerosol, accounting only for direct effects)
    * SI (anthropogenic sulfate aerosol, accounting only for indirect effects)
    * SA (= SD + SI; anthropogenic sulfate aerosol direct and indirect effects)
    * TO (tropospheric ozone)
    * SO (stratospheric ozone)
    * OZ (ozone; =tropospheric and stratospheric)
    * LU (land-use change)
    * Sl (solar irradiance)
    * Vl (volcanic aerosol)
    * SS (sea salt)
    * Ds (Dust)
    * BC (black carbon)
    * MD (mineral dust)
    * OC (organic carbon)

To find the branch point for where the historical runs depart from the control run,
the information should be in the global history attributes (`branch_time` global attribute).
There's also a `parent_experiment_rip` which might refer to the relevant control run??
Sometimes this information is either missing or wrong, 
so Jonathan Gregory also maintains a [pcmdi-ancestry document](http://pcmdi-cmip.llnl.gov/cmip5/errata/jgregory_cmip5ancestry.txt).
[Here](https://github.com/durack1/cmip5/blob/master/make_cmip5_spawninfo.py) is an example of it being used in Python. 


## Variables

### Omon

Salinity

* soga: global mean sea water salinity
* so: sea water salinity (units = psu)
* sos: sea surface salinity

Temperature

* tos: sea surface temperature 
* thetao: sea water potential temperature (K)

Wind stress

* tauuo: surface downward x stress (Pa)  
* tauvo: surface downward y stress (Pa) 
* tauucorr: surface downward x stress correction (Pa)  
* tauvcorr: surface downward y stress correction (Pa)

Surface radiative fluxes

* rlds: surface net downward longwave flux (where ocean is ice free) ($W m^{-2}$)
* rsntds: net downward shortwave flux at sea water surface ($W m^{-2}$)

Surface heat fluxes

* hfss: surface downward sensible heat flux ($W m^{-2}$)
* hfls: surface downward latent heat flux ($W m^{-2}$)
* hfds: downward heat flux at sea water surface (net flux of heat entering the liquid water column through its upper surface, excluding any "flux adjustment") ($W m^{-2}$)
* hfsithermds: heat flux into sea water due to sea ice thermodynamics ($W m^{-2}$)
* There are also a bunch of other obscure flux variables (iceberg thermodynamics, frazil ice formation, snow thermodynamics, runoff...)
* hfcorr: heat flux correction (positive indicates correction adds heat to ocean) ($W m^{-2}$)

Internal heat fluxes

* hfy: ocean heat y transport ($W$)
* hfx: ocean heat x transport ($W$)
* Rare: hfnorth (use hfy), hfbasin (northward ocean heat transport)

Other variables of interest

* pr: rainfall flux (ice free ocean)
* evs: water evaporation flux (ice free ocean)
* rhopoto: sea water potential density   
* msftmyz: ocean meridional overturning mass streamfunction (like hfbasin, lat/depth/basin)   
* msftyyz: ocean y overturning mass streamfunction (like hfy)

### Amon

TOA radiative fluxes:

* rsdt: toa incoming shortwave flux ($W m^{-2}$)
* rsut: toa outgoing shortwave flux ($W m^{-2}$)
* rlut: toa outgoing longwave flux ($W m^{-2}$)

Surface radiative fluxes:

* rsds: surface downwelling shortwave flux in air ($W m^{-2}$)
* rsus: surface upwelling shortwave flux in air ($W m^{-2}$)
* rlds: surface downwelling longwave flux in air ($W m^{-2}$)
* rlus: surface upwelling longwave flux in air ($W m^{-2}$)

Surface heat fluxes:

* hfss: surface upward sensible heat flux ($W m^{-2}$)
* hfls: surface upward latent heat flux (includes evaporation and sublimation) ($W m^{-2}$)

Surface wind stress:

* tauu: surface downward eastward stress (Pa)
* tauv: surface downward northward stress (Pa)

Other surface variables of interest:

* pr: precipitation flux ($kg m^{-2} s^{-1}$)  
* evspsbl: water evaporation flux ($kg m^{-2} s^{-1}$)  
* tas: air temperature (K)
 
### ocean fx      

* areacello: grid cell area
* volcello: grid cell volume
* basin: flag (i.e. integer value) specifying which ocean basin the grid cell is in
    * land = 0, southern ocean = 1, atlantic = 2, pacific = 3, arctic = 4, indian = 5, mediterranean = 6, black sea = 7, hudson bay = 8, baltic sea = 9, red sea = 10
* deptho: sea floor depth
* sftop: sea area fraction (for many models this is just 0 or 100)  

### atmos fx

* areacella: grid cell area  
* sftlf: land area fraction  
* od550aer: ambient aerosol optical thickness at 550 nm  


## Timescales

* Monthly: Omon
* Yearly: Oyr

### Model overlap

From [Heuzé & Heywood (2015)](https://journals.ametsoc.org/doi/full/10.1175/JCLI-D-14-00381.1):

* ACCESS1.0 has the same atmosphere model code and configuration as HadGEM2 and the same ocean model code as GFDL CM3 and GFDL-ESM2M (but a different configuration).
* CCSM4 and CESM1 (CAM5) have the same ocean model code but use a different atmosphere model code.
* CMCC-CM and CMCC-CMS have the same ocean code and configuration and the same atmosphere code with different configurations.
* GFDL-ESM2G and GFDL-ESM2M share the same atmosphere, land, and sea ice model codes. GFDL-ESM2M and GFDL CM3 share ocean codes that are roughly the same, whereas their atmosphere codes differ.
* GISS-E2-H and GISS-E2-R have the same atmosphere model code but different oceans.
* HadGEM2-ES is basically HadGEM2-CC with the addition of tropospheric chemistry.
* IPSL-CM5A-LR and IPSL-CM5A-MR have the same ocean and atmosphere model codes, but the resolution of the atmosphere is higher in IPSL-CM5A-MR.
* MIROC5 features a more recent version of the ocean model code than MIROC-ESM-CHEM and a different atmosphere model.
* MPI-ESM-LR and MPI-ESM-MR share the same ocean and atmosphere model codes; however, MPI-ESM-MR has a higher horizontal resolution in the ocean and vertical resolution in the atmosphere.


### General model details

#### Aerosol representation

Much of the information on the indirect effects and Ant source come from Wilcox (2013). There's also a table in
[Jones (2013)](http://onlinelibrary.wiley.com/doi/10.1002/jgrd.50239/full) which has a good summary.

| Model          | Institution  | First indirect | Second indirect | Ant source | Reference     | Notes | Web | Email |
| -------------- | -----------  | -------------- | --------------- | ---------- | ----------    | ----- | --- | ----- |
| ACCESS1.0      |              |                |                 |            |               |       |     |       |
| ACCESS1.3      |              |                |                 |            |               |       |     |       |
| CanESM2        |              | Yes            | No              | E1         | VonSalzen2013 |       | [Data download page](http://www.cccma.ec.gc.ca/data/cgcm4/cgcm4.shtml) on allows click, so they suggest downloading from ESGF ("show all replicas") |       |
| CCSM4          | NCAR         |                |                 |            |               |       | [Model site](http://www2.cesm.ucar.edu/), [Data download page](https://www.earthsystemgrid.org/search.html) |       |
| CESM1-CAM5     | NSF-DOE-NCAR |                |                 |            |               |       | [Model site](http://www2.cesm.ucar.edu/), [CMIP5 forcing info](http://www.cesm.ucar.edu/CMIP5/forcing_information/), [Data download page](https://www.earthsystemgrid.org/search.html) | bballard@ucar.edu (Barbara) |
| CMCC-CESM      |              |                |                 |            |               |       |     |       |
| CMCC-CMS       |              |                |                 |            |               |       |     |       |
| CNRM-CM5       |              |                |                 |            |               |       |     |       |
| CNRM-CM5-2     |              |                |                 |            |               |       |     |       |
| CSIRO-Mk3.6.0  |              | Yes            | No              | E1a        | Rotstayn2012  | Two funny grid points in North Atlantic (Didier) |   |   |
| FGOALS-g2      | LASG-IAP     |                |                 |            |               |       | aims3.llnl.gov |   |
| GFDL-CM3       |              | Yes            | No              | E1         | Donner2011    |       | [CMIP5 site](http://www.gfdl.noaa.gov/cmip), [Data download page](http://nomads.gfdl.noaa.gov:8080/DataPortal/cmip5.jsp) |       |   
| GFDL-ESM2G     |              |                |                 |            |               |       | [CMIP5 site](http://www.gfdl.noaa.gov/cmip), [Data download page](http://nomads.gfdl.noaa.gov:8080/DataPortal/cmip5.jsp) |       |
| GFDL-ESM2M     |              | No             | No              | E1         | Dunne2012     |       | [CMIP5 site](http://www.gfdl.noaa.gov/cmip), [Data download page](http://nomads.gfdl.noaa.gov:8080/DataPortal/cmip5.jsp) |       |
| GISS-E2-H      |              |                |                 |            | Miller2014, Schmidt2014  |       | [CMIP5 site](http://data.giss.nasa.gov/modelE/ar5/), [Data site](ftp://giss_cmip5@ftp.nccs.nasa.gov/), [Forcing info](http://data.giss.nasa.gov/modelforce/) | gavin.a.schmidt@nasa.gov |
| GISS-E2-H-CC   |              |                |                 |            | Miller2014, Schmidt2014  |       | [CMIP5 site](http://data.giss.nasa.gov/modelE/ar5/), [Data site](ftp://giss_cmip5@ftp.nccs.nasa.gov/), [Forcing info](http://data.giss.nasa.gov/modelforce/) | gavin.a.schmidt@nasa.gov |
| GISS-E2-R      |              |                |                 |            | Miller2014, Schmidt2014  |       | [CMIP5 site](http://data.giss.nasa.gov/modelE/ar5/), [Data site](ftp://giss_cmip5@ftp.nccs.nasa.gov/), [Forcing info](http://data.giss.nasa.gov/modelforce/) | gavin.a.schmidt@nasa.gov |
| GISS-E2-R-CC   |              |                |                 |            | Miller2014, Schmidt2014  |       | [CMIP5 site](http://data.giss.nasa.gov/modelE/ar5/), [Data site](ftp://giss_cmip5@ftp.nccs.nasa.gov/), [Forcing info](http://data.giss.nasa.gov/modelforce/) | gavin.a.schmidt@nasa.gov |
| HadGEM2-CC     |              |                |                 |            |               |       |     |       |  
| HadGEM2-ES     |              |                |                 |            |               |       |     |       |
| INM-CM4        |              |                |                 |            |               |       |     |       |
| IPSL-CM5A-LR   |              | Yes            | No              | E1         | Dufresne2013  |       | [CMIP5 site](http://icmc.ipsl.fr/index.php/icmc-projects/icmc-international-projects/international-project-cmip5) | ipsl-cmip5@ipsl.jussieu.fr | 
| IPSL-CM5A-MR   |              |                |                 |            |               |       |     |       |
| MIROC-ESM      |              |                |                 |            |               |       |     |       |
| MIROC-ESM-CHEM |              |                |                 |            |               |       |     |       | 
| MIROC4h        |              |                |                 |            |               |       |     |       | 
| MPI-ESM-LR     |              |                |                 |            |               |       |     |       |
| MPI-ESM-MR     |              |                |                 |            |               |       |     |       |
| MPI-ESM-P      |              |                |                 |            |               |       |     |       |
| MRI-CGCM3      |              |                |                 |            |               |       |     |       |
| NorESM1-M      |              |                |                 |            | Bentsen2013   |       | [Project homepage](http://folk.uib.no/ngfhd/EarthClim/index.htm) | [Contacts](http://folk.uib.no/ngfhd/EarthClim/Contacts/contacts.html) | 
| NorESM1-ME     |              |                |                 |            |               |       |     |       |

#### HistoricalMisc specifics

| Model         | rip             | forcing details | forcing notes (" " means in file attributes)                                                                                                                                 | thetao status                            | notes |
| ---           | ---             | ---             | ---                                                                                                                                                                          | ---                                      | ---   |      
| CanESM2       | r[1-5]i1p2      | LU              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p3      | Sl              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p4      | **AA**          |                                                                                                                                                                              | NCI has data                             |       |
| CCSM4 [c]     | r[1,4,6]i1p10   | **AA**          | 																																											   | Need to download from modelling group    |       |
|               | r[1,2,4,6]i1p11 | Ant             | 																																											   | Need to download from modelling group    |       |
|               | r[1,4,6]i1p12   | BC              | 																																											   |                                          |       |
|               | r[1,4,6]i1p13   | LU              | 																																											   |                                          |       |
|               | r[1,4,6]i1p14   | Oz              | 																																											   |                                          |       |
|               | r[1,4,6]i1p15   | SD              | 																																											   |                                          |       |
|               | r[1,4,6]i1p16   | Vl              | 																																											   |                                          |       |
|               | r[1,4,6]i1p17   | Sl              | 																																											   |                                          |       |
| CESM1-CAM5 [c]| r[1,2,3]i1p10   | **AA**          | 																																											   | No AA for thetao                         |       |
|               | r[1,2,3]i1p11   | Ant             | 																																											   | Could download from modelling group      |       |
|               | r[1,2,3]i1p13   | LU              | 																																											   |                                          |       |
|               | r[1,2,3]i1p14   | Oz              | 																																											   |                                          |       |
|               | r[1,2,3]i1p16   | Vl              | 																																											   |                                          |       |
|               | r[1,2,3]i1p17   | Sl              | 																																											   |                                          |       |
| CSIRO-Mk3.6   | r[1-10]i1p1     | Ant             |                                                                                                                                                                              | NCI has data                             |       |
|               | r[1-10]i1p2     | NoOz            |                                                                                                                                                                              | NCI has data                             |       |
|               | r[1-10]i1p3     | **NoAA**        | "Ant, Nat (anthropogenic aerosols, including the indirect effect of aerosols on snow albedo, fixed at pre-industrial levels)"                                                | NCI has data                             |       |
|               | r[1-10]i1p4     | **AA**          | "AA (anthropogenic aerosols, including the indirect effect of aerosols on snow albedo)"                                                                                      | NCI has data                             |       |
|               | r[1-10]i1p5     | AntNoAA         | Same as NoAA except AA emissions allowed to vary in Asian region                                                                                                             | NCI has data                             |       |
|               | r[1-10]i1p6     | Vl              |                                                                                                                                                                              | NCI has data                             |       |
| CNRM-CM5      | r[1-10]i1p1     | Ant             | "GHG,SA,BC,OC"                                                                                                                                                               | On ESGF (DKRZ)                           |       |
| FGOALS-g2     | r1i1p1          | Oz              |                                                                                                                                                                              |                                          |       |
|               | r2i1p1 [b]      | **AA**          | Aerosol forcing only SA, BC, Ds, OC, SS (via conc)                                                                                                                           | Copied from NCI bulk data (v20130314)    |       |
| GFDL-CM3      | r[1,3,5]i1p1    | **AA**          | direct + indirect, from emissions: "SA,BC,OC"    (i.e. forced by emissions, not concentrations)                                                                              | NCI has data but downloaded from modelling group (v20110601) due to time axis errors |     |
|               | r[1,3,5]i1p2    | Ant             |                                                                                                                                                                              | NCI has data but downloaded from modelling group (v20110601) due to time axis errors |     |                                          
| GFDL-ESM2G    | r1i1p3          | noLU            |                                                                                                                                                                              |                                          |       |
|               | r1i1p4          | noLU            |                                                                                                                                                                              |                                          |       |
| GFDL-ESM2M    | r1i1p2          | Ant             |                                                                                                                                                                              | Downloaded from modelling group (v20110601) |       |
|               | r1i1p3          | NoLU            |                                                                                                                                                                              |                                          |       |
|               | r1i1p4          | NoLU            |                                                                                                                                                                              |                                          |       |
|               | r1i1p5          | **AA**          | "SD,SS,BC,MD,OC"                                                                                                                                                             | Downloaded from modelling group (v20110601) |       |    
|               | r1i1p6          | LU              |                                                                                                                                                                              |                                          |       |
|               | r1i1p7          | Sl              |                                                                                                                                                                              |                                          |       |
|               | r1i1p8          | Vl              |                                                                                                                                                                              |                                          |       |
| GISS-E2-H [a] | r[1-5]i1p1      | **NoAIE**       | All forcings except aerosol indirect effects: "GHG, LU, Sl, Vl, BC, OC, SD, Oz (also includes orbital change - BC on snow - Nitrate aerosols - no aerosol indirect effects)" | NCI has data                                                  |       |
|               | r[1-5]i1p102    | Sl              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p103    | Vl              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p104    | LU              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p105    | Oz              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p106    | **AA-direct**   | Anthropogenic tropospheric aerosol: direct effect only (via concentration)                                                                                                   | Need to download from modelling group    |       |  
|               | r[1-5]i1p107    | **AA**          | Anthropogenic tropospheric aerosol: direct and indirect effect only (via concentration)                                                                                      | Need to download from modelling group    |       |
|               | r[1-5]i1p108    | BCsnow          |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p109    | Ant             |                                                                                                                                                                              | NCI has data                                                 |       |
|               | r[1-5]i1p302    | Sl              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p303    | Vl              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p309    | Ant             |                                                                                                                                                                              |                                          |       |
|               | r[1-5]i1p310    | **AA**          | Anthropogenic tropospheric aerosol via emissions of SO2, BC, OC, NH3 (i.e. forced by emissions, not concentrations)                                                          | Need to download from modelling group    |       |
|               | r[1-5]i1p311    | SLG             | Anthropogenic tropospheric reactive gasses (emissions of NOx, CO, VOCs, CH4)                                                                                                 |                                          |       | 
|               | r[1-5]i1p312    | ODS             | emissions of CFCs                                                                                                                                                            |                                          |       |
|               | r[1-5]i1p313    | GHGnoCH4        |                                                                                                                                                                              | Schmidt2014 says access now              |       |
| GISS-E2-R [a] | r[1-5]i1p1      | **NoAIE**       | All forcings except aerosol indirect effects: "GHG, LU, Sl, Vl, BC, OC, SD, Oz (also includes orbital change - BC on snow - Nitrate aerosols - no aerosol indirect effects)" | NCI has data                             |       |
|               | r[1-5]1p102     | Sl              |                                                                                                                                                                              | NCI has data                             |       |
|               | r[1-5]1p103     | Vl              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]1p104     | LU              |                                                                                                                                                                              | NCI has data                             |       |
|               | r[1-5]1p105     | Oz              |                                                                                                                                                                              | NCI has data                             |       |
|               | r[1-5]1p106     | **AA-direct**   | Anthropogenic tropospheric aerosol: direct effect only (via concentration)                                                                                                   | Need to download from modelling group    |       |  
|               | r[1-5]1p107     | **AA**          | Anthropogenic tropospheric aerosol: direct and indirect effect only (via concentration)                                                                                      | Need to download from modelling group    |       |
|               | r[1-5]1p108     | BCsnow          |                                                                                                                                                                              | Schmidt2014 says access now                                    |       |
|               | r[1-5]1p109     | Ant             |                                                                                                                                                                              |                                          |       |
|               | r[1-5]1p302     | Sl              |                                                                                                                                                                              | Need to download from modelling group    |       |
|               | r[1-5]1p303     | Vl              |                                                                                                                                                                              |                                          |       |
|               | r[1-5]1p309     | Ant             |                                                                                                                                                                              | Need to download from modelling group    |       |
|               | r[1-5]1p310     | **AA**          | Anthropogenic tropospheric aerosol via emissions of SO2, BC, OC, NH3  (i.e. forced by emissions, not concentrations)                                                         | Need to download from modelling group    |       |
|               | r[1-5]1p311     | SLG             | Anthropogenic tropospheric reactive gasses (emissions of NOx, CO, VOCs, CH4)                                                                                                 |                                          |       | 
|               | r[1-5]1p312     | ODS             | emissions of CFCs                                                                                                                                                            |                                          |       |
|               | r[1-5]1p313     | GHGnoCH4        |                                                                                                                                                                              |                                          |       |
| IPSL-CM5-LR   | r[1,3]i1p1      | noLU            |                                                                                                                                                                              |                                          |       | 
|               | r[1-3]i1p2      | Ant             |                                                                                                                                                                              | Contacted modelling group (? on ESGF at DKRZ) |       |
|               | r1i1p3          | **AA**          |                                                                                                                                                                              | Contacted modelling group (? on ESGF at DKRZ) |       |
|               | r[1-4]i1p4      | **noAA**        | "Nat,Ant,GHG,Oz,LU"                                                                                                                                                          | Contacted modelling group (? on ESGF at DKRZ) |       |
|               | r[1-5]i1p5      | noOz            |                                                                                                                                                                              |                                          |       |
|               | r[1-2]i1p6      | GHGSA           |                                                                                                                                                                              |                                          |       |
| NorESM1-M     | r1i1p1          | **AA**          | Aerosol forcing only                                                                                                                                                         | Contacted modelling group                |       |


a: For the GISS E2 models the p1xx anf p3xx are produced by model versions that differ in their treatment of aerosols and atmospheric chemistry (see [here](http://data.giss.nasa.gov/modelE/ar5/) for details) 
b: For this simulation the r and p values were accidentally reversed
c: For the CCSM4 and CESM1-CAM5 models all of the following are included in single forcing runs, but except for the species identified in the simulation shorthand column of the table, they are held fixed or cycled over the annual cycle consistent with 1850 values: GHG, Vl, Sl, LU SS Ds SD BC MD OC Oz and DMS-derived aerosols. Further information about the forcing included in various CCSM4 and CESM1-CAM5 model simulations is available at http://www.cesm.ucar.edu/CMIP5/forcing_information

NCI also has atmospheric historicalMisc data for the BNU-ESM model, which isn't listed by Schmidt2014

#### Branch times

| Model          | ocean grid      | branch time |       
| ---            | ---             | ---         |                                          
| CanESM2        | regular lat/lon | Correct in metadata (171915 for historical and 1pctCO2 experiments) | 
| CCSM4          | curvilinear     | Wrong in metadata. Correct is 342005 for historical), 91615 for 1pctCO2: see http://www.cesm.ucar.edu/CMIP5/errata/branch_times.html |                                                
| CSIRO-Mk3-6-0  | regular lat/lon | 29200 (historical), which is correct in most but not all metadata. (For rndt you need to start at year 220 to avoid step change in control.) 37595 for 1pctCO2. |                                                               
| FGOALS-g2      | rotated pole?   | 175382.5 (visual estimate) |                                                           
| GFDL-CM3       | rotated pole    | Correct in metadata |
| GFDL-ESM2M     | rotated pole    | Correct in metadata |                                                            
| GISS-E2-H (p1) | regular lat/lon | Time gap in control data. After removing data prior to year 2410, branch time is zero. (For OHC you need to start at year 2650 to avoid step change in control.) |                                                             
| GISS-E2-H (p3) | regular lat/lon | Time gap in control data. After removing data prior to year 2490, branch time is zero. |                                                               
| GISS-E2-R (p1) | regular lat/lon | Time gap in control data. After removing data prior to year 3981, branch time is zero. (For historical and 1pctCO2.) |                                                             
| GISS-E2-R (p3) | regular lat/lon | Time gap in control data. After removing data prior to year 3560, branch time is zero. |                                                               
| IPSL-CM5-LR    | curvilinear?    | Correct in metadata (for hfds must start at year 2370 due to missing hfls data). |           
| NorESM1-M      | curvilinear     | Correct in metadata (255151 for historical and piControl) |


#### Ocean model

Model details from [Huang and Qiao (2015)](https://link.springer.com/article/10.1007/s13131-015-0631-x).

| Model          | ocean model     |  ocean grid     | ocean model details |       
| ---            | ---             | ---             | ---                 |  
| ACCESS1-0      | MOM4.1          |                 | BO, FS, FWF (Bi et al., 2013) |
| ACCESS1-3      | MOM4.1          |                 | BO, FS, FWF (Bi et al., 2013) |
| BCC-CSM1-1     |                 |                 | BO, FS, FWF (Griffies et al., 2005) |
| BCC-CSM1-1-m   |                 |                 | BO, FS, FWF (Griffies et al., 2005) |
| CanESM2        |                 | regular lat/lon | BO, RL, VSF (Merryfield et al., 2013) |
| CCSM4          |                 | curvilinear     | BO, FS, VSF (Danabasoglu et al., 2012) |
| CESM1-BGC      |                 |                 | BO, FS, VSF (Danabasoglu et al., 2012) |
| [CMCC-CM](https://www.cmcc.it/models/cmcc-cm) | OPA8.2 | | BO, FS, FWF [(Fogli et al., 2009)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1517282) |
| [CMCC-CMS](https://www.cmcc.it/models/cmcc-cm) | OPA8.2 | | BO, FS, FWF [(Fogli et al., 2009)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1517282) |
| CSIRO-Mk3-6-0  |                 | regular lat/lon | BO, RL, VSF (Gordon et al., 2010) |
| FGOALS-g2      |                 | rotated pole?   | BO, FS, FWF (Li et al., 2013) |
| GFDL-CM3       |                 | rotated pole    | BO, FS, FWF (Griffies et al., 2011) |
| GFDL-ESM2G     |                 |                 | BO, FS, FWF (Dunne et al., 2012) |
| GFDL-ESM2M     |                 | rotated pole    | BO, FS, FWF (Dunne et al., 2012) |
| GISS-E2-R      |                 | regular lat/lon | NB, FS, FWF (Liu et al., 2003) |
| GISS-E2-R-CC   |                 |                 | NB, FS, FWF (Liu et al., 2003) |
| IPSL-CM5A-LR   |                 |                 | BO, FS, FWF (Dufresne et al., 2013) |
| IPSL-CM5A-MR   |                 |                 | BO, FS, FWF (Dufresne et al., 2013) |
| IPSL-CM5B-LR   |                 |                 | BO, FS, FWF (Dufresne et al., 2013) |
| MIROC-ESM      |                 |                 | BO, FS, FWF (Watanable et al., 2011) |
| MPI-ESM-LR     |                 |                 | BO, FS, FWF (Jungclaus et al., 2013) |
| MPI-ESM-MR     |                 |                 | BO, FS, FWF (Jungclaus et al., 2013) |
| MRI-CGCM3      |                 |                 | BO, FS, FWF (Yukimoto et al., 2012) |
| NorESM1-M      |                 | curvilinear     | NB, FS, VSF (Bentsen et al., 2012) |
| NorESM1-ME     |                 |                 | NB, FS, VSF (Bentsen et al., 2012) |

BO = Boussinesq; NB = non-Boussinesq  
FS = free surface; RL = rigid lid  
FWF = freshwater flux; VSF = virtual salt flux


### Data issues

#### CanESM2

* Bad volcello data

#### CCSM4

* Bad volcello data
* Some of the CCSM4 piControl sea water salinity data files have units g/kg (as they should), while others (for the same run) have kg/kg (or 1).
* For the CCSM4 model, r6i1p10 of historicalMisc only goes to 1999 (instead of 2005) and there are other experiments (e.g. historicalGHG) where some runs start at 1851 and others at 1850  
* Some of the historicalMisc (r1i1p10) monthly thetao data files have random zeros in places (in the 1860, 1910, 1920 and 1930 files)

#### CSIRO-Mk3-6-0

* In the CSIRO-Mk3-6-0 rcp85 (and probably other experiments) hfbasin data the position of the "global ocean" and "indian pacific ocean" regions are mislabelled. The "global ocean" data is the last of the three regions (i.e. Python index -1 or 2) and "indian pacific ocean" is the middle. 

#### FGOALS-g2

* The time axis units in the FGOALS-g2 data is `days since 0001-01`. The lack of a day specifier causes problems with time related operations in Iris. 

#### GFDL-ESM2M

* For the GFDL-ESM2M historical and historicalAA (r1i1p5) experiments, the parent experiment is listed as historicalMisc when it should be piControl  

#### GISS-E2-H and GISS-E2-R 

* Bad volcello data for GISS-E2-R
* For the GISS-E2-H and GISS-E2-R models, the sea surface salinity (sos) and sea surface temperature (tos) data is on the atmospheric grid rather than the oceanic. This means you need to use areacella instead of areacello.  
* For the GISS-E2-R model (haven't checked E2-H), the ocean surface variables that are on the ocean grid (e.g. hfds, areacello) are missing their land mask (zeros instead of the fill value have been used)
* The Southern Ocean extends a long way north in the GISS-E2-R basin file, so don't use it.  
* The theato, r1i1p1 (haven't checked other variables/runs) piControl data is missing some files. It jumps from 363012 to 398101. The historical data branches at 398101.  
* For the GISS-E2-R model the branch time corresponds to the branch year, not the days since... 

#### IPSL-CM5A-LR

* Bad volcello data

#### MIROC-ESM

* wfo wrong sign (I've only checked piControl, r1i1p1)

#### MIROC-ESM-CHEM

* wfo wrong sign (I've only checked piControl, r1i1p1)

#### NorESM1-M

* Bad volcello data

