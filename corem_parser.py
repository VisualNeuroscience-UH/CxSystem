'''
The program is distributed under the terms of the GNU General Public License
Copyright 2017 Vafa Andalibi, Simo Vanni, Henri Hokkanen.
'''

import pandas as pd
import numpy as np
import sys,os,time
import matplotlib.pyplot as plt
import scipy.io as spio
import re
from string import Template
import cPickle as pickle
import bz2
from brian2 import *  # Load brian2 last for unit-handling to work properly in Numpy


class Corem_retina(object):
    '''
    Class for running a COREM retina model and accessing results after simulation
    '''

    # Global constants
    COREM_ROOT_DIR = '/home/shohokka/PycharmProjects/COREM/COREM/'
    COREM_RESULTS_DIR = 'results/'  # directory relative to ROOT_DIR
    COREM_RETINA_SCRIPTS_DIR = 'Retina_scripts/'  # directory relative to ROOT_DIR
    SUFFIX_BUILT_FROM_TEMPLATE = '_runme'

    CXSYSTEM_INPUT_DIR = '/home/shohokka/PycharmProjects/CXSystem_Git/video_input_files/'

    def __init__(self, retina_script_filename=None, result_ids=[], results_unit=1, script_is_template=False, custom_results_dir=None, retina_timestep=1*ms):
        '''

        :param retina_script_filename: str, file in COREM_RETINA_SCRIPTS_DIR to run
        :param retina_timestep: x*ms, timestep of COREM simulation (default 1*ms)
        '''

        if script_is_template is False:
            print 'Loaded a retina with all parameters in the script. Just simulate_retina() to get results.'
            self.retina_script_filename = retina_script_filename
        else:
            self.retina_script_filename = ''
            self.retina_script_template_filename = retina_script_filename
            self.template_file_location = self.COREM_ROOT_DIR + self.COREM_RETINA_SCRIPTS_DIR + self.retina_script_template_filename
            self.template_param_keys = self._which_parameters()
            print 'Loaded a template retina. Please set_parameters() before you simulate_retina().'
            print 'The parameters you need to give are:'
            print self.template_param_keys

        self.result_ids = result_ids
        self.results_unit = results_unit
        self.custom_results_dir = custom_results_dir
        self.retina_timestep = retina_timestep
        self.results_data = dict()

    def _which_parameters(self):

        fi = open(self.template_file_location, 'r')
        self.template_script = fi.read()
        fi.close()
        param_keys = re.findall('\$\w*', self.template_script)
        param_keys = [key.lstrip('$') for key in param_keys]
        return list(set(param_keys))

    def set_parameters(self, param_keys_and_values):
        '''
        Replace parameter names in a retina template script with corresponding values.

        :param keys_and_values: dict
        :return:
        '''

        template_script = Template(self.template_script)
        runnable_script = template_script.substitute(param_keys_and_values)

        template_script_basename = os.path.basename(self.retina_script_template_filename)
        template_script_basename = os.path.splitext(template_script_basename)[0]
        runnable_script_filename = template_script_basename + self.SUFFIX_BUILT_FROM_TEMPLATE + '.py'
        runnable_file_location = self.COREM_ROOT_DIR + self.COREM_RETINA_SCRIPTS_DIR + runnable_script_filename
        fi = open(runnable_file_location, 'w')
        fi.write(runnable_script)
        fi.close()
        self.retina_script_filename = runnable_script_filename

        print 'Retina template parameters set. Retina ready for simulate_retina().'

    def simulate_retina(self):
        '''
        Run the retina script.
        Note that this always deletes any previous data in the results directory (COREM default behavior).

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


    def _get_timedarray(self, id):
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
        corem_ge_on = self._get_timedarray('P_ganglion_L_ON_')
        model_eq_on = Equations(model_eq, ge='corem_ge_on(t,i)')

        gc_on = NeuronGroup(number_cells, model=model_eq_on, namespace=gc_params,
                            threshold='vm > '+repr(gc_params['V_th']), reset='vm = '+repr(gc_params['V_reset']),
                            refractory=gc_params['t_ref'], method='euler')

        # Create OFF ganglion cells and
        # connect them to corresponding COREM nodes
        corem_ge_off = self._get_timedarray('P_ganglion_L_OFF_')
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
        plt.xlim([0, runtime/ms])
        plt.legend()

        plt.show()


    def example_run_parafoveal(self):
        '''
        An attempt at integrating COREM to CxSystem and at simulating parafoveal retina of macaque monkey.

        :return:
        '''
        ### Runtime parameters
        r = 5  # eccentricity 5 degrees (nasal in visual field)
        cone_density = 1000  # per degree^2, depends on r (here taken from Wassle et al 1990)
        runtime = 900*ms

        w_cones = 10  # width of visual field of interest
        h_cones = 10  # height of visual field of interest

        # Parameters for Schwartz's retinocortical mapping
        k = 17
        a = 1

        ### User-defined parameters end here

        # We want even numbers
        if w_cones % 2 == 1:
            w_cones -= 1
        if h_cones % 2 == 1:
            h_cones -= 1

        ### Create ganglion cell mosaic -> "z coordinates" in CxSystem

        # Assuming hexagonal lattice with horizontal rows and assuming 1:2 cone:PC ganglion cell ratio (ON and OFF)
        grid_center = 5+0j  # in complex coordinates z=x+yj, x>0 and y representing location on retina in degrees
        ganglion_spacing_adjacent = sqrt(2 / (sqrt(3) * cone_density))
        ganglion_spacing_rows = sqrt(sqrt(3) / (2 * cone_density))

        w_range = np.arange(-w_cones/2, w_cones/2 + 1) * ganglion_spacing_adjacent
        h_range = np.arange(-h_cones / 2, h_cones / 2 + 1) * ganglion_spacing_rows
        h_range = np.flipud(h_range)  # Vertical range needs to run in up->down direction

        # Generate ON ganglion cell coordinates
        z_coord_on = []
        row_counter = 0
        for y in h_range:
            row_counter += 1
            for x in w_range:
                z = grid_center + complex(x,y)
                if row_counter % 2 == 0:
                    z -= complex(ganglion_spacing_adjacent/2)  # Shift every other row to have a hexagonal lattice

                z_coord_on.append(z)

        z_coord_on = np.array(z_coord_on)

        # Generate OFF ganglion cell coordinates
        z_coord_off = [z+np.random.rand()*ganglion_spacing_adjacent/3 for z in z_coord_on]
        z_coord_off = np.array(z_coord_off)

        ### Map mosaic to cortical coordinates -> "w coordinates" in CxSystem
        cortical_map = lambda z: k * log(z + a)  # Schwartz's retina->cortex mapping
        w_coord_on = cortical_map(z_coord_on)
        w_coord_off = cortical_map(z_coord_off)

        ### Combine & save positions
        output_dict = dict()

        z_coord = np.concatenate([z_coord_on, z_coord_off])
        output_dict['z_coord'] = z_coord

        w_coord = np.concatenate([w_coord_on, w_coord_off])
        output_dict['w_coord'] = w_coord

        # For saving as MATLAB files, add the following lines:

        # output_dict['z_coord'] = [[z] for z in z_coord]  # silly but otherwise load-/savemat produces bad indexing
        # output_dict['w_coord'] = [[w] for w in w_coord]
        # spio.savemat(self.CXSYSTEM_INPUT_DIR + 'corem_test.mat', output_dict)


        ### Simulate ganglion cells (this could go inside a separate method later)

        number_cells = w_cones * h_cones

        # PC ganglion cell parameters
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

        # Create ON ganglion cells and connect them to corresponding COREM nodes
        corem_ge_on = self._get_timedarray('P_ganglion_L_ON_')
        model_eq_on = Equations(model_eq, ge='corem_ge_on(t,i)')

        gc_on = NeuronGroup(number_cells, model=model_eq_on, namespace=gc_params,
                            threshold='vm > '+repr(gc_params['V_th']), reset='vm = '+repr(gc_params['V_reset']),
                            refractory=gc_params['t_ref'], method='euler')

        # Create OFF ganglion cells and connect them to corresponding COREM nodes
        corem_ge_off = self._get_timedarray('P_ganglion_L_OFF_')
        model_eq_off = Equations(model_eq, ge='corem_ge_off(t,i)')

        gc_off = NeuronGroup(number_cells, model=model_eq_off, namespace=gc_params,
                            threshold='vm > ' + repr(gc_params['V_th']), reset='vm = ' + repr(gc_params['V_reset']),
                            refractory=gc_params['t_ref'], method='euler')

        # Spike detectors
        spikes_on = SpikeMonitor(gc_on)
        spikes_off = SpikeMonitor(gc_off)

        # Run simulation
        print 'Generating ganglion cell spike data'
        run(runtime)

        # CxSystem (CxSystem.py->method relay->submethod spikes) loads given spike/input file and
        # expects spike data inside two arrays:
        # SPK_GENERATOR_SP = spikes_data['spikes_0'][0] - index of neuron
        # SPK_GENERATOR_TI = spikes_data['spikes_0'][1] - time of spike

        plt.scatter(spikes_on.t/ms, spikes_on.i, s=0.4, color='green', label='ON ganglion')
        plt.scatter(spikes_off.t/ms, spikes_off.i+number_cells, s=0.4, color='red', label='OFF ganglion')

        output_dict['spikes_0'] = []
        output_dict['spikes_0'].append(list(spikes_on.i))
        output_dict['spikes_0'][0].extend([i+number_cells for i in spikes_off.i])
        output_dict['spikes_0'].append(list(spikes_on.t))  # Needs to have unit (CxS bug)
        output_dict['spikes_0'][1].extend(list(spikes_off.t))

        # Vafa's savedata
        save_path = self.CXSYSTEM_INPUT_DIR + 'parafov_output.bz2'
        with bz2.BZ2File(save_path, 'wb') as fb:
            pickle.dump(output_dict, fb, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':

    #ret = Corem_retina('parvocustom.py', ['P_ganglion_L_ON_', 'P_ganglion_L_OFF_'], nsiemens)
    #ret.example_run_primate_model()

    ret = Corem_retina('parafoveal_parvo.py', ['P_ganglion_L_ON_', 'P_ganglion_L_OFF_'], nsiemens, script_is_template=True)
    retina_params = {'SIM_TIME': 1200, 'REC_START_TIME': 100, 'PX_PER_DEG': 10, 'RF_CENTER_SIGMA': 0.03,
                     'CONE_H1_SIGMA': 0.5, 'RF_SURROUND_SIGMA': 0.5, 'SHOW_SIM': 'False'}

    retina_params['INPUT_LINE'] = "retina.Input('grating',{'type','0','step','0.001','length1','0.0','length2','4.0','length3','0.0','sizeX','20','sizeY','20','freq','2.5','period','20.0','Lum','100.0','Contr','0.5','phi_s','0.0','phi_t','0.0','orientation','0.0','red_weight','1.0','green_weight','1.0','blue_weight','1.0','red_phase','0.0','green_phase','0.0','blue_phase','0.0'})"

    ret.set_parameters(retina_params)
    ret.simulate_retina()

    ret.example_run_parafoveal()

    print 'Done.'