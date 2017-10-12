'''
The program is distributed under the terms of the GNU General Public License
Copyright 2017 Vafa Andalibi, Simo Vanni, Henri Hokkanen.
'''

from __future__ import division
import pandas as pd
import numpy as np
import sys,os,time
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.collections import PatchCollection
import scipy.io as spio
import re
from string import Template
import cPickle as pickle
import bz2
from brian2 import *  # Load brian2 last for unit-handling to work properly in Numpy


# Global constants
# DIR: absolute directory reference, RELDIR: relative directory reference
COREM_ROOT_DIR = '/home/shohokka/PycharmProjects/COREM/COREM/'
COREM_RESULTS_RELDIR = 'results/'  # directory relative to ROOT_DIR
COREM_RETINA_SCRIPTS_DIR = 'Retina_scripts/'  # directory relative to ROOT_DIR
SUFFIX_BUILT_FROM_TEMPLATE = '_runme'
CXSYSTEM_INPUT_DIR = '/home/shohokka/PycharmProjects/CXSystem_Git/video_input_files/'


class CoremRetina(object):
    '''
    Class for running a COREM retina model and accessing results after simulation
    '''


    def __init__(self, retina_script_filename=None, pixels_per_degree=100, result_ids=[], results_unit=1, script_is_template=False, custom_results_dir=None, retina_timestep=1*ms):
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
            self.template_file_location = COREM_ROOT_DIR + COREM_RETINA_SCRIPTS_DIR + self.retina_script_template_filename
            self.template_param_keys = self._which_parameters()
            print 'Loaded a template retina. Please prepare_template() before you simulate_retina().'
            print 'The parameters you need to give are:'
            print self.template_param_keys

        self.script_is_template = script_is_template
        self.pixels_per_degree = pixels_per_degree
        self.result_ids = result_ids
        self.results_unit = results_unit
        self.custom_results_dir = custom_results_dir
        self.retina_timestep = retina_timestep
        self.results_data = dict()
        self.input_line = "retina.Input('impulse', {'start','100.0','stop','500.0','amplitude','1800.0','offset','100.0','sizeX','20','sizeY','20'})"

    def _which_parameters(self):

        fi = open(self.template_file_location, 'r')
        self.template_script = fi.read()
        fi.close()
        param_keys = re.findall('\$\w*', self.template_script)
        param_keys = [key.lstrip('$') for key in param_keys]
        return list(set(param_keys))

    def _prepare_template(self, param_keys_and_values):
        '''
        Replace parameter names in a retina template script with corresponding values.

        :param keys_and_values: dict
        :return:
        '''

        # If not INPUT_LINE is given, we expect a method has been used to define it
        if 'INPUT_LINE' not in param_keys_and_values.keys():
            param_keys_and_values['INPUT_LINE'] = self.input_line
        else:
            self.input_line = param_keys_and_values['INPUT_LINE']

        # Make sure PX_PER_DEG is in the template parameters
        param_keys_and_values['PX_PER_DEG'] = self.pixels_per_degree


        template_script = Template(self.template_script)
        runnable_script = template_script.substitute(param_keys_and_values)

        template_script_basename = os.path.basename(self.retina_script_template_filename)
        template_script_basename = os.path.splitext(template_script_basename)[0]
        runnable_script_filename = template_script_basename + SUFFIX_BUILT_FROM_TEMPLATE + '.py'
        runnable_file_location = COREM_ROOT_DIR + COREM_RETINA_SCRIPTS_DIR + runnable_script_filename
        fi = open(runnable_file_location, 'w')
        fi.write(runnable_script)
        fi.close()
        self.retina_script_filename = runnable_script_filename

        print 'Retina template prepared for running.'

    def simulate_retina(self, retina_params={}):
        '''
        Run the retina script.
        Note that this always deletes any previous data in the results directory (COREM default behavior).

        :return: True if script could be run, otherwise False
        '''

        if self.script_is_template is True:
            self._prepare_template(retina_params)

        print 'Running retina simulation %s' % self.retina_script_filename
        original_run_path = os.path.abspath(os.path.curdir)
        os.chdir(COREM_ROOT_DIR)
        call = './corem ' + COREM_RETINA_SCRIPTS_DIR + self.retina_script_filename
        try:
            os.system(call)
        except:
            return False
        os.chdir(original_run_path)
        return True

    def archive_results(self, results_archive_dir, simulation_name):

        self._read_results(make_timedarray=False)  # data saved in timestep-resolution and without units

        save_path = results_archive_dir + simulation_name + '.bz2'
        print 'Archiving simulation results to ' + save_path

        with bz2.BZ2File(save_path, 'wb') as fb:
            pickle.dump(self.results_data, fb, pickle.HIGHEST_PROTOCOL)


    def _read_results(self, make_timedarray=True):
        '''
        Read data from the COREM results folder into a dict (of TimedArrays)

        :return: dict of results, indexed by result IDs -> cell number
        '''

        if self.custom_results_dir is None:
            results_dir = COREM_ROOT_DIR + COREM_RESULTS_RELDIR
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

            if make_timedarray is True:
                b = transpose(a)  # because of TimedArray
                c = b * self.results_unit
                self.results_data[id] = TimedArray(c, dt=self.retina_timestep)
            else:
                self.results_data[id] = a

    def _get_timedarray(self, id):

        # Make sure results data have been loaded
        if len(self.results_data) == 0:
            self._read_results()
        else:
            pass

        return self.results_data[id]

    def set_input_grating(self, grating_type, width, height, spatial_freq, temporal_freq, orientation=0, contrast=0.5):
        '''
        Set input to drifting/static/oscillating grating with given parameters

        :param px_per_deg:
        :param grating_type: type of grating (0=drifting, 1=oscillating (or static with temporal_freq=0))
        :param width: input width in degrees
        :param height: input height in degrees
        :param spatial_freq: spatial frequency in cycles/degree
        :param temporal_freq: temporal frequency in hertz
        :param orientation: grating orientation in degrees (eg. 0: vertical, moving left-to-right, 90: horizontal, moving up-to-down)
        :param contrast: contrast between grating peaks and troughs
        :return:
        '''
        width_px = int(width * self.pixels_per_degree)
        height_px = int(height * self.pixels_per_degree)
        spatial_period = int(self.pixels_per_degree/spatial_freq)
        orientation_rad = (orientation/360)*2*pi
        self.input_line = "retina.Input('grating',{'type','"+str(grating_type)+"','step','0.001','length1','0.0','length2','4.0'," \
                          "'length3','0.0','sizeX','"+str(width_px)+"','sizeY','"+str(height_px)+"','freq','"+str(temporal_freq)+"'," \
                          "'period','"+str(spatial_period)+"','Lum','100.0','Contr','"+str(contrast)+"','phi_s','0.0'," \
                          "'phi_t','0.0','orientation','"+str(orientation_rad)+"','red_weight','1.0','green_weight','1.0'," \
                          "'blue_weight','1.0','red_phase','0.0','green_phase','0.0','blue_phase','0.0'})"
        #print self.input_line

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
        save_path = CXSYSTEM_INPUT_DIR + 'parafov_output.bz2'
        with bz2.BZ2File(save_path, 'wb') as fb:
            pickle.dump(output_dict, fb, pickle.HIGHEST_PROTOCOL)


