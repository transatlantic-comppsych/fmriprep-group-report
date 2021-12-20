from pathlib import Path
from shutil import copy, copytree
import numpy as np
import pandas as pd
from ..reports import _make_report_snippet, parse_report


def test_make_report_snippet():
    """
    Run `reports._make_report_snippet` and confirm that output is as expected by comparison to output previously stored
    in this function.
    Returns
    -------
    None
    """
    row = {'idx':0,
           'chunk':0,
           'subject': '22293',
           'acquisition': 'mprage',
           'reconstruction': 'prenorm',
           'run': 1,
           'suffix': 'dseg',
           'extension': '.svg',
           'path': './sub-22293/figures/sub-22293_acq-mprage_rec-prenorm_run-1_dseg.svg',
           'filename': 'sub-22293_acq-mprage_rec-prenorm_run-1_dseg.svg',
           'run_title': 'Brain mask and brain tissue segmentation of the T1w',
           'elem_caption': 'This panel shows the template T1-weighted image (if several T1w images were found), with contours delineating the detected brain mask and brain tissue segmentations.',
           'space': np.nan,
           'desc': np.nan,
           'session': np.nan,
           'task': np.nan,
           'report_type': 'dseg'}
    expected_output = ['<div id="id-0_filename-sub-22293_acq-mprage_rec-prenorm_run-1_dseg">',
                       '<script type="text/javascript">',
                       'var subj_qc = {"idx": 0, "chunk": 0, "subject": "22293", "acquisition": "mprage", "reconstruction": "prenorm", "run": 1, "suffix": "dseg", "space": NaN, "desc": NaN, "session": NaN, "task": NaN, "report_type": "dseg", "been_on_screen": false}',
                       '</script>',
                       '<h2> subject <span class="bids-entity">22293</span>, acquisition <span class="bids-entity">mprage</span>, reconstruction <span class="bids-entity">prenorm</span>, run <span class="bids-entity">1</span>, suffix <span class="bids-entity">dseg</span></h2>',
                       '<div class="radio">',
                       '<label><input type="radio" name="inlineRadio0" id="inlineRating1" value="1" onclick="qc_update(0, \'report\', this.value)"> Good </label>',
                       '<label><input type="radio" name="inlineRadio0" id="inlineRating0" value="0" onclick="qc_update(0, \'report\', this.value)"> Bad</label>',
                       '</div>',
                       '<p> Notes: <input type="text" id="box0" oninput="qc_update(0, \'note\', this.value)"></p>',
                       '<object class="svg-reportlet" type="image/svg+xml" data="./sub-22293/figures/sub-22293_acq-mprage_rec-prenorm_run-1_dseg.svg"> </object>',
                       '</div>',
                       '<script type="text/javascript">',
                       'subj_qc["report"] = -1',
                       'subjs.push(subj_qc)',
                       '</script>'
                       ]
    output = _make_report_snippet(row)
    output = [oo.strip() for oo in output.split('\n') if len(oo.strip()) > 0]
    assert np.all([aa == bb for aa,bb in zip(expected_output, output)])

def test_parse_report():
    """
    Run `reports.parse_report` on sub-20900test.html and confirm that output is as expected by comparison to previously
    saved output.
    Returns
    -------
    None
    """
    test_data_dir = Path(__file__).parent.resolve() / 'data'
    output = parse_report(test_data_dir / 'fmriprep/sub-20900.html')
    expected_output = pd.read_csv(test_data_dir / 'sub-20900test.csv')
    expected_output['subject'] = expected_output.subject.astype(str)
    assert expected_output.equals(output)

def test_fmriprepgr(tmp_path, script_runner):
    test_out_dir = tmp_path
    test_data_dir = Path(__file__).parent.resolve() / 'data/fmriprep'
    copytree(test_data_dir, test_out_dir / 'fmriprep')
    ret = script_runner.run('fmriprepgr', test_out_dir.as_posix())

    assert ret.success
    expected_out_dir = test_data_dir / 'group'
    out_dir = test_out_dir / 'group'
    expected_files = sorted(expected_out_dir.glob('*'))
    out_files = sorted(out_dir.glob('*'))
    expected_file_names = np.array([pp.parts[-1] for pp in expected_files])
    out_file_names = np.array([pp.parts[-1] for pp in out_files])
    assert (expected_file_names == out_file_names).all()
    # test that html files are generated correctly
    for of, ef in zip(out_files, expected_files):
        if ef.as_posix().split('.')[-1] == '.html':
            econtent = ef.read_text()
            ocontent = of.read_text()
            assert ocontent == econtent
    # test that links are valid
    out_links = sorted((out_dir / 'sub-20900' / 'figures').glob('*'))
    out_links += sorted((out_dir / 'sub-22293' / 'figures').glob('*'))
    for ll in out_links:
        assert ll.is_symlink()
        assert ll.resolve().exists()
