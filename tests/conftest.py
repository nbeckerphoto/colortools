import numpy as np
from colortools.heuristics import DEFAULT_N_COLORS_MAX, PIL_NUM_HUES

ARRAY_TOLERANCE = 1


def get_hsv_array(n_hues, distribute=False, extra_hues=[]):
    if distribute:
        hue_increment = int(PIL_NUM_HUES / DEFAULT_N_COLORS_MAX)
        hues = [min(hue_increment * n, PIL_NUM_HUES - 1) for n in range(n_hues)]
    else:
        hues = [h for h in range(n_hues)]

    rows = [[h, 255, 255] for h in hues]
    extra_hues = [[h, 255, 255] for h in extra_hues]
    rows.extend(extra_hues)
    return np.array([rows])
