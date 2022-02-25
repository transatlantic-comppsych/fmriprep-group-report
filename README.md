# FMRIPrep Group Report
[![Run Python Tests](https://github.com/nimh-comppsych/fmriprep-group-report/actions/workflows/ci.yml/badge.svg)](https://github.com/nimh-comppsych/fmriprep-group-report/actions/workflows/ci.yml)  
Fmriprep produces a bunch of subject level reports and each subject level report has many sub-reports. 
I've found it's easier to review things if all of the sub-reports of a given type are consolidated into a single page. 
Fmriprep produces a bunch of subject level reports ([like](https://nimh-comppsych.github.io/fmriprep-group-report/fmriprepgr/test/data/fmriprep/sub-20900.html) [this](https://nimh-comppsych.github.io/fmriprep-group-report//fmriprepgr/test/data/fmriprep/sub-22293.html)) and each subject level report has many sub-reports. 
I've found it's easier to review things if all of the sub-reports of a given type are consolidated into a single page ([like](https://nimh-comppsych.github.io/fmriprep-group-report/fmriprepgr/test/data/fmriprep/group/consolidated_dseg_000.html) [this](https://nimh-comppsych.github.io/fmriprep-group-report//fmriprepgr/test/data/fmriprep/group/consolidated_reconall_000.html)). The consolidated pages also let you perform the qc serverlessly on each page and download a tsv of your ratings. 
This package will make a set of consolidated reports from a fmriprep output directory. In principle, if the provided 
fmriprep output directory follow any of the two path settings described on the [Paths](#paths) section below, the code should run for
any fmriprep version. Note, that we tested the code on fmriprep versions 21.0.0, 20.2.3, 20.0.6. 

## How to install:
`pip install fmriprep-group-report`  

## How to run:
`fmriprepgr [path to fmriprep output directory]`

## Options: 
--reports_per_page: How many sub-reports do you want on each page? Default is 50. 
Set to None if you want all reports on a single page  

### Image modification options
Some of the SVGs produced by fmriprep aren't setup in a way that facilitates bulk review. Here are some options to manipulate the SVGs. Note that if you use any of these options, all of the report SVGs will be copied instead of symlinked. For all of these options, pass it multiple times if there are multiple sub-reports with SVGs you want to modify.  
--flip_images:  Flip the background and foreground on SVGs that change when you mouse over. For example the registrations to standard space have the standard space image till you mouse over them. If you want to be able to quickly spot weirdness, it's easier to have the subject images appear first and the standard space images appear on mouse over. `--flip_images MNI152NLin6Asym` will flip the `MNI152NLin6Asym` registrations. If there's more than one you want to change, pass it twice: `--flip_images MNI152NLin6Asym --flip_images MNI152NLin2009cAsym`.  
--drop_background: Modify the SVGs for a given sub-report to drop the image that appears before mousing over.  
--drop_foreground: Modify the SVGs for a given sub-report to drop the image that appears after mousing over.

## Report features
Counts in the header tell you how many good (green), bad (red) and unreviewed images (yellow) remain on this page. You can enter your initials so that the reviewer identity will be saved in the tsv when you download it.
<img width="815" alt="header_example" src="https://user-images.githubusercontent.com/5289368/154563861-5acacec7-7587-485d-b92f-546e9dab5428.png">


Each image has an index (idx-0 in this case), indicating which image on the page it is, which makes it much easier to find images that are problematic when you're reviewing someone else's QC. It can be rated as good or bad, and there's a free text field for notes. Don't put commas in your notes though.
<img width="897" alt="image_example" src="https://user-images.githubusercontent.com/5289368/154523867-9909f37f-1218-4d60-85a6-c7411d5d7096.png">

Finally, for those of you with hundreds of images to review, if the image is fine, you can just scroll past it, and it will be automatically marked as good.

## Paths
This code assumes that the provided fmriprep output directory follows a specific structure; it assumes that the html reports are at the same level as the subject results directory,
and that the figures directory is at the top level with each subject level report directory as the location of the report.htmls to figure out the relative paths to the figures directory.
Because in older fmriprep versions the figures output have been consolidated into a single figure folder, I will describe the two expected fmriprep directories that the code can handle. 

### Consolidated figures folder
In this use case all figures are located inside a single figure folder under the subject's directory.
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

### Different sessions have separate figure folders
Older versions of fmriprep (e.g., 20.0.6) used to have separate figure folders for the different sessions
as following:
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
    │         └── figures
    │              └── ...
    │         └── func
    │              └── ...
    │    └── ses-v2
    │         └── anat
    │              └── ...
    │         └── figures
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
    │         └── figures
    │              └── ...
    │         └── func
    │              └── ...
    │    └── ses-v2
    │         └── anat
    │              └── ...
    │         └── figures
    │              └── ...
    │         └── func
    │              └── ...
    ├── sub-22293.html
    └── ...
```
When there are multiple figure directories, the code will copy/symlink them separately. The new group directory created will look like this
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
        │   │   └── ses-v1
        │   │   │    └── figures -> ../../sub-20900/ses-v1/figures
        │   │   └── ses-v2
        │   │       └── figures -> ../../sub-20900/ses-v2/figures
        │   └── sub-22293
        │   │   └── figures -> ../../sub-22293/figures
        │   │   └── ses-v1
        │   │   │    └── figures -> ../../sub-22293/ses-v1/figures
        │   │   └── ses-v2
        │   │       └── figures -> ../../sub-22293/ses-v2/figures
        └── ...
```