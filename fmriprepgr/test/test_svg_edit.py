from pathlib import Path
from .._svg_edit import _flip_images, _drop_image

def test_flip(tmp_path):
    orig_path = (Path(__file__).parent.resolve()
                 / 'data/svg_edit/sub-22293_acq-mprage_rec-prenorm_run-1_space-MNI152NLin6Asym_T1w.svg')
    new_path = tmp_path / 'flipped.svg'
    expected_path = (Path(__file__).parent.resolve()
                 / 'data/svg_edit/sub-22293_acq-mprage_rec-prenorm_run-1_space-MNI152NLin6Asym_T1w_flipped.svg')
    _flip_images(orig_path, new_path)
    expected_svg = expected_path.read_text()
    output_svg = new_path.read_text()
    assert expected_svg == output_svg

def test_dropfg(tmp_path):
    orig_path = (Path(__file__).parent.resolve()
                 / 'data/svg_edit/sub-22293_acq-mprage_rec-prenorm_run-1_space-MNI152NLin6Asym_T1w.svg')
    new_path = tmp_path / 'dropfg.svg'
    expected_path = (Path(__file__).parent.resolve()
                 / 'data/svg_edit/sub-22293_acq-mprage_rec-prenorm_run-1_space-MNI152NLin6Asym_T1w_dropfg.svg')
    _drop_image(orig_path, new_path, 'foreground')
    expected_svg = expected_path.read_text()
    output_svg = new_path.read_text()
    assert expected_svg == output_svg

def test_dropbg(tmp_path):
    orig_path = (Path(__file__).parent.resolve()
                 / 'data/svg_edit/sub-22293_acq-mprage_rec-prenorm_run-1_space-MNI152NLin6Asym_T1w.svg')
    new_path = tmp_path / 'dropbg.svg'
    expected_path = (Path(__file__).parent.resolve()
                 / 'data/svg_edit/sub-22293_acq-mprage_rec-prenorm_run-1_space-MNI152NLin6Asym_T1w_dropbg.svg')
    _drop_image(orig_path, new_path, 'background')
    expected_svg = expected_path.read_text()
    output_svg = new_path.read_text()
    assert expected_svg == output_svg
