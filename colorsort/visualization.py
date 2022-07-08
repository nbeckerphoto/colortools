import os
from pathlib import Path
from typing import List, Union

import numpy as np
from PIL import Image, ImageOps

import colorsort.config as conf
from colorsort.analyzed_image import AnalyzedImage
from colorsort.util import ImageOrientation

# TODO refactor
# TODO test
# TODO docstrings


def save(image: Union[AnalyzedImage, Image.Image, np.array], dest_path: Union[Path, str]):
    """Save the provided image to disk.

    If the image is an image representation, create a hard link between the image's original file and
    the provided path to save on disk space.

    Args:
        image (Union[Image, np.array]): The image to save to disk.
        dest_path (Union[Path, str]): The output path to which to save the image.
    """
    if not isinstance(dest_path, Path):
        dest_path = Path(dest_path)

    dest_parent = dest_path.parents[0]
    _ = dest_parent.mkdir(parents=True, exist_ok=True)

    if isinstance(image, AnalyzedImage):
        os.link(image.image_path, dest_path)
    elif isinstance(image, Image.Image):
        image.save(dest_path)
    else:
        image = Image.fromarray(image)
        image.save(dest_path)


def save_chips_visualization(
    analyzed_image: AnalyzedImage,
    dest: str,
    image_orientation: ImageOrientation,
    include_remapped_image: bool,
    display: bool,
):
    if image_orientation == ImageOrientation.AUTO:
        image_orientation = analyzed_image.get_orientation()
        visualization_orientation = image_orientation.rotate()

    stacked_chips = get_2d_stack(
        get_color_chips(analyzed_image.get_dominant_colors()),
        conf.DEFAULT_CHIP_GAP,
        image_orientation,
    )

    vis_components = [analyzed_image.pil_image, stacked_chips]
    if include_remapped_image:
        vis_components.append(analyzed_image.get_remapped_image())
    outer_border = int(conf.DEFAULT_CHIP_BORDER / 2)
    inner_border = int(conf.DEFAULT_CHIP_BORDER / 4)
    if visualization_orientation == ImageOrientation.HORIZONTAL:
        visualization = concat_horizontal(vis_components, outer_border, inner_border)
    elif visualization_orientation == ImageOrientation.VERTICAL:
        visualization = concat_vertical(vis_components, outer_border, inner_border)
    else:
        raise ValueError(f"Unrecognized orientation: {image_orientation}")

    if display:
        visualization.show()
    save(visualization, dest)


def get_2d_stack(images, gap, orientation: ImageOrientation):
    with_borders = [images[0]]
    if orientation == ImageOrientation.HORIZONTAL:
        top = bottom = right = 0
        left = gap
        concat = h_concat
    elif orientation == ImageOrientation.VERTICAL:
        bottom = left = right = 0
        top = gap
        concat = v_concat
    else:
        raise ValueError(f"Unrecognized orientation: {orientation}")

    with_borders.extend(add_borders(images[1:], left, top, right, bottom))
    return concat(with_borders)


def get_color_chips(colors, size=conf.DEFAULT_CHIP_SIZE):
    chips = []
    for color in colors:
        chips.append(Image.new("RGB", (size, size), color=tuple(color)))  # (chip))

    return chips


def concat_horizontal(visualization_components, outer_border, inner_border):
    visualization_components = enforce_matching_height(visualization_components)  # all components have same height
    visualization_components = pad_horizontal(visualization_components, outer_border, inner_border)
    return h_concat(visualization_components)


def enforce_matching_height(imgs):
    max_height = max([img.height for img in imgs])
    padded = []

    for img in imgs:
        diff = max_height - img.height
        top = bottom = int(diff / 2)
        if not diff % 2 == 0:
            bottom += 1
        img_with_border = add_borders([img], 0, top, 0, bottom)[0]
        padded.append(img_with_border)

    return padded


def pad_horizontal(imgs, outer_border, inner_border):
    padded = []
    if len(imgs) == 1:
        padded.append(
            add_borders(imgs[0], left=outer_border, top=outer_border, right=outer_border, bottom=outer_border)
        )
    elif len(imgs) == 2:
        padded.append(add_borders(imgs[0], outer_border, outer_border, inner_border, outer_border))
        padded.append(add_borders(imgs[1], 0, outer_border, outer_border, outer_border))
    elif len(imgs) > 2:
        padded.append(add_borders(imgs[0], outer_border, outer_border, inner_border, outer_border))
        for img in imgs[1:-1]:
            padded.append(add_borders(img, 0, outer_border, inner_border, outer_border))
        padded.append(add_borders(imgs[-1], 0, outer_border, outer_border, outer_border))
    else:
        raise ValueError(f"Unexpected number of images to pad: {len(imgs)}")

    return padded


