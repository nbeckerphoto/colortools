import pytest
from colortools.analyzed_image import AnalyzedImage
from colortools.sort import colorsort
from colortools.util import DominantColorAlgorithm

from conftest import get_image_path


def test_colorsort():
    dims = (100, 100)
    colors = ["black", "blue", "gray", "green", "red", "white"]
    image_paths = [get_image_path(dims, color) for color in colors]
    analyzed_images = [
        AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, 1, None) for image_path in image_paths
    ]

    sorted_all = colorsort(analyzed_images, None)
    sorted_all_filenames = [image.image_path.name for image in sorted_all]
    assert sorted_all_filenames == [
        "100-by-100-red.jpg",
        "100-by-100-green.jpg",
        "100-by-100-blue.jpg",
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
def test_colorsort_with_anchor(anchor_image, target_color):
    dims = (100, 100)
    colors = ["black", "blue", "gray", "green", "red", "white"]
    image_paths = [get_image_path(dims, color) for color in colors]
    analyzed_images = [
        AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, 1, None) for image_path in image_paths
    ]

    sorted_all = colorsort(analyzed_images, anchor_image)

    target_bw = [
        "100-by-100-black.jpg",
        "100-by-100-gray.jpg",
        "100-by-100-white.jpg",
    ]
    target_all = list(target_color)
    target_all.extend(target_bw)

    sorted_all_filenames = [image.image_path.name for image in sorted_all]
    assert sorted_all_filenames == target_all
