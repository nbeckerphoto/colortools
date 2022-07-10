import colorsys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Union

import numpy as np


# enums
# --------------------------------------------------------------------------------
class ImageOrientation(Enum):
    """Enum for image orientations."""

    HORIZONTAL = 0
    VERTICAL = 1
    AUTO = 2

    def rotate(self):
        if self.value == 0 or self.value == 1:
            return ImageOrientation(int(not self.value))
        else:
            return ImageOrientation(self.value)


class DominantColorAlgorithm(Enum):
    """Enum for dominant color algorithms."""

    HUE_DIST = "HUE_DIST"
    KMEANS = "KMEANS"


# general operations
# --------------------------------------------------------------------------------
def get_timestamp_string():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def collect_jpg_paths(input_dir):
    if not isinstance(input_dir, Path):
        input_dir = Path(input_dir)

    return [input_dir] if input_dir.is_file() else list(input_dir.rglob("*.jpg"))


# mathematical operations
# --------------------------------------------------------------------------------
def round_to_int(val: float) -> int:
    """Round a single float value to the nearest integer.

    Args:
        val (float): The float to round.

    Returns:
        int: The rounded integer.
    """
    return int(val + 0.5)


def round_array(vals: Union[List, np.array]) -> Union[List[List[int]], List[int]]:
    """Round an entire list/array (or list/array of lists/arrays) of values to integers.

    Args:
        vals (Union[List, np.array]): The list/array (or list/array of lists/arrays) to round.

    Returns:
        Union[List[List[int]], List[int]]: The rounded output list.
    """
    rounded = np.uint(np.around(vals, 0))
    return [a.tolist() for a in rounded]


def normalize_8bit_hsv(hsv_list: Union[List[int], List[List[int]]]) -> Union[List[int], List[List[int]]]:
    """Normalize an HSV array specified with 8-bit integers to the standard HSV space.

    Standard HSV space: hue [0..360], sat [0..100], val [0..100].

    Args:
        hsv_list (Union[List[int], List[List[int]]]): A single HSV array, or a list of them.

    Returns:
        Union[List[int], List[List[int]]]: The normalized HSV array, or a list of them.
    """
    if not isinstance(hsv_list[0], List):
        just_one = True
        hsv_list = [hsv_list]
    else:
        just_one = False

    normalized = []
    for hsv in hsv_list:
        h = ((hsv[0] / 255) * 360) % 360
        s = (hsv[1] / 255) * 100
        v = (hsv[2] / 255) * 100
        normalized.append([h, s, v])

    if just_one:
        normalized = normalized[0]
    return normalized


# color space conversions
# --------------------------------------------------------------------------------
def rgb_to_hsv(
    rgb_list: Union[List[int], List[List[int]]], hsv_normalize_h: int = 360, hsv_normalize_sv: int = 100
) -> Union[List[int], List[List[int]]]:
    """Convert an RGB array to HSV.

    Args:
        rgb_list (Union[List[int], List[List[int]]]): A single RGB array, or a list of them.
        hsv_normalize_h (int, optional): The target normalization factor for HSV hues. Defaults to 360.
        hsv_normalize_sv (int, optional): The target normalization factor for HSV saturations and values.
            Defaults to 100.

    Returns:
        Union[List[int], List[List[int]]]: The converted HSV array, or a list of them.
    """
    if not isinstance(rgb_list[0], List):
        just_one = True
        rgb_list = [rgb_list]
    else:
        just_one = False

    converted = []
    for rgb in rgb_list:
        (h, s, v) = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
        converted.append([(h * hsv_normalize_h) % hsv_normalize_h, s * hsv_normalize_sv, v * hsv_normalize_sv])

    if just_one:
        converted = converted[0]
    return converted


def hsv_to_rgb(
    hsv_list: Union[List[int], List[List[int]]], hsv_normalize_h: int = 360, hsv_normalize_sv: int = 100
) -> Union[List[int], List[List[int]]]:
    """Convert an HSV array to RGB.

    Args:
        hsv_list (Union[List[int], List[List[int]]]): A single HSV array, or a list of them.
        hsv_normalize_h (int, optional): The source normalization factor for HSV hues. Defaults to 360.
        hsv_normalize_sv (int, optional): The source normalization factor for HSV saturations and values.
            Defaults to 100.

    Returns:
        Union[List[int], List[List[int]]]: The converted RGB array, or a list of them.
    """
    if not isinstance(hsv_list[0], List):
        just_one = True
        hsv_list = [hsv_list]
    else:
        just_one = False

    converted = []
    for hsv in hsv_list:
        (r, g, b) = colorsys.hsv_to_rgb(hsv[0] / hsv_normalize_h, hsv[1] / hsv_normalize_sv, hsv[2] / hsv_normalize_sv)
        converted.append([r * 255, g * 255, b * 255])

    if just_one:
        converted = converted[0]
    return converted


# def get_sample(image: np.array) -> np.array:
#     """Get a sample of pixels from an image.

#     Gets data from rule of thirds lines and quadrant lines.

#     Args:
#         image (np.array): The image from which to pull the sample.

#     Returns:
#         np.array: A sample of pixels from the provided image.
#     """
#     rot_sample = get_rule_of_thirds_sample(image)
#     quad_sample = get_quadrant_sample(image)
#     return np.concatenate((rot_sample, quad_sample))


# def get_rule_of_thirds_sample(image: np.array) -> np.array:
#     """Get a sample of pixels from an image using the "rule of thirds" lines.

#     Args:
#         image (np.array): The image from which to pull the sample.

#     Returns:
#         np.array: A sample of pixels from the provided image.
#     """
#     height, width, _ = np.shape(image)
#     h0 = int(height / 3)
#     h1 = h0 * 2
#     v0 = int(width / 3)
#     v1 = v0 * 2

#     horizontal_slices = np.array([image[h0], image[h1]]).reshape((width * 2), 3)
#     vertical_slices = np.array([image[:, v0], image[:, v1]]).reshape((height * 2), 3)
#     return np.concatenate((horizontal_slices, vertical_slices))


# def get_quadrant_sample(image: np.array) -> np.array:
#     """Get a sample of pixels from an image using quadrant lines

#     Sample draws pixels along the lines that bisect the image horizontally and vertically.

#     Args:
#         image (np.array): The image from which to pull the sample.

#     Returns:
#         np.array: A sample of pixels from the provided image.
#     """
#     height, width, _ = np.shape(image)
#     h = int(height / 2)
#     v = int(width / 2)

#     horizontal_slice = np.array([image[h]]).reshape(width, 3)
#     vertical_slice = np.array([image[:, v]]).reshape(height, 3)
#     return np.concatenate((horizontal_slice, vertical_slice))
