import brian2_obj_defs

__author__ = 'V_AD'
from brian_genn_version  import *
import brian2genn
import os
import sys
from brian2_obj_defs import *
from Plotter import *
from save_data import *
from stimuli import *
import ast
import copy # for copying Equation object

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

    def __init__(self, config_path, save_path, use_genn=0):
        '''
        Initialize the cortical system by parsing the configuration file.

        :param config_path: The path to the configuration file.
        :param save_path: The path to save the final data.
        :param use_genn: switch the GeNN mode on/off (1/0), by default genn is off

        Main internal variables:


        * customized_neurons_list: This list contains the customized_neuron instances. So for each neuron group target line, there would be an element in this list which contains all the information for that particular neuron group.
        * customized_synapses_list: This list contains the customized_synapse instances. Hence, for each synapse custom line, there would be an element in this list, containing all the necessary information.
        * neurongroups_list: This list contains name of the NeuronGroup() instances that are placed in the Globals().
        * synapses_name_list: This list contains name of the Synapses() instances that are placed in the Globals().
        * monitor_name_bank: The dictionary containing the name of the monitors that are defined for any NeuronGroup() or Synapses().
        * default_monitors: In case --> and <-- symbols are used in the configuration file, this default monitor will be applied on all the target lines in between those marks.
        * save_data: The save_data() object for saving the final data.

        '''
        self.use_genn = use_genn
        self._options = {
            'G': self.neuron_group,
            'S': self.synapse,
            'IN': self.relay,
            'total_synapses': self._set_total_synapses,
            'sys_mode': self._set_sys_mode, # either "local" or "expanded"
            'params': self.set_runtime_parameters,
            'do_optimize' : self._set_do_optimize,

        }
        self.current_parameters_list = []
        self.current_values_list = []
        self.NG_indices = []
        self.customized_neurons_list = []  # This list contains the customized_neuron instances. So for each neuron group target line, there would be an element in this list which contains all the information for that particular neuron group.
        self.customized_synapses_list = []  # This list contains the customized_synapse instances. Hence, for each synapse custom line, there would be an element in this list, containing all the necessary information.
        self.neurongroups_list = []  # This list contains name of the NeuronGroup() instances that are placed in the Globals().
        self.synapses_name_list = []  # This list contains name of the Synapses() instances that are placed in the Globals().
        self.synapses_perc_list = [] # This list contains percentages of the Synapses() instances that are placed in the Globals().
        self.monitor_name_bank = {}  # The dictionary containing the name of the monitors that are defined for any NeuronGroup() or Synapses().
        self.default_monitors = []  # In case --> and <-- symbols are used in the configuration file, this default monitor will be applied on all the target lines in between those marks.
        self.monitor_idx = 0
        self.save_data = save_data(save_path)  # The save_data() object for saving the final data.
        self.save_data.creat_key('positions_all')
        self.save_data.data['positions_all']['w_coord'] = {}
        self.save_data.data['positions_all']['z_coord'] = {}
        self.total_synapses = 0
        self.sys_mode = ''
        self.config_path = config_path
        self.optimized_probabilities = []
        self.total_number_of_synapses = 0

        with open(self.config_path, 'r') as f:
            for self.line in f:
                self.line = self.line.replace('\n', '')
                self.line = self.line.lstrip()
                if 'do_optimize' in self.line or self.line[0:6] == 'params':
                    _splitted_line = [non_empty.strip() for non_empty in self.line.split(',') if non_empty != '']
                    if 'row_type' in self.line:
                        self.current_parameters_list = _splitted_line[1:]
                    elif _splitted_line[0] in self._options:
                        self.current_values_list = _splitted_line[1:]
                        self._options[_splitted_line[0]]()

        if os.path.isfile(os.path.abspath('./generated_connections.csv')) and self.do_optimize == 1:
            var = ''
            while var != 'Y' and var != 'N':
                var = raw_input("Optimized file already exist, Overwrite?(Y/N) ")
            if var == 'Y':
                generated_file_name = './generated_connections.csv'
            elif var == 'N':
                sure = ''
                while sure != 'Y':
                    generated_file_name = raw_input("Enter the file name: ")
                    generated_file_name = generated_file_name .replace('.csv','') if '.csv' in generated_file_name else generated_file_name
                    while sure != 'Y' and sure != 'N':
                        sure = raw_input("Are you sure?(Y/N) ")

        with open(self.config_path, 'r') as f:  # Here is the configuration file parser.
            if self.do_optimize:
                with open(os.path.abspath("./generated_connections.csv"), 'w') as new_file:
                    for self.line in f:
                        self.line = self.line.replace('\n', '')
                        self.line = self.line.lstrip()
                        try:
                            if self.line[0] == '#' or not self.line.split(','): # comments
                                continue
                        except:
                            continue
                        _splitted_line = [non_empty.strip() for non_empty in self.line.split(',') if non_empty != '']
                        if 'row_type' in self.line:
                            self.current_parameters_list = _splitted_line[1:]
                        elif _splitted_line[0] in self._options:
                            self.current_values_list = _splitted_line[1:]
                            self._options[_splitted_line[0]]()
                        new_file.write(self.line + "\n")
            else:
                for self.line in f:
                    self.line = self.line.replace('\n', '')
                    self.line = self.line.lstrip()
                    try:
                        if self.line[0] == '#' or not self.line.split(','):  # comments
                            continue
                    except:
                        continue
                    _splitted_line = [non_empty.strip() for non_empty in self.line.split(',') if non_empty != '']
                    if 'row_type' in self.line:
                        self.current_parameters_list = _splitted_line[1:]
                    elif _splitted_line[0] in self._options:
                        self.current_values_list = _splitted_line[1:]
                        self._options[_splitted_line[0]]()


        if self.sys_mode != '' and self.do_optimize:
            assert len(self.synapses_name_list) == len(self.synapses_perc_list), "When the percentage for a synapse is defined, it should be defined for all others as well. Error: One or more synaptses percentages are missing"
            assert sum(map(float,self.synapses_perc_list)) == 1 , "Error: the percentage of the synapses does not sum up to 1"
            # if self.optimization_notfound ==1 :
            #     with open(self.config_path, "a") as f:
            #         f.write("\noptimized_probabilities: %s"%(','.join(str(x) for x in self.optimized_probabilities)))
            #     print "optimized percentages saved in the configuration file, you can now use them and change the mode to expanded"
        if self.do_optimize == 1:
            sys.exit("Execution Compeleted. the synapses are optimized based on their percentages and the new connection file is generated. Use the name of the new configuration file to re-run the program.")
        print "Cortical Module initialization Done."

    def set_runtime_parameters(self):
        for idx,parameter in enumerate(self.current_parameters_list):
            assert parameter in self._options.keys(), 'The tag %s is not defined.' % parameter
            self._options[parameter](self.current_values_list[idx])
        if self.sys_mode == '':
            print "Warning: system mode is not defined. "

    def _set_total_synapses(self,*args):
        self.total_synapses = int(args[0])

    def _set_sys_mode(self,*args):
        self.sys_mode = args[0]

    def _set_do_optimize(self,*args):
        self.do_optimize = int(args[0])
        tmp_idx = self.current_parameters_list.index('do_optimize')
        indices = [i for i, ltr in enumerate(self.line) if ltr == ',']
        try:
            self.line = self.line[:indices[tmp_idx] + 1] + self.line[indices[tmp_idx] + 1:indices[tmp_idx + 1]].replace(
            '1', str(0)) + self.line[indices[tmp_idx + 1]:]
        except:
            self.line = self.line[:indices[tmp_idx] + 1] + self.line[indices[tmp_idx] + 1:].replace('1', str(0))
        if self.do_optimize :
            print "Info: Probabilities are going to be optimized based on their percentages and the result is save in a new file. do_optimize flag set to zero."
        # if self.do_optimize == 1:
        #     self.optimization_notfound = 1
        #     with open(self.config_path, "rb") as f:
        #         f.seek(-2, 2)  # Jump to the second last byte.
        #         while f.read(1) != b"\n":  # Until EOL is found...
        #             f.seek(-2, 1)  # ...jump back the read byte plus one more.
        #         last_line = f.readline()
        #     if "optimized_probabilities:" in last_line:
        #         last_line = last_line.replace("optimized_probabilities:", "")
        #         self.optimized_probabilities = last_line.split(',')
        #         self.optimization_notfound = 0


    def neuron_group(self, *args):
        '''
        The method that creates the NeuronGroups() based on the parameters that are extracted from the configuraiton file in the __init__ method of the class.

        :param args: This method have at least 3 main positional argumenst directly passed from the __init__ method: Number of Neurons in the group, Type of neuron in the group and layer index. Description of the layer index as well as other possible arguments can be found in the configuration file tutorial.

        Main internal variables:

        * mon_args: contains the monitor arguments extracted from the target line.
        * net_center: center position of the neuron group in visual field coordinates, description can be found in configuration file tutorial.
        * NG_name: Generated vriable name for the NeuonGroup() object in brian2.
        * NN_name: Generated vriable name for corresponding Neuron Number.
        * NE_name: Generated vriable name for the NeuonGroup() equation.
        * NT_name: Generated vriable name for the NeuonGroup() threshold.
        * NRes_name: Generated vriable name for the NeuonGroup() reset value.
        * NRef_name: Generated vriable name for the NeuonGroup() refractory value.
        * NNS_name: Generated vriable name for the NeuonGroup() namespace.
        * NG_init: NeuronGroups() should be initialized with a random vm, ge and gi values. To address this, a 6-line code is generated and put in this variable, the running of which will lead to initialization of current NeuronGroup().
        '''
        assert self.sys_mode != '', "Error: System mode not defined."
        _all_columns = ['idx','number_of_neurons','neuron_type','layer_idx','threshold','reset','refractory','net_center','monitors']
        _obligatory_params = [0,1,2,3]
        assert len(self.current_values_list) <= len(_all_columns), 'One or more of of the columns for input definition \
        is missing. Following obligatory columns should be defined:\n%s\n ' \
                                                                   % str([_all_columns[ii] for ii in _obligatory_params])
        assert 'N/A' not in [self.current_values_list[ii] for ii in
                             _obligatory_params], 'Following obligatory values cannot be "N/A":\n%s'% str([_all_columns[ii] for ii in _obligatory_params])
        # args = args[0]
        # mon_args = []  # contains the monitor arguments extracted from the target line.
        idx = -1
        net_center = 0 + 0j
        number_of_neurons = 0
        neuron_type = ''
        layer_idx = 0
        threshold = ''
        reset =''
        refractory = ''
        monitors = ''
        for column in _all_columns:
            try:
                exec "%s=self.current_values_list[self.current_parameters_list.index('%s')]"%(column,column)
            except:
                exec "%s='N/A'" %column
        if net_center == 'N/A':
            net_center = 0 + 0j  # center position of the neuron group in visual field coordinates, description can be found in configuration file tutorial.
        net_center = complex(net_center)
        # if '[M]' in args:  # check if target line contains monitors
        #     mon_args = args[args.index('[M]') + 1:]
        #     args = args[0:args.index('[M]')]
        # if '[CN]' in args:  # check if target line contains center position.
        #     net_center = complex(args[args.index('[CN]') + 1])
        #     args = args[0:args.index('[CN]')]
        current_idx = len(self.customized_neurons_list)
        if neuron_type == 'PC':  # extract the layer index of PC neurons separately (since it is in form of a list like [4,1]
            exec 'layer_idx = array(' + layer_idx.replace('->',',') + ')'
        self.customized_neurons_list.append(customized_neuron(idx,number_of_neurons,neuron_type, layer_idx,
                                                              network_center=net_center).output_neuron)  # creating a customized_neuron() object and passing the positional arguments to it. The main member of the class called output_neuron is then appended to customized_neurons_list.
      # in case of threshold/reset/refractory overwrite
        if threshold != 'N/A':
            self.customized_neurons_list[-1]['threshold'] = threshold
        if reset != 'N/A' :
            self.customized_neurons_list[-1]['reset'] = reset
        if refractory != 'N/A':
            self.customized_neurons_list[-1]['refractory'] =refractory
        NG_name = self._NeuronGroup_prefix + str(current_idx) + '_' + neuron_type  # Generated vriable name for the NeuonGroup().
        self.neurongroups_list.append(NG_name)
        NN_name = self._NeuronNumber_prefix + str(current_idx)  # Generated vriable name for corresponding Neuron Number.
        NE_name = self._NeuronEquation_prefix + str(current_idx)  # Generated vriable name for the NeuonGroup() equation.
        NT_name = self._NeuronThreshold_prefix + str(current_idx)  # Generated vriable name for the NeuonGroup() threshold.
        NRes_name = self._NeuronReset_prefix + str(current_idx)  # Generated vriable name for the NeuonGroup() reset value.
        NRef_name = self._NeuronRef_prefix + str(current_idx)  # Generated vriable name for the NeuonGroup() refractory value.
        NNS_name = self._NeuronNS_prefix + str(current_idx)  # Generated vriable name for the NeuonGroup() namespace.
        # NPos_name = self._NeuronPos_prefix + str(current_idx)
        # self.monitor_name_bank['NeuroGroups'].append(NG_name)

        # next  6 line create the variable that are needed for current target line NeuronGroup().
        exec "%s=self.customized_neurons_list[%d]['number_of_neurons']" % (NN_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['equation']" % (NE_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['threshold']" % (NT_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['reset']" % (NRes_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['refractory']" % (NRef_name, current_idx)
        exec "%s=self.customized_neurons_list[%d]['namespace']" % (NNS_name, current_idx)
        # Creating the actual NeuronGroup() using the variables in the previous 6 lines
        exec "%s= NeuronGroup(%s, model=%s, threshold=%s, reset=%s,refractory = %s, namespace = %s)" \
             % (NG_name, NN_name, NE_name, NT_name, NRes_name, NRef_name, NNS_name)
        # Setting the position of the neurons in the current Neurong Group.
        exec "%s.x=real(self.customized_neurons_list[%d]['w_positions'])*mm\n%s.y=imag(self.customized_neurons_list[%d]['w_positions'])*mm" % (
            NG_name, current_idx, NG_name, current_idx)

        # Saving the neurons' positions both in visual field and cortical coordinates in save_data() object.
        self.save_data.data['positions_all']['z_coord'][NG_name] = self.customized_neurons_list[current_idx]['z_positions']
        self.save_data.data['positions_all']['w_coord'][NG_name] = self.customized_neurons_list[current_idx]['w_positions']

        # NeuronGroups() should be initialized with a random vm, ge and gi values. To address this, a 6-line code is generated and put in NG_init variable, the running of which will lead to initialization of current NeuronGroup().
        NG_init = 'Vr_offset = rand(len(%s))\n' % NG_name
        NG_init += "for _key in %s.variables.keys():\n" % NG_name
        NG_init += "\tif _key.find('vm')>=0:\n"
        NG_init += "\t\tsetattr(%s,_key,%s['Vr']+Vr_offset * (%s['VT']-%s['Vr']))\n" % (NG_name, NNS_name, NNS_name, NNS_name)
        NG_init += "\telif ((_key.find('ge')>=0) or (_key.find('gi')>=0)):\n"
        NG_init += "\t\tsetattr(%s,_key,0)" % NG_name
        exec NG_init
        # updating the Globals()
        exec "globals().update({'%s':%s,'%s':%s,'%s':%s,'%s':%s,'%s':%s,'%s':%s,'%s':%s})" % \
            (NN_name, NN_name, NE_name, NE_name, NT_name, NT_name, NRes_name, NRes_name, NRef_name, NRef_name, NNS_name,
             NNS_name, NG_name, NG_name)
        # passing remainder of the arguments to monitors() method to take care of the arguments.
        self.monitors(monitors.split(' '), NG_name, self.customized_neurons_list[-1]['equation'])

    def monitors(self, mon_args, object_name, equation):
        '''
        This method creates the Monitors() in brian2 based on the parameters that are extracted from a target line in configuraiton file.

        :param mon_args: The monitor arguments extracted from the target line.
        :param object_name: The generated name of the current object.
        :param equation: The equation of the NeuronGroup() to check if the target variable exist in it.

        Main internal variables:

        * mon_tag: The tag that is extracted from the target line everytime.
        * Mon_name: Generated variable name for a specific monitor.
        * Mon_str: The syntax used for building a specific StateMonitor.
        * sub_mon_tags: The tags in configuration file that are specified for a StateMonitor(), e.g. in record=True which is specified by [rec]True in configuration file, [rec] is saved in sub_mon_tags
        * sub_mon_args: The corresponding arguments of sub_mon_tags for a StateMonitor(), e.g. in record=True which is specified by [rec]True in configuration file, True is saved in sub_mon_args.
        '''
        if 'N/A' in mon_args:
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
            assert mon_tag in monitor_options.keys(),'Error: %s is not recognized as a type of monitor ' %mon_tag
            mon_arg = mon_arg.replace(mon_tag, '')
            if mon_tag == '[Sp]':  # This is for SpikeMonitor()s
                # If there is a spike monitor, a spikes_all field is added to the save_data() object.
                self.save_data.creat_key('spikes_all')
                Mon_name = monitor_options['[Sp]'][0] + str(
                    self.monitor_idx) + '_' + object_name  # Generated variable name for a specific monitor.
                self.save_data.syntax_bank.append("self.save_data.data['spikes_all']['%s'] = %s.it" % (object_name,
                                                                                                       Mon_name))  # After simulation, this syntax will be used to save this specific monitor's result.
                self.monitor_name_bank[object_name].append(Mon_name)
                # build the monitor object based on the generated name:
                exec "%s=%s(%s)" % (Mon_name, monitor_options['[Sp]'][1], object_name)
                # update the Globals():
                exec "globals().update({'%s':%s})" % (Mon_name, Mon_name)
                # update monitor index:
                self.monitor_idx += 1
            else:  # Work on StateMonitors() :
                # Split the StateMonitors if there are multiple of them separated by a "+" :
                mon_arg = mon_arg.split('+')
                for sub_mon_arg in mon_arg:  # going through each state variable:
                    Mon_str = "=%s(%s," % (str(monitor_options[mon_tag][1]),
                                           object_name)  # The syntax used for building a specific StateMonitor.
                    sub_mon_tags = []  # The tags in configuration file that are specified for a StateMonitor(), e.g. in record=True which is specified by [rec]True in configuration file, [rec] is saved in sub_mon_tags
                    if not ('[' in sub_mon_arg):  # if there is no tag, it means that the only tag that should be there is record = true
                        sub_mon_arg = sub_mon_arg.split()
                        sub_mon_arg.append('True')
                        sub_mon_tags.append('[rec]')
                        # Mon_name = monitor_options['[St]'][0] + str(self.monitor_idx) + '_' + object_name + '_' + \
                        #        sub_mon_arg
                    else:
                        tag_open_indices = [idx for idx, ltr in enumerate(sub_mon_arg) if
                                            ltr == '[']  # find the start index of all tags
                        tag_close_indices = [idx for idx, ltr in enumerate(sub_mon_arg) if
                                             ltr == ']']  # find the end index of all tags
                        assert len(tag_open_indices) == len(
                            tag_close_indices), 'Error: wrong sets of tagging paranteses in monitor definitoins. '
                        for tag_idx in range(len(tag_open_indices)):  # go through each StateMonitor tag:
                            sub_mon_tags.append(sub_mon_arg[sub_mon_arg.index('['):sub_mon_arg.index(']') + 1])
                            sub_mon_arg = sub_mon_arg.replace(sub_mon_tags[tag_idx], ' ')
                        sub_mon_arg = sub_mon_arg.split(' ')
                        if not '[rec]' in sub_mon_tags:  # if some tags exist and [rec] is not present, it means record=True
                            sub_mon_tags.append('[rec]')
                            sub_mon_arg.append('True')
                        else:
                            sub_mon_arg[sub_mon_tags.index('[rec]')+1] = 'arange'+ sub_mon_arg[sub_mon_tags.index('[rec]')+1].replace('-',',')
                        assert len(sub_mon_arg) == len(sub_mon_tags) + 1, 'Error in monitor tag definition.'
                    self.save_data.creat_key('%s_all' % sub_mon_arg[
                        0])  # Create a key in save_data() object for that specific StateMonitor variable.
                    Mon_name = monitor_options['[St]'][0] + str(self.monitor_idx) + '_' + object_name + '__' + \
                               sub_mon_arg[0]
                    self.save_data.syntax_bank.append("self.save_data.data['%s_all']['%s'] = asarray(%s.%s)" % (
                    sub_mon_arg[0], object_name, Mon_name, sub_mon_arg[
                        0]))  # After simulation, this syntax will be used to save this specific monitor's result.

                    self.monitor_name_bank[object_name].append(Mon_name)
                    Mon_str = Mon_name + Mon_str + "'" + sub_mon_arg[0] + "'"
                    # check if the variable exist in the equation:
                    if ('d' + sub_mon_arg[0]) in str(equation):
                        assert (sub_mon_arg[0] + '/') in str(equation), \
                            'The monitor varibale %s is not defined in the equation.' % sub_mon_arg[0]
                    else:
                        assert (sub_mon_arg[0]) in str(equation), \
                            'The monitor varibale %s is not defined in the equation.' % sub_mon_arg[0]
                    del (sub_mon_arg[0])
                    # add each of the tag and their argument, e.g. "record" as tag and "True" as argument, to the Mon_str syntax string.
                    for idx, tag in enumerate(sub_mon_tags):
                        Mon_str += monitor_options[tag][0] + sub_mon_arg[idx]
                    Mon_str += ')'
                    # create the Monitor() object
                    exec Mon_str
                    # Update the Globals()
                    exec "globals().update({'%s':%s})" % (Mon_name, Mon_name)
                    self.monitor_idx += 1

    def synapse(self, *args):
        '''
        The method that creates the Synapses() in brian2, based on the parameters that are extracted from the configuraiton file in the __init__ method of the class.

        :param args: This method will have at least 4 main positional argumenst directly passed from __init__ method: The receptor, e.g. ge or gi, presynaptic neurong group index, post synaptic group index, and type of Synaptic connection , i.e. STDP or Fixed. Description of other possible arguments can be found in Configuration file tutorial.

        Main internal variables:

        * mon_args: contains the monitor arguments extracted from the target line.
        * args: normally args contains a set of arguments for a single Synapses() object. However, this changes when the post-synaptic neuron is the first (with index of 0) compartment of a multi-compartmental neuron. In this case, one might intend to target all three subcompartments, i.e. Basal dendrites, Soma and proximal apical dendrites. So the single set of arguments will be changed to 3 sets of arguments and a for loop will take care of every one of them.
        * S_name: Generated vriable name for the Synapses() object in brian2.
        * SE_name: Generated vriable name for the Synapses() equation.
        * SPre_name: Generated variable name for pre_synaptic equations, i.e. "pre=..."
        * SPost_name: Generated variable name for post_synaptic equations, i.e. "post= ..."
        * SNS_name: Generated vriable name for the Synapses() namespace.
        * syn_con_str: The string containing the sytanct for connect() method of a current Synapses() object. This string changes depending on using the [p] and [n] tags in the configuration file.
        '''
        _all_columns = ['receptor','pre_syn_idx','post_syn_idx','syn_type','p','n','monitors','percentage']
        _obligatory_params = [0, 1, 2, 3]
        assert len(self.current_values_list) <= len(_all_columns), 'One or more of of the columns for input definition \
            is missing. Following obligatory columns should be defined:\n%s\n ' \
                                                                   % str([_all_columns[ii] for ii in _obligatory_params])
        assert 'N/A' not in [self.current_values_list[ii] for ii in
                             _obligatory_params], 'Following obligatory values cannot be "N/A":\n%s' % str(
            [_all_columns[ii] for ii in _obligatory_params])

        _options = {
            '[C]': self.neuron_group,
        }

        # try:
        #     perc_arg = args[0][args[0].index('[%]') + 1:]
        #     args = list(args)
        #     args[0] = args[0][0:args[0].index('[%]')]
        #     args = tuple(args)
        # except:
        #     assert self.sys_mode == '', "Error: You have defined the system mode, however the percentages of the synapses are not defined in the synaptic definitions."
        #     pass
        # try: # extracting the monitors
        #     mon_args = args[0][args[0].index('[M]') + 1:]
        #     args = list(args)
        #     args[0] = args[0][0:args[0].index('[M]')]
        #     args = tuple(args)
        # except:
        #     pass
        # try:  # extracting the number of connection in a synapse (n)
        #     n_arg = args[0][args[0].index('[n]') + 1:args[0].index('[n]') + 2][0]
        #     args = list(args)
        #     args[0] = args[0][0:args[0].index('[n]')]
        #     args = tuple(args)
        # except:
        #     pass
        # try:  # extracting the probability (p)
        #     p_arg = args[0][args[0].index('[p]') + 1:args[0].index('[p]') + 2][0]
        #     args = list(args)
        #     args[0] = args[0][0:args[0].index('[p]')]
        #     args = tuple(args)
        # except:
        #     try:
        #         p_arg = self.optimized_probabilities[len(self.customized_synapses_list)]
        #     except:
        #         pass

        if len(self.current_values_list[self.current_parameters_list.index('post_syn_idx')]) > 1 and '[' in self.current_values_list[self.current_parameters_list.index('post_syn_idx')]:  # This if is for when the post-synaptic neuron is a \
            # multicompartmental PC neuon, the rules are described in the configuration file description.
            try :
                self.synapses_perc_list.extend(map(float,self.current_values_list[self.current_parameters_list.index('percentage')].split('+')))
                _current_percs = map(float,self.current_values_list[self.current_parameters_list.index('percentage')].split('+'))
            except:
                try:
                    _current_percs = float(self.current_values_list[self.current_parameters_list.index('percentage')])
                    self.synapses_perc_list.append(float(self.current_values_list[self.current_parameters_list.index('percentage')]))
                except:
                    _current_percs = []
                    try:
                        assert (self.current_values_list[self.current_parameters_list.index('percentage')] == 'N/A'), "when targetting multiple comparments near some, their percentage should be defined separately and especifically. Unless it's marked as 'N/A'"
                        _current_percs = 'N/A'
                    except:
                        assert self.do_optimize == 0, "Error: if ther percentages in the synapses are not defined, the do_optimize should be set to 0. "
            # if len(_current_percs) > 1 :
            try:
                _current_probs = map(float,self.current_values_list[self.current_parameters_list.index('p')].split('+'))

            except:
                try:
                    assert self.current_values_list[self.current_parameters_list.index('p')] == 'N/A', "when targetting multiple comparments near some, their probabilitiy should be defined separately and especifically. Unless it's marked as 'N/A'"
                    _current_probs = 'N/A'
                except:
                    assert 'p' not in self.current_parameters_list
            try:
                _current_ns = map(float,self.current_values_list[self.current_parameters_list.index('n')].split('+'))
            except:
                try:
                    assert self.current_values_list[self.current_parameters_list.index('n')] == 'N/A', "when targetting multiple comparments near some, their number of connections 'n' should be defined separately and especifically. Unless it's marked as 'N/A'"
                    _current_ns = 'N/A'
                except:
                    assert 'n' not in self.current_parameters_list
            arg = self.current_values_list[self.current_parameters_list.index('post_syn_idx')]  # post-synaptic target layer index
            tag = arg[arg.index('['):arg.index(']') + 1]  # extracting the tag
            assert tag in _options.keys(), 'The synaptic tag %s is not defined.' % tag
            if tag == '[C]':  # [C] means the target is a compartment
                _post_group_idx, _post_com_idx = arg.split('[' + 'C' + ']')
                self.current_values_list[self.current_parameters_list.index('post_syn_idx')] = _post_group_idx
                pre_group_ref_idx = [self.customized_neurons_list.index(gr) for gr in self.customized_neurons_list if
                                      gr['idx'] == int(self.current_values_list[self.current_parameters_list.index('pre_syn_idx')])][0]
                post_group_ref_idx =  [self.customized_neurons_list.index(gr) for gr in self.customized_neurons_list if
                                       gr['idx'] == int(self.current_values_list[self.current_parameters_list.index('post_syn_idx')])][0]
                assert self.customized_neurons_list[post_group_ref_idx]['type'] == 'PC', \
                    'A compartment is targetted but the neuron geroup is not PC. Check Synapses in the configuration file.'
                _pre_type = self.customized_neurons_list[pre_group_ref_idx]['type']  # Pre-synaptic neuron type
                _post_type = self.customized_neurons_list[post_group_ref_idx]['type']  # Post-synaptic neuron type
                self.current_parameters_list.extend(['pre_type', 'post_type','post_comp_name'])
                self.current_values_list.extend([_pre_type, _post_type])
                if str(_post_com_idx)[0] == '0':  # this is in case the target is from compartment 0 which has 3 compartments itself (Description in configuration file tutorial).
                    assert len(_post_com_idx) > 1, 'Error: a soma of a compartmental neuron is being targeted but the exact compartment in the soma is not defined. After 0, use "b" for basal dendrites, "s" for soma and "a" for apical dendrites.'

                    # if len(_post_com_idx) == 1:
                    #     triple_args = []
                    #     tmp_args = list(args[0])
                    #     tmp_args.append('_basal')
                    #     triple_args.append(tmp_args)
                    #     tmp_args = list(args[0])
                    #     tmp_args.append('_soma')
                    #     triple_args.append(tmp_args)
                    #     tmp_args = list(args[0])
                    #     tmp_args.append('_a0')
                    #     triple_args.append(tmp_args)
                    #     args = triple_args
                    # else:
                    triple_args = []
                    # if self.current_values_list[self.current_parameters_list.index('percentage')] != 'N/A':
                    #     comp_percs = self.current_values_list[self.current_parameters_list.index('percentage')].split('+')

                    for idx, tmp_idx in enumerate(_post_com_idx[1:]):
                        tmp_args = list(self.current_values_list)
                        if 'p' in self.current_parameters_list:
                            tmp_args[self.current_parameters_list.index('p')] = _current_probs[idx] if tmp_args[self.current_parameters_list.index('p')]!= 'N/A' else 'N/A'
                        if 'n' in self.current_parameters_list:
                            tmp_args[self.current_parameters_list.index('n')] = _current_ns[idx] if tmp_args[self.current_parameters_list.index('n')]!= 'N/A' else 'N/A'
                        if 'percentage' in self.current_parameters_list:
                            tmp_args[self.current_parameters_list.index('percentage')] = _current_percs[idx] if tmp_args[self.current_parameters_list.index('percentage')] != 'N/A' else 'N/A'
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
                    self.current_values_list.append('_a' + str(_post_com_idx))
            if type(self.current_values_list[0]) != list :
                self.current_values_list = [self.current_values_list]
            if 'percentage' in self.current_parameters_list and _current_percs!='N/A':
                assert len(self.current_values_list) == len(_current_percs),"Not enough percentage values are defined for a PC neuron. In a multi-compartmental PC neuron, when multiple compartments in soma are being targeted, the percentage of each of those connection should be declared separately. Check configuration file tutorial."
            # for value_set in self.current_values_list :
            #     if value_set[self.current_parameters_list.index('percentage')] != 'N/A':
            #         assert len(self.current_values_list) == self.current_values_list[self.current_parameters_list.index(['percentage'])], "Not enough percentage values are defined for a PC neuron. In a multi-compartmental PC neuron, when multiple compartments in soma are being targeted, the percentage of each of those connection should be declared separately. Check configuration file tutorial."
        else:
            try:
                _current_perc = float(self.current_values_list[self.current_parameters_list.index('percentage')])
                self.synapses_perc_list.append(_current_perc)
            except:
                _current_perc = 'N/A'
            pre_group_ref_idx = [self.customized_neurons_list.index(gr) for gr in self.customized_neurons_list if
                                     int(gr['idx']) == int(self.current_values_list[self.current_parameters_list.index('pre_syn_idx')])][0]
            post_group_ref_idx = [self.customized_neurons_list.index(gr) for gr in self.customized_neurons_list if
                              int(gr['idx']) == int(self.current_values_list[self.current_parameters_list.index('post_syn_idx')])][0]
            _pre_type = self.customized_neurons_list[pre_group_ref_idx]['type']   # Pre-synaptic neuron type
            _post_type = self.customized_neurons_list[post_group_ref_idx]['type']  # Post-synaptic neuron type
            assert _post_type!= 'PC', 'Error: The post_synaptc group is a multicompartmental PC but the target compartment is not selected. Use [C] tag. '
            self.current_values_list.extend([_pre_type, _post_type,'_soma'])
            self.current_parameters_list.extend(['pre_type', 'post_type','post_comp_name'])
            self.current_values_list = [self.current_values_list]
        for syn in self.current_values_list:
            receptor = syn[self.current_parameters_list.index('receptor')]
            pre_syn_idx = syn[self.current_parameters_list.index('pre_syn_idx')]
            post_syn_idx = syn[self.current_parameters_list.index('post_syn_idx')]
            syn_type = syn[self.current_parameters_list.index('syn_type')]
            try:
                p_arg = syn[self.current_parameters_list.index('p')]
            except:
                p_arg = 'N/A'
            try:
                n_arg = syn[self.current_parameters_list.index('n')]
            except:
                n_arg = 'N/A'
            try:
                monitors = syn[self.current_parameters_list.index('monitors')]
            except:
                monitors = 'N/A'
            try:
                percentage= syn[self.current_parameters_list.index('percentage')]
            except:
                percentage = 'N/A'
            pre_type = syn[self.current_parameters_list.index('pre_type')]
            post_type = syn[self.current_parameters_list.index('post_type')]
            post_comp_name= syn[self.current_parameters_list.index('post_comp_name')]

            # check monitors in line:
            _number_of_synapse = 0 #_number_of_synapse number of synaptic connections in the Synapses() object
            current_idx = len(self.customized_synapses_list)
            self.customized_synapses_list.append(customized_synapse( receptor, pre_syn_idx, post_syn_idx, syn_type, pre_type, post_type, post_comp_name).output_synapse)  # creating a customized_synapse object and passing the positional arguments to it. The main member of the class called output_synapse is then appended to customized_synapses_list.
            S_name = self._Synapses_prefix + str(current_idx) + '_' + syn_type  # Generated vriable name for the Synapses() object in brian2.
            self.synapses_name_list.append(S_name)
            SE_name = self._SynapsesEquation_prefix + str(current_idx)  # Generated vriable name for the Synapses() equation.
            SPre_name = self._SynapsesPre_prefix + str(current_idx)  # Generated variable name for pre_synaptic equations, i.e. "pre=..."
            SPost_name = self._SynapsesPost_prefix + str(current_idx)  # Generated variable name for post_synaptic equations, i.e. "post= ..."
            SNS_name = self._SynapsesNS_prefix + str(current_idx)  # Generated vriable name for the Synapses() namespace.

            exec "%s=self.customized_synapses_list[%d]['equation']" % (SE_name, current_idx)
            exec "%s=self.customized_synapses_list[%d]['pre_eq']" % (SPre_name, current_idx)
            try:  # in case of a fixed synapse there is no "post = ...", hence the pass
                exec "%s=self.customized_synapses_list[%d]['post_eq']" % (SPost_name, current_idx)
            except:
                pass
            exec "%s=self.customized_synapses_list[%d]['namespace']" % (SNS_name, current_idx)

            ### creating the initial synaptic connection :
            exec "eq_tmp = copy.deepcopy(%s)" % SE_name  # after passing a model equation to a Syanpses(), a new line will automatically be added to equation, e.i. lastupdate: seconds. This is to remove that specific line
            try:
                exec "%s = Synapses(%s,%s,model = eq_tmp, pre = %s, post = %s, namespace= %s)" \
                     % (S_name, self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], \
                        self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']], SPre_name,
                        SPost_name, SNS_name)
            except:  # for when there is no "post =...", i.e. fixed connection
                exec "%s = Synapses(%s,%s,model = eq_tmp, pre = %s, namespace= %s)" \
                     % (S_name, self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], \
                        self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']], SPre_name,
                        SNS_name)
            syn_con_str = "%s.connect('i!=j', p= " % S_name
            # Connecting the synapses based on either [the defined probability and the distance] or [only the distance] plus considering the number of connections
            try:
                if '_relay_vpm' in self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']]:
                    syn_con_str += "'exp(-((sqrt((x_pre-x_post)**2+(y_pre-y_post)**2))*%f)/(2*0.025**2))/(sqrt((x_pre-x_post)**2+(y_pre-y_post)**2)/mm)'   " \
                                   % (self.customized_synapses_list[-1]['ilam'])

                elif self.sys_mode== 'local':
                    syn_con_str += "'%f'" %(float(p_arg))
                    # if (p_arg != 'N/A' and n_arg!='N/A') and  percentage == 'N/A':
                    #     print "Info: Target percentage is not defined in local mode and some synapses are working based on p and n (see brian2 syanpses())."
                elif self.sys_mode == 'expanded':
                    syn_con_str += "'%f*exp(-(sqrt((x_pre-x_post)**2+(y_pre-y_post)**2))*%f)/(sqrt((x_pre-x_post)**2+(y_pre-y_post)**2)/mm)'   " \
                                   % (float(p_arg), self.customized_synapses_list[-1]['ilam'])


            except:
                p_arg = self.customized_synapses_list[-1]['sparseness']
                if self.sys_mode== 'local':
                    syn_con_str += "'%f'" %(p_arg)
                elif self.sys_mode == 'expanded' :
                    syn_con_str += "'%f*exp(-(sqrt((x_pre-x_post)**2+(y_pre-y_post)**2))*%f)/(sqrt((x_pre-x_post)**2+(y_pre-y_post)**2)/mm)'   " \
                                   % (p_arg, self.customized_synapses_list[-1]['ilam'])
            try:
                syn_con_str += ',n=%d)' % int(n_arg)
            except:
                syn_con_str += ')'
            exec syn_con_str
            exec "_number_of_synapse = len(%s.i)" % S_name #at this stage, _number_of_synapse contains the inital number of synapses.

            exec "%s.wght=%s['wght0']" % (S_name, SNS_name)  # set the weights

            try:  # update the Globals()
                exec "globals().update({'%s':%s,'%s':%s,'%s':%s,'%s':%s})" % \
                     (SE_name, SE_name, SPre_name, SPre_name, SPost_name, SPost_name, SNS_name, SNS_name)
            except:  # in case of fixed connection
                exec "globals().update({'%s':%s,'%s':%s,'%s':%s})" % \
                     (SE_name, SE_name, SPre_name, SPre_name, SNS_name, SNS_name )
            if self.sys_mode == 'local' and self.do_optimize:
                assert (p_arg == 'N/A' or p_arg == self.customized_synapses_list[-1]['sparseness']) and percentage!='N/A','Error: The system is in local mode and set to optimize the probabilities based on the percentages. In this case the probability should set to "N/A" which is not. Check the following line:\n%s'%self.line
                exec "del %s" % S_name
                try :
                    self._Synapses_Optimizer(syn,_number_of_synapse,S_name,SE_name,SPre_name,SPost_name,SNS_name,p_arg,float(percentage),n_arg)
                except NameError:
                    self._Synapses_Optimizer(syn,_number_of_synapse, S_name, SE_name, SPre_name, SPost_name,SNS_name, p_arg,float(percentage))
            else:
                exec "globals().update({'%s':%s})" % (S_name, S_name)
            exec "%s._name = 'synapses_%d'" % (S_name, current_idx + 1)
            self.monitors(monitors.split(' '), S_name,
                          self.customized_synapses_list[-1]['equation'])  # taking care of the monitors

            num_tmp = 0
            exec "num_tmp = len(%s.i)"%S_name
            self.total_number_of_synapses += num_tmp
            print "Number of synapses from %s to %s: %d \t Total number of synapses: %d" %(self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']],num_tmp, self.total_number_of_synapses)

        try:
            if 'percentage' in self.current_parameters_list:
                tmp_idx = self.current_parameters_list.index('p')
                indices = [iii for iii, ltr in enumerate(self.line) if ltr == ',']
                self.line = self.line[:indices[tmp_idx] + 1] + self.line[indices[tmp_idx] + 1:indices[tmp_idx + 1]].replace(
                    'N/A', str(self.optimized_probabilities).replace('[','').replace(']','').replace(',','+').replace("'",'').replace(" ",'')) + self.line[indices[tmp_idx + 1]:]
                self.optimized_probabilities = []
        except:
            pass
    def _Synapses_Optimizer(self,syn,_number_of_synapse,S_name,SE_name,SPre_name,SPost_name,SNS_name,p_arg,percentage,n_arg='no_n_arg' ):
        assert self.total_synapses != 0 , "System is in [local] mode and the synapses are to be optimized, but the total number of synapses are not defined."
        if n_arg == 'no_n_arg' or n_arg == 'N/A':
            del n_arg
        # self.optimization_notfound = 1
        # # check if the optimized probabtilities are already written to the file:
        # with open(self.config_path, "rb") as f:
        #     f.seek(-2, 2)  # Jump to the second last byte.
        #     while f.read(1) != b"\n":  # Until EOL is found...
        #         f.seek(-2, 1)  # ...jump back the read byte plus one more.
        #     last_line = f.readline()
        # if "optimized_probabilities:" in last_line:
        #     last_line = last_line.replace("optimized_probabilities:", "")
        #     self.optimized_probabilities = last_line.split(',')
        #     self.optimization_notfound = 0

        # if self.optimization_notfound:
        _optimization_direction = 'decrease' if _number_of_synapse > percentage * self.total_synapses else 'increase'
        constant = 0.01
        p_arg_list = []
        p_arg_list.append(p_arg)
        target_number = percentage * self.total_synapses
        while True:
            if abs((target_number - _number_of_synapse) / target_number) < 0.05:
                exec "globals().update({'%s':%s})" % (S_name, S_name)
                break
            if _optimization_direction == 'decrease':
                if _number_of_synapse < target_number:
                    self._status_printer("Change direction")
                    del p_arg_list[-1]
                    p_arg = p_arg_list[-1]
                    constant = constant/2
                else:
                    constant = constant *  2
                p_arg = str(float(p_arg) - constant) if (float(p_arg)-constant)>0 else str(float(p_arg)/2)
                p_arg_list.append(p_arg)

            elif _optimization_direction == 'increase':
                if _number_of_synapse > target_number :
                    self._status_printer("Change direction")
                    del p_arg_list[-1]
                    p_arg = p_arg_list[-1]
                    constant = constant/2
                else:
                    constant =  constant* 2
                p_arg = str(float(p_arg) + constant)
                p_arg_list.append(p_arg)

            try:
                exec "del %s" % S_name
            except:
                pass
            exec "eq_tmp = copy.deepcopy(%s)" % SE_name  # after passing a model equation to a Syanpses(), a new line will automatically be added to equation, e.i. lastupdate: seconds. This is to remove that specific line
            try:
                exec "%s = Synapses(%s,%s,model = eq_tmp, pre = %s, post = %s, namespace= %s)" \
                     % (S_name, self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], \
                        self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']], SPre_name,
                        SPost_name, SNS_name)
            except:  # for when there is no "post =...", i.e. fixed connection
                exec "%s = Synapses(%s,%s,model = eq_tmp, pre = %s, namespace= %s)" \
                     % (S_name, self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], \
                        self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']], SPre_name,
                        SNS_name)
            syn_con_str = "%s.connect('i!=j', p='" % S_name
            # Connecting the synapses based on either [the defined probability and the distance] or [only the distance] plus considering the number of connections
            try:
                syn_con_str += "%s" % (p_arg)
            except:
                p_arg = self.customized_synapses_list[-1]['sparseness']
                syn_con_str += "%f" % (p_arg)
            try:
                syn_con_str += "',n=%s)" % n_arg
            except:
                syn_con_str += "')"
            exec syn_con_str
            exec "_number_of_synapse = len(%s.i)" % S_name
            self._status_printer("probability: %s" %p_arg)
        assert 'p' in self.current_parameters_list, 'Error: probabilities are to be optimized but the "p" column is not defined in synapses definitions. '

        self.optimized_probabilities.append(p_arg)
        print "\noptimization for %s finished"%S_name
        # else:
        #     print "Warning: the CX_system is running in local mode but the percentages are already determined and saved in the configuration file . If this is not intentional, either remove the last line of configuration file to re-optimize the percentages, or change the mode to 'expanded' mode."
        #     try:
        #         exec "del %s" % S_name
        #     except:
        #         pass
        #     exec "eq_tmp = copy.deepcopy(%s)" % SE_name  # after passing a model equation to a Syanpses(), a new line will automatically be added to equation, e.i. lastupdate: seconds. This is to remove that specific line
        #     try:
        #         exec "%s = Synapses(%s,%s,model = eq_tmp, pre = %s, post = %s, namespace= %s)" \
        #              % (S_name, self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], \
        #                 self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']], SPre_name,
        #                 SPost_name, SNS_name)
        #     except:  # for when there is no "post =...", i.e. fixed connection
        #         exec "%s = Synapses(%s,%s,model = eq_tmp, pre = %s, namespace= %s)" \
        #              % (S_name, self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], \
        #                 self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']], SPre_name,
        #                 SNS_name)
        #     syn_con_str = "%s.connect('i!=j', p=' " % S_name
        #     # Connecting the synapses based on either [the defined probability and the distance] or [only the distance] plus considering the number of connections
        #     syn_con_str += "%s" % (self.optimized_probabilities[current_idx])
        #     try:
        #         syn_con_str += "',n=%s)" % n_arg
        #     except:
        #         syn_con_str += "')"
        #     exec syn_con_str
        #     exec "globals().update({'%s':%s})" % (S_name, S_name)

    def relay(self, *args):
        '''
        The method that creates the relay NeuronGroups based on the parameters that are extracted from the configuraiton \
        file in the __init__ method of the class. Note that the SpikeGeneratorGroup() does not support the locations and \
        synaptic connection based on the distance between the input, and the target neuron group. For this reason, a "realy"\
         neuron group is created which is directly connected to the SpikeGeneratorGroup(). Unlike SpikeGeneratorGroup() this \
        relay group supports the locations. With this workaround, the synaptic connection between the input and the Neuron group can be implemented \
        based on the distance of the neurons then.

        Note: extracting the input spikes and time sequences for using in a SpikeGeneratorGroup() is done in this method. \
        This procedure needs using a "run()" method in brian2. However, one of the limitations of the Brian2Genn is that \
        the user cannot use multiple "run()" methods in the whole scirpt. To address this issue, the genn device should be \
        set after using the first run(), hence the unusual placement of "set_device('genn')" command in current method.

        :param args: This method will have at least 4 main positional argumenst directly passed from __init__ method: path to the input .mat file, and the frequency. Description of other possible arguments can be found in Configuration file tutorial.

        Main internal variables:

        * inp: an instance of stimuli() object from stimuli module.
        * relay_group: the dictionary containing the data for relay NeuonGroup()
        * NG_name: Generated vriable name for the NeuonGroup() object in brian2.
        * NN_name: Generated vriable name for corresponding Neuron Number.
        * NE_name: Generated vriable name for the NeuonGroup() equation.
        * NT_name: Generated vriable name for the NeuonGroup() threshold.
        * NRes_name: Generated vriable name for the NeuonGroup() reset value.
        * SGsyn_name: variable name for the Synapses() objecct that connects SpikeGeneratorGroup() and relay neurons.

        following four variables are build using the load_input_seq() method in simuli object:

        * spikes_str: The string containing the syntax for Spike indices in the input neuron group.
        * times_str: The string containing the syntax for time indices in the input neuron group.
        * SG_str: The string containing the syntax for creating the SpikeGeneratorGroup() based on the input .mat file.
        * number_of_neurons: The number of neurons that exist in the input .mat file.
        '''
        NG_name = ''
        def video(self):
            print "creating an input based on the video input."
            path = self.current_values_list[_all_columns.index('path')].strip()
            freq = self.current_values_list[_all_columns.index('freq')]
            inp = stimuli()
            inp.generate_inputs(path,freq )
            spikes_str, times_str, SG_str, number_of_neurons = inp.load_input_seq(path)
            Spikes_Name = spikes_str.split('=')[0].rstrip()
            Time_Name = times_str.split('=')[0].rstrip()
            SG_Name = SG_str.split('=')[0].rstrip()

            # Internal switch for brian2GeNN:
            if self.use_genn == 1:
                set_device('genn')

            exec spikes_str in globals(), locals() # runnig the string containing the syntax for Spike indices in the input neuron group.
            exec times_str in globals(), locals()# running the string containing the syntax for time indices in the input neuron group.
            exec SG_str in globals(), locals()# running the string containing the syntax for creating the SpikeGeneratorGroup() based on the input .mat file.
            exec "globals().update({'%s':%s,'%s':%s,'%s':%s})" % \
                 (Spikes_Name, Spikes_Name, Time_Name, Time_Name, SG_Name, SG_Name) in globals(), locals() # updating the Globals()

            # current_idx = len(self.customized_neurons_list)
            # relay_group = {}
            # relay_group['idx'] = int(idx)
            # relay_group['type'] = 'in'
            # relay_group['z_positions'] = squeeze(inp.get_input_positions(path))
            # relay_group['w_positions'] = 17 * log(relay_group['z_positions'] + 1)
            # relay_group['equation'] = ''
            self.customized_neurons_list[current_idx]['z_positions'] = squeeze(inp.get_input_positions(path))
            self.customized_neurons_list[current_idx]['w_positions'] = 17 * log(relay_group['z_positions'] + 1)
            NG_name = self._NeuronGroup_prefix + str(current_idx) + '_relay_video' #  Generated variable name for the NeuonGroup() object in brian2.
            self.neurongroups_list.append(NG_name)
            NN_name = self._NeuronNumber_prefix + str(current_idx) #  Generated vriable name for corresponding Neuron Number.
            NE_name = self._NeuronEquation_prefix + str(current_idx) # Generated vriable name for the NeuonGroup() equation.
            NT_name = self._NeuronThreshold_prefix + str(current_idx) # Generated vriable name for the NeuonGroup() threshold.
            NRes_name = self._NeuronReset_prefix + str(current_idx) # Generated vriable name for the NeuonGroup() reset value.
            Eq = """'''emit_spike : 1
                x : meter
                y : meter'''"""
            exec "%s=%s" % (NN_name, number_of_neurons) in globals(), locals()
            exec "%s=%s" % (NE_name, Eq) in globals(), locals()
            exec "%s=%s" % (NT_name, "'emit_spike>=1'") in globals(), locals()
            exec "%s=%s" % (NRes_name, "'emit_spike=0'") in globals(), locals()
            exec "%s= NeuronGroup(%s, model=%s, threshold=%s, reset=%s)" \
                 % (NG_name, NN_name, NE_name, NT_name, NRes_name) in globals(), locals()
            # setting the position of the neurons based on the positions in the .mat input file:
            exec "%s.x=real(self.customized_neurons_list[%d]['w_positions'])*mm\n%s.y=imag(self.customized_neurons_list[%d]['w_positions'])*mm" % (
                NG_name, current_idx, NG_name, current_idx) in globals(), locals()
            # self.save_data.syntax_bank.append(
            #     "%s.save_data.data['positions_all']['%s'] = %s.customized_neurons_list[%d]['positions']" % (
            #         self.name, NG_name, self.name, current_idx))
            self.save_data.data['positions_all']['z_coord'][NG_name] = self.customized_neurons_list[current_idx][
                'z_positions']
            self.save_data.data['positions_all']['w_coord'][NG_name] = self.customized_neurons_list[current_idx][
                'w_positions']
            SGsyn_name = 'SGEN_Syn' # variable name for the Synapses() objecct that connects SpikeGeneratorGroup() and relay neurons.
            exec "%s = Synapses(GEN, %s, pre='emit_spike+=1', connect='i==j')" % (SGsyn_name, NG_name) in globals(), locals()# connecting the SpikeGeneratorGroup() and relay group.

            exec "globals().update({'%s':%s,'%s':%s,'%s':%s,'%s':%s,'%s':%s,'%s':%s})" % \
                 (NN_name, NN_name, NE_name, NE_name, NT_name, NT_name, NRes_name, NRes_name, NG_name, NG_name, SGsyn_name,
                  SGsyn_name) in globals(), locals()# updating the Globals()
            self.monitors(mons.split(' '), NG_name, self.customized_neurons_list[-1]['equation'])  # taking care of the monitors


        def VPM(self): #ventral posteromedial (VPM) thalamic nucleus
            spike_times = self.current_values_list[_all_columns.index('spike_times')].strip().replace(' ',',')
            spike_times_list = ast.literal_eval(spike_times[0:spike_times.index('*')])
            spike_times_unit = spike_times[spike_times.index('*')+1:]
            exec 'spike_times_ = spike_times_list * %s' %spike_times_unit in globals(), locals()
            try:
                net_center = self.current_values_list[_all_columns.index('net_center')].strip()
            except:
                net_center = 0 + 0j
            net_center = complex (net_center)
            number_of_neurons = self.current_values_list[_all_columns.index('number_of_neurons')].strip()
            print "creating an input based on the central %s neurons."%number_of_neurons
            Spikes_Name = 'GEN_SP'
            Time_Name = 'GEN_TI'
            SG_Name = 'GEN'
            spikes_str = 'GEN_SP=tile(arange(%s),%d)'%(number_of_neurons,len(spike_times_))
            times_str = 'GEN_TI = repeat(%s,%s)*%s'%(spike_times[0:spike_times.index('*')],number_of_neurons,spike_times_unit)
            SG_str = 'GEN = SpikeGeneratorGroup(%s, GEN_SP, GEN_TI)'%number_of_neurons
            # Internal switch for brian2GeNN:
            if self.use_genn == 1:
                set_device('genn')

            exec spikes_str in globals(), locals()  # runnig the string containing the syntax for Spike indices in the input neuron group.
            exec times_str in globals(), locals()  # running the string containing the syntax for time indices in the input neuron group.
            exec SG_str in globals(), locals()  # running the string containing the syntax for creating the SpikeGeneratorGroup() based on the input .mat file.
            exec "globals().update({'%s':%s,'%s':%s,'%s':%s})" % \
                 (Spikes_Name, Spikes_Name, Time_Name, Time_Name, SG_Name,
                  SG_Name) in globals(), locals()  # updating the Globals()
            vpm_customized_neuron = customized_neuron(current_idx, int(number_of_neurons),'L1i','0',net_center)
            self.customized_neurons_list[current_idx]['z_positions'] = vpm_customized_neuron.output_neuron['z_positions']
            self.customized_neurons_list[current_idx]['w_positions'] = vpm_customized_neuron.output_neuron['w_positions']

            NG_name = self._NeuronGroup_prefix + str(current_idx) + '_relay_vpm'  # Generated variable name for the NeuonGroup() object in brian2.
            self.neurongroups_list.append(NG_name)
            NN_name = self._NeuronNumber_prefix + str(current_idx)  # Generated vriable name for corresponding Neuron Number.
            NE_name = self._NeuronEquation_prefix + str(current_idx)  # Generated vriable name for the NeuonGroup() equation.
            NT_name = self._NeuronThreshold_prefix + str(current_idx)  # Generated vriable name for the NeuonGroup() threshold.
            NRes_name = self._NeuronReset_prefix + str(current_idx)  # Generated vriable name for the NeuonGroup() reset value.
            Eq = """'''emit_spike : 1
                            x : meter
                            y : meter'''"""
            exec "%s=%s" % (NN_name, number_of_neurons) in globals(), locals()
            exec "%s=%s" % (NE_name, Eq) in globals(), locals()
            exec "%s=%s" % (NT_name, "'emit_spike>=1'") in globals(), locals()
            exec "%s=%s" % (NRes_name, "'emit_spike=0'") in globals(), locals()
            exec "%s= NeuronGroup(%s, model=%s, threshold=%s, reset=%s)" \
                 % (NG_name, NN_name, NE_name, NT_name, NRes_name) in globals(), locals()
            # setting the position of the neurons based on the positions in the .mat input file:
            exec "%s.x=real(self.customized_neurons_list[%d]['w_positions'])*mm\n%s.y=imag(self.customized_neurons_list[%d]['w_positions'])*mm" % (
                NG_name, current_idx, NG_name, current_idx) in globals(), locals()
            # self.save_data.syntax_bank.append(
            #     "%s.save_data.data['positions_all']['%s'] = %s.customized_neurons_list[%d]['positions']" % (
            #         self.name, NG_name, self.name, current_idx))
            self.save_data.data['positions_all']['z_coord'][NG_name] = self.customized_neurons_list[current_idx][
                'z_positions']
            self.save_data.data['positions_all']['w_coord'][NG_name] = self.customized_neurons_list[current_idx][
                'w_positions']
            SGsyn_name = 'SGEN_Syn'  # variable name for the Synapses() objecct that connects SpikeGeneratorGroup() and relay neurons.
            exec "%s = Synapses(GEN, %s, pre='emit_spike+=1', connect= 'i!=j')" % (
            SGsyn_name, NG_name) in globals(), locals()  # connecting the SpikeGeneratorGroup() and relay group.
            exec "globals().update({'%s':%s,'%s':%s,'%s':%s,'%s':%s,'%s':%s,'%s':%s})" % \
                 (NN_name, NN_name, NE_name, NE_name, NT_name, NT_name, NRes_name, NRes_name, NG_name, NG_name,
                  SGsyn_name,
                  SGsyn_name) in globals(), locals()  # updating the Globals()
            self.monitors(mons.split(' '), NG_name,
                          self.customized_neurons_list[-1]['equation'])  # taking care of the monitors

        assert self.sys_mode != '', "Error: System mode not defined."
        assert 'type' in self.current_parameters_list, 'The type of the input is not defined in the configuration file.'
        _input_params = {
            'video': [['idx', 'type', 'path', 'freq', 'monitors'], [0, 1, 2],video],
            'VPM': [['idx', 'type','number_of_neurons','spike_times','net_center','monitors' ], [0, 1,2,3],VPM]
        }
        assert self.current_values_list[self.current_parameters_list.index('type')] in _input_params.keys(), 'The input type %s of the configuration file is not defined' %self.current_parameters_list[_all_columns.index('type')]
        _all_columns = _input_params[self.current_values_list[self.current_parameters_list.index('type')]][0]
        _obligatory_params = _input_params[self.current_values_list[self.current_parameters_list.index('type')]][1]
        assert len(self.current_values_list) >= len(_obligatory_params), 'One or more of of the columns for\
                     input definition is missing. Following obligatory columns should be defined:\n%s\n' % str(
            [_all_columns[ii] for ii in _obligatory_params])
        assert 'N/A' not in [self.current_values_list[ii] for ii in
                             _obligatory_params], 'Following obligatory values cannot be "N/A":\n%s' % str(
            [_all_columns[ii] for ii in _obligatory_params])
        assert len(self.current_parameters_list) == len(self.current_values_list) , 'The number of columns for the input are not equal to number of values in the configuration file.'
        try:
            mons = self.current_values_list[_all_columns.index('monitors')]
        except:
            mons = 'N/A'
        idx = self.current_values_list[_all_columns.index('idx')]
        assert idx not in self.NG_indices, "Error: multiple indices with same values exist in the configuration file."
        self.NG_indices.append(idx)
        current_idx = len(self.customized_neurons_list)
        relay_group = {}
        relay_group['idx'] = int(idx)
        relay_group['type'] = 'in'
        relay_group['z_positions'] = []
        relay_group['w_positions'] = []
        relay_group['equation'] = ''
        self.customized_neurons_list.append(relay_group)
        _input_params[self.current_values_list[self.current_parameters_list.index('type')]][2](self)



    def gather_result(self):
        '''
        After the simulation and using the syntaxes that are previously prepared in the synatx_bank of save_data() object, this method saves the collected data to a file.

        '''
        for syntax in self.save_data.syntax_bank:
            exec syntax
        self.save_data.save_to_file()

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

    def _status_printer(self,str):
        cleaner = ' ' * 100
        print '\r' + cleaner + '\r' + str,