class CoremOutput(object):

    def __init__(self, corem_archive_dir, corem_simulation_name, corem_output_unit=1, corem_timestep=1*ms, pixels_per_deg=1, input_width=1, input_height=1):
        '''
        Initialization routine for class Corem_output

        :param corem_archive_dir: str, absolute reference to where packaged COREM output is stored
        :param corem_simulation_name: str, (file-)name of COREM simulation data (without extension)
        :param corem_output_unit: Brian2 unit, eg. nS, mV
        :param corem_timestep: multiple of 1*ms, resolution of COREM simulation (TODO - should come automatically)
        '''

        self.corem_archive_dir = corem_archive_dir
        self.corem_simulation_name = corem_simulation_name
        self.corem_output_unit = corem_output_unit
        self.corem_timestep = corem_timestep

        # TODO - These should come from simulation data:
        self.pixels_per_deg = pixels_per_deg
        self.input_width = input_width
        self.input_height = input_height

        # Load COREM simulation data
        self.corem_output_data = dict()
        self._load_corem_output()

        # Set default positions (origin ie. 0) for COREM output cells
        # Note that Brian2 TimedArray also indexes neurons from 0 onwards
        self.corem_positions = dict()
        for channel_id in self.corem_output_data.keys():
            neuron_count = len(self.corem_output_data[channel_id][0])
            self.corem_positions[channel_id] = [0]*neuron_count

    def _load_corem_output(self):
        save_path = self.corem_archive_dir + self.corem_simulation_name + '.bz2'
        print 'Reading simulation data from ' + save_path

        with bz2.BZ2File(save_path, 'r') as fb:
            output_raw = pickle.load(fb)

        for id in output_raw.keys():
            a = output_raw[id]
            b = transpose(a)  # TimedArray takes in 2D arrays with time as the 1st and neuron index as the 2nd dimension
            c = b * self.corem_output_unit
            self.corem_output_data[id] = c

    def get_corem_channel_raw(self, channel_id):

        try:
            return self.corem_output_data[channel_id]
        except:
            print 'Output channel ' + str(channel_id) + ' not found from simulation data. Please try one of these: '
            print self.corem_output_data.keys()

    def get_corem_channel_ta(self, channel_id):

        try:
            c = self.corem_output_data[channel_id]
            return TimedArray(c, dt=self.corem_timestep)
        except:
            print 'Output channel ' + str(channel_id) + ' not found from simulation data. Please try one of these: '
            print self.corem_output_data.keys()

    def set_corem_positions_rectgrid(self, channel_id, grid_center):
        '''

        :param channel_id: str, name of the output channel in COREM data
        :param grid_center: complex coordinates z=x+yj, x>0 and y representing location on retina in degrees
        :return:
        '''

        neuron_spacing = 1/self.pixels_per_deg
        w_neurons = self.input_width * self.pixels_per_deg
        h_neurons = self.input_height * self.pixels_per_deg

        # Assume w_neurons and h_neurons are even numbers
        w_range = np.arange(-w_neurons / 2, w_neurons / 2) * neuron_spacing  # TODO - why here no +1 needed?
        h_range = np.arange(-h_neurons / 2, h_neurons / 2) * neuron_spacing
        h_range = np.flipud(h_range)  # For geometrical reasons (upper left spot belongs to neuron 0)

        # Generate coordinates
        z_coords = []
        for y in h_range:
            for x in w_range:
                z = grid_center + complex(x, y)
                small_shift = neuron_spacing/2  # add a shift to have positions in the centers of grid squares
                z += complex(small_shift, small_shift)

                z_coords.append(z)

        self.corem_positions[channel_id] = np.array(z_coords)

        # print len(self.corem_positions[channel_id])
        # plt.scatter(self.corem_positions[channel_id].real, self.corem_positions[channel_id].imag)
        # plt.show()

    def get_corem_positions(self, channel_id):
        return self.corem_positions[channel_id]

    def get_corem_neuron_position(self, channel_id, neuron_index):
        return self.corem_positions[channel_id][neuron_index]

    def get_outputs_within_circle(self, center, radius, channel_id):

        output_grid = self.corem_positions[channel_id]
        wanted_indices = np.where(np.absolute(center - output_grid) <= radius)
        return wanted_indices[0]  # For some reason np.where returns a tuple

    def get_outputs_within_hexagon(self, center, radius, channel_id):
        pass

