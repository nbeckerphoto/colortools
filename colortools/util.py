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


class ColorSpace(str, Enum):
    """Enum for color spaces used when clustering with the KMEANS algorithm."""

    RGB = "rgb"
    LAB = "lab"


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
    rounded = np.around(vals, 0).astype(int)
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


# sRGB <-> CIE XYZ <-> CIE L*a*b* conversion constants (D65 white point).
# Reference: http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html

# sRGB gamma companding (IEC 61966-2-1): piecewise linear-near-black, power curve elsewhere.
SRGB_GAMMA_EXPONENT = 2.4
SRGB_LINEAR_SLOPE = 12.92
SRGB_GAMMA_OFFSET = 0.055
SRGB_DECODE_THRESHOLD = 0.04045  # breakpoint in gamma-encoded space, for decoding to linear light
SRGB_ENCODE_THRESHOLD = 0.0031308  # same breakpoint in linear space, for encoding back to gamma

# CIE Lab nonlinearity: cube root, with a linear segment near black (below delta**3) to avoid an
# infinite slope at zero. `delta` is the breakpoint in linear XYZ-ratio terms; the same breakpoint
# reappears as plain `delta` once already inside the cube-root ("f") domain, e.g. in lab_to_rgb.
LAB_DELTA = 6 / 29

LAB_D65_WHITE = np.array([0.95047, 1.0, 1.08883])  # CIE standard illuminant D65 reference white
LAB_RGB_TO_XYZ_MATRIX = np.array(  # sRGB (linear) to CIE XYZ, D65 white point
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ]
)
LAB_XYZ_TO_RGB_MATRIX = np.linalg.inv(LAB_RGB_TO_XYZ_MATRIX)


def rgb_to_lab(rgb: Union[List, np.ndarray]) -> np.ndarray:
    """Convert RGB values (0-255) to CIE L*a*b*.

    Unlike `rgb_to_hsv`, this operates via vectorized NumPy operations rather than one color at a time, since
    it's also used to convert entire images' worth of pixels for clustering in Lab space. Accepts a single
    color, a list of colors, or a full `(height, width, 3)` image.

    Args:
        rgb (Union[List, np.ndarray]): RGB values (0-255), in any shape ending in a size-3 last axis.

    Returns:
        np.ndarray: The converted L*a*b* values, in the same shape as the input.
    """
    rgb_normalized = np.asarray(rgb, dtype=float) / 255
    linear = np.where(
        rgb_normalized <= SRGB_DECODE_THRESHOLD,
        rgb_normalized / SRGB_LINEAR_SLOPE,
        ((rgb_normalized + SRGB_GAMMA_OFFSET) / (1 + SRGB_GAMMA_OFFSET)) ** SRGB_GAMMA_EXPONENT,
    )
    xyz = linear @ LAB_RGB_TO_XYZ_MATRIX.T

    xyz_normalized = xyz / LAB_D65_WHITE
    f = np.where(
        xyz_normalized > LAB_DELTA**3,
        np.cbrt(xyz_normalized),
        xyz_normalized / (3 * LAB_DELTA**2) + 4 / 29,
    )

    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def lab_to_rgb(lab: Union[List, np.ndarray]) -> np.ndarray:
    """Convert CIE L*a*b* values back to RGB (0-255).

    See `rgb_to_lab` for details on accepted shapes.

    Args:
        lab (Union[List, np.ndarray]): L*a*b* values, in any shape ending in a size-3 last axis.

    Returns:
        np.ndarray: The converted RGB values (0-255), in the same shape as the input.
    """
    lab = np.asarray(lab, dtype=float)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]

    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200
    xyz_normalized = np.stack(
        [np.where(f > LAB_DELTA, f**3, 3 * LAB_DELTA**2 * (f - 4 / 29)) for f in (fx, fy, fz)], axis=-1
    )
    xyz = xyz_normalized * LAB_D65_WHITE

    linear = np.clip(xyz @ LAB_XYZ_TO_RGB_MATRIX.T, 0, None)
    rgb_normalized = np.where(
        linear <= SRGB_ENCODE_THRESHOLD,
        linear * SRGB_LINEAR_SLOPE,
        (1 + SRGB_GAMMA_OFFSET) * linear ** (1 / SRGB_GAMMA_EXPONENT) - SRGB_GAMMA_OFFSET,
    )
    return np.clip(rgb_normalized, 0, 1) * 255
