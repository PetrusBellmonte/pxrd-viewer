import io
import numpy as np
from pathlib import Path

import pytest

from pxrd_viewer.data_sources import load_xyd_file

# Collect all .xyd files in the data/xyds folder
DATA_DIR = Path(__file__).parent / "data" / "xyds"
XYD_FILES = list(DATA_DIR.glob("*.xyd"))


@pytest.fixture(params=XYD_FILES)
def xyd_file_path(request):
    return request.param


def test_load_xyd_file_shape_and_normalization(xyd_file_path):
    # Read file as bytes and wrap in BytesIO
    with open(xyd_file_path, "rb") as f:
        file_bytes = io.BytesIO(f.read())
    x, y = load_xyd_file(file_bytes)
    assert isinstance(x, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert x.shape == y.shape
    assert x.ndim == 1
    assert y.ndim == 1
    # Check normalization: max(y) should be 1.0
    assert np.isclose(np.max(y), 1.0)
    # Check that there are at least two data points
    assert len(x) >= 2