class GanglionMosaic(object):

    def __init__(self, grid_center, gc_density, df_radius, input_width, input_height):
        self.grid_center = grid_center
        self.gc_density = gc_density
        self.df_radius = df_radius
        self.input_width = input_width
        self.input_height = input_height
        self.gc_rows = 0
        self.gc_columns = 0

        self._create_hexgrid()

        self.retina_output_data = ''
        self.retina_output_channel = ''
        self.gc_to_corem_nodes = [[]] * len(self.gc_positions)


    def _create_hexgrid(self):
        # Create ganglion cell mosaic (hexagonal grid)
        ganglion_spacing_adjacent = sqrt(2 / (sqrt(3) * self.gc_density))
        w_ganglioncells = self.input_width / ganglion_spacing_adjacent

        ganglion_spacing_rows = sqrt(sqrt(3) / (2 * self.gc_density))
        h_ganglioncells = self.input_height / ganglion_spacing_rows

        w_range = np.arange(-w_ganglioncells / 2, w_ganglioncells / 2 + 1) * ganglion_spacing_adjacent
        h_range = np.arange(-h_ganglioncells / 2, h_ganglioncells / 2 + 1) * ganglion_spacing_rows
        h_range = np.flipud(h_range)  # Indexing runs in up->down and left->right direction

        # Generate ganglion cell coordinates
        z_coords = []
        row_counter = 0
        for y in h_range:
            row_counter += 1
            for x in w_range:
                z = self.grid_center + complex(x, y)
                if row_counter % 2 == 0:
                    z -= complex(ganglion_spacing_adjacent / 2)  # Shift every other row to have a hexagonal lattice

                z_coords.append(z)

        z_coords = np.array(z_coords)

        self.gc_positions = z_coords
        self.gc_rows = h_ganglioncells
        self.gc_columns = w_ganglioncells

    def _compute_gc_to_corem_mapping(self):

        bc_grid = self.retina_output_data
        gc_grid = self.gc_positions

        for i in range(0, len(gc_grid)):
            current_gc = gc_grid[i]
            corresponding_outputs = bc_grid.get_outputs_within_circle(current_gc, self.df_radius, self.retina_output_channel)
            self.gc_to_corem_nodes[i] = corresponding_outputs

    def import_corem_output(self, retina_output, channel_id):

        self.retina_output_data = retina_output
        self.retina_output_channel = channel_id
        self._compute_gc_to_corem_mapping()

    def show_grids(self):

        bc_grid = self.retina_output_data.get_corem_positions(self.retina_output_channel)
        gc_grid = self.gc_positions

        # Show COREM grid (eg. bipolar cells)
        plt.scatter(bc_grid.real, bc_grid.imag, s=0.5)

        # Show ganglion cell grid
        # patches = [Circle((z.real, z.imag), self.df_radius) for z in gc_grid]
        patches = [RegularPolygon((z.real, z.imag), 6, self.df_radius) for z in gc_grid]
        collection = PatchCollection(patches)
        collection.set_facecolor('none')
        collection.set_edgecolor('r')
        ax = plt.gca()
        ax.add_collection(collection)

        plt.show()

    def average_corem_output(self, gc_index):

        bc_grid = self.retina_output_data.get_corem_positions(self.retina_output_channel)
        gc_grid = self.gc_positions

        gc_pos = gc_grid[gc_index]
        corr_bc_nodes = self.gc_to_corem_nodes[gc_index]

        # Get data from corresponding output nodes
        bc_data = self.retina_output_data.get_corem_channel_raw(self.retina_output_channel)
        corr_bc_data = transpose(bc_data)[corr_bc_nodes]  # 2D array with [output indices][time points]
        #corr_bc_data = transpose(corr_bc_data)

        # Scale output data in relation to distance from the ganglion cell "soma" (here gaussian filter)
        sigma = 1
        mu = gc_pos
        output_decay = lambda z: np.exp(- np.absolute(z - mu)**2 / (2 * sigma**2)) * 1/(sigma * np.sqrt(2 * np.pi))

        for k in range(0, len(corr_bc_nodes)):
            corr_bc_data[k] *= output_decay(bc_grid[k])

        # Sum filtered outputs
        corr_bc_data = transpose(corr_bc_data)  # back to [time points][output indices]
        gc_input = [sum(corr_bc_data[t]) for t in range(0, len(corr_bc_data))]

        return gc_input

