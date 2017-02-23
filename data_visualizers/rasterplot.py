from __future__ import division
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import scipy.io as spio
from collections import OrderedDict
import numpy as np
import re
import pandas as pd
import os.path
import zlib
import cPickle as pickle
import bz2
from brian2 import *
import random


mycmap = 'jet'


class SimulationData(object):

    #default_data_file = '/home/henri/PycharmProjects/CX_Output/'
    default_data_file = '/opt3/CX_Output/calcium/calcium21_2s.gz'
    default_data_file_path = '/opt3/tmp/'
    default_sampling_frequency = 1000
    defaultclock_dt = 0.1 * ms

    group_numbering = {1: 'NG1_L1i_L1', 2: 'NG2_PC_L2toL1', 3: 'NG3_BC_L2', 4: 'NG4_MC_L2', 5: 'NG5_PC_L4toL2',
                       6: 'NG6_PC_L4toL1', 7: 'NG7_SS_L4', 8: 'NG8_BC_L4', 9: 'NG9_MC_L4', 10: 'NG10_PC_L5toL1',
                       11: 'NG11_BC_L5', 12: 'NG12_MC_L5', 13: 'NG13_PC_L6toL4', 14: 'NG14_PC_L6toL1',
                       15: 'NG15_BC_L6', 16: 'NG16_MC_L6'}

    neurons_in_group = {1: 338, 2: 5877, 3: 1198, 4: 425, 5: 2674, 6: 1098, 7: 406, 8: 329, 9: 137, 10: 5050,
                        11: 558, 12: 491,  13: 9825, 14: 1637, 15: 813, 16: 372}

    group_number_to_type = {1: 'L1i', 2: 'PC', 3: 'BC', 4:'MC', 5: 'PC', 6:'PC', 7:'SS', 8:'BC', 9:'MC', 10: 'PC',
                            11: 'BC', 12: 'MC', 13: 'PC', 14: 'PC', 15:'BC', 16:'MC'}

    layers = [2, 4, 5, 6]

    # Per group returns an array of [[excitatory] and [inhibitory]] groups
    groups_of_layer = {1: [[], [1]], 2: [[2], [3, 4]], 4: [[5, 6, 7], [8,9]], 5: [[10], [11,12]], 6:[[13, 14], [15, 16]]}

    def __init__(self, data_file=default_data_file, data_path=default_data_file_path):

        basename = os.path.basename(data_file)
        data_loc = data_path + data_file
        if basename[-2:] == 'gz':
            self.data = self._loadgz(data_loc)
        elif basename[-3:] == 'mat':
            self.data = self._loadmat(data_loc)
        elif basename[-3:] == 'bz2':
            self.data = self._loadbz2(data_loc)
        else:
            print 'Format not supported so no file was loaded.'

        self.datafile = data_file

        self.spikedata = self.data['spikes_all']  # [group][0] -> neuron indices inside group, [group][1] -> spike times
        self.spikedata = OrderedDict(sorted(self.spikedata.items(), key=self._group_name_for_ordering ))  # TODO Order nicely
        self.runtime = self.data['runtime']
        self.neuron_groups = [row[0] for row in self.spikedata.items()[1:]]

    def _loadgz(self, filename):
        with open(filename, 'rb') as fb:
            d_pickle = zlib.decompress(fb.read())
            data = pickle.loads(d_pickle)

        return data

    def _loadbz2(self, filename):
        with bz2.BZ2File(filename, 'rb') as fb:
            data = pickle.load(fb)

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
        counts_n = len(bins) # Broken?
        freqs = np.fft.rfftfreq(counts_n, delta_t)
        counts_n = len(freqs)

        voltage = pd.DataFrame(data=self.data['vm_all'][neuron_group])
        voltage_aggregate = voltage.mean()

        voltage_agg_tf = np.fft.rfft(voltage_aggregate)
        pow_spectrum = [pow(np.linalg.norm(x), 2) / counts_n for x in voltage_agg_tf]

        return freqs, pow_spectrum

    def rasterplot_compressed(self, neurons_per_group=20, ax=None):
        print 'Working on ' + self.datafile
        spike_dict = dict()
        indices_dict = dict()
        number_of_group = {value: key for (key,value) in SimulationData.group_numbering.items()}

        for group in self.neuron_groups:
            print '   Processing ' + group
            group_sp = self.spikedata[group]
            N = len(group_sp[0])  # = len(group_sp[1])
            if N > 0:
                spike_tuples = [(int(group_sp[0][i]), group_sp[1][i], group) for i in range(N)]
                spikes = pd.DataFrame(spike_tuples)
                spikes.columns = ['neuron_index', 'time', 'group']

                if len(spikes.neuron_index.unique()) > neurons_per_group:
                    indices = np.random.choice(spikes.neuron_index.unique(), neurons_per_group, replace=False)
                    spikes = spikes[spikes.neuron_index.isin(indices)]
                    start_index = (16 - number_of_group[group]) * neurons_per_group + 1
                    fixed_indices = range(start_index, start_index+neurons_per_group+1)
                    fixed_ind_dict = {indices[i]: fixed_indices[i] for i in range(neurons_per_group)}
                    spikes.neuron_index = spikes.neuron_index.map(fixed_ind_dict)

                    spike_dict[group] = spikes
                else:
                    print '   Group ' + group + ' has too few spiking neurons (or sampling was too sparse)! Skipping...'


        spike_df = pd.concat(spike_dict)
        if ax is None:
            plt.scatter(spike_df.time, spike_df.neuron_index, s=0.8)
            q = neurons_per_group
            runtime = self.data['runtime']

            ticklabels = ['VI', 'V', 'IV', 'II/III', 'I']
            plt.yticks([4 * q, 7 * q, 12 * q, 15 * q, 16 * q], ticklabels)
            plt.xticks(np.arange(runtime + 0.1, step=1))
            plt.xlabel('Time (s)')

            plt.xlim([0, runtime])
            plt.ylim([0, 16 * q])

            plt.show()

        else:
            scatplot = ax.scatter(spike_df.time, spike_df.neuron_index, s=0.6, c='gray')
            return scatplot


    def voltage_rasterplot(self, max_per_group=20, dt_downsampling_factor=10):

        divider_height = 1

        tmp_group = self.data['vm_all'].keys()[0]
        t_samples = len(self.data['vm_all'][tmp_group][0])
        samplepoints = np.arange(0, t_samples, dt_downsampling_factor)
        T = len(samplepoints)

        # print 'Experiment duration ' + str(self.defaultclock_dt*t_samples)
        # print 'Experiment sampling rate ' + str(self.defaultclock_dt)
        # print 'Downsampling by a factor of ' + str(dt_downsampling_factor)

        N_groups = len(self.group_numbering)

        group_start_ix = [0]*(N_groups+2)
        yticklocations = [0]*(N_groups+1)

        combined_neurons_vm = []

        # Run through groups to downsample and to select which neurons to show (if too many sampled)
        for i in np.arange(1, N_groups+1):
            group_name = self.group_numbering[i]
            # print 'Processing group ' + group_name + ', start index is ' + str(group_start_ix[i])

            group_neurons_vm = self.data['vm_all'][group_name]
            N_neurons_in_group = len(group_neurons_vm)
            # print '# of neurons sampled is ' + str(N_neurons_in_group)

            if N_neurons_in_group > max_per_group:
                N_neurons_in_group = max_per_group  # Ie. make N_neurons_in_group the amount of neurons to *sample*

            # print '# of neurons to show is ' + str(N_neurons_in_group)
            group_start_ix[i + 1] = group_start_ix[i] + N_neurons_in_group + divider_height
            yticklocations[i] = int((group_start_ix[i+1]-group_start_ix[i])/2 + group_start_ix[i])

            # Time-downsampling
            downsampled_neurons_vm = ['-']*N_neurons_in_group
            for n in range(0,N_neurons_in_group):
                downsampled_neurons_vm[n] = [group_neurons_vm[n][t] for t in samplepoints]

            # Add v_m series of N_neurons_in_group/max_per_group (randomly selected) neurons
            combined_neurons_vm.extend(downsampled_neurons_vm[0:N_neurons_in_group])  # Selection should be randomized

            # After the data, add const series (one or many) as a divider between groups
            divider = [[0] * T for k in range(0, divider_height)]
            combined_neurons_vm.extend(divider)



        # Plot a heatmap
        # Annoying labeling issue: sns.heatmap has indices increasing from top-left, matplotlib from bottom-left
        # That's why label locations are inversed (but not the whole y axis)
        # plt.style.use('seaborn-whitegrid')

        fig = plt.figure()
        fig.suptitle(self.datafile)
        ax = sns.heatmap(combined_neurons_vm, cmap=mycmap, vmin=-0.07, vmax=-0.04)

        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.set_xticklabels([self.defaultclock_dt/ms*dt_downsampling_factor*i for i in range(0,11)])
        ax.set_xlabel('Time (ms)')

        y_limit = ax.get_ylim()[1]
        yticklocs = [y_limit - yticklocations[i] for i in range(1,N_groups+1)]

        ax.yaxis.set_major_locator(plt.FixedLocator(yticklocs))
        ax.yaxis.set_major_formatter(plt.FixedFormatter(self.group_numbering.values()))
        plt.yticks(rotation=0)


        # plt.yticks(yticklocations, self.group_numbering.values(), rotation=0) # TODO Fix tick locations
        #plt.yticks(group_start_ix[1:N_groups + 1], group_start_ix[1:N_groups + 1], rotation=0)


        plt.show()

    # Could be used to obtain all parameters...
    def _get_group_leak(self, group_id):

        physio_config = self.data['Physiology_configuration']
        number_of_rows = len(physio_config['Variable'])

        # Find in self.data['Physiology_configuration'] the line where group_id config starts
        begin_ix = list(physio_config['Variable']).index(self.group_number_to_type[group_id])  # list() so that we can use index()

        # Find where the next group's config starts (or the config file ends)
        end_ix = 0
        try:
            end_ix = (i for i in range(begin_ix+1, number_of_rows)
                      if type(physio_config['Variable'][i]) == str).next()  # Empty rows are floats, non-empty are strings
        except StopIteration:
            end_ix = number_of_rows

        # Take data from lines between those -> dict
        # params = dict()
        # for i in range(begin_ix, end_ix):
        #     params[physio_config['Key'][i]] = physio_config['Value'][i]

        if self.group_number_to_type[group_id] == 'PC':
            gL_index = list(physio_config['Key'][begin_ix:end_ix]).index('gL_soma')
        else:
            gL_index = list(physio_config['Key'][begin_ix:end_ix]).index('gL')

        return eval(physio_config['Value'][begin_ix + gL_index])


    def conductanceplot(self, group_id):

        group = self.group_numbering[group_id]
        # Pick random neuron from group (assuming neuron indexing inside vm_all, ge_soma_all, gi_soma_all is the same
        # ie. that neurons have been sampled with same density for each status monitor)
        neuron_ix = np.random.randint(len(self.data['vm_all'][group]))

        # Deal with time range here

        vm = self.data['vm_all'][group][neuron_ix]
        ge = self.data['ge_soma_all'][group][neuron_ix]
        gi = self.data['gi_soma_all'][group][neuron_ix]
        if self.group_number_to_type[group_id] == 'PC':
            Idendr = self.data['Idendr_soma_all'][group][neuron_ix]
            N_columns = 4
        else:
            N_columns = 3

        runtime = len(vm)*self.defaultclock_dt
        t = np.arange(0, runtime, self.defaultclock_dt)

        # Get spikes for cell HERE
        # spikes_t = self.data['spikes_all'][group][neuron_ix] doesn't work unfortunately
        # self.spikedata[0] -> indices, [1] -> spike times

        # TODO - spikedata have real indices, status monitors don't!!!

        spiking_neuron_ix = self.spikedata[group][0]
        spiking_neuron_t = self.spikedata[group][1]
        spikes_t = []

        for i in range(len(spiking_neuron_ix)):
            if spiking_neuron_ix[i] == neuron_ix: spikes_t.append(spiking_neuron_t[i]*1000*ms)  # Unit in saved data is second

        #C =
        #tau_m =
        gL = self._get_group_leak(group_id)
        Ee = 0*mV
        VT = -45*mV
        EL = -70*mV
        Ei = -75*mV

        ### PLOTTING BEGINS
        plt.subplots(1, N_columns)
        plt.suptitle(self.group_numbering[group_id])

        ### Membrane voltage plot
        plt.subplot(1, N_columns, 1)
        plt.title('$V_m$ with spikes')
        plt.plot(t / ms, vm*pow(10,3), c='blue')
        plt.plot(spikes_t/ms, [0 * mV] * len(spikes_t), '.')
        xlabel('Time (ms)')
        ylabel('$V_m$ (mV)')
        ylim([-75, 20])

        ### Conductance plot
        plt.subplot(1, N_columns, 2)
        plt.title('Conductance')
        plt.plot(t / ms, ge*pow(10,9), label='ge', c='green')
        plt.plot(t / ms, gi*pow(10,9), label='gi', c='red')
        xlabel('Time (ms)')
        ylabel('Conductance (nS)')
        # ylim([0, 50e-9])
        plt.legend()

        if self.group_number_to_type[group_id] == 'PC':
            plt.title('Dendritic current in soma')
            plt.subplot(1, N_columns, 3)
            plt.plot(t/ms, Idendr*pow(10,12), label='Idendr', c='blue')
            xlabel('Time (ms)')
            ylabel('Current (pA)')
            plt.legend()

            plt.subplot(1,N_columns,4)
        else:
            plt.subplot(1,N_columns,3)

        ### ge/gi plot with AP threshold line
        plt.title('Exc vs inh conductance')

        def gi_line(x): return (-x * (Ee - VT) - gL * (EL - VT)) / (Ei - VT)

        x_values = np.arange(0 * nS, 50 * nS, 1 * nS)
        plt.plot(x_values*pow(10,9), [gi_line(x)*pow(10,9) for x in x_values], label='$dV_m/dt = 0$')

        for spike_time in spikes_t/self.defaultclock_dt:
             plt.plot(ge[spike_time]*pow(10,9), gi[spike_time]*pow(10,9), 'g.')

        plt.plot(ge*pow(10,9), gi*pow(10,9), 'y.', alpha=0.02)
        plt.axis('equal')
        plt.xlabel('ge (nS)')
        plt.ylabel('gi (nS)')
        plt.legend()

        plt.show()

    def currentplot(self, group_id):

        group = self.group_numbering[group_id]


        ### Random neuron data
        # Pick random neuron from group (assuming neuron indexing inside vm_all, ge_soma_all, gi_soma_all is the same
        # ie. that neurons have been sampled with same density for each status monitor)
        neuron_ix = np.random.randint(len(self.data['vm_all'][group]))

        vm = self.data['vm_all'][group][neuron_ix]
        ge = self.data['ge_soma_all'][group][neuron_ix]
        gi = self.data['gi_soma_all'][group][neuron_ix]
        if self.group_number_to_type[group_id] == 'PC':
            Idendr = self.data['Idendr_soma_all'][group][neuron_ix]
        else:
            Idendr = [0.0]*len(vm)

        ### Mean of all sampled neurons
        vm_mean = np.mean(self.data['vm_all'][group], axis=0)
        ge_mean = np.mean(self.data['ge_soma_all'][group], axis=0)
        gi_mean = np.mean(self.data['gi_soma_all'][group], axis=0)
        if self.group_number_to_type[group_id] == 'PC':
            Idendr_mean = np.mean(self.data['Idendr_soma_all'][group], axis=0)
        else:
            Idendr_mean = [0.0]*len(vm)


        ### Plotting
        n_samples = len(vm)
        runtime = n_samples * self.defaultclock_dt
        plotting_density = 10
        t = np.arange(0, runtime, self.defaultclock_dt)

        gL = self._get_group_leak(group_id)
        Ee = 0*mV
        VT = -45*mV
        EL = -70*mV
        Ei = -75*mV

        exc_current = [ge[i]*siemens * (Ee-vm[i]*volt)+max(0,Idendr[i])*amp for i in np.arange(0, n_samples, plotting_density)]
        inh_current = [-(gi[i]*siemens * (Ei - vm[i]*volt) + min(0, Idendr[i])*amp) for i in np.arange(0, n_samples, plotting_density)]

        exc_current_mean = [ge_mean[i]*siemens * (Ee-vm_mean[i]*volt)+max(0,Idendr_mean[i])*amp for i in np.arange(0, n_samples, plotting_density)]
        inh_current_mean = [-(gi_mean[i]*siemens * (Ei - vm_mean[i]*volt) + min(0, Idendr_mean[i])*amp) for i in np.arange(0, n_samples, plotting_density)]

        plt.suptitle(self.group_numbering[group_id])
        plt.title('Mean E/I current (trace of E/I of a random neuron)')
        plt.plot(exc_current/pA, inh_current/pA, c='g', alpha=0.1)
        plt.plot(exc_current_mean/pA, inh_current_mean/pA, c='black', lw=1)
        plt.axis('equal')
        plt.xlabel('Excitatory current (pA)')
        plt.ylabel('Inhibitory current (pA)')
        plt.legend()
        plt.show()

    def group_interspikeintervals(self, group_id):
        # Get the group spikes. Remember: [0]->indices, [1]->spike times
        spikes = self.spikedata[self.group_numbering[group_id]]

        # Get indices of the neurons that are spiking
        spiking_neurons = unique(spikes[0])

        # Pick each neuron and go through the times it has spiked
        spikeintervals = dict()
        spiking_neurons_2 = []  # Those with at least 2 spikes
        for neuron in spiking_neurons:
            spike_idx = sort(where(spikes[0] == neuron)[0])

            if len(spike_idx) >= 2:
                spikeintervals[neuron] = []
                spiking_neurons_2.append(neuron)
                # Begin counting from 2nd spike and for each step calculate the duration between jth - (j-1)th spike time
                for j in range(1, len(spike_idx)):
                    interval = (spikes[1][spike_idx[j]] - spikes[1][spike_idx[j-1]]) * 1000  # x1000 s->ms
                    spikeintervals[neuron].append(interval)

        return spikeintervals, spiking_neurons_2

    def group_isi_histogram(self, group_id, ax=None):

        # Collection of spike times for each neuron in the group - let's just flatten it now
        spikeintervals, spiking_neurons = self.group_interspikeintervals(group_id)
        group_spikeintervals = []
        [group_spikeintervals.extend(spikeintervals[neuron]) for neuron in spiking_neurons]

        # Show a histogram of the interspike intervals (ISIs)
        if ax is None:
            plt.hist(group_spikeintervals, bins='auto')
            plt.xlabel('Time (ms)')
            plt.ylabel('Count')
            plt.show()
        else:
            ax.hist(group_spikeintervals, bins=40)

    # TODO - Begin analysis from certain point in time
    def isi_histograms(self):
        fig, ax = plt.subplots(4, 4)
        fig.suptitle(self.datafile)

        for group_id in range(1,16+1):
            plt.subplot(4, 4, group_id)
            plt.title(self.group_numbering[group_id])
            self.group_isi_histogram(group_id, plt.gca() )
            plt.xlabel('ISI (ms)')
            plt.ylabel('Count')

        plt.show()

    # For now, only prints out mean firing rates for each group
    # TODO - Begin analysis from certain point in time
    def mean_firing_rates_by_group(self):

        # Get interspike intervals for all neuron groups and all their neurons
        spikeintervals = dict()
        spiking_neurons = dict()
        for group_id in range(1,16+1):
            spikeintervals[group_id], spiking_neurons[group_id] = self.group_interspikeintervals(group_id)

        # For each neuron group, calculate the mean firing rates of neurons
        firing_rates = dict()
        for group_id in range(1,16+1):
            firing_rates[group_id] = []
            for neuron in spiking_neurons[group_id]:
                # Mean firing rate is spikes/runtime, which is the same as number of interspike intervals +1 / runtime
                # Runtime below is in seconds, so the firing_rate unit is hertz
                firing_rates[group_id].append((len(spikeintervals[group_id][neuron])+1) / self.runtime)



        # Draw horizontally group/line the mean and individual firing rates
        for group_id in range(1, 16+1):
            print self.group_numbering[group_id]
            print nanmean(firing_rates[group_id])


    # Calculation of single-neuron coefficient of variation of interspike intervals, see eg. Sterratt book p209
    def neuron_isi_cv(self, isi_list):
        return std(isi_list)/mean(isi_list)

    # TODO - Begin analysis from certain point in time
    def group_isi_cv(self, group_id):
        spikeintervals, spiking_neurons = self.group_interspikeintervals(group_id)

        neuron_cv_list = []
        for neuron in spiking_neurons:
            neuron_cv = self.neuron_isi_cv(spikeintervals[neuron])
            neuron_cv_list.append(neuron_cv)

        return mean(neuron_cv_list)

    # TODO - Begin analysis from certain point in time
    def isi_cv_all(self):
        for group_id in range(1,16+1):
            print self.group_numbering[group_id] + ', mean of 1-neuron CoV of ISIs (irregularity): ' + str(self.group_isi_cv(group_id))

    def group_spike_count_histogram(self, group_id, bin_size=3*ms, ax=None):

        # Collect spike counts (of the group) into runtime divided by (time-)bin_size many bins
        timebin = bin_size/second
        spikes = self.data['spikes_all'][self.group_numbering[group_id]]
        n_bins = int(self.runtime/timebin)
        spike_counts, bin_edges = np.histogram(spikes[1], bins=n_bins)
        # Spike count divided by bin size could be called the "population firing rate", but we don't really need that here

        # Count how many time-bins with each firing rate/spike count -> spike count histogram
        if ax is None:
            plt.hist(spike_counts, bins='auto')
            plt.xlabel('Spike count')
            plt.ylabel('Frequency (# of timebins)')
            plt.show()
        else:
            ax.hist(spike_counts, bins='auto')

        # Print Fano factors (spike_counts variance/mean) to stdout
        sp_mean = mean(spike_counts)
        sp_var = np.var(spike_counts)
        print self.group_numbering[group_id] + ': mean '+str(sp_mean)+', variance '+str(sp_var)
        print 'Fano factor (population synchrony): '+ str(sp_var/sp_mean)


    def spike_count_histograms(self):
        fig, ax = plt.subplots(4, 4)
        fig.suptitle(self.datafile)

        for group_id in range(1, 16 + 1):
            plt.subplot(4, 4, group_id)
            plt.title(self.group_numbering[group_id])
            self.group_spike_count_histogram(group_id, ax=plt.gca())
            plt.xlabel('Spike count')
            plt.ylabel('Frequency (timebins)')

        plt.show()


    def group_firing_rates(self, group_id, bin_size=3*ms):
        # Collect spike counts (of the group) into runtime divided by (time-)bin_size many bins
        timebin = bin_size/second
        spikes = self.data['spikes_all'][self.group_numbering[group_id]]
        n_bins = int(self.runtime/timebin)
        spike_counts, bin_edges = np.histogram(spikes[1], bins=n_bins)

        # Count instantaneous firing rates in spikes/s
        group_firing_rates = [count/timebin for count in spike_counts]

        return group_firing_rates, bin_edges  # bin_edges is of length len(group_firing_rates)+1


    def layer_firing_rates(self, layer_number):
        flatten = lambda l: [item for sublist in l for item in sublist]
        groups = flatten(self.groups_of_layer[layer_number])

        bin_size = 3*ms
        plt.title('Layer ' + str(layer_number))
        plt.xlabel('Time (s)')
        plt.ylabel('Group firing rate (spikes/s)')
        for group_id in groups:
            firing_rates, bin_edges = self.group_firing_rates(group_id, bin_size)
            plt.plot(bin_edges[:-1], firing_rates, label=self.group_numbering[group_id])

        plt.legend()
        plt.show()

    def layer_ei_firing_rates(self, layer_number, ax=None):
        groups = self.groups_of_layer[layer_number]
        e_groups = groups[0]
        i_groups = groups[1]
        bin_size = 3*ms

        e_firing_rates = [self.group_firing_rates(e_group, bin_size)[0] for e_group in e_groups]
        i_firing_rates = [self.group_firing_rates(i_group, bin_size)[0] for i_group in i_groups]
        bin_edges = self.group_firing_rates(1, bin_size)[1]

        e_rates_sum = np.sum(e_firing_rates, axis=0)
        i_rates_sum = np.sum(i_firing_rates, axis=0)

        if ax is None:
            plt.title('Layer '+ str(layer_number))
            plt.plot(bin_edges[:-1], e_rates_sum, label='Excitatory', c='g')
            plt.plot(bin_edges[:-1], i_rates_sum, label='Inhibitory', c='r')
            plt.xlabel('Time (s)')
            plt.ylabel('Population firing rate (spikes/s)')

            plt.legend()
            plt.show()

        else:
            ax.plot(bin_edges[:-1], e_rates_sum, label='Excitatory', c='g')
            ax.plot(bin_edges[:-1], i_rates_sum, label='Inhibitory', c='r')
            ax.legend()


    def ei_firing_rates(self):
        n_layers = len(self.layers)

        fig, ax = plt.subplots(n_layers, 1)
        fig.suptitle('E/I population firing rates (spikes/s)')

        for i in range(0, n_layers):
            plt.subplot(n_layers, 1, i+1)
            plt.title('Layer '+str(self.layers[i]))
            self.layer_ei_firing_rates(self.layers[i], ax=plt.gca())

        plt.show()


    def layer_ei_plot(self, layer_number):
        groups = self.groups_of_layer[layer_number]
        e_groups = groups[0]
        i_groups = groups[1]
        bin_size = 3*ms  # Refractory time is 3ms so a single neuron can fire only once in time bin

        e_pop_size = np.sum([self.neurons_in_group[e_group] for e_group in e_groups])
        i_pop_size = np.sum([self.neurons_in_group[i_group] for i_group in i_groups])


        e_firing_counts = [self.group_firing_rates(e_group, bin_size)[0]*bin_size for e_group in e_groups]
        i_firing_counts = [self.group_firing_rates(i_group, bin_size)[0]*bin_size for i_group in i_groups]
        bin_edges = self.group_firing_rates(1, bin_size)[1]

        e_counts_sum = np.sum(e_firing_counts, axis=0)
        i_counts_sum = np.sum(i_firing_counts, axis=0)

        e_activity = [100*e_t/e_pop_size for e_t in e_counts_sum]
        i_activity = [100*i_t/i_pop_size for i_t in i_counts_sum]

        plt.plot(e_activity, i_activity, '.')
        plt.xlabel('Excitatory population activity')
        plt.ylabel('Inhibitory population activity')

        # plt.legend()
        plt.show()

