__author__ = 'V_AD'
from brian2  import *
import sys
import pandas

class synapse_namespaces(object):
    '''
    This class contains all the variables that are required for the Synapses() object namespaces. There are several reference dictionaries in this class for:

    * cw: connection weights for any connection between NeuronGroup()s.
    * sp: Sparseness values for any connection between NeuronGroup()s.
    * STDP: values for A_pre, A_post, Tau_pre and Tau_post for any connection between NeuronGroup()s.
    * dist: distribution of the neurons for connection between NeuronGroup()s.

    There are also some important internal variables:

    * Cp: Synaptic potentiation coefficient according to van Rossum J Neurosci 2000
    * Cd: Synaptic depression coefficient according to van Rossum J Neurosci 2000
    * stdp_Nsweeps: 60 in papers one does multiple trials to reach +-50% change in synapse strength. A-coefficient will be divided by this number
    * stdp_max_strength_coefficient: This value is to avoid runaway plasticity.
    * conn_prob_gain: This is used for compensation of small number of neurons and thus incoming synapses

    '''

    def __init__(self,output_synapse,physio_df):
        '''
        The initialization method for namespaces() object.

        :param output_synapse: This is the dictionary created in customized_neuron() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this class, Synaptic namespace parameters are directly added to it. Following values are set after initialization: Cp, Cd, sparseness, ilam. Other variables are then set based on the type of the synaptic connection (STDP,Fixed).
        '''
        self.output_synapse = output_synapse
        self.physio_df = physio_df
        synapse_namespaces.type_ref = array (['STDP','Fixed'])
        assert output_synapse['type'] in synapse_namespaces.type_ref, "Cell type '%s' is not defined." % output_synapse['type']
        self.output_namespace = {}
        self.output_namespace['Cp'] = self.value_extractor(self.physio_df,'Cp')
        self.output_namespace['Cd'] = self.value_extractor(self.physio_df,'Cd')
        self.sparseness = self.value_extractor(self.physio_df,'sp_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type']))
        self.ilam = self.value_extractor(self.physio_df,'ilam_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type']))
        getattr(synapse_namespaces,output_synapse['type'])(self)

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
                return eval(df['Value'][df['Key'] == key_name].item())
        except NameError:
            new_key = df['Value'][df['Key'] == key_name].item().replace("']", "").split("['")
            return self.value_extractor(df,new_key)

    def STDP(self):
        '''
        The STDP method for assigning the STDP parameters to the customized_synapses() object.

        :param output_synapse:  This is the dictionary created in customized_neuron() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP values are set in this method: Apre, Apost, Tau_pre, Tau_post, wght_max, wght0.
        '''
        self.output_namespace['Apre'], self.output_namespace['Apost'], self.output_namespace['taupre'], \
        self.output_namespace['taupost'] = self.value_extractor(self.physio_df,'stdp_%s_%s' % (self.output_synapse['pre_group_type'], \
            self.output_synapse['post_group_type'] + self.output_synapse['post_comp_name']))
        stdp_max_strength_coefficient = self.value_extractor(self.physio_df,'stdp_max_strength_coefficient')
        self.output_namespace['wght_max'] = self.value_extractor(self.physio_df,'cw_%s_%s'% (self.output_synapse['pre_group_type'],self.output_synapse['post_group_type']))* stdp_max_strength_coefficient
        std_wght = self.value_extractor(self.physio_df,'cw_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / nS
        mu_wght = std_wght / 2.
        self.output_namespace['wght0'] = '(%f * rand() + %f) * nS' % (std_wght , mu_wght)
        std_delay = self.value_extractor(self.physio_df,'delay_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / ms
        min_delay = std_delay / 2.
        self.output_namespace['delay'] = '(%f * rand() + %f) * ms' % (std_delay, min_delay)


    def Fixed(self):
        '''
        The Fixed method for assigning the parameters for Fixed synaptic connection to the customized_synapses() object.

        :param output_synapse: This is the dictionary created in customized_neuron() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP values are set in this method: wght_max, wght0.
        '''
        stdp_max_strength_coefficient = self.value_extractor(self.physio_df,'stdp_max_strength_coefficient')
        self.output_namespace['wght_max'] = self.value_extractor(self.physio_df,'cw_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type']))* stdp_max_strength_coefficient
        std_wght = self.value_extractor(self.physio_df,'cw_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / nS
        mu_wght = std_wght / 2.
        self.output_namespace['wght0'] = '(%f * rand() + %f) * nS' % (std_wght , mu_wght)
        std_delay = self.value_extractor(self.physio_df,'delay_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / ms
        min_delay = std_delay / 2.
        self.output_namespace['delay'] = '(%f * rand() + %f) * ms' % (std_delay, min_delay)


#############################################
##################### Neurons  #############
############################################


class neuron_namespaces (object):
    'This class embeds all parameter sets associated to all neuron types and will return it as a namespace in form of dictionary'
    def __init__(self, output_neuron,physio_df):
        self.physio_df = physio_df
        neuron_namespaces.type_ref = array(['PC', 'SS', 'BC', 'MC','L1i','VPM'])
        assert output_neuron['type'] in neuron_namespaces.type_ref, "Cell type '%s' is not defined." % output_neuron['category']
        self.output_namespace = {}
        variable_start_idx = self.physio_df['Variable'][self.physio_df['Variable'] == output_neuron['type']].index[0]
        try:
            variable_end_idx = self.physio_df['Variable'].dropna().index.tolist()[
                self.physio_df['Variable'].dropna().index.tolist().index(variable_start_idx) + 1]
            cropped_df = self.physio_df.loc[variable_start_idx:variable_end_idx-1]
        except IndexError:
            cropped_df = self.physio_df.loc[variable_start_idx:]

        for neural_parameter in cropped_df['Key'].dropna():
            self.output_namespace[neural_parameter] = self.value_extractor(cropped_df,neural_parameter)

        getattr(self, '_'+ output_neuron['type'])(output_neuron)

    def _PC(self,output_neuron):
        '''
        :param parameters_type: The type of parameters associated to compartmental neurons. 'Generic' is the common type. Other types could be defined when discovered in literature.
        :type parameters_type: String
        :return:
        :rtype:
        '''

        # total capacitance in compartments. The *2 comes from Markram et al Cell 2015: corrects for the dendritic spine area
        self.output_namespace['C']= self.output_namespace['fract_areas'][output_neuron['dend_comp_num']] * self.output_namespace['Cm'] * self.output_namespace['Area_tot_pyram'] *2
        if output_neuron['soma_layer'] in [6]: # neuroelectro portal layer5/6 capacitance
            self.output_namespace['C'] = self.output_namespace['fract_areas'][output_neuron['dend_comp_num']] * self.output_namespace['Cm'] * self.output_namespace['Area_tot_pyram']
        # total g_leak in compartments
        self.output_namespace['gL']= self.output_namespace['fract_areas'][output_neuron['dend_comp_num']] * self.output_namespace['gL'] * self.output_namespace['Area_tot_pyram']
        self.output_namespace['taum_soma'] = self.output_namespace['C'][1] / self.output_namespace['gL'][1]

    def _BC(self,output_neuron):
        self.output_namespace['taum_soma'] = self.output_namespace['C'] / self.output_namespace['gL']  # Badel et al. 2008: 9 ms
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']

    def _L1i(self,output_neuron):
        self.output_namespace['C'] = self.output_namespace['taum_soma'] * self.output_namespace['gL']  #
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  #
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']

    def _VPM(self,output_neuron):
        pass

    def _MC(self,output_neuron):
        self.output_namespace['gL'] = self.output_namespace['C'] / self.output_namespace['taum_soma']
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV # inherited from FS
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']  # inherited from FS


    def _SS(self,output_neuron):
        self.output_namespace['C']= 0.03 * self.output_namespace['Cm'] * self.output_namespace['Area_tot_pyram'] * 2 # 0.38 is summation of array([0.2, 0.03, 0.15])
        self.output_namespace['gL'] = 0.03 * self.output_namespace['gl'] * self.output_namespace['Area_tot_pyram'] # 0.38 is summation of array([0.2, 0.03, 0.15])
        self.output_namespace['taum_soma'] = self.output_namespace['C'] / self.output_namespace['gL']

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
                return eval(df['Value'][df['Key'] == key_name].item())
        except NameError:
            new_key = df['Value'][df['Key'] == key_name].item().replace("']", "").split("['")
            return self.value_extractor(df,new_key)