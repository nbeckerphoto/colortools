#  Determine the dominant colors in an image.
#  Ideas shamelessly borrowed from:
# - https://www.timpoulsen.com/2018/finding-the-dominant-colors-of-an-image.html
# - https://code.likeagirl.io/finding-dominant-colour-on-an-image-b4e075f98097
# - https://github.com/baptiste0928/dominant-color
#   - Specifically, the algorithm described here:
#     https://github.com/baptiste0928/dominant-color/blob/main/src/lib.rs#L27

import logging
from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
from PIL import Image

import colortools.util as util
from colortools.analysis import build_histogram_from_clusters, fit_and_predict
from colortools.heuristics import NColorsHeuristic, compute_hue_dist, get_n_heuristic

logging.basicConfig(format="%(levelname)s: %(message)s")


class AnalyzedImage:
    """
    Internal representation of an analyzed image. Includes basic image metadata as well as analysis results.
    """

    def __init__(
        self,
        image_path: Union[Path, str],
        resize_long_axis: int,
        edge_crop: float,
        dominant_color_algorithm: util.DominantColorAlgorithm,
        n_colors: int,
        auto_n_heuristic: NColorsHeuristic,
    ):
        """Create an instance of this class.

        Args:
            image_path (Union[Path, str]): The path to the JPG image on disk.
            resize_long_axis (int): The target length of the long axis after resizing.
            dominant_color_algorithm (util.DominantColorAlgorithm): The algorithm to use for determining
                the dominant colors.
            n_colors (int): The number of dominant colors to find. More useful when using KMEANS for
                determining dominant colors.
            auto_n_heuristic (NHeuristic): The heuristic to use for automatically determining the number of
                colors to find in this image. More useful when using KMEANS for determining dominant colors.
        """
        if isinstance(image_path, str):
            image_path = Path(image_path)
        self.image_path = image_path
        self.dominant_color_algorithm = dominant_color_algorithm

        # set image, dimensions, and orientation
        pil_image = Image.open(image_path)
        original_width, original_height = pil_image.size
        if original_height > original_width:
            self.orientation = util.ImageOrientation.VERTICAL
            resized_height = resize_long_axis if resize_long_axis is not None else original_height
            resized_width = int((original_width / original_height) * resized_height)
        else:
            self.orientation = util.ImageOrientation.HORIZONTAL
            resized_width = resize_long_axis if resize_long_axis is not None else original_width
            resized_height = int((original_height / original_width) * resized_width)

        self.pil_image = pil_image.resize((resized_width, resized_height))
        self.width, self.height = self.pil_image.size
        self.edge_crop = edge_crop

        # set n, if not provided
        if n_colors is None or n_colors == 0:
            if auto_n_heuristic is None:
                if not self.dominant_color_algorithm == util.DominantColorAlgorithm.HUE_DIST:
                    logging.warning("neither n_colors nor auto_n_heuristic was provided; setting n_colors=1")
                self.n_colors = 1
            else:
                auto_n_heuristic_func = get_n_heuristic(auto_n_heuristic)
                self.n_colors = auto_n_heuristic_func(self.get_as_array(hsv=True, crop_center=True))
        else:
            self.n_colors = n_colors

        if self.dominant_color_algorithm == util.DominantColorAlgorithm.HUE_DIST:
            if self.n_colors > 1:
                logging.warning(
                    f"Using {self.dominant_color_algorithm.value} with n_colors={self.n_colors}; "
                    "dominant colors may be very similar."
                )
            self.dominant_colors_rgb, self.dominant_colors_hsv = self.get_dominant_colors_hue_dist(self.n_colors)
        elif self.dominant_color_algorithm == util.DominantColorAlgorithm.KMEANS:
            self.dominant_colors_rgb, self.dominant_colors_hsv = self.get_dominant_colors_kmeans(self.n_colors)
        else:
            raise ValueError(f"Unrecognized dominant color algorithm: {self.dominant_color_algorithm}")

    def get_dominant_colors_hue_dist(self, n_colors: int) -> Tuple[List, List]:
        """Get dominant colors using the HUE_DIST algorithm.

        Args:
            n_colors (int): The number of dominant colors to compute.

        Returns:
            Tuple[List, List]: The dominant colors (RGB values, HSV values).
        """
        hue_dist = compute_hue_dist(self.get_as_array(hsv=True, crop_center=True))
        hue_dist = [
            (hue, hsv_list) for hue, hsv_list in sorted(hue_dist.items(), key=lambda item: len(item[1]), reverse=True)
        ]

        dominant_colors_hsv = []
        for i in range(n_colors):
            current_hue_list = hue_dist[i]
            hue = current_hue_list[0]
            if len(current_hue_list[1]) > 0:
                avg_sat = np.median([hsv[1] for hsv in current_hue_list[1]])
                avg_val = np.median([hsv[2] for hsv in current_hue_list[1]])
            else:
                logging.warning(
                    f"No pixels found for hue value {hue}; n_colors may be larger than number of hues in image."
                )
                avg_sat, avg_val = 0, 0
            dominant_colors_hsv.append([hue, avg_sat, avg_val])

        dominant_colors_hsv = util.normalize_8bit_hsv(dominant_colors_hsv)
        dominant_colors_rgb = util.hsv_to_rgb(dominant_colors_hsv)
        return dominant_colors_rgb, dominant_colors_hsv

    def get_dominant_colors_kmeans(self, n_colors: int) -> Tuple[List, List]:
        """Get dominant colors using the KMEANS algorithm.

        Args:
            n_colors (int): The number of dominant colors to compute.

        Returns:
            Tuple[List, List]: The dominant colors (RGB values, HSV values).
        """
        self.model, self.predicted = fit_and_predict(self.get_as_array(crop_center=True), n_colors)
        self.cluster_histogram = build_histogram_from_clusters(self.model)
        dominant_colors_rgb = [rgb.tolist() for rgb, _ in self.cluster_histogram]
        dominant_colors_hsv = util.rgb_to_hsv(dominant_colors_rgb)
        return dominant_colors_rgb, dominant_colors_hsv

    def get_as_array(self, hsv=False, crop_center=False) -> np.ndarray:
        """Get this image as a NumPy array.

        Args:
            hsv (bool, optional): Whether to convert pixels to HSV space before returning. Defaults to False.

        Returns:
            np.ndarray: This image as a NumPy array.
        """
        if hsv:
            as_array = np.asarray(self.pil_image.convert("HSV"))
        else:
            as_array = np.asarray(self.pil_image)

        if crop_center:
            return util.crop_center(as_array, self.edge_crop)
        else:
            return as_array

    def get_dominant_colors(self, hsv=False, round=False) -> List[List]:
        """Get the dominant colors that were computed for this image.

        Args:
            hsv (bool, optional): Whether to convert colors to HSV space before returning. Defaults to False.

        Returns:
            List[List]: A list of the dominant colors for this image.
        """
        dom_colors = self.dominant_colors_hsv if hsv else self.dominant_colors_rgb
        dom_colors = util.round_array(dom_colors) if round else dom_colors
        if hsv:
            for dc in dom_colors:
                dc[0] = dc[0] % 360  # hue space fix
        return dom_colors

    def get_dominant_color(self, hsv=False, round=False) -> List:
        """Get the single most dominant color for this image.

        Args:
            hsv (bool, optional): Whether to convert the color to HSV space before returning. Defaults to False.

        Returns:
            List: _description_
        """
        return self.get_dominant_colors(hsv, round)[0]

    def get_orientation(self) -> util.ImageOrientation:
        """Get the orientation of this image.

        Returns:
            util.ImageOrientation: This image's orientation.
        """
        return self.orientation

    def is_bw(self) -> bool:
        """Determine whether this image is black and white.

        Determines whether the represented image is black and white by checking to see if the saturation of
        the most dominant color is equal to 0.

        Returns:
            bool: Whether this image is black and white or not.
        """
        return self.get_dominant_color(hsv=True)[1] < 1

    def get_remapped_image(self, other: "AnalyzedImage" = None) -> Union[Image.Image, None]:
        """Use the model created for this image to predict mapped colors for another image (or this image itself).

        In machine-learning terms, use the model that was trained with this image representation to predict values for
        the provided input, which may optionally be another image.

        Essentially, this method can be used to map the pixels of this image to the colors represented by the cluster
        centers that were discovered during model fitting. The result is an image reduced to the same number of colors
        as there are dominant colors.

        Args:
            other (AnalyzedImage, optional): Another image to use as input to the model that was trained using this
                image. If `None`, use this image's original pixels as input. Defaults to None.

        Returns:
            Union[Image.Image, None]: An image mapped to the colors represented by this analyzed image's associated
                model, if present, else None.
        """
        if self.dominant_color_algorithm == util.DominantColorAlgorithm.KMEANS:
            target_colors = self.model.cluster_centers_
            if other is None:
                height, width = self.height, self.width
                other_rgb_data = self.get_as_array().reshape((height * width, 3))
            else:
                height, width = other.height, other.width
                other_rgb_data = other.get_as_array().reshape((height * width, 3))

            other_predicted = self.model.predict(other_rgb_data)
            remapped_image = np.array([target_colors[i] for i in other_predicted])
            return Image.fromarray(np.uint8(remapped_image.reshape((height, width, 3))))
        else:
            raise ValueError(f"Cannot remap images using the {self.dominant_color_algorithm.value} algorithm")

    def generate_filename(self, index: int, base: str) -> str:
        """Generate a filename using this analyzed image.

        Args:
            index (int): An index to use as a prefix for the generated filename.
            base (str): A base string to use in the generated filename.

        Returns:
            str: The generated filename.
        """
        if index is not None:
            filename = f"{str(index)}_"
        else:
            filename = ""

        dom_color_hsv = util.round_array(self.get_dominant_color(hsv=True))
        dom_hue, dom_sat, dom_val = dom_color_hsv[0], dom_color_hsv[1], dom_color_hsv[2]
        filename += f"{base}_hue={dom_hue}_sat={dom_sat}_val={dom_val}_n={self.n_colors}.jpg"
        return filename

    def get_pretty_string(self) -> str:
        """Get a pretty string representation of this image and its dominant colors.

        Returns:
            str: A pretty string representation of this analyzed image.
        """
        out = f"{self.image_path.name}: n={self.n_colors}, algorithm={self.dominant_color_algorithm.value} \n"
        out += f"    rgb={util.round_array(self.dominant_colors_rgb)}\n"
        out += f"    hsv={util.round_array(self.dominant_colors_hsv)}"
        return out

    def get_huesort_metric(self) -> int:
        """Get a value to use for sorting.

        Currently, this method returns the dominant color's hue, shifted by -90 degrees so that colors in the
        red region of the spectrum come before colors in the blue region of the spectrum. (If not shifted, some
        reds may appear at the beginning of the sort order, while some reds might appear at the end of the sort
        order.)

        Returns:
            int: A value to use when sorting this image.
        """
        dom_hue = self.get_dominant_color(hsv=True)[0]
        dom_hue = (dom_hue + 90) % 360
        return dom_hue
