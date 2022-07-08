import pytest
from colorsort.analyzed_image import AnalyzedImage
from colorsort.heuristics import NHeuristic
from colorsort.util import DominantColorAlgorithm, ImageOrientation

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
def test_analyzed_image_resize(test_dimensions, resize_long_axis, target_dimensions):
    image_path = get_image_path(test_dimensions, "blue")
    analyzed_image = AnalyzedImage(
        image_path, resize_long_axis, DominantColorAlgorithm.HUE_DIST, None, NHeuristic.AUTO_N_HUE
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
def test_analyzed_image_orientation(test_dimensions, resize_long_axis, target_orientation):
    image_path = get_image_path(test_dimensions, "red")
    orientation = AnalyzedImage(
        image_path, resize_long_axis, DominantColorAlgorithm.HUE_DIST, None, NHeuristic.AUTO_N_HUE
    ).orientation
    assert orientation == target_orientation
