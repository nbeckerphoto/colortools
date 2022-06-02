import cv2
import numpy as np


def rgb_to_hsv(rgb):
    color_rep = np.zeros((1, 1, 3), np.uint8)
    color_rep[:] = rgb
    color_rep_hsv = cv2.cvtColor(color_rep, cv2.COLOR_RGB2HSV)
    hue, sat, val = color_rep_hsv[0][0]
    return np.array([hue, sat, val])


def hsv_to_rgb(hsv):
    color_rep = np.zeros((1, 1, 3), np.uint8)
    color_rep[:] = hsv
    color_rep_rgb = cv2.cvtColor(color_rep, cv2.COLOR_HSV2RGB)
    r, g, b = color_rep_rgb[0][0]
    return np.array([r, g, b])


def enhance_color(image_rgb, saturation=0.1, value=0.1):
    color_hsv = rgb_to_hsv(image_rgb)
    color_hsv[1] = color_hsv[1] * (1 + saturation)
    color_hsv[2] = color_hsv[2] * (1 + value)
    color_rgb = hsv_to_rgb(color_hsv)
    return color_rgb
