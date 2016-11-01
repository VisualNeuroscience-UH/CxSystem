from __future__ import division
import matplotlib.pyplot as plt
import scipy.io as spio
from collections import OrderedDict
import numpy as np
import re
import pandas as pd

default_mat_file_path = '/home/henri/PycharmProjects/CX_Output/calcium24.mat'

class SimulationData(object):

    def __init__(self, mat_file=default_mat_file_path):

        self.data = self.loadmat(mat_file)
        self.spikedata = self.data['spikes_all']  # [0] -> neuron indices inside group, [1] -> spike times
        self.spikedata = OrderedDict(sorted(self.spikedata.items(), key=self._group_name_for_ordering ))  # TODO Order nicely
        self.runtime = self.data['runtime']
        self.neuron_groups = [row[0] for row in self.spikedata.items()[1:]]

    def loadmat(self, filename):
        '''
        this function should be called instead of direct spio.loadmat
        as it cures the problem of not properly recovering python dictionaries
        from mat files. It calls the function check keys to cure all entries
        which are still mat-objects
        '''
        data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
        return self._check_keys(data)

    def _check_keys(self, dict):
        '''
        checks if entries in dictionary are mat-objects. If yes
        todict is called to change them to nested dictionaries
        '''
        for key in dict:
            if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
                dict[key] = self._todict(dict[key])
        return dict

    def _todict(self, matobj):
        '''
        A recursive function which constructs from matobjects nested dictionaries
        '''
        dict = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, spio.matlab.mio5_params.mat_struct):
                dict[strg] = self._todict(elem)
            else:
                dict[strg] = elem
        return dict

    def _group_name_for_ordering(self, spikedata):
        corrected_name = re.sub(r'NG(\w{1})_', r'NG0\1_', spikedata[0])
        return str(corrected_name)


    # RASTER PLOT
    def rasterplot(self):

        fig = plt.figure()
        fig.suptitle('Ca2+ x mM')
        for index,group_spikes in enumerate(self.spikedata.items()[1:], start=1):
            ax = plt.subplot(16,1,index)
            plt.xlim([0, 0.5])
            ylabel = plt.ylabel(group_spikes[0])
            ylabel.set_rotation(0)
            ax.set_yticklabels([])

            try:
                ax.scatter(group_spikes[1][1], group_spikes[1][0], s=0.1)
            except IndexError:
                pass

        plt.show()


    # SPECTRAL PLOT
    def group_spectrum(self, neuron_group):

        sampling_frequency = 1000
        delta_t  = float(1/sampling_frequency)

        bins = np.arange(0.0, self.runtime+delta_t, delta_t)
        spikes = self.spikedata[neuron_group]

        binned_spikes = pd.cut(spikes[1], bins)
        counts = pd.value_counts(binned_spikes)
        counts = counts.reindex(binned_spikes.categories)  # value_counts orders by count so re-ordering is needed
        counts_n = len(counts)

        counts_tf = np.fft.rfft(counts)
        freqs = np.fft.rfftfreq(counts_n, delta_t)
        pow_spectrum = [pow(np.linalg.norm(x),2)/counts_n for x in counts_tf]

        plt.plot(freqs, pow_spectrum)
        plt.show()

        #plt.plot(bins, pd.value_counts(binned_spikes))


# MAIN

calcium24 = SimulationData()
#calcium24.rasterplot()
#calcium24.group_spectrum('NG7_SS_L4')
for group in calcium24.neuron_groups:
    calcium24.group_spectrum(group)