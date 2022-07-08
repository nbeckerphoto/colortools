import numpy as np

from colorsort.heuristics import MAX_N, PIL_NUM_HUES


def get_image_path(dimensions, color_name):
    return f"tests/test_images/{dimensions[0]}-by-{dimensions[1]}-{color_name}.jpg"


def get_hsv_array(n_hues, distribute=False, extra_hues=[]):
    if distribute:
        hue_increment = int(PIL_NUM_HUES / MAX_N)
        hues = [min(hue_increment * n, PIL_NUM_HUES - 1) for n in range(n_hues)]
    else:
        hues = [h for h in range(n_hues)]

    rows = [[h, 255, 255] for h in hues]
    extra_hues = [[h, 255, 255] for h in extra_hues]
    rows.extend(extra_hues)
    return np.array([rows])
