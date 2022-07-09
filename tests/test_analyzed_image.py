import numpy as np
import pytest
from colorsort.analyzed_image import AnalyzedImage
from colorsort.heuristics import NHeuristic
from colorsort.util import DominantColorAlgorithm, ImageOrientation, rgb_to_hsv, hsv_to_rgb

from conftest import get_image_path

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
@pytest.mark.parametrize(
    "auto_n_heuristic",
    [
        NHeuristic.AUTO_N_HUE,
        NHeuristic.AUTO_N_HUE_BINNED,
        NHeuristic.AUTO_N_BINNED_WITH_THRESHOLD,
        NHeuristic.AUTO_N_SIMPLE_THRESHOLD,
    ],
)
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
@pytest.mark.parametrize(
    "auto_n_heuristic",
    [
        NHeuristic.AUTO_N_HUE,
        NHeuristic.AUTO_N_HUE_BINNED,
        NHeuristic.AUTO_N_BINNED_WITH_THRESHOLD,
        NHeuristic.AUTO_N_SIMPLE_THRESHOLD,
    ],
)
def test_analyzed_image_orientation(test_dimensions, resize_long_axis, target_orientation, auto_n_heuristic):
    image_path = get_image_path(test_dimensions, "red")
    orientation = AnalyzedImage(
        image_path, resize_long_axis, DominantColorAlgorithm.HUE_DIST, None, auto_n_heuristic
    ).orientation
    assert orientation == target_orientation


@pytest.mark.parametrize("dominant_color_algorithm", [DominantColorAlgorithm.HUE_DIST, DominantColorAlgorithm.KMEANS])
@pytest.mark.parametrize(
    "auto_n_heuristic",
    [
        NHeuristic.AUTO_N_HUE,
        NHeuristic.AUTO_N_HUE_BINNED,
        NHeuristic.AUTO_N_BINNED_WITH_THRESHOLD,
        NHeuristic.AUTO_N_SIMPLE_THRESHOLD,
    ],
)
def test_analyzed_image_algorithms(dominant_color_algorithm, auto_n_heuristic):
    image_path = f"tests/test_images/red-blue.jpg"
    analyzed_image = AnalyzedImage(image_path, None, dominant_color_algorithm, None, auto_n_heuristic)
    dominant_colors_rgb = analyzed_image.get_dominant_colors()
    dominant_colors_hsv = analyzed_image.get_dominant_colors(hsv=True)
    assert len(dominant_colors_rgb) == len(dominant_colors_hsv)
    for i in range(len(dominant_colors_rgb)):
        rgb = dominant_colors_rgb[i]
        hsv = dominant_colors_hsv[i]
        np.testing.assert_allclose(rgb_to_hsv(rgb), hsv, atol=1)  # TODO: round dominant colors only when needed
