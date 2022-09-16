import colorsys
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Union

import numpy as np

DIGIT_RE = re.compile(r"(\d+)")


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


class DominantColorAlgorithm(str, Enum):
    """Enum for dominant color algorithms."""

    HUE_DIST = "hue_dist"
    KMEANS = "kmeans"


# general operations
# --------------------------------------------------------------------------------
def get_timestamp_string() -> str:
    """Return a timestamp string.

    Returns:
        str: A string representation of a newly-constructed datetime object.
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")


def atoi(text: str) -> Union[int, str]:
    """ASCII to integer function."

    Args:
        text (str): Text to convert to integer, if possible.

    Returns:
        Union[int, str]: The text as an integer, if possible.
    """
    return int(text) if text.isdigit() else text


def natural_keys(text: str) -> List[str]:
    """Converts a string to a list of "natural keys."

    `alist.sort(key=natural_keys)` sorts in human order.

    References:
    - https://stackoverflow.com/a/5967539
    - http://nedbatchelder.com/blog/200712/human_sorting.html (see Toothy's implementation
    (in the comments)

    Args:
        text (str): Text to convert to natural keys

    Returns:
        List[str]: A list of "natural keys" from the provided string.
    """
    if not isinstance(text, str):
        text = str(text)
    return [atoi(c) for c in DIGIT_RE.split(text)]


def collect_jpg_paths(input_dir: Union[Path, str]) -> List[Path]:
    """Find all .jpg images in the provided directory.

    Args:
        input_dir (Union[Path, str]): A folder containing .jpg files, or a single .jpg file.

    Returns:
        List[Path]: A list of .jpg files, sorted in natural order.
    """
    if not isinstance(input_dir, Path):
        input_dir = Path(input_dir)

    jpg_paths = [input_dir] if input_dir.is_file() else list(input_dir.rglob("*.jpg"))
    jpg_paths.sort(key=natural_keys)
    return jpg_paths


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


def round_array(vals: Union[List, np.ndarray]) -> Union[List[List[int]], List[int]]:
    """Round an entire list/array (or list/array of lists/arrays) of values to integers.

    Args:
        vals (Union[List, np.ndarray]): The list/array (or list/array of lists/arrays) to round.

    Returns:
        Union[List[List[int]], List[int]]: The rounded output list.
    """
    rounded = np.uint(np.around(vals, 0))
    return [a.tolist() for a in rounded]


def normalize_8bit_hsv(hsv_list: Union[List[int], List[List[int]]]) -> Union[List[int], List[List[int]]]:
    """Normalize an HSV array specified with 8-bit integers to the standard HSV space.

    Standard HSV space: hue [0..360], sat [0..100], val [0..100].

    Args:
        hsv_list (Union[List[int], List[List[int]]]): A single HSV array specified in 8-bit values, or a list
        of them.

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


def crop_center(rgb_image_data: np.ndarray, border_percent_y: float, border_percent_x: float = None) -> np.ndarray:
    """Crop the borders of an image, leaving only the center.

    Source: https://stackoverflow.com/a/39382475

    Args:
        rgb_image_data (np.ndarray): The image to crop, as a NumPy array.
        border_percent_y (float): The percentage to crop from the top and bottom.
        border_percent_x (float, optional): The percentage to crop from the left and right; if None, sets to the
            same value as border_percent_y. Defaults to None.

    Returns:
        np.ndarray: The cropped image array.
    """
    if border_percent_x is None:
        border_percent_x = border_percent_y
    height, width = rgb_image_data.shape[0], rgb_image_data.shape[1]
    cropped_height = height - (2 * round_to_int(border_percent_y * height))
    cropped_width = width - (2 * round_to_int(border_percent_x * width))

    start_y = height // 2 - (cropped_height // 2)
    start_x = width // 2 - (cropped_width // 2)
    return rgb_image_data[start_y : start_y + cropped_height, start_x : start_x + cropped_width]


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


# def get_sample(image: np.ndarray) -> np.ndarray:
#     """Get a sample of pixels from an image.

#     Gets data from rule of thirds lines and quadrant lines.

#     Args:
#         image (np.ndarray): The image from which to pull the sample.

#     Returns:
#         np.ndarray: A sample of pixels from the provided image.
#     """
#     rot_sample = get_rule_of_thirds_sample(image)
#     quad_sample = get_quadrant_sample(image)
#     return np.concatenate((rot_sample, quad_sample))


# def get_rule_of_thirds_sample(image: np.ndarray) -> np.ndarray:
#     """Get a sample of pixels from an image using the "rule of thirds" lines.

#     Args:
#         image (np.ndarray): The image from which to pull the sample.

#     Returns:
#         np.ndarray: A sample of pixels from the provided image.
#     """
#     height, width, _ = np.shape(image)
#     h0 = int(height / 3)
#     h1 = h0 * 2
#     v0 = int(width / 3)
#     v1 = v0 * 2

#     horizontal_slices = np.ndarray([image[h0], image[h1]]).reshape((width * 2), 3)
#     vertical_slices = np.ndarray([image[:, v0], image[:, v1]]).reshape((height * 2), 3)
#     return np.concatenate((horizontal_slices, vertical_slices))


# def get_quadrant_sample(image: np.ndarray) -> np.ndarray:
#     """Get a sample of pixels from an image using quadrant lines

#     Sample draws pixels along the lines that bisect the image horizontally and vertically.

#     Args:
#         image (np.ndarray): The image from which to pull the sample.

#     Returns:
#         np.ndarray: A sample of pixels from the provided image.
#     """
#     height, width, _ = np.shape(image)
#     h = int(height / 2)
#     v = int(width / 2)

#     horizontal_slice = np.ndarray([image[h]]).reshape(width, 3)
#     vertical_slice = np.ndarray([image[:, v]]).reshape(height, 3)
#     return np.concatenate((horizontal_slice, vertical_slice))
