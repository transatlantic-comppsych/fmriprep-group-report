# FMRIPrep Group Report
[![Run Python Tests](https://github.com/nimh-comppsych/fmriprep-group-report/actions/workflows/ci.yml/badge.svg)](https://github.com/nimh-comppsych/fmriprep-group-report/actions/workflows/ci.yml)  
Fmriprep produces a bunch of subject level reports and each subject level report has many sub-reports. 
I've found it's easier to review things if all of the sub-reports of a given type are consolidated into a single page. 
This package will make a set of consolidated reports from an fmriprep output directory.

## How to install:
`pip install fmriprep-group-report`  

## How to run:
`fmriprepgr [path to fmriprep output directory]`

## Options: 
--reports_per_page: How many sub-reports do you want on each page? Default is 50. 
Set to None if you want all reports on a single page  
--path_to_figures: if your fmriprep directories are laid out in a non-standard way, you'll need to use this to specify
the correct relative path. See paths discussion below.

## Paths
You probably won't have to worry about this. Try it once and see if it's worked, if you get an error mentioning 
path_to_figures, then the solution might be here.
I assume that the html reports are at the same level as the subject results directory,
and that the figures directory are at the top level with each subject level report directory. like so:
```commandline
    fmriprep
        ├── dataset_description.json
        ├── desc-aparcaseg_dseg.tsv
        ├── desc-aseg_dseg.tsv
        ├── logs
        │    └── ...
        ├── sub-20900
        │    └── anat
        │         └── ...
        │    └── figures
        │         ├── sub-20900_acq-mprage_rec-prenorm_run-1_desc-reconall_T1w.svg
        │         └── ...
        │    └── ses-v1
        │         └── anat
        │              └── ...
        │         └── func
        │              └── ...
        │    └── ses-v2
        │         └── anat
        │              └── ...
        │         └── func
        │              └── ...
        ├── sub-20900.html
        ├── sub-22293
        │    └── anat
        │         └── ...
        │     └── figures
        │         ├── sub-22293_acq-mprage_rec-prenorm_run-1_desc-reconall_T1w.svg
        │         └── ...
        │    └── ses-v1
        │         └── anat
        │              └── ...
        │         └── func
        │              └── ...
        │    └── ses-v2
        │         └── anat
        │              └── ...
        │         └── func
        │              └── ...
        ├── sub-22293.html
        └── ...
```
Once the code is run, the group directory will be added with symlinks to figures directories so it doesn't waste space 
on disk, but can be rsynced relatively easily to another location with `-L`. This will look like this:
```commandline
    fmriprep
        ├── group
        │   ├── consolidated_dseg_000.html
        │   ├── consolidated_MNI152NLin2009cAsym_000.html
        │   ├── consolidated_MNI152NLin6Asym_000.html
        │   ├── consolidated_pepolar_000.html
        │   ├── consolidated_reconall_000.html
        │   ├── sub-20900
        │   │   └── figures -> ../../sub-20900/figures
        │   └── sub-22293
        │       └── figures -> ../../sub-22293/figures
        └── ...
```
I use the location of the report.htmls to figure out the relative paths to the figures directory. 
If figures aren't located `./sub-{subject}/figures` relative to the directory that contains `sub-{subject}.html`, 
then you'll need to provide the format for the figure symlinks in the path_to_figures option. For example if your directory
looks like this:
```commandline
    fmriprep
        ├── dataset_description.json
        ├── desc-aparcaseg_dseg.tsv
        ├── desc-aseg_dseg.tsv
        ├── logs
        │    └── ...
        ├── fmriprep
        │    └── sub-20900
        │       └── anat
        │           └── ...
        │       └── figures
        │            ├── sub-20900_acq-mprage_rec-prenorm_run-1_desc-reconall_T1w.svg
        │            └── ...
        │       └── ses-v1
        │             └── anat
        │                  └── ...
        │             └── func
        │                   └── ...
        │       └── ses-v2
        │           └── anat
        │              └── ...
        │         └── func
        │              └── ...
        ├── sub-20900.html
        └── ...
```
Then you'll need the output to look like this:
```commandline
    fmriprep
        ├── group
        │   ├── consolidated_dseg_000.html
        │   ├── consolidated_MNI152NLin2009cAsym_000.html
        │   ├── consolidated_MNI152NLin6Asym_000.html
        │   ├── consolidated_pepolar_000.html
        │   ├── consolidated_reconall_000.html
        │   ├── sub-20900
        │   │   └── figures -> ../../fmriprep/sub-20900/figures
        │   └── sub-22293
        │       └── figures -> ../../fmriprep/sub-22293/figures
        └── ...
```
So you'll need to set `path_to_figures` to `'../../fmriprep/sub-{subject}/figures''`. 