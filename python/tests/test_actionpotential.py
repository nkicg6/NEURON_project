# test for action potential
from . import context
import pytest
import numpy as np

from mitral_cell import actionpotential as ap

def test_ap_find_peak():
    arr =np.zeros(20)
    arr[10] = 15
    inds =  ap.ap_find_peak(arr)
    assert isinstance(inds, int)
    assert inds == 10
    two_peak = np.zeros(40)
    two_peak[10] = 15
    two_peak[20] = 15
    with pytest.raises(AssertionError):
        ap.ap_find_peak(two_peak)
