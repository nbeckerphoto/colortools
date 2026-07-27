import logging

import colortools.config as config
import colortools.visualization as visualization
import numpy as np
import pytest
from colortools.analyzed_image import AnalyzedImage
from colortools.util import DominantColorAlgorithm, ImageOrientation, round_to_int
from PIL import Image

TEST_IMAGE_DIR = "tests/test_images/test_analyzed_image"
EDGE_CROP = 0


def load_analyzed_image(color_name, n_colors=1, algorithm=DominantColorAlgorithm.HUE_DIST):
    """Load one of the solid-color 100x100 test fixtures as an AnalyzedImage."""
    image_path = f"{TEST_IMAGE_DIR}/100-by-100-{color_name}.jpg"
    return AnalyzedImage(image_path, None, EDGE_CROP, algorithm, n_colors, None)


def test_save_analyzed_image_hardlinks(tmp_path):
    """Saving an AnalyzedImage hard-links to the original file rather than copying it."""
    analyzed_image = load_analyzed_image("red")
    dest = tmp_path / "out" / "linked.jpg"
    visualization.save(analyzed_image, dest)
    assert dest.exists()
    assert dest.stat().st_ino == analyzed_image.image_path.stat().st_ino


def test_save_pil_image(tmp_path):
    """Saving a plain PIL image writes it to disk unchanged in size and content."""
    image = Image.new("RGB", (50, 50), (10, 20, 30))
    dest = tmp_path / "out" / "plain.jpg"
    visualization.save(image, dest)
    saved = Image.open(dest)
    assert saved.size == (50, 50)
    np.testing.assert_allclose(saved.getpixel((25, 25)), (10, 20, 30), atol=5)  # small JPEG compression tolerance


def test_save_ndarray(tmp_path):
    """Saving a NumPy array converts it to an image first and preserves its content."""
    array = np.zeros((20, 30, 3), dtype=np.uint8)
    array[:, :, 0] = 200
    dest = tmp_path / "out" / "array.jpg"
    visualization.save(array, dest)
    saved = Image.open(dest)
    assert saved.size == (30, 20)
    np.testing.assert_allclose(saved.getpixel((15, 10)), (200, 0, 0), atol=5)


def test_save_resizes_oversized_image(tmp_path, monkeypatch):
    """Images larger than MAX_IMAGE_DIM are downscaled to fit before saving."""
    monkeypatch.setattr(visualization, "MAX_IMAGE_DIM", 10)
    image = Image.new("RGB", (50, 20), (1, 2, 3))
    dest = tmp_path / "big.jpg"
    visualization.save(image, dest)
    saved = Image.open(dest)
    assert saved.size == (10, 10)


def test_concat_horizontal():
    """Horizontal concatenation places images side by side and pads shorter ones with black."""
    img1 = Image.new("RGB", (10, 20), (255, 0, 0))
    img2 = Image.new("RGB", (15, 30), (0, 255, 0))
    result = visualization.concat_horizontal([img1, img2])
    assert result.size == (25, 30)
    assert result.getpixel((5, 10)) == (255, 0, 0)
    assert result.getpixel((15, 10)) == (0, 255, 0)
    assert result.getpixel((5, 25)) == (0, 0, 0)  # img1 is shorter; unfilled area stays black


def test_concat_vertical():
    """Vertical concatenation stacks images top to bottom."""
    img1 = Image.new("RGB", (10, 20), (255, 0, 0))
    img2 = Image.new("RGB", (30, 15), (0, 255, 0))
    result = visualization.concat_vertical([img1, img2])
    assert result.size == (30, 35)
    assert result.getpixel((5, 10)) == (255, 0, 0)
    assert result.getpixel((5, 25)) == (0, 255, 0)


@pytest.mark.parametrize(
    "orientation, expected_size",
    [(ImageOrientation.HORIZONTAL, (25, 10)), (ImageOrientation.VERTICAL, (10, 25))],
)
def test_get_2d_stack(orientation, expected_size):
    """Stacking inserts the requested gap between images, in the requested orientation."""
    images = [Image.new("RGB", (10, 10), (255, 0, 0)), Image.new("RGB", (10, 10), (0, 255, 0))]
    result = visualization.get_2d_stack(images, 5, orientation)
    assert result.size == expected_size


