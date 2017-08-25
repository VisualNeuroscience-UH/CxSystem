'''
The program is distributed under the terms of the GNU General Public License
Copyright 2017 Vafa Andalibi, Simo Vanni, Henri Hokkanen.
'''

import pandas as pd
import numpy as np
import sys,os,time
import matplotlib.pyplot as plt
from brian2 import *  # Load brian2 last for unit-handling to work properly in Numpy


class Corem_retina(object):
    '''
    Class for running a COREM retina model and accessing results after simulation
    '''

    # Global constants
    COREM_ROOT_DIR = '/home/shohokka/PycharmProjects/COREM/COREM/'
    COREM_RESULTS_DIR = 'results/'
    COREM_RETINA_SCRIPTS_DIR = 'Retina_scripts/'

    def __init__(self, retina_script_filename=None, result_ids=[], results_unit=1, custom_results_dir=None, retina_timestep=1*ms):
        '''

        :param retina_script_filename: str, file in COREM_RETINA_SCRIPTS_DIR to run
        :param retina_timestep: x*ms, timestep of COREM simulation (default 1*ms)
        '''

        self.retina_script_filename = retina_script_filename
        self.result_ids = result_ids
        self.results_unit = results_unit
        self.custom_results_dir = custom_results_dir
        self.retina_timestep = retina_timestep
        self.results_data = dict()

    def simulate_retina(self):
        '''
        Run the retina script.
        Note that this always deletes any previous data in the results directory.

        :return: True if script could be run, otherwise False
        '''

        print 'Running retina simulation %s' % self.retina_script_filename
        original_run_path = os.path.abspath(os.path.curdir)
        os.chdir(self.COREM_ROOT_DIR)
        call = './corem ' + self.COREM_RETINA_SCRIPTS_DIR + self.retina_script_filename
        try:
            os.system(call)
        except:
            return False
        os.chdir(original_run_path)
        return True

    def read_results(self):
        '''
        Read data from the COREM results folder into a dict of TimedArrays

        :return: dict of arrays containing TimedArrays, indexed by result IDs -> cell number -> time
        '''

        if self.custom_results_dir is None:
            results_dir = self.COREM_ROOT_DIR+self.COREM_RESULTS_DIR
        else:
            results_dir = self.custom_results_dir

        print 'Reading retina simulation results from %s' % results_dir

        results_dict = dict()

        for id in self.result_ids:
            simulation_files = [sim_file for sim_file in os.listdir(results_dir) if id in sim_file]
            simulation_files.sort()  # Sort in ascending order, eg. Ganglion_ON_0, 1, ..., Ganglion_ON_1000
            print '%s simulated on %s' % (id, time.ctime(os.path.getmtime(results_dir+simulation_files[0])))

            n_sim_files = len(simulation_files)
            results_dict[id] = []

            # Go through all simulation results (for the id in question)
            for i in range(0, n_sim_files):
                try:
                    sim_file_data = np.loadtxt(results_dir+simulation_files[i]).astype(float64)
                    #sim_file_data = TimedArray(sim_file_data, dt=self.retina_timestep)  # Make a Brian2 TimedArray
                    results_dict[id].append(sim_file_data)
                except:
                    print 'Error reading retina simulation results!'
                    return False

            a = results_dict[id]
            b = transpose(a)
            c = b * self.results_unit
            self.results_data[id] = TimedArray(c, dt=self.retina_timestep)


    def get_timedarray(self, id):
        if len(self.results_data) == 0:
            self.read_results()
        else:
            pass

        return self.results_data[id]

    def example_run_primate_model(self):
        '''
        Brian2 adaptation of COREM's example_run_primate_model.py which uses NEST.
        The NEST-based model is a simplified version of the model proposed in (*) with simplified
        photoreceptors, no amacrine cells and no synaptic connectivity between retinal cells.
        This is an adaptation of the _simplified_ version.

        (*) Martinez-Canada, P., Morillas, C., Pelayo, F. (2017) A Conductance-Based
        Neuronal Network Model for Color Coding in the Primate Foveal Retina. In IWINAC 2017.

        :return:
        '''

        number_cells = 25*25

        # Midget aka P ganglion cell parameters
        # retina_parvo_ganglion_cell_params = {
        gc_params = {
            "C_m": 100.0*pF,
            "g_L": 10.0*nS,
            "E_ex": 0.0*mV,
            "E_in": -70.0*mV,
            "E_L": -60.0*mV,
            "V_th": -55.0*mV,
            "V_reset": -60.0*mV,
            "t_ref": 2.0*ms,
            "rate": 0.0*Hz,         # not used
            "tau_e": 3.0*ms,        # not used
            "tau_i": 8.3*ms,        # not used
            "tonic_current": 0*pA,
            "noise": 0.1*mV,
            "gi": 0*nS
        }

        gc_params['tau_m'] = gc_params['C_m'] / gc_params['g_L']

        model_eq = 'dvm/dt = (((g_L*(E_L-vm) + ge*(E_ex-vm) + gi*(E_in-vm)) + tonic_current) / C_m) + noise*xi*tau_m**-0.5: volt'

        # Create ON ganglion cells and
        # connect them to corresponding COREM nodes
        corem_ge_on = self.get_timedarray('P_ganglion_L_ON_')
        model_eq_on = Equations(model_eq, ge='corem_ge_on(t,i)')

        gc_on = NeuronGroup(number_cells, model=model_eq_on, namespace=gc_params,
                            threshold='vm > '+repr(gc_params['V_th']), reset='vm = '+repr(gc_params['V_reset']),
                            refractory=gc_params['t_ref'], method='euler')

        # Create OFF ganglion cells and
        # connect them to corresponding COREM nodes
        corem_ge_off = self.get_timedarray('P_ganglion_L_OFF_')
        model_eq_off = Equations(model_eq, ge='corem_ge_off(t,i)')

        gc_off = NeuronGroup(number_cells, model=model_eq_off, namespace=gc_params,
                            threshold='vm > ' + repr(gc_params['V_th']), reset='vm = ' + repr(gc_params['V_reset']),
                            refractory=gc_params['t_ref'], method='euler')

        # Spike detectors
        spikes_on = SpikeMonitor(gc_on)
        spikes_off = SpikeMonitor(gc_off)

        # Run simulation
        runtime = 1300*ms
        run(runtime)

        # Visualization
        plt.figure()

        plt.title('Spikes')
        plt.scatter(spikes_on.t/ms, spikes_on.i, s=0.4, color='green', label='ON ganglion')
        plt.scatter(spikes_off.t/ms, spikes_off.i+number_cells, s=0.4, color='red', label='OFF ganglion')
        plt.xlim([0,runtime/ms])
        plt.legend()

        plt.show()


if __name__ == '__main__':

    ret = Corem_retina('parvocustom.py', ['P_ganglion_L_ON_', 'P_ganglion_L_OFF_'], nsiemens)

    #ret.simulate_retina()
    ret.example_run_primate_model()

    #ret.read_results()

    # ta = ret.get_timedarray('P_ganglion_L_ON_')
    # plt.figure()
    # plt.plot(ta(linspace(1,1200,1200)*ms, 4))
    # plt.show()
    print 'Done.'