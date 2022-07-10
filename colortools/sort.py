from collections import deque
from typing import List, Tuple

from colortools.analyzed_image import AnalyzedImage


def colorsort(
    image_reps: List[AnalyzedImage], anchor_image: str
) -> Tuple[List[AnalyzedImage], List[AnalyzedImage], List[AnalyzedImage]]:
    """Static method for sorting a collection of analyzed images by their hue.

    Uses the AnalyzedImage.get_sort_metric() function for sorting color images.

    TODO: add more sorting options here

    Returns:
        Tuple[List["AnalyzedImage"], List["AnalyzedImage"], List["AnalyzedImage"]]: Three lists:
            - The first list is all analyzed images. Color images are first, sorted by hue, followed by black
                and white images, sorted by value.
            - The second list is just the color images, sorted by hue.
            - The third list is just the black and white images, sorted by value.
    """
    color = []
    bw = []
    for img in image_reps:
        if img.is_bw():
            bw.append(img)
        else:
            color.append(img)

    # sort by hue, then value
    color.sort(
        key=lambda elem: (
            elem.get_sort_metric(),
            elem.get_dominant_color(hsv=True)[2],
        )
    )

    # sort by value
    bw.sort(key=lambda elem: elem.get_dominant_color(hsv=True)[2])

    starting_index = 0
    if anchor_image:
        try:
            while not color[starting_index].image_path.name == anchor_image:
                starting_index += 1
        except IndexError:
            print(f"Starting image {anchor_image} not found!")
            starting_index = 0

    color = deque(color)
    for _ in range(starting_index):
        color.append(color.popleft())

    combined = []
    combined.extend(color)
    combined.extend(bw)
    return combined, color, bw
