import numpy as np
import pytest
from PIL import Image
from colorsort.analysis import fit_and_predict


@pytest.mark.parametrize("test_side_length, color", [(100, (255, 0, 0)), (100, (0, 255, 0)), (100, (0, 0, 255))])
def test_analyzed_image_resize(test_side_length, color):
    image = Image.new("RGB", (test_side_length, test_side_length), color)
    clusters, predicted = fit_and_predict(np.asarray(image), 1)
    assert (clusters.cluster_centers_ == [list(color)]).all()
    assert (predicted == [0] * image.size[0] * image.size[1]).all()
