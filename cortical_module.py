__author__ = 'V_AD'
from brian2 import *
import brian2genn
import os
from Definitions import *
import brian2genn_tester as bt

class cortical_module:
    'A customizable model of cortical module for Brian2Genn'
    _NeuronGroup_prefix = 'NG'
    _NeuronNumber_prefix = 'NN'
    _NeuronEquation_prefix = 'NE'
    _NeuronThreshold_prefix = 'NT'
    _NeuronReset_prefix = 'NRes'
    _NeuronRef_prefix = 'NRef'
    _NeuronNS_prefix = 'NNs' # name space prefix
    _Synapses_prefix = 'S'
    _SynapsesEquation_prefix = 'SE'
    _SynapsesPre_prefix = 'SPre'
    _SynapsesPost_prefix = 'SPost'
    _SynapsesNS_prefix = 'SNS'
    _SynapticConnection_prefix = 'SC'
    _SynapticWeight_prefix = 'SW'
    def __init__(self,path,name):
        _options = {
            '[G]': self.neuron_group,
            '[S]': self.synapse,
            '[IN]': self.relay
        }
        is_tag = ['[']
        self.name = name
        self.syntax_bank = {}
        self.syntax_bank['Ingredients'] = []
        self.syntax_bank['NeuronGroups'] = []
        self.syntax_bank['NeuronGroups_init'] = []
        self.syntax_bank['Synapses_params'] = []
        self.syntax_bank['Synapses'] = []
        self.customized_neurons_list = []
        self.customized_synapses_list = []
        self.neurongroups_list = []
        self.synapses_list = []
        with open (path, 'r') as f :
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

        args = args[0]
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

        NN_str = "%s=%s.customized_neurons_list[%d]['number_of_neurons']"% (NN_name, self.name ,current_idx)
        NE_str= "%s=%s.customized_neurons_list[%d]['equation']"% (NE_name ,self.name , current_idx)
        NT_str = "%s=%s.customized_neurons_list[%d]['threshold']"%(NT_name ,self.name ,current_idx)
        NRes_str = "%s=%s.customized_neurons_list[%d]['reset']"% (NRes_name,self.name , current_idx)
        NRef_str = "%s=%s.customized_neurons_list[%d]['refractory']"% (NRef_name,self.name,current_idx)
        NNS_str  = "%s=%s.customized_neurons_list[%d]['namespace']"% (NNS_name,self.name,current_idx)
        self.syntax_bank['Ingredients'].extend([NN_str,NE_str,NT_str,NRes_str,NRef_str,NNS_str])

        NG_str = "%s= NeuronGroup(%s, model=%s, threshold=%s, reset=%s,refractory = %s, namespace = %s)" \
                 % (NG_name , NN_name , NE_name,NT_name, NRes_name, NRef_name , NNS_name)
        self.syntax_bank['NeuronGroups'].append(NG_str)

        NG_init = 'Vr_offset = rand(len(%s))\n'%NG_name
        NG_init += "for _key in %s.variables.keys():\n"%NG_name
        NG_init += "\tif _key.find('vm')>=0:\n"
        NG_init += "\t\tsetattr(%s,_key,%s['Vr']+Vr_offset * (%s['VT']-%s['Vr']))\n"%(NG_name,NNS_name,NNS_name,NNS_name)
        NG_init += "\telif ((_key.find('ge')>=0) or (_key.find('gi')>=0)):\n"
        NG_init += "\t\tsetattr(%s,_key,0)" %NG_name
        self.syntax_bank['NeuronGroups_init'].append(NG_init)
        # tmp_str = "self.%s = NeuronGroup(self.customized_neurons_list[-1]['number_of_neurons'], model=self.customized_neurons_list[-1]['equation'], threshold='vm>Vcut', reset='vm=V_res', \
        #             refractory = '4 * ms', namespace =self.customized_neurons_list[-1]['namespace'])" %group_name

    # N1 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])



    def synapse(self, *args):
        _options = {
            '[C]': self.neuron_group,
        }
        # _is_tag = ['[']
        # args = args[0]
        if len(args[0][2])> 1 and '[' in args[0][2]:
            arg = args[0][2]
            tag = arg[arg.index('['):arg.index(']') + 1]
            assert tag in _options.keys(), 'The synaptic tag %s is not defined.' % tag
            if tag == '[C]':
                _post_group_idx , _post_com_idx = arg.split('[' + 'C' + ']')
                args[0][2] = _post_group_idx
                assert self.customized_neurons_list[int(args[0][2])]['type'] == 'PC'  , 'A compartment is targetted but the neuron geroup is not PC. Check Synapses in the configuration file.'
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
            _pre_type = self.customized_neurons_list[int(args[0][1])]['type']
            _post_type = self.customized_neurons_list[int(args[0][2])]['type']
            args[0].extend([_pre_type,_post_type])
        for syn in args :
            current_idx = len(self.customized_synapses_list)
            self.customized_synapses_list.append(customized_synapse(*syn).output_synapse)
            S_name = self._Synapses_prefix+str(current_idx) + '_' + syn[3]
            self.synapses_list.append(S_name)
            SE_name= self._SynapsesEquation_prefix + str(current_idx)
            SPre_name=  self._SynapsesPre_prefix + str(current_idx)
            SPost_name = self._SynapsesPost_prefix + str(current_idx)
            SNS_name = self._SynapsesNS_prefix + str(current_idx)

            SE_str= "%s=%s.customized_synapses_list[%d]['equation']" %(SE_name,self.name,current_idx)
            SPre_str = "%s=%s.customized_synapses_list[%d]['pre_eq']" %(SPre_name,self.name,current_idx)
            SPost_str = "%s=%s.customized_synapses_list[%d]['post_eq']" % (SPost_name, self.name, current_idx)
            SNS_str = "%s=%s.customized_synapses_list[%d]['namespace']" % (SNS_name, self.name, current_idx)
            self.syntax_bank['Ingredients'].extend([SE_str,SPre_str,SPost_str,SNS_str])


            S_str = "%s = Synapses(%s,%s,model = %s, pre = %s, post = %s, namespace= %s)"\
                      %(S_name,self.neurongroups_list[self.customized_synapses_list[-1]['pre_group_idx']], \
                        self.neurongroups_list[self.customized_synapses_list[-1]['post_group_idx']],SE_name,SPre_name,SPost_name, SNS_name)
            self.syntax_bank['Synapses'].append(S_str)
            SC_str = "%s.connect('i!=j',p=%f)"%(S_name,self.customized_synapses_list[-1]['probability'])
            SW_str = "%s.wght=%s['wght0']" %(S_name,SNS_name)
            self.syntax_bank['Synapses_params'].extend([SC_str, SW_str])

    def relay(self,*args):
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
        self.syntax_bank['Ingredients'].extend([NN_str, NE_str, NT_str, NRes_str])

        NG_str = "%s= NeuronGroup(%s, model=%s, threshold=%s, reset=%s)" \
                 % (NG_name, NN_name, NE_name, NT_name, NRes_name)
        self.syntax_bank['NeuronGroups'].append(NG_str)