def test_get_2d_stack_bad_orientation():
    """An unrecognized orientation (e.g. AUTO) raises rather than silently picking one."""
    images = [Image.new("RGB", (10, 10)), Image.new("RGB", (10, 10))]
    with pytest.raises(ValueError):
        visualization.get_2d_stack(images, 5, ImageOrientation.AUTO)


def test_get_color_chips():
    """Each requested color produces one solid-colored, correctly-sized chip."""
    colors = [[255, 0, 0], [0, 128, 64]]
    chips = visualization.get_color_chips(colors, 20)
    assert len(chips) == 2
    for chip, color in zip(chips, colors):
        assert chip.size == (20, 20)
        assert chip.getpixel((0, 0)) == tuple(color)


def test_enforce_matching_height():
    """Shorter images are padded (top/bottom, split as evenly as the pixel parity allows) to the tallest height."""
    tall = Image.new("RGB", (10, 16), (255, 0, 0))
    short_even_diff = Image.new("RGB", (10, 10), (0, 255, 0))  # diff=6 (even) -> top=bottom=3
    short_odd_diff = Image.new("RGB", (10, 13), (0, 0, 255))  # diff=3 (odd) -> top=1, bottom=2

    result = visualization.enforce_matching_height([tall, short_even_diff, short_odd_diff])
    assert [img.height for img in result] == [16, 16, 16]
    assert [img.width for img in result] == [10, 10, 10]

    # padding is white; check it lands exactly where the even/odd split arithmetic predicts
    assert result[1].getpixel((0, 2)) == (255, 255, 255)
    assert result[1].getpixel((0, 3)) == (0, 255, 0)
    assert result[1].getpixel((0, 12)) == (0, 255, 0)
    assert result[1].getpixel((0, 13)) == (255, 255, 255)

    assert result[2].getpixel((0, 0)) == (255, 255, 255)
    assert result[2].getpixel((0, 1)) == (0, 0, 255)
    assert result[2].getpixel((0, 13)) == (0, 0, 255)
    assert result[2].getpixel((0, 14)) == (255, 255, 255)


def test_enforce_matching_width():
    """Narrower images are padded (left/right, split as evenly as the pixel parity allows) to the widest width."""
    wide = Image.new("RGB", (16, 10), (255, 0, 0))
    narrow_even_diff = Image.new("RGB", (10, 10), (0, 255, 0))  # diff=6 (even) -> left=right=3
    narrow_odd_diff = Image.new("RGB", (13, 10), (0, 0, 255))  # diff=3 (odd) -> left=2, right=1

    result = visualization.enforce_matching_width([wide, narrow_even_diff, narrow_odd_diff])
    assert [img.width for img in result] == [16, 16, 16]
    assert [img.height for img in result] == [10, 10, 10]

    assert result[1].getpixel((2, 0)) == (255, 255, 255)
    assert result[1].getpixel((3, 0)) == (0, 255, 0)
    assert result[1].getpixel((12, 0)) == (0, 255, 0)
    assert result[1].getpixel((13, 0)) == (255, 255, 255)

    assert result[2].getpixel((1, 0)) == (255, 255, 255)
    assert result[2].getpixel((2, 0)) == (0, 0, 255)
    assert result[2].getpixel((14, 0)) == (0, 0, 255)
    assert result[2].getpixel((15, 0)) == (255, 255, 255)


@pytest.mark.parametrize("n_images", [1, 2, 3, 5])
def test_pad_horizontal(n_images):
    """Each image gets the border widths appropriate to its position (first/middle/last/only)."""
    images = [Image.new("RGB", (10, 10)) for _ in range(n_images)]
    outer, inner = 4, 2
    padded = visualization.pad_horizontal(images, outer, inner)
    assert len(padded) == n_images
    for img in padded:
        assert img.height == 10 + 2 * outer
    if n_images == 1:
        assert padded[0].width == 10 + 2 * outer
    else:
        assert padded[0].width == 10 + outer + inner
        assert padded[-1].width == 10 + outer
        for mid in padded[1:-1]:
            assert mid.width == 10 + inner


