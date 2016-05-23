__author__ = 'V_AD'
from brian2 import *
import brian2genn
import os
from Definitions import *
import brian2genn_tester as bt
set_device('genn')
class cortical_module:
    'A customizable model of cortical module for Brian2Genn'
    _neurongroup_prefix = 'NG'
    _neuronnumber_prefix = 'NN'
    _neuronequation_prefix = 'NE'
    _neuronthreshold_prefix = 'NT'
    _neuronreset_prefix = 'NRes'
    _neuronref_prefix = 'NRef'
    _neuronNS_prefix = 'NNs' # name space prefix
    _synapses_prefix = 'S'
    _synapseequation_prefix = 'SE'

    def __init__(self,path,name):
        _options = {
            '[G]': self.neuron_group,
            '[S]' : self.synapse
        }
        is_tag = ['[']
        self.name = name
        self.syntax_bank = {}
        self.syntax_bank['NeuronGroups'] = []
        self.syntax_bank['Ingredients'] = []
        self.customized_neurons = []
        self.customized_synapses = []
        self.neurongroups_list = []
        self.synapses_list = []
        with open (path, 'r') as f :
            for line in f:
                if line[0]  in is_tag :
                    tag = line[line.index('['):line.index(']')+1]
                    assert tag in _options.keys(), 'The tag %s is not defined.'%tag
                else:
                    continue
                line = line.replace(tag, '')
                line = line.replace('\n', '')
                line = line.lstrip()
                args = line.split(' ')
                _options[tag](args)


        print "Cortical Module initialization Done Create an example connection "

        # indices = array([0, 1, 2])
        # times = array([1, 2, 3])*ms
        # G = SpikeGeneratorGroup(3, indices, times)
        # forward = Synapses(G,self.N0,  connect='i==j')
        # s_mon1 = SpikeMonitor(G)
        # s_mon2 = SpikeMonitor(self.N0)
        # s_mon3 = SpikeMonitor(self.N1)

        # network_obj = Network(collect())
        # for item in self.neurongroups_list +self.synapses_list:
        #     network_obj.add(item)


        # network_obj.run (1*second)


        # figure()
        # plot(s_mon1.t / ms, s_mon1.i, '.k')
        # figure()
        # plot(s_mon2.t / ms, s_mon2.i, '.k')
        # figure()
        # plot(s_mon3.t / ms, s_mon3.i, '.k')
        # xlabel('Time (ms)')
        # ylabel('Neuron index')
        # show()
    # def __str__(self):
    #     print "A summary of this cortical module: "
    def neuron_group (self, *args ):

        args = args[0]
        current_idx=  len(self.customized_neurons)
        if args[1] == 'PC' :
            exec 'args[3] = array(' + args[3] + ')'
        else:
            args[3] = int(args[3])
        self.customized_neurons.append(customized_neuron (*args[0:4]).output_neuron) # layer_idx is created by dynamic compiler
        if len(args) > 4: # in case of threshold/reset/refractory overwrite
            for arg_idx in range (4,len(args)):
                if 'threshold' in args[arg_idx] :
                    args[arg_idx] = args[arg_idx][args[arg_idx].index("'")+1:-2]
                    self.customized_neurons[-1]['threshold'] = args[arg_idx]
                elif 'reset' in args[arg_idx]:
                    args[arg_idx] = args[arg_idx][args[arg_idx].index("'")+1:-2]
                    self.customized_neurons[-1]['reset'] = args[arg_idx]
                elif 'refractory' in args[arg_idx]:
                    args[arg_idx] = args[arg_idx][args[arg_idx].index("'")+1:-2]
                    self.customized_neurons[-1]['refractory'] =  args[arg_idx]
        NG_name = self._neurongroup_prefix + str(current_idx) + '_'+args[1]
        self.neurongroups_list.append(NG_name)
        NN_name = self._neuronnumber_prefix + str(current_idx)
        NE_name = self._neuronequation_prefix + str(current_idx)
        NT_name = self._neuronthreshold_prefix + str(current_idx)
        NRes_name = self._neuronreset_prefix + str(current_idx)
        NRef_name = self._neuronref_prefix + str(current_idx)
        NNS_name = self._neuronNS_prefix + str(current_idx )

        NN_str = "%s=%s.customized_neurons[%d]['number_of_neurons']"% (NN_name, self.name ,current_idx)
        NE_str= "%s=%s.customized_neurons[%d]['equation']"% (NE_name ,self.name , current_idx)
        NT_str = "%s=%s.customized_neurons[%d]['threshold']"%(NT_name ,self.name ,current_idx)
        NRes_str = "%s=%s.customized_neurons[%d]['reset']"% (NRes_name,self.name , current_idx)
        NRef_str = "%s=%s.customized_neurons[%d]['refractory']"% (NRef_name,self.name,current_idx)
        NNS_str  = "%s=%s.customized_neurons[%d]['namespace']"% (NNS_name,self.name,current_idx)
        self.syntax_bank['Ingredients'].extend([NN_str,NE_str,NT_str,NRes_str,NRef_str,NNS_str])

        NG_str = "%s= NeuronGroup(%s, model=%s, threshold=%s, reset=%s,refractory = %s, namespace = %s)" \
                 % (NG_name , NN_name , NE_name,NT_name, NRes_name, NRef_name , NNS_name)
        self.syntax_bank['NeuronGroups'].append(NG_str)

        # tmp_str = "self.%s = NeuronGroup(self.customized_neurons[-1]['number_of_neurons'], model=self.customized_neurons[-1]['equation'], threshold='vm>Vcut', reset='vm=V_res', \
        #             refractory = '4 * ms', namespace =self.customized_neurons[-1]['namespace'])" %group_name

    # N1 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])



    def synapse(self, *args):
        _options = {
            '[C]': self.neuron_group,
        }
        _is_tag = ['[']
        # args = args[0]
        if len(args[0][2])> 1:
            arg = args[0][2]
            tag = arg[arg.index('['):arg.index(']') + 1]
            assert tag in _options.keys(), 'The synaptic tag %s is not defined.' % tag
            if tag == '[C]':
                _post_group_idx , _post_com_idx = arg.split('[' + 'C' + ']')
                args[0][2] = _post_group_idx
                if _post_com_idx[0] == '0':
                    if len(_post_com_idx) == 1:
                        triple_args = []
                        triple_args.append(args[0].append('_basal'))
                        triple_args.append(args[0].append('_soma'))
                        triple_args.append(args[0].append('_a0'))
                        args = triple_args
                    else :
                        triple_args = []
                        for tmp_idx in _post_com_idx[1:]:
                            if tmp_idx == '0':
                                triple_args.append(args[0].append('_basal'))
                            elif tmp_idx == '1':
                                triple_args.append(args[0].append('_soma'))
                            elif tmp_idx == '2':
                                triple_args.append(args[0].append('_a0'))
                        args = triple_args
                elif int(_post_com_idx) > 0 :
                    args[0].append('_a'+str(_post_com_idx))
        for syn in args :
            current_idx = len(self.customized_synapses)
            group_name = '%s%d_%s' % (self._synapses_prefix, current_idx, syn[3])
            self.synapses_list.append(group_name)
            self.customized_synapses.append(customized_synapse(*syn))
            tmp_str = "self.%s = Synapses(self.%s,self.%s,model = self.customized_synapses[-1].output_synapse['syn_eq'],\
            pre = self.customized_synapses[-1].output_synapse['pre_eq'], post = self.customized_synapses[-1].output_synapse['post_eq'],\
            namespace=self.customized_synapses[-1].output_synapse['namespace'])"\
                      %(group_name,self.neurongroups_list[self.customized_synapses[-1].output_synapse['pre_group_idx']], \
                        self.neurongroups_list[self.customized_synapses[-1].output_synapse['post_group_idx']])
            exec tmp_str
            tmp_str = "self.%s.connect('i!=j')"%group_name
            exec tmp_str
            tmp_str = "self.%s.wght=self.customized_synapses[-1].output_synapse['namespace']['wght0']" %group_name
            exec tmp_str

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

