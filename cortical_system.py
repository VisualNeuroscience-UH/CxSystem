__author__ = 'V_AD'
from brian2 import *
import brian2genn
import os
import sys
from brian2_obj_defs import *
from matplotlib.pyplot import  *
from save_data import *
from stimuli import *
import ast
import ntpath
from scipy.sparse import csr_matrix
from datetime import datetime
import cPickle as pickle
import zlib
import bz2
import time
import __builtin__
import csv
import shutil
import pandas
import threading
import array_run
import multiprocessing


class cortical_system(object):
    '''
    The main object of cortical system module for building and running a customized model of cortical module in Brian2Genn.
    '''

    _NeuronGroup_prefix = 'NG'
    _NeuronNumber_prefix = 'NN'
    _NeuronEquation_prefix = 'NE'
    _NeuronThreshold_prefix = 'NT'
    _NeuronReset_prefix = 'NRes'
    _NeuronRef_prefix = 'NRef'
    _NeuronNS_prefix = 'NNs'  # name space prefix
    # _NeuronPos_prefix = 'NPos' # position prefix
    _Synapses_prefix = 'S'
    _SynapsesEquation_prefix = 'SE'
    _SynapsesPre_prefix = 'SPre'
    _SynapsesPost_prefix = 'SPost'
    _SynapsesNS_prefix = 'SNS'
    _SynapticConnection_prefix = 'SC'
    _SynapticWeight_prefix = 'SW'
    _SpikeMonitor_prefix = 'SpMon'
    _StateMonitor_prefix = 'StMon'

    def __init__(self, anatomy_and_system_config,physiology_config, output_file_suffix = ''):
        '''
        Initialize the cortical system by parsing the configuration file.

        :param anatomy_and_system_config: The path to the configuration file.
        :param output_path: The path to save the final data.
        :param use_genn: switch the GeNN mode on/off (1/0), by default GeNN is off

        Main internal variables:


        * customized_neurons_list: This list contains the customized_neuron instances. So for each neuron group target line, there would be an element in this list which contains all the information for that particular neuron group.
        * customized_synapses_list: This list contains the customized_synapse instances. Hence, for each synapse custom line, there would be an element in this list, containing all the necessary information.
        * neurongroups_list: This list contains name of the NeuronGroup() instances that are placed in the Globals().
        * synapses_name_list: This list contains name of the Synapses() instances that are placed in the Globals().
        * monitor_name_bank: The dictionary containing the name of the monitors that are defined for any NeuronGroup() or Synapses().
        * default_monitors: In case --> and <-- symbols are used in the configuration file, this default monitor will be applied on all the target lines in between those marks.
        * save_data: The save_data() object for saving the final data.

        '''
        self.start_time = time.time()
        self.main_module = sys.modules['__main__']
        try:  # try to find the CX_module in the sys.modules, to find if the __main__ is cortical_system.py or not
            self.CX_module = sys.modules['cortical_system']
        except KeyError:
            pass
        self._options = {
            #Parameter_name : [set priority (0 is highest),function_to_run]
            'device': [0,self.set_device],
            'save_generated_video_input_flag': [1,self.save_generated_video_input_flag],
            'runtime': [2,self._set_runtime],
            'sys_mode': [3,self._set_sys_mode],  # either "local" or "expanded"
            'scale': [4,self._set_scale],
            'grid_radius': [5,self._set_grid_radius],
            'min_distance': [6,self._set_min_distance],
            'do_init_vms': [7,self.do_init_vms],
            'output_path_and_filename': [8,self._set_output_path],
            'connections_saving_path_and_filename': [9,self._set_save_brian_data_path],
            'connections_loading_path_and_filename': [10,self._set_load_brian_data_path],
            'load_positions_only': [11,self.load_positions_only],
            'do_benchmark': [12,self.do_benchmark],
            'multidimension_array_run': [13,self.passer],  # this parameter is used by array_run module, so here we just pass
            'number_of_process': [14,self.passer],  # this parameter is used by array_run module, so here we just pass
            'trials_per_config': [15,self.passer],
            'G': [nan,self.neuron_group],
            'S': [nan,self.synapse],
            'IN': [nan,self.relay],
            'params': [nan,self.set_runtime_parameters],
        }
        self.StartTime_str = '_' + str(datetime.now()).replace('-', '').replace(' ', '_').replace(':', '')\
            [0:str(datetime.now()).replace('-', '').replace(' ', '_').replace(':', '').index('.')+3].replace('.','') + output_file_suffix
        print "Info: current run filename suffix is: %s"%self.StartTime_str[1:]
        # self.scale = 1
        #self.do_benchmark = 0
        # defaultclock.dt = 0.01 * ms
        if defaultclock.dt/second != 1e-4:
            print "\nWarning: default clock is %s\n" %str(defaultclock.dt)
        self.numerical_integration_method = 'euler'
        print "Info : the system is running with %s integration method"%self.numerical_integration_method
        # self.conn_prob_gain = synapse_namespaces.conn_prob_gain
        self.conn_prob_gain =1
        self.current_parameters_list = []
        self.current_parameters_list_orig_len = 0 # current_parameters_list is changing at some point in the code, so the original length of it is needed
        self.current_values_list = []
        self.NG_indices = []
        self.customized_neurons_list = []  # This list contains the customized_neuron instances. So for each neuron group target line, there would be an element in this list which contains all the information for that particular neuron group.
        self.customized_synapses_list = []  # This list contains the customized_synapse instances. Hence, for each synapse custom line, there would be an element in this list, containing all the necessary information.
        self.neurongroups_list = []  # This list contains name of the NeuronGroup() instances that are placed in the Globals().
        self.synapses_name_list = []  # This list contains name of the Synapses() instances that are placed in the Globals().
        self.monitor_name_bank = {}  # The dictionary containing the name of the monitors that are defined for any NeuronGroup() or Synapses().
        self.default_monitors = []  # In case --> and <-- symbols are used in the configuration file, this default monitor will be applied on all the target lines in between those marks.
        self.default_save_flag = -1
        self.default_load_flag = -1
        self.monitor_idx = 0
        self.total_synapses = 0
        self.sys_mode = ''
        self.total_number_of_synapses = 0
        self.total_number_of_connections = 0
        self.general_grid_radius = 0
        self.min_distance = 0
        self.do_init_vms = 0
        self.do_save_connections = 0 # if there is at least one connection to save, this flag will be set to 1
        self.load_positions_only = 0
        self.awaited_conf_lines = []
        self.physio_config_df = pandas.read_csv(physiology_config) if type(physiology_config) == str else physiology_config
        self.physio_config_df = self.physio_config_df.applymap(lambda x: NaN if str(x)[0] == '#' else x)
        self.anat_and_sys_conf_df = pandas.read_csv(anatomy_and_system_config,header=None) if type(anatomy_and_system_config) == str else anatomy_and_system_config
        self.anat_and_sys_conf_df = self.anat_and_sys_conf_df.applymap(lambda x: x.strip() if type(x) == str else x)
        ## dropping the commented lines :
        self.anat_and_sys_conf_df =  self.anat_and_sys_conf_df.drop(self.anat_and_sys_conf_df[0].index[self.anat_and_sys_conf_df[0][
            self.anat_and_sys_conf_df[0].str.contains('#') == True].index.tolist()]).reset_index(drop=True)
        self.physio_config_df = self.physio_config_df.drop(self.physio_config_df['Variable'].index[self.physio_config_df['Variable'][
            self.physio_config_df['Variable'].str.contains('#') == True].index.tolist()]).reset_index(drop=True)

        self.conf_df_to_save = self.anat_and_sys_conf_df
        self.physio_df_to_save =  self.physio_config_df
        self.array_run = 0
        check_array_run_anatomy = self.anat_and_sys_conf_df.applymap(lambda x: True if ('|' in str(x) or '&' in str(x)) else False)
        check_array_run_physiology = self.physio_config_df.applymap(lambda x: True if ('|' in str(x) or '&' in str(x)) else False)
        if any(check_array_run_anatomy) or any(check_array_run_physiology):
            array_run.array_run(self.anat_and_sys_conf_df,self.physio_config_df)
            self.array_run = 1
            return
        self.configuration_executer()
        if type(self.awaited_conf_lines) != list :
           if self.thr.is_alive()==True:
               print "Waiting for the video input"
               self.thr.join()
           self.anat_and_sys_conf_df = self.awaited_conf_lines
           self.configuration_executer()

        print "Cortical Module initialization Done."


    def configuration_executer(self):
        definition_lines_idx = self.anat_and_sys_conf_df.ix[:,0][self.anat_and_sys_conf_df.ix[:,0]=='row_type'].index
        order_of_lines = ['params','IN','G','S']
        for value_line_title in order_of_lines:
            for def_idx in definition_lines_idx:
                if value_line_title in self.anat_and_sys_conf_df.ix[def_idx+1,0]:
                    self.current_parameters_list = self.anat_and_sys_conf_df.ix[def_idx,1:].dropna()
                    self.current_parameters_list = self.current_parameters_list[~self.current_parameters_list.str.contains('#')]
                    self.current_parameters_list_orig_len = len(self.current_parameters_list)
                    try:
                        next_def_line_idx = definition_lines_idx[definition_lines_idx.tolist().index(def_idx)+1].item()
                    except IndexError:
                        next_def_line_idx = self.anat_and_sys_conf_df[0].__len__()
                    for self.value_line_idx in range(def_idx+1,next_def_line_idx):
                        if type(self.anat_and_sys_conf_df.ix[self.value_line_idx, 0]) == str:
                            if self.anat_and_sys_conf_df.ix[self.value_line_idx,0] in self._options.keys() and self.anat_and_sys_conf_df.ix[self.value_line_idx,0][0]!='#':
                                self.current_parameters_list = self.anat_and_sys_conf_df.ix[def_idx,1:].dropna()
                                self.current_parameters_list = self.current_parameters_list[~self.current_parameters_list.str.contains('#')]
                                self.current_values_list = self.anat_and_sys_conf_df.ix[self.value_line_idx,self.current_parameters_list.index].dropna()
                                self._options[self.anat_and_sys_conf_df.ix[self.value_line_idx,0]][1]()
                    break

    def passer(self,*args):
        pass

    def set_device(self,*args):
        self.device = args[0]
        assert self.device in ['GeNN', 'Cpp',
                               'Python'], 'Device %s is not defined. Check capital letters in device name.' % self.device
        if device == 'GeNN':
            print "Warning: system is going to be run using GeNN devices, " \
                  "Errors may rise if Brian2/Brian2GeNN/GeNN is not installed correctly or the limitations are not " \
                  "taken in to account."

    def run(self):
        if not self.array_run:
            run(self.runtime, report='text')
            if self.do_benchmark:
                self.benchmarking_data = {}
                titles= ['Computer Name','Device','File Suffix','Simulation Time','Python Compilation','Brian Code generation',\
                         'Device-Specific Compilation','Run','Extract and Save Result','Total Time']
                self.benchmarking_data['Simulation Time'] = str(self.runtime)
                self.benchmarking_data['Device'] = self.device
                self.benchmarking_data['File Suffix'] = self.StartTime_str[1:]
                if self.device != 'Python':
                    self.benchmarking_data['Python Compilation'] = __builtin__.code_generation_start - self.start_time
                    self.benchmarking_data['Brian Code generation'] = __builtin__.compile_start - __builtin__.code_generation_start
                    self.benchmarking_data['Device-Specific Compilation'] = __builtin__.run_start - __builtin__.compile_start
                else:
                    self.benchmarking_data['Python Compilation'] = __builtin__.run_start - self.start_time
                    self.benchmarking_data['Brian Code generation'] = '-'
                    self.benchmarking_data['Device-Specific Compilation'] = '-'
                self.saving_start_time = time.time()
                self.benchmarking_data['Run'] = self.saving_start_time -  __builtin__.run_start
            self.gather_result()
            self.end_time = time.time()
            if self.do_benchmark:
                self.benchmarking_data['Extract and Save Result'] = self.end_time - self.saving_start_time
                self.benchmarking_data['Total Time'] = self.end_time - self.start_time
                import platform
                self.benchmarking_data['Computer Name'] = platform.node()
                write_titles = 1 if not os.path.isfile(os.path.join(self.output_folder,'benchmark.csv')) else 0
                with open(os.path.join(self.output_folder,'benchmark.csv'), 'ab') as f:
                    w = csv.DictWriter(f, titles)
                    if write_titles:
                        w.writeheader()
                    w.writerow(self.benchmarking_data)
                    print "Benchmarking data saved"
            print "Info: simulating %s took in total %d s" % (str(self.runtime),self.end_time-self.start_time)
            if self.device == 'GeNN':
                shutil.rmtree(os.path.join(self.output_folder, self.StartTime_str[1:]))
            elif self.device == 'Cpp':
                shutil.rmtree(os.path.join(self.output_folder, self.StartTime_str[1:]))

    def set_runtime_parameters(self):
        if not any(self.current_parameters_list.str.contains('runtime')):
            print "\nWarning: runtime duration is not defined in the configuration file. The default runtime duratoin is 500*ms\n"
            self.runtime = 500*ms
        if not any(self.current_parameters_list.str.contains('device')):
            print "\nWarning: device is not defined in the configuration file. The default device is Python.\n"
            self.device = 'Python'
        for ParamIdx, parameter in self.current_parameters_list.iteritems():
            if parameter not in self._options.keys():
                print "Warning: system parameter %s not defined." % parameter
        options_with_priority = [it for it in self._options if not isnan(self._options[it][0])]
        parameters_to_set_prioritized = [it for priority_idx in range(len(options_with_priority)) for it in self._options if self._options[it][0]==priority_idx]
        for correct_parameter_to_set in parameters_to_set_prioritized:
            for ParamIdx,parameter in self.current_parameters_list.iteritems():
                if parameter == correct_parameter_to_set:
                    assert (parameter in self._options.keys()), 'The tag %s is not defined.' % parameter
                    self._options[parameter][1](self.current_values_list[ParamIdx])
                    break
        if self.sys_mode == '':
            raise NameError("System mode is not defined.")
        else:
            print "Info: CX system is running in %s mode" %self.sys_mode
        if self.do_benchmark:
            print "####### Warning: CX_system is performing benchmarking. The Brian2 should be configured to use benchmarking."
        if self.device == 'GeNN':
            set_device('genn', directory=os.path.join(self.output_folder, self.StartTime_str[1:]))
            prefs.codegen.cpp.extra_compile_args_gcc = ['-O3', '-pipe']
        elif self.device == 'Cpp':
            set_device('cpp_standalone', directory=os.path.join(self.output_folder, self.StartTime_str[1:]))
            prefs.codegen.cpp.extra_compile_args_gcc = ['-O3', '-pipe']


    def _set_runtime(self,*args):
        assert '*' in args[0], 'Please specify the unit for the runtime parameter, e.g. um , mm '
        self.runtime = eval(args[0])

    def _set_sys_mode(self, *args):
        assert args[0] in ['local','expanded'], "System mode should be either local or expanded. "
        self.sys_mode = args[0]

    def save_generated_video_input_flag(self, *args):
        assert int(args[0]) == 0 or int(args[0]) == 1, \
            'The do_init_vm flag should be either 0 or 1 but it is %s .' % args[0]
        self.save_generated_video_input_flag = int(args[0])

    def _set_grid_radius(self, *args):
        assert '*' in args[0], 'Please specify the unit for the grid radius parameter, e.g. um , mm '
        self.general_grid_radius = eval(args[0])
        try:
            if self.scale!=1 :
                print "Info: Radius of the system scaled to %s from %s" % (str(sqrt(self.scale)*self.general_grid_radius), str(self.general_grid_radius))
            self.general_grid_radius = sqrt(self.scale)*self.general_grid_radius
            if self.sys_mode != 'expanded' and self.scale != 1:
                print '\nWARNING: system is scaled by factor of %f but the system mode is local instead of expanded\n'%(self.scale)
        except AttributeError:
            pass

    def _set_min_distance(self, *args):
        assert '*' in args[0], 'Please specify the unit for the minimum distance parameter, e.g. um , mm '
        self.min_distance = eval(args[0])

    def _set_output_path(self, *args):
        self.output_path = args[0]
        assert os.path.splitext(self.output_path)[1], "The output_path_and_filename should contain file extension (.gz, .bz2 or .pickle)"
        self.output_folder = os.path.dirname(self.output_path)
        self.output_file_extension = '.'+self.output_path.split('.')[-1]
        self.StartTime_str += '_' + self.device + '_' + str(int((self.runtime / second) * 1000)) + 'ms'
        self.save_output_data = save_data(self.output_path,self.StartTime_str)  # This is for saving the output
        self.save_output_data.creat_key('positions_all')
        self.save_output_data.creat_key('Neuron_Groups_Parameters')
        self.save_output_data.data['Anatomy_configuration'] = self.conf_df_to_save
        self.save_output_data.data['Physiology_configuration'] = self.physio_df_to_save
        self.save_output_data.data['time_vector'] = arange(0,self.runtime,defaultclock.dt)
        self.save_output_data.data['positions_all']['w_coord'] = {}
        self.save_output_data.data['positions_all']['z_coord'] = {}
        self.save_output_data.data['number_of_neurons'] = {}
        self.save_output_data.data['runtime'] = self.runtime / self.runtime._get_best_unit()
        self.save_output_data.data['sys_mode'] = self.sys_mode
        try:
            self.save_output_data.data['scale'] = self.scale
        except AttributeError:
            pass

    def _set_load_brian_data_path(self, *args):
        self.load_brian_data_path = args[0]
        assert os.path.splitext(self.load_brian_data_path)[1], "The connections_loading_path_and_filename should contain file extension (.gz, .bz2 or .pickle)"
        self.load_brian_data_filename = ntpath.basename(self.load_brian_data_path)
        self.load_brian_data_folder = ntpath.dirname(self.load_brian_data_path)
        self.load_brian_data_extension = os.path.splitext(self.load_brian_data_path)[1]
        assert any(extension in self.load_brian_data_extension for extension in ['gz','bz2','pickle']), 'The extension of the brian_data input/output ' \
                                                         'should be gz, bz2 or pickle but it is %s'%self.load_brian_data_extension
        assert os.path.isfile(os.path.abspath(self.load_brian_data_path)),\
            'The brian_data file cannot be found for loading'
        if 'gz' in self.load_brian_data_extension:
            with open(self.load_brian_data_path, 'rb') as fb:
                data = zlib.decompress(fb.read())
                self.loaded_brian_data = pickle.loads(data)
        elif 'bz2' in self.load_brian_data_extension:
            with bz2.BZ2File(self.load_brian_data_path, 'rb') as fb:
                self.loaded_brian_data = pickle.load(fb)
        elif 'pickle' in self.load_brian_data_extension:
            with open(self.load_brian_data_path, 'rb') as fb:
                self.loaded_brian_data = pickle.load(fb)
        print 'Info: brian data file loaded from %s'%os.path.abspath(self.load_brian_data_path)
        if 'scale' in self.loaded_brian_data.keys():
            self.scale = self.loaded_brian_data['scale']
            print "Info: scale of the system loaded from brian file"

    def _set_save_brian_data_path(self, *args):
        self.save_brian_data_path = args[0]
        assert os.path.splitext(self.save_brian_data_path)[1], "The connections_saving_path_and_filename should contain file extension (.gz, .bz2 or .pickle)"
        self.save_brian_data_filename = ntpath.basename(self.save_brian_data_path)
        self.save_brian_data_folder = ntpath.dirname(self.save_brian_data_path)
        self.save_brian_data_extension = os.path.splitext(self.save_brian_data_path)[1]
        assert any(extension in self.save_brian_data_extension for extension in ['gz','bz2','pickle']), 'The extension of the brian_data input/output ' \
                                                         'should be gz,bz2 or pickle, but it is %s'%self.save_brian_data_extension
        self.save_brian_data = save_data(self.save_brian_data_path,self.StartTime_str)

    def do_init_vms(self,*args):
        assert int(args[0]) == 0 or int(args[0]) == 1, \
            'The do_init_vm flag should be either 0 or 1 but it is %s .'%args[0]
        self.do_init_vms = int(args[0])
        if self.do_init_vms:
            print 'Info: Membrane voltages are being randomly initialized.'
        if not self.do_init_vms:
            print 'Info: no initialization for membrane voltages.'

    def _set_scale(self,*args):
        # if float(args[0])!=1.0:
        self.scale = float(args[0])
        if self.scale != 1 :
            print "Info: CX System is being build on the scale of %s" %args[0]

    def load_positions_only(self,*args):
        assert int(args[0]) == 0 or int(args[0]) == 1, \
            'The load_positions_only flag should be either 0 or 1 but it is %s .' % args[0]
        self.load_positions_only = int(args[0])
        if self.load_positions_only and hasattr(self,'loaded_brian_data'):
            print "Info: only positions are being loaded from the brian_data_file"

    def do_benchmark(self,*args):
        assert int(args[0]) in [0,1] , "Do benchmark flag should be either 0 or 1"
        self.do_benchmark = int(args[0])

    def neuron_group(self, *args):
        '''
        The method that creates the NeuronGroups() based on the parameters that are extracted from the configuration file in the __init__ method of the class.

        :param args: This method have at least 3 main positional arguments directly passed from the __init__ method: Number of Neurons in the group, Type of neuron in the group and layer index. Description of the layer index as well as other possible arguments can be found in the configuration file tutorial.

        Main internal variables:

        * mon_args: contains the monitor arguments extracted from the target line.
        * net_center: center position of the neuron group in visual field coordinates, description can be found in configuration file tutorial.
        * NG_name: Generated variable name for the NeuronGroup() object in brian2.
        * NN_name: Generated variable name for corresponding Neuron Number.
        * NE_name: Generated variable name for the NeuronGroup() equation.
        * NT_name: Generated variable name for the NeuronGroup() threshold.
        * NRes_name: Generated variable name for the NeuronGroup() reset value.
        * NRef_name: Generated variable name for the NeuronGroup() refractory value.
        * NNS_name: Generated variable name for the NeuronGroup() namespace.
        * NG_init: NeuronGroups() should be initialized with a random vm, ge and gi values. To address this, a 6-line code is generated and put in this variable, the running of which will lead to initialization of current NeuronGroup().
        '''
        assert self.sys_mode != '', "System mode is not defined."
        _all_columns = ['idx', 'number_of_neurons', 'neuron_type', 'layer_idx', 'threshold',
                        'reset', 'refractory', 'net_center','monitors','noise_sigma','gemean','gestd','gimean','gistd']
        _obligatory_params = [0, 1, 2, 3]
        assert len(self.current_values_list) <= len(_all_columns), 'One or more of of the columns for NeuronGroups definition \
        is missing. Following obligatory columns should be defined:\n%s\n ' \
                                                                % str([_all_columns[ii] for ii in _obligatory_params])
        obligatory_columns = list(array(_all_columns)[_obligatory_params])
        obligatory_indices = [self.current_parameters_list[self.current_parameters_list == ii].index.item() for ii in
                              obligatory_columns]
        assert not any(self.current_values_list.ix[obligatory_indices] == '--'), \
            'Following obligatory values cannot be "--":\n%s' % str([_all_columns[ii] for ii in _obligatory_params])
        assert len(self.current_values_list) == self.current_parameters_list_orig_len,\
            "One or more of of the columns for NeuronGroup definition is missing in the following line:\n %s " % str(self.anat_and_sys_conf_df.ix[self.value_line_idx].to_dict().values())
        idx = -1
        net_center = 0 + 0j
        number_of_neurons = 0
        noise_sigma = ''
        gemean = ''
        gestd = ''
        gimean = ''
        gistd = ''
        neuron_type = ''
        layer_idx = 0
        threshold = ''
        reset = ''
        refractory = ''
        monitors = ''
        for column in _all_columns:
            try:
                tmp_value_idx = self.current_parameters_list[self.current_parameters_list==column].index.item()
                exec "%s=self.current_values_list[tmp_value_idx]" % column
            except ValueError:
                exec "%s='--'" % column
        assert idx not in self.NG_indices, \
            "Error: multiple indices with same values exist in the configuration file."
        self.NG_indices.append(idx)
        if net_center == '--':
            net_center = 0 + 0j  # center position of the neuron group in visual field coordinates,
            # description can be found in configuration file tutorial.
        net_center = complex(net_center)
        current_idx = len(self.customized_neurons_list)

        # Somewhat clumsy (rushed) implementation here, will fix later
        if noise_sigma == '--':
            noise_sigma = '0*mV'
        noise_sigma = eval(noise_sigma)
        assert 'V' in str(noise_sigma._get_best_unit()), 'The unit of noise_sigma should be volt'

        if gemean == '--':
            gemean = '0*nS'
        if gestd == '--':
            gestd = '0*nS'
        if gimean == '--':
            gimean = '0*nS'
        if gistd == '--':
            gistd = '0*nS'

        if neuron_type == 'PC':  # extract the layer index of PC neurons separately
            exec 'layer_idx = array(' + layer_idx.replace('->', ',') + ')'
        try:
            number_of_neurons = str(int(int(number_of_neurons) * self.scale))
        except AttributeError:
            pass
        self.customized_neurons_list.append(customized_neuron(idx, number_of_neurons, neuron_type,
                                                  layer_idx, self.general_grid_radius, self.min_distance,self.physio_config_df,
                                                              network_center=net_center).output_neuron)  # creating a
        # customized_neuron() object and passing the positional arguments to it. The main member of the class called
        # output_neuron is then appended to customized_neurons_list.
        # in case of threshold/reset/refractory overwrite
        if threshold != '--':
            self.customized_neurons_list[-1]['threshold'] = threshold
        if reset != '--':
            self.customized_neurons_list[-1]['reset'] = reset
        if refractory != '--':
            self.customized_neurons_list[-1]['refractory'] = refractory
        # Generating variable names for Groups, NeuronNumbers, Equations, Threshold, Reset, Refractory and Namespace
        NG_name = self._NeuronGroup_prefix + str(current_idx) + '_' + neuron_type + '_L' + str(layer_idx).replace\
            (' ', 'toL').replace('[', '').replace(']', '')
        self.neurongroups_list.append(NG_name)
        NN_name = self._NeuronNumber_prefix + str(current_idx)
        NE_name = self._NeuronEquation_prefix + str(current_idx)
        NT_name = self._NeuronThreshold_prefix + str(current_idx)
        NRes_name = self._NeuronReset_prefix + str(current_idx)
        NRef_name = self._NeuronRef_prefix + str(current_idx)
        NNS_name = self._NeuronNS_prefix + str(current_idx)

        # next  6 line create the variable that are needed for current target line NeuronGroup().
        self.save_output_data.data['Neuron_Groups_Parameters'][NG_name] = self.customized_neurons_list[-1]
        self.customized_neurons_list[current_idx]['object_name'] = NG_name
        exec "%s=self.customized_neurons_list[%d]['number_of_neurons']" % (NN_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['equation']" % (NE_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['threshold']" % (NT_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['reset']" % (NRes_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['refractory']" % (NRef_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['namespace']" % (NNS_name, current_idx)
        # Adding the noise sigma to the namespace
        self.customized_neurons_list[current_idx]['namespace']['noise_sigma'] = noise_sigma
        # Adding ge/gi mean/std to the namespace
        self.customized_neurons_list[current_idx]['namespace']['gemean'] = eval(gemean)
        self.customized_neurons_list[current_idx]['namespace']['gestd'] = eval(gestd)
        self.customized_neurons_list[current_idx]['namespace']['gimean'] = eval(gimean)
        self.customized_neurons_list[current_idx]['namespace']['gistd'] = eval(gistd)

        # Creating the actual NeuronGroup() using the variables in the previous 6 lines
        exec "%s= NeuronGroup(%s, model=%s, method='%s', threshold=%s, reset=%s,refractory = %s, namespace = %s)" \
             % (NG_name, NN_name, NE_name,self.numerical_integration_method ,NT_name, NRes_name, NRef_name, NNS_name)
        # trying to load the positions in the groups
        if hasattr(self,'loaded_brian_data'):
            # in case the NG index are different.
            # for example a MC_L2 neuron might have had index 3 as NG3_MC_L2 and now it's NG10_MC_L2 :
            Group_type = NG_name[NG_name.index('_')+1:]
            GroupKeyName =[kk for kk in self.loaded_brian_data['positions_all']['w_coord'].keys() if Group_type in kk][0]
            self.customized_neurons_list[current_idx]['w_positions'] = self.loaded_brian_data['positions_all']['w_coord'][GroupKeyName]
            self.customized_neurons_list[current_idx]['z_positions'] = self.loaded_brian_data['positions_all']['z_coord'][GroupKeyName]
            print "Position for the group %s loaded" %NG_name
        # Setting the position of the neurons in the current NeuronGroup.
        try :
            exec "%s.x=real(self.customized_neurons_list[%d]['w_positions'])*mm\n%s.y=imag(self.customized_neurons_list[%d]['w_positions'])*mm" % (
                NG_name, current_idx, NG_name, current_idx)
        except ValueError as e:
            raise ValueError(e.message + '\n You are probably trying to load the positions from a file that does not contain the same number of cells.')
        # Saving the neurons' positions both in visual field and cortical coordinates in save_data() object.
        self.save_output_data.data['positions_all']['z_coord'][NG_name] = \
            self.customized_neurons_list[current_idx]['z_positions']
        self.save_output_data.data['positions_all']['w_coord'][NG_name] = \
            self.customized_neurons_list[current_idx]['w_positions']
        self.save_output_data.data['number_of_neurons'][NG_name] = eval(NN_name)
        # NeuronGroups() should be initialized with a random vm, ge and gi values.
        # To address this, a 6-line code is generated and put in NG_init variable,
        # the running of which will lead to initialization of current NeuronGroup().
        if self.do_init_vms:
            NG_init = 'Vr_offset = rand(len(%s))\n' % NG_name
            NG_init += "for _key in %s.variables.keys():\n" % NG_name
            NG_init += "\tif _key.find('vm')>=0:\n"
            NG_init += "\t\tsetattr(%s,_key,%s['Vr']+Vr_offset * (%s['VT']-%s['Vr']))\n" % \
                       (NG_name, NNS_name, NNS_name, NNS_name)
            NG_init += "\telif ((_key.find('ge')>=0) or (_key.find('gi')>=0)):\n"
            NG_init += "\t\tsetattr(%s,_key,0)" % NG_name
            exec NG_init
        else:
            NG_init = "for _key in %s.variables.keys():\n" % NG_name
            NG_init += "\tif _key.find('vm')>=0:\n"
            NG_init += "\t\tsetattr(%s,_key,%s['Vr'])\n" % (NG_name, NNS_name)
            NG_init += "\telif ((_key.find('ge')>=0) or (_key.find('gi')>=0)):\n"
            NG_init += "\t\tsetattr(%s,_key,0)" % NG_name
            exec NG_init
        setattr(self.main_module, NG_name, eval(NG_name))
        try:
            setattr(self.CX_module, NG_name, eval(NG_name))
        except AttributeError:
            pass


        # passing remainder of the arguments to monitors() method to take care of the arguments.
        self.monitors(str(monitors).split(' '), NG_name, self.customized_neurons_list[-1]['equation'])

    def monitors(self, mon_args, object_name, equation):
        '''
        This method creates the Monitors() in brian2 based on the parameters that are extracted from a target line in configuration file.

        :param mon_args: The monitor arguments extracted from the target line.
        :param object_name: The generated name of the current object.
        :param equation: The equation of the NeuronGroup() to check if the target variable exist in it.

        Main internal variables:

        * mon_tag: The tag that is extracted from the target line every time.
        * Mon_name: Generated variable name for a specific monitor.
        * Mon_str: The syntax used for building a specific StateMonitor.
        * sub_mon_tags: The tags in configuration file that are specified for a StateMonitor(), e.g. in record=True which is specified by [rec]True in configuration file, [rec] is saved in sub_mon_tags
        * sub_mon_args: The corresponding arguments of sub_mon_tags for a StateMonitor(), e.g. in record=True which is specified by [rec]True in configuration file, True is saved in sub_mon_args.
        '''
        if '--' in mon_args:
            return
        if not mon_args and not self.default_monitors:
            return
        if not mon_args:
            mon_args = self.default_monitors
        # check if default monitor should be applied or not
        if '-->' in mon_args:
            del (mon_args[mon_args.index('-->')])
            self.default_monitors = mon_args
        if '<--' in mon_args:
            del (mon_args[mon_args.index('<--')])
            if not mon_args:
                mon_args = self.default_monitors
            self.default_monitors = []

        monitor_options = {
            '[Sp]': ['SpMon', 'SpikeMonitor'],
            '[St]': ['StMon', 'StateMonitor'],
            '[dt]': [',dt='],
            '[rec]': [',record=']
        }
        self.monitor_name_bank[object_name] = []
        for mon_arg in mon_args:
            # Extracting the monitor tag
            mon_tag = mon_arg[mon_arg.index('['):mon_arg.index(']') + 1]
            assert mon_tag in monitor_options.keys(),'%s is not recognized as a type of monitor ' %mon_tag
            mon_arg = mon_arg.replace(mon_tag, '').split('+')
            for sub_mon_arg in mon_arg:  # going through each state variable:
                Mon_str = "=%s(%s" % (str(monitor_options[mon_tag][1]),
                                       object_name) # The syntax used for building a specific StateMonitor.
                sub_mon_tags = []  # The tags in configuration file that are specified for a StateMonitor(), e.g.
                # in record=True which is specified by [rec]True in configuration file, [rec] is saved in sub_mon_tags
                if not ('[' in sub_mon_arg) and sub_mon_arg != '':  # if there is no tag,
                    # it means that the only tag that should be there is record = true
                    sub_mon_arg = sub_mon_arg.split()
                    sub_mon_arg.append('True')
                    sub_mon_tags.append('[rec]')
                else:
                    tag_open_indices = [idx for idx, ltr in enumerate(sub_mon_arg) if
                                        ltr == '[']  # find the start index of all tags
                    tag_close_indices = [idx for idx, ltr in enumerate(sub_mon_arg) if
                                         ltr == ']']  # find the end index of all tags
                    assert len(tag_open_indices) == len(
                        tag_close_indices), 'Wrong sets of tagging parentheses in monitor definitions. '
                    for tag_idx in range(len(tag_open_indices)):  # go through each StateMonitor tag:
                        sub_mon_tags.append(sub_mon_arg[sub_mon_arg.index('['):sub_mon_arg.index(']') + 1])
                        sub_mon_arg = sub_mon_arg.replace(sub_mon_tags[tag_idx], ' ')
                    sub_mon_arg = sub_mon_arg.split(' ')
                    if '[rec]' not in sub_mon_tags and sub_mon_arg != ['']:
                        # if some tags exist and [rec] is not present, it means record=True
                        sub_mon_tags.append('[rec]')
                        sub_mon_arg.append('True')
                    elif '[rec]' in sub_mon_tags:
                        sub_mon_arg[sub_mon_tags.index('[rec]')+1] = 'arange'+ sub_mon_arg[sub_mon_tags.index('[rec]')+1].replace('-', ',')
                        if self.scale >= 1:
                            assert int(sub_mon_arg[sub_mon_tags.index('[rec]')+1].split(',')[1]) < \
                                   self.customized_neurons_list[-1]['number_of_neurons'], \
                                "The stop index (%d) in the following monitor, is higher than the number of neurons in the group (%d): \n %s " %(int(sub_mon_arg[sub_mon_tags.index('[rec]')+1].split(',')[1]),self.customized_neurons_list[-1]['number_of_neurons'],str(self.current_values_list.tolist()),)
                        elif int(sub_mon_arg[sub_mon_tags.index('[rec]')+1].split(',')[1]) < self.customized_neurons_list[-1]['number_of_neurons']:
                            "\n Warning: The stop index (%d) in the following monitor, is higher than the number of neurons in the group (%d): \n %s . This is caused by using a scale < 1" % (
                            int(sub_mon_arg[sub_mon_tags.index('[rec]') + 1].split(',')[1]),
                            self.customized_neurons_list[-1]['number_of_neurons'],
                            str(self.current_values_list.tolist()),)


                    assert len(sub_mon_arg) == len(sub_mon_tags) + 1, 'Error in monitor tag definition.'
                if sub_mon_arg[0] == '':
                    assert mon_tag == '[Sp]', 'The monitor state variable is not defined properly'
                    self.save_output_data.creat_key('spikes_all')  # Create a key in save_data() object
                    # for that specific StateMonitor variable.
                    Mon_name = monitor_options[mon_tag][0] + str(self.monitor_idx) + '_' + object_name
                    self.save_output_data.syntax_bank.append(
                        "self.save_output_data.data['spikes_all']['%s'] = asarray(%s.it)" % (object_name, Mon_name))
                    Mon_str = Mon_name + Mon_str
                else:
                    self.save_output_data.creat_key('%s_all' % sub_mon_arg[0])  # Create a key in save_data()
                    # object for that specific StateMonitor variable.
                    Mon_name = monitor_options[mon_tag][0] + \
                        str(self.monitor_idx) + '_' + object_name + '__' + sub_mon_arg[0]
                    # After simulation, the following syntax will be used to save this specific monitor's result:
                    self.save_output_data.syntax_bank.append("self.save_output_data.data['%s_all']"
                                                             "['%s'] = asarray(%s.%s)"
                                                             %(sub_mon_arg[0], object_name, Mon_name, sub_mon_arg[0]))
                    Mon_str = Mon_name + Mon_str + ",'" + sub_mon_arg[0] + "'"
                    del (sub_mon_arg[0])
                    # add each of the tag and their argument,
                    # e.g. "record" as tag and "True" as argument, to the Mon_str syntax string.
                    for idx, tag in enumerate(sub_mon_tags):
                        Mon_str += monitor_options[tag][0] + sub_mon_arg[idx]

                self.monitor_name_bank[object_name].append(Mon_name)
                Mon_str += ')'
                # create the Monitor() object
                exec Mon_str
                setattr(self.main_module, Mon_name, eval(Mon_name))
                try:
                    setattr(self.CX_module, Mon_name, eval(Mon_name))
                except AttributeError:
                    pass
                self.monitor_idx += 1

    def synapse(self, *args):
        '''
        The method that creates the Synapses() in brian2, based on the parameters that are extracted from the configuration file in the __init__ method of the class.

        :param args: This method will have at least 4 main positional arguments directly passed from __init__ method: The receptor, e.g. ge or gi, pre-synaptic NeuronGroup index, post synaptic group index, and type of Synaptic connection , i.e. STDP or Fixed. Description of other possible arguments can be found in Configuration file tutorial.

        Main internal variables:

        * mon_args: contains the monitor arguments extracted from the target line.
        * args: normally args contains a set of arguments for a single Synapses() object. However, this changes when the post-synaptic neuron is the first (with index of 0) compartment of a multi-compartmental neuron. In this case, one might intend to target all three sub-compartments, i.e. Basal dendrites, Soma and proximal apical dendrites. So the single set of arguments will be changed to 3 sets of arguments and a for loop will take care of every one of them.
        * S_name: Generated variable name for the Synapses() object in brian2.
        * SE_name: Generated variable name for the Synapses() equation.
        * SPre_name: Generated variable name for pre_synaptic equations, i.e. "on_pre=..."
        * SPost_name: Generated variable name for post_synaptic equations, i.e. "on_post= ..."
        * SNS_name: Generated variable name for the Synapses() namespace.
        * syn_con_str: The string containing the syntax for connect() method of a current Synapses() object. This string changes depending on using the [p] and [n] tags in the configuration file.
        '''
        _all_columns = ['receptor', 'pre_syn_idx', 'post_syn_idx', 'syn_type', 'p', 'n', 'monitors','load_connection',\
                        'save_connection']
        _obligatory_params = [0, 1, 2, 3]
        assert len(self.current_values_list) <= len(_all_columns), \
            'One or more of the obligatory columns for input definition is missing. Obligatory columns are:\n%s\n ' \
                                                                % str([_all_columns[ii] for ii in _obligatory_params])
        obligatory_columns = list(array(_all_columns)[_obligatory_params])
        obligatory_indices = [self.current_parameters_list[self.current_parameters_list == ii].index.item() for ii in
                              obligatory_columns]
        assert not any(self.current_values_list.ix[obligatory_indices].isnull()), \
            'Following obligatory values cannot be "--":\n%s' % str([_all_columns[ii] for ii in _obligatory_params])
        assert len(self.current_values_list) == self.current_parameters_list_orig_len, \
        "One or more of of the columns for synapse definition is missing in the following line:\n %s " %str(self.anat_and_sys_conf_df.ix[self.value_line_idx].to_dict().values())
        _options = {
            '[C]': self.neuron_group,
        }
        # getting the connection probability gain from the namespace and apply it on all the connections:
        index_of_receptor = int(where(self.current_parameters_list.values == 'receptor')[0])
        index_of_post_syn_idx = int(where(self.current_parameters_list.values == 'post_syn_idx')[0])
        index_of_pre_syn_idx = int(where(self.current_parameters_list.values=='pre_syn_idx')[0])
        index_of_syn_type = int(where(self.current_parameters_list.values=='syn_type')[0])
        try:
            index_of_p = int(where(self.current_parameters_list.values == 'p')[0])
        except TypeError:
            pass
        try:
            index_of_n = int(where(self.current_parameters_list.values == 'n')[0])
        except TypeError:
            pass
        try:
            index_of_monitors = int(where(self.current_parameters_list.values == 'monitors')[0])
        except TypeError:
            pass
        current_post_syn_idx = self.current_values_list.values[index_of_post_syn_idx]
        current_pre_syn_idx = self.current_values_list.values[index_of_pre_syn_idx]
        try:
            _current_probs = self.current_values_list.values[index_of_p]
        except (ValueError,NameError):
            pass
        try:
            _current_ns = self.current_values_list.values[index_of_n]
        except (ValueError,NameError):
            pass
        # When the post-synaptic neuron is a multi-compartmental PC neuron:
        if len(current_post_syn_idx) > 1 and '[' in current_post_syn_idx:
            try:
                _current_probs = map(float, _current_probs.split('+'))
            except NameError:
                pass
            except ValueError:
                assert _current_probs == '--', \
                    "When targeting multiple compartments near soma, their probability should be defined separately. Unless it's marked as '--'"
            try:
                _current_ns = map(float,_current_ns.split('+'))
            except NameError:
                pass
            except ValueError:
                assert _current_ns == '--', \
                    "When targeting multiple compartments near soma, their number of connections, i.e. 'n', should be defined separately. Unless it's marked as '--'"

            current_post_syn_tags = current_post_syn_idx[current_post_syn_idx.index('['):current_post_syn_idx.index(']') + 1]
            assert current_post_syn_tags in _options.keys(), \
                'The synaptic tag %s is not defined.'% current_post_syn_tags
            if current_post_syn_tags == '[C]':  # [C] means the target is a compartment
                _post_group_idx, _post_com_idx = current_post_syn_idx.split('[' + 'C' + ']')
                assert int(_post_group_idx) < len(self.neurongroups_list),\
                'The synapse in the following line is targeting a group index that is not defined:\n%s'%str(self.anat_and_sys_conf_df.ix[self.value_line_idx].to_dict().values())
                self.current_values_list.values[index_of_post_syn_idx] = _post_group_idx
                pre_group_ref_idx = [self.customized_neurons_list.index(tmp_group) for tmp_group in
                                     self.customized_neurons_list if tmp_group['idx'] == int(current_pre_syn_idx)][0]
                post_group_ref_idx = [self.customized_neurons_list.index(tmp_group) for tmp_group in
                                      self.customized_neurons_list if tmp_group['idx'] == int(_post_group_idx)][0]
                assert self.customized_neurons_list[post_group_ref_idx]['type'] == 'PC', \
                    'A compartment is targeted but the neuron group is not PC. Check Synapses in the configuration file.'
                _pre_type = self.customized_neurons_list[pre_group_ref_idx]['type']  # Pre-synaptic neuron type
                _post_type = self.customized_neurons_list[post_group_ref_idx]['type']  # Post-synaptic neuron type
                self.current_parameters_list = self.current_parameters_list.append(pandas.Series(['pre_type', 'post_type','post_comp_name']),ignore_index=True)
                self.current_values_list = self.current_values_list.append(pandas.Series([_pre_type, _post_type]), ignore_index=True)
                #  In case the target is from compartment 0 which has 3 compartments itself
                if str(_post_com_idx)[0] == '0':
                    assert len(_post_com_idx) > 1, \
                        'A soma of a compartmental neuron is being targeted, but the exact compartment in the soma is not defined. After 0, use "b" for basal dendrites, "s" for soma and "a" for apical dendrites.'
                    if _current_probs != '--':
                        assert len(_post_com_idx[1:]) == len(_current_probs) , \
                            "When targeting multiple compartments near soma, their probability, i.e. 'p', should be defined separately. Unless it's marked as '--'"
                    if _current_ns != '--':
                        assert len(_post_com_idx[1:]) == len(_current_ns), \
                            "When targeting multiple compartments near soma, their number of connections, i.e. 'n', should be defined separately. Unless it's marked as '--'"
                    # creating the required synapses for targeting compartment 0, it can be at most 3 synapses (basal,
                    # soma or apical), hence the name triple_args
                    triple_args = []
                    for idx, tmp_idx in enumerate(_post_com_idx[1:]):
                        tmp_args = list(self.current_values_list)
                        if any(self.current_parameters_list.str.contains('p')):
                            tmp_args[index_of_p] = _current_probs[idx] if \
                                str(tmp_args[index_of_p])!= '--' else '--'
                        if any(self.current_parameters_list.str.contains('n')):
                            tmp_args[index_of_n] = _current_ns[idx] if \
                                str(tmp_args[index_of_n])!= '--' else '--'
                        if tmp_idx == 'b':
                            tmp_args.append('_basal')
                            triple_args.append(tmp_args)
                        elif tmp_idx == 's':
                            tmp_args.append('_soma')
                            triple_args.append(tmp_args)
                        elif tmp_idx == 'a':
                            tmp_args.append('_a0')
                            triple_args.append(tmp_args)
                    self.current_values_list = triple_args
                elif int(_post_com_idx) > 0:
                    self.current_values_list = self.current_values_list.append(pandas.Series(['_a' + str(_post_com_idx)]), ignore_index = True)
            if type(self.current_values_list[0]) != list : # type of self.current_values_list[0] would be list in case
                # of multiple synaptic targets in soma area
                self.current_values_list = [self.current_values_list]
        else:
            assert int(current_post_syn_idx) < len(self.neurongroups_list), \
                'The synapse in the following line is targeting a group index that is not defined:\n%s' % str(self.anat_and_sys_conf_df.ix[self.value_line_idx].to_dict().values())
            pre_group_ref_idx = [self.customized_neurons_list.index(tmp_group) for tmp_group in \
                                 self.customized_neurons_list if int(tmp_group['idx']) == \
                                 int(current_pre_syn_idx)][0]
            post_group_ref_idx = [self.customized_neurons_list.index(tmp_group) for tmp_group in \
                                  self.customized_neurons_list if int(tmp_group['idx']) == \
                                  int(current_post_syn_idx)][0]
            _pre_type = self.customized_neurons_list[pre_group_ref_idx]['type']   # Pre-synaptic neuron type
            _post_type = self.customized_neurons_list[post_group_ref_idx]['type']  # Post-synaptic neuron type
            assert _post_type!= 'PC', \
            'The post_synaptic group is a multi-compartmental PC but the target compartment is not selected. Use [C] tag followed by compartment number.'
            self.current_values_list = self.current_values_list.append(pandas.Series([_pre_type, _post_type,'_soma']), ignore_index=True)
            self.current_parameters_list = self.current_parameters_list.append(pandas.Series(['pre_type', 'post_type','post_comp_name']), ignore_index=True)
            self.current_values_list = [self.current_values_list]
        for syn in self.current_values_list:
            receptor = syn[index_of_receptor]
            pre_syn_idx = syn[index_of_pre_syn_idx]
            post_syn_idx = syn[index_of_post_syn_idx]
            syn_type = syn[index_of_syn_type]
            try:
                p_arg = float(syn[index_of_p])*self.conn_prob_gain
            except (ValueError,NameError):
                p_arg = '--'
            try:
                n_arg = syn[index_of_n]
            except (ValueError,NameError):
                n_arg = '--'
            try:
                monitors = syn[index_of_monitors]
            except (ValueError, NameError):
                monitors = '--'
            pre_type = syn[self.current_parameters_list[self.current_parameters_list=='pre_type'].index.item()]
            post_type = syn[self.current_parameters_list[self.current_parameters_list=='post_type'].index.item()]
            post_comp_name= syn[self.current_parameters_list[self.current_parameters_list=='post_comp_name'].index.item()]
            # check monitors in line:
            current_idx = len(self.customized_synapses_list)
            # creating a customized_synapse object and passing the positional arguments to it. The main member of
            # the class called output_synapse is then appended to customized_synapses_list:
            self.customized_synapses_list.append(customized_synapse(receptor, pre_syn_idx, post_syn_idx, syn_type,
                                                                 pre_type, post_type,self.physio_config_df ,post_comp_name).output_synapse)
            _pre_group_idx = self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']]
            _post_group_idx = self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']]
            # Generated variable name for the Synapses(), equation, pre_synaptic and post_synaptic equation and Namespace
            S_name = self._Synapses_prefix + str(current_idx) + '_' + syn_type
            self.synapses_name_list.append(S_name)
            SE_name = self._SynapsesEquation_prefix + str(current_idx)
            SPre_name = self._SynapsesPre_prefix + str(current_idx)
            SPost_name = self._SynapsesPost_prefix + str(current_idx)
            SNS_name = self._SynapsesNS_prefix + str(current_idx)

            exec "%s=self.customized_synapses_list[%d]['equation']" % (SE_name, current_idx)
            exec "%s=self.customized_synapses_list[%d]['pre_eq']" % (SPre_name, current_idx)
            try:  # in case of a fixed synapse there is no "on_post = ...", hence the pass
                exec "%s=self.customized_synapses_list[%d]['post_eq']" % (SPost_name, current_idx)
            except KeyError:
                pass
            exec "%s=self.customized_synapses_list[%d]['namespace']" % (SNS_name, current_idx)

            ### creating the initial synaptic connection :
            try:
                exec "%s = Synapses(%s,%s,model = %s, on_pre = %s, on_post = %s, namespace= %s)" \
                     % (S_name, _pre_group_idx, _post_group_idx, SE_name,SPre_name, SPost_name, SNS_name)
            except NameError:  # for when there is no "on_post =...", i.e. fixed connection
                exec "%s = Synapses(%s,%s,model = %s, on_pre = %s, namespace= %s)" \
                     % (S_name, _pre_group_idx, _post_group_idx,SE_name, SPre_name, SNS_name)

            ###############
            ############### Connecting synapses
            ###############

            _syn_ref_name = self.neurongroups_list[int(current_pre_syn_idx)][self.neurongroups_list[int( \
                current_pre_syn_idx)].index('_')+1:] + "__to__" + self.neurongroups_list[self.\
                customized_synapses_list[-1]['post_group_idx']][self.neurongroups_list[self.\
                customized_synapses_list[-1]['post_group_idx']].index('_') + 1:] + \
                            self.customized_synapses_list[-1]['post_comp_name']
            try:
                index_of_load_connection = int(where(self.current_parameters_list.values == 'load_connection')[0])
                if '-->' in syn[index_of_load_connection ]:
                    self.default_load_flag = int(syn[index_of_load_connection ].replace('-->',''))
                elif '<--' in syn[index_of_load_connection ]:
                    self.default_load_flag = -1
                    _do_load = int(syn[index_of_load_connection ].replace('<--', ''))
                    if _do_load ==1:
                        assert hasattr(self,'loaded_brian_data'), "Synaptic connection in the following line is set to be loaded, however the load_brian_data_path is not defined in the parameters. The connection is being created:\n%s"%str(self.anat_and_sys_conf_df.ix[self.value_line_idx].to_dict().values())
                else:
                    _do_load = int(syn[self.current_parameters_list[self.current_parameters_list=='load_connection'].index.item()])
            except TypeError:
                pass

            try:
                index_of_save_connection = int(where(self.current_parameters_list.values=='save_connection')[0])
                if '-->' in syn[index_of_save_connection]:
                    self.default_save_flag = int(syn[index_of_save_connection].replace('-->',''))
                elif '<--' in syn[index_of_save_connection]:
                    self.default_save_flag = -1
                    _do_save = int(syn[index_of_save_connection].replace('<--', ''))
                else:
                    _do_save = int(syn[index_of_save_connection])
            except TypeError:
                pass

            if (self.default_load_flag==1 or (self.default_load_flag==-1 and _do_load == 1 )) and \
                    hasattr(self,'loaded_brian_data') and not self.load_positions_only:
                assert _syn_ref_name in self.loaded_brian_data.keys(), \
                    "The data for the following connection was not found in the loaded brian data: %s" % _syn_ref_name
                eval(S_name).connect(i=self.loaded_brian_data[_syn_ref_name]['data'][0][0].tocoo().row, \
                                     j=self.loaded_brian_data[_syn_ref_name]['data'][0][0].tocoo().col,\
                                     n = int(self.loaded_brian_data[_syn_ref_name]['n']))
                eval(S_name).wght = repeat(self.loaded_brian_data[_syn_ref_name]['data'][0][0].data/int(self.\
                    loaded_brian_data[_syn_ref_name]['n']),int(self.loaded_brian_data[_syn_ref_name]['n'])) * siemens
                _load_str = 'Connection loaded from '

            elif (self.default_load_flag==1 or (self.default_load_flag==-1 and _do_load == 1 )) and not \
                    hasattr(self,'loaded_brian_data') :
                print "Warning: synaptic connection is set to be loaded, however the load_brian_data_path is not defined in the parameters. The connection is being created."

            else:
                syn_con_str = "%s.connect('i!=j', p= " % S_name
                # Connecting the synapses based on either [the defined probability and the distance] or
                # [only the distance] plus considering the number of connections
                try:
                    if self.sys_mode == 'local':
                        syn_con_str += "'%f'" % float(p_arg)
                    elif self.sys_mode == 'expanded':
                        # syn_con_str += "'%f*exp(-((sqrt((x_pre-x_post)**2+(y_pre-y_post)**2))*%f))/(sqrt((x_pre-x_post) \
                        #    **2+(y_pre-y_post)**2)/mm)'   " % (float(p_arg), self.customized_synapses_list[-1]['ilam'])
                        syn_con_str += "'%f*exp(-((sqrt((x_pre-x_post)**2+(y_pre-y_post)**2))*%f))'" % (
                        float(p_arg), self.customized_synapses_list[-1]['ilam']) # todo the divisoin by the distance is temporarily removed to avoid division by zeros, try to understand what is going on using Hanna's email and if it's needed, add a fixed version

                except ValueError:
                    p_arg = self.customized_synapses_list[-1]['sparseness']
                    if '_relay_vpm' in self.neurongroups_list[int(current_pre_syn_idx)]:
                        syn_con_str += "'%f*exp(-((sqrt((x_pre-x_post)**2+(y_pre-y_post)**2)))/(2*0.025**2))'" \
                                       % (float(p_arg))
                    elif self.sys_mode == 'local':
                        syn_con_str += "'%f'" % p_arg
                    elif self.sys_mode == 'expanded':
                        # syn_con_str += "'%f*exp(-((sqrt((x_pre-x_post)**2+(y_pre-y_post)**2))*%f))/(sqrt((x_pre-x_post)\
                        # **2+(y_pre-y_post)**2)/mm)'   " % (p_arg, self.customized_synapses_list[-1]['ilam'])
                        syn_con_str += "'%f*exp(-((sqrt((x_pre-x_post)**2+(y_pre-y_post)**2))*%f))'" % (
                        p_arg, self.customized_synapses_list[-1]['ilam']) # todo the divisoin by the distance is temporarily removed to avoid division by zeros, try to understand what is going on using Hanna's email and if it's needed, add a fixed version
                try:
                    syn_con_str += ',n=%d)' % int(n_arg)
                except ValueError:
                    syn_con_str += ')'
                exec syn_con_str
            exec "%s.wght=%s['wght0']" % (S_name, SNS_name)  # set the weights
            exec "%s.delay=%s['delay']" % (S_name, SNS_name)  # set the delays
            setattr(self.main_module, S_name, eval(S_name))
            try:
                setattr(self.CX_module, S_name, eval(S_name))
            except AttributeError:
                pass

            self.monitors(monitors.split(' '), S_name, self.customized_synapses_list[-1]['equation'])

            if self.device == 'Python' :
                num_tmp = 0
                exec "num_tmp = len(%s.i)" % S_name
                self.total_number_of_synapses += num_tmp
                try:
                    _current_connections = int(num_tmp/float(syn[self.current_parameters_list[self.current_parameters_list=='n'].index.item()])) / len(self.current_values_list)
                except ValueError:
                    print "\nWarning: number of synapses for last connection was equal to number of connections\n"
                    _current_connections = num_tmp
                self.total_number_of_connections += _current_connections
                try:
                    print "%s%s to %s: Number of synapses %d \t Number of connections: %d \t Total synapses: %d \t " "Total connections: %d" \
                          %(_load_str ,_pre_group_idx, _post_group_idx,num_tmp,_current_connections, \
                            self.total_number_of_synapses, self.total_number_of_connections)
                except (ValueError, UnboundLocalError):
                    print "Connection created from %s to %s: Number of synapses %d \t Number of connections: %d \t Total synapses: %d \t Total connections: %d" \
                      % (_pre_group_idx, _post_group_idx, num_tmp, _current_connections, \
                         self.total_number_of_synapses, self.total_number_of_connections)
            else:
                try:
                    print "%s%s to %s" %(_load_str ,_pre_group_idx, _post_group_idx)
                except UnboundLocalError:
                    print "Connection created from %s to %s" % ( _pre_group_idx, _post_group_idx)
            if (self.default_save_flag == 1 or (self.default_save_flag == -1 and _do_save )) and \
                    hasattr(self, 'save_brian_data_path') :
                self.do_save_connections = 1
                self.save_brian_data.creat_key(_syn_ref_name)
                self.save_brian_data.syntax_bank.append('self.save_brian_data.data["%s"]["data"] = \
                csr_matrix((%s.wght[:],(%s.i[:],%s.j[:])),shape=(len(%s.source),len(%s.target)))' \
                                                        %(_syn_ref_name,S_name,S_name,S_name,S_name,S_name))
                self.save_brian_data.syntax_bank.append('self.save_brian_data.data["%s"]["n"] = %d' \
                                                        %(_syn_ref_name,int(n_arg)))
            elif (self.default_save_flag==1 or (self.default_save_flag==-1 and _do_save )) and \
                    not hasattr(self,'save_brian_data_path') :
                raise ValueError("Synaptic connection is set to be saved, however the save_brian_data_path parameter is not defined.")

    def relay(self, *args):
        '''
        The method that creates the relay NeuronGroups based on the parameters that are extracted from the configuration \
        file in the __init__ method of the class. Note that the SpikeGeneratorGroup() does not support the locations and \
        synaptic connection based on the distance between the input, and the target neuron group. For this reason, a "relay"\
         neuron group is created which is directly connected to the SpikeGeneratorGroup(). Unlike SpikeGeneratorGroup() this \
        relay group supports the locations. With this workaround, the synaptic connection between the input and the Neuron group can be implemented \
        based on the distance of the neurons then.

        Note: extracting the input spikes and time sequences for using in a SpikeGeneratorGroup() is done in this method. \
        This procedure needs using a "run()" method in brian2. However, one of the limitations of the Brian2GeNN is that \
        the user cannot use multiple "run()" methods in the whole script. To address this issue, the GeNN device should be \
        set after using the first run(), hence the unusual placement of "set_device('genn')" command in current method.

        Note2: The radius of the VPM input is determined based on the Markram et al. 2015: The radius of the system is 210 um \
        and the number of VPM input is 60 (page 19 of supplements). As for the radius of the VPM input, it is mentioned in the \
         paper (page 462) that "neurons were arranged in 310 mini-columns at horizontal positions". considering the area of the \
         circle with radius of 210um and 60/310 mini-columns, the radius will be equal to 92um.

        :param args: This method will have at least 4 main positional arguments directly passed from __init__ method: path to the input .mat file, and the frequency. Description of other possible arguments can be found in Configuration file tutorial.

        Main internal variables:

        * inp: an instance of stimuli() object from stimuli module.
        * relay_group: the dictionary containing the data for relay NeuronGroup()
        * NG_name: Generated variable name for the NeuronGroup() object in brian2.
        * NN_name: Generated variable name for corresponding Neuron Number.
        * NE_name: Generated variable name for the NeuronGroup() equation.
        * NT_name: Generated variable name for the NeuronGroup() threshold.
        * NRes_name: Generated variable name for the NeuronGroup() reset value.
        * SGsyn_name: variable name for the Synapses() object that connects SpikeGeneratorGroup() and relay neurons.

        following four variables are build using the load_input_seq() method in stimuli object:

        * spikes_str: The string containing the syntax for Spike indices in the input neuron group.
        * times_str: The string containing the syntax for time indices in the input neuron group.
        * SG_str: The string containing the syntax for creating the SpikeGeneratorGroup() based on the input .mat file.
        * number_of_neurons: The number of neurons that exist in the input .mat file.
        '''
        NG_name = ''
        def video(self):
            print "creating an input based on the video input."
            input_mat_path = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='path'].index.item()]
            freq = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='freq'].index.item()]
            inp = stimuli(duration=self.runtime,input_mat_path=input_mat_path,output_folder=self.output_folder, \
                          output_file_extension = self.output_file_extension,
                          save_generated_input_flag = self.save_generated_video_input_flag)
            proc = multiprocessing.Process(target=inp.generate_inputs, args=(freq,))
            proc.start()
            self.video_input_idx =len(self.neurongroups_list)
            self.neurongroups_list.append('awaiting_video_group')

            def waitress(self):
                time.sleep(3)
                while proc.is_alive():
                    time.sleep(1)
                SPK_GENERATOR_SP, SPK_GENERATOR_TI, thread_number_of_neurons = inp.load_input_seq(self.output_folder)
                SPK_GENERATOR = SpikeGeneratorGroup(thread_number_of_neurons , SPK_GENERATOR_SP, SPK_GENERATOR_TI)
                setattr(self.main_module, 'SPK_GENERATOR', SPK_GENERATOR)
                try:
                    setattr(self.CX_module, 'SPK_GENERATOR', SPK_GENERATOR)
                except AttributeError:
                    pass
                # Generated variable name for the NeuronGroup, Neuron_number,Equation, Threshold, Reset
                thread_NG_name = self._NeuronGroup_prefix + str(self.video_input_idx) + '_relay_video'
                self.neurongroups_list[self.video_input_idx] = thread_NG_name
                thread_NN_name = self._NeuronNumber_prefix + str(self.video_input_idx)
                thread_NE_name = self._NeuronEquation_prefix + str(self.video_input_idx)
                thread_NT_name = self._NeuronThreshold_prefix + str(self.video_input_idx)
                thread_NRes_name = self._NeuronReset_prefix + str(self.video_input_idx)
                Eq = """'''emit_spike : 1
                    x : meter
                    y : meter'''"""
                # In order to use the dynamic compiler in a sub-routine, the scope in which the syntax is going to be run
                # should be defined, hence the globals(), locals(). They indicate that the syntaxes should be run in both
                # global and local scope
                exec "%s=%s" % (thread_NN_name, thread_number_of_neurons) in globals(), locals()
                exec "%s=%s" % (thread_NE_name, Eq) in globals(), locals()
                exec "%s=%s" % (thread_NT_name, "'emit_spike>=1'") in globals(), locals()
                exec "%s=%s" % (thread_NRes_name, "'emit_spike=0'") in globals(), locals()
                exec "%s= NeuronGroup(%s, model=%s,method='%s', threshold=%s, reset=%s)" \
                     % (thread_NG_name, thread_NN_name, thread_NE_name, self.numerical_integration_method,thread_NT_name, thread_NRes_name) in globals(), locals()
                if hasattr(self, 'loaded_brian_data'):
                    # in case the NG index are different. for example a MC_L2 neuron might have had
                    # index 3 as NG3_MC_L2 and now it's NG10_MC_L2 :
                    thread_Group_type = thread_NG_name[thread_NG_name.index('_') + 1:]
                    thread_GroupKeyName = \
                    [kk for kk in self.loaded_brian_data['positions_all']['w_coord'].keys() if thread_Group_type in kk][0]
                    self.customized_neurons_list[self.video_input_idx]['w_positions'] = \
                    self.loaded_brian_data['positions_all']['w_coord'][thread_GroupKeyName]
                    self.customized_neurons_list[self.video_input_idx]['z_positions'] = \
                    self.loaded_brian_data['positions_all']['z_coord'][thread_GroupKeyName]
                    print "Position for the group %s loaded" % thread_NG_name
                else: # load the positions:
                    self.customized_neurons_list[self.video_input_idx]['z_positions'] = squeeze(inp.get_input_positions())
                    self.customized_neurons_list[self.video_input_idx]['w_positions'] = 17 * log(relay_group['z_positions'] + 1)

                # setting the position of the neurons based on the positions in the .mat input file:
                exec "%s.x=real(self.customized_neurons_list[%d]['w_positions'])*mm\n" \
                     "%s.y=imag(self.customized_neurons_list[%d]['w_positions'])*mm" % \
                     (thread_NG_name, self.video_input_idx, thread_NG_name, self.video_input_idx) in globals(), locals()
                self.save_output_data.data['positions_all']['z_coord'][thread_NG_name] = \
                    self.customized_neurons_list[self.video_input_idx]['z_positions']
                self.save_output_data.data['positions_all']['w_coord'][thread_NG_name] = \
                    self.customized_neurons_list[self.video_input_idx]['w_positions']
                self.save_output_data.data['number_of_neurons'][thread_NG_name] = eval(thread_NN_name)
                thread_SGsyn_name = 'SGEN_Syn' # variable name for the Synapses() object
                # that connects SpikeGeneratorGroup() and relay neurons.
                exec "%s = Synapses(SPK_GENERATOR, %s, on_pre='emit_spike+=1')" % \
                     (thread_SGsyn_name, thread_NG_name) in globals(), locals()# connecting the SpikeGeneratorGroup() and relay group.
                exec "%s.connect(j='i')" % thread_SGsyn_name in globals(), locals() # SV change
                setattr(self.main_module, thread_NG_name, eval(thread_NG_name))
                setattr(self.main_module, thread_SGsyn_name, eval(thread_SGsyn_name))
                try:
                    setattr(self.CX_module, thread_NG_name, eval(thread_NG_name))
                    setattr(self.CX_module, thread_SGsyn_name, eval(thread_SGsyn_name))
                except AttributeError:
                    pass
                # taking care of the monitors:
                self.monitors(mons.split(' '), thread_NG_name, self.customized_neurons_list[-1]['equation'])

            input_neuron_group_idx = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='idx'].index.item()]
            syn_lines = self.anat_and_sys_conf_df[self.anat_and_sys_conf_df[0].str.startswith('S') == True]
            input_synaptic_lines = syn_lines[syn_lines[2] == '0']
            row_type_lines = self.anat_and_sys_conf_df.loc[:input_synaptic_lines.index[0]][0].str.startswith('row_type') == True
            synapse_def_line = self.anat_and_sys_conf_df.loc[row_type_lines[row_type_lines == True].index[-1]]
            load_conn_idx = synapse_def_line[synapse_def_line=='load_connection'].index[0]
            save_conn_idx = synapse_def_line[synapse_def_line=='save_connection'].index[0]
            for conn_load_item in input_synaptic_lines[load_conn_idx]:
                if '<--' in conn_load_item or '-->' in conn_load_item:
                    for synaptic_row in range(input_synaptic_lines.index[0]+1 , self.anat_and_sys_conf_df[0].index[-1]):
                        if self.anat_and_sys_conf_df.loc[synaptic_row][0][0]!='#':
                            sign_to_add = '-->' if '-->' in conn_load_item else '<--'
                            self.anat_and_sys_conf_df.loc[input_synaptic_lines.index[0]+1,load_conn_idx] += sign_to_add
                            break
            for conn_save_item in input_synaptic_lines[save_conn_idx]:
                if '<--' in conn_save_item or '-->' in conn_save_item:
                    for synaptic_row in range (input_synaptic_lines.index[0]+1 , self.anat_and_sys_conf_df[0].index[-1]):
                        if self.anat_and_sys_conf_df.loc[synaptic_row][0][0]!='#':
                            sign_to_add = '-->' if '-->' in conn_save_item else '<--'
                            self.anat_and_sys_conf_df.loc[input_synaptic_lines.index[0]+1,save_conn_idx] += sign_to_add
                            break
            self.awaited_conf_lines = synapse_def_line.to_frame().transpose().reset_index(drop=True).append(input_synaptic_lines).reset_index(drop=True)
            self.anat_and_sys_conf_df = self.anat_and_sys_conf_df.drop(input_synaptic_lines.index.tolist()).reset_index(drop=True)
            self.thr = threading.Thread(target = waitress,args=(self,))
            self.thr.start()
            if inp.file_exist_flag:
                self.thr.join()

        def VPM(self): #ventral posteromedial (VPM) thalamic nucleus
            spike_times = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='spike_times'].index.item()].replace(' ',',')
            spike_times_list = ast.literal_eval(spike_times[0:spike_times.index('*')])
            spike_times_unit = spike_times[spike_times.index('*')+1:]
            exec 'spike_times_ = spike_times_list * %s' %(spike_times_unit) in globals(), locals()
            try:
                net_center = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='net_center'].index.item()]
                net_center = complex(net_center)
            except ValueError:
                net_center = 0 + 0j
            number_of_neurons = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='number_of_neurons'].index.item()]
            radius = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='radius'].index.item()]
            print "creating an input based on the central %s neurons."%number_of_neurons
            Spikes_Name = 'GEN_SP'
            Time_Name = 'GEN_TI'
            SG_Name = 'GEN'
            spikes_str = 'GEN_SP=tile(arange(%s),%d)'%(number_of_neurons,len(spike_times_))
            times_str = 'GEN_TI = repeat(%s,%s)*%s'%(spike_times[0:spike_times.index('*')],number_of_neurons,spike_times_unit)
            SG_str = 'GEN = SpikeGeneratorGroup(%s, GEN_SP, GEN_TI)'%number_of_neurons
            exec spikes_str in globals(), locals()  # running the string containing the syntax for Spike indices in the input neuron group.
            exec times_str in globals(), locals()  # running the string containing the syntax for time indices in the input neuron group.
            exec SG_str in globals(), locals()  # running the string containing the syntax for creating the SpikeGeneratorGroup() based on the input .mat file.

            setattr(self.main_module, SG_Name, eval(SG_Name))
            try:
                setattr(self.CX_module, SG_Name, eval(SG_Name))
            except AttributeError:
                pass

            NG_name = self._NeuronGroup_prefix + str(current_idx) + '_relay_vpm'  # Generated variable name for the NeuronGroup() object in brian2.
            self.neurongroups_list.append(NG_name)
            NN_name = self._NeuronNumber_prefix + str(current_idx)  # Generated variable name for corresponding Neuron Number.
            NE_name = self._NeuronEquation_prefix + str(current_idx)  # Generated variable name for the NeuronGroup() equation.
            NT_name = self._NeuronThreshold_prefix + str(current_idx)  # Generated variable name for the NeuronGroup() threshold.
            NRes_name = self._NeuronReset_prefix + str(current_idx)  # Generated variable name for the NeuronGroup() reset value.
            Eq = """'''emit_spike : 1
                            x : meter
                            y : meter'''"""
            exec "%s=%s" % (NN_name, number_of_neurons) in globals(), locals()
            exec "%s=%s" % (NE_name, Eq) in globals(), locals()
            exec "%s=%s" % (NT_name, "'emit_spike>=1'") in globals(), locals()
            exec "%s=%s" % (NRes_name, "'emit_spike=0'") in globals(), locals()
            exec "%s= NeuronGroup(%s, model=%s, method='%s',threshold=%s, reset=%s)" \
                 % (NG_name, NN_name, NE_name, self.numerical_integration_method, NT_name, NRes_name) in globals(), locals()
            if hasattr(self, 'loaded_brian_data'): # load the positions if available
                # in case the NG index are different. for example a MC_L2 neuron might have had
                # index 3 as NG3_MC_L2 and now it's NG10_MC_L2 :
                Group_type = NG_name[NG_name.index('_') + 1:]
                GroupKeyName = \
                [kk for kk in self.loaded_brian_data['positions_all']['w_coord'].keys() if Group_type in kk][0]
                self.customized_neurons_list[current_idx]['w_positions'] = self.loaded_brian_data['positions_all']['w_coord'][GroupKeyName]
                self.customized_neurons_list[current_idx]['z_positions'] = self.loaded_brian_data['positions_all']['z_coord'][GroupKeyName]
                print "Positions for the group %s loaded" % NG_name
            else: # generating the positions:
                vpm_customized_neuron = customized_neuron(current_idx, int(number_of_neurons), 'VPM', '0', eval(radius),
                                                          self.min_distance, self.physio_config_df ,network_center=net_center)
                self.customized_neurons_list[current_idx]['z_positions'] = vpm_customized_neuron.output_neuron[
                    'z_positions']
                self.customized_neurons_list[current_idx]['w_positions'] = vpm_customized_neuron.output_neuron[
                    'w_positions']
            # setting the position of the neurons:
            exec "%s.x=real(self.customized_neurons_list[%d]['w_positions'])*mm\n"\
                 "%s.y=imag(self.customized_neurons_list[%d]['w_positions'])*mm" \
                 %(NG_name, current_idx, NG_name, current_idx) in globals(), locals()
            # saving the positions :
            self.save_output_data.data['positions_all']['z_coord'][NG_name] = \
                self.customized_neurons_list[current_idx]['z_positions']
            self.save_output_data.data['positions_all']['w_coord'][NG_name] = \
                self.customized_neurons_list[current_idx]['w_positions']
            self.save_output_data.data['number_of_neurons'][NG_name] = eval(NN_name)
            SGsyn_name = 'SGEN_Syn'  # variable name for the Synapses() object
            # that connects SpikeGeneratorGroup() and relay neurons.
            exec "%s = Synapses(GEN, %s, on_pre='emit_spike+=1')" \
                 % (SGsyn_name, NG_name) in globals(), locals()  # connecting the SpikeGeneratorGroup() and relay group.
            eval(SGsyn_name).connect(j='i')
            setattr(self.main_module, NG_name, eval(NG_name))
            setattr(self.main_module, SGsyn_name, eval(SGsyn_name))
            try:
                setattr(self.CX_module, NG_name, eval(NG_name))
                setattr(self.CX_module, SGsyn_name, eval(SGsyn_name))
            except AttributeError:
                pass
            # taking care of the monitors:
            self.monitors(mons.split(' '), NG_name,self.customized_neurons_list[-1]['equation'])

        assert self.sys_mode != '', "Error: System mode not defined."
        assert any(self.current_parameters_list.str.contains('type')), 'The type of the input is not defined in the configuration file.'
        _input_params = {
            'video': [['idx', 'type', 'path','freq', 'monitors'], [0, 1, 2], video],
            'VPM': [['idx', 'type', 'number_of_neurons', 'radius', 'spike_times', 'net_center', 'monitors'],
                    [0, 1, 2, 3, 4], VPM]
        }
        _input_type = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='type'].index.item()]
        _all_columns = _input_params[_input_type][0] # all possible columns of parameters for the current type of input in configuration fil
        assert _input_type in _input_params.keys(), 'The input type %s of the configuration file is ' \
            'not defined' % _input_type

        _obligatory_params = _input_params[_input_type][1]
        assert len(self.current_values_list) >= len(_obligatory_params), \
            'One or more of of the columns for input definition is missing. Following obligatory columns should be defined:\n%s\n' % str(
            [_all_columns[ii] for ii in _obligatory_params])
        assert len (self.current_parameters_list) <= len(_input_params[_input_type][0]), 'Too many parameters for the\
         current %s input. The parameters should be consist of:\n %s'%(_input_type,_input_params[_input_type][0])
        obligatory_columns = list(array(_input_params[_input_type][0])[_input_params[_input_type][1]])
        obligatory_indices = [self.current_parameters_list[self.current_parameters_list==ii].index.item() for ii in obligatory_columns]
        assert not any(self.current_values_list.ix[obligatory_indices]=='--'), \
            'Following obligatory values cannot be "--":\n%s' % str([_all_columns[ii] for ii in _obligatory_params])
        assert len(self.current_parameters_list) == len(self.current_values_list), \
            'The number of columns for the input are not equal to number of values in the configuration file.'
        try:
            mons = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='monitors'].index.item()]
        except ValueError:
            mons = '--'
        group_idx = self.current_values_list[self.current_parameters_list[self.current_parameters_list=='idx'].index.item()]

        assert group_idx not in self.NG_indices, \
            "Error: multiple indices with same values exist in the configuration file."
        self.NG_indices.append(group_idx)
        current_idx = len(self.customized_neurons_list)
        relay_group = {}
        relay_group['idx'] = int(group_idx)
        relay_group['type'] = 'in'
        relay_group['z_positions'] = []
        relay_group['w_positions'] = []
        relay_group['equation'] = ''
        self.customized_neurons_list.append(relay_group)
        _input_params[_input_type][2](self)


    def gather_result(self):
        '''
        After the simulation and using the syntaxes that are previously prepared in the syntax_bank of save_data() object, this method saves the collected data to a file.

        '''
        print "Generating the syntaxes for saving CX output."
        for syntax in self.save_output_data.syntax_bank:
            exec syntax
        self.save_output_data.save_to_file()
        if hasattr(self,'save_brian_data') and self.do_save_connections:
            print "Generating the syntaxes for saving connection data."
            for syntax in self.save_brian_data.syntax_bank:
                exec syntax
            self.save_brian_data.creat_key('positions_all')
            self.save_brian_data.data['positions_all']['w_coord'] = self.save_output_data.data['positions_all']['w_coord']
            self.save_brian_data.data['positions_all']['z_coord'] = self.save_output_data.data['positions_all']['z_coord']
            self.save_brian_data.save_to_file()

    def visualise_connectivity(self,S):
        Ns = len(S.source)
        Nt = len(S.target)
        figure(figsize=(10, 4))
        subplot(121)
        plot(zeros(Ns), arange(Ns), 'ok', ms=10)
        plot(ones(Nt), arange(Nt), 'ok', ms=10)
        for i, j in zip(S.i, S.j):
            plot([0, 1], [i, j], '-k')
        xticks([0, 1], ['Source', 'Target'])
        ylabel('Neuron index')

    def multi_y_plotter(self,ax, len, variable,item,title):

        for i in range(len):
            tmp_str = 'ax.plot(item.t/ms, item.%s[%d])'%(variable,i);exec tmp_str
            tmp_str = "ax.set_title('%s')" % (title);exec tmp_str


if __name__ == '__main__' :
    # CM = cortical_system(os.path.dirname(os.path.realpath(__file__)) + '/LightConfigForTesting.csv', device = 'Python' , runtime=1000* ms)
    # CM.run()
    # CM = cortical_system(os.path.dirname(os.path.realpath(__file__)) + '/LightConfigForTesting.csv', device='Cpp',runtime=1000 * ms)
    # CM.run()
    CM = cortical_system(os.path.dirname(os.path.realpath(__file__)) + '/Markram_config_file.csv', \
                         os.path.dirname(os.path.realpath(__file__)) + '/Physiological_Parameters.csv',) # runtime and device are now set in configuration file
    CM.run()
