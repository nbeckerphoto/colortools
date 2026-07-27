from pathlib import Path

import pytest
from colortools.analyzed_image import AnalyzedImage
from colortools.sort import get_sort_function, huesort, satsort, valsort
from colortools.util import DominantColorAlgorithm

TEST_IMAGE_DIR = "tests/test_images/test_sort"
EDGE_CROP = 0


def load_analyzed_images():
    """Load every test fixture image in TEST_IMAGE_DIR, in filesystem (i.e. arbitrary) order."""
    test_image_dir = Path(TEST_IMAGE_DIR)
    image_paths = list(test_image_dir.glob("*.jpg"))
    return [
        AnalyzedImage(image_path, None, EDGE_CROP, DominantColorAlgorithm.HUE_DIST, 1, None)
        for image_path in image_paths
    ]


@pytest.mark.parametrize(
    "sort_method,expected",
    [("hue", "huesort"), ("saturation", "satsort"), ("value", "valsort")],
)
def test_get_sort_function(sort_method, expected):
    """Each sort method name resolves to its corresponding sort function."""
    func = get_sort_function(sort_method)
    assert func.__name__ == expected


def test_bad_get_sort_function():
    """An unrecognized sort method name raises rather than silently returning nothing."""
    with pytest.raises(ValueError):
        _ = get_sort_function("fake")


@pytest.mark.parametrize("sort_reverse", [False, True])
def test_huesort(sort_reverse):
    """huesort orders color images by hue (then value, then saturation) with bw images always last."""
    target_color_sorted = [
        "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
        "0-100-50.jpg",
        "0-100-100.jpg",
        "120-100-50.jpg",
        "120-50-100.jpg",
        "120-100-100.jpg",
        "240-100-50.jpg",
        "240-50-100.jpg",
        "240-100-100.jpg",
    ]
    target_bw_sorted = ["0-0-0.jpg", "0-0-50.jpg", "0-0-100.jpg"]

    expected = []
    if not sort_reverse:
        expected.extend(target_color_sorted)
        expected.extend(target_bw_sorted)
    else:
        target_color_sorted.reverse()
        target_bw_sorted.reverse()
        expected.extend(target_color_sorted)
        expected.extend(target_bw_sorted)

    sorted_all = huesort(load_analyzed_images(), sort_reverse, None)
    results = [image.image_path.name for image in sorted_all]
    assert results == expected


@pytest.mark.parametrize(
    "anchor_image,target_color_sorted",
    [
        (
            "0-50-100.jpg",
            [
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-100-50.jpg",
                "0-100-100.jpg",
                "120-100-50.jpg",
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-100-50.jpg",
                "240-50-100.jpg",
                "240-100-100.jpg",
            ],
        ),
        (
            "fake.jpg",
            [
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-100-50.jpg",
                "0-100-100.jpg",
                "120-100-50.jpg",
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-100-50.jpg",
                "240-50-100.jpg",
                "240-100-100.jpg",
            ],
        ),
        (
            "0-100-100.jpg",
            [
                "0-100-100.jpg",
                "120-100-50.jpg",
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-100-50.jpg",
                "240-50-100.jpg",
                "240-100-100.jpg",
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-100-50.jpg",
            ],
        ),
        (
            "120-50-100.jpg",
            [
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-100-50.jpg",
                "240-50-100.jpg",
                "240-100-100.jpg",
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-100-50.jpg",
                "0-100-100.jpg",
                "120-100-50.jpg",
            ],
        ),
        (
            "240-100-100.jpg",
            [
                "240-100-100.jpg",
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-100-50.jpg",
                "0-100-100.jpg",
                "120-100-50.jpg",
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-100-50.jpg",
                "240-50-100.jpg",
            ],
        ),
    ],
)
def test_huesorts_with_anchor(anchor_image, target_color_sorted):
    """huesort rotates the color-sorted sequence to start at the given anchor image (or not, if not found)."""
    expected = list(target_color_sorted)
    expected.extend(["0-0-0.jpg", "0-0-50.jpg", "0-0-100.jpg"])

    sorted_all = huesort(load_analyzed_images(), False, anchor_image)
    results = [image.image_path.name for image in sorted_all]
    assert results == expected


@pytest.mark.parametrize("sort_reverse", [False, True])
def test_satsort(sort_reverse):
    """satsort orders all images by saturation, then value, then hue."""
    expected = [
        "0-0-0.jpg",
        "0-0-50.jpg",
        "0-0-100.jpg",
        "0-50-100.jpg",
        "120-50-100.jpg",
        "240-50-100.jpg",
        "0-100-50.jpg",
        "120-100-50.jpg",
        "240-100-50.jpg",
        "0-100-100.jpg",
        "120-100-100.jpg",
        "240-100-100.jpg",
    ]

    if sort_reverse:
        expected.reverse()

    sorted_all = satsort(load_analyzed_images(), sort_reverse, None)
    results = [image.image_path.name for image in sorted_all]
    assert results == expected