if __name__ == '__main__' :
    CM = cortical_system (os.path.dirname(os.path.realpath(__file__)) + '/generated_config_file.csv' , os.getcwd())
    #
    #
    run(500*ms,report = 'text')
    # if CM.use_genn == 1 :
    #     device.build(directory='tester',
    #                 compile=True,
    #                  run=True,
    #                  use_GPU=True)
    #
    #
    CM.gather_result()
    # CM.visualise_connectivity(S0_Fixed)
    for group in CM.monitor_name_bank:
        mon_num = len(CM.monitor_name_bank[group])
        exec "f, axarr = plt.subplots(%d, sharex=True)"%mon_num
        for item_idx,item in enumerate(CM.monitor_name_bank[group]):
            if 'SpMon' in item :
                if len (CM.monitor_name_bank[group]) ==1  :
                    exec "axarr.plot(%s.t/ms,%s.i,'.k')" % ( item, item);
                    exec "axarr.set_title('%s')" % ( item);
                else:
                    exec "axarr[%d].plot(%s.t/ms,%s.i,'.k')" % (item_idx, item, item)
                    exec "axarr[%d].set_title('%s')"% (item_idx, item)
            elif 'StMon' in item:
                underscore= item.index('__')
                variable = item[underscore+2:]
                exec 'y_num=len(%s.%s)'%(item,variable)
                try :
                    exec "multi_y_plotter(axarr[%d] , y_num , '%s',%s , '%s')" %(item_idx,variable,item,item)
                except:
                    exec "multi_y_plotter(axarr , y_num , '%s',%s , '%s')" % ( variable, item, item)
    show()

