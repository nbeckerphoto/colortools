from typing import List, Tuple

import numpy as np
from sklearn.cluster import KMeans


def fit_and_predict(image_rgb: np.array, n_clusters: int) -> Tuple[KMeans, np.array]:
    """_summary_

    Args:
        image_rgb (np.array): _description_
        n_clusters (int): _description_

    Returns:
        Tuple[KMeans, np.array]: _description_
    """
    image_size = image_rgb.shape[0] * image_rgb.shape[1]
    image_rgb_data = image_rgb.reshape((image_size, 3))
    clusters = KMeans(n_clusters=n_clusters, random_state=0)
    predicted = clusters.fit_predict(image_rgb_data)
    return clusters, predicted


def build_histogram_from_clusters(cluster_model: KMeans) -> List[Tuple[np.array, float]]:
    """Generate a distribution of predictions for provided k-means cluster model.

    Args:
        cluster_model (KMeans): Fitted k-means cluster model from which to generate a histogram.

    Returns:
        List[Tuple[np.array, float]]: A histogram (distribution) of predictions and their associated
            proportions.
    """
    bins = np.arange(0, len(cluster_model.cluster_centers_) + 1)  # bins by label ([0, 1, 2, 3, ...])
    hist, _ = np.histogram(cluster_model.labels_, bins=bins)  # array of counts by label
    hist = hist.astype("float32")
    hist /= hist.sum()  # array of proportions
    color_and_proportion = list(zip(cluster_model.cluster_centers_, hist))  # cluster centers are RGB colors

    return [
        (rgb_color, proportion)
        for rgb_color, proportion in sorted(color_and_proportion, key=lambda x: x[1], reverse=True)
    ]