def test_pad_horizontal_empty_raises():
    """Padding an empty sequence of images is an unsupported input and raises."""
    with pytest.raises(ValueError):
        visualization.pad_horizontal([], 4, 2)


@pytest.mark.parametrize("n_images", [1, 2, 3, 5])
def test_pad_vertical(n_images):
    """Each image gets the border heights appropriate to its position (first/middle/last/only)."""
    images = [Image.new("RGB", (10, 10)) for _ in range(n_images)]
    outer, inner = 4, 2
    padded = visualization.pad_vertical(images, outer, inner)
    assert len(padded) == n_images
    for img in padded:
        assert img.width == 10 + 2 * outer
    if n_images == 1:
        assert padded[0].height == 10 + 2 * outer
    else:
        assert padded[0].height == 10 + outer + inner
        assert padded[-1].height == 10 + outer
        for mid in padded[1:-1]:
            assert mid.height == 10 + inner


def test_pad_vertical_empty_raises():
    """Padding an empty sequence of images is an unsupported input and raises."""
    with pytest.raises(ValueError):
        visualization.pad_vertical([], 4, 2)


def test_add_borders_single_image():
    """A single image gets a border added on each requested side."""
    img = Image.new("RGB", (10, 10), (1, 2, 3))
    result = visualization.add_borders(img, 1, 2, 3, 4)
    assert isinstance(result, Image.Image)
    assert result.size == (14, 16)


def test_add_borders_list_of_images():
    """A list of images each independently get the same border applied."""
    images = [Image.new("RGB", (10, 10)) for _ in range(3)]
    result = visualization.add_borders(images, 1, 2, 3, 4)
    assert isinstance(result, list)
    assert len(result) == 3
    for img in result:
        assert img.size == (14, 16)


def test_pad_concat_horizontal():
    """Padding and horizontal concatenation compose to the size hand-derived from both border rules."""
    images = [Image.new("RGB", (10, 10)), Image.new("RGB", (10, 20))]
    outer, inner = 3, 2
    result = visualization.pad_concat_horizontal(images, outer, inner)
    assert result.size == (28, 26)


def test_pad_concat_vertical():
    """Padding and vertical concatenation compose to the size hand-derived from both border rules."""
    images = [Image.new("RGB", (10, 10)), Image.new("RGB", (20, 10))]
    outer, inner = 3, 2
    result = visualization.pad_concat_vertical(images, outer, inner)
    assert result.size == (26, 28)


def test_save_dominant_color_visualization_kmeans_remapped(tmp_path):
    """Requesting the remapped image adds it to the output, making it strictly larger than without."""
    analyzed_image = AnalyzedImage(
        f"{TEST_IMAGE_DIR}/red-blue.jpg", None, EDGE_CROP, DominantColorAlgorithm.KMEANS, 2, None
    )
    without_remap = tmp_path / "no_remap.jpg"
    with_remap = tmp_path / "with_remap.jpg"
    visualization.save_dominant_color_visualization(
        analyzed_image, 40, without_remap, include_remapped_image=False, display=False
    )
    visualization.save_dominant_color_visualization(
        analyzed_image, 40, with_remap, include_remapped_image=True, display=False
    )
    # red-blue.jpg is horizontal, so components stack vertically; the extra remapped image adds height
    assert analyzed_image.get_orientation() == ImageOrientation.HORIZONTAL
    assert Image.open(with_remap).height > Image.open(without_remap).height


def test_save_dominant_color_visualization_hue_dist_remapped_warns(tmp_path, caplog):
    """Requesting a remapped image with hue_dist (unsupported) warns but still saves the rest of the graphic."""
    analyzed_image = load_analyzed_image("red")
    dest = tmp_path / "dc.jpg"
    with caplog.at_level(logging.WARNING):
        visualization.save_dominant_color_visualization(
            analyzed_image, 40, dest, include_remapped_image=True, display=False
        )
    assert "Unable to include remapped image" in caplog.text
    assert dest.exists()


