import os
from pathlib import Path
from typing import List, Union

import numpy as np
from PIL import ImageOps
from PIL.Image import Image

import colorsort.config as config
from colorsort.analyzed_image import AnalyzedImage
from colorsort.util import ImageOrientation

# TODO: write tests for these functions
# TODO: remove dependency on config file; all parameters should be passed in


def save(image: Union[AnalyzedImage, Image, np.array], dest_path: Union[Path, str]):
    """Save the provided image to disk.

    If the image is an image representation, create a hard link between the image's original file and
    the provided path to save on disk space.

    Args:
        image (Union[AnalyzedImage, Image, np.array]): The image to save to disk.
        dest_path (Union[Path, str]): The output path to which to save the image.
    """
    if not isinstance(dest_path, Path):
        dest_path = Path(dest_path)

    dest_parent = dest_path.parents[0]
    _ = dest_parent.mkdir(parents=True, exist_ok=True)

    if isinstance(image, AnalyzedImage):
        os.link(image.image_path, dest_path)
    elif isinstance(image, Image):
        image.save(dest_path)
    else:
        image = Image.fromarray(image)
        image.save(dest_path)


def save_dominant_color_visualization(
    analyzed_image: AnalyzedImage,
    dest_path: str,
    visualization_orientation: ImageOrientation,
    include_remapped_image: bool,
    display: bool,
):
    """Save a visualization of the provided analyzed image's dominant colors.

    Saves the dominant colors as chips alongside a representation of the original image, optionally with
    a remapped version of that image (if KMEANS algorithm was used to determine dominant colors).

    Args:
        analyzed_image (AnalyzedImage): The analyzed image for which to generate the dominant color visualization.
        dest_path (str): The output folder to which to save image files.
        visualization_orientation (ImageOrientation): The orientation of the saved output graphic.
        include_remapped_image (bool): Include the remapped (color-reduced) image alongside the original graphic
            and dominant color chips.
        display (bool): Whether to display the generated graphic.

    Raises:
        ValueError: If an unrecognized orientation value is provided.
    """
    image_orientation = analyzed_image.get_orientation()
    if visualization_orientation == ImageOrientation.AUTO:
        visualization_orientation = image_orientation.rotate()

    stacked_chips = get_2d_stack(
        get_color_chips(analyzed_image.get_dominant_colors()),
        config.DEFAULT_CHIP_GAP,
        image_orientation,
    )

    visualization_components = [analyzed_image.pil_image, stacked_chips]
    if include_remapped_image:
        visualization_components.append(analyzed_image.get_remapped_image())
    outer_border = int(config.DEFAULT_CHIP_BORDER / 2)
    inner_border = int(config.DEFAULT_CHIP_BORDER / 4)
    if visualization_orientation == ImageOrientation.HORIZONTAL:
        visualization = pad_concat_horizontal(visualization_components, outer_border, inner_border)
    elif visualization_orientation == ImageOrientation.VERTICAL:
        visualization = pad_concat_vertical(visualization_components, outer_border, inner_border)
    else:
        raise ValueError(f"Unrecognized orientation: {image_orientation}")

    if display:
        visualization.show()
    save(visualization, dest_path)


def get_2d_stack(images: List[Image], gap: int, orientation: ImageOrientation) -> Image:
    """Stack a sequence of images into a single image.

    Args:
        images (List[Image]): A list of images to stack.
        gap (int): The gap between images in the generated stack of images.
        orientation (ImageOrientation): The orientation of the generated stack of images.

    Raises:
        ValueError: If an unrecognized orientation value is provided.

    Returns:
        Image: An image containing a two-dimensional stack of the provided sequence of images.
    """
    with_borders = [images[0]]
    if orientation == ImageOrientation.HORIZONTAL:
        top = bottom = right = 0
        left = gap
        concat = concat_horizontal
    elif orientation == ImageOrientation.VERTICAL:
        bottom = left = right = 0
        top = gap
        concat = concat_vertical
    else:
        raise ValueError(f"Unrecognized orientation: {orientation}")

    with_borders.extend(add_borders(images[1:], left, top, right, bottom))
    return concat(with_borders)


def concat_horizontal(images: List[Image]) -> Image:
    """Concatenate a sequence of images horizontally into a single image.

    Args:
        images (List[Image]): The sequence of images to concatenate.

    Returns:
        Image: The image resulting from the horizontal concatenation of the provided images.
    """
    width = sum([img.width for img in images])
    height = images[0].height
    dest_image = Image.new("RGB", (width, height))
    h_pos = 0
    for img in images:
        dest_image.paste(img, (h_pos, 0))
        h_pos += img.width
    return dest_image


