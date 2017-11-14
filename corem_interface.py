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
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
import scipy.io as spio
import re
from string import Template
import cPickle as pickle
import bz2
from matplotlib.animation import FuncAnimation
from brian2 import *  # Load brian2 last for unit-handling to work properly in Numpy


# Global constants
# DIR: absolute directory reference, RELDIR: relative directory reference
COREM_ROOT_DIR = '/home/shohokka/PycharmProjects/COREM/COREM/'
COREM_RESULTS_RELDIR = 'results/'  # directory relative to ROOT_DIR
COREM_RETINA_SCRIPTS_DIR = 'Retina_scripts/'  # directory relative to ROOT_DIR
SUFFIX_BUILT_FROM_TEMPLATE = '_runme'
CXSYSTEM_INPUT_DIR = '/home/shohokka/PycharmProjects/CXSystem_Git/video_input_files/'


class CoremRetina(object):
    """
    Class for running a COREM retina model
    """


    def __init__(self, retina_script_filename=None, pixels_per_degree=100, stream_ids=[], results_unit=1, script_is_template=False, custom_results_dir=None, retina_timestep=1 * ms):
        """
        Initialization method for class CoremRetina

        :param retina_script_filename: str, file in COREM_RETINA_SCRIPTS_DIR to run
        :param retina_timestep: x*ms, timestep of COREM simulation (default 1*ms)
        """

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
        self.stream_ids = stream_ids
        self.results_unit = results_unit  # DATA_UNIT
        self.custom_results_dir = custom_results_dir
        self.retina_timestep = retina_timestep  # RETINA_SIM_TIMESTEP
        self.simulation_data = dict()
        self.input_line = "retina.Input('impulse', {'start','100.0','stop','500.0','amplitude','1800.0','offset','100.0','sizeX','20','sizeY','20'})"

        #self.parameters_to_save = dict()

    def _which_parameters(self):
        '''
        Private method listing the parameters in a template script

        :return: array of strings, parameter names
        '''

        fi = open(self.template_file_location, 'r')
        self.template_script = fi.read()
        fi.close()
        param_keys = re.findall('\$\w*', self.template_script)
        param_keys = [key.lstrip('$') for key in param_keys]
        return list(set(param_keys))

    def _prepare_template(self, param_keys_and_values):
        '''
        Replace parameter names in a retina template script with set values.

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

    def _archive_parameters(self):
        pass

    def archive_data(self, results_archive_dir, simulation_name):
        """
        Archive and save data from a retina simulation (COREM erases everything in the results folder before runs)

        :param results_archive_dir: string, absolute reference to target directory
        :param simulation_name: string, wanted filename (the suffix .bz2 will be added automatically)
        :return:
        """
        self._read_results(make_timedarray=False)  # data is to be saved in timestep-resolution and without units

        save_path = results_archive_dir + simulation_name + '.bz2'
        print 'Archiving simulation results to ' + save_path

        with bz2.BZ2File(save_path, 'wb') as fb:
            pickle.dump(self.simulation_data, fb, pickle.HIGHEST_PROTOCOL)

    def _natural_sort(self, l):
        """
        Thanks to Mark Byers at StackOverflow

        :param l:
        :return:
        """
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)

    def _read_results(self, make_timedarray=True):
        '''
        Read data from the COREM results folder into a dict (of TimedArrays)

        :param make_timedarray: results can be directly read into Brian2 TimedArrays (used in demo)
        :return: dict of results, indexed by channel IDs and then cell number
        '''

        if self.custom_results_dir is None:
            results_dir = COREM_ROOT_DIR + COREM_RESULTS_RELDIR
        else:
            results_dir = self.custom_results_dir

        print 'Reading retina simulation results from %s' % results_dir

        results_dict = dict()

        for id in self.stream_ids:
            simulation_files = [sim_file for sim_file in os.listdir(results_dir) if id in sim_file]

            # NB! Since COREM names output files without leading zeros, the default sort will produce
            # weird behavior later on. Natural sort is needed.
            # simulation_files.sort()  # Sort in ascending order, eg. Ganglion_ON_0, 1, ..., Ganglion_ON_1000
            simulation_files = self._natural_sort(simulation_files)

            # print simulation_files
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
                self.simulation_data[id] = TimedArray(c, dt=self.retina_timestep)
            else:
                self.simulation_data[id] = a

    def _get_timedarray(self, stream_id):
        """
        Return simulation data of a particular channel as a Brian2 TimedArray

        :param stream_id: string, channel ID
        :return:
        """

        # Make sure results data have been loaded
        if len(self.simulation_data) == 0:
            self._read_results()
        else:
            pass

        return self.simulation_data[stream_id]

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

    def run_demo(self):
        '''
        An attempt at integrating COREM to CxSystem and at simulating parafoveal retina of macaque monkey.
        TODO - Obsolete, these functionalities have been moved to class CoremData

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
        plt.legend()
        plt.show()

        output_dict['spikes_0'] = []
        output_dict['spikes_0'].append(list(spikes_on.i))
        output_dict['spikes_0'][0].extend([i+number_cells for i in spikes_off.i])
        output_dict['spikes_0'].append(list(spikes_on.t))  # Needs to have unit (CxS bug)
        output_dict['spikes_0'][1].extend(list(spikes_off.t))

        # Vafa's savedata
        # save_path = CXSYSTEM_INPUT_DIR + 'parafov_output.bz2'
        # with bz2.BZ2File(save_path, 'wb') as fb:
        #     pickle.dump(output_dict, fb, pickle.HIGHEST_PROTOCOL)


