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
    no_peaks = np.zeros(20)
    with pytest.raises(AssertionError):
        ap.ap_find_peak(no_peaks)
    arr[10] = 15


def test_ap_calculate_amplitude():
    arr = np.zeros(20)
    arr[10] = 15
    ind = ap.ap_find_peak(arr)
    assert ap.ap_calculate_amplitude(arr, ind, -65) == 80
    # index out of range
    with pytest.raises(AssertionError):
        ap.ap_calculate_amplitude(arr, 30, -65)
    with pytest.raises(AssertionError):
        ap.ap_calculate_amplitude([], 30, -65)
    with pytest.raises(AssertionError):
        ap.ap_calculate_amplitude(arr, 30, 65)

def test_ap_batch_amplitude():
    arr = np.zeros(20)
    arr[10] = 15
    arr2 = arr.copy()
    list_of_arrs = [arr, arr2]
    assert ap.ap_batch_amplitude(list_of_arrs, -65) == [80, 80]
    arr3 = np.zeros(20)
    with_no_peak = [arr, arr2, arr3]
    assert ap.ap_batch_amplitude(with_no_peak, -65) == [80, 80, 0]
    with_empty_arr = [arr, arr2, arr3, np.asarray([])]
    assert ap.ap_batch_amplitude(with_empty_arr, -65) == [80, 80, 0, 0]
