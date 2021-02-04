### Links

* CLEX CMS wiki: http://climate-cms.wikis.unsw.edu.au/Home 
* NCI CMIP community page: https://opus.nci.org.au/display/CMIP/CMIP+Community+Home
* NCI Data Training Page: https://nci-data-training.readthedocs.io/en/latest/index.html
* NCI data catalogue (only high level info on CMIP, there are better alternatives): https://geonetwork.nci.org.au/

### Help

* Website: https://track.nci.org.au/servicedesk/customer/portals
* Email: cws_help@nci.org.au (i.e. CMS team) or help@nci.org.au (general NCI help)
* Slack: https://arccss.slack.com
* Request access to different projects here: https://my.nci.org.au/mancini/

### CWS Virtual Desktop

[VDI User Guide](https://opus.nci.org.au/display/Help/VDI+User+Guide)

#### Access requirements

1. An NCI login with access to compute and storage resources
   
  * username: dbi599
  * compute/storage: I'm on r87 project, which means I should write to `/local/r87/dbi599/tmp`
    * Can also write to `/g/data/r87/dbi599`

2. A client application that enables connection using the secure shell protocol and a VNC client application
 
  * VNC client = TurboVNC  
  * Desktop launcher = Strudel  
  * Instructions: https://docs.google.com/document/d/1qx_BSd-WRSGW05_ZqSWt7bxxe3beCBrDIv9Nv6kB0QE/edit  
  
### Software solution

Install miniconda at `/g/data/r87/dbi599` and use conda environments.

### Version control

Need to use ssh (not https) when cloning.  
  
The following seems to help with a `git push ERROR: Permission to git denied to deploy key`:  
```
eval "$(ssh-agent -s)"  
ssh-add ~/.ssh/id_rsa_nci_virtuallab
``` 

### Moving files to local computer  

```
$ scp dbi599@gadi.nci.org.au:/g/data/r87/dbi599/figures/tauuo-zm/* .
```
If you want to transfer a file from the VDIs,
replace `gadi` with the output from `$ hostname` (e.g. `vdi-n1`).
  
### Creating symlinks

To create a new symlink (will fail if symlink exists already):  
```
ln -s /path/to/file /path/to/symlink
```   

To create or update a symlink:  
```
ln -sf /path/to/file /path/to/symlink
```  

### Queuing system (on Gadi or Raijin)

To submit to the queue, run `qsub job.txt` where:
```
$ cat job.txt

#!/bin/bash
#PBS -P r87
#PBS -q normal
#PBS -l walltime=02:00:00
#PBS -l storage=gdata/r87+gdata/oi10
#PBS -l mem=60GB
#PBS -l wd

command...

```
Use `qstat -u dbi599 -sw` to check status of jobs (job state definitions [here](https://www.jlab.org/hpc/PBS/qstat.html)) and `qdel <jobid>` to kill one.

For large memory, single core jobs it's better to submit to the `hugemem` instead of `normal` queue. 
  