class CoremData(object):
    """
    Class for accessing COREM simulation data and placing it spatially
    """
    # TODO - default stream parameter, so you don't have to mention the stream every time

    def __init__(self, corem_archive_dir, corem_simulation_name, corem_output_unit=1, corem_timestep=1*ms, pixels_per_deg=1, input_width=1, input_height=1):
        """
        Initialization method for class CoremOutput

        :param corem_archive_dir: str, absolute reference to where packaged COREM output is stored
        :param corem_simulation_name: str, (file-)name of COREM simulation data (without extension)
        :param corem_output_unit: Brian2 unit, eg. nS, mV
        :param corem_timestep: multiple of 1*ms, resolution of COREM simulation (TODO - should come automatically)
        """

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
        self._load_corem_data()

        # Set default positions (origin ie. 0) for COREM output cells
        # Note that Brian2 TimedArray also indexes neurons from 0 onwards
        self.corem_positions = dict()
        for channel_id in self.corem_output_data.keys():
            neuron_count = len(self.corem_output_data[channel_id][0])
            self.corem_positions[channel_id] = [0]*neuron_count

    def _load_corem_data(self):
        """
        Internal method for loading archived COREM simulation data

        :return:
        """

        save_path = self.corem_archive_dir + self.corem_simulation_name + '.bz2'
        print 'Reading simulation data from ' + save_path

        with bz2.BZ2File(save_path, 'r') as fb:
            output_raw = pickle.load(fb)

        for id in output_raw.keys():
            a = output_raw[id]
            b = transpose(a)  # TimedArray takes in 2D arrays with time as the 1st and neuron index as the 2nd dimension
            c = b * self.corem_output_unit
            self.corem_output_data[id] = c

    def get_corem_stream_raw(self, stream_id):
        """
        Return a particular output stream as a raw 2D array. Neuron indexing begins from 0.

        :param stream_id: str
        :return: 2D array with time as the 1st and neuron index as the 2nd dimension
        """
        try:
            return self.corem_output_data[stream_id]
        except:
            print 'Output stream ' + str(stream_id) + ' not found from simulation data. Please try one of these: '
            print self.corem_output_data.keys()

    def get_corem_stream_ta(self, stream_id):
        """
        Return a particular output stream as a Brian2 TimedArray. Neuron indexing begins from 0.

        :param stream_id: str
        :return: Brian2 TimedArray
        """
        try:
            c = self.corem_output_data[stream_id]
            return TimedArray(c, dt=self.corem_timestep)
        except:
            print 'Output stream ' + str(stream_id) + ' not found from simulation data. Please try one of these: '
            print self.corem_output_data.keys()

    def place_corem_on_rectgrid(self, stream_id, grid_center):
        """
        Place COREM nodes of a particular stream on a rectangular grid centered at grid_center
        TODO - Check this

        :param stream_id: str, name of the output stream in COREM data
        :param grid_center: complex coordinates z=x+yj, x>0 and y representing location in visual field (?) in degrees
        :return:
        """

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

        self.corem_positions[stream_id] = np.array(z_coords)

        # print len(self.corem_positions[channel_id])
        # plt.scatter(self.corem_positions[channel_id].real, self.corem_positions[channel_id].imag)
        # plt.show()

    def get_corem_positions(self, stream_id):
        """
        Return positions of COREM nodes of a particular stream

        :param stream_id: str
        :return:
        """
        return self.corem_positions[stream_id]

    def get_corem_node_position(self, stream_id, neuron_index):
        """
        Return position of a COREM node of a particular stream

        :param stream_id: str
        :param neuron_index: int
        :return:
        """
        return self.corem_positions[stream_id][neuron_index]

    def get_nodes_within_circle(self, center, radius, stream_id):
        """
        Get nodes (of a stream) within a set distance from a set point

        :param center: x+yj
        :param radius: float
        :param stream_id: str
        :return: array of ints (neuron indices)
        """
        output_grid = self.corem_positions[stream_id]
        wanted_indices = np.where(np.absolute(center - output_grid) <= radius)
        return wanted_indices[0]  # For some reason np.where returns a tuple

    def get_nodes_within_hexagon(self, center, radius, stream_id):
        """
        Get nodes inside a hexagon

        :param center: x+yj
        :param radius: float
        :param stream_id: str
        :return: array of ints (neuron indices)
        """

        output_grid = self.corem_positions[stream_id]

        hexagon = RegularPolygon((center.real, center.imag), 6, radius=radius)
        hexagon_path = hexagon.get_path()       # matplotlib returns the unit hexagon
        hexagon_tf = hexagon.get_transform()    # which can then be transformed to give the real path
        real_hexagon_path = hexagon_tf.transform_path(hexagon_path)

        output_grid_tuples = [(z.real, z.imag) for z in output_grid]
        wanted_indices = np.where(real_hexagon_path.contains_points(output_grid_tuples))

        return wanted_indices[0]


