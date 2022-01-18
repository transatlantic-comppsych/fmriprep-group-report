from pathlib import Path

def _parse_figure(fig_path):
    """
    Parse an fmriprep figure into header, background, middle, foreground, and tail.
    Parameters
    ----------
    fig_path: str
        Path to the figure to parse

    Returns
    -------
    header: list of str
        Lines preceding the background image
    background: list of str
        Lines corresponding to the background image
    middle: list of str
        any lines occuring between the background and foreground lines
    foreground: list of str
        Lines corresponding to the foreground image
    tail: list of str
        Lines following the foreground image
    """
    fig_path = Path(fig_path)
    fig = fig_path.read_text()
    fig_lines = fig.split("\n")
    header = []
    origbg = []
    middle = []
    origfg = []
    tail = []
    inhead = True
    inorigbg = False
    inmiddle = False
    inorigfg = False
    intail = False
    for fl in fig_lines:
        if fl.strip() == '<g class="background-svg">':
            open_gs = 1
            inhead = False
            inorigbg = True
            origbg.append(fl)
            continue
        elif fl.strip() == '<g class="foreground-svg">':
            open_gs = 1
            inmiddle = False
            inorigfg = True
            origfg.append(fl)
            continue
        elif inhead:
            header.append(fl)
        elif inmiddle:
            middle.append(fl)
        elif intail:
            tail.append(fl)
        elif inorigbg:
            origbg.append(fl)
            if '<g ' in fl:
                open_gs += 1
            if '</g>' in fl:
                open_gs -= 1
                if open_gs == 0:
                    inorigbg = False
                    inmiddle = True
        elif inorigfg:
            origfg.append(fl)
            if '<g ' in fl:
                open_gs +=1
            if '</g>' in fl:
                open_gs -= 1
                if open_gs == 0:
                    inorigfg = False
                    intail = True

    return header, origbg, middle, origfg, tail


def _flip_images(fig_path, new_path):
    """
    Flip the foreground and background images
    Parameters
    ----------
    fig_path : str
        Path to source image
    new_path : str
        Path for new image

    """

    header, origbg, middle, origfg, tail = _parse_figure(fig_path)
    new_path = Path(new_path)
    newbg = origfg
    newbg[0] = newbg[0].replace('foreground', 'background')

    newfg = origbg
    newfg[0] = newfg[0].replace('background', 'foreground')

    new_svg = '\n'.join(header + newbg + middle + newfg + tail)
    new_path.write_text(new_svg)

def _drop_image(fig_path, new_path, image_to_drop):
    """
    Drop the foreground or background image. The background image is the one displayed before mousing over the svg.
    Parameters
    ----------
    fig_path : str
        Path to source image
    new_path : str
        Path for new image
    image_to_drop : str
        Which image to drop, allowed values are "background", "foreground".
    """

    if not image_to_drop in ['background', 'foreground']:
        raise ValueError(f"image_to_drop must be one of ['background', 'foreground'], {image_to_drop} "
                         f"is not a valid option.")

    header, origbg, middle, origfg, tail = _parse_figure(fig_path)
    new_path = Path(new_path)

    if image_to_drop == 'foreground':
        newbg = origfg
        newbg[0] = newbg[0].replace('foreground', 'background')
        new_svg = '\n'.join(header + newbg + middle + tail)
        new_path.write_text(new_svg)
    else:
        new_svg = '\n'.join(header + origbg + middle + tail)
        new_path.write_text(new_svg)