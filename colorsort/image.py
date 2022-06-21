#  Use k-means clustering to find the most-common colors in an image
#  Ideas shamelessly borrowed from:
# - https://www.timpoulsen.com/2018/finding-the-dominant-colors-of-an-image.html
# - https://code.likeagirl.io/finding-dominant-colour-on-an-image-b4e075f98097

from collections import deque
from pathlib import Path

import cv2
import numpy as np

import config as conf
import heuristics as heuristics
import util
from analysis import build_histogram_from_clusters, fit_and_predict
from util import ImageOrientation


class Image:
    """
    Internal representation of an image. Includes basic image metadata as well as analysis results.
    """

    def __init__(self, image_path, resize_long_axis, n_clusters, auto_n_heuristic, no_enhance):
        # load image
        if isinstance(image_path, str):
            image_path = Path(image_path)
        self.image_path = image_path
        image_rgb_full_size = cv2.imread(str(image_path))

        # resize
        if resize_long_axis > 0:
            height, width, _ = np.shape(image_rgb_full_size)
            if height > width:
                self.orientation = util.ImageOrientation.VERTICAL
                resize_h = resize_long_axis
                resize_w = int((width / height) * resize_h)
            else:
                resize_w = resize_long_axis
                resize_h = int((height / width) * resize_w)

            self.image_rgb = cv2.resize(image_rgb_full_size, (resize_w, resize_h))
        else:
            self.image_rgb = image_rgb_full_size

        # set dimensions
        height, width, _ = np.shape(self.image_rgb)
        self.image_height = height
        self.image_width = width

        # set n using selected heuristic
        if n_clusters is None:
            heuristic = heuristics.get_heuristic(auto_n_heuristic)
            self.n = heuristic(self.image_rgb)
        else:
            self.n = n_clusters

        self.enhance = not no_enhance

        # train model, generate prdictions, and build histogram
        self.model, self.predicted = fit_and_predict(self.image_rgb, self.n)
        self.cluster_histogram = build_histogram_from_clusters(self.model)

    def get_image_rgb(self) -> np.array:
        return self.image_rgb

    def get_dominant_colors(self, hsv=False):
        dominant_colors_rgb = [util.enhance_color(color_rgb) for color_rgb, _ in self.cluster_histogram]
        if self.enhance:
            dominant_colors_rgb = [util.enhance_color(color_rgb) for color_rgb in dominant_colors_rgb]
        if not hsv:
            return dominant_colors_rgb
        else:
            return [util.rgb_to_hsv(rgb_rep) for rgb_rep in dominant_colors_rgb]

    def get_dominant_color(self, hsv=False):
        dominant_colors = self.get_dominant_colors(hsv)
        return dominant_colors[0]

    def is_bw(self):
        dominant_color_hsv = self.get_dominant_color(hsv=True)
        return dominant_color_hsv[1] == 0

    def get_color_chips(self, size=conf.DEFAULT_CHIP_SIZE):
        chips = []
        for color in self.get_dominant_colors():
            chip = np.zeros((size, size, 3), np.uint8)
            chip[:] = (color[0], color[1], color[2])
            chips.append(chip)

        return chips

    def get_remapped_image(self, other: "Image" = None):
        target_colors = (
            [util.enhance(cluster_center) for cluster_center in self.model.cluster_centers_]
            if self.enhance
            else self.model.cluster_centers_
        )
        if other is None:
            # remapped_image = np.array([(self.labels_to_rgb[i]) for i in self.fitted_model.labels_])
            remapped_image = np.array([target_colors[i] for i in self.predicted])
            return np.uint8(remapped_image.reshape((self.img_height, self.img_width, 3)))
        else:
            # TODO test this
            other_rgb_data = other.image_rgb.reshape((other.img_height * other.img_width, 3))
            other_predicted = self.model.predict(other_rgb_data)
            # remapped_image = np.array([self.fitted_model.cluster_centers_[i] for i in other_predicted])
            remapped_image = np.array([target_colors[i] for i in other_predicted])
            return np.uint8(remapped_image.reshape((self.img_height, self.img_width, 3)))

    def generate_filename(self, index, base):
        if index is not None:
            filename = str(index)
        else:
            filename = ""

        filename += f"_{base}_n={self.n}_enhance={self.enhance}.jpg"
        return filename

    def get_orientation(self):
        if self.image_height > self.image_width:
            return ImageOrientation.VERTICAL
        else:
            return ImageOrientation.HORIZONTAL

    @staticmethod
    def colorsort(image_reps, anchor_image):
        color = []
        bw = []
        for img in image_reps:
            if img.is_bw:
                bw.append(img)
            else:
                color.append(img)

        # sort by hue
        color.sort(
            key=lambda elem: (
                elem.get_dominant_color(hsv=True)[0],
                elem.get_dominant_color(hsv=True)[1],
                elem.get_dominant_color(hsv=True)[2],
            ),
            reverse=True,
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
