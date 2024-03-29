from enum import Enum
from typing import Callable, Dict

import numpy as np

from colortools.config import DEFAULT_N_COLORS_MAX, DEFAULT_N_COLORS_MIN
from colortools.util import round_to_int

PIL_NUM_HUES = 256  # images converted to HSV are in the range 0-255 (8 bits)


class NColorsHeuristic(str, Enum):
    """Enum type for heuristic names."""

    AUTO_N_HUE = "auto_n_hue"
    AUTO_N_HUE_BINNED = "auto_n_hue_binned"
    AUTO_N_BINNED_WITH_THRESHOLD = "auto_n_binned_with_threshold"
    AUTO_N_SIMPLE_THRESHOLD = "auto_n_simple_threshold"


def get_n_heuristic(heuristic_name: NColorsHeuristic) -> Callable:
    """Get the function that corresponds to a heuristic name.

    Args:
        heuristic_name (HeuristicName): The name of the heuristic to return.

    Raises:
        ValueError: Raised if the provided heuristic name is not recognized.

    Returns:
        Callable: The function corresponding to a heuristic name.
    """
    if heuristic_name == NColorsHeuristic.AUTO_N_HUE:
        return auto_n_hue
    elif heuristic_name == NColorsHeuristic.AUTO_N_HUE_BINNED:
        return auto_n_hue_binned
    elif heuristic_name == NColorsHeuristic.AUTO_N_BINNED_WITH_THRESHOLD:
        return auto_n_binned_with_threshold
    elif heuristic_name == NColorsHeuristic.AUTO_N_SIMPLE_THRESHOLD:
        return auto_n_simple_threshold
    else:
        raise ValueError(f"Invalid heuristic selected: {heuristic_name}")


def compute_hue_dist(image_hsv: np.ndarray, n_bins: int = PIL_NUM_HUES, hue_counts_only: bool = False) -> Dict:
    """Compute the distribution of hues for the provided image.

    Args:
        image_hsv (np.ndarray): The image for which to generate a hue distribution.
        n_bins (int, optional): The number of bins to use for the distribution. Defaults to PIL_NUM_HUES.
        hue_counts_only (bool, optional): Whether to return lists of pixel representations in the returned
            distribution, or the lengths of those lists. Defaults to False.

    Raises:
        ValueError: If an invalid hue is encountered.

    Returns:
        Dict: A distribution of hues represented by a dictionary, where keys are discrete hue values and values
            are either lists of pixel representations or the lengths of those lists.
    """
    flattened_hsv = image_hsv.reshape((image_hsv.shape[0] * image_hsv.shape[1], 3))
    n_bins = min(n_bins, PIL_NUM_HUES)

    hue_dist = {i: [] for i in range(n_bins)}
    try:
        for hsv in flattened_hsv:
            hue_dist[int(hsv[0] / (PIL_NUM_HUES / n_bins))].append(hsv)
    except KeyError as e:
        raise ValueError(f"Invalid hue value ({hsv[0]}: {e}")

    if hue_counts_only:
        hue_dist = {i: len(v) for i, v in hue_dist.items()}

    return hue_dist


def auto_n_hue(image_hsv: np.ndarray) -> int:
    """Determine the number of clusters based on the number of hues present in the provided image.

    This heuristic determines `n` using the following steps:
    - determine the number of discrete hues that are present in the provided image
    - determine the percentage of hues represented in the provided image
    - multiply the percentage of hues that are represented by 6
    - return the maximum of the computed value and 2

    Args:
        image_rgb (np.ndarray): The image to generate `n` for.

    Returns:
        int: The value of `n` (number of clusters) generated by this heuristic.
    """
    flattened_hsv = image_hsv.reshape((image_hsv.shape[0] * image_hsv.shape[1], 3))
    n_hues = set([hsv[0] for hsv in flattened_hsv])
    hue_coverage = len(n_hues) / PIL_NUM_HUES
    n_clusters = max(DEFAULT_N_COLORS_MIN, round_to_int(hue_coverage * DEFAULT_N_COLORS_MAX))
    return n_clusters


def auto_n_hue_binned(image_hsv: np.ndarray) -> int:
    """Determine the number of clusters based on the range of hues present in the provided image.

    This heuristic determines `n` using the following steps:
    - reduce the provided image to a long list of hues
    - sort the list of hues by color by distributing them into bins that are evenly spaced across the possible hue
    spectrum (i.e. [0, 30], [30, 60], ..., [150, 180])
    - determine which bin has most hues represented (which bin is the most full); set this to hue_bin_max
    - set `n` equal to the number of bins whose counts are within one standard deviation hue_bin_max

    Args:
        image_rgb (np.ndarray): The image to generate `n` for.

    Returns:
        int: The value of `n` (number of clusters) generated by this heuristic.
    """
    return auto_n_binned_with_threshold(image_hsv, threshold=0)


def auto_n_binned_with_threshold(image_hsv: np.ndarray, threshold: float = 0.1) -> int:
    """Determine the number of clusters based on the range of hues present in the provided image.

    This heuristic determines `n` using the following steps:
    - reduce the provided image to a long list of hues
    - sort the list of hues by color by distributing them into bins that are evenly spaced across the possible
    hue spectrum (i.e. [0, 30], [30, 60], ..., [150, 180])
    - determine which bin has most hues represented (which bin is the most full); set this to hue_bin_max
    - set `n` equal to the number of bins whose counts are at least at the threshold percentage of hue_bin_max
    (for instance, if the threshold is set to 0.1, then `n` is set to the number of bins whose counts are at
    least 10% of hue_bin_max)

    Args:
        image_rgb (np.ndarray): The image to generate `n` for.
        threshold (float): The threshold for determining the bin count to use for `n`.

    Returns:
        int: The value of `n` (number of clusters) generated by this heuristic.
    """
    hue_dist = compute_hue_dist(image_hsv, DEFAULT_N_COLORS_MAX, True)
    max_hue_count = np.max(list(hue_dist.values()))
    hue_count_threshold = threshold * max_hue_count
    n_clusters = sum([1 for hue_count in list(hue_dist.values()) if hue_count > hue_count_threshold])
    n_clusters = max(DEFAULT_N_COLORS_MIN, n_clusters)
    return n_clusters


def auto_n_simple_threshold(image_hsv: np.ndarray, threshold: float = 0.1) -> int:
    """Determine the number of clusters based on the range of hues present in the provided image.

    This heuristic sets `n` using the following steps:
    - reduce the provided image to a long list of hues
    - sort the list of hues by color by distributing them into bins that are evenly spaced across the possible
    hue spectrum (i.e. [0, 30], [30, 60], ..., [150, 180])
    - set `n` equal to the number of bins whose counts are at least at the threshold percentage of the total
    number of hues (for instance, if the threshold is set to 0.1, then `n` is set to the number of bins whose
    counts make up at least 10% of the total hue count)

    Args:
        image_rgb (np.ndarray): The image to generate `n` for.
        threshold (float): The threshold for determining the bin count to use for `n`.

    Returns:
        int: The value of `n` (number of clusters) generated by this heuristic.
    """
    hue_dist = compute_hue_dist(image_hsv, DEFAULT_N_COLORS_MAX, True)
    pixel_count = sum(list(hue_dist.values()))
    threhold_hue_count = threshold * pixel_count
    n_clusters = sum([1 for hue_count in list(hue_dist.values()) if hue_count > threhold_hue_count])
    n_clusters = max(DEFAULT_N_COLORS_MIN, n_clusters)
    return n_clusters
