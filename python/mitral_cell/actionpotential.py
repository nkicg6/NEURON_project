# action potential analysis
import numpy as np
import scipy.signal as s

def ap_find_peak(y: np.ndarray) -> int:
    """use scipy to find the peak of the AP. Fails if multiple peaks or no peaks"""
    p_inds, _ = s.find_peaks(y, height = 10, prominence=None, distance=5)
    if len(p_inds) != 1:
        raise AssertionError(f"Must be one peak. {len(p_inds)} detected")
    int_ind = p_inds[0]
    return int(int_ind)

def ap_calculate_amplitude(y: np.ndarray, ind: int, rmp: float) -> float:
    """return the amplitude of the action potential"""
    assert len(y) > ind, "Index out of range. length array = {len(y)}, index = {ind}"
    assert rmp<0, "RMP should be negative, did you make a mistake? RMP = {rmp}"
    amp_peak = y[ind]
    return float(abs(rmp) + abs(amp_peak))

def ap_batch_amplitude(list_of_traces: list, rmp: float) -> list:
    """composed function to map over a list of numpy arrays representing a series of NEURON simulations to calculate amplitude
    """
    amps = []
    for experiment in list_of_traces:
        try:
            inds = ap_find_peak(experiment)
            amp = ap_calculate_amplitude(experiment, inds, rmp)
            amps.append(amp)
        except AssertionError:
            amps.append(0)
    return amps

def ap_normalize_to_0(y: np.ndarray, rmp: float) -> np.ndarray:
    """return the trace normalized to 0 for further calculations"""
    return y - rmp
def ap_normalized_half_max(normalized_y: np.ndarray, peak_ind: int) -> float:
    """return the half max of the peak"""
    return normalized_y[peak_ind]/2

def ap_simple_fwhm_inds(normalized_y: np.ndarray, half_max: float) -> tuple:
    """ simple method for FWHM indicies. Only works with ONE peak."""
    greater = np.where(normalized_y > half_max)[0]
    assert len(greater > 2), "nothing greater than half max detected."
    return (greater[0], greater[-1])

def ap_calculate_fwhm(x: np.ndarray, first_ind: int, second_ind: int) -> float:
    assert second_ind > first_ind, f"Second ind ({second_ind}) must be > first ind ({first_ind})."
    return float(x[second_ind] - x[first_ind])

def ap_batch_fwhm(list_of_times: list, list_of_traces: list, rmp: float) -> list:
    assert len(list_of_times) == len(list_of_traces), f"Length of time ({len(list_of_times)}) != to length of traces ({len(list_of_traces)})."
    fwhms = []
    for time, experiment in zip(list_of_times, list_of_traces):
        try:
            ind = ap_find_peak(experiment)
            norm_y = ap_normalize_to_0(experiment, rmp)
            half_max = ap_normalized_half_max(norm_y, ind)
            first, second = ap_simple_fwhm_inds(norm_y, half_max)
            fwhm = ap_calc_fwhm(time, first, second)
            fwhms.append(fwhm)
        except AssertionError:
            fwhms.append(0)
    return fwhms
