__author__ = 'V_AD'
from brian2 import *
import brian2genn
import turtle
import os
from namespaces import  *

set_device('genn')



class cortical_module:
    'A customizable model of cortical module for Brian2Genn'

    def __init__(self,path):
        _options = {
            '#': self.comment,
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
        run(101 * ms)
        device.build(directory='CXModule',
                    compile=True,
                     run=True,
                     use_GPU=True)

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
        current_idx=  len(self.customized_neurons)
        exec 'layer_idx = array(' + args[5] + ')'
        self.customized_neurons.append(customized_neuron (args[0], cell_category= args[2], namespace_type=args[3], eq_category= args[4],layers_idx=layer_idx).output_neuron) # layer_idx is created by dynamic compiler
        tmp_str = "self.N%d = NeuronGroup(int(args[1]), model=self.customized_neurons[-1]['equation'], threshold='vm>Vcut', reset='vm=V_res', \
                    refractory = '4 * ms', namespace =self.customized_neurons[-1]['namespace'])" %current_idx
        exec tmp_str

    # N1 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])

    def comment(self, *args):
        pass

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
            self.customized_synapses.append(customized_synapse(*syn))
            tmp_str = "self.S%d = Synapses(self.N%d,self.N%d,model = self.customized_synapses[-1].output_synapse['syn_eq'],pre = self.customized_synapses[-1].output_synapse['pre_eq'], post = self.customized_synapses[-1].output_synapse['post_eq'],namespace=self.customized_synapses[-1].output_synapse['namespace'])"%(current_idx,self.customized_synapses[-1].output_synapse['pre_group_idx'],self.customized_synapses[-1].output_synapse['post_group_idx'])
            exec tmp_str
            self.S0.connect('i != j')
            self.S0.wght = 0.72 * nS*8.1

# if targ_type == 'PC' and targ_comp_idx == 0:
#     self.output_synapse['targ_comp_name'] = ['_basal', '_soma', '_a0']


class custom_neuron_group:
    'A customizable neuron group of a specific type of cell'
    def __init__(self,):
        print "Neuron group initialization Done"
    # def __str__(self):
    #     print "A summary of this neuron group: "


class customized_synapse(object):
    def __init__(self, receptor,pre_group_idx ,post_group_idx, syn_type, post_comp_name='_soma'):
        customized_synapse.syntypes = array(['STDP'])
        assert syn_type in customized_synapse.syntypes, "Error: cell type '%s' is not defined" % syn_type
        self.output_synapse = {}
        self.output_synapse['type'] = syn_type
        self.output_synapse['receptor'] = receptor
        # self.output_synapse['namespace_type'] = namespace_type
        # self.output_synapse['pre_type'] = pre_group_type
        self.output_synapse['pre_group_idx'] = int(pre_group_idx)
        # self.output_synapse['post_type'] = post_group_type
        self.output_synapse['post_group_idx'] = int(post_group_idx)
        self.output_synapse['post_comp_name'] = post_comp_name
        self.output_synapse['namespace'] = {}
        # self.output_synapse['namespace'] = namespaces(self.output_synapse).final_namespace
        # self.output_synapse['equation'] = synaptic_equations(self.output_synapse).final_equation
        getattr(customized_synapse, self.output_synapse['type'])(self)


    def STDP(self):
        customized_synapse.stdp = {
            'stdp01_a4': [0, 0, inf, inf],
            # Plasticity not implemented. Elsewhere assuming connectivity to compartments a3 and a4 only.
            'stdp01_a3': [0, 0, inf, inf],
            'stdp01_a2': [0, 0, inf, inf],
            'stdp01_a1': [20/100., -21.5/100., 5.4*ms, 124.7*ms],  # BoD  WHY /100 , WHY not multiplied directly
            'stdp01_a0': [20/100., -21.5/100., 5.4*ms, 124.7*ms],  # BoD
            'stdp02a': [-46, -56, 39.9, 39.1],  # NBoD
            'stdp11_a4': [-21, 42, 15, 103.4],  # BoD
            'stdp11_a3': [7.50, 7.00, 15.00, 103.4],  # BoD
            'stdp11_a2': [36, -28, 12.5, 103.4],  # BoD
            'stdp11_a1': [76, -48, 15.9, 19.3],  # BoD
            'stdp11_a0': [76, -48, 15.9, 19.3],  # BoD
            'stdp12a': [-46, -56, 39.9, 39.1],  # BoD
            'stdp12b': [240, -50, 7.1, 39.1],  # BoD
            'stdp2a1': [0, 0, inf, inf],
            'stdp2b1': [0, 0, inf, inf],
            'stdp2a2a': [0, 0, inf, inf],
            'stdp2b2b': [0, 0, inf, inf],
            'stdp1Xe': [20, -21.5, 5.4, 124.7],  # NBoD
            'stdpXeXi': [-46, -56, 39.9, 39.1],  # NBoD
            'stdpXbasalXe': [0, 0, inf, inf],
            'stdp1Xi': [-46, -56, 39.9, 39.1],  # NBoD
            'stdpXiXe': [0, 0, inf, inf],
            'stdpXe1_a4': [-21, 42, 15, 103.4],  # BoD
            'stdpXe1_a3': [7.50, 7.00, 15.00, 103.4],  # BoD
            'stdpXe1_a2': [36, -28, 12.5, 103.4],  # BoD
            'stdpXe1_a1': [76, -48, 15.9, 19.3],  # BoD
            'stdpXe1_a0': [76, -48, 15.9, 19.3],  # BoD
            'stdpXe2a': [-46, -56, 39.9, 39.1],  # NBoD
            'stdpXe2b': [240, -50, 7.1, 39.1],  # NBoD
        }
        self.output_synapse['syn_eq'] = '''
            wght : siemens
            dapre/dt = -apre/taupre : siemens (event-driven)
            dapost/dt = -apost/taupost : siemens (event-driven)
            '''
        self.output_synapse['namespace']['Apre'], self.output_synapse['namespace']['Apost'], self.output_synapse['namespace']['taupre'], self.output_synapse['namespace']['taupost'] = \
            self.stdp['stdp%d%d%s' % (self.output_synapse['pre_group_idx'],self.output_synapse['post_group_idx'], self.output_synapse['post_comp_name'])]
        self.output_synapse['namespace']['wght_max'] = 0.72 * nS*8.1  *15
        self.output_synapse['namespace']['wght0'] = 0.72 * nS*8.1
        self.output_synapse['namespace']['Cp'] = 0.1
        self.output_synapse['namespace']['Cd'] =0.3
        if self.output_synapse['namespace']['Apre'] >= 0:
            self.output_synapse['pre_eq'] = '''
                        %s+=wght
                        apre += Apre * wght0 * Cp
                        wght = clip(wght + apost, 0, wght_max)
                        ''' % (self.output_synapse['receptor'] + self.output_synapse['post_comp_name'] +  '_post')
        else:
            self.output_synapse['pre_eq'] = '''
                        %s+=wght
                        apre += Apre * wght * Cd
                        wght = clip(wght + apost, 0, wght_max)
                        ''' % (self.output_synapse['receptor']+self.output_synapse['post_comp_name'] + '_post')
        if self.output_synapse['namespace']['Apost'] <= 0:
            self.output_synapse['post_eq'] = '''
                        apost += Apost * wght * Cd
                        wght = clip(wght + apre, 0, wght_max)
                        '''
        else:
            self.output_synapse['post_eq'] = '''
                        apost += Apost * wght0 * Cp
                        wght = clip(wght + apre, 0, wght_max)
                        '''



class customized_neuron(object):
    '''Using this class you will get a dictionary containing all parameters and variables that are needed to \
    create a group of that customized cell. This dictionary will eventually be used to build the cortical module.'''
    # This vairable is to keep track of all customized neurons do be able to draw it
    instances = []
    def __init__(self, cell_type,cell_category,namespace_type,  eq_category, layers_idx ):
        '''
        :param cell_type: type of cell which is either PC, SS, BC, MC, Inh[?].
        :type cell_type: string
        :param layers_idx: This tuple numpy array defines the first and last layers in which the neuron resides. So array([4,1]) means that the\
        soma resides in layer 4 and the apical dendrites which are (2 compartments) extend to layer 2/3 and 1. To avoid confusion, layer 2\
        is used as the indicator of layer 2/3. Hence, if the last compartment of a neuron is in layer 2/3, use number 2.
        :type layers_idx: numpy array
        '''
        customized_neuron.instances.append(self) # this is for tracking the instance of the class, may be can be removed and transferred to higher level
        # check cell_type
        customized_neuron._celltypes = array(['PC', 'SS', 'BC', 'MC'])
        assert cell_type in customized_neuron._celltypes, "Error: cell type '%s' is not defined" %cell_type
        # check layers_idx
        assert len(layers_idx) < 3 , "Error: length of layers_idx array is larger than 2"
        if len (layers_idx) == 2 :
            assert layers_idx[1] < layers_idx [0] , "Error: indices of the layer_idx array are not descending"
        elif len (layers_idx) == 1 :
            assert cell_type != 'PC' , "Cell type is PC but the start and end of the neuron is not defined in layers_idx"
        # final neuron is the output neuron containing equation, parameters , etc TODO
        self.output_neuron = {}
        self.output_neuron['type'] = cell_type
        self.output_neuron['category'] = cell_category
        self.output_neuron['namespace_type'] = namespace_type
        self.output_neuron['eq_category'] = eq_category
        self.output_neuron['soma_layer'] = layers_idx[0]
        # _comparts_tmp1 & 2 are for extracting the layer of the compartments if applicable
        self._comparts_tmp1 = array(range (layers_idx[0]-1,layers_idx[1]-1,-1))
        self._comparts_tmp2 = delete(self._comparts_tmp1,where(self._comparts_tmp1==3)) if 3 in self._comparts_tmp1 else self._comparts_tmp1
        self.output_neuron['dends_layer'] = array([0]) if self.output_neuron['type'] != 'PC'  else self._comparts_tmp2
        # number of compartments if applicable
        self.output_neuron['dend_comp_num'] = len (self.output_neuron['dends_layer']) if self.output_neuron['dends_layer'].all() != 0 else array([0])
        self.output_neuron['total_comp_num'] = self.output_neuron['dend_comp_num'] + 3 if self.output_neuron['type'] == 'PC' or  self.output_neuron['type'] == 'SS' else 1 # plus soma , proximal apical dendrite and basal dendrites which are in the same layer
        self.output_neuron['namespace'] = neuron_namespaces(self.output_neuron).final_namespace
        self.output_neuron['equation'] = neuron_equations(self.output_neuron).final_equation

        # self.output_neuron['equation'] = Equations(_eq_template_soma, gL=gL[N_comp], ge='ge_soma', geX='geX_soma',
        # gi='gi_soma', gealpha='gealpha_soma', gealphaX='gealphaX_soma', gialpha='gialpha_soma',
        # C=C[N_comp], I_dendr='Idendr_soma')

        #sorting the final dict to be neat
        print "Customized cell initialized"
    def __str__(self):
    #     'Prints a description of the cell'
    #     print "Description of this cell:"
        return 'Customized Neuron Object'
    def __repr__ (self):
        return 'Customized Neuron Object'




class neuron_equations (object):
    '''
    Creates instances of neuron_equations which can be used in any cell. Determination of whether or not the output\
    equation matches the nature of neuron, is to the user. Equations other than Fast Spiking, Low Threshold Spiking, \
    Multi-Compartmental neurons and soma-only neurons should be defined in this class.
    '''
    def __init__(self, output_neuron):
        '''
        :param eq_category: The spiking pattern in the neuron ['multi_comp','soma_only','FS','LTS'].
        :type eq_category: String
        :param comparts: Number of Compartments in case the requested equation is 'multi_comp'.
        :type comparts: int
        :return:
        :rtype:
        '''
        neuron_equations.all_eq_types = array(['multi_comp','soma_only','FS','LTS'])
        assert output_neuron['eq_category'] in neuron_equations.all_eq_types, "Equation type '%s' is not defined." % output_neuron['eq_category']
        self.final_equation = ''
        getattr(neuron_equations, output_neuron['eq_category'])(self,output_neuron)


    # def __str__(self):
    #     'prints a description of the equation'
    #     print "Description of Equation"

    def multi_comp (self, output_neuron) :
        '''
        :param namespace_type: defines the category of the equation.
        :type namespace_type: str
        :param n_comp: number of compartments in the neuron
        :type n_comp: int
        :param layer_idx: indices of the layers in which neuron resides.
        :type layer_idx: array
        :param eq_template_soma: Contains template somatic equation used in Brian2.

        ::

            dgeX/dt = -geX/tau_eX : siemens
            dgealphaX/dt = (geX-gealphaX)/tau_eX : siemens
            dgi/dt = -gi/tau_i : siemens
            dgialpha/dt = (gi-gialpha)/tau_i : siemens

        :param eq_template_dend: Contains template somatic equation used in Brian2.
        :type eq_template_dend: str
        :param test_param: something here
        :type test_param: some type here
        '''

        #: The template for the somatic equations used in multi compartmental neurons, the inside values could be replaced later using "Equation" function in brian2.
        eq_template_soma = '''
        layers_idx : 1
        dvm/dt = (gL*(EL-vm) + gealpha * (Ee-vm) + gealphaX * (Ee-vm) + gialpha * (Ei-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) +I_dendr) / C : volt (unless refractory)
        dge/dt = -ge/tau_e : siemens
        dgealpha/dt = (ge-gealpha)/tau_e : siemens
        dgeX/dt = -geX/tau_eX : siemens
        dgealphaX/dt = (geX-gealphaX)/tau_eX : siemens
        dgi/dt = -gi/tau_i : siemens
        dgialpha/dt = (gi-gialpha)/tau_i : siemens
        '''
        #: The template for the dendritic equations used in multi compartmental neurons, the inside values could be replaced later using "Equation" function in brian2.
        eq_template_dend = '''
        dvm/dt = (gL*(EL-vm) + gealpha * (Ee-vm) + gealphaX * (Ee-vm) + gialpha * (Ei-vm) +I_dendr) / C : volt
        dge/dt = -ge/tau_e : siemens
        dgealpha/dt = (ge-gealpha)/tau_e : siemens
        dgeX/dt = -geX/tau_eX : siemens
        dgealphaX/dt = (geX-gealphaX)/tau_eX : siemens
        dgi/dt = -gi/tau_i : siemens
        dgialpha/dt = (gi-gialpha)/tau_i : siemens
        '''

        self.final_equation =(Equations(eq_template_dend, vm = "vm_basal", ge="ge_basal", gealpha="gealpha_basal",
                C=output_neuron['namespace']['C'][0], gL=output_neuron['namespace']['gL'][0],
                gi="gi_basal", geX="geX_basal", gialpha="gialpha_basal", gealphaX="gealphaX_basal",I_dendr="Idendr_basal"))
        self.final_equation += Equations (eq_template_soma, gL=output_neuron['namespace']['gL'][1],
                ge='ge_soma', geX='geX_soma', gi='gi_soma', gealpha='gealpha_soma', gealphaX='gealphaX_soma',
                gialpha='gialpha_soma', C=output_neuron['namespace']['C'][1], I_dendr='Idendr_soma')
        for _ii in range (output_neuron['dend_comp_num']+1): # extra dendritic compartment in the same level of soma
            self.final_equation+=Equations(eq_template_dend, vm = "vm_a%d" %_ii, C=output_neuron['namespace']['C'][_ii],
            gL=output_neuron['namespace']['gL'][_ii],ge="ge_a%d" %_ii, gi="gi_a%d" %_ii, geX="geX_a%d" %_ii,
            gealpha="gealpha_a%d" %_ii, gialpha="gialpha_a%d" %_ii, gealphaX="gealphaX_a%d" %_ii,I_dendr="Idendr_a%d" %_ii)

        # basal self connection
        self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself)  : amp',
                         gapre=1/(output_neuron['namespace']['Ra'][0]),
                         I_dendr="Idendr_basal", vmself= "vm_basal", vmpre= "vm")
        self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself)  + gapost*(vmpost-vmself) : amp',
                         gapre=1/(output_neuron['namespace']['Ra'][1]),
                         gapost=1/(output_neuron['namespace']['Ra'][0]),
                         I_dendr="Idendr_soma" , vmself= "vm",
                         vmpre= "vm_a0", vmpost= "vm_basal")
        self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself) + gapost*(vmpost-vmself) : amp',
                                 gapre=1/(output_neuron['namespace']['Ra'][2]),
                                 gapost=1/(output_neuron['namespace']['Ra'][1]),
                                 I_dendr="Idendr_a0" , vmself= "vm_a0" ,vmpre= "vm_a1" , vmpost= "vm")

        for _ii in arange(1,output_neuron['dend_comp_num']):
            self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself) + gapost*(vmpost-vmself) : amp',
                             gapre=1/(output_neuron['namespace']['Ra'][_ii]),
                             gapost=1/(output_neuron['namespace']['Ra'][_ii-1]),
                             I_dendr="Idendr_a%d" %_ii, vmself= "vm_a%d" %_ii,
                             vmpre= "vm_a%d" %(_ii+1), vmpost= "vm_a%d" %(_ii-1))

        self.final_equation += Equations('I_dendr = gapost*(vmpost-vmself) : amp',
                         I_dendr="Idendr_a%d"%output_neuron['dend_comp_num'] , gapost=1/(output_neuron['namespace']['Ra'][-1]),
                         vmself= "vm_a%d"%output_neuron['dend_comp_num'], vmpost= "vm_a%d"%(output_neuron['dend_comp_num']-1))







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

cortical_module (os.path.dirname(os.path.realpath(__file__)) + '/Connections.txt')

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
