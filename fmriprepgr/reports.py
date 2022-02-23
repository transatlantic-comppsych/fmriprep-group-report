import os
from shutil import copytree
import re
import json
from pathlib import Path
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from bs4.element import Tag
import click
from bids import BIDSLayout
from bids.tests import get_test_data_path
from ._html_snippets import _generate_html_head, html_foot, reviewer_initials, nav
from ._svg_edit import _flip_images, _drop_image
layout = BIDSLayout(Path(get_test_data_path()) / 'synthetic')

def parse_report(report_path):
    """
    Parse an fmriprep report and return a dataframe with one row per image.
    Parameters
    ----------
    report_path : str
        Path to an existing fmriprep report html

    Returns
    -------
    report_elements : Pandas.DataFrame
        DataFrame of the images in the report and parsable metadata about those.
    """
    report_path = Path(report_path)
    # create a nested data structure from an html report
    soup = BeautifulSoup(report_path.read_text(), 'html.parser')
    file_divs = soup.findAll(attrs={'class':'svg-reportlet'})
    # we're going to build a dataframe called report elements by
    # appending row dictionaries to this list
    report_elements = []
    # default the previous run title to Nan
    prev_run_title = np.nan
    for fd in file_divs:
        fig_path = fd.get('src', fd.get('data'))
        # initialize the
        row = layout.parse_file_entities(fig_path, config=['bids', 'derivatives'])
        row['path'] = fig_path
        row['filename'] = Path(fig_path).parts[-1]
        elem_identifier = f"Parent div of {fig_path}"

        # Run titles should be hierarchical, if the current object doesn't have one
        # then it should be ok to use the previous one
        run_titles = fd.parent.findAll("h3", attrs={"class": "run-title"})
        try:
            # validation may be a better name than retrieval
            row['run_title'] = _unique_retrieval(run_titles, elem_identifier, 'run-title')
            prev_run_title = row['run_title']
        except ValueError:
            row['run_title'] = prev_run_title

        # Some elements aren't in divs so the parent returns the whole document
        # in this case, loop through previous elements till we find one with an elem-caption class
        try:
            elem_captions = fd.parent.findAll("p", attrs={"class": "elem-caption"})
            row['elem_caption'] = _unique_retrieval(elem_captions, elem_identifier, 'elem-caption')
        except ValueError:
            for prev in fd.previous_siblings:
                if isinstance(prev, Tag) and prev.has_attr('class') and prev.get('class', '') == 'elem-caption':
                    row['elem_caption'] = prev.text

        report_elements.append(row)
    report_elements = pd.DataFrame(report_elements)
    # make a report type column, in general, this will just be the desc field, but some images don't have that
    report_elements['report_type'] = report_elements.desc
    dseg_ind = report_elements.report_type.isnull() & (report_elements.suffix == 'dseg')
    report_elements.loc[dseg_ind, 'report_type'] = report_elements.loc[dseg_ind, 'suffix']
    if 'space' in report_elements.columns:
        t1w_ind = report_elements.report_type.isnull() & report_elements.space.notnull()
        report_elements.loc[t1w_ind, 'report_type'] = report_elements.loc[t1w_ind, 'space']

    # get fmriprep version from the fmriprep html report
    li_text = []
    for ultag in soup.find_all('div', {'id': 'About'}):
        for litag in ultag.find_all('li'):
            li_text.append(litag.text)

    # Get only the numbers for the fmriprep version
    for li in li_text:
        re_match = re.findall(r'fMRIPrep version: .*', li)
        if re_match:
            fmriprep_version = re_match[0].strip('fMRIPrep version: ')

    # Check that the fmriprep version on the html report is the same as the dataset_description.
    fmriprep_root = report_path.parent
    dataset_description = fmriprep_root / 'dataset_description.json'
    if dataset_description.exists():
        with open(dataset_description) as handle:
            description = json.load(handle)
            description_fmriprep = description['GeneratedBy'][0]['Version']
    try:
        description_fmriprep == fmriprep_version
    except ValueError:
        print('The versions of fmriprep on the dataset_decription.json and the html report do not match. Check your fmriprep run.')

    return report_elements, fmriprep_version


def _unique_retrieval(element_list, elem_identifier, search_identifier):
    """
    Get the text from a ResultSet that is expected to have a length of 1.
    Parameters
    ----------
    element_list :  bs4.element.ResultSet
        Result of a `findAll`
    elem_identifier : str
        An identifier for the element being searched, used in error messages.
    search_identifier : str
        An identifier for the thing being searched for, used in error messages.
    Returns
    -------
    str
        Text for the single matching element if one was found.
    """
    if len(element_list) > 1:
        raise ValueError(f"{elem_identifier} has more than one {search_identifier}.")
    elif len(element_list) == 0:
        raise ValueError(f"{elem_identifier} has no {search_identifier}.")
    else:
        return element_list[0].text


