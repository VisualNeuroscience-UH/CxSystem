# -*- coding: utf-8 -*-
__author__ = 'Andalibi, V., Hokkanen H., Vanni, S.'

'''
The preliminary version of this software has been developed at Aalto University 2012-2015, 
and the full version at the University of Helsinki 2013-2017. The software is distributed 
under the terms of the GNU General Public License. 
Copyright 2017 Vafa Andalibi, Henri Hokkanen and Simo Vanni.
'''


from networkx.drawing import layout
from brian2  import *
from parameter_parser import *
import random as rnd
import operator


class neuron_reference(object):
    '''
    Using this class, a dictionary object is created which contains all parameters and variables that are needed to \
    create a group of that customized cell. This dictionary will eventually be used in process of building the cortical module.\
    New types of neurons should be implemented in this class.
    '''

    def __init__(self,idx, number_of_neurons, cell_type, layers_idx, general_grid_radius ,min_distance, physio_config_df, network_center=0 + 0j):
        '''
        initialize the neuron_reference based on the arguments.

        :param number_of_neurons: number of neurons in the NeuronGroup() object.
        :param cell_type: type of cell in the NeuronGroup: currently PC, SS, BC, MC and L1i.
        :param layers_idx: indicating the layer in which the cell group is located. In case of SS, BC, MC and L1i it is an integer \
         but for PC which is a multi-compartmental neuron, it is a tuple array. This tuple numpy array defines the first \
         and last layers in which the neuron resides. So array([4,1]) means that the soma resides in layer 4 and the apical \
         dendrites which are (2 compartments) extend to layer 2/3 and 1. To avoid confusion, layer 2 is used as the indicator \
         of layer 2/3. Hence, if the last compartment of a neuron is in layer 2/3, use number 2.
        :param network_center: as the name implies, this argument defines the center of teh NeuronGroup() in visual field coordinates. The default value is 0+0j.
        :param resolution: resolution for formation of neurons in the grid. Default value is 0.1

        Main internal variables:

        * output_neuron: the main dictionary containing all the data about current Customized_neuron_group including: number of neurons, threshold, reset, refractory, neuron type, soma position(layer), dendrites layer, total number of compartments, namespace, equation, positions (both in cortical and visual coordinates).
        '''
        self.physio_config_df = physio_config_df
        neuron_reference._celltypes = array(['PC', 'SS', 'BC', 'MC', 'L1i', 'VPM'])
        assert general_grid_radius > min_distance , u'❌ The distance between cells should be less than the grid radius'
        assert cell_type in neuron_reference._celltypes, u"❌ Cell type '%s' is not defined" % cell_type  # check cell type
        assert len(layers_idx) < 3, u"❌ Length of layers_idx array is larger than 2"  # check layer index
        if len(layers_idx) == 2:
            assert layers_idx[1] < layers_idx[0], u"❌ Indices of the layer_idx array are not descending"
        elif len(layers_idx) == 1:
            assert cell_type != 'PC', u"❌ Cell type is PC but the start and end of the neuron is not defined in layers_idx"
        # final neuron is the output neuron containing equation, parameters
        self.output_neuron = {}
        self.output_neuron['idx'] = int(idx)
        self.output_neuron['number_of_neurons'] = int(number_of_neurons)
        self.output_neuron['threshold'] = 'vm>Vcut'
        self.output_neuron['reset'] = 'vm=V_res'
        self.output_neuron['refractory'] = '4 * ms'
        self.output_neuron['type'] = cell_type
        self.output_neuron['soma_layer'] = int(layers_idx[0])
        # _comparts_tmp1 & 2 are for extracting the layer of the compartments if applicable
        if self.output_neuron['type'] == 'PC':
            self._comparts_tmp1 = array(range(layers_idx[0] - 1, layers_idx[1] - 1, -1))
            self._comparts_tmp2 = delete(self._comparts_tmp1, where(
                self._comparts_tmp1 == 3)) if 3 in self._comparts_tmp1 else self._comparts_tmp1
            self.output_neuron['dends_layer'] = self._comparts_tmp2
            self.output_neuron['dend_comp_num'] = len(self.output_neuron['dends_layer'])
            self.output_neuron['total_comp_num'] = self.output_neuron['dend_comp_num'] + 3
        else:
            self.output_neuron['dends_layer'] = self.output_neuron['soma_layer']
            self.output_neuron['dend_comp_num'] = array([0])
            self.output_neuron['total_comp_num'] = array([1])
            # number of compartments if applicable

        self.output_neuron['namespace'] = neuron_parser(self.output_neuron, physio_config_df).output_namespace
        self.output_neuron['equation'] = ''

        variable_start_idx = self.physio_config_df['Variable'][self.physio_config_df['Variable'] == self.output_neuron['type']].index[0]
        try:
            variable_end_idx = self.physio_config_df['Variable'].dropna().index.tolist()[
                self.physio_config_df['Variable'].dropna().index.tolist().index(variable_start_idx) + 1]
            self.cropped_df_for_current_type = self.physio_config_df.loc[variable_start_idx:variable_end_idx - 1]
        except IndexError:
            self.cropped_df_for_current_type = self.physio_config_df.loc[variable_start_idx:]
        getattr(self, self.output_neuron['type'])()


        self.output_neuron['z_center'] = network_center
        self.output_neuron['w_center'] = 17 * log(self.output_neuron['z_center']+ 1)
        self.output_neuron['w_positions'] = self._get_w_positions(self.output_neuron['number_of_neurons'],
                                                                'fixed_grid', general_grid_radius,min_distance)
        # self.output_neuron['w_positions'] = 17 * log(self.output_neuron['z_positions'] + 1)
        self.output_neuron['z_positions'] =  map(lambda x: e ** (x/17) - 1,self.output_neuron['w_positions'] )
        print u"✅ Customized " + str(cell_type) + " neuron in layer " + str(layers_idx) + " initialized with " + \
              str(self.output_neuron['number_of_neurons']) + " neurons."



    def _get_w_positions(self, N, layout,  general_grid_radius,min_distance):

        r = general_grid_radius / mm
        possible_pos_idx = arange (-r,r,min_distance/mm)
        if layout == 'fixed_grid':
            _positions = [(rnd.choice(possible_pos_idx),rnd.choice(possible_pos_idx)) for a1,a2 in zip(range(N),range(N))]
            for idx,item in enumerate(_positions):
                while sqrt(_positions[idx][0]**2 + _positions[idx][1]**2)>r:
                    _positions[idx] =  (rnd.choice(possible_pos_idx),rnd.choice(possible_pos_idx))
            # _positions =[tuple(map(operator.add,_itm, (float(real(_centre)),float(imag(_centre))))) for _itm in _positions]
            _positions = [complex(_itm[0],_itm[1]) + self.output_neuron['w_center'] for _itm in _positions]
        return _positions

    def PC(self):
        '''
        This method build up the equation for PC neurons based on the number of compartments. The final equation is then saved in output_neuron['equation'].

        Main internal variables:

        * eq_template_soma: Contains template somatic equation, the variables in side the equation could be replaced later using "Equation" function in brian2. :

            ::

                dvm/dt = (gL*(EL-vm) + gealpha * (Ee-vm) + gealphaX * (Ee-vm) + gialpha * (Ei-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) +I_dendr) / C : volt (unless refractory)
                dge/dt = -ge/tau_e : siemens
                dgealpha/dt = (ge-gealpha)/tau_e : siemens
                dgeX/dt = -geX/tau_eX : siemens
                dgealphaX/dt = (geX-gealphaX)/tau_eX : siemens
                dgi/dt = -gi/tau_i : siemens
                dgialpha/dt = (gi-gialpha)/tau_i : siemens
                x : meter
                y : meter

        * eq_template_dend: Contains template dendritic equation:

            ::

                dvm/dt = (gL*(EL-vm) + gealpha * (Ee-vm) + gealphaX * (Ee-vm) + gialpha * (Ei-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) +I_dendr) / C : volt (unless refractory)
                dge/dt = -ge/tau_e : siemens
                dgealpha/dt = (ge-gealpha)/tau_e : siemens
                dgeX/dt = -geX/tau_eX : siemens
                dgealphaX/dt = (geX-gealphaX)/tau_eX : siemens
                dgi/dt = -gi/tau_i : siemens
                dgialpha/dt = (gi-gialpha)/tau_i : siemens

        '''

        #: The template for the somatic equations used in multi compartmental neurons, the inside values could be replaced later using "Equation" function in brian2.

        # eq_template_soma = self.value_extractor(self.cropped_df_for_current_type,'eq_template_soma')
        # eq_template_dend = self.value_extractor(self.cropped_df_for_current_type,'eq_template_dend')

        eq_template_soma = '''
        dvm/dt = ((gL*(EL-vm) + gealpha * (Ee-vm) + gealphaX * (Ee-vm) + gialpha * (Ei-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) +I_dendr) / C) +  noise_sigma*xi*taum_soma**-0.5 : volt (unless refractory)
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

        self.output_neuron['equation'] = Equations(eq_template_dend, vm="vm_basal", ge="ge_basal",
                                                   gealpha="gealpha_basal",
                                                   C=self.output_neuron['namespace']['C'][0],
                                                   gL=self.output_neuron['namespace']['gL'][0],
                                                   gi="gi_basal", geX="geX_basal", gialpha="gialpha_basal",
                                                   gealphaX="gealphaX_basal", I_dendr="Idendr_basal")
        self.output_neuron['equation'] += Equations(eq_template_soma, gL=self.output_neuron['namespace']['gL'][1],
                                                    ge='ge_soma', geX='geX_soma', gi='gi_soma', gealpha='gealpha_soma',
                                                    gealphaX='gealphaX_soma',
                                                    gialpha='gialpha_soma', C=self.output_neuron['namespace']['C'][1],
                                                    I_dendr='Idendr_soma',taum_soma=self.output_neuron['namespace']['taum_soma'])
        for _ii in range(self.output_neuron['dend_comp_num'] + 1):  # extra dendritic compartment in the same level of soma
            self.output_neuron['equation'] += Equations(eq_template_dend, vm="vm_a%d" % _ii,
                                                        C=self.output_neuron['namespace']['C'][_ii],
                                                        gL=self.output_neuron['namespace']['gL'][_ii],
                                                        ge="ge_a%d" % _ii,
                                                        gi="gi_a%d" % _ii, geX="geX_a%d" % _ii,
                                                        gealpha="gealpha_a%d" % _ii, gialpha="gialpha_a%d" % _ii,
                                                        gealphaX="gealphaX_a%d" % _ii, I_dendr="Idendr_a%d" % _ii)

        # basal self connection
        self.output_neuron['equation'] += Equations('I_dendr = gapre*(vmpre-vmself)  : amp',
                                                    gapre=1 / (self.output_neuron['namespace']['Ra'][0]),
                                                    I_dendr="Idendr_basal", vmself="vm_basal", vmpre="vm")
        self.output_neuron['equation'] += Equations('I_dendr = gapre*(vmpre-vmself)  + gapost*(vmpost-vmself) : amp',
                                                    gapre=1 / (self.output_neuron['namespace']['Ra'][1]),
                                                    gapost=1 / (self.output_neuron['namespace']['Ra'][0]),
                                                    I_dendr="Idendr_soma", vmself="vm",
                                                    vmpre="vm_a0", vmpost="vm_basal")
        self.output_neuron['equation'] += Equations('I_dendr = gapre*(vmpre-vmself) + gapost*(vmpost-vmself) : amp',
                                                    gapre=1 / (self.output_neuron['namespace']['Ra'][2]),
                                                    gapost=1 / (self.output_neuron['namespace']['Ra'][1]),
                                                    I_dendr="Idendr_a0", vmself="vm_a0", vmpre="vm_a1", vmpost="vm")

        for _ii in arange(1, self.output_neuron['dend_comp_num']):
            self.output_neuron['equation'] += Equations('I_dendr = gapre*(vmpre-vmself) + gapost*(vmpost-vmself) : amp',
                                                        gapre=1 / (self.output_neuron['namespace']['Ra'][_ii]),
                                                        gapost=1 / (self.output_neuron['namespace']['Ra'][_ii - 1]),
                                                        I_dendr="Idendr_a%d" % _ii, vmself="vm_a%d" % _ii,
                                                        vmpre="vm_a%d" % (_ii + 1), vmpost="vm_a%d" % (_ii - 1))

        self.output_neuron['equation'] += Equations('I_dendr = gapost*(vmpost-vmself) : amp',
                                                    I_dendr="Idendr_a%d" % self.output_neuron['dend_comp_num'],
                                                    gapost=1 / (self.output_neuron['namespace']['Ra'][-1]),
                                                    vmself="vm_a%d" % self.output_neuron['dend_comp_num'],
                                                    vmpost="vm_a%d" % (self.output_neuron['dend_comp_num'] - 1))

        self.output_neuron['equation'] += Equations('''x : meter
                            y : meter''')

    def BC(self):
        '''
        This method build up the equation for BC neurons. The final equation is then saved in output_neuron['equation'].

        * The equation of the neuron is as follows:

            ::

                dvm/dt = (gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + ge_soma * (Ee-vm) + gi_soma * (Ei-vm)) / C : volt (unless refractory)
                dge_soma/dt = -ge_soma/tau_e : siemens
                dgi_soma/dt = -gi_soma/tau_i : siemens
                x : meter
                y : meter
        '''
        # eq_template = self.value_extractor(self.cropped_df_for_current_type,'eq_template')
        # self.output_neuron['equation'] = Equations(eq_template, ge='ge_soma', gi='gi_soma')
        self.output_neuron['equation'] = Equations('''
            dvm/dt = ((gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + ge * (Ee-vm) + gi * (Ei-vm)) / C) +  noise_sigma*xi*taum_soma**-0.5: volt (unless refractory)
            dge/dt = -ge/tau_e : siemens
            dgi/dt = -gi/tau_i : siemens
            ''', ge='ge_soma', gi='gi_soma')

        self.output_neuron['equation'] += Equations('''x : meter
            y : meter''')

    def L1i(self):
        '''
        This method build up the equation for Layer 1 inhibitory (L1i) neurons. The final equation is then saved in output_neuron['equation'].

        * The equation of the neuron is as follows:

            ::

                dvm/dt = (gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + ge_soma * (Ee-vm) + gi_soma * (Ei-vm)) / C : volt (unless refractory)
                dge_soma/dt = -ge_soma/tau_e : siemens
                dgi_soma/dt = -gi_soma/tau_i : siemens
                x : meter
                y : meter
        '''
        # eq_template = self.value_extractor(self.cropped_df_for_current_type, 'eq_template')
        # self.output_neuron['equation'] = Equations(eq_template, ge='ge_soma', gi='gi_soma')
        self.output_neuron['equation'] = Equations('''
            dvm/dt = ((gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + ge * (Ee-vm) + gi * (Ei-vm)) / C) +  noise_sigma*xi*taum_soma**-0.5 : volt (unless refractory)
            dge/dt = -ge/tau_e : siemens
            dgi/dt = -gi/tau_i : siemens
            ''', ge='ge_soma', gi='gi_soma')

        self.output_neuron['equation'] += Equations('''x : meter
            y : meter''')


    def MC(self):
        '''
            This method build up the equation for MC neurons. The final equation is then saved in output_neuron['equation'].

            * The equation of the neuron is as follows:

                ::

                    dvm/dt = (gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + ge_soma * (Ee-vm) + gi_soma * (Ei-vm)) / C : volt (unless refractory)
                    dge_soma/dt = -ge_soma/tau_e : siemens
                    dgi_soma/dt = -gi_soma/tau_i : siemens
                    x : meter
                    y : meter
            '''
        # eq_template = self.value_extractor(self.cropped_df_for_current_type, 'eq_template')
        # self.output_neuron['equation'] = Equations(eq_template, ge='ge_soma', gi='gi_soma')

        self.output_neuron['equation'] = Equations('''
            dvm/dt = ((gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + ge * (Ee-vm) + gi * (Ei-vm)) / C)+  noise_sigma*xi*taum_soma**-0.5 : volt (unless refractory)
            dge/dt = -ge/tau_e : siemens
            dgi/dt = -gi/tau_i : siemens
            ''', ge='ge_soma', gi='gi_soma')

        self.output_neuron['equation'] += Equations('''x : meter
            y : meter''')

    def SS(self):
        '''
            This method build up the equation for SS neurons. The final equation is then saved in output_neuron['equation'].

            * The equation of the neuron is as follows:

                ::

                    dvm/dt = (gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + ge_soma * (Ee-vm) + gi_soma * (Ei-vm)) / C : volt (unless refractory)
                    dge_soma/dt = -ge_soma/tau_e : siemens
                    dgi_soma/dt = -gi_soma/tau_i : siemens
                    x : meter
                    y : meter
            '''

        # eq_template = self.value_extractor(self.cropped_df_for_current_type, 'eq_template')
        # self.output_neuron['equation'] = Equations(eq_template, ge='ge_soma', gi='gi_soma')

        self.output_neuron['equation'] = Equations('''
            dvm/dt = ((gL*(EL-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + ge * (Ee-vm) + gi * (Ei-vm)) / C)+  noise_sigma*xi*taum_soma**-0.5 : volt (unless refractory)
            dge/dt = -ge/tau_e : siemens
            dgi/dt = -gi/tau_i : siemens
            ''', ge='ge_soma', gi='gi_soma')
        self.output_neuron['equation'] += Equations('''x : meter
            y : meter''')

    def VPM(self):
        '''
        This method build up the equation for VPM neurons. No equation is needed.
        '''
        self.output_neuron['equation'] = ''


    def value_extractor(self, df, key_name):
        non_dict_indices = df['Variable'].dropna()[df['Key'].isnull()].index.tolist()
        for non_dict_idx in non_dict_indices:
            exec "%s=%s" % (df['Variable'][non_dict_idx], df['Value'][non_dict_idx])
        try:
            return eval(key_name)
        except (NameError, TypeError):
            pass
        try:
            if type(key_name) == list:
                variable_start_idx = df['Variable'][df['Variable'] == key_name[0]].index[0]
                try:
                    variable_end_idx = df['Variable'].dropna().index.tolist()[
                        df['Variable'].dropna().index.tolist().index(variable_start_idx) + 1]
                    cropped_df = df.loc[variable_start_idx:variable_end_idx-1]
                except IndexError:
                    cropped_df = df.loc[variable_start_idx:]
                return eval(cropped_df['Value'][cropped_df['Key'] == key_name[1]].item())
            else:
                try:
                    return eval(df['Value'][df['Key'] == key_name].item())
                except NameError:
                    df_reset_index = df.reset_index(drop=True)
                    df_reset_index = df_reset_index[0:df_reset_index[df_reset_index['Key'] == key_name].index[0]]
                    for neural_parameter in df_reset_index['Key'].dropna():
                        if neural_parameter  in df['Value'][df['Key'] == key_name].item():
                            exec "%s =self.value_extractor(df,neural_parameter)" % (neural_parameter)
                    return eval(df['Value'][df['Key'] == key_name].item())
                else:
                    raise('The syntax %s is not a valid syntax for physiological configuration file or the elements that comprise this syntax are not defined.'%df['Value'][df['Key'] == key_name].item())

        except NameError:
            new_key = df['Value'][df['Key'] == key_name].item().replace("']", "").split("['")
            return self.value_extractor(df,new_key)

#################
#################
################# Synapses
#################
#################



class synapse_reference(object):
    '''
        In this class, a dictionary object is created which contains all parameters and variables that are needed to \
        create a Synapses() object between two neuron group. This dictionary will eventually be used in process of \
        building the cortical module. New types of synapses should be implemented in this class.
    '''

    def __init__(self, receptor, pre_group_idx, post_group_idx, syn_type, pre_type, post_type,physio_config_df,post_comp_name='_soma'):
        '''
        initializes the synapse_reference based on its arguments.

        :param receptor: defines the type of the receptor in the synaptic connection. Currently ge and gi are implemented.
        :param pre_group_idx: The index of the pre-synaptic group.
        :param post_group_idx: The index of the post-synaptic group.
        :param syn_type: Type of the synaptic connection, currently STDP and Fixed are implemented.
        :param pre_type: Type of the pre-synaptic NeuronGroup.
        :param post_type: Type of the post-synaptic NeuronGroup.
        :param post_comp_name: Name of the target compartment in the cells of the post-synaptic NeuronGroup. The default value is "_soma" as usually soma is being targeted. In case other compartments are targeted in a PC cell, e.g. basal or apical dendrites, _basal or _apical will be used.

        Main internal variables:

        * output_synapse: the main dictionary containing all the data about current customized_synapse_group including: synaptic equations (model, pre, post), type of synapse, type of receptor, index and type of pre- and post-synaptic group, namespace for the Synapses() object, sparseness, ilam (?).
        * _name_space: An instance of brian2_obj_namespaces() object which contains all the constant parameters for this synaptic equation.

        '''
        synapse_reference.syntypes = array(['STDP', 'STDP_with_scaling', 'Fixed'])
        assert syn_type in synapse_reference.syntypes, u"❌ Cell type '%s' is not defined" % syn_type
        self.output_synapse = {}
        self.output_synapse['type'] = syn_type
        self.output_synapse['receptor'] = receptor
        # self.output_synapse['namespace_type'] = namespace_type
        # self.output_synapse['pre_type'] = pre_group_type
        self.output_synapse['pre_group_idx'] = int(pre_group_idx)
        self.output_synapse['pre_group_type'] = pre_type
        # self.output_synapse['post_type'] = post_group_type
        self.output_synapse['post_group_idx'] = int(post_group_idx)
        self.output_synapse['post_group_type'] = post_type
        self.output_synapse['post_comp_name'] = post_comp_name
        _name_space = synapse_parser(self.output_synapse, physio_config_df)
        self.output_synapse['namespace'] = {}
        self.output_synapse['namespace'] = _name_space.output_namespace
        self.output_synapse['sparseness'] = _name_space.sparseness
        self.output_synapse['ilam'] = _name_space.ilam
        getattr(self, self.output_synapse['type'])()

    def STDP(self):
        '''
        The method for implementing the STDP synaptic connection.

        '''

        self.output_synapse['equation'] = Equations('''
            wght : siemens
            wght0 : siemens
            dapre/dt = -apre/taupre : siemens (event-driven)
            dapost/dt = -apost/taupost : siemens (event-driven)
            ''')

        if self.output_synapse['namespace']['Apre'] >= 0:
            self.output_synapse['pre_eq'] = '''
                        %s+=wght
                        apre += Apre * wght0 * Cp
                        wght = clip(wght + apost, 0, wght_max)
                        ''' % (self.output_synapse['receptor'] + self.output_synapse['post_comp_name'] + '_post')
        else:
            self.output_synapse['pre_eq'] = '''
                        %s+=wght
                        apre += Apre * wght * Cd
                        wght = clip(wght + apost, 0, wght_max)
                        ''' % (self.output_synapse['receptor'] + self.output_synapse['post_comp_name'] + '_post')
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
    def STDP_with_scaling(self):
        '''
        The method for implementing the STDP synaptic connection.

        '''
        #TODO scaling to all synapses in a cell. Invert for inhibitory synapses. Check hertz for spike monitor,
        # TODO check scaling factors with simulations.
        self.output_synapse['equation'] = Equations('''
            wght0 : siemens
            dwght/dt = scaling_speed * wght * (ap_target_frequency - spike_sensor)  : siemens (event-driven)
            dapre/dt = -apre/taupre : siemens (event-driven)
            dapost/dt = -apost/taupost : siemens (event-driven)
            dspike_sensor/dt = -spike_sensor/tau_synaptic_scaling : hertz (event-driven)
            ''')

        if self.output_synapse['namespace']['Apre'] >= 0:
            self.output_synapse['pre_eq'] = '''
                        %s+=wght
                        apre += Apre * wght0 * Cp
                        wght = clip(wght + apost, 0, wght_max)
                        ''' % (self.output_synapse['receptor'] + self.output_synapse['post_comp_name'] + '_post')
        else:
            self.output_synapse['pre_eq'] = '''
                        %s+=wght
                        apre += Apre * wght * Cd
                        wght = clip(wght + apost, 0, wght_max)
                        ''' % (self.output_synapse['receptor'] + self.output_synapse['post_comp_name'] + '_post')
        if self.output_synapse['namespace']['Apost'] <= 0:
            self.output_synapse['post_eq'] = '''
                        apost += Apost * wght * Cd
                        wght = clip(wght + apre, 0, wght_max)
                        spike_sensor += 1 * hertz
                        '''
        else:
            self.output_synapse['post_eq'] = '''
                        apost += Apost * wght0 * Cp
                        wght = clip(wght + apre, 0, wght_max)
                        spike_sensor += 1 * hertz
                        '''

    def Fixed(self):
        '''
        The method for implementing the Fixed synaptic connection.

        '''
        self.output_synapse['equation'] = Equations('''
            wght:siemens
            ''')
        self.output_synapse['pre_eq'] = '''
        %s+=wght
        ''' % (self.output_synapse['receptor'] + self.output_synapse['post_comp_name'] + '_post')