def test_get_histogram_as_bar_single_color():
    """With include_all_colors off, the bar is filled entirely with the image's single dominant color."""
    analyzed_image = load_analyzed_image("red", n_colors=1)
    bar = visualization.get_histogram_as_bar(analyzed_image, include_all_colors=False, height=100, width=10)
    assert bar.size == (10, 100)
    expected_color = tuple(int(c) for c in analyzed_image.get_dominant_color())
    assert bar.getpixel((5, 50)) == expected_color


def test_get_histogram_as_bar_all_colors():
    """With include_all_colors on, colors stack bottom-up by dominance with heights matching their proportions."""
    analyzed_image = AnalyzedImage(
        f"{TEST_IMAGE_DIR}/red-blue.jpg", None, EDGE_CROP, DominantColorAlgorithm.KMEANS, 2, None
    )
    height = 200
    expected_histogram = list(analyzed_image.cluster_histogram)  # most dominant first
    most_dominant_rgb, most_dominant_proportion = expected_histogram[0]
    least_dominant_rgb, _ = expected_histogram[-1]

    bar = visualization.get_histogram_as_bar(analyzed_image, include_all_colors=True, height=height, width=10)
    assert bar.size == (10, height)
    assert bar.getpixel((5, height - 1)) == tuple(int(c) for c in most_dominant_rgb)
    assert bar.getpixel((5, 0)) == tuple(int(c) for c in least_dominant_rgb)

    # cluster_histogram should be untouched by building the bar
    assert analyzed_image.cluster_histogram == expected_histogram

    # scan up from the bottom to measure the most-dominant color's actual band height
    expected_band_height = round_to_int(most_dominant_proportion * height)
    actual_band_height = 0
    for y in range(height - 1, -1, -1):
        if bar.getpixel((5, y)) == tuple(int(c) for c in most_dominant_rgb):
            actual_band_height += 1
        else:
            break
    assert actual_band_height == expected_band_height


def test_save_spectrum_visualization(tmp_path):
    """The spectrum graphic's dimensions match the requested height and the per-image bar width formula."""
    images = [load_analyzed_image(c) for c in ["red", "green", "blue"]]
    dest = tmp_path / "spectrum.jpg"
    visualization.save_spectrum_visualization(images, False, 90, dest, display=False)
    assert dest.exists()
    saved = Image.open(dest)
    assert saved.height == 90
    assert saved.width == 3 * round_to_int((90 * config.DEFAULT_SPECTRUM_RATIO) / 3)


def test_save_image_collage_row_chunking_by_width(tmp_path):
    """A narrower requested width wraps images into more, shorter rows, changing the overall aspect ratio."""
    images = [load_analyzed_image(c) for c in ["red", "green", "blue", "white"]]
    dest_wide = tmp_path / "wide.jpg"
    dest_narrow = tmp_path / "narrow.jpg"
    visualization.save_image_collage(images, 4, dest_wide, display=False)  # 1 row of 4
    visualization.save_image_collage(images, 2, dest_narrow, display=False)  # 2 rows of 2

    wide = Image.open(dest_wide)
    narrow = Image.open(dest_narrow)
    assert wide.height < narrow.height
    assert wide.width > narrow.width


@pytest.mark.parametrize(
    "color_names, expected_width",
    [
        (["red", "green", "blue", "white"], 2),  # perfect square: sqrt(4) == 2
        (["red", "green", "blue", "white", "black"], 3),  # non-square: sqrt(5) ~= 2.24, rounds up to 3
    ],
)
def test_save_image_collage_sqrt_width_matches_explicit_width(tmp_path, color_names, expected_width):
    """ "sqrt" width mode selects the same column count as the equivalent explicit width."""
    images = [load_analyzed_image(c) for c in color_names]
    sqrt_dest = tmp_path / "sqrt.jpg"
    explicit_dest = tmp_path / "explicit.jpg"
    visualization.save_image_collage(images, "sqrt", sqrt_dest, display=False)
    visualization.save_image_collage(images, expected_width, explicit_dest, display=False)
    assert Image.open(sqrt_dest).size == Image.open(explicit_dest).size
