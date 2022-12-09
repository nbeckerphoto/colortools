from typing import List, Tuple

import numpy as np
from sklearn.cluster import KMeans


def fit_and_predict(rgb_image_data: np.ndarray, n_clusters: int) -> Tuple[KMeans, np.ndarray]:
    """Create a scikit-learn k-means model and fit to provided data.

    Create the model, fit it to the provided RGB image data, and get predictions for the provided data.

    Args:
        rgb_image_data (np.ndarray): An RGB image as an array.
        n_clusters (int): The number of clusters to find in the data.

    Returns:
        Tuple[KMeans, np.ndarray]: The fitted model clusters and the predictions for the provided data.
    """
    image_size = rgb_image_data.shape[0] * rgb_image_data.shape[1]
    image_rgb_data = rgb_image_data.reshape((image_size, 3))
    clusters = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto")
    predicted = clusters.fit_predict(image_rgb_data)
    return clusters, predicted


def build_histogram_from_clusters(cluster_model: KMeans) -> List[Tuple[np.ndarray, float]]:
    """Generate a distribution of predictions for provided k-means cluster model.

    Args:
        cluster_model (KMeans): Fitted k-means cluster model from which to generate a histogram.

    Returns:
        List[Tuple[np.ndarray, float]]: A histogram (distribution) of predictions and their associated
            proportions.
    """
    bins = np.arange(0, len(cluster_model.cluster_centers_) + 1)  # bins by label ([0, 1, 2, 3, ...])
    histogram, _ = np.histogram(cluster_model.labels_, bins=bins)  # array of counts by label
    histogram = histogram.astype("float32")
    histogram /= histogram.sum()  # array of proportions
    color_and_proportion = list(zip(cluster_model.cluster_centers_, histogram))  # cluster centers are RGB colors

    return [
        (rgb_color, proportion)
        for rgb_color, proportion in sorted(color_and_proportion, key=lambda x: x[1], reverse=True)
    ]
