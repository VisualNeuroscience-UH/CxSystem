"""
Fitness evaluation for adaptive exponential integrate-and-fire neurons
using traces from simulated BBP neurons
by Henri Hokkanen <henri.hokkanen@helsinki.fi>, January 2018

Neuron models from
1) https://bbp.epfl.ch/nmc-portal/downloads

Implementation inspired by
2) https://github.com/BlueBrain/eFEL/blob/master/examples/nmc-portal/L5TTPC2.ipynb
3) http://efel.readthedocs.io/en/latest/deap_optimisation.html
4) Naud et al. 2008

For generating step injection traces
  - download neuron model from (1)
  - follow instructions in (2) on how to run the model
"""

from __future__ import division
from brian2 import *
import numpy as np
import matplotlib.pyplot as plt
from os import path, getcwd
import efel
prefs.codegen.target = 'numpy'


class MarkramStepInjectionTraces(object):
    """
    Extracts data from step current injection traces
    """

    def __init__(self, traces_directory='', traces_file_prefix='', current_steps=[], stim_total=3000, stim_start=700, stim_end=2700):
        times = []
        voltages = []
        traces_file_suffix = '.dat'
        traces_file_pointer = path.join(getcwd(), traces_directory) + '/' + traces_file_prefix
        self.n_steps = len(current_steps)

        # Read the data from files and insert into eFel-compatible dictionary
        self.traces = []
        for step_number in range(1, self.n_steps):
            data = np.loadtxt(traces_file_pointer + str(step_number) + traces_file_suffix)
            times.append(data[:, 0])
            voltages.append(data[:, 1])

            trace = {}
            trace['T'] = times[step_number-1]
            trace['V'] = voltages[step_number-1]
            trace['stim_start'] = [stim_start]
            trace['stim_end'] = [stim_end]
            trace['step_current'] = [current_steps[step_number]]
            trace['hyperpolarization'] = [current_steps[0]]
            self.traces.append(trace)

        self.current_steps = current_steps
        self.stim_total = stim_total

    def plotTraces(self, optimizable_traces=None):
        n_traces = self.n_steps - 1
        try:
            opt_traces_iter = iter(optimizable_traces)
        except TypeError:
            opt_traces_iter = None

        plt.subplots(1, n_traces)

        i=1
        for target_trace in self.traces:
            plt.subplot(1, n_traces, i)
            plt.plot(target_trace['T'], target_trace['V'], color='black', linewidth=1, linestyle='-')
            if opt_traces_iter is not None:
                opt_trace = opt_traces_iter.next()
                plt.plot(opt_trace['T'], opt_trace['V'], color='red', linewidth=0.5, linestyle='-')

            plt.xlim([0, self.stim_total])
            plt.title(str(target_trace['step_current'][0]) + ' nA')
            i += 1

        plt.show()

    def getTargetValues(self, feature_list):
        feature_values = efel.getFeatureValues(self.traces, feature_list)
        return feature_values


