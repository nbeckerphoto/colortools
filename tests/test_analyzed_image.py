import logging

import numpy as np
import pytest
from colortools.analyzed_image import AnalyzedImage
from colortools.heuristics import NColorsHeuristic
from colortools.util import ColorSpace, DominantColorAlgorithm, ImageOrientation, hsv_to_rgb, rgb_to_hsv, round_array

from conftest import ARRAY_TOLERANCE

AUTO_N_HEURISTICS = [nch for nch in NColorsHeuristic]
DOMINANT_COLOR_ALGORITHMS = [dca for dca in DominantColorAlgorithm]
COLOR_SPACES = [cs for cs in ColorSpace]
TEST_IMAGE_DIR = "tests/test_images/test_analyzed_image"
EDGE_CROP = 0


def get_image_path(dimensions, color_name):
    """Build the path to a solid-color test fixture of the given (width, height) and color name."""
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
    """Images are resized so their long axis matches resize_long_axis, preserving aspect ratio."""
    image_path = get_image_path(test_dimensions, "blue")
    analyzed_image = AnalyzedImage(
        image_path, resize_long_axis, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, None, auto_n_heuristic
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
    """An image's orientation is derived correctly from its (possibly resized) width and height."""
    image_path = get_image_path(test_dimensions, "red")
    orientation = AnalyzedImage(
        image_path, resize_long_axis, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, None, auto_n_heuristic
    ).get_orientation()
    assert orientation == target_orientation


@pytest.mark.parametrize("dominant_color_algorithm", DOMINANT_COLOR_ALGORITHMS)
@pytest.mark.parametrize("auto_n_heuristic", AUTO_N_HEURISTICS)
@pytest.mark.parametrize("color_space", COLOR_SPACES)
def test_analyzed_image_algorithms(dominant_color_algorithm, auto_n_heuristic, color_space):
    """Every algorithm/heuristic/color_space combo produces n_colors valid, mutually-consistent RGB/HSV colors."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    analyzed_image = AnalyzedImage(
        image_path, None, EDGE_CROP, dominant_color_algorithm, None, auto_n_heuristic, color_space
    )
    dominant_colors_rgb = analyzed_image.get_dominant_colors()
    dominant_colors_hsv = analyzed_image.get_dominant_colors(hsv=True)
    assert len(dominant_colors_rgb) == len(dominant_colors_hsv) == analyzed_image.n_colors
    for rgb, hsv in zip(dominant_colors_rgb, dominant_colors_hsv):
        assert all(0 <= channel <= 255 for channel in rgb)
        assert 0 <= hsv[0] < 360 and 0 <= hsv[1] <= 100 and 0 <= hsv[2] <= 100
        np.testing.assert_allclose(hsv_to_rgb(rgb_to_hsv(rgb)), rgb, atol=ARRAY_TOLERANCE)
        np.testing.assert_allclose(rgb_to_hsv(hsv_to_rgb(hsv)), hsv, atol=ARRAY_TOLERANCE)


def test_get_dominant_colors_kmeans_lab_cluster_histogram():
    """Clustering in Lab space still produces a valid, fully-proportioned, RGB cluster_histogram."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    n_colors = 2
    analyzed_image = AnalyzedImage(
        image_path, None, EDGE_CROP, DominantColorAlgorithm.KMEANS, n_colors, None, ColorSpace.LAB
    )
    assert len(analyzed_image.cluster_histogram) == n_colors
    proportions = [proportion for _, proportion in analyzed_image.cluster_histogram]
    assert sum(proportions) == pytest.approx(1.0, abs=1e-4)
    for rgb, _ in analyzed_image.cluster_histogram:
        assert len(rgb) == 3
        assert all(0 <= channel <= 255 for channel in rgb)


def test_get_remapped_image_lab():
    """Remapping onto itself in Lab space reproduces exactly the colors in cluster_histogram."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    n_colors = 2
    analyzed_image = AnalyzedImage(
        image_path, None, EDGE_CROP, DominantColorAlgorithm.KMEANS, n_colors, None, ColorSpace.LAB
    )
    remapped_image = analyzed_image.get_remapped_image()
    assert remapped_image.size == (analyzed_image.width, analyzed_image.height)

    # get_remapped_image rounds (rather than truncates) to uint8, so match that rule here too, to confirm
    # the remapped pixels are actually the correct cluster colors, not just few enough of them
    remapped_colors = {tuple(pixel) for pixel in np.asarray(remapped_image).reshape((-1, 3))}
    expected_colors = {tuple(np.round(rgb).astype(np.uint8).tolist()) for rgb, _ in analyzed_image.cluster_histogram}
    assert remapped_colors == expected_colors


def test_get_remapped_image_other_image():
    """Remapping a different image predicts on that image's own pixels, using this image's trained model."""
    model_image = AnalyzedImage(
        f"{TEST_IMAGE_DIR}/red-blue.jpg", None, EDGE_CROP, DominantColorAlgorithm.KMEANS, 2, None
    )
    other_image = AnalyzedImage(
        get_image_path((100, 100), "blue"), None, EDGE_CROP, DominantColorAlgorithm.KMEANS, 2, None
    )
    # model_image and other_image differ in both size and content, so a bug that remapped model_image's own
    # pixels instead of other_image's would be caught by either check below.
    assert model_image.width != other_image.width or model_image.height != other_image.height

    remapped_image = model_image.get_remapped_image(other_image)
    assert remapped_image.size == (other_image.width, other_image.height)

    # other_image is a solid color, so every pixel should collapse to exactly one of the model's clusters
    remapped_colors = {tuple(pixel) for pixel in np.asarray(remapped_image).reshape((-1, 3))}
    assert len(remapped_colors) == 1
    (remapped_color,) = remapped_colors

    # that one cluster should be the "blue" one (highest blue channel), not the "red" one
    cluster_colors = [tuple(np.round(rgb).astype(np.uint8).tolist()) for rgb, _ in model_image.cluster_histogram]
    bluest_cluster = max(cluster_colors, key=lambda rgb: rgb[2] - rgb[0])
    assert remapped_color == bluest_cluster


def test_get_remapped_image_error_hue_dist():
    """Remapping is only supported for kmeans; hue_dist raises rather than silently doing nothing."""
    analyzed_image = AnalyzedImage(
        f"{TEST_IMAGE_DIR}/red-blue.jpg", None, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, 1, None
    )
    with pytest.raises(ValueError):
        analyzed_image.get_remapped_image()


def test_get_pretty_string():
    """The pretty-printed summary assembles the filename, n_colors, algorithm, color_space, and rgb/hsv colors."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    n_colors = 2
    analyzed_image = AnalyzedImage(
        image_path, None, EDGE_CROP, DominantColorAlgorithm.KMEANS, n_colors, None, ColorSpace.LAB
    )
    pretty_string = analyzed_image.get_pretty_string()
    assert "red-blue.jpg" in pretty_string
    assert f"n={n_colors}" in pretty_string
    assert "algorithm=kmeans" in pretty_string
    assert "color_space=lab" in pretty_string
    assert str(round_array(analyzed_image.dominant_colors_rgb)) in pretty_string
    assert str(round_array(analyzed_image.dominant_colors_hsv)) in pretty_string


def test_initialization_error_n_colors_n_heuristic(caplog):
    """With kmeans and neither n_colors nor an auto heuristic given, n_colors defaults to 1 with a warning."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    with caplog.at_level(logging.WARNING):
        _ = AnalyzedImage(image_path, None, EDGE_CROP, DominantColorAlgorithm.KMEANS, None, None)

    assert "setting n_colors=1" in caplog.text


@pytest.mark.parametrize("n_colors", [0, None])
def test_initialization_hue_dist_default_n_heuristic(n_colors):
    """A falsy n_colors (0 or None) defaults to 1 for hue_dist even without an auto heuristic."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    analyzed_image = AnalyzedImage(image_path, None, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, n_colors, None)
    assert analyzed_image.n_colors == 1


def test_initialization_error_bad_algorithm():
    """An unrecognized dominant_color_algorithm value raises rather than silently doing nothing."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    with pytest.raises(ValueError):
        _ = AnalyzedImage(image_path, None, EDGE_CROP, "FAKE_ALGORITHM", 5, None)


def test_get_dominant_colors_hue_dist_error_n_colors_too_large():
    """n_colors larger than the number of available hue bins raises a clear error, not an IndexError."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    with pytest.raises(ValueError):
        _ = AnalyzedImage(image_path, None, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, 300, None)


def test_get_dominant_colors_hue_dist_cluster_histogram():
    """hue_dist builds a valid, fully-proportioned cluster_histogram, matching kmeans's shape/invariants."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    n_colors = 2
    analyzed_image = AnalyzedImage(image_path, None, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, n_colors, None)
    assert len(analyzed_image.cluster_histogram) == n_colors
    proportions = [proportion for _, proportion in analyzed_image.cluster_histogram]
    assert sum(proportions) == pytest.approx(1.0, abs=1e-4)
    for rgb, _ in analyzed_image.cluster_histogram:
        assert len(rgb) == 3
        assert all(0 <= channel <= 255 for channel in rgb)


@pytest.mark.parametrize(
    "test_color,target_is_bw",
    [("black", True), ("blue", False), ("gray", True), ("green", False), ("red", False), ("white", True)],
)
def test_is_bw(test_color, target_is_bw):
    """is_bw() correctly classifies solid black/white/gray images as bw and solid hues as color."""
    image_path = get_image_path((100, 100), test_color)
    analyzed_image = AnalyzedImage(image_path, None, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, 1, None)
    assert analyzed_image.is_bw() == target_is_bw


@pytest.mark.parametrize("index", [None, 1, "a"])
@pytest.mark.parametrize("base", [1, "a"])
@pytest.mark.parametrize("n_colors", [1, 2, 100])
@pytest.mark.parametrize("color_space", [ColorSpace.RGB, ColorSpace.LAB])
def test_generate_filename(n_colors, index, base, color_space):
    """Generated filenames include the given index (if any), base string, n_colors, and color_space."""
    image_path = f"{TEST_IMAGE_DIR}/red-blue.jpg"
    analyzed_image = AnalyzedImage(
        image_path, None, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, n_colors, None, color_space
    )
    test_filename = analyzed_image.generate_filename(index, base)
    if index is not None:
        assert f"{str(index)}_" in test_filename
    assert f"{str(base)}_" in test_filename
    assert f"_n={str(n_colors)}_cs={color_space.value}.jpg" in test_filename
