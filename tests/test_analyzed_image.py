import numpy as np
import pytest
from colorsort.analyzed_image import AnalyzedImage
from colorsort.heuristics import NHeuristic
from colorsort.util import DominantColorAlgorithm, ImageOrientation, hsv_to_rgb, rgb_to_hsv

from conftest import ARRAY_TOLERANCE, get_image_path

AUTO_N_HEURISTICS = [
    NHeuristic.AUTO_N_HUE,
    NHeuristic.AUTO_N_HUE_BINNED,
    NHeuristic.AUTO_N_BINNED_WITH_THRESHOLD,
    NHeuristic.AUTO_N_SIMPLE_THRESHOLD,
]

DOMINANT_COLOR_ALGORITHMS = [DominantColorAlgorithm.HUE_DIST, DominantColorAlgorithm.KMEANS]


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
    image_path = "tests/test_images/red-blue.jpg"
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
    image_path = "tests/test_images/red-blue.jpg"
    with pytest.raises(ValueError):
        _ = AnalyzedImage(image_path, None, dominant_color_algorithm, None, None)


def test_initialization_error_bad_algorithm():
    image_path = "tests/test_images/red-blue.jpg"
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
    image_path = "tests/test_images/red-blue.jpg"
    analyzed_image = AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, n_colors, None)
    test_filename = analyzed_image.generate_filename(index, base)
    if index is not None:
        assert f"{str(index)}_" in test_filename
    assert f"{str(base)}_" in test_filename
    assert f"_n={str(n_colors)}.jpg" in test_filename


def test_colorsort():
    dims = (100, 100)
    colors = ["black", "blue", "gray", "green", "red", "white"]
    image_paths = [get_image_path(dims, color) for color in colors]
    analyzed_images = [
        AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, 1, None) for image_path in image_paths
    ]

    sorted_all, sorted_color, sorted_bw = AnalyzedImage.colorsort(analyzed_images, None)
    sorted_all_filenames = [image.image_path.name for image in sorted_all]
    assert sorted_all_filenames == [
        "100-by-100-red.jpg",
        "100-by-100-green.jpg",
        "100-by-100-blue.jpg",
        "100-by-100-black.jpg",
        "100-by-100-gray.jpg",
        "100-by-100-white.jpg",
    ]

    sorted_color_filenames = [image.image_path.name for image in sorted_color]
    assert sorted_color_filenames == [
        "100-by-100-red.jpg",
        "100-by-100-green.jpg",
        "100-by-100-blue.jpg",
    ]

    sorted_bw_filenames = [image.image_path.name for image in sorted_bw]
    assert sorted_bw_filenames == [
        "100-by-100-black.jpg",
        "100-by-100-gray.jpg",
        "100-by-100-white.jpg",
    ]


@pytest.mark.parametrize(
    "anchor_image,target_color",
    [
        ("100-by-100-red.jpg", ["100-by-100-red.jpg", "100-by-100-green.jpg", "100-by-100-blue.jpg"]),
        ("100-by-100-green.jpg", ["100-by-100-green.jpg", "100-by-100-blue.jpg", "100-by-100-red.jpg"]),
        ("100-by-100-blue.jpg", ["100-by-100-blue.jpg", "100-by-100-red.jpg", "100-by-100-green.jpg"]),
        ("100-by-100-white.jpg", ["100-by-100-red.jpg", "100-by-100-green.jpg", "100-by-100-blue.jpg"]),
    ],
)
def test_colorsortw_with_anchor(anchor_image, target_color):
    dims = (100, 100)
    colors = ["black", "blue", "gray", "green", "red", "white"]
    image_paths = [get_image_path(dims, color) for color in colors]
    analyzed_images = [
        AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, 1, None) for image_path in image_paths
    ]

    sorted_all, sorted_color, sorted_bw = AnalyzedImage.colorsort(analyzed_images, anchor_image)

    target_bw = [
        "100-by-100-black.jpg",
        "100-by-100-gray.jpg",
        "100-by-100-white.jpg",
    ]
    target_all = list(target_color)
    target_all.extend(target_bw)

    sorted_all_filenames = [image.image_path.name for image in sorted_all]
    assert sorted_all_filenames == target_all

    sorted_color_filenames = [image.image_path.name for image in sorted_color]
    assert sorted_color_filenames == target_color

    sorted_bw_filenames = [image.image_path.name for image in sorted_bw]
    assert sorted_bw_filenames == target_bw
