from typing import List, Tuple

import numpy as np
from sklearn.cluster import KMeans

import colortools.util as util


def fit_and_predict(image_data: np.ndarray, n_clusters: int) -> Tuple[KMeans, np.ndarray]:
    """Create a scikit-learn k-means model and fit to provided data.

    Create the model, fit it to the provided image data, and get predictions for the provided data.

    Args:
        image_data (np.ndarray): An image as an array, in whatever color space clustering should happen in
            (e.g. RGB or Lab).
        n_clusters (int): The number of clusters to find in the data.

    Returns:
        Tuple[KMeans, np.ndarray]: The fitted model clusters and the predictions for the provided data.
    """
    image_size = image_data.shape[0] * image_data.shape[1]
    image_data = image_data.reshape((image_size, 3))
    clusters = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto")
    predicted = clusters.fit_predict(image_data)
    return clusters, predicted


def build_histogram_from_clusters(
    cluster_model: KMeans, color_space: util.ColorSpace = util.ColorSpace.LAB
) -> List[Tuple[np.ndarray, float]]:
    """Generate a distribution of predictions for provided k-means cluster model.

    Args:
        cluster_model (KMeans): Fitted k-means cluster model from which to generate a histogram.
        color_space (util.ColorSpace, optional): The color space the model was fit in. If LAB, cluster centers
            are converted back to RGB before being returned. Defaults to util.ColorSpace.LAB.

    Returns:
        List[Tuple[np.ndarray, float]]: A histogram (distribution) of predictions and their associated
            proportions. Cluster centers (colors) are always in RGB, regardless of `color_space`.
    """
    bins = np.arange(0, len(cluster_model.cluster_centers_) + 1)  # bins by label ([0, 1, 2, 3, ...])
    histogram, _ = np.histogram(cluster_model.labels_, bins=bins)  # array of counts by label
    histogram = histogram.astype("float32")
    histogram /= histogram.sum()  # array of proportions

    cluster_centers_rgb = cluster_model.cluster_centers_
    if color_space == util.ColorSpace.LAB:
        cluster_centers_rgb = util.lab_to_rgb(cluster_centers_rgb)
    color_and_proportion = list(zip(cluster_centers_rgb, histogram))

    return [
        (rgb_color, proportion)
        for rgb_color, proportion in sorted(color_and_proportion, key=lambda x: x[1], reverse=True)
    ]
