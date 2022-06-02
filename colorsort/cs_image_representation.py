#  Use k-means clustering to find the most-common colors in an image
#  Ideas shamelessly borrowed from:
# - https://www.timpoulsen.com/2018/finding-the-dominant-colors-of-an-image.html
# - https://code.likeagirl.io/finding-dominant-colour-on-an-image-b4e075f98097

from collections import deque
from pathlib import Path

import cv2
import numpy as np
from sklearn.cluster import KMeans

import config as conf
import heuristics as heuristics
import image_utils as image_utils


class HistogramColor:
    def __init__(self, rgb_rep, proportion):
        self.rgb_rep = rgb_rep
        self.hsv_rep = image_utils.rgb_to_hsv(rgb_rep)
        self.proportion = proportion

    def __str__(self):
        # return f"rgb={self.rgb_rep}, hsv={self.hsv_rep}, proportion={self.proportion:0.3f}"
        return f"hsv={self.hsv_rep}, proportion={self.proportion:0.3f}"


class CsImageRepresentation:
    def __init__(self, image_path, resize_long_axis, n_clusters, resolve, enhance):
        if isinstance(image_path, str):
            image_path = Path(image_path)

        self.image_path = image_path
        img_rgb_full_size = cv2.imread(str(image_path))
        if resize_long_axis > 0:
            height, width, _ = np.shape(img_rgb_full_size)
            if height >= width:
                resize_h = resize_long_axis
                resize_w = int((width / height) * resize_h)
            else:
                resize_w = resize_long_axis
                resize_h = int((height / width) * resize_w)

            self.image_rgb = cv2.resize(img_rgb_full_size, (resize_w, resize_h))
        else:
            self.image_rgb = img_rgb_full_size

        height, width, _ = np.shape(self.image_rgb)
        self.img_height = height
        self.img_width = width

        self.resolve = resolve
        self.enhance = enhance

        if n_clusters is None:
            # self.n = heuristics.auto_k_simple_threshold(self.image_rgb)
            # self.n = heuristics.auto_k_hue(self.image_rgb)
            # self.n = heuristics.auto_k_hue_binned(self.image_rgb)
            self.n = heuristics.auto_k_binned_with_threshold(self.image_rgb)
        else:
            self.n = n_clusters

        self.set_model_and_histogram(self.n)

    def print_state(self):
        print(self.image_path)
        print(self.get_dominant_colors(hsv=True))

    def set_model_and_histogram(self, n_clusters):
        self.fitted_model = self._train_model(n_clusters)
        self.cluster_histogram = self._build_histogram()

        dominant_colors_hsv = self.get_dominant_color(hsv=True)
        self.is_bw = dominant_colors_hsv[1] == 0

    def _train_model(self, n_clusters):
        image_rgb_data = self.image_rgb.reshape((self.img_height * self.img_width, 3))
        clusters = KMeans(n_clusters=n_clusters, random_state=0)
        clusters.fit(image_rgb_data)
        return clusters

    def _build_histogram(self):
        """_summary_

        Args:
            fitted_model (_type_): fitted cluster model from which to use cluster centers
            sort (_type_):

        Returns:
            List[ClusterColor]: _description_
        """
        bins = np.arange(0, len(self.fitted_model.cluster_centers_) + 1)  # bins by label ([0, 1, 2, 3, ...])
        hist, _ = np.histogram(self.fitted_model.labels_, bins=bins)  # array of counts by label
        hist = hist.astype("float32")
        hist /= hist.sum()  # array of proportions
        color_and_proportion = list(zip(self.fitted_model.cluster_centers_, hist))  # cluster centers are RGB colors

        # resolve and enhance
        if self.resolve:
            resolved = []
            image_rgb_data = heuristics.get_sample(self.image_rgb)
            for color, _ in color_and_proportion:
                min_color = image_rgb_data[0][:]
                min_dist = np.linalg.norm(color[:] - min_color)
                for pixel in image_rgb_data:
                    current_dist = np.linalg.norm(color[:] - pixel[:])
                    if current_dist < min_dist:
                        min_color = pixel[:]
                        min_dist = current_dist

                resolved.append(min_color)
            color_and_proportion = list(zip(resolved, hist))

        if self.enhance:
            enhanced = [image_utils.enhance_color(color) for color, _ in color_and_proportion]
            color_and_proportion = list(zip(enhanced, hist))

        self.labels_to_rgb = {index: cp[0] for index, cp in enumerate(color_and_proportion)}
        cluster_histogram = [
            HistogramColor(color, proportion)
            for color, proportion in sorted(color_and_proportion, key=lambda x: x[1], reverse=True)
        ]
        self.dom_colors_rgb = [hist_color.rgb_rep for hist_color in cluster_histogram]

        return cluster_histogram

    def get_dominant_colors(self, hsv=False):
        if not hsv:
            return self.dom_colors_rgb
        else:
            return [image_utils.rgb_to_hsv(rgb_rep) for rgb_rep in self.dom_colors_rgb]

    def get_dominant_color(self, hsv=False):
        dom_colors = self.get_dominant_colors(hsv)
        return dom_colors[0]

    def get_color_chips(self, size=conf.DEFAULT_CHIP_SIZE):
        chips = []
        for color in self.get_dominant_colors():
            chip = np.zeros((size, size, 3), np.uint8)
            chip[:] = (color[0], color[1], color[2])
            chips.append(chip)

        return chips

    def get_remapped_image(self, other=None):
        if other is None:
            remapped_image = np.array([(self.labels_to_rgb[i]) for i in self.fitted_model.labels_])
            return np.uint8(remapped_image.reshape((self.img_height, self.img_width, 3)))
        else:
            # TODO test this
            other_rgb_data = other.image_rgb.reshape((other.img_height * other.img_width, 3))
            other_predicted = self.fitted_model.predict(other_rgb_data)
            remapped_image = np.array([self.fitted_model.cluster_centers_[i] for i in other_predicted])
            return np.uint8(remapped_image.reshape((self.img_height, self.img_width, 3)))

    def get_filename(self, index, type):
        if index is not None:
            filename = str(index)
        else:
            filename = ""

        filename += f"_{type}_n={self.n}_resolved={self.resolve}_enhance={self.enhance}.jpg"
        return filename

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
