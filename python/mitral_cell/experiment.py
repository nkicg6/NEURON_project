# utilities to run experiments and save results
import numpy as np


def get_results(results_array, get_id):
    arr = results_array["recording_vectors"][get_id]
    return np.asarray(arr).copy()
