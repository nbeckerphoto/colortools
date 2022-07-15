from datetime import datetime
from pathlib import Path

import colortools.util as util
import numpy as np
import pytest

from conftest import ARRAY_TOLERANCE

TEST_IMAGE_DIR = "tests/test_images/test_sort"

RGB_HSV_PAIRS = [
    ([0, 0, 0], [0, 0, 0]),
    ([255, 255, 255], [0, 0, 100]),
    ([255, 0, 0], [0, 100, 100]),
    ([255, 255, 0], [60, 100, 100]),
    ([0, 255, 0], [120, 100, 100]),
    ([0, 255, 255], [180, 100, 100]),
    ([0, 0, 255], [240, 100, 100]),
    ([255, 0, 255], [300, 100, 100]),
    ([128, 128, 128], [0, 0, 50]),
    ([128, 64, 64], [0, 50, 50]),
    ([128, 128, 64], [60, 50, 50]),
    ([64, 128, 64], [120, 50, 50]),
    ([64, 128, 128], [180, 50, 50]),
    ([64, 64, 128], [240, 50, 50]),
    ([128, 64, 128], [300, 50, 50]),
    ([64, 48, 64], [300, 25, 25]),
]


@pytest.mark.parametrize(
    "orientation, expected",
    [
        (util.ImageOrientation.HORIZONTAL, util.ImageOrientation.VERTICAL),
        (util.ImageOrientation.VERTICAL, util.ImageOrientation.HORIZONTAL),
        (util.ImageOrientation.AUTO, util.ImageOrientation.AUTO),
    ],
)
def test_image_orientation_rotate(orientation, expected):
    assert orientation.rotate() == expected


def test_get_timestamp_string():
    ts_str = util.get_timestamp_string()
    try:
        _ = datetime.strptime(ts_str, "%Y%m%d%H%M%S")
        parseable = True
    except:  # noqa
        parseable = False
    assert parseable


@pytest.mark.parametrize("input_dir", [TEST_IMAGE_DIR, Path(TEST_IMAGE_DIR)])
def test_collect_jpg_paths(input_dir):
    expected = [
        f"{TEST_IMAGE_DIR}/0-0-0.jpg",
        f"{TEST_IMAGE_DIR}/0-0-50.jpg",
        f"{TEST_IMAGE_DIR}/0-0-100.jpg",
        f"{TEST_IMAGE_DIR}/0-50-100.jpg",
        f"{TEST_IMAGE_DIR}/0-100-50.jpg",
        f"{TEST_IMAGE_DIR}/0-100-100.jpg",
        f"{TEST_IMAGE_DIR}/120-50-100.jpg",
        f"{TEST_IMAGE_DIR}/120-100-50.jpg",
        f"{TEST_IMAGE_DIR}/120-100-100.jpg",
        f"{TEST_IMAGE_DIR}/240-50-100.jpg",
        f"{TEST_IMAGE_DIR}/240-100-50.jpg",
        f"{TEST_IMAGE_DIR}/240-100-100.jpg",
    ]
    expected = set([Path(p) for p in expected])
    results = set(util.collect_jpg_paths(input_dir))
    assert results == expected


@pytest.mark.parametrize("input_file", [f"{TEST_IMAGE_DIR}/0-0-0.jpg", Path(f"{TEST_IMAGE_DIR}/0-0-0.jpg")])
def test_collect_jpg_paths_one_file(input_file):
    expected = [Path(f"{TEST_IMAGE_DIR}/0-0-0.jpg")]
    results = util.collect_jpg_paths(input_file)
    assert results == expected


@pytest.mark.parametrize("test_rgb, test_hsv", RGB_HSV_PAIRS)
def test_rgb_to_hsv(test_rgb, test_hsv):
    np.testing.assert_allclose(util.rgb_to_hsv(test_rgb), test_hsv, atol=ARRAY_TOLERANCE)


@pytest.mark.parametrize(
    "input, expected",
    [
        ((0, 0, 0), [0, 0, 0]),
        ([0, 0, 0], [0, 0, 0]),
        ([[255, 0, 0], [0, 255, 0], [0, 0, 255]], [[0, 0, 0], [0, 100, 0], [0, 0, 100]]),
        ([[128, 0, 0], [0, 128, 0], [0, 0, 128]], [[180, 0, 0], [0, 50, 0], [0, 0, 50]]),
    ],
)
def test_normalize_8bit_hsv(input, expected):
    np.testing.assert_allclose(util.normalize_8bit_hsv(input), expected, atol=ARRAY_TOLERANCE)


@pytest.mark.parametrize("test_rgb, test_hsv", RGB_HSV_PAIRS)
def test_hsv_to_rgb(test_rgb, test_hsv):
    np.testing.assert_allclose(util.hsv_to_rgb(test_hsv), test_rgb, atol=ARRAY_TOLERANCE)


@pytest.mark.parametrize(
    "test_input, target_output",
    [
        (0, 0),
        (0.0001, 0),
        (0.5, 1),
        (0.9999, 1),
        (1.0001, 1),
        (1.4999, 1),
        (1.5, 2),
        (1.50001, 2),
    ],
)
def test_round_to_int(test_input, target_output):
    assert util.round_to_int(test_input) == target_output
