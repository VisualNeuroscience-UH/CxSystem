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

    def __init__(self, traces_directory='', traces_file_prefix='', current_steps=[], stim_start=500, stim_end=2500):
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
            trace['T'] = times[step_number]
            trace['V'] = voltages[step_number]
            trace['stim_start'] = [stim_start]
            trace['stim_end'] = [stim_end]
            trace['step_current'] = current_steps[step_number]
            trace['hyperpolarization'] = current_steps[0]
            self.traces.append(trace)

        # Extract needed features
        # Objectives: number of spikes, first spike latency, first ISI, last ISI (...) => squared error
        self.traces_features = efel.getFeatureValues(self.traces,
                                                     ['spikecount_stimint', 'time_to_first_spike', 'inv_first_ISI',
                                                      'inv_last_ISI'])
        self.current_steps = current_stepss



class AdexNeuron(object):

    def __init__(self, target_traces=MarkramStepInjectionTraces(), stim_total=3000, stim_start=500, stim_end=2500):
        self.target = target_traces

        self.stim_total = stim_total
        self.stim_start = stim_start
        self.stim_end = stim_end

        self.equation_soma = '''
        dvm/dt = (gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) -w + I) / C : volt (unless refractory)
        dw/dt = (-a*(EL-vm)-w)/tau_w : amp
        I : amp
        '''

    def evaluateModel(self, individual):
        """
        Runs model with given parameters and evaluates results with respect to target features

        :param individual: [a, tau_w, b, V_res]
        :return:
        """
        # Better variable names for sake of clarity
        a, tau_w, b, V_res = individual
        n_steps = self.target.n_steps
        current_steps = self.target.current_steps

        # Make neuron group
        G = NeuronGroup(n_steps, self.equation_soma, threshold='vm > ' + repr(Vcut),
                        reset='vm = ' + repr(V_res) + '; w=w+' + repr(b),
                        refractory=refr_time, method='euler')

        M = StateMonitor(G, ('vm'), record=True)

        # Run the step current injections
        G.I = current_steps[0]
        run(self.stim_start * ms)

        for step in range(1, n_steps):
            G.I[step] = current_steps[step]
        run((self.stim_end-self.stim_start)*ms)

        G.I = current_steps[0]
        run((self.stim_total-self.stim_end) * ms)

        # Extract voltage traces

        # Compute fitness

# Class OptimizationTarget: extracts data from STEP CURRENT INJECTIONS of Markram neurons


# Def: Fitness/cost function; optimizes a,b,w,V_res

if __name__ == '__main__':
