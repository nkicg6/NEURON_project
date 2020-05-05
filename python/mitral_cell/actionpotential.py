# action potential analysis
import numpy as np
import scipy.signal as s

def ap_find_peak(y: np.ndarray) -> int:
    """use scipy to find the peak of the AP"""
    p_inds, _ = s.find_peaks(y, height = 10, prominence=None, distance=5)
    if len(p_inds) != 1:
        raise AssertionError(f"Must be one peak. {len(p_inds)} detected")
    int_ind = p_inds[0]
    return int(int_ind)

def ap_calculate_amplitude(y: np.array,ind: np.array, rmp: float) -> float:
    """return the amplitude of the action potential"""
    if isinstance(ind, type(None)):
        raise AssertionError("Index not found")
    assert len(ind) == 1, f"Length of indicies must be = 1, length = {len(ind)}"
    assert rmp < 0, f"resting membrane potential must be negative, rmp={rmp}"
    amp_peak = y[ind][0]
    return float(abs(rmp) + abs(amp_peak))

def ap_batch_amplitude(list_of_traces: list, rmp: float) -> list:
    """composed function to map over a list of numpy arrays representing a series of NEURON simulations to calculate amplitude
    """
    amps = []
    for experiment in list_of_traces:
        inds = ap_find_peak(experiment)
        try:
            amp = ap_calculate_amplitude(experiment, inds, rmp)
            amps.append(amp)
        except AssertionError:
            amps.append(0)
    return amps
