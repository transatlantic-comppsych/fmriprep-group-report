# FMRIPrep Group Report
[![Run Python Tests](https://github.com/nimh-comppsych/fmriprep-group-report/actions/workflows/ci.yml/badge.svg)](https://github.com/nimh-comppsych/fmriprep-group-report/actions/workflows/ci.yml)  
Fmriprep produces a bunch of subject level reports and each subject level report has many sub-reports. 
I've found it's easier to review things if all of the sub-reports of a given type are consolidated into a single page. 
Fmriprep produces a bunch of subject level reports ([like](https://nimh-comppsych.github.io/fmriprep-group-report/fmriprepgr/test/data/fmriprep/sub-20900.html) [this](https://nimh-comppsych.github.io/fmriprep-group-report//fmriprepgr/test/data/fmriprep/sub-22293.html)) and each subject level report has many sub-reports. 
I've found it's easier to review things if all of the sub-reports of a given type are consolidated into a single page ([like](https://nimh-comppsych.github.io/fmriprep-group-report/fmriprepgr/test/data/fmriprep/group/consolidated_dseg_000.html) [this](https://nimh-comppsych.github.io/fmriprep-group-report//fmriprepgr/test/data/fmriprep/group/consolidated_reconall_000.html)). The consolidated pages also let you perform the qc serverlessly on each page and download a csv of your ratings. 
This package will make a set of consolidated reports from an fmriprep (v21.0.0 or later) output directory.

## How to install:
`pip install fmriprep-group-report`  

## How to run:
`fmriprepgr [path to fmriprep output directory]`

## Options: 
--reports_per_page: How many sub-reports do you want on each page? Default is 50. 
Set to None if you want all reports on a single page  
--path_to_figures: If your fmriprep directories are laid out in a non-standard way, you'll need to use this to specify
the correct relative path. See paths discussion below.
### Image modification options
Some of the SVGs produced by fmriprep aren't setup in a way that facilitates bulk review. Here are some options to manipulate the SVGs. Note that if you use any of these options, all of the report SVGs will be copied instead of symlinked. For all of these options, pass it multiple times if there are multiple sub-reports with SVGs you want to modify.  
--flip_images:  Flip the background and foreground on SVGs that change when you mouse over. For example the registrations to standard space have the standard space image till you mouse over them. If you want to be able to quickly spot weirdness, it's easier to have the subject images appear first and the standard space images appear on mouse over. `--flip_images MNI152NLin6Asym` will flip the `MNI152NLin6Asym` registrations. If there's more than one you want to change, pass it twice: `--flip_images MNI152NLin6Asym --flip_images MNI152NLin2009cAsym`.  
--drop_background: Modify the SVGs for a given sub-report to drop the image that appears before mousing over.  
--drop_foreground: Modify the SVGs for a given sub-report to drop the image that appears after mousing over.

## Report features
Counts in the header tell you how many good (green), bad (red) and unreviewed images (yellow) remain on this page. You can enter your initials so that the reviewer identity will be saved in the csv when you download it.  
<img width="895" alt="header_example" src="https://user-images.githubusercontent.com/5289368/154523835-6a8f1e57-c8bb-4f03-b2be-012d5c9fd91b.png">

Each image has an index (idx-0 in this case), indicating which image on the page it is, which makes it much easier to find images that are problematic when you're reviewing someone else's QC. It can be rated as good or bad, and there's a free text field for notes.
<img width="897" alt="image_example" src="https://user-images.githubusercontent.com/5289368/154523867-9909f37f-1218-4d60-85a6-c7411d5d7096.png">

Finally, for those of you with hundreds of images to review, if the image is fine, you can just scroll past it, and it will be automatically marked as good.

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
