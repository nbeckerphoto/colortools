import pytest
from colortools.heuristics import (
    NColorsHeuristic,
    auto_n_binned_with_threshold,
    auto_n_hue,
    auto_n_hue_binned,
    auto_n_simple_threshold,
    compute_hue_dist,
    get_n_heuristic,
)

from conftest import get_hsv_array


@pytest.mark.parametrize(
    "n_hues, n_bins, expected_count",
    [
        (10, 2, {0: 10}),
        (129, 2, {0: 128, 1: 1}),
        (256, 256, {i: 1 for i in range(256)}),
        (256, 128, {i: 2 for i in range(128)}),
        (256, 8, {i: 32 for i in range(8)}),
    ],
)
def test_get_hue_dist_simple(n_hues, n_bins, expected_count):
    test_input = get_hsv_array(n_hues)
    hue_dist = compute_hue_dist(test_input, n_bins, hue_counts_only=True)
    expected = {i: 0 for i in range(n_bins)}
    expected.update(expected_count)
    assert hue_dist == expected


def test_get_hue_dist_exception():
    test_input = get_hsv_array(257)
    with pytest.raises(ValueError):
        _ = compute_hue_dist(test_input)


@pytest.mark.parametrize(
    "test_hue_number, expected_n", [(1, 2), (51, 2), (80, 3), (160, 5), (239, 7), (240, 8), (256, 8)]
)
def test_auto_n_hue(test_hue_number, expected_n):
    test_input = get_hsv_array(test_hue_number)
    n = auto_n_hue(test_input)
    assert n == expected_n


@pytest.mark.parametrize(
    "test_hue_number, distribute_hues, expected_n",
    [
        (1, False, 2),
        (32, False, 2),
        (64, False, 2),
        (65, False, 3),
        (160, False, 5),
        (242, False, 8),
        (256, False, 8),
        (1, True, 2),
        (2, True, 2),
        (3, True, 3),
        (5, True, 5),
        (8, True, 8),
        (9, True, 8),
        (256, True, 8),
    ],
)
def test_auto_n_hue_binned(test_hue_number, distribute_hues, expected_n):
    test_input = get_hsv_array(test_hue_number, distribute_hues)
    n = auto_n_hue_binned(test_input)
    assert n == expected_n


@pytest.mark.parametrize(
    "test_hue_number, distribute_hues, extra_hues, threshold, expected_n",
    [
        (1, False, [], 0, 2),
        (32, False, [], 0, 2),
        (64, False, [], 0, 2),
        (65, False, [], 0, 3),
        (160, False, [], 0, 5),
        (242, False, [], 0, 8),
        (256, False, [], 0, 8),
        (8, True, [], 0, 8),
        (8, True, [1] * 4, 0.1, 8),  # max_hue_count = 5, hue_count_threshold = 0.5
        (8, True, [1] * 4, 0.2, 2),  # max_hue_count = 5, hue_count_threshold = 1
        (8, True, [1, 1, 1, 1, 33], 0.2, 2),  # max_hue_count = 5, hue_count_threshold = 1
        (8, True, [1, 1, 1, 1, 33, 65], 0.1, 8),  # max_hue_count = 5, hue_count_threshold = 0.5
        (8, True, [1, 1, 1, 1, 33, 65], 0.2, 3),  # max_hue_count = 5, hue_count_threshold = 1
        (8, True, [1, 1, 1, 1, 33, 65], 0.4, 2),  # max_hue_count = 5, hue_count_threshold = 2
        (8, True, [1, 1, 1, 1, 33, 33, 65, 65], 0.1, 8),  # max_hue_count = 5, hue_count_threshold = 0.5
        (8, True, [1, 1, 1, 1, 33, 33, 65, 65], 0.2, 3),  # max_hue_count = 5, hue_count_threshold = 1
        (8, True, [1, 1, 1, 1, 33, 33, 65, 65], 0.4, 3),  # max_hue_count = 5, hue_count_threshold = 2
        (8, True, [1, 1, 1, 1, 33, 33, 65], 0.1, 8),  # max_hue_count = 5, hue_count_threshold = 0.5
        (8, True, [1, 1, 1, 1, 33, 33, 65], 0.2, 3),  # max_hue_count = 5, hue_count_threshold = 1
        (8, True, [1, 1, 1, 1, 33, 33, 65], 0.4, 2),  # max_hue_count = 5, hue_count_threshold = 2
    ],
)
def test_auto_n_hue_binned_with_threshold(test_hue_number, distribute_hues, extra_hues, threshold, expected_n):
    test_input = get_hsv_array(test_hue_number, distribute_hues, extra_hues)
    n = auto_n_binned_with_threshold(test_input, threshold)
    assert n == expected_n