for syntax in CM.syntax_bank['Ingredients'] :
    exec syntax
for syntax in CM.syntax_bank['NeuronGroups'] :
    exec syntax






# eqs = bt.eqs
# names = bt.names
# q = 10
# tmp_str = "G%d = NeuronGroup(q , model = eqs,threshold='vm>Vcut', reset='vm=V_res', refractory = '4 * ms', namespace= names)" %1
# exec tmp_str
# H = bt.H_group
#
# eq = bt.eq
# pre = bt.pre
# post = bt.post
# syn_names = bt.syn_names
# S = Synapses(G, H, model= eq,pre = pre, post=post,namespace=syn_names)
# S.connect(4,5)

indices = array([0, 1, 2])
times = array([1, 2, 3])*ms
# Ge = SpikeGeneratorGroup(3, indices, times)
# forward = Synapses(Ge,G,  connect='i==j')
# s_mon1 = SpikeMonitor(Ge)
# s_mon2 = SpikeMonitor(G)
s_mon_b = StateMonitor(NG0_PC,'vm_basal',record = 0)
s_mon = StateMonitor(NG0_PC,'vm',record=0)
s_mon0 = StateMonitor(NG0_PC,'vm_a0',record=0)
s_mon1 = StateMonitor(NG0_PC,'vm_a1',record=0)
s_mon2 = StateMonitor(NG0_PC,'vm_a2',record=0)


run(101*ms)
device.build(directory='tester',
            compile=True,
             run=True,
             use_GPU=True)

f, axarr = plt.subplots(5, sharex=True)
axarr[0].plot(s_mon_b.t / ms, s_mon_b.vm_basal[0])
axarr[1].plot(s_mon.t / ms, s_mon.vm[0])
axarr[2].plot(s_mon0.t / ms, s_mon0.vm_a0[0])
axarr[3].plot(s_mon1.t / ms, s_mon1.vm_a1[0])
axarr[4].plot(s_mon2.t / ms, s_mon2.vm_a2[0])
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
