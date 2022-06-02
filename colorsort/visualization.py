import os
from pathlib import Path

import cv2
import numpy as np

import colorsort.config as conf
from colorsort.cs_image_representation import CsImageRepresentation, HistogramColor


def save(image, dest_path):
    if not isinstance(dest_path, Path):
        dest_path = Path(dest_path)

    dest_parent = dest_path.parents[0]
    _ = dest_parent.mkdir(parents=True, exist_ok=True)

    if isinstance(image, CsImageRepresentation):
        os.link(image.image_path, dest_path)
    else:
        cv2.imwrite(str(dest_path), image)


def save_chips_visualization(image_representations, dest, display=False):
    border_half = int(conf.DEFAULT_CHIP_BORDER / 2)
    border_quarter = int(conf.DEFAULT_CHIP_BORDER / 4)
    stacked_chips = get_vertical_stack(image_representations.get_color_chips(), 10)
    original_image, chips, remapped_image = enforce_matching_height(
        *[image_representations.image_rgb, stacked_chips, image_representations.get_remapped_image()]
    )
    target_height = original_image.shape[0] + conf.DEFAULT_CHIP_BORDER
    original_image = pad(original_image, target_height, left=border_half, right=border_quarter)
    chips = pad(chips, target_height, left=border_quarter, right=border_quarter)
    remapped_image = pad(remapped_image, target_height, left=border_quarter, right=border_half)
    sbs = cv2.hconcat([original_image, chips, remapped_image])

    if display:
        display_until_key(sbs)
    save(sbs, dest)


def save_spectrum_visualization(image_reps, dest, display=False):
    vertical_bars = [get_histogram_as_bar(rep) for rep in image_reps]
    spectrum = cv2.hconcat(vertical_bars)

    if display:
        display_until_key(spectrum)
    save(spectrum, dest)


def get_histogram_as_bar(img_representation, dominant_color_only: bool=True, height=conf.DEFAULT_BAR_HEIGHT, width=conf.DEFAULT_BAR_WIDTH):
    if dominant_color_only: 
        color_hist = [HistogramColor(img_representation.get_dominant_color(), 1)]
        print(f"{img_representation.image_path.stem} - {img_representation.get_dominant_color(hsv=True)}")
    else: 
        color_hist = img_representation.cluster_histogram
    bar = np.zeros((height, width, 3), np.uint8)
    start_y = 0

    for color in color_hist:  # build top-down
        color_rgb = color.rgb_rep.tolist()  # color.rgb_rep.astype("uint8").tolist()

        # plot the relative percentage of each cluster
        end_y = start_y + (color.proportion * height)
        cv2.rectangle(
            bar,  # image to be filled
            (0, int(start_y)),  # start
            (width, int(end_y)),  # end
            color_rgb,  # color in BGR
            -1,
        )
        start_y = end_y

    # return the bar chart
    return bar


def display_until_key(img):
    cv2.imshow("img", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_vertical_stack(imgs, gap):
    with_borders = [imgs[0]]
    for i in range(1, len(imgs)):
        with_borders.append(cv2.copyMakeBorder(imgs[i], gap, 0, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255]))

    return cv2.vconcat(with_borders)


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


def pad(img, target_height, left, right):
    height = img.shape[0]
    top_and_bottom = int((target_height - height) / 2)
    top = top_and_bottom
    bottom = top_and_bottom
    actual_height = height + (2 * top_and_bottom)
    if not actual_height == target_height:
        bottom += target_height - actual_height

    with_border = cv2.copyMakeBorder(
        img, int(top), int(bottom), left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )
    return with_border
