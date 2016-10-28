__author__ = 'V_AD'
from numpy import *
from brian_genn_version  import *
# import scipy.io as sio
from scipy import io
import os


class stimuli(object):
    '''
    [Extracted from VCX_model] This is the stimulation object for applying the input to a particular NeuronGroup(). Currently only video input is supported.
    '''
    def __init__(self):
        self.indices = array([])
        self.times = array([])
        self.i_patterns = {}
        self.input_defs = []
        self.BaseLine= 0 * second
        self.SimulationDuration = 0.4 * second

    def generate_inputs(self, path, freq):
        '''
        The method for generating input based on the .mat file, using the internal _initialize_inputs() and _calculate_input_seqs() methods.

        :param path: path to the input .mat file.
        :param freq: frequency.
        :return:
        '''
        self._initialize_inputs(path, freq)
        self._calculate_input_seqs(path)

    def load_input_seq(self, input_path):
        _input_file = os.path.join(input_path[0:[idx for idx, ltr in enumerate(input_path) if ltr == '/'][-1]], 'input.mat')
        tmp_dict = io.loadmat(_input_file, variable_names='spikes_0')
        new_spikes = tmp_dict['spikes_0']
        spikes_str = 'GEN_SP = array(%s)' %str(list(new_spikes[0]))
        times_str = 'GEN_TI = array(%s)*second' %str(list(new_spikes[1]))
        SG_str = 'GEN = SpikeGeneratorGroup(%d, GEN_SP, GEN_TI)'%int(max(new_spikes[0])+1)
        return spikes_str, times_str,  SG_str , int(max(new_spikes[0])+1)

    def get_input_positions(self, path):
        '''
        Extract the positions from the .mat file.

        :param path: Path to the .mat file.
        '''
        _V1_mats = {}
        io.loadmat(path, _V1_mats)
        return _V1_mats['z_coord']

    def _initialize_inputs(self,  path, freq):

        print "Initializing stimuli..."

        _new_input_defs = []
        #type : video
        _V1_mats = {}

        io.loadmat(os.path.abspath(path), _V1_mats)
        try:
            frameduration = double(_V1_mats['frameduration'])  # _V1_mats['frameduration'] is numpy nd array
        except:
            frameduration = 100  # in ms
        frames = TimedArray(np.transpose(_V1_mats['stimulus']),
                            dt=frameduration * ms)  # video_data has to be shape (frames, neurons), dt=frame rate
        self.frames = frames
        exec 'self.factor = %s' %freq
        self.i_patterns[len(self.i_patterns)] = frames.values * self.factor  # These must be final firing rates
        _all_stim = squeeze(_V1_mats['stimulus'])
        if len(_all_stim.shape) == 2:
            slash_indices = [idx for idx, ltr in enumerate(path) if ltr == '/']
            print 'One video stimulus found in file ' + path[slash_indices[-1]+1:]

        # self.input_defs = _new_input_defs


    def _calculate_input_seqs(self,path):

        inputdt = defaultclock.dt
        spikemons = []
        N0 = len(self.i_patterns[0].T)
        frames = self.frames
        factor = self.factor
        tmp_group = NeuronGroup(N0, 'rate = frames(t,i)*factor : Hz', threshold='rand()<rate*dt')
        tmp_network = Network()
        tmp_network.add(tmp_group)
        tmp_mon = SpikeMonitor(tmp_group)
        tmp_network.add(tmp_mon)
        spikemons.append(tmp_mon)
        if self.BaseLine == 0 * second:
            tmp_network.run(self.SimulationDuration, report='text')
        else:
            tmp_network.run(self.BaseLine)
            tmp_network.run(self.SimulationDuration - self.BaseLine)
        save_path = os.path.join(path[0:[idx for idx, ltr in enumerate(path) if ltr == '/'][-1]],'input.mat')
        self.VCX_save_input_sequence(spikemons,save_path)



    def VCX_save_input_sequence(self,spike_mons, filename):
        data = {}
        for ii in range(len(spike_mons)):
            data['spikes_' + str(ii)] = spike_mons[ii].it  # .spikes in Brian 1.X
        io.savemat(filename, data)

            # _V1_mats = {}
        # sio.loadmat(path, _V1_mats)
        # _all_stim = squeeze(_V1_mats['stimulus'])
        # if len(_all_stim.shape) > 1:
        #     _N_stim = _all_stim.shape[1]
        # else:
        #     _N_stim = 1  # there is at least one stimulus
        #
        # print str(_N_stim) + ' stimuli found in file '
        # for _stim_ndx in range(_N_stim):
        #     if _N_stim > 1:
        #         _rel_rates = _all_stim.T[_stim_ndx]
        #     else:
        #         _rel_rates = _all_stim.T
        #     self.i_patterns[len(self.i_patterns)] =  _rel_rates * self.factor




# test = input ()
# test._calculate_input_seqs(os.path.join(os.getcwd(),'V1_input_layer_2015_10_30_11_7_31.mat'), 190 * Hz)