class GanglionMosaic(object):
    """
    Class for generating ganglion cell responses
    """
    def __init__(self, grid_center, gc_density, df_radius, input_width, input_height):
        self.grid_center = grid_center
        self.gc_density = gc_density
        if df_radius == 0:
            self.df_radius = self._compute_hexagon_radius(gc_density)
        else:
            self.df_radius = df_radius

        self.input_width = input_width
        self.input_height = input_height
        self.gc_rows = 0
        self.gc_columns = 0

        self._create_hexgrid()

        self.retina_output_data = ''
        self.retina_output_channel = ''
        self.gc_to_corem_nodes = [[]] * len(self.gc_positions)

        # Ganglion cell parameters
        self.default_gc_params = {
            "C_m": 100.0 * pF,
            "g_L": 10.0 * nS,
            "E_ex": 0.0 * mV,
            "E_in": -70.0 * mV,
            "E_L": -60.0 * mV,
            "V_th": -55.0 * mV,
            "V_reset": -60.0 * mV,
            "t_ref": 2.0 * ms,
            "rate": 0.0 * Hz,  # not used
            "tau_e": 3.0 * ms,  # not used
            "tau_i": 8.3 * ms,  # not used
            "tonic_current": 0 * pA,
            "noise": 0 * mV,
            "gi": 0 * nS
        }

    def _compute_hexagon_radius(self, gc_density):
        """
        Given a density ganglion cells, computes how large a hexagon can GCs have

        :param gc_density: int/float, density of ganglion cells per deg^2
        :return: float, maximal radius of hexagons (in deg)
        """

        a = 2/(3*sqrt(3)*gc_density)  # from simple trigonometry
        return sqrt(a)

    def _create_hexgrid(self):
        """
        Places the ganglion cells in a hexagonal grid according to __init__ parameters

        :return:
        """

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
        """
        Computes the 1-to-many mapping of ganglion cells to COREM nodes and stores it in the class variable
        gc_to_corem_nodes

        :return:
        """
        bc_grid = self.retina_output_data
        gc_grid = self.gc_positions

        for i in range(0, len(gc_grid)):
            current_gc = gc_grid[i]
            # corresponding_outputs = bc_grid.get_nodes_within_circle(current_gc, self.df_radius, self.retina_output_channel)
            corresponding_outputs = bc_grid.get_nodes_within_hexagon(current_gc, self.df_radius, self.retina_output_channel)

            self.gc_to_corem_nodes[i] = corresponding_outputs

    def import_corem_output(self, retina_output, stream_id):
        """
        Imports COREM simulation data

        :param retina_output: CoremData instance
        :param stream_id: str, name of wanted stream
        :return:
        """
        self.retina_output_data = retina_output
        self.retina_output_channel = stream_id
        self._compute_gc_to_corem_mapping()

    def show_grids(self):
        """
        Display of COREM data and simulated ganglion cell spikes in retinal and cortical locations

        :return:
        """

        bc_grid = self.retina_output_data.get_corem_positions(self.retina_output_channel)
        gc_grid = self.gc_positions

        bc_grid_cortex = self._cortical_mapping(bc_grid)
        gc_grid_cortex = self._cortical_mapping(gc_grid)

        self.grids_fig, self.grids_ax = plt.subplots(1, 3)

        ### Bipolar output
        plt.subplot(131)
        ax = plt.gca()
        plt.title('Bipolar output')
        # self.anim_bipolar_grid = sns.heatmap(np.zeros((40,40)), vmin=0, vmax=1000, ax=ax)
        self.anim_bipolar_grid = ax.imshow(np.random.random((40,40)), interpolation='none', vmin=0.5e-9, vmax=1.5e-9, aspect='auto')

        ### GRIDS in retina
        plt.subplot(132)
        ax = plt.gca()
        plt.title('Ganglion cell spikes (in retina)')
        plt.xlabel('Eccentricity (deg)')
        plt.ylabel('Azimuth (deg)')
        # Show COREM grid (eg. bipolar cells)
        plt.scatter(bc_grid.real, bc_grid.imag, s=0.5)
        # self.anim_retina_grid, = self.grids_ax[0].plot([5], [0], '.')
        self.anim_retina_grid, = ax.plot([], [], '.')

        # Show ganglion cell grid
        patches = [RegularPolygon((z.real, z.imag), 6, self.df_radius) for z in gc_grid]
        collection = PatchCollection(patches)
        collection.set_facecolor('none')
        collection.set_edgecolor('grey')
        ax = plt.gca()
        ax.add_collection(collection)

        # For testing: circles around hexagons
        # patches_circ = [Circle((z.real, z.imag), self.df_radius) for z in gc_grid]
        # collection_circ = PatchCollection(patches_circ)
        # collection_circ.set_facecolor('none')
        # collection_circ.set_edgecolor('b')
        # ax = plt.gca()
        # ax.add_collection(collection_circ)

        ### GRIDS in cortex
        plt.subplot(133)
        ax = plt.gca()
        plt.title('Ganglion cell spikes (proj to cortex)')
        plt.xlabel('x (mm)')
        plt.ylabel('y (mm)')
        decay_const = 5
        plt.scatter(bc_grid_cortex.real, bc_grid_cortex.imag, s=0.5)
        # plt.scatter(gc_grid_cortex.real, gc_grid_cortex.imag)
        self.anim_cortex_grid, = ax.plot([], [], '.')
        patches_circ = [Circle((z.real, z.imag), 1/decay_const) for z in gc_grid_cortex]
        collection_circ = PatchCollection(patches_circ)
        collection_circ.set_facecolor('none')
        collection_circ.set_edgecolor('grey')
        ax = plt.gca()
        ax.add_collection(collection_circ)

        network_center = 17*log((5+0j)+1)
        network_radius = 2.5
        network_circle = Circle((network_center.real, network_center.imag), network_radius)
        network_circle.set_facecolor('none')
        network_circle.set_edgecolor('green')
        ax.add_artist(network_circle)

        # plt.tight_layout()
        # patches = [RegularPolygon((z.real, z.imag), 6, self.df_radius) for z in gc_grid_cortex] # not really but
        # collection = PatchCollection(patches)
        # collection.set_facecolor('none')
        # collection.set_edgecolor('r')
        # ax = plt.gca()
        # ax.add_collection(collection)

        # plt.show()

    def animate_grids(self, i):
        """
        Animation routine for show_grids

        :param i: int, time step (typically refers to i-th millisecond)
        :return:
        """

        # Parameters (for spike plots)
        t = i * 1*ms
        t_abs = t/second
        t_res = 0.001  # 0.001 seems ok

        bc_grid = self.retina_output_data.get_corem_positions(self.retina_output_channel)
        gc_grid = self.gc_positions
        gc_grid_cortex = self._cortical_mapping(gc_grid)

        # First draw bipolar output
        bc_data = self.retina_output_data.get_corem_stream_ta(self.retina_output_channel)
        bc_snapshot = np.reshape([bc_data(t, k) for k in range(len(bc_grid))], (-1, 40))

        self.anim_bipolar_grid.set_array(bc_snapshot)

        # Then, draw spiking
        # w_coord = self.data['positions_all']['w_coord'][group_name]
        spikes_i = self.gc_spikes_i.astype(int)
        spikes_t = self.gc_spikes_t  # / second

        who_are_spiking = np.unique(spikes_i[np.where(abs(spikes_t - t_abs) < t_res)])
        retina_spikers_coord = np.array([gc_grid[i] for i in who_are_spiking])
        cortex_spikers_coord = np.array([gc_grid_cortex[i] for i in who_are_spiking])

        self.grids_fig.suptitle('Time ' + str(t), fontsize=18)

        self.anim_retina_grid.set_data(retina_spikers_coord.real, retina_spikers_coord.imag)
        self.anim_cortex_grid.set_data(cortex_spikers_coord.real, cortex_spikers_coord.imag)

    def average_corem_output(self, gc_index):
        """
        Averages data from many COREM nodes corresponding to 1 ganglion cell

        :param gc_index: int, index of ganglion cell
        :return: array of floats, ganglion cell input [indexing in time]
        """

        bc_grid = self.retina_output_data.get_corem_positions(self.retina_output_channel)
        gc_grid = self.gc_positions

        gc_pos = gc_grid[gc_index]
        corr_bc_nodes = self.gc_to_corem_nodes[gc_index]

        # For testing purposes
        # new_bc_nodes = self.retina_output_data.get_nodes_within_hexagon(gc_pos, self.df_radius, self.retina_output_channel)
        # print 'Hex BC nodes are: ' + str(new_bc_nodes)
        # print 'Circular BC nodes are: ' + str(corr_bc_nodes)
        # print 'Nodes within hexagon '+str(gc_index)+': '
        # print corr_bc_nodes

        # Get data from corresponding output nodes
        bc_data = self.retina_output_data.get_corem_stream_raw(self.retina_output_channel)
        corr_bc_data = transpose(bc_data)[corr_bc_nodes]  # 2D array with [output indices][time points]
        #corr_bc_data = transpose(corr_bc_data)

        # Scale output data in relation to distance from the ganglion cell "soma" (here gaussian filter)
        sigma = 1
        mu = gc_pos
        output_decay = lambda z: np.exp(- np.absolute(z - mu)**2 / (2 * sigma**2))  # * 1/(sigma * np.sqrt(2 * np.pi))
        # output_decay = lambda z: 1

        distance_weights = [output_decay(bc_grid[corr_bc_nodes[i]]) for i in range(len(corr_bc_nodes))]

        corr_bc_data = transpose(corr_bc_data)  # back to [time points][output indices]
        # gc_input = [sum(corr_bc_data[t]) for t in range(0, len(corr_bc_data))]
        # TODO - Mean of empty slice warning!
        if len(corr_bc_nodes) > 0:
            gc_input = [numpy.average(corr_bc_data[t], weights=distance_weights) for t in range(0, len(corr_bc_data))]
        else:
            gc_input = [0 for t in range(len(corr_bc_data))]

        return gc_input

    def archive_gc_input(self, filename):
        """
        Archives averaged ganglion cell input (not usually necessary)

        :param filename: str, file to which data is written
        :return:
        """
        data_to_save = dict()
        data_to_save['z_coord'] = self.gc_positions
        data_to_save['retinal_gc_input'] = []

        for i in range(len(self.gc_positions)):
            a = self.average_corem_output(i)
            data_to_save['retinal_gc_input'].append(a)

        save_path = CXSYSTEM_INPUT_DIR + filename + '.bz2'
        print 'Archiving GC input to ' + save_path

        with bz2.BZ2File(save_path, 'wb') as fb:
            pickle.dump(data_to_save, fb, pickle.HIGHEST_PROTOCOL)

    def _cortical_mapping(self, z):
        """
        Retino-cortical coordinate transformation

        :param z: complex number, coordinates of visual field (deg)
        :return: w, coordinates in cortex (mm)
        """
        k = 17
        a = 1
        w = k*log(z+a)
        return w

    def generate_gc_spikes(self, filename, runtime=0*ms, show_sim=False):
        """
        Simulates ganglion cell responses and then saves them to a file

        :param filename: str
        :param runtime: time in ms
        :param show_sim: bool, shows a rasterplot of responses (default: False)
        :return:
        """

        gc_params = self.default_gc_params
        gc_params['tau_m'] = gc_params['C_m'] / gc_params['g_L']
        defaultclock.dt = 0.1 * ms

        model_eq = 'dvm/dt = (((g_L*(E_L-vm) + ge*(E_ex-vm) + gi*(E_in-vm)) + tonic_current) / C_m) + noise*xi*tau_m**-0.5: volt'
        N_gc = len(self.gc_positions)

        # Prepare GC input for interfacing with Brian2
        gc_input = [self.average_corem_output(k) for k in range(N_gc)]
        gc_input = transpose(gc_input) * siemens  # TODO - unit should come from config
        retina_timestep = self.retina_output_data.corem_timestep
        gc_input_ta = TimedArray(gc_input, dt=retina_timestep)
        model_eq_on = Equations(model_eq, ge='gc_input_ta(t,i)')

        # Create GC neurons
        gc_neuron = NeuronGroup(N_gc, model=model_eq_on, namespace=gc_params,
                                threshold='vm > ' + repr(gc_params['V_th']), reset='vm = ' + repr(gc_params['V_reset']),
                                refractory=gc_params['t_ref'], method='euler')

        gc_spikes = SpikeMonitor(gc_neuron)

        # Simulate ganglion cells!

        run(runtime)

        # Prepare spike trains for archiving
        output_dict = dict()

        # CxSystem (CxSystem.py->method relay->submethod spikes) loads given spike/input file and
        # expects spike data inside two arrays:
        # SPK_GENERATOR_SP = spikes_data['spikes_0'][0] - index of neuron
        # SPK_GENERATOR_TI = spikes_data['spikes_0'][1] - time of spike
        output_dict['spikes_0'] = []
        output_dict['spikes_0'].append(list(gc_spikes.i))
        output_dict['spikes_0'].append(list(gc_spikes.t))

        # Save for visualization
        self.gc_spikes_i = np.array(gc_spikes.i)
        self.gc_spikes_t = np.array(gc_spikes.t)

        # Save positions in retina (in degrees of visual field)
        output_dict['z_coord'] = self.gc_positions
        output_dict['w_coord'] = self._cortical_mapping(self.gc_positions)

        save_path = CXSYSTEM_INPUT_DIR + filename + '.bz2'
        print 'Saving GC spikes to ' + save_path

        with bz2.BZ2File(save_path, 'wb') as fb:
            pickle.dump(output_dict, fb, pickle.HIGHEST_PROTOCOL)

        if show_sim is True:
            plt.scatter(gc_spikes.t / ms, gc_spikes.i, s=0.4, color='green')
            plt.show()

    def show_gc_output(self, gc_index):
        """
        Obsolete - can probably be erased soon

        :param gc_index:
        :return:
        """

        # Ganglion cell parameters
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

        gc_input = self.average_corem_output(gc_index)*siemens
        retina_timestep = self.retina_output_data.corem_timestep
        gc_input_ta = TimedArray(gc_input, dt=retina_timestep)
        model_eq_on = Equations(model_eq, ge='gc_input_ta(t)')

        gc_neuron = NeuronGroup(1, model=model_eq_on, namespace=gc_params,
                                threshold='vm > ' + repr(gc_params['V_th']), reset='vm = ' + repr(gc_params['V_reset']),
                                refractory=gc_params['t_ref'], method='euler')

        gc_spikes = SpikeMonitor(gc_neuron)
        gc_state = StateMonitor(gc_neuron, ['vm'], record=[0])

        runtime=1000*ms
        run(runtime)

        plt.subplots(1, 3, sharex=True)

        plt.subplot(131)
        plt.title('Input to GC')
        x_arg = np.linspace(0, runtime/ms, 1000)
        plt.plot(x_arg, gc_input_ta(x_arg*ms))

        plt.subplot(132)
        plt.title('GC memb.voltage')
        plt.plot(gc_state.t/ms, gc_state.vm[0]/mV)

        plt.subplot(133)
        plt.title('Firing rate')

        # Moving avg firing rate
        bin_size = 5*ms
        n_bins = int(runtime / bin_size)
        spike_counts, bin_edges = np.histogram(gc_spikes.t/ms, bins=n_bins)
        firing_rates = [count / bin_size for count in spike_counts]

        sigma = 1
        gaussian_filter = lambda x: np.exp(- x ** 2 / (2 * sigma ** 2)) * 1 / (sigma * np.sqrt(2 * np.pi))
        filter_radius = 50
        v = gaussian_filter(np.arange(-filter_radius, filter_radius))
        b = np.convolve(firing_rates, v, mode='same')
        plt.plot(bin_edges[:-1], b)

        plt.show()



