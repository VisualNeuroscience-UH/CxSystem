__author__ = 'V_AD'
from brian2 import *
import brian2genn
import os
from Definitions import *
set_device('genn')

class cortical_module:
    'A customizable model of cortical module for Brian2Genn'
    neurongroup_prefix = 'N'
    synapses_prefix = 'S'
    def __init__(self,path):
        _options = {
            '[G]': self.neuron_group,
            '[S]' : self.synapse
        }
        is_tag = ['[']
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
    def neuron_group (self, *args):

        args = args[0]
        layer_idx = array([])
        current_idx=  len(self.customized_neurons)
        if args[1] == 'PC' :
            exec 'args[3] = array(' + args[3] + ')'
        else:
            args[3] = int(args[3])
        group_name = '%s%d_%s'%(self.neurongroup_prefix,current_idx,args[1])
        self.neurongroups_list.append(group_name)
        self.customized_neurons.append(customized_neuron (*args[1:]).output_neuron) # layer_idx is created by dynamic compiler
        tmp_str = "self.%s = NeuronGroup(int(args[0]), model=self.customized_neurons[-1]['equation'], threshold='vm>Vcut', reset='vm=V_res', \
                    refractory = '4 * ms', namespace =self.customized_neurons[-1]['namespace'])" %group_name
        exec tmp_str

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
                if int(_post_com_idx) == 0 :
                    triple_args = []
                    triple_args.append(args[0].append('_basal'))
                    triple_args.append(args[0].append('_soma'))
                    triple_args.append(args[0].append('_a0'))
                    args = triple_args
                elif int(_post_com_idx) > 0 :
                    args[0].append('_a'+str(_post_com_idx))
        for syn in args :
            current_idx = len(self.customized_synapses)
            group_name = '%s%d_%s' % (self.synapses_prefix, current_idx, syn[3])
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












