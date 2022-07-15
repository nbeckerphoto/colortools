import numpy as np
import pytest
from colortools.analyzed_image import AnalyzedImage
from colortools.heuristics import NColorsHeuristic
from colortools.util import DominantColorAlgorithm, ImageOrientation, hsv_to_rgb, rgb_to_hsv

from conftest import ARRAY_TOLERANCE

AUTO_N_HEURISTICS = [nch for nch in NColorsHeuristic]
DOMINANT_COLOR_ALGORITHMS = [dca for dca in DominantColorAlgorithm]
TEST_IMAGE_DIR = "tests/test_images/test_analyzed_image"


def get_image_path(dimensions, color_name):
    return f"{TEST_IMAGE_DIR}/{dimensions[0]}-by-{dimensions[1]}-{color_name}.jpg"


@pytest.mark.parametrize(
    "test_dimensions, resize_long_axis, target_dimensions",
    [
        ((100, 200), 200, (100, 200)),
        ((100, 200), 100, (50, 100)),
        ((100, 200), 400, (200, 400)),
        ((100, 100), 100, (100, 100)),
        ((100, 100), 50, (50, 50)),
        ((100, 100), 200, (200, 200)),
        ((200, 100), 200, (200, 100)),
        ((200, 100), 100, (100, 50)),
        ((200, 100), 400, (400, 200)),
    ],
)
@pytest.mark.parametrize("auto_n_heuristic", AUTO_N_HEURISTICS)
def test_analyzed_image_resize(test_dimensions, resize_long_axis, target_dimensions, auto_n_heuristic):
    image_path = get_image_path(test_dimensions, "blue")
    analyzed_image = AnalyzedImage(
        image_path, resize_long_axis, DominantColorAlgorithm.HUE_DIST, None, auto_n_heuristic
    )
    assert (analyzed_image.width, analyzed_image.height) == target_dimensions


@pytest.mark.parametrize(
    "test_dimensions, resize_long_axis, target_orientation",
    [
        ((100, 200), 200, ImageOrientation.VERTICAL),
        ((100, 100), 100, ImageOrientation.HORIZONTAL),
        ((200, 100), 200, ImageOrientation.HORIZONTAL),
    ],
)
@pytest.mark.parametrize("auto_n_heuristic", AUTO_N_HEURISTICS)
def test_analyzed_image_orientation(test_dimensions, resize_long_axis, target_orientation, auto_n_heuristic):
    image_path = get_image_path(test_dimensions, "red")
    orientation = AnalyzedImage(
        image_path, resize_long_axis, DominantColorAlgorithm.HUE_DIST, None, auto_n_heuristic
    ).get_orientation()
    assert orientation == target_orientation


@pytest.mark.parametrize("dominant_color_algorithm", DOMINANT_COLOR_ALGORITHMS)
@pytest.mark.parametrize("auto_n_heuristic", AUTO_N_HEURISTICS)
def test_analyzed_image_algorithms(dominant_color_algorithm, auto_n_heuristic):
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    analyzed_image = AnalyzedImage(image_path, None, dominant_color_algorithm, None, auto_n_heuristic)
    dominant_colors_rgb = analyzed_image.get_dominant_colors()
    dominant_colors_hsv = analyzed_image.get_dominant_colors(hsv=True)
    assert len(dominant_colors_rgb) == len(dominant_colors_hsv)
    for i in range(len(dominant_colors_rgb)):
        rgb = dominant_colors_rgb[i]
        hsv = dominant_colors_hsv[i]
        np.testing.assert_allclose(rgb_to_hsv(rgb), hsv, atol=ARRAY_TOLERANCE)
        np.testing.assert_allclose(hsv_to_rgb(hsv), rgb, atol=ARRAY_TOLERANCE)


@pytest.mark.parametrize("dominant_color_algorithm", DOMINANT_COLOR_ALGORITHMS)
def test_initialization_error_n_colors_n_heuristic(dominant_color_algorithm):
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    with pytest.raises(ValueError):
        _ = AnalyzedImage(image_path, None, dominant_color_algorithm, None, None)


@pytest.mark.parametrize("n_colors", [0, None, 1])
def test_initialization_hue_dist_default_n_heuristic(n_colors):
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    analyzed_image = AnalyzedImage(
        image_path, None, DominantColorAlgorithm.HUE_DIST, n_colors, NColorsHeuristic.DEFAULT
    )
    assert analyzed_image.n_colors == 1


def test_initialization_error_bad_algorithm():
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    with pytest.raises(ValueError):
        _ = AnalyzedImage(image_path, None, "FAKE_ALGORITHM", 5, None)


@pytest.mark.parametrize(
    "test_color,target_is_bw",
    [("black", True), ("blue", False), ("gray", True), ("green", False), ("red", False), ("white", True)],
)
def test_is_bw(test_color, target_is_bw):
    image_path = get_image_path((100, 100), test_color)
    analyzed_image = AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, 1, None)
    assert analyzed_image.is_bw() == target_is_bw


@pytest.mark.parametrize("index", [None, 1, "a"])
@pytest.mark.parametrize("base", [1, "a"])
@pytest.mark.parametrize("n_colors", [1, 2, 100])
def test_generate_filename(n_colors, index, base):
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    analyzed_image = AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, n_colors, None)
    test_filename = analyzed_image.generate_filename(index, base)
    if index is not None:
        assert f"{str(index)}_" in test_filename
    assert f"{str(base)}_" in test_filename
    assert f"_n={str(n_colors)}.jpg" in test_filename
