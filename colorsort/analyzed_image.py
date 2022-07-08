#  Use k-means clustering to find the most-common colors in an image
#  Ideas shamelessly borrowed from:
# - https://www.timpoulsen.com/2018/finding-the-dominant-colors-of-an-image.html
# - https://code.likeagirl.io/finding-dominant-colour-on-an-image-b4e075f98097

import logging
from collections import deque
from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image

import colorsort.util as util
from colorsort.analysis import build_histogram_from_clusters, fit_and_predict
from colorsort.heuristics import NHeuristic, compute_hue_dist, get_n_heuristic


class AnalyzedImage:
    """
    Internal representation of an image. Includes basic image metadata as well as analysis results.
    """

    def __init__(
        self,
        image_path: Union[Path, str],
        resize_long_axis: int,
        dominant_color_algorithm: util.DominantColorAlgorithm,
        n_colors: int,
        auto_n_heuristic: NHeuristic,
    ):
        self.image_path = image_path
        self.dominant_color_algorithm = dominant_color_algorithm

        # set image, dimensions, and orientation
        pil_image = Image.open(image_path)
        width, height = pil_image.size
        if height > width:
            self.orientation = util.ImageOrientation.VERTICAL
            resized_height = resize_long_axis
            resized_width = int((width / height) * resized_height)
        else:
            self.orientation = util.ImageOrientation.HORIZONTAL
            resized_width = resize_long_axis
            resized_height = int((height / width) * resized_width)

        self.pil_image = pil_image.resize((resized_width, resized_height))
        self.width, self.height = self.pil_image.size

        # set n using selected heuristic
        if n_colors is None or n_colors == 0:
            n_heuristic = get_n_heuristic(auto_n_heuristic)
            self.n_colors = n_heuristic(self.get_as_array(hsv=True))
        else:
            self.n_colors = n_colors

        if self.dominant_color_algorithm == util.DominantColorAlgorithm.HUE_DIST:
            self.dominant_colors_rgb, self.dominant_colors_hsv = self.get_dominant_colors_hue_dist(self.n_colors)
        elif self.dominant_color_algorithm == util.DominantColorAlgorithm.KMEANS:
            self.dominant_colors_rgb, self.dominant_colors_hsv = self.get_dominant_colors_kmeans(self.n_colors)

    def get_dominant_colors_hue_dist(self, n_colors):
        hue_dist = compute_hue_dist(self.get_as_array(hsv=True))
        hue_dist = [
            (hue, hsv_list) for hue, hsv_list in sorted(hue_dist.items(), key=lambda item: len(item[1]), reverse=True)
        ]

        dominant_colors_hsv = []
        for i in range(n_colors):
            current_hue_list = hue_dist[i]
            hue = current_hue_list[0]
            if len(current_hue_list[1]) > 0:
                avg_sat = int(np.median([hsv[1] for hsv in current_hue_list[1]]))
                avg_val = int(np.median([hsv[2] for hsv in current_hue_list[1]]))
            else:
                # TODO log warning
                avg_sat, avg_val = 0, 0
            dominant_colors_hsv.append([hue, avg_sat, avg_val])

        dominant_colors_hsv = util.normalize_hsv(dominant_colors_hsv)
        dominant_colors_rgb = util.hsv_to_rgb(dominant_colors_hsv)
        return dominant_colors_rgb, dominant_colors_hsv

    def get_dominant_colors_kmeans(self, n_colors):
        self.model, self.predicted = fit_and_predict(self.get_as_array(), n_colors)
        self.cluster_histogram = build_histogram_from_clusters(self.model)
        dominant_colors_rgb = [np.uint8(rgb).tolist() for rgb, _ in self.cluster_histogram]
        dominant_colors_hsv = util.rgb_to_hsv(dominant_colors_rgb)

        return dominant_colors_rgb, dominant_colors_hsv

    def get_as_array(self, hsv=False):
        if hsv:
            return np.asarray(self.pil_image.convert("HSV"))
        else:
            return np.asarray(self.pil_image)

    def get_dominant_colors(self, hsv=False):
        if hsv:
            return self.dominant_colors_hsv
        else:
            return self.dominant_colors_rgb

    def get_dominant_color(self, hsv=False):
        return self.get_dominant_colors(hsv)[0]

    def get_sort_metric(self):
        dom_hue = self.get_dominant_color(hsv=True)[0]
        dom_hue = (dom_hue + 90) % 360
        return dom_hue

    def get_orientation(self):
        return self.orientation

    def is_bw(self):
        return self.get_dominant_color(hsv=True)[1] == 0

    def get_remapped_image(self, other: "AnalyzedImage" = None):
        target_colors = self.model.cluster_centers_
        if other is None:
            other_predicted = self.predicted
        else:  # experimental - TODO test this
            other_rgb_data = other.get_as_array().reshape((other.height * other.width, 3))
            other_predicted = self.model.predict(other_rgb_data)

        remapped_image = np.array([target_colors[i] for i in other_predicted])
        return Image.fromarray(np.uint8(remapped_image.reshape((self.height, self.width, 3))))

    def generate_filename(self, index, base):
        if index is not None:
            filename = f"{str(index)}_"
        else:
            filename = ""

        dom_color_hsv = self.get_dominant_color(hsv=True)
        dom_hue, dom_sat, dom_val = dom_color_hsv[0], dom_color_hsv[1], dom_color_hsv[2]
        filename += f"{base}_hue={dom_hue}_sat={dom_sat}_val={dom_val}_n={self.n_colors}.jpg"
        return filename

    def get_pretty_string(self):
        out = f"{self.image_path.name}: n={self.n_colors}, algorithm={self.dominant_color_algorithm.value} \n"
        out += f"    rgb={self.dominant_colors_rgb}\n"
        out += f"    hsv={self.dominant_colors_hsv}"
        return out

    @staticmethod
    def colorsort(image_reps, anchor_image):
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
