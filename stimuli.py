__author__ = 'V_AD'
from numpy import *
from brian2  import *
# import scipy.io as sio
from scipy import io
import os
import cPickle as pickle
import zlib
import bz2
import shutil


class stimuli(object):
    '''
    [Extracted from VCX_model] This is the stimulation object for applying the input to a particular NeuronGroup(). Currently only video input is supported.
    '''
    def __init__(self,duration,input_mat_path,output_folder,output_file_extension,save_generated_input_flag):
        self.i_patterns = {}
        self.BaseLine= 0 * second
        self.input_mat_path = input_mat_path
        self.duration = duration
        self.output_folder = output_folder
        self.output_file_extension = output_file_extension
        self.save_generated_input_flag = save_generated_input_flag
        if os.path.isfile(os.path.join(self.output_folder, 'input'+self.output_file_extension)):
            self.file_exist_flag = 1
            print "\nWarning: Generated video input exist in %s/input.%s " \
                  "\nThe input will NOT be overwritten for the sake of array running (even though you might not be using it). " \
                  "\nIf you need the data to be newly generated, please rename or remove the previous input file.\n" % (
            self.output_file_extension, self.output_folder)
        else:
            self.file_exist_flag = 0
    def generate_inputs(self, freq):
        '''
        The method for generating input based on the .mat file, using the internal _initialize_inputs() and _calculate_input_seqs() methods.

        :param path: path to the input .mat file.
        :param freq: frequency.
        :return:
        '''
        if not self.file_exist_flag:
            self.initialize_inputs(freq)
            self.calculate_input_seqs()
        else:
            return

    def initialize_inputs(self,  freq):
        print "Initializing stimuli..."

        #type : video
        _V1_mats = {}

        io.loadmat(os.path.abspath(path), _V1_mats)

        # Fill ISI with N-1 times frameduration of zeros
        SOA = 90 # in ms
        stimulus_epoch_duration = 15 # in ms, duration of Burbank whole stimulus
        assert np.mod(SOA, stimulus_epoch_duration) == 0, 'Stimulus onset asynchrony (SOA) must be an integer times frameduration, aborting...'
        SOA_in_N_frames = int(SOA / stimulus_epoch_duration)
        dense_stimulus = _V1_mats['stimulus']
        sparse_stimulus = np.tile(np.zeros_like(dense_stimulus), (1, SOA_in_N_frames))
        sparse_stimulus[:, 0::SOA_in_N_frames] = dense_stimulus

        try:
            frameduration = double(_V1_mats['frameduration'])
            raise NotImplementedError('Frameduration coming from actual video frame rate. This is not implemented yet for CXSystem')
        except:
            frameduration = stimulus_epoch_duration
        frames = TimedArray(np.transpose(sparse_stimulus),
                            dt=frameduration * ms)  # video_data has to be shape (frames, neurons), dt=frame rate
        self.frames = frames
        exec 'self.factor = %s' %freq
        self.i_patterns[len(self.i_patterns)] = frames.values * self.factor  # These must be final firing rates
        _all_stim = squeeze(self._V1_mats['stimulus'])
        if len(_all_stim.shape) == 2:
            slash_indices = [idx for idx, ltr in enumerate(self.input_mat_path) if ltr == '/']
            print 'One video stimulus found in file ' + self.input_mat_path[slash_indices[-1]+1:]

    def calculate_input_seqs(self):
        set_device('cpp_standalone', directory=os.path.join(self.output_folder,'Input_cpp_run'))
        inputdt = defaultclock.dt
        spikemons = []
        N0 = len(self.i_patterns[0].T)
        frames = self.frames
        factor = self.factor
        tmp_group = NeuronGroup(N0, 'rate = frames(t,i)*factor : Hz', threshold='rand()<rate*dt')
        tmp_network = Network()
        tmp_network.add(tmp_group)
        tmp_mon = SpikeMonitor(tmp_group)
        tmp_network.add(tmp_mon)
        spikemons.append(tmp_mon)
        if self.BaseLine == 0 * second:
            tmp_network.run(self.duration, report='text')
        else:
            tmp_network.run(self.BaseLine)
            tmp_network.run(self.duration - self.BaseLine)
        self.save_input_sequence(spikemons,os.path.join(self.output_folder,'input' ))
        shutil.rmtree(os.path.join(self.output_folder,'Input_cpp_run'))

    def save_input_sequence(self,spike_mons, save_path):
        if self.save_generated_input_flag:
            print "Saving the generated video input..."
            self.generated_input_folder = save_path + self.output_file_extension
            data_to_save = {}
            for ii in range(len(spike_mons)):
                data_to_save['spikes_' + str(ii)] = []
                data_to_save['spikes_' + str(ii)].append(spike_mons[ii].it[0].__array__())
                data_to_save['spikes_' + str(ii)].append(spike_mons[ii].it[1].__array__())
            self.data_saver(save_path+self.output_file_extension,data_to_save)
        else:
            print "Warning: generated video output is NOT saved."

    def load_input_seq(self,input_spike_file_location):
        if os.path.isfile(input_spike_file_location):
            input_spike_file_location = input_spike_file_location
        else:
            input_spike_file_location = os.path.join(input_spike_file_location, 'input' + self.output_file_extension)
        self.loaded_data = self.data_loader(input_spike_file_location)
        new_spikes = self.loaded_data['spikes_0']
        neuron_positions_in_cortex = io.loadmat(self.input_mat_path, variable_names='w_coord')
        number_of_neurons = len(neuron_positions_in_cortex['w_coord'])
        print "Info: Video input loaded"
        return new_spikes[0], new_spikes[1], number_of_neurons


    def get_input_positions(self):
        '''
        Extract the positions from the .mat file.

        :param path: Path to the .mat file.
        '''
        neuron_positions = io.loadmat(self.input_mat_path, variable_names='z_coord')
        return neuron_positions['z_coord']

    def data_loader(self,input_path):
        if '.gz' in input_path:
            with open(input_path, 'rb') as fb:
                data = zlib.decompress(fb.read())
                loaded_data = pickle.loads(data)
        elif '.bz2' in input_path:
            with bz2.BZ2File(input_path, 'rb') as fb:
                loaded_data = pickle.load(fb)
        elif 'pickle' in input_path:
            with open(input_path, 'rb') as fb:
                loaded_data= pickle.load(fb)
        return loaded_data

    def data_saver(self,save_path,data):
        if '.gz' in save_path:
            with open(save_path, 'wb') as fb:
                fb.write(zlib.compress(pickle.dumps(data, pickle.HIGHEST_PROTOCOL), 9))
        elif '.bz2' in save_path:
            with bz2.BZ2File(save_path, 'wb') as fb:
                pickle.dump(data, fb, pickle.HIGHEST_PROTOCOL)
        elif '.pickle' in save_path:
            with open(save_path, 'wb') as fb:
                pickle.dump(data, fb, pickle.HIGHEST_PROTOCOL)