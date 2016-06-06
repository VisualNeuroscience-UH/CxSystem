__author__ = 'V_AD'
from brian2 import *
import brian2genn
import os
from Definitions import *
import brian2genn_tester as bt
from Plotter import *
from save_data import *

class cortical_module(object):
    'A customizable model of cortical module for Brian2Genn'
    _NeuronGroup_prefix = 'NG'
    _NeuronNumber_prefix = 'NN'
    _NeuronEquation_prefix = 'NE'
    _NeuronThreshold_prefix = 'NT'
    _NeuronReset_prefix = 'NRes'
    _NeuronRef_prefix = 'NRef'
    _NeuronNS_prefix = 'NNs' # name space prefix
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

    def __init__(self,config_path,name,save_path):
        '''


        :param config_path: The path to the configuration file. The description of the configuration file can be found in ().
        :param name: Name of the
        :param save_path:
        '''
        _options = {
            '[G]': self.neuron_group,
            '[S]': self.synapse,
            '[IN]': self.relay
        }
        is_tag = ['[']
        self.name = name
        self.syntax_bank = {}
        self.syntax_bank[1] = []  # components of both neuron groups and synapses
        self.syntax_bank[2] = [] # definitions of the neuron groups
        self.syntax_bank[3] = [] # neuron groups initialization
        self.syntax_bank[4] = []
        self.syntax_bank[5] = []
        self.syntax_bank[6] = [] # monitors
        self.customized_neurons_list = []
        self.customized_synapses_list = []
        self.neurongroups_list = []
        self.synapses_list = []
        self.monitor_name_bank = {}
        self.default_monitors = []
        self.monitor_idx = 0
        self.save_data = save_data(save_path)
        self.save_data.creat_key('positions_all')
        with open (config_path, 'r') as f :
            for line in f:
                if line[0]  in is_tag :
                    line = line[line.index(']')+1:]
                    tag = line[line.index('['):line.index(']')+1]
                    assert tag in _options.keys(), 'The tag %s is not defined.'%tag
                else:
                    continue
                line = line.replace(tag, '')
                line = line.replace('\n', '')
                line = line.lstrip()
                args = line.split(' ')
                _options[tag](args)

        print "Cortical Module initialization Done."


    def neuron_group (self, *args ):
        '''
        The method that creates the NeuronGroups() based on the parameters that are extracted from the configuraiton file in the __init__ method of the class.

        :param args:
        :return:
        '''
        args = args[0]
        mon_args=[]
        #check monitors in line:
        if '[M]' in args :
            mon_args = args[args.index('[M]')+1:]
            args = args[0:args.index('[M]')]
        current_idx=  len(self.customized_neurons_list)
        if args[1] == 'PC' :
            exec 'args[2] = array(' + args[2] + ')'
        self.customized_neurons_list.append(customized_neuron (*args[0:3]).output_neuron) # layer_idx is created by dynamic compiler
        if len(args) > 3: # in case of threshold/reset/refractory overwrite
            for arg_idx in range (3,len(args)):
                if 'threshold' in args[arg_idx] :
                    args[arg_idx] = args[arg_idx][args[arg_idx].index("'")+1:-2]
                    self.customized_neurons_list[-1]['threshold'] = args[arg_idx]
                elif 'reset' in args[arg_idx]:
                    args[arg_idx] = args[arg_idx][args[arg_idx].index("'")+1:-2]
                    self.customized_neurons_list[-1]['reset'] = args[arg_idx]
                elif 'refractory' in args[arg_idx]:
                    args[arg_idx] = args[arg_idx][args[arg_idx].index("'")+1:-2]
                    self.customized_neurons_list[-1]['refractory'] =  args[arg_idx]
        NG_name = self._NeuronGroup_prefix + str(current_idx) + '_' + args[1]
        self.neurongroups_list.append(NG_name)
        NN_name = self._NeuronNumber_prefix + str(current_idx)
        NE_name = self._NeuronEquation_prefix + str(current_idx)
        NT_name = self._NeuronThreshold_prefix + str(current_idx)
        NRes_name = self._NeuronReset_prefix + str(current_idx)
        NRef_name = self._NeuronRef_prefix + str(current_idx)
        NNS_name = self._NeuronNS_prefix + str(current_idx)
        # NPos_name = self._NeuronPos_prefix + str(current_idx)
        # self.monitor_name_bank['NeuroGroups'].append(NG_name)

        NN_str = "%s=%s.customized_neurons_list[%d]['number_of_neurons']"% (NN_name, self.name ,current_idx)
        NE_str= "%s=%s.customized_neurons_list[%d]['equation']"% (NE_name ,self.name , current_idx)
        NT_str = "%s=%s.customized_neurons_list[%d]['threshold']"%(NT_name ,self.name ,current_idx)
        NRes_str = "%s=%s.customized_neurons_list[%d]['reset']"% (NRes_name,self.name , current_idx)
        NRef_str = "%s=%s.customized_neurons_list[%d]['refractory']"% (NRef_name,self.name,current_idx)
        NNS_str  = "%s=%s.customized_neurons_list[%d]['namespace']"% (NNS_name,self.name,current_idx)
        self.syntax_bank[1].extend([NN_str,NE_str,NT_str,NRes_str,NRef_str,NNS_str])

        NG_str = "%s= NeuronGroup(%s, model=%s, threshold=%s, reset=%s,refractory = %s, namespace = %s)" \
                 % (NG_name , NN_name , NE_name,NT_name, NRes_name, NRef_name , NNS_name)
        self.syntax_bank[2].append(NG_str)

        NPos_str = "%s.x=real(%s.customized_neurons_list[%d]['positions'])*mm\n%s.y=imag(%s.customized_neurons_list[%d]['positions'])*mm" % (NG_name, self.name, current_idx,NG_name, self.name, current_idx)
        self.save_data.syntax_bank.append("%s.save_data.data['positions_all']['%s'] = %s.customized_neurons_list[%d]['positions']" % (self.name, NG_name,self.name, current_idx ))

        NG_init = 'Vr_offset = rand(len(%s))\n'%NG_name
        NG_init += "for _key in %s.variables.keys():\n"%NG_name
        NG_init += "\tif _key.find('vm')>=0:\n"
        NG_init += "\t\tsetattr(%s,_key,%s['Vr']+Vr_offset * (%s['VT']-%s['Vr']))\n"%(NG_name,NNS_name,NNS_name,NNS_name)
        NG_init += "\telif ((_key.find('ge')>=0) or (_key.find('gi')>=0)):\n"
        NG_init += "\t\tsetattr(%s,_key,0)" %NG_name
        self.syntax_bank[3].extend([NPos_str, NG_init])
        self.monitors(mon_args,args[1],NG_name , self.customized_neurons_list[-1]['equation'])


    def monitors(self,mon_args,cell_type, object_name , equation):
        '''
        The method that creates the monitors() based on the parameters that are extracted from the configuraiton file in the __init__ method of the class.

        :param mon_args:
        :param cell_type:
        :param object_name:
        :param equation:
        :return:
        '''
        if not mon_args and not self.default_monitors:
            return
        if not mon_args:
            mon_args = self.default_monitors
        if '-->' in mon_args:
            del (mon_args[mon_args.index('-->')])
            self.default_monitors = mon_args
        if '<--' in mon_args:
            del (mon_args[mon_args.index('<--')])
            if not mon_args:
                mon_args = self.default_monitors
            self.default_monitors= []

        monitor_options = {
            '[Sp]': ['SpMon', 'SpikeMonitor'],
            '[St]': ['StMon', 'StateMonitor'],
            '[dt]' : [',dt='],
            '[rec]': [',record=']
        }
        self.monitor_name_bank[object_name] = []
        for mon_arg in mon_args:
            mon_tag = mon_arg[mon_arg.index('['):mon_arg.index(']') + 1]
            mon_arg = mon_arg.replace(mon_tag, '')
            if mon_tag == '[Sp]':
                self.save_data.creat_key('spikes_all')
                Mon_name = monitor_options['[Sp]'][0] + str(self.monitor_idx) + '_' + object_name
                self.save_data.syntax_bank.append("%s.save_data.data['spikes_all']['%s'] = %s.it"%(self.name,object_name,Mon_name))
                self.monitor_name_bank[object_name].append(Mon_name)
                Mon_str = "%s=%s(%s)" % (Mon_name, monitor_options['[Sp]'][1], object_name)
                self.syntax_bank[6].append(Mon_str)
                self.monitor_idx +=1
            else:
                mon_arg = mon_arg.split('+')
                for sub_mon_arg in mon_arg:
                    # Mon_name = monitor_options['[St]'][0] + str(self.monitor_idx) + '_' + object_name + '_' +
                    Mon_str = "=%s(%s,"% ( str(monitor_options[mon_tag][1]),object_name)
                    sub_mon_tags = []
                    if not ('[' in sub_mon_arg):
                        sub_mon_arg = sub_mon_arg.split()
                        sub_mon_arg.append('True')
                        sub_mon_tags.append('[rec]')
                        # Mon_name = monitor_options['[St]'][0] + str(self.monitor_idx) + '_' + object_name + '_' + \
                        #        sub_mon_arg
                    else:
                        tag_open_indices = [idx for idx, ltr in enumerate(sub_mon_arg) if ltr == '[']
                        tag_close_indices = [idx for idx, ltr in enumerate(sub_mon_arg) if ltr == ']']
                        assert len(tag_open_indices)==len(tag_close_indices), 'Error: wrong sets of tagging paranteses in monitor definitoins. '
                        for tag_idx in range(len(tag_open_indices)) :
                            sub_mon_tags.append(sub_mon_arg[sub_mon_arg.index('['):sub_mon_arg.index(']') + 1])
                            sub_mon_arg = sub_mon_arg.replace(sub_mon_tags[tag_idx],' ') # replace the tags with space
                        sub_mon_arg = sub_mon_arg.split(' ')
                        if not '[rec]' in sub_mon_tags  :
                            sub_mon_tags.append('[rec]')
                            sub_mon_arg.append('True')
                        assert len(sub_mon_arg) == len(sub_mon_tags) + 1 , 'Error in monitor tag definition.'
                    self.save_data.creat_key('%s_all'%sub_mon_arg[0])
                    Mon_name = monitor_options['[St]'][0] + str(self.monitor_idx) + '_' + object_name + '__' + sub_mon_arg[0]
                    self.save_data.syntax_bank.append("%s.save_data.data['%s_all']['%s'] = asarray(%s.%s)" % (self.name,sub_mon_arg[0], object_name, Mon_name,sub_mon_arg[0]))

                    self.monitor_name_bank[object_name].append(Mon_name)
                    Mon_str = Mon_name + Mon_str + "'" + sub_mon_arg[0] + "'"
                        # check if the variable exist in the equation
                    if ('d' + sub_mon_arg[0]) in str(equation):
                        assert (sub_mon_arg[0] + '/') in str(equation), \
                            'The monitor varibale %s is not defined in the equation.' % sub_mon_arg[0]
                    else:
                        assert (sub_mon_arg[0]) in str(equation), \
                            'The monitor varibale %s is not defined in the equation.' % sub_mon_arg[0]
                    del(sub_mon_arg[0])
                    for idx,tag in enumerate(sub_mon_tags):
                        Mon_str += monitor_options[tag][0] + sub_mon_arg[idx]
                    Mon_str +=')'
                    self.syntax_bank[6].append(Mon_str)
                    self.monitor_idx += 1



    def synapse(self, *args):
        '''
        The method that creates the Synapses() in brian2, based on the parameters that are extracted from the configuraiton file in the __init__ method of the class.

        :param args:
        :return:
        '''
        _options = {
            '[C]': self.neuron_group,
        }
        # _is_tag = ['[']
        # args = args[0]
        mon_args = []
        if len(args[0][2])> 1 and '[' in args[0][2]:
            arg = args[0][2]
            tag = arg[arg.index('['):arg.index(']') + 1]
            assert tag in _options.keys(), 'The synaptic tag %s is not defined.' % tag
            if tag == '[C]':
                _post_group_idx , _post_com_idx = arg.split('[' + 'C' + ']')
                args[0][2] = _post_group_idx
                assert self.customized_neurons_list[int(args[0][2])]['type'] == 'PC'  , 'A compartment is targetted but the neuron geroup is not PC. Check Synapses in the configuration file.'
                if '[M]' in args[0]:
                    mon_args = args[0][args[0].index('[M]') + 1:]
                    args = list(args)
                    args[0] = args[0][0:args[0].index('[M]')]
                    args = tuple(args)
                _pre_type = self.customized_neurons_list[int(args[0][1])]['type']
                _post_type = self.customized_neurons_list[int(args[0][2])]['type']
                args[0].extend([_pre_type,_post_type])
                if _post_com_idx[0] == '0':
                    if len(_post_com_idx) == 1:
                        triple_args = []

                        tmp_args = list(args[0])
                        tmp_args.append('_basal')
                        triple_args.append(tmp_args)
                        tmp_args = list(args[0])
                        tmp_args.append('_soma')
                        triple_args.append(tmp_args)
                        tmp_args = list(args[0])
                        tmp_args.append('_a0')
                        triple_args.append(tmp_args)
                        args = triple_args
                    else :
                        triple_args = []
                        for tmp_idx in _post_com_idx[1:]:
                            tmp_args = list(args[0])
                            if tmp_idx == '0':
                                tmp_args.append('_basal')
                                triple_args.append(tmp_args)
                            elif tmp_idx == '1':
                                tmp_args.append('_soma')
                                triple_args.append(tmp_args)
                            elif tmp_idx == '2':
                                tmp_args.append('_a0')
                                triple_args.append(tmp_args)
                        args = triple_args
                elif int(_post_com_idx) > 0 :
                    args[0].append('_a'+str(_post_com_idx))
        else:
            if '[M]' in args[0]:
                mon_args = args[0][args[0].index('[M]') + 1:]
                args = list(args)
                args[0] = args[0][0:args[0].index('[M]')]
                args = tuple(args)
            _pre_type = self.customized_neurons_list[int(args[0][1])]['type']
            _post_type = self.customized_neurons_list[int(args[0][2])]['type']
            args[0].extend([_pre_type,_post_type])
        for syn in args :

            # check monitors in line:
            current_idx = len(self.customized_synapses_list)
            self.customized_synapses_list.append(customized_synapse(*syn).output_synapse)
            S_name = self._Synapses_prefix+str(current_idx) + '_' + syn[3]
            self.synapses_list.append(S_name)
            SE_name= self._SynapsesEquation_prefix + str(current_idx)
            SPre_name=  self._SynapsesPre_prefix + str(current_idx)
            SPost_name = self._SynapsesPost_prefix + str(current_idx)
            SNS_name = self._SynapsesNS_prefix + str(current_idx)
            # self.monitor_name_bank['Synapses'].append(S_name)

            SE_str= "%s=%s.customized_synapses_list[%d]['equation']" %(SE_name,self.name,current_idx)
            SPre_str = "%s=%s.customized_synapses_list[%d]['pre_eq']" %(SPre_name,self.name,current_idx)
            SPost_str = "%s=%s.customized_synapses_list[%d]['post_eq']" % (SPost_name, self.name, current_idx)
            SNS_str = "%s=%s.customized_synapses_list[%d]['namespace']" % (SNS_name, self.name, current_idx)
            self.syntax_bank[1].extend([SE_str,SPre_str,SPost_str,SNS_str])


            S_str = "%s = Synapses(%s,%s,model = %s, pre = %s, post = %s, namespace= %s)"\
                      %(S_name,self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], \
                        self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']],SE_name,SPre_name,SPost_name, SNS_name)
            # self.monitor_name_bank['Synapses_definitions'].append(S_str)
            self.syntax_bank[4].append(S_str)
            SC_str = "%s.connect('i!=j', p='%f*exp(-(sqrt((x_pre-x_post)**2+(y_pre-y_post)**2))*%f)')"\
                     %(S_name,self.customized_synapses_list[-1]['sparseness'],self.customized_synapses_list[-1]['ilam'])
            SW_str = "%s.wght=%s['wght0']" %(S_name,SNS_name)
            self.syntax_bank[5].extend([SC_str, SW_str])
            self.monitors(mon_args, syn[3], S_name, self.customized_synapses_list[-1]['equation'])

    def relay(self,*args):
        '''
        The method that creates the relay NeuronGroups based on the parameters that are extracted from the configuraiton file in the __init__ method of the class.

        :param args:
        :return:
        '''
        args = args[0]
        current_idx=  len(self.customized_neurons_list)
        relay_group = {}
        relay_group['type'] = 'in'
        self.customized_neurons_list.append(relay_group)
        NG_name = self._NeuronGroup_prefix +str(current_idx) +'_' + 'relay'
        self.neurongroups_list.append(NG_name)
        NN_name = self._NeuronNumber_prefix + str(current_idx)
        NE_name = self._NeuronEquation_prefix + str(current_idx)
        NT_name = self._NeuronThreshold_prefix + str(current_idx)
        NRes_name = self._NeuronReset_prefix + str(current_idx)
        Eq= """'''emit_spike : 1
            x : meter
            y : meter'''"""
        NN_str = "%s=%s" % (NN_name, args[0])
        NE_str = "%s=%s" % (NE_name, Eq)
        NT_str = "%s=%s" % (NT_name, "'emit_spike==1'")
        NRes_str = "%s=%s" % (NRes_name, "'emit_spike=0'")
        self.syntax_bank[1].extend([NN_str, NE_str, NT_str, NRes_str])

        NG_str = "%s= NeuronGroup(%s, model=%s, threshold=%s, reset=%s)" \
                 % (NG_name, NN_name, NE_name, NT_name, NRes_name)
        self.syntax_bank[2].append(NG_str)