### END of class SimulationData

def calciumplot(sim_files, sim_titles, runtime, neurons_per_group=20, suptitle='Effect of increased $Ca^{2+}$ concentration (mM)'):

    sim_n = len(sim_files)
    q = neurons_per_group

    ticklabels = ['VI', 'V', 'IV', 'II/III', 'I']
    w, h = matplotlib.figure.figaspect(1 / sim_n)
    fig, ax = plt.subplots(ncols=sim_n, figsize=(w, h), dpi=600)
    #plt.style.use('seaborn-whitegrid')


    fig.suptitle(suptitle, fontsize=16)
    fig.subplots_adjust(top=0.85, bottom=0.1, left=0.03, right=0.97)
    plt.setp(ax, xticks=np.arange(runtime + 0.1, step=1),
             yticks=[4 * q, 7 * q, 12 * q, 15 * q, 16 * q], yticklabels=ticklabels, xlim=[0, runtime],
             ylim=[0, 16 * q],
             xlabel='Time (s)')

    [SimulationData(sim_files[i]).rasterplot_compressed(40, ax[i]) for i in range(sim_n)]
    [ax[i].set_title(sim_titles[i]) for i in range(sim_n)]

    plt.tight_layout()
    fig.subplots_adjust(top=0.80, bottom=0.20, left=0.03, right=0.97)
    plt.savefig('calciumplot.eps', dpi=600)
    # plt.savefig('calciumplot.png')
    #plt.show()