def _make_report_snippet(row):
    """
    Make a report snippet from a row generated by parse report.
    Parameters
    ----------
    row : dict
        Dictionary of report metadata for an svg from an fmriprep report.

    Returns
    -------
    snippet : str
        HTML snippet for the report image.
    """
    id_blacklist = ['path', 'run_title', 'elem_caption', 'extension', 'filename']
    header_blacklist = id_blacklist + ['desc', 'report_type', 'idx', 'chunk']
    id_ents = {k:v for k,v in row.items() if k not in id_blacklist}
    # needed for scripting to update counts as you scroll around
    id_ents['been_on_screen'] = False
    id_ents['rater'] = np.NaN
    id_ents['report'] = np.NaN
    id_ents['note'] = np.NaN
    header_ents = {k:v for k,v in row.items() if k not in header_blacklist}

    # TODO: make this header a path to the relevant image
    header_vals = [f'{k} <span class="bids-entity">{v}</span>' for k,v in header_ents.items() if pd.notnull(v)]
    header = f" <h2>idx-{row['idx']}: " + ', '.join(header_vals) + "</h2>"
    snippet = f"""
    <div id="id-{row['idx']}_filename-{row['filename'].split('.')[0]}">
      <script type="text/javascript">
        var subj_qc = {json.dumps(id_ents)}
      </script>
      {header}
      <div class="radio">
        <label><input type="radio" name="inlineRadio{row['idx']}" id="inlineRating1" value="1" onclick="qc_update({row['idx']}, 'report', this.value)"> Good </label>
        <label><input type="radio" name="inlineRadio{row['idx']}" id="inlineRating0" value="0" onclick="qc_update({row['idx']}, 'report', this.value)"> Bad</label>
      </div>
      <p> Notes: <input type="text" id="box{row['idx']}" oninput="qc_update({row['idx']}, 'note', this.value)"></p>
      <object class="svg-reportlet" type="image/svg+xml" data="{row['path']}"> </object>
    </div>
    <script type="text/javascript">
      subj_qc["report"] = -1
      subjs.push(subj_qc)
    </script>
    """
    return snippet


@click.command()
@click.option('--reports_per_page', default=50,
              help='How many figures per page. If None, then put them all on a single page.')
@click.option('--path_to_figures', default=None,
              help="Relative path from group/sub-{subject} to subject's figure directory."
                   " If None, infer from report location.")
@click.option('--flip_images', '-f', default=(), multiple=True,
              help="The names of any report subsections where you want to flip which image is shown when mousing over."
                   " Can be passed multiple times to specify multiple subsections.")
@click.option('--drop_background', default=(), multiple=True,
              help="The names of any report subsections where you want to drop the image that shows before mousing over"
                   " and just see the image that's shown when mousing over. Can be passed multiple times to specify"
                   " multiple subsections.")
@click.option('--drop_foreground', default=(), multiple=True,
              help="The names of any report subsections where you want to drop the image that shows after mousing over"
                   " and just see the image that's shown before mousing over. Can be passed multiple times to specify"
                   " multiple subsections.")
