from collections import deque
from enum import Enum
from typing import List, Tuple

from colortools.analyzed_image import AnalyzedImage
import logging


class SortMethod(str, Enum):
    """Enum for image sorting methods."""

    COLOR = "color"
    VALUE = "value"


def separate_color_and_bw(analyzed_images: List[AnalyzedImage]) -> Tuple[List[AnalyzedImage], List[AnalyzedImage]]:
    """Separate a list of images into a list of color images and a list of black and white images.

    Args:
        analyzed_images (List[AnalyzedImage]): A list of analyzed images

    Returns:
        Tuple[List[AnalyzedImage], List[AnalyzedImage]]: A list of color images followed by a list
            of black and white images.
    """
    color = []
    bw = []
    for img in analyzed_images:
        if img.is_bw():
            bw.append(img)
        else:
            color.append(img)

    return color, bw


def orient_to_sort_anchor(sorted_analyzed_images: List[AnalyzedImage], sort_anchor: str) -> List[AnalyzedImage]:
    """Shift a sequence of sorted images so that it starts with the provided sort anchor.

    Args:
        sorted_analyzed_images (List[AnalyzedImage]): A sorted list of analyzed images.
        sort_anchor (str): The anchor image with whih to begin the returned sorted sequence.

    Returns:
        List[AnalyzedImage]: Sorted results, starting with the sort anchor.
    """
    starting_index = 0
    if sort_anchor:
        try:
            while not sorted_analyzed_images[starting_index].image_path.name == sort_anchor:
                starting_index += 1
        except IndexError:
            logging.warning(f"Starting image {sort_anchor} not found!")
            starting_index = 0

    sorted_analyzed_images = deque(sorted_analyzed_images)
    for _ in range(starting_index):
        sorted_analyzed_images.append(sorted_analyzed_images.popleft())

    return list(sorted_analyzed_images)


def colorsort(analyzed_images: List[AnalyzedImage], sort_anchor: str) -> List[AnalyzedImage]:
    """Static method for sorting a collection of analyzed images by their hue.

    Uses the AnalyzedImage.get_sort_metric() function for sorting color images.

    Args:
        analyzed_images (List[AnalyzedImage]): A list of analyzed images.
        sort_anchor (str): The anchor image with whih to begin the returned sorted sequence.

    Returns:
        List[AnalyzedImage]: Sorted results, where color images are first, sorted by the hue of
            their dominant color, followed by black and white images, sorted by the value of
            their dominant color.
    """
    color, bw = separate_color_and_bw(analyzed_images)

    # sort color images by built-in sort metric, then value
    color.sort(
        key=lambda elem: (
            elem.get_sort_metric(),
            elem.get_dominant_color(hsv=True)[2],
        )
    )

    # sort black and white images by value
    bw.sort(key=lambda elem: elem.get_dominant_color(hsv=True)[2])

    color = orient_to_sort_anchor(color, sort_anchor)
    combined = []
    combined.extend(color)
    combined.extend(bw)
    return combined


def valuesort(analyzed_images: List[AnalyzedImage], sort_anchor: str) -> List[AnalyzedImage]:
    """Static method for sorting a collection of analyzed images by their value.

    Args:
        analyzed_images (List[AnalyzedImage]): A list of analyzed images.
        sort_anchor (str): The anchor image with whih to begin the returned sorted sequence.

    Returns:
        List[AnalyzedImage]: Sorted results, where all images are sorted by the value of
            their domiant color.
    """

    # sort color images by built-in sort metric, then value
    analyzed_images.sort(key=lambda elem: (elem.get_dominant_color(hsv=True)[2], elem.get_sort_metric()))
    return orient_to_sort_anchor(orient_to_sort_anchor(analyzed_images, sort_anchor))