# if targ_type == 'PC' and targ_comp_idx == 0:
#     self.output_synapse['targ_comp_name'] = ['_basal', '_soma', '_a0']




                # class synaptic_equations (object):
#     def __init__(self, output_synapse):
#         synaptic_equations.all_eq_types = array(['STDP'])
#         assert output_synapse['type'] in synaptic_equations.all_eq_types, "Equation type '%s' is not defined." % \
#                                                                                output_synapse['eq_category']
#         self.output_equation = []
#         getattr(synaptic_equations, output_synapse['type'])(self, output_synapse)
#
#     def STDP(self, output_neuron):
#         syn_eq = '''
#             wght : siemens
#             dapre/dt = -apre/taupre : siemens (event-driven)
#             dapost/dt = -apost/taupost : siemens (event-driven)
#             '''

CM = cortical_module (os.path.dirname(os.path.realpath(__file__)) + '/Connections.txt' , 'CM')

# for item in CM.neurongroups_list:
#     tmp_str = item + "= CM." + item
#     exec tmp_str
# for item in CM.synapses_list:
#     tmp_str = item + "= CM." + item
#     exec tmp_str

# N0_PC = CM.N0_PC
#
# s_mon_b = StateMonitor(N0_PC, 'vm_basal', record=0)
# s_mon = StateMonitor(N0_PC, 'vm', record=0)
# s_mon0 = StateMonitor(N0_PC, 'vm_a0', record=0)
# s_mon1 = StateMonitor(N0_PC, 'vm_a1', record=0)
# s_mon2 = StateMonitor(N0_PC, 'vm_a2', record=0)
# run(1000 * ms, report='text')
# device.build(directory='CXModule',
#              compile=True,
#              run=True,
#              use_GPU=True)
#
# f, axarr = plt.subplots(5, sharex=True)
# axarr[0].plot(s_mon_b.t / ms, s_mon_b.vm_basal[0])
# axarr[1].plot(s_mon.t / ms, s_mon.vm[0])
# axarr[2].plot(s_mon0.t / ms, s_mon0.vm_a0[0])
# axarr[3].plot(s_mon1.t / ms, s_mon1.vm_a1[0])
# axarr[4].plot(s_mon2.t / ms, s_mon2.vm_a2[0])
# show()
set_device('genn')
for syntax in CM.syntax_bank['Ingredients'] :
    exec syntax
