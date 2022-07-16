import logging
from collections import deque
from enum import Enum
from typing import Callable, List, Tuple

from colortools.analyzed_image import AnalyzedImage


class SortMethod(str, Enum):
    """Enum for image sorting methods."""

    HUE = "hue"
    SATURATION = "saturation"
    VALUE = "value"


def get_sort_function(sort_method: SortMethod) -> Callable:
    """Get the function that corresponds to a sort method name.

    Args:
        sort_method (HeuristicName): The name of the sort method function to return.

    Raises:
        ValueError: Raised if the provided sort method name is not recognized.

    Returns:
        Callable: The function corresponding to a heuristic name.
    """
    if sort_method == SortMethod.HUE:
        return huesort
    elif sort_method == SortMethod.SATURATION:
        return satsort
    elif sort_method == SortMethod.VALUE:
        return valsort
    else:
        raise ValueError(f"Invalid sort method selected: {sort_method}")


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


def huesort(analyzed_images: List[AnalyzedImage], sort_reverse: bool, sort_anchor: str) -> List[AnalyzedImage]:
    """Static method for sorting a collection of analyzed images by their hue.

    Sort by color (using the AnalyzedImage.get_huesort_metric()), then by value, then by saturation. All
    black and white images are moved to the end of the sequence.

    Args:
        analyzed_images (List[AnalyzedImage]): A list of analyzed images.
        sort_reverse (bool): Whether to reverse the sort order.
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
            elem.get_huesort_metric(),
            elem.get_dominant_color(hsv=True, round=True)[2],
            elem.get_dominant_color(hsv=True, round=True)[1],
        ),
        reverse=sort_reverse,
    )

    # sort black and white images by value
    bw.sort(key=lambda elem: elem.get_dominant_color(hsv=True, round=True)[2], reverse=sort_reverse)

    color = orient_to_sort_anchor(color, sort_anchor)
    combined = []
    combined.extend(color)
    combined.extend(bw)  # bw always at end
    return combined


def satsort(analyzed_images: List[AnalyzedImage], sort_reverse: bool, sort_anchor: str) -> List[AnalyzedImage]:
    """Static method for sorting a collection of analyzed images by their saturation.

    Sort by saturation (high to low), then by value, then hue.

    Args:
        analyzed_images (List[AnalyzedImage]): A list of analyzed images.
        sort_reverse (bool): Whether to reverse the sort order.
        sort_anchor (str): The anchor image with whih to begin the returned sorted sequence.

    Returns:
        List[AnalyzedImage]: Sorted results, where all images are sorted by the saturation of
            their domiant color.
    """
    analyzed_images.sort(
        key=lambda elem: (
            elem.get_dominant_color(hsv=True, round=True)[1],
            elem.get_dominant_color(hsv=True, round=True)[2],
            elem.get_huesort_metric(),
        ),
        reverse=sort_reverse,
    )
    return orient_to_sort_anchor(analyzed_images, sort_anchor)


def valsort(analyzed_images: List[AnalyzedImage], sort_reverse: bool, sort_anchor: str) -> List[AnalyzedImage]:
    """Static method for sorting a collection of analyzed images by their value.

    Sort by value (low to high), then by color, then by saturation.

    Args:
        analyzed_images (List[AnalyzedImage]): A list of analyzed images.
        sort_reverse (bool): Whether to reverse the sort order.
        sort_anchor (str): The anchor image with whih to begin the returned sorted sequence.

    Returns:
        List[AnalyzedImage]: Sorted results, where all images are sorted by the value of
            their domiant color.
    """
    analyzed_images.sort(
        key=lambda elem: (
            elem.get_dominant_color(hsv=True, round=True)[2],
            elem.get_huesort_metric(),
            elem.get_dominant_color(hsv=True, round=True)[1],
        ),
        reverse=sort_reverse,
    )
    return orient_to_sort_anchor(analyzed_images, sort_anchor)
