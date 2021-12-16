# FMRIPrep Group Report
[![Run Python Tests](https://github.com/nimh-comppsych/fmriprep-group-report/actions/workflows/ci.yml/badge.svg)](https://github.com/nimh-comppsych/fmriprep-group-report/actions/workflows/ci.yml)  
Fmriprep produces a bunch of subject level reports and each subject level report has many sub-reports. 
I've found it's easier to review things if all of the sub-reports of a given type are consolidated into a single page. 
This package will make a set of consolidated reports from an fmriprep output directory.

## How to install:
Clone the repo and pip install it. Will be on pypi once I've recovered my account.

## How to run:
`fmriprepgr [path to fmriprep output directory]`

## Options: 
--reports_per_page: How many sub-reports do you want on each page? Default is 50. 
Set to None if you want all reports on a single page  
--path_to_figures: The group reports are output to 
`[path to fmriprep output directory]/group`. 
In order to keep from wasting disk space by copying figures, figures directory for each subject are symlinked from
`[path to fmriprep output directory]/group/sub-[subject]/figures` to the appropriate location.
By default, this should be `../../sub-{subject}/figures`, but if you've laid out your fmriprep output differently
change this option to get the symlinks working.
