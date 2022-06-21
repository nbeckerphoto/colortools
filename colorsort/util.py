from enum import Enum

import cv2
import numpy as np


class ImageOrientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    AUTO = 2

    def rotate(self):
        if self.value == 0 or self.value == 1:
            return ImageOrientation(int(not self.value))
        else:
            return ImageOrientation(self.value)


def rgb_to_hsv(rgb):
    color_rep = np.zeros((1, 1, 3), np.uint8)
    color_rep[:] = rgb
    color_rep_hsv = cv2.cvtColor(color_rep, cv2.COLOR_RGB2HSV)
    hue, sat, val = color_rep_hsv[0][0]
    return np.array([hue, sat, val])


def hsv_to_rgb(hsv):
    color_rep = np.zeros((1, 1, 3), np.uint8)
    color_rep[:] = hsv
    color_rep_rgb = cv2.cvtColor(color_rep, cv2.COLOR_HSV2RGB)
    r, g, b = color_rep_rgb[0][0]
    return np.array([r, g, b])


def enhance_color(image_rgb, saturation=0.1, value=0.1):
    color_hsv = rgb_to_hsv(image_rgb)
    color_hsv[1] = color_hsv[1] * (1 + saturation)
    color_hsv[2] = color_hsv[2] * (1 + value)
    color_rgb = hsv_to_rgb(color_hsv)
    return color_rgb


def get_sample(image: np.array) -> np.array:
    """Get a sample of pixels from an image.

    Gets data from rule of thirds lines and quadrant lines.

    Args:
        image (np.array): The image from which to pull the sample.

    Returns:
        np.array: A sample of pixels from the provided image.
    """
    rot_sample = get_rule_of_thirds_sample(image)
    quad_sample = get_quadrant_sample(image)
    return np.concatenate((rot_sample, quad_sample))


def get_rule_of_thirds_sample(image: np.array) -> np.array:
    """Get a sample of pixels from an image using the "rule of thirds" lines.

    Args:
        image (np.array): The image from which to pull the sample.

    Returns:
        np.array: A sample of pixels from the provided image.
    """
    height, width, _ = np.shape(image)
    h0 = int(height / 3)
    h1 = h0 * 2
    v0 = int(width / 3)
    v1 = v0 * 2

    horizontal_slices = np.array([image[h0], image[h1]]).reshape((width * 2), 3)
    vertical_slices = np.array([image[:, v0], image[:, v1]]).reshape((height * 2), 3)
    return np.concatenate((horizontal_slices, vertical_slices))


def get_quadrant_sample(image: np.array) -> np.array:
    """Get a sample of pixels from an image using quadrant lines

    Sample draws pixels along the lines that bisect the image horizontally and vertically.

    Args:
        image (np.array): The image from which to pull the sample.

    Returns:
        np.array: A sample of pixels from the provided image.
    """
    height, width, _ = np.shape(image)
    h = int(height / 2)
    v = int(width / 2)

    horizontal_slice = np.array([image[h]]).reshape(width, 3)
    vertical_slice = np.array([image[:, v]]).reshape(height, 3)
    return np.concatenate((horizontal_slice, vertical_slice))