@pytest.mark.parametrize(
    "test_hue_number, distribute_hues, extra_hues, threshold, expected_n",
    [
        (1, False, [], 0, 2),
        (32, False, [], 0, 2),
        (64, False, [], 0, 2),
        (65, False, [], 0, 3),
        (160, False, [], 0, 5),
        (242, False, [], 0, 8),
        (256, False, [], 0, 8),
        (8, True, [], 0, 8),
        (8, True, [1] * 4, 0.05, 8),  # pixel_count = 12, threhold_hue_count = 0.6
        (8, True, [1] * 4, 0.1, 2),  # pixel_count = 12, threhold_hue_count = 2.4
        (8, True, [1, 1, 1, 1, 33, 33], 0.05, 8),  # pixel_count = 14, hue_count_threshold = 0.7
        (8, True, [1, 1, 1, 1, 33, 33], 0.1, 2),  # pixel_count = 14, hue_count_threshold = 1.4
        (8, True, [1, 1, 1, 1, 33, 33], 0.2, 2),  # pixel_count = 14, hue_count_threshold = 1.4
        (8, True, [1, 1, 1, 1, 33, 33, 65], 0.05, 8),  # pixel_count = 15, hue_count_threshold = 0.75
        (8, True, [1, 1, 1, 1, 33, 33, 65], 0.1, 3),  # pixel_count = 15, hue_count_threshold = 1.5
        (8, True, [1, 1, 1, 1, 33, 33, 65], 0.2, 2),  # pixel_count = 15, hue_count_threshold = 2.25
        (8, True, [1, 1, 1, 1, 33, 33, 65, 65], 0.05, 8),  # pixel_count = 16, hue_count_threshold = 0.8
        (8, True, [1, 1, 1, 1, 33, 33, 65, 65], 0.1, 3),  # pixel_count = 16, hue_count_threshold = 1.6
        (8, True, [1, 1, 1, 1, 33, 33, 65, 65], 0.2, 2),  # pixel_count = 16, hue_count_threshold = 3.2
        (8, True, [1, 1, 1, 1, 33, 33, 33, 65, 65], 0.05, 8),  # pixel_count = 19, hue_count_threshold = 0.95
        (8, True, [1, 1, 1, 1, 33, 33, 33, 65, 65], 0.1, 3),  # pixel_count = 19, hue_count_threshold = 1.9
        (8, True, [1, 1, 1, 1, 33, 33, 33, 65, 65], 0.2, 2),  # pixel_count = 19, hue_count_threshold = 3.8
        (8, True, [1, 1, 1, 1, 33, 33, 33, 33, 65], 0.05, 8),  # pixel_count = 19, hue_count_threshold = 3.8
        (8, True, [1, 1, 1, 1, 33, 33, 33, 33, 65], 0.1, 3),  # pixel_count = 19, hue_count_threshold = 1.9
        (8, True, [1, 1, 1, 1, 33, 33, 33, 33, 65], 0.2, 2),  # pixel_count = 19, hue_count_threshold = 3.8
    ],
)
def test_auto_n_simple_threshold(test_hue_number, distribute_hues, extra_hues, threshold, expected_n):
    test_input = get_hsv_array(test_hue_number, distribute_hues, extra_hues)
    n = auto_n_simple_threshold(test_input, threshold)
    assert n == expected_n


def test_get_n_heuristic_default():
    expected = auto_n_binned_with_threshold
    test_default = get_n_heuristic(NColorsHeuristic.DEFAULT)
    assert test_default == expected


def test_get_n_heuristic_bad():
    with pytest.raises(ValueError):
        _ = get_n_heuristic("FAKE")