if __name__ == '__main__':

    ### DEMO
    # ret = CoremRetina('parafoveal_parvo.py', 5, ['P_ganglion_L_ON_', 'P_ganglion_L_OFF_'], nsiemens, script_is_template=True)
    # retina_params = {'SIM_TIME': 1100,
    #                  'REC_START_TIME': 100,
    #                  'RF_CENTER_SIGMA': 0.03,
    #                  'CONE_H1_SIGMA': 0.5,
    #                  'RF_SURROUND_SIGMA': 0.5,
    #                  'SHOW_SIM': 'False'}
    #
    # ret.set_input_grating(grating_type=0, width=2, height=2, spatial_freq=1, temporal_freq=7, orientation=0)
    #
    # ret.simulate_retina(retina_params)
    # ret.run_demo()

    STIMSEQ_NAME = 'smallspot'

    ## STEP 1: Simulate retina
    # ret = CoremRetina('parafoveal_parvo.py', 20, ['P_ganglion_L_ON_', 'P_ganglion_L_OFF_'], nsiemens, script_is_template=True)
    #
    # ### TODO - Retina params should go to init
    # retina_params = {'SIM_TIME': 1100,
    #                  'REC_START_TIME': 100,
    #                  'RF_CENTER_SIGMA': 0.03,
    #                  'CONE_H1_SIGMA': 0.5,
    #                  'RF_SURROUND_SIGMA': 0.5,
    #                  'SHOW_SIM': 'True'}
    #
    # ## TODO - Make a function of making seq films
    # retina_params['INPUT_LINE'] = "retina.Input('sequence','input_sequences/smallspot/',{'InputFramePeriod','100'})"
    # # ret.set_input_grating(grating_type=1, width=2, height=2, spatial_freq=1, temporal_freq=5, orientation=45)
    #
    # ret.simulate_retina(retina_params)
    #
    # ## TODO- archive_data shouldn't be a separate call
    # ret.archive_data('/home/shohokka/PycharmProjects/corem_archive/', STIMSEQ_NAME)


    # ### STEP 2: Read simulation output
    # TODO - Is it ever necessary to read CoremData separately? Could this just be inside the GanglionMosaic class?
    ret_output = CoremData('/home/shohokka/PycharmProjects/corem_archive/', STIMSEQ_NAME,
                           nS, pixels_per_deg=20, input_width=2, input_height=2)  # TODO <- these should be in the output file
    ret_output.place_corem_on_rectgrid('P_ganglion_L_ON_', 5+0j)
    #
    #
    # ### STEP 3: Define ganglion cell layer
    # # grid_center, gc_density, df_radius, input_width, input_height
    glayer = GanglionMosaic(5+0j, 200, df_radius=0, input_width=2, input_height=2)
    glayer.import_corem_output(ret_output, 'P_ganglion_L_ON_')
    glayer.generate_gc_spikes(STIMSEQ_NAME, 1000*ms, show_sim=False)

    glayer.show_grids()
    anim = FuncAnimation(glayer.grids_fig, glayer.animate_grids, frames=np.arange(1000), interval=40)
    print 'Saving animation'
    anim.save('/home/shohokka/' + STIMSEQ_NAME + '.mp4', extra_args=['-vcodec', 'libx264'])
    # plt.show()


    print 'Done.'