# MAIN

if __name__ == '__main__':

    # sim = SimulationData('extrinsic_16a_calcium_concentration1.2_Cpp_2000ms.bz2')
    sim = SimulationData('extrinsic_23_calcium_concentration2.0_background_rate_inhibition0.2H_Cpp_2000ms.bz2')
    sim.currentplot(10)
    # sim.layer_ei_plot(5)
    # sim.ei_firing_rates()
    # sim.isi_cv_all()
    # sim.mean_firing_rates_by_group()
    # sim.voltage_rasterplot()
    # sim.ei_firing_rates()

    # sim.layer_firing_rates(4)
    # sim.ei_firing_rates()
    # sim.layer_ei_plot(4)
    # firing_rates, bin_edges = sim.group_firing_rates(7)
    # plt.plot(bin_edges[:-1], firing_rates)
    # firing_rates, bin_edges = sim.group_firing_rates(8)
    # plt.plot(bin_edges[:-1], firing_rates)
    # plt.show()
    # sim.rate_boxplot()
    # sim.isi_cv_all()
    # sim.spike_count_histograms()

    # sim.group_spike_count_histogram(5)
    # sim.isi_cv_all()
    # sim.isi_histograms()
    # sim.rasterplot()
    # sim.rate_boxplot()


    # simulations = ['depol_37_calcium_concentration1.0_Cpp_3000ms.bz2', 'depol_37_calcium_concentration1.4_Cpp_3000ms.bz2',
    #                'depol_37_calcium_concentration2.0_Cpp_3000ms.bz2']
    # sim_title = ['1.0', '1.4', '2.0']
    #
    # calciumplot(sim_files=simulations, sim_titles=sim_title, neurons_per_group=40, runtime=3.0)

    # sim = SimulationData('constudy_02_calcium_concentration2.0_Cpp_1000ms.bz2')
    # sim._get_group_leak(1)
    # for i in range (1,16+1):
    #     print 'Group '+ sim.group_numbering[i]
    #     print sim._get_group_leak(i)
    #sim.rasterplot()

    # sim.conductanceplot(11)



