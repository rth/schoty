from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path

import numpy as np
from numpy.testing import assert_allclose


DATA_DIR = os.path.join(os.path.split(__file__)[0], 'data')

def assert_equal(x, y, message, rtol=1e-5):
    assert np.allclose(x, y, rtol=1e-5), message

