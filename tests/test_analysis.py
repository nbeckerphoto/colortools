import numpy as np
import pytest
from colortools import util
from colortools.analysis import build_histogram_from_clusters, fit_and_predict
from PIL import Image

from conftest import ARRAY_TOLERANCE


@pytest.mark.parametrize("test_side_length, color", [(100, (255, 0, 0)), (100, (0, 255, 0)), (100, (0, 0, 255))])
def test_fit_and_predict_solid_color(test_side_length, color):
    """A single-cluster fit on a solid-color image finds that color as its one cluster center."""
    image = Image.new("RGB", (test_side_length, test_side_length), color)
    clusters, predicted = fit_and_predict(np.asarray(image), 1)
    assert (clusters.cluster_centers_ == [list(color)]).all()
    assert (predicted == [0] * image.size[0] * image.size[1]).all()


@pytest.mark.parametrize("color", [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 64, 200)])
def test_build_histogram_from_clusters_lab(color):
    """Building a histogram from a Lab-space fit converts cluster centers back to the correct RGB color."""
    image = Image.new("RGB", (100, 100), color)
    image_data = util.rgb_to_lab(np.asarray(image))
    clusters, _ = fit_and_predict(image_data, 1)

    cluster_histogram = build_histogram_from_clusters(clusters, util.ColorSpace.LAB)
    assert len(cluster_histogram) == 1
    rgb, proportion = cluster_histogram[0]
    np.testing.assert_allclose(rgb, color, atol=ARRAY_TOLERANCE)
    assert proportion == pytest.approx(1.0)
