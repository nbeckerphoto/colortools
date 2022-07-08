import colorsys
from enum import Enum
from typing import List


class ImageOrientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    AUTO = 2

    def rotate(self):
        if self.value == 0 or self.value == 1:
            return ImageOrientation(int(not self.value))
        else:
            return ImageOrientation(self.value)


class DominantColorAlgorithm(Enum):
    HUE_DIST = "HUE_DIST"
    KMEANS = "KMEANS"


def round_to_int(val):
    return int(val + 0.5)


def rgb_to_hsv(rgb_list, normalize_h=360, normalize_sv=100):
    print(rgb_list)
    if not isinstance(rgb_list[0], List):
        just_one = True
        rgb_list = [rgb_list]
    else:
        just_one = False

    converted = []
    for rgb in rgb_list:
        (h, s, v) = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
        converted.append(
            [round_to_int(h * normalize_h), round_to_int(s * normalize_sv), round_to_int(v * normalize_sv)]
        )

    if just_one:
        converted = converted[0]
    return converted


def hsv_to_rgb(hsv_list, normalize_h=360, normalize_sv=100):
    if not isinstance(hsv_list[0], List):
        just_one = True
        hsv_list = [hsv_list]
    else:
        just_one = False

    converted = []
    for hsv in hsv_list:
        (r, g, b) = colorsys.hsv_to_rgb(hsv[0] / normalize_h, hsv[1] / normalize_sv, hsv[2] / normalize_sv)
        converted.append([round_to_int(r * 255), round_to_int(g * 255), round_to_int(b * 255)])

    if just_one:
        converted = converted[0]
    return converted


def normalize_hsv(hsv_list):
    if not isinstance(hsv_list[0], List):
        just_one = True
        hsv_list = [hsv_list]
    else:
        just_one = False

    normalized = []
    for hsv in hsv_list:
        h = round_to_int((hsv[0] / 255) * 360)
        s = round_to_int((hsv[1] / 255) * 100)
        v = round_to_int((hsv[2] / 255) * 100)
        normalized.append([h, s, v])

    if just_one:
        normalized = normalized[0]
    return normalized


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
