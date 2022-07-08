import pytest
import colorsort.util as util

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
    assert util.rgb_to_hsv(test_rgb) == test_hsv


@pytest.mark.parametrize("test_rgb,test_hsv", rgb_hsv_pairs)
def test_hsv_to_rgb(test_rgb, test_hsv):
    assert util.hsv_to_rgb(test_hsv) == test_rgb
