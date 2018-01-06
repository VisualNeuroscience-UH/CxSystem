"""
Parameter fitting for adaptive exponential integrate-and-fire neurons
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

import numpy as np
import efel
from os import path, getcwd
from brian2 import *


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
                plt.plot(opt_trace['T'], opt_trace['V'], color='grey', linewidth=0.5, linestyle='-')

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
    def __init__(self, passive_params, target_traces=MarkramStepInjectionTraces(), stim_total=3000, stim_start=700, stim_end=2700):
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
        self.feature_names = ['mean_frequency']
        self.target_values = self.target.getTargetValues(self.feature_names)

    def evaluateFitness(self, individual, plot_traces=False):
        """
        Runs model with given parameters and evaluates results with respect to target features

        :param individual: [a, tau_w, b, V_res]
        :return:
        """
        # Better variable names for sake of clarity
        a, tau_w, b, V_res = individual
        neupar = self.adex_passive_params
        n_steps = self.target.n_steps
        current_steps = self.target.current_steps

        # Assign units
        a = a*nS; tau_w = tau_w*ms; b = b*pA; V_res = V_res*mV

        # Make neuron group
        equation_final = Equations(self.equation_soma, C=neupar['C'], gL=neupar['gL'], EL=neupar['EL'],
                                   DeltaT=neupar['DeltaT'], VT=neupar['VT'],
                                   a=a, tau_w=tau_w)
        G = NeuronGroup(n_steps, equation_final, threshold='vm > ' + repr(neupar['Vcut']),
                        reset='vm = ' + repr(V_res) + '; w=w+' + repr(b),
                        refractory=neupar['refr_time'], method='euler')

        M = StateMonitor(G, ('vm'), record=True)

        # Run the step current injections
        G.I_hypol = current_steps[0]*nA
        run(self.stim_start * ms)

        for step in range(1, n_steps):
            G.I_depol[step] = current_steps[step]*nA
        run((self.stim_end-self.stim_start)*ms)

        G.I_depol = 0*nA
        run((self.stim_total-self.stim_end) * ms)

        # Extract voltage traces
        times = M.t/ms
        voltages = [M.vm[step]/mV for step in range(n_steps)]

        optimizable_traces = []
        for step_number in range(1, n_steps):

            trace = {}
            trace['T'] = times
            trace['V'] = voltages[step_number]
            trace['stim_start'] = [self.stim_start]
            trace['stim_end'] = [self.stim_end]
            trace['step_current'] = [current_steps[step_number]]
            trace['hyperpolarization'] = [current_steps[0]]
            optimizable_traces.append(trace)

        # Compute fitness
        print 'Target values: '
        print str(self.target_values)

        print 'Current values: '
        feature_values = efel.getFeatureValues(optimizable_traces, self.feature_names)
        print str(feature_values)

        # Plot traces
        if plot_traces == True:
            self.target.plotTraces(optimizable_traces)

# Def: Fitness/cost function; optimizes a,b,w,V_res

if __name__ == '__main__':
    current_steps = [-0.037109, 0.1291404, 0.1399021, 0.1506638]
    test_target = MarkramStepInjectionTraces('L5_MC_bAC217_1/hoc_recordings/', 'soma_voltage_step', current_steps)
    # test_target.plot_traces()

    MC_passive_params = {'C': 92.1*pF, 'gL': 4.2*nS, 'VT': -42.29*mV, 'DeltaT': 2*mV,
                         'Vcut': 20*mV, 'EL': -60.38*mV, 'refr_time': 4*ms}
    test_neuron = AdexOptimizable(MC_passive_params, test_target)
    test_neuron.evaluateFitness([2, 300, 50, -55], plot_traces=True)