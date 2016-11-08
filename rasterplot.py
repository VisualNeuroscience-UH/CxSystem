from __future__ import division
import matplotlib.pyplot as plt
import scipy.io as spio
from collections import OrderedDict
import numpy as np
import re
import pandas as pd
import os.path
import zlib
import cPickle as pickle



class SimulationData(object):

    default_data_file = '/home/henri/PycharmProjects/CX_Output/calcium20.gz'
    #default_data_file = '/opt3/CX_Output/calcium/calcium21_2s.gz'
    default_data_file_path = '/opt3/CX_Output/calcium/'
    default_sampling_frequency = 1000

    group_numbering = {1: 'NG1_L1i_L1', 2: 'NG2_PC_L2toL1', 3: 'NG3_BC_L2', 4: 'NG4_MC_L2', 5: 'NG5_PC_L4toL2',
                       6: 'NG6_PC_L4toL1', 7: 'NG7_SS_L4', 8: 'NG8_BC_L4', 9: 'NG9_MC_L4', 10: 'NG10_PC_L5toL1',
                       11: 'NG11_BC_L5', 12: 'NG12_MC_L5', 13: 'NG13_PC_L6toL4', 14: 'NG14_PC_L6toL1',
                       15: 'NG15_BC_L6', 16: 'NG16_MC_L6'}

    def __init__(self, data_file=default_data_file):

        basename = os.path.basename(data_file)
        if basename[-2:] == 'gz':
            self.data = self._loadgz(data_file)
        elif basename[-3:] == 'mat':
            self.data = self._loadmat(data_file)
        else:
            print 'Format not supported so no file was loaded.'

        self.datafile = data_file

        self.spikedata = self.data['spikes_all']  # [0] -> neuron indices inside group, [1] -> spike times
        self.spikedata = OrderedDict(sorted(self.spikedata.items(), key=self._group_name_for_ordering ))  # TODO Order nicely
        self.runtime = self.data['runtime']
        self.neuron_groups = [row[0] for row in self.spikedata.items()[1:]]

    def _loadgz(self, filename):
        with open(filename, 'rb') as fb:
            d_pickle = zlib.decompress(fb.read())
            data = pickle.loads(d_pickle)

        return data

    def _loadmat(self, filename):
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

    def _check_group_name(self, group):
        if isinstance(group, int):
            return SimulationData.group_numbering[group]
        else:
            return group

    def rasterplot(self):

        runtime = self.runtime
        fig = plt.figure()
        fig.suptitle(self.datafile)
        for index,group_spikes in enumerate(self.spikedata.items()[1:], start=1):
            ax = plt.subplot(16,1,index)
            plt.xlim([0, runtime])
            ylabel = plt.ylabel(group_spikes[0])
            ylabel.set_rotation(0)
            ax.set_yticklabels([])

            try:
                ax.scatter(group_spikes[1][1], group_spikes[1][0], s=0.1)
            except IndexError:
                pass

        plt.show()

    def spikes_spectrum_group(self, neuron_group):

        neuron_group = self._check_group_name(neuron_group)

        sampling_frequency = SimulationData.default_sampling_frequency
        delta_t = float(1/sampling_frequency)

        bins = np.arange(0.0, self.runtime+delta_t, delta_t)
        counts_n = len(bins)-1
        spikes = self.spikedata[neuron_group]
        freqs = np.fft.rfftfreq(counts_n, delta_t)

        try:
            binned_spikes = pd.cut(spikes[1], bins)
            counts = pd.value_counts(binned_spikes)
            counts = counts.reindex(binned_spikes.categories)  # value_counts orders by count so re-ordering is needed
            counts_tf = np.fft.rfft(counts)
            pow_spectrum = [pow(np.linalg.norm(x), 2) / counts_n for x in counts_tf]

        except IndexError:
            print 'No spikes in group ' + neuron_group + '.'
            pow_spectrum = freqs


        return freqs, pow_spectrum

    def plot_spikes_spectra(self):

        fig = plt.figure()

        for index, group in enumerate(self.neuron_groups, start=1):
            ax = plt.subplot(4, 4, index)
            ax.set_yticklabels([])
            plt.title(group, fontsize=8)
            freqs, spectrum = self.spikes_spectrum_group(group)
            if freqs is spectrum:
                ax.set_axis_bgcolor((0.8, 0.8, 0.8))
            else:
                plt.plot(freqs, spectrum)

        plt.tight_layout(pad=0.1)
        fig.suptitle(os.path.basename(self.datafile), fontsize=16)
        plt.show()

    def spikes_spectrum_all(self):
        pass

    def plot_voltage(self, neuron_group):

        neuron_group = self._check_group_name(neuron_group)

        voltage = self.data['vm_all'][neuron_group]
        [plt.plot(voltage[i]) for i in range(0,len(voltage))]
        plt.show()


    def voltage_spectrum_group(self, neuron_group):

        neuron_group = self._check_group_name(neuron_group)
        sampling_frequency = 1000000
        delta_t = float(1 / sampling_frequency)
        bins = np.arange(0.0, self.runtime, delta_t)
        # counts_n = len(bins)
        freqs = np.fft.rfftfreq(counts_n, delta_t)
        counts_n = len(freqs)

        voltage = pd.DataFrame(data=self.data['vm_all'][neuron_group])
        voltage_aggregate = voltage.mean()

        voltage_agg_tf = np.fft.rfft(voltage_aggregate)
        pow_spectrum = [pow(np.linalg.norm(x), 2) / counts_n for x in voltage_agg_tf]

        return freqs, pow_spectrum

# MAIN

if __name__ == '__main__':
    calcium_sim = SimulationData()
    #calcium_sim.plot_spikes_spectra()
    #calcium_sim.plot_voltage(7)
    #calcium_sim.rasterplot()
    #pass
    freqs, spectrum = calcium_sim.voltage_spectrum_group(7)
    plt.plot(freqs, spectrum)