def h_concat(imgs):
    width = sum([im.width for im in imgs])
    height = imgs[0].height
    dst = Image.new("RGB", (width, height))
    h_pos = 0
    for im in imgs:
        dst.paste(im, (h_pos, 0))
        h_pos += im.width
    return dst


def concat_vertical(visualization_components, outer_border, inner_border):
    visualization_components = enforce_matching_width(visualization_components)  # all components have same height
    visualization_components = pad_vertical(visualization_components, outer_border, inner_border)
    return v_concat(visualization_components)


def enforce_matching_width(imgs):
    max_width = max([img.width for img in imgs])
    padded = []

    for img in imgs:
        diff = max_width - img.width
        left = right = int(diff / 2)
        if not diff % 2 == 0:
            left += 1
        img_with_border = add_borders([img], left, 0, right, 0)[0]
        padded.append(img_with_border)

    return padded


def pad_vertical(imgs, outer_border, inner_border):
    padded = []
    if len(imgs) == 1:
        padded.append(
            add_borders(imgs[0], left=outer_border, top=outer_border, right=outer_border, bottom=outer_border)
        )
    elif len(imgs) == 2:
        padded.append(add_borders(imgs[0], outer_border, outer_border, outer_border, inner_border))
        padded.append(add_borders(imgs[1], outer_border, 0, outer_border, outer_border))
    elif len(imgs) > 2:
        padded.append(add_borders(imgs[0], outer_border, outer_border, outer_border, inner_border))
        for img in imgs[1:-1]:
            padded.append(add_borders(img, outer_border, 0, outer_border, inner_border))
        padded.append(add_borders(imgs[-1], outer_border, 0, outer_border, outer_border))
    else:
        raise ValueError(f"Unexpected number of images to pad: {len(imgs)}")

    return padded


def v_concat(imgs):
    width = imgs[0].width
    height = sum([im.height for im in imgs])
    dst = Image.new("RGB", (width, height))
    v_pos = 0
    for im in imgs:
        dst.paste(im, (0, v_pos))
        v_pos += im.height
    return dst


def add_borders(images, left, top, right, bottom):
    """

    border components: left, top, right, bottom

    Args:
        images (_type_): _description_
        borders (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not isinstance(images, List):
        just_one = True
        images = [images]
    else:
        just_one = False

    with_borders = []
    for im in images:
        img_with_border = ImageOps.expand(im, border=(left, top, right, bottom), fill="white")
        with_borders.append(img_with_border)

    if just_one:
        with_borders = with_borders[0]
    return with_borders


def save_spectrum_visualization(image_reps, dest, display=False):
    vertical_bars = [get_histogram_as_bar(rep) for rep in image_reps]
    spectrum = h_concat(vertical_bars)

    if display:
        spectrum.show()
    save(spectrum, dest)


def get_histogram_as_bar(
    img_representation: AnalyzedImage,
    dominant_color_only: bool = True,
    height=conf.DEFAULT_BAR_HEIGHT,
    width=conf.DEFAULT_BAR_WIDTH,
):
    """Get a representation of an image's histogram as a stacked vertical bar.

    TODO Remove defaults; set from CLI

    Args:
        img_representation (Image): _description_
        dominant_color_only (bool, optional): _description_. Defaults to True.
        height (_type_, optional): _description_. Defaults to conf.DEFAULT_BAR_HEIGHT.
        width (_type_, optional): _description_. Defaults to conf.DEFAULT_BAR_WIDTH.

    Returns:
        _type_: _description_
    """
    if dominant_color_only:
        color_hist = [(img_representation.get_dominant_color(), 1)]
        print(f"{img_representation.image_path.stem} - {img_representation.get_dominant_color(hsv=True)}")
    else:
        color_hist = img_representation.cluster_histogram

    bar_components = []
    for color_rgb, proportion in color_hist:  # build top-down
        converted = tuple([int(color) for color in color_rgb])
        bar_components.append(Image.new("RGB", (width, proportion * height), color=converted))

    return v_concat(bar_components)