# class neuron_equations (object):
#     '''
#     Creates instances of neuron_equations which can be used in any cell. Determination of whether or not the output\
#     equation matches the nature of neuron, is to the user. Equations other than Fast Spiking, Low Threshold Spiking, \
#     Multi-Compartmental neurons and soma-only neurons should be defined in this class.
#     '''
#     def __init__(self, output_neuron):
#         '''
#         :param eq_category: The spiking pattern in the neuron ['multi_comp','soma_only','FS','LTS'].
#         :type eq_category: String
#         :param comparts: Number of Compartments in case the requested equation is 'multi_comp'.
#         :type comparts: int
#         :return:
#         :rtype:
#         '''
#         neuron_equations.all_eq_types = array(['multi_comp','soma_only','FS','LTS'])
#         assert output_neuron['eq_category'] in neuron_equations.all_eq_types, "Equation type '%s' is not defined." % output_neuron['eq_category']
#         self.final_equation = ''
#         getattr(neuron_equations, output_neuron['eq_category'])(self,output_neuron)
#
#
#     # def __str__(self):
#     #     'prints a description of the equation'
#     #     print "Description of Equation"
#
#     def multi_comp (self, output_neuron) :
#         '''
#         :param namespace_type: defines the category of the equation.
#         :type namespace_type: str
#         :param n_comp: number of compartments in the neuron
#         :type n_comp: int
#         :param layer_idx: indices of the layers in which neuron resides.
#         :type layer_idx: array
#         :param eq_template_soma: Contains template somatic equation used in Brian2.
#
#         ::
#
#             dgeX/dt = -geX/tau_eX : siemens
#             dgealphaX/dt = (geX-gealphaX)/tau_eX : siemens
#             dgi/dt = -gi/tau_i : siemens
#             dgialpha/dt = (gi-gialpha)/tau_i : siemens
#
#         :param eq_template_dend: Contains template somatic equation used in Brian2.
#         :type eq_template_dend: str
#         :param test_param: something here
#         :type test_param: some type here
#         '''
#
#         #: The template for the somatic equations used in multi compartmental neurons, the inside values could be replaced later using "Equation" function in brian2.
#         eq_template_soma = '''
#         layers_idx : 1
#         dvm/dt = (gL*(EL-vm) + gealpha * (Ee-vm) + gealphaX * (Ee-vm) + gialpha * (Ei-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) +I_dendr) / C : volt (unless refractory)
#         dge/dt = -ge/tau_e : siemens
#         dgealpha/dt = (ge-gealpha)/tau_e : siemens
#         dgeX/dt = -geX/tau_eX : siemens
#         dgealphaX/dt = (geX-gealphaX)/tau_eX : siemens
#         dgi/dt = -gi/tau_i : siemens
#         dgialpha/dt = (gi-gialpha)/tau_i : siemens
#         '''
#         #: The template for the dendritic equations used in multi compartmental neurons, the inside values could be replaced later using "Equation" function in brian2.
#         eq_template_dend = '''
#         dvm/dt = (gL*(EL-vm) + gealpha * (Ee-vm) + gealphaX * (Ee-vm) + gialpha * (Ei-vm) +I_dendr) / C : volt
#         dge/dt = -ge/tau_e : siemens
#         dgealpha/dt = (ge-gealpha)/tau_e : siemens
#         dgeX/dt = -geX/tau_eX : siemens
#         dgealphaX/dt = (geX-gealphaX)/tau_eX : siemens
#         dgi/dt = -gi/tau_i : siemens
#         dgialpha/dt = (gi-gialpha)/tau_i : siemens
#         '''
#
#         self.final_equation =(Equations(eq_template_dend, vm = "vm_basal", ge="ge_basal", gealpha="gealpha_basal",
#                 C=output_neuron['namespace']['C'][0], gL=output_neuron['namespace']['gL'][0],
#                 gi="gi_basal", geX="geX_basal", gialpha="gialpha_basal", gealphaX="gealphaX_basal",I_dendr="Idendr_basal"))
#         self.final_equation += Equations (eq_template_soma, gL=output_neuron['namespace']['gL'][1],
#                 ge='ge_soma', geX='geX_soma', gi='gi_soma', gealpha='gealpha_soma', gealphaX='gealphaX_soma',
#                 gialpha='gialpha_soma', C=output_neuron['namespace']['C'][1], I_dendr='Idendr_soma')
#         for _ii in range (output_neuron['dend_comp_num']+1): # extra dendritic compartment in the same level of soma
#             self.final_equation+=Equations(eq_template_dend, vm = "vm_a%d" %_ii, C=output_neuron['namespace']['C'][_ii],
#             gL=output_neuron['namespace']['gL'][_ii],ge="ge_a%d" %_ii, gi="gi_a%d" %_ii, geX="geX_a%d" %_ii,
#             gealpha="gealpha_a%d" %_ii, gialpha="gialpha_a%d" %_ii, gealphaX="gealphaX_a%d" %_ii,I_dendr="Idendr_a%d" %_ii)
#
#         # basal self connection
#         self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself)  : amp',
#                          gapre=1/(output_neuron['namespace']['Ra'][0]),
#                          I_dendr="Idendr_basal", vmself= "vm_basal", vmpre= "vm")
#         self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself)  + gapost*(vmpost-vmself) : amp',
#                          gapre=1/(output_neuron['namespace']['Ra'][1]),
#                          gapost=1/(output_neuron['namespace']['Ra'][0]),
#                          I_dendr="Idendr_soma" , vmself= "vm",
#                          vmpre= "vm_a0", vmpost= "vm_basal")
#         self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself) + gapost*(vmpost-vmself) : amp',
#                                  gapre=1/(output_neuron['namespace']['Ra'][2]),
#                                  gapost=1/(output_neuron['namespace']['Ra'][1]),
#                                  I_dendr="Idendr_a0" , vmself= "vm_a0" ,vmpre= "vm_a1" , vmpost= "vm")
#
#         for _ii in arange(1,output_neuron['dend_comp_num']):
#             self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself) + gapost*(vmpost-vmself) : amp',
#                              gapre=1/(output_neuron['namespace']['Ra'][_ii]),
#                              gapost=1/(output_neuron['namespace']['Ra'][_ii-1]),
#                              I_dendr="Idendr_a%d" %_ii, vmself= "vm_a%d" %_ii,
#                              vmpre= "vm_a%d" %(_ii+1), vmpost= "vm_a%d" %(_ii-1))
#
#         self.final_equation += Equations('I_dendr = gapost*(vmpost-vmself) : amp',
#                          I_dendr="Idendr_a%d"%output_neuron['dend_comp_num'] , gapost=1/(output_neuron['namespace']['Ra'][-1]),
#                          vmself= "vm_a%d"%output_neuron['dend_comp_num'], vmpost= "vm_a%d"%(output_neuron['dend_comp_num']-1))







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

CM = cortical_module (os.path.dirname(os.path.realpath(__file__)) + '/Connections.txt')

# for item in CM.neurongroups_list:
#     tmp_str = item + "= CM." + item
#     exec tmp_str
# for item in CM.synapses_list:
#     tmp_str = item + "= CM." + item
#     exec tmp_str

N0_PC = CM.N0_PC

s_mon_b = StateMonitor(N0_PC, 'vm_basal', record=0)
s_mon = StateMonitor(N0_PC, 'vm', record=0)
s_mon0 = StateMonitor(N0_PC, 'vm_a0', record=0)
s_mon1 = StateMonitor(N0_PC, 'vm_a1', record=0)
s_mon2 = StateMonitor(N0_PC, 'vm_a2', record=0)
run(1000 * ms, report='text')
device.build(directory='CXModule',
             compile=True,
             run=True,
             use_GPU=True)

f, axarr = plt.subplots(5, sharex=True)
axarr[0].plot(s_mon_b.t / ms, s_mon_b.vm_basal[0])
axarr[1].plot(s_mon.t / ms, s_mon.vm[0])
axarr[2].plot(s_mon0.t / ms, s_mon0.vm_a0[0])
axarr[3].plot(s_mon1.t / ms, s_mon1.vm_a1[0])
axarr[4].plot(s_mon2.t / ms, s_mon2.vm_a2[0])
show()


# p = customized_neuron ('PC', cell_category= 'multi_comp', namespace_type='generic', eq_category= 'multi_comp',layers_idx=array([4,1])).output_neuron
# N1 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])
# N2 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])


# run(101*ms)
# device.build(directory='shortEX',
#             compile=True,
#              run=True,
#              use_GPU=True)
# p = customized_equation ('PC' , array([6,4]))
# print p.output_neuron
# print help(customized_equation)