@pytest.mark.parametrize(
    "anchor_image,expected",
    [
        (
            "0-0-0.jpg",
            [
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-0-100.jpg",
                "0-50-100.jpg",
                "120-50-100.jpg",
                "240-50-100.jpg",
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-100-100.jpg",
                "120-100-100.jpg",
                "240-100-100.jpg",
            ],
        ),
        (
            "fake.jpg",
            [
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-0-100.jpg",
                "0-50-100.jpg",
                "120-50-100.jpg",
                "240-50-100.jpg",
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-100-100.jpg",
                "120-100-100.jpg",
                "240-100-100.jpg",
            ],
        ),
        (
            "0-50-100.jpg",
            [
                "0-50-100.jpg",
                "120-50-100.jpg",
                "240-50-100.jpg",
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-100-100.jpg",
                "120-100-100.jpg",
                "240-100-100.jpg",
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-0-100.jpg",
            ],
        ),
        (
            "120-100-50.jpg",
            [
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-100-100.jpg",
                "120-100-100.jpg",
                "240-100-100.jpg",
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-0-100.jpg",
                "0-50-100.jpg",
                "120-50-100.jpg",
                "240-50-100.jpg",
                "0-100-50.jpg",
            ],
        ),
        (
            "240-100-100.jpg",
            [
                "240-100-100.jpg",
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-0-100.jpg",
                "0-50-100.jpg",
                "120-50-100.jpg",
                "240-50-100.jpg",
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-100-100.jpg",
                "120-100-100.jpg",
            ],
        ),
    ],
)
def test_satsort_with_anchor(anchor_image, expected):
    """satsort rotates the saturation-sorted sequence to start at the given anchor image (or not, if not found)."""
    sorted_all = satsort(load_analyzed_images(), False, anchor_image)
    results = [image.image_path.name for image in sorted_all]
    assert results == expected


@pytest.mark.parametrize("sort_reverse", [False, True])
def test_valsort(sort_reverse):
    """valsort orders all images by value, then hue, then saturation."""
    expected = [
        "0-0-0.jpg",
        "0-0-50.jpg",
        "0-100-50.jpg",
        "120-100-50.jpg",
        "240-100-50.jpg",
        "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
        "0-0-100.jpg",
        "0-100-100.jpg",
        "120-50-100.jpg",
        "120-100-100.jpg",
        "240-50-100.jpg",
        "240-100-100.jpg",
    ]

    if sort_reverse:
        expected.reverse()

    sorted_all = valsort(load_analyzed_images(), sort_reverse, None)
    results = [image.image_path.name for image in sorted_all]
    assert results == expected


@pytest.mark.parametrize(
    "anchor_image,expected",
    [
        (
            "0-0-0.jpg",
            [
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-0-100.jpg",
                "0-100-100.jpg",
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-50-100.jpg",
                "240-100-100.jpg",
            ],
        ),
        (
            "fake.jpg",
            [
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-0-100.jpg",
                "0-100-100.jpg",
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-50-100.jpg",
                "240-100-100.jpg",
            ],
        ),
        (
            "0-100-50.jpg",
            [
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-0-100.jpg",
                "0-100-100.jpg",
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-50-100.jpg",
                "240-100-100.jpg",
                "0-0-0.jpg",
                "0-0-50.jpg",
            ],
        ),
        (
            "120-50-100.jpg",
            [
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-50-100.jpg",
                "240-100-100.jpg",
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-0-100.jpg",
                "0-100-100.jpg",
            ],
        ),
        (
            "240-100-100.jpg",
            [
                "240-100-100.jpg",
                "0-0-0.jpg",
                "0-0-50.jpg",
                "0-100-50.jpg",
                "120-100-50.jpg",
                "240-100-50.jpg",
                "0-50-100.jpg",  # actual: [358.5882352941177, 49.411764705882355, 99.6078431372549]
                "0-0-100.jpg",
                "0-100-100.jpg",
                "120-50-100.jpg",
                "120-100-100.jpg",
                "240-50-100.jpg",
            ],
        ),
    ],
)
def test_valuesort_with_anchor(anchor_image, expected):
    """valsort rotates the value-sorted sequence to start at the given anchor image (or not, if not found)."""
    sorted_all = valsort(load_analyzed_images(), False, anchor_image)
    for s in sorted_all:
        print(s.get_dominant_color(True))
    results = [image.image_path.name for image in sorted_all]
    assert results == expected
