import os
from pathlib import Path
from typing import Union

import cv2
import numpy as np

import config as conf
from image import Image
from util import ImageOrientation

# TODO refactor
# TODO test
# TODO docstrings


def save(image: Union[Image, np.array], dest_path: Union[Path, str]):
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

    if isinstance(image, Image):
        os.link(image.image_path, dest_path)
    else:
        cv2.imwrite(str(dest_path), image)


def save_chips_visualization(image_representation: Image, dest: str, orientation: ImageOrientation, display: bool):
    if orientation == ImageOrientation.AUTO:
        orientation = image_representation.get_orientation()

    border_half = int(conf.DEFAULT_CHIP_BORDER / 2)
    border_quarter = int(conf.DEFAULT_CHIP_BORDER / 4)
    stacked_chips = get_2d_stack(image_representation.get_color_chips(), conf.DEFAULT_CHIP_GAP, orientation.rotate())

    if orientation == ImageOrientation.HORIZONTAL:
        original_image, chips, remapped_image = enforce_matching_height(
            *[image_representation.get_image_rgb(), stacked_chips, image_representation.get_remapped_image()]
        )
        target_height = original_image.shape[0] + conf.DEFAULT_CHIP_BORDER
        original_image = pad_to_height(original_image, target_height, left=border_half, right=border_quarter)
        chips = pad_to_height(chips, target_height, left=border_quarter, right=border_quarter)
        remapped_image = pad_to_height(remapped_image, target_height, left=border_quarter, right=border_half)
        chips_viz = cv2.hconcat([original_image, chips, remapped_image])
    elif orientation == ImageOrientation.VERTICAL:
        original_image, chips, remapped_image = enforce_matching_width(
            *[image_representation.get_image_rgb(), stacked_chips, image_representation.get_remapped_image()]
        )
        target_width = original_image.shape[1] + conf.DEFAULT_CHIP_BORDER
        original_image = pad_to_width(original_image, target_width, top=border_half, bottom=border_quarter)
        chips = pad_to_width(chips, target_width, top=border_quarter, bottom=border_quarter)
        remapped_image = pad_to_width(remapped_image, target_width, top=border_quarter, bottom=border_half)
        chips_viz = cv2.vconcat([original_image, chips, remapped_image])
    else:
        raise ValueError(f"Unrecognized orientation: {orientation}")

    if display:
        display_until_key(chips_viz)
    save(chips_viz, dest)


def save_spectrum_visualization(image_reps, dest, display=False):
    vertical_bars = [get_histogram_as_bar(rep) for rep in image_reps]
    spectrum = cv2.hconcat(vertical_bars)

    if display:
        display_until_key(spectrum)
    save(spectrum, dest)


def get_histogram_as_bar(
    img_representation: Image,
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
    bar = np.zeros((height, width, 3), np.uint8)
    start_y = 0

    for color_rgb, proportion in color_hist:  # build top-down
        # color_rgb_as_list = color_rgb.tolist() # color.rgb_rep.astype("uint8").tolist()

        # plot the relative percentage of each cluster
        end_y = start_y + (proportion * height)
        cv2.rectangle(
            bar,  # image to be filled
            (0, int(start_y)),  # start
            (width, int(end_y)),  # end
            color_rgb.tolist(),  # color in RGB (or BGR?)
            -1,
        )
        start_y = end_y

    # return the bar chart
    return bar


def display_until_key(img):
    cv2.imshow("img", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_2d_stack(images, gap, orientation: ImageOrientation):
    with_borders = [images[0]]
    if orientation == ImageOrientation.HORIZONTAL:
        top = bottom = right = 0
        left = gap
        concat = cv2.hconcat
    elif orientation == ImageOrientation.VERTICAL:
        bottom = left = right = 0
        top = gap
        concat = cv2.vconcat
    else:
        raise ValueError(f"Unrecognized orientation: {orientation}")

    for i in range(1, len(images)):
        with_borders.append(
            cv2.copyMakeBorder(images[i], top, bottom, left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        )

    return concat(with_borders)


def enforce_matching_height(*imgs):
    max_height = max([img.shape[0] for img in imgs])
    padded = []

    for img in imgs:
        diff = max_height - img.shape[0]
        top = bottom = int(diff / 2)
        if not diff % 2 == 0:
            bottom += 1
        img_with_border = cv2.copyMakeBorder(img, top, bottom, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        padded.append(img_with_border)

    return padded


def enforce_matching_width(*imgs):
    max_width = max([img.shape[1] for img in imgs])
    padded = []

    for img in imgs:
        diff = max_width - img.shape[1]
        left = right = int(diff / 2)
        if not diff % 2 == 0:
            left += 1
        img_with_border = cv2.copyMakeBorder(img, 0, 0, left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        padded.append(img_with_border)

    return padded


def pad_to_height(img, target_height, left, right):
    height = img.shape[0]
    top_and_bottom = int((target_height - height) / 2)
    top = bottom = top_and_bottom
    actual_height = height + (2 * top_and_bottom)
    if not actual_height == target_height:
        bottom += target_height - actual_height

    with_border = cv2.copyMakeBorder(
        img, int(top), int(bottom), left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )
    return with_border


def pad_to_width(img, target_width, top, bottom):
    width = img.shape[1]
    left_and_right = int((target_width - width) / 2)
    left = right = left_and_right
    actual_width = width + (2 * left_and_right)
    if not actual_width == target_width:
        bottom += target_width - actual_width

    with_border = cv2.copyMakeBorder(
        img, top, bottom, int(left), int(right), cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )
    return with_border