for syntax in CM.syntax_bank['NeuronGroups'] :
    exec syntax
for syntax in CM.syntax_bank['NeuronGroups_init']:
    exec syntax
for syntax in CM.syntax_bank['Synapses']:
    exec syntax
for syntax in CM.syntax_bank['Synapses_params']:
    exec syntax



# indices = arange(NN0)
# all_idx = append(indices,indices)
# all_idx = append(all_idx, indices)
# times = repeat (array([10, 15, 25])*ms, NN0)
Ge = SpikeGeneratorGroup(10, array([0,1,2,3,4]), array([20,100,120,50,280])*ms)
forward = Synapses(Ge,NG16_relay, pre = 'emit_spike+=1',  connect='i==j')
s_mon1 = SpikeMonitor(Ge)
s_mon2 = SpikeMonitor(NG16_relay)
s_mon3 = StateMonitor(NG15_L1i,'vm',record = True)
# s_mon2 = StateMonitor(NG16_relay,'vm',record = True)
# s_mon3 = StateMonitor(NG1_PC,'vm',record=[0,5,10])
# s_mon0 = StateMonitor(NG2_L1i,'vm',record=0)
# s_mon1 = StateMonitor(NG0_SS,'vm_a1',record=0)
# s_mon2 = StateMonitor(NG0_SS,'vm_a2',record=0)


run(501*ms)
device.build(directory='tester',
            compile=True,
             run=True,
             use_GPU=True)

f, axarr = plt.subplots(3, sharex=True)
axarr[0].plot(s_mon1.t / ms, s_mon1.i,'.k')
axarr[1].plot(s_mon2.t / ms, s_mon2.i,'.k')
# axarr[2].plot(s_mon3.t / ms, s_mon3.i,'.k')
axarr[2].plot(s_mon3.t / ms, s_mon3.vm[1])
axarr[2].plot(s_mon3.t / ms, s_mon3.vm[2])
axarr[2].plot(s_mon3.t / ms, s_mon3.vm[3])
axarr[2].plot(s_mon3.t / ms, s_mon3.vm[4])
#
# axarr[2].plot(s_mon3.t / ms, s_mon3.vm[0])

# axarr[3].plot(s_mon1.t / ms, s_mon1.vm_a1[0])
# axarr[4].plot(s_mon2.t / ms, s_mon2.vm_a2[0])
# plot(s_mon2.t / ms, s_mon2.i, '.k')
# xlabel('Time (ms)')
# ylabel('Neuron index')
# figure()
# plot(s_mon3.t / ms, s_mon3.i, '.k')
# xlabel('Time (ms)')
# ylabel('Neuron index')

show()













# p = customized_neuron ('PC', cell_category= 'multi_comp', namespace_type='generic', eq_category= 'multi_comp',layers_idx=array([4,1])).output_neuron
# N1 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])
# N2 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])
#
#
# run(101*ms)
# device.build(directory='shortEX',
#             compile=True,
#              run=True,
#              use_GPU=True)
# p = customized_equation ('PC' , array([6,4]))
# print p.output_neuron
# print help(customized_equation)