if __name__ == '__main__':

    ### STEP 1: Simulate retina
    # ret = Corem_retina('parafoveal_parvo.py', 20, ['P_ganglion_L_ON_', 'P_ganglion_L_OFF_'], nsiemens, script_is_template=True)
    # retina_params = {'SIM_TIME': 1200,
    #                  'REC_START_TIME': 100,
    #                  'RF_CENTER_SIGMA': 0.03,
    #                  'CONE_H1_SIGMA': 0.5,
    #                  'RF_SURROUND_SIGMA': 0.5,
    #                  'SHOW_SIM': 'False'}
    #
    # ret.set_input_grating(grating_type=0, width=2, height=2, spatial_freq=1, temporal_freq=10, orientation=45)
    #
    # ret.simulate_retina(retina_params)
    # ret.archive_results('/home/shohokka/PycharmProjects/corem_archive/', 'oblique_grating')

    ### STEP 2: Read simulation output
    ret_output = CoremOutput('/home/shohokka/PycharmProjects/corem_archive/', 'oblique_grating', nS, pixels_per_deg=20, input_width=2, input_height=2)
    ret_output.set_corem_positions_rectgrid('P_ganglion_L_ON_', 5+0j)

    ### STEP 3: Define ganglion cell layer
    # grid_center, gc_density, df_radius, input_width, input_height
    glayer = GanglionMosaic(5 + 0j, 10, 0.15, 2, 2)
    glayer.import_corem_output(ret_output, 'P_ganglion_L_ON_')
    #glayer.show_grids()
    a = glayer.average_corem_output(10)
    plt.plot(range(0, len(a)), a)
    plt.show()

    print 'Done.'