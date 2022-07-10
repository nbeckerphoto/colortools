import pytest
from colorsort.analyzed_image import AnalyzedImage
from colorsort.sort import colorsort
from colorsort.util import DominantColorAlgorithm

from conftest import get_image_path


def test_colorsort():
    dims = (100, 100)
    colors = ["black", "blue", "gray", "green", "red", "white"]
    image_paths = [get_image_path(dims, color) for color in colors]
    analyzed_images = [
        AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, 1, None) for image_path in image_paths
    ]

    sorted_all, sorted_color, sorted_bw = colorsort(analyzed_images, None)
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
def test_colorsort_with_anchor(anchor_image, target_color):
    dims = (100, 100)
    colors = ["black", "blue", "gray", "green", "red", "white"]
    image_paths = [get_image_path(dims, color) for color in colors]
    analyzed_images = [
        AnalyzedImage(image_path, None, DominantColorAlgorithm.HUE_DIST, 1, None) for image_path in image_paths
    ]

    sorted_all, sorted_color, sorted_bw = colorsort(analyzed_images, anchor_image)

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
