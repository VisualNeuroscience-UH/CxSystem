__author__ = 'V_AD'
from numpy import *
from brian2 import *
import scipy.io as sio
import os


class input(object):
    def __init__(self):
        self.indices = array([])
        self.times = array([])

    def read_mat_file(self,path,freq):
        _V1_mats = {}
        sio.loadmat(path, _V1_mats)
        _all_stim = squeeze(_V1_mats['stimulus'])
        if len(_all_stim.shape) > 1:
            _N_stim = _all_stim.shape[1]
        else:
            _N_stim = 1  # there is at least one stimulus

        print str(_N_stim) + ' stimuli found in file '
        for _stim_ndx in range(_N_stim):
            if _N_stim > 1:
                _rel_rates = _all_stim.T[_stim_ndx]
            else:
                _rel_rates = _all_stim.T
            _rates = _rel_rates * freq



test = input ()
test.read_mat_file(os.path.join(os.getcwd(),'V1_input_layer_2015_10_30_11_7_31.mat'), 190 * Hz)