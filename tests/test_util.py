import colortools.util as util
import numpy as np
import pytest

from conftest import ARRAY_TOLERANCE

rgb_hsv_pairs = [
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


@pytest.mark.parametrize("test_rgb,test_hsv", rgb_hsv_pairs)
def test_rgb_to_hsv(test_rgb, test_hsv):
    np.testing.assert_allclose(util.rgb_to_hsv(test_rgb), test_hsv, atol=ARRAY_TOLERANCE)


@pytest.mark.parametrize("test_rgb,test_hsv", rgb_hsv_pairs)
def test_hsv_to_rgb(test_rgb, test_hsv):
    np.testing.assert_allclose(util.hsv_to_rgb(test_hsv), test_rgb, atol=ARRAY_TOLERANCE)


@pytest.mark.parametrize(
    "test_input,target_output",
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