@click.argument('fmriprep_output_path')
def make_report(fmriprep_output_path, reports_per_page=50, path_to_figures=None,
                flip_images=(), drop_background=(), drop_foreground=()):
    """
    Make a consolidated report from an fMRIPrep output directory. Optionally, you can also tweak the images in the
     reports. Using flip_images, drop_background, or drop_foreground will mean that images are copied to the group
     report directory instead of being symlinked so that the original figures are not modified. Each report type can
     only be modified in a single way.
    """
    fmriprep_output_path = Path(fmriprep_output_path)

    # Assuming this is what the fmriprep directory (for fmriprep versions > 21.0.0) looks like before running
    # fmriprep group report
    """
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
    """
    # The new group directory created will look like this
    """
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
    """

    # One of the changes of fmriprep 21.0.0 compared to the previous versions is that it now consolidates the figures
    # output at the subject level. So all figures are located in a single figure folder, this is not true for the
    # previous fmriprep version. Therefore, for older versions of fmriprep (< 21.0.0) the fmriprep directory should
    # look like this
    """
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
    """
    # The new group directory created will look like this
    """
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
    """

    # check to see if we're symlinking or copying
    if len(flip_images) == 0 and len(drop_background) == 0 and len(drop_foreground) == 0:
        image_changes = False
    else:
        image_changes = True
        flip_images = set(flip_images)
        drop_background = set(drop_background)
        drop_foreground = set(drop_foreground)
        if not flip_images.isdisjoint(drop_foreground):
            intersection = flip_images.intersection(drop_foreground)
            raise ValueError(f"Each report type may only be modified in a single way. {intersection} is specified for "
                             f"both flip_images and drop_foreground.")
        if not flip_images.isdisjoint(drop_background):
            intersection = flip_images.intersection(drop_background)
            raise ValueError(f"Each report type may only be modified in a single way. {intersection} is specified for "
                             f"both flip_images and drop_background.")
        if not drop_foreground.isdisjoint(drop_background):
            intersection = drop_foreground.intersection(drop_background)
            raise ValueError(f"Each report type may only be modified in a single way. {intersection} is specified for "
                             f"both drop_foreground and drop_background.")



    group_dir = fmriprep_output_path / 'group'
    group_dir.mkdir(exist_ok=True)
    # write parameters
    params = {'fmriprep_output_path': fmriprep_output_path.as_posix(),
              'reports_per_page': reports_per_page,
              'path_to_figures': path_to_figures,
              'flip_images': list(flip_images),
              'drop_background': list(drop_background),
              'drop_foreground': list(drop_foreground)}
    try:
        bids_version = json.loads((fmriprep_output_path / 'dataset_description.json').read_text())['BIDSVersion']
    except: # I know a naked except is generally bad, but I don't ever want a failure here to stop execution.
        bids_version = 'unknown'
    dataset_description = {
        'Name': 'fMRIPrep-Group-Report output',
        'BIDSVersion': bids_version,
        'DatasetType': 'derivative',
        'GeneratedBy': [
            {
                'Name': 'fMRIPrep-Group-Report',
                'CodeURL': "https://github.com/nimh-comppsych/fmriprep-group-report",
                'Parameters': params,
            }
        ]
    }
    (group_dir / 'dataset_description.json').write_text(json.dumps(dataset_description, indent=2))
    # parse all the subject reports
    all_htmls_paths = sorted(fmriprep_output_path.glob('**/sub-*.html'))
    # Older versions of fmriprep (e.g., 20.2.2) have multiple sub-*.html. So, we want to the select only the sub-xx.html
    # file without having to hardcode the fmriprep directory structure and subject ID.
    report_paths = []
    for html in all_htmls_paths:
        if layout.parse_file_entities(html)['suffix'] == layout.parse_file_entities(html)['subject']:
            report_paths.append(html)
    if not report_paths:
        FileNotFoundError("No sub-{participant_ID}.html file was found. Please check if there are any sub-{participant_ID}.html"
                          "on the provided fmriprep output directory.")
    reports = []
    for report_idx, report_path in enumerate(report_paths):
        if not 'figures' in report_path.parts:
            report, fmriprep_version = parse_report(report_path)
            reports.append(report)

            # symlink figures directory into place
            subject = layout.parse_file_entities(report_path)['subject']
            subj_group_dir = group_dir / f'sub-{subject}'
            subj_group_dir.mkdir(exist_ok=True)

            orig_fig_dirs = []
            if path_to_figures is None:

                # check the fmriprep version and if there are multiple sessions. If only one session is available,
                # the behavior is similar to fmriprep_version > 21.0.0
                if (fmriprep_version < '21.0.0') and ('session' in reports[report_idx]):

                    sessions = reports[report_idx]['session'].unique()
                    # drop the nan session
                    sessions = [session for session in sessions if str(session) != 'nan']
                    expected_subj_fig_dirs = [report_path.parent / f'sub-{subject}' / f'ses-{session}' / 'figures'
                                              for session in sessions]
                    # Create session folders
                    group_session_dirs = [subj_group_dir / f'ses-{session}' for session in sessions]
                    for group_session_dir in group_session_dirs:
                        group_session_dir.mkdir(exist_ok=True)
                    # append 'figures' folders as the consolidated report expect all figures to be inside a figures folder
                    subj_group_fig_dirs = [group_session_dir / 'figures' for group_session_dir in group_session_dirs]
                    # append the figures folder
                    expected_subj_fig_dirs.append(report_path.parent / f'sub-{subject}' / 'figures')
                    subj_group_fig_dirs.append(subj_group_dir / 'figures')

                else:
                    expected_subj_fig_dirs = [report_path.parent / f'sub-{subject}' / 'figures']
                    subj_group_fig_dirs = [subj_group_dir / 'figures']
                for expected_subj_idx, expected_subj_fig_dir in enumerate(expected_subj_fig_dirs):
                    if not expected_subj_fig_dir.exists():
                        FileNotFoundError(f"path_to_figures was not specified and the subject figures dir for sub-{subject}"
                                          " was not at the expected location: {expected_subj_fig_dir}. Please use "
                                          " path_to_figures to specify the correct relative path from the group dir to the"
                                          " subject figures directory.")
                    # I don't like any of the relative path tools in python
                    # To get the relative path I want I've got to start from a place on the common path of
                    # expected_subj_fig_dir, which should be the fmriprep_output_path
                    good_parts = list(expected_subj_fig_dir.relative_to(fmriprep_output_path).parts)
                    # figure out how many levels down the subj_group_fig_dir is (should be 2, for fmriprep >= 21.0.0
                    # and 3 otherwise).
                    lvls_down = len(subj_group_fig_dirs[expected_subj_idx].relative_to(fmriprep_output_path).parts) - 1
                    # assemble the path parts into a list
                    path_parts = (['..'] * lvls_down + good_parts)
                    # join them with os.path.join
                    orig_fig_dirs.append(Path(os.path.join(*path_parts)))

                    if subj_group_fig_dirs[expected_subj_idx].is_symlink() or \
                       subj_group_fig_dirs[expected_subj_idx].exists():
                        raise ValueError(
                            f"{subj_group_fig_dirs[expected_subj_idx]} exists and would be overwritten. "
                            f"Rename or delete the existing group directory before running fmriprepgr.")

            else:
                orig_fig_dirs = [path_to_figures.format(subject=subject)]
                for orig_fig_idx, orig_fig_dir in enumerate(orig_fig_dirs):
                    if not (subj_group_dir / orig_fig_dir).exists():
                        raise ValueError(f"path_to_figures is not correct. Based on {path_to_figures}, "
                                         f"{subj_group_fig_dirs[orig_fig_idx] / orig_fig_dir} should exist, but it doesn't.")

            for orig_fig_idx, orig_fig_dir in enumerate(orig_fig_dirs):
                if image_changes:
                    copytree(subj_group_fig_dirs[orig_fig_idx].parent / orig_fig_dir, subj_group_fig_dirs[orig_fig_idx])
                else:
                    subj_group_fig_dirs[orig_fig_idx].symlink_to(orig_fig_dir, target_is_directory=True)

    reports = pd.concat(reports).reset_index(drop=True)

    # make a consolidated report for each report type
    for report_type, rtdf in reports.groupby('report_type'):
        rtdf = rtdf.copy().reset_index(drop=True)
        rtdf = rtdf.reset_index().rename(columns={'index': 'idx'})

        # deal with image changes
        if image_changes:
            if (report_type in flip_images) or (report_type in drop_foreground) or (report_type in drop_background):
                for ix, row in rtdf.iterrows():
                    if fmriprep_version < '21.0.0':
                        if row['session']:
                            subj_group_dir = group_dir / f'sub-{row.subject}' / f'ses-{row.session}' / 'figures'
                        else:
                            subj_group_dir = group_dir / f'sub-{row.subject}' / 'figures'
                    else:
                        subj_group_dir = group_dir / f'sub-{row.subject}' / 'figures'
                    image_path = subj_group_dir / row.filename
                    if (not image_path.exists()):
                        raise FileNotFoundError(f"Something's gone wrong, {image_path} doesn't exist, but should.")
                    if image_path.is_symlink():
                        raise ValueError(f"Something's gone wrong, {image_path} is a symlink, but should have been "
                                         f"copied.")
                    if report_type in flip_images:
                        _flip_images(image_path, image_path)
                    elif report_type in drop_foreground:
                        _drop_image(image_path, image_path, "foreground")
                    elif report_type in drop_background:
                        _drop_image(image_path, image_path, "background")

        if reports_per_page is None:
            rtdf['chunk'] = 0
        else:
            rtdf['chunk'] = rtdf.idx // reports_per_page
        for chunk, cdf in rtdf.groupby('chunk'):
            consolidated_path = group_dir / f'consolidated_{report_type}_{chunk:03d}.html'
            dl_file_name =  f'consolidated_{report_type}_{chunk:03d}.tsv'
            cdf = cdf.reset_index(drop=True).reset_index().drop('idx', axis=1).rename(columns={'index': 'idx'})
            lines = '\n'.join([_make_report_snippet(row) for row in cdf.to_dict('records')])

            rpt_text = '\n'.join([_generate_html_head(dl_file_name),
                                  nav,
                                  reviewer_initials,
                                  lines,
                                  html_foot])
            consolidated_path.write_text(rpt_text)