def concat_vertical(images: List[Image]) -> Image:
    """Concatenate a sequence of images vertically into a single image.

    Args:
        images (List[Image]): The sequence of images to concatenate.

    Returns:
        Image: The image resulting from the vertical concatenation of the provided images.
    """
    width = images[0].width
    height = sum([img.height for img in images])
    dest_image = Image.new("RGB", (width, height))
    v_pos = 0
    for img in images:
        dest_image.paste(img, (0, v_pos))
        v_pos += img.height
    return dest_image


def get_color_chips(colors: List[List], size=config.DEFAULT_CHIP_SIZE) -> List[Image]:
    """Get a set of chips (small, single-color images) representing each dominant color.

    Args:
        colors (List[List]): The RGB colors to get chips for.
        size (_type_, optional): The size of the generated chips. Defaults to config.DEFAULT_CHIP_SIZE.

    Returns:
        List[Image]: A list of chips corresponding to the provided colors.
    """
    chips = []
    for color in colors:
        chips.append(Image.new("RGB", (size, size), color=tuple(color)))

    return chips


def pad_concat_horizontal(visualization_components: List[Image], outer_border: int, inner_border: int) -> Image:
    """Pad and concatenate asequence of images horizontally into a single image.

    Applies padding to ensure that
    - all images have the same height before concatenating
    - `outer_border` and `inner_border` are applied correctly

    Args:
        visualization_components (List[Image]): Images to pad and concatenate horizontally.
        outer_border (int): The width of the outer border of the final concatenated image (px).
        inner_border (int): The width of the inner border between concatenated components (px).

    Returns:
        Image: The image resulting from the padding and horizontal concatenation of the provided images.
    """
    visualization_components = enforce_matching_height(visualization_components)
    visualization_components = pad_horizontal(visualization_components, outer_border, inner_border)
    return concat_horizontal(visualization_components)


def enforce_matching_height(images: List[Image]) -> List[Image]:
    """Returns the provided sequence of images with padding to ensure equal height.

    Args:
        images (List[Image]): A sequence of images.

    Returns:
        List[Image]: A sequence of images with the same height.
    """
    max_height = max([img.height for img in images])
    padded = []

    for img in images:
        height_diff = max_height - img.height
        top = bottom = int(height_diff / 2)
        if not height_diff % 2 == 0:
            bottom += 1
        padded.append(add_borders(img, 0, top, 0, bottom)[0])

    return padded


def pad_horizontal(images: List[Image], outer_border: int, inner_border: int) -> List[Image]:
    """Applies padding to images before horizontal concatenation.

    Ensures the provided sequence of images will have the provided `outer_border` and `inner_border` once
    horizontally concatenated.

    Args:
        images (List[Image]): The sequence of images to apply padding to.
        outer_border (int): The desired width of the outer border of the final concatenated image (px).
        inner_border (int): The desired width of the inner border between concatenated components (px).

    Raises:
        ValueError: If `images` is empty.

    Returns:
        List[Image]: A sequence of properly padded images.
    """
    padded = []
    if len(images) == 1:
        padded.append(
            add_borders(images[0], left=outer_border, top=outer_border, right=outer_border, bottom=outer_border)
        )
    elif len(images) == 2:
        padded.append(add_borders(images[0], outer_border, outer_border, inner_border, outer_border))
        padded.append(add_borders(images[1], 0, outer_border, outer_border, outer_border))
    elif len(images) > 2:
        padded.append(add_borders(images[0], outer_border, outer_border, inner_border, outer_border))
        for img in images[1:-1]:
            padded.append(add_borders(img, 0, outer_border, inner_border, outer_border))
        padded.append(add_borders(images[-1], 0, outer_border, outer_border, outer_border))
    else:
        raise ValueError(f"Unexpected number of images to pad: {len(images)}")

    return padded


def pad_concat_vertical(visualization_components: List[Image], outer_border: int, inner_border: int) -> Image:
    """Pad and concatenate asequence of images vertically into a single image.

    Applies padding to ensure that
    - all images have the same width before concatenating
    - `outer_border` and `inner_border` are applied correctly

    Args:
        visualization_components (List[Image]): Images to pad and concatenate vertically.
        outer_border (int): The width of the outer border of the final concatenated image (px).
        inner_border (int): The width of the inner border between concatenated components (px).


    Returns:
        Image: The image resulting from the padding and horizontal concatenation of the provided images.
    """
    visualization_components = enforce_matching_width(visualization_components)
    visualization_components = pad_vertical(visualization_components, outer_border, inner_border)
    return concat_vertical(visualization_components)