class AdexOptimizable(object):
    """
    Runs experiments on an AdEx neuron & evaluates fitness
    """
    def __init__(self, passive_params, target_traces=MarkramStepInjectionTraces(), feature_names=None, stim_total=3000, stim_start=700, stim_end=2700):
        self.adex_passive_params = passive_params
        self.target = target_traces

        self.stim_total = stim_total
        self.stim_start = stim_start
        self.stim_end = stim_end

        self.equation_soma = '''
        dvm/dt = (gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) -w + I_hypol + I_depol) / C : volt (unless refractory)
        dw/dt = (-a*(EL-vm)-w)/tau_w : amp
        I_depol : amp
        I_hypol : amp
        '''

        # Objectives: number of spikes, first spike latency, first ISI, last ISI (...) => squared error
        # For possible features: efel.api.getFeatureNames()
        if feature_names is None:
            self.feature_names = ['Spikecount_stimint', 'inv_time_to_first_spike', 'inv_first_ISI',
                                  'inv_last_ISI']
        else:
            self.feature_names = feature_names

        self.target_values = self.target.getTargetValues(self.feature_names)

    def _listMean(self, val):
        """
        Handling of possible lists from feature extraction

        :param val:
        :return:
        """
        if val is None:
            return 0
        else:
            try:
                return float(val)
            except:
                if len(val) > 0:
                    return mean(val)
                else:
                    return 0

    def _listFirst(self, val):
        """
        Handling of possible lists from feature extraction

        :param val:
        :return:
        """

        if val is None:
            return 0
        else:
            try:
                return float(val)
            except:
                if len(val) > 0:
                    return float(val[0])
                else:
                    return 0


    def evaluateFitness(self, individual, plot_traces=False, test_feature_extraction=False, verbose=False):
        """
        Runs model with given parameters and evaluates results with respect to target features

        :param individual: [a, tau_w, b, V_res] in units nS, ms, pA, mV, respectively
        :return: list of errors, length depending number of extracted features
        """
        if verbose is True:
            print 'Current AdEx params (a, tau_w, b, V_res): ' + str(individual)

        # PREPARE FOR RUNNING CURRENT INJECTIONS
        # Better variable names for sake of clarity
        neupar = self.adex_passive_params
        if len(individual) == 4:
            a, tau_w, b, V_res = individual
        else:
            a, tau_w, b, V_res, VT, DeltaT = individual
            neupar['VT'] = VT*mV
            neupar['DeltaT'] = DeltaT*mV

        n_steps = self.target.n_steps
        current_steps = self.target.current_steps

        # Assign units to raw numbers
        a = a*nS; tau_w = tau_w*ms; b = b*pA; V_res = V_res*mV

        # Make neuron group
        equation_final = Equations(self.equation_soma, C=neupar['C'], gL=neupar['gL'], EL=neupar['EL'],
                                   DeltaT=neupar['DeltaT'], VT=neupar['VT'],
                                   a=a, tau_w=tau_w)
        G = NeuronGroup(n_steps, equation_final, threshold='vm > ' + repr(neupar['Vcut']),
                        reset='vm = ' + repr(V_res) + '; w=w+' + repr(b),
                        refractory=neupar['refr_time'], method='euler')

        G.vm = neupar['EL']  # NB! eFel will fail without this line (for unknown reasons)
        M = StateMonitor(G, ('vm'), record=True)

        # RUN THE CURRENT INJECTIONS
        G.I_hypol = current_steps[0] * nA
        run(self.stim_start * ms)

        for step in range(1, n_steps):
            G.I_depol[step] = current_steps[step] * nA
        run((self.stim_end-self.stim_start) * ms)

        G.I_depol = 0*nA
        run((self.stim_total-self.stim_end) * ms)

        # Extract voltage traces
        optimizable_traces = []
        traces = []
        for step_number in range(1, n_steps):

            trace = {}
            trace['T'] = M.t/ms
            trace['V'] = M.vm[step_number]/mV
            trace['stim_start'] = [self.stim_start]
            trace['stim_end'] = [self.stim_end]
            trace['step_current'] = [current_steps[step_number]]
            trace['hyperpolarization'] = [current_steps[0]]
            optimizable_traces.append(trace)

        # Test if eFel feature extraction is working correctly
        # if test_feature_extraction is True:
        #     test_feature_values = efel.getFeatureValues(optimizable_traces, ['peak_time', 'AP_height'])
        #
        #     plt.subplots(1, n_steps-1)
        #     for step_number in range(1, n_steps):
        #         peak_times = test_feature_values[step_number-1]['peak_time']
        #         ap_heights = test_feature_values[step_number-1]['AP_height']
        #
        #         plt.subplot(1, n_steps-1, step_number)
        #         plt.plot(optimizable_traces[step_number-1]['T'], optimizable_traces[step_number-1]['V'])
        #         plt.plot(peak_times, ap_heights, 'o')
        #
        #     plt.show()

        # COMPUTE "FITNESS"
        # raise_warning disabled to allow processing of non-spiking configs
        individual_values = efel.getFeatureValues(optimizable_traces, self.feature_names, raise_warnings=False)

        # Preprocess value lists (take first value or mean; change with handleList)
        handle_list = lambda v: self._listFirst(v)
        for step in range(0, n_steps - 1):
            individual_values[step] = {k: handle_list(v) for k, v in individual_values[step].items()}
            self.target_values[step] = {k: handle_list(v) for k, v in self.target_values[step].items()}

        # Calculate errors in extracted features by averaging over all current steps
        feature_errors=[]
        for feature in self.feature_names:
            abs_errors = [abs(individual_values[i][feature] - self.target_values[i][feature]) for i in range(0, n_steps - 1)]
            avg_errors = mean(abs_errors)
            feature_errors.append(avg_errors)
            if verbose is True:
                print '---'
                print feature + ' current: ' + str([individual_values[i][feature] for i in range(0, n_steps-1)])
                print feature + ' target:  ' + str([self.target_values[i][feature] for i in range(0, n_steps - 1)])
                print feature + ' diff:    ' + str(abs_errors)


        # PLOT TRACES (if requested)
        if plot_traces is True:
            self.target.plotTraces(optimizable_traces)

        if verbose is True:
            print 'Mean errors:'
            print self.feature_names
            print feature_errors

        return feature_errors


if __name__ == '__main__':
    # Example use of classes
    current_steps = [-0.037109, 0.1291404, 0.1399021, 0.1506638]
    test_target = MarkramStepInjectionTraces('L5_MC_bAC217_1/hoc_recordings/', 'soma_voltage_step', current_steps)

    # MC_params_Heikkinen = {'C': 92.1*pF, 'gL': 4.2*nS, 'VT': -42.29*mV, 'DeltaT': 4*mV,
    #                        'Vcut': 20*mV, 'EL': -60.38*mV, 'refr_time': 4*ms}

    MC_params_Markram = {'C': 66.9*pF, 'gL': 3.04*nS, 'VT': -59*mV, 'DeltaT': 4*mV,
                         'Vcut': 20*mV, 'EL': -72.3*mV, 'refr_time': 4*ms}

    test_neuron = AdexOptimizable(MC_params_Markram, test_target,
                                  ['Spikecount_stimint', 'inv_time_to_first_spike', 'inv_first_ISI',
                                   'inv_last_ISI', 'AHP_depth_abs', 'AP_duration'])

    # Visualization of optimized parameters (after 100 generations); Heikkinen params
    # init_guess = [0.7199995715982088, 153.18939361105447, 62.88915388914671, -45.405472248324564]

    # Visualization of optimized parameters (after 100 generations); Markram params
    init_guess = [2.2278445002270919, 162.43372483712233, 23.861384306019414, -58.235779695550065, -58.877534049585194, 3.2588649046444811]

    test_neuron.evaluateFitness(init_guess, plot_traces=True, verbose=True)