# a = datetime.datetime.now()
#
# CM = cortical_module (os.path.dirname(os.path.realpath(__file__)) + '/Connections.txt' , 'CM', os.getcwd())
#
#
# set_device('genn')
# for hierarchy in CM.syntax_bank :
#     for syntax in CM.syntax_bank[hierarchy]:
#         exec syntax
#
#
# Ge = SpikeGeneratorGroup(10, array([0,0,1,2,3,4]), array([20,25,100,120,50,280])*ms)
# forward = Synapses(Ge,NG16_relay, pre = 'emit_spike+=1',  connect='i==j')
#
#
# run(500*ms)
# device.build(directory='tester',
#             compile=True,
#              run=True,
#              use_GPU=True)
#
#
# for group in CM.monitor_name_bank:
#     mon_num = len(CM.monitor_name_bank[group])
#     tmp_str = "f, axarr = plt.subplots(%d, sharex=True)"%mon_num ; exec tmp_str
#     for item_idx,item in enumerate(CM.monitor_name_bank[group]):
#         if 'SpMon' in item :
#             tmp_str = "axarr[%d].plot(%s.t/ms,%s.i,'.k')" % (item_idx, item, item);exec tmp_str
#             tmp_str= "axarr[%d].set_title('%s')"% (item_idx, item);exec tmp_str
#         elif 'StMon' in item:
#             underscore= item.index('__')
#             variable = item[underscore+2:]
#             tmp_str = 'y_num=len(%s.%s)'%(item,variable);exec tmp_str
#             tmp_str = "multi_y_plotter(axarr[%d] , y_num , '%s',%s , '%s')" %(item_idx,variable,item,item);exec tmp_str
#
#
#
# for syntax in CM.save_data.syntax_bank :
#     exec syntax
# CM.save_data.save_to_file()
#
# b = datetime.datetime.now()
# c = b - a
# print c
# divmod(c.days * 86400 + c.seconds, 60)
# print divmod(c.days * 86400 + c.seconds, 60)