def enforce_matching_width(images: List[Image]) -> List[Image]:
    """Returns the provided sequence of images with padding to ensure equal width.

    Args:
        images (List[Image]): A sequence of images.

    Returns:
        List[Image]: A sequence of images with the same width.
    """
    max_width = max([img.width for img in images])
    padded = []

    for img in images:
        width_diff = max_width - img.width
        left = right = int(width_diff / 2)
        if not width_diff % 2 == 0:
            left += 1
        img_with_border = add_borders(img, left, 0, right, 0)[0]
        padded.append(img_with_border)

    return padded


def pad_vertical(images: List[Image], outer_border: int, inner_border: int) -> List[Image]:
    """Applies padding to images before vertical concatenation.

    Ensures the provided sequence of images will have the provided `outer_border` and `inner_border` once
    vertically concatenated.

    Args:
        images (List[Image]): The sequence of images to apply padding to.
        outer_border (int): The desired width of the outer border of the final concatenated image (px).
        inner_border (int): The desired width of the inner border between concatenated components (px).

    Raises:
        ValueError: If `images` is empty.

    Returns:
        List[Image]: A sequence of properly padded images.
    """
    padded = []
    if len(images) == 1:
        padded.append(
            add_borders(images[0], left=outer_border, top=outer_border, right=outer_border, bottom=outer_border)
        )
    elif len(images) == 2:
        padded.append(add_borders(images[0], outer_border, outer_border, outer_border, inner_border))
        padded.append(add_borders(images[1], outer_border, 0, outer_border, outer_border))
    elif len(images) > 2:
        padded.append(add_borders(images[0], outer_border, outer_border, outer_border, inner_border))
        for img in images[1:-1]:
            padded.append(add_borders(img, outer_border, 0, outer_border, inner_border))
        padded.append(add_borders(images[-1], outer_border, 0, outer_border, outer_border))
    else:
        raise ValueError(f"Unexpected number of images to pad: {len(images)}")

    return padded


def add_borders(
    images: Union[Image, List[Image]], left: int, top: int, right: int, bottom: int
) -> Union[Image, List[Image]]:
    """Apply borders to an image or sequence of images.

    Args:
        images (Union[Image, List[Image]]): The image or sequence of images to apply borders to.
        left (int): The desired left border width.
        top (int): The desired top border width.
        right (int): The desired right border width.
        bottom (int): The desired bottom border width.

    Returns:
        Union[Image, List[Image]]: The image or images with borders applied.
    """
    if not isinstance(images, List):
        just_one = True
        images = [images]
    else:
        just_one = False

    with_borders = []
    for im in images:
        img_with_border = ImageOps.expand(im, border=(left, top, right, bottom), fill="white")
        with_borders.append(img_with_border)

    if just_one:
        with_borders = with_borders[0]
    return with_borders


def save_spectrum_visualization(analyzed_images: List[AnalyzedImage], dest_path: str, display: bool):
    """Generate a "spectrum" visualization of the dominant colors in each of a sequence of images.

    Final output is a sequence of concatenated bars corresponding to dominant colors.

    Args:
        analyzed_images (List[AnalyzedImage]): The sequence of analyzed images for which to generate
            the spectrum visualization.
        dest_path (str): The output folder to which to write the generated graphic.
        display (bool): Whether to display the generated graphic.
    """
    vertical_bars = [get_histogram_as_bar(img) for img in analyzed_images]
    spectrum = concat_horizontal(vertical_bars)

    if display:
        spectrum.show()
    save(spectrum, dest_path)


def get_histogram_as_bar(
    analyzed_image: AnalyzedImage,
    dominant_color_only: bool = True,
    height: int = config.DEFAULT_BAR_HEIGHT,
    width: int = config.DEFAULT_BAR_WIDTH,
) -> Image:
    """Get a representation of an image's dominant color histogram as a stacked vertical bar.

    TODO: remove default values; set from CLI

    Args:
        analyzed_image (Image): The analyzed image from which to generate the histogram.
        dominant_color_only (bool, optional): Whether to include just the single most dominant color.
            Defaults to True.
        height (int, optional): The height of the generated bar. Defaults to conf.DEFAULT_BAR_HEIGHT.
        width (int, optional): The width of the generated bar. Defaults to conf.DEFAULT_BAR_WIDTH.

    Returns:
        Image: An image representing the provided image's dominant color histogram.
    """
    if dominant_color_only:
        color_hist = [(analyzed_image.get_dominant_color(), 1)]
        print(f"{analyzed_image.image_path.stem} - {analyzed_image.get_dominant_color(hsv=True)}")
    else:
        color_hist = analyzed_image.cluster_histogram

    bar_components = []
    for color_rgb, proportion in color_hist:  # build top-down
        converted = tuple([int(color) for color in color_rgb])
        bar_components.append(Image.new("RGB", (width, proportion * height), color=converted))

    return concat_vertical(bar_components)
