from __future__ import division
from brian2  import *
import numpy as np
from matplotlib import pyplot
import sys
import pandas

__author__ = 'V_AD'



class synapse_parser(object):
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

    # For _change_calcium()
    _excitatory_groups = ['PC', 'SS']
    _steep_post_inhibitory_groups = ['MC']
    _shallow_post_inhibitory_groups = ['BC']
    _steep_post = _excitatory_groups + _steep_post_inhibitory_groups
    _shallow_post = _shallow_post_inhibitory_groups

    def __init__(self,output_synapse,physio_config_df):
        '''
        The initialization method for namespaces() object.

        :param output_synapse: This is the dictionary created in neuron_reference() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this class, Synaptic namespace parameters are directly added to it. Following values are set after initialization: Cp, Cd, sparseness, ilam. Other variables are then set based on the type of the synaptic connection (STDP,Fixed).
        '''
        self.output_synapse = output_synapse
        self.physio_config_df = physio_config_df

        synapse_parser.type_ref = array (['STDP','STDP_with_scaling', 'Fixed'])
        assert output_synapse['type'] in synapse_parser.type_ref, "Cell type '%s' is not defined." % output_synapse['type']
        self.output_namespace = {}
        self.output_namespace['Cp'] = self.value_extractor(self.physio_config_df,'Cp')
        self.output_namespace['Cd'] = self.value_extractor(self.physio_config_df,'Cd')
        self.sparseness = self.value_extractor(self.physio_config_df,'sp_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type']))
        self.ilam = self.value_extractor(self.physio_config_df,'ilam_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type']))
        self.calcium_concentration = self.value_extractor(self.physio_config_df, 'calcium_concentration' )   # Change calcium concentration here or with _change_calcium()

        # Set dissociation constant for Hill equation (see change_calcium)
        if output_synapse['pre_group_type'] in self._excitatory_groups and output_synapse['post_group_type'] in self._steep_post:
            self._K12 = 2.79
        elif output_synapse['pre_group_type'] in self._excitatory_groups and output_synapse['post_group_type'] in self._shallow_post:
            self._K12 = 1.09
        else:
            self._K12 = np.average([2.79, 1.09])

        # Set (initial) weights for chosen synapse type
        getattr(synapse_parser, output_synapse['type'])(self)

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
        except ValueError:
            raise ValueError("Parameter %s not found in the configuration file."%key_name)


    def _change_calcium(self, ca):

        original_synapse_strength = self.cw_baseline_calcium
        ca0 = 2.0  # The Ca concentration in which cw_baseline_calcium is given

        calcium_factor = (pow(ca,4)/(pow(self._K12,4) + pow(ca,4))) / (pow(ca0,4)/(pow(self._K12,4) + pow(ca0,4)))
        final_synapse_strength = original_synapse_strength * calcium_factor

        return final_synapse_strength

    def STDP(self):
        '''
        The STDP method for assigning the STDP parameters to the customized_synapses() object.

        :param output_synapse:  This is the dictionary created in neuron_reference() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP values are set in this method: Apre, Apost, Tau_pre, Tau_post, wght_max, wght0.
        '''
        self.output_namespace['Apre'], self.output_namespace['Apost'], self.output_namespace['taupre'], \
        self.output_namespace['taupost'] = self.value_extractor(self.physio_config_df,'stdp_%s_%s' % (self.output_synapse['pre_group_type'], \
            self.output_synapse['post_group_type'] + self.output_synapse['post_comp_name']))
        stdp_max_strength_coefficient = self.value_extractor(self.physio_config_df,'stdp_max_strength_coefficient')
        self.output_namespace['wght_max'] = self.value_extractor(self.physio_config_df,'cw_%s_%s'% (self.output_synapse['pre_group_type'],self.output_synapse['post_group_type']))* stdp_max_strength_coefficient
        std_wght = self.value_extractor(self.physio_config_df,'cw_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / nS
        mu_wght = std_wght / 2.
        self.output_namespace['init_wght'] = '(%f * rand() + %f) * nS' % (std_wght , mu_wght)
        std_delay = self.value_extractor(self.physio_config_df,'delay_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / ms
        min_delay = std_delay / 2.
        self.output_namespace['delay'] = '(%f * rand() + %f) * ms' % (std_delay, min_delay)

    def STDP_with_scaling(self):
        '''
        The STDP method for assigning the STDP parameters to the customized_synapses() object.

        :param output_synapse:  This is the dictionary created in neuron_reference() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP values are set in this method: Apre, Apost, Tau_pre, Tau_post, wght_max, wght0.
        '''
        self.output_namespace['Apre'], self.output_namespace['Apost'], self.output_namespace['taupre'], \
        self.output_namespace['taupost'] = self.value_extractor(self.physio_config_df,'stdp_%s_%s' % (self.output_synapse['pre_group_type'], \
            self.output_synapse['post_group_type'] + self.output_synapse['post_comp_name']))
        self.output_namespace['tau_synaptic_scaling'] = self.value_extractor(self.physio_config_df,
                                                                             'tau_synaptic_scaling')
        stdp_max_strength_coefficient = self.value_extractor(self.physio_config_df,'stdp_max_strength_coefficient')
        self.output_namespace['wght_max'] = self.value_extractor(self.physio_config_df,'cw_%s_%s'% (self.output_synapse['pre_group_type'],self.output_synapse['post_group_type']))* stdp_max_strength_coefficient
        std_wght = self.value_extractor(self.physio_config_df,'cw_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / nS
        mu_wght = std_wght / 2.
        self.output_namespace['init_wght'] = '(%f * rand() + %f) * nS' % (std_wght , mu_wght)
        std_delay = self.value_extractor(self.physio_config_df,'delay_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / ms
        min_delay = std_delay / 2.
        self.output_namespace['delay'] = '(%f * rand() + %f) * ms' % (std_delay, min_delay)


    def Fixed(self):
        '''
        The Fixed method for assigning the parameters for Fixed synaptic connection to the customized_synapses() object.

        :param output_synapse: This is the dictionary created in neuron_reference() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP values are set in this method: wght_max, wght0.
        '''
        stdp_max_strength_coefficient = self.value_extractor(self.physio_config_df,'stdp_max_strength_coefficient')
        self.output_namespace['wght_max'] = self.value_extractor(self.physio_config_df,'cw_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type']))* stdp_max_strength_coefficient
        std_wght = self.value_extractor(self.physio_config_df,'cw_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / nS
        mu_wght = std_wght / 2.

        if self.calcium_concentration > 0: # For change_calcium()
            self.cw_baseline_calcium = std_wght
            std_wght = self._change_calcium(self.calcium_concentration)

        self.output_namespace['init_wght'] = '(%f * rand() + %f) * nS' % (std_wght , mu_wght)
        std_delay = self.value_extractor(self.physio_config_df,'delay_%s_%s' % (self.output_synapse['pre_group_type'], self.output_synapse['post_group_type'])) / ms
        min_delay = std_delay / 2.
        self.output_namespace['delay'] = '(%f * rand() + %f) * ms' % (std_delay, min_delay)


#############################################
##################### Neurons  #############
############################################


class neuron_parser (object):
    'This class embeds all parameter sets associated to all neuron types and will return it as a namespace in form of dictionary'
    def __init__(self, output_neuron,physio_config_df):
        self.physio_config_df = physio_config_df
        neuron_parser.type_ref = array(['PC', 'SS', 'BC', 'MC', 'L1i', 'VPM'])
        assert output_neuron['type'] in neuron_parser.type_ref, "Cell type '%s' is not defined." % output_neuron['category']
        self.output_namespace = {}
        variable_start_idx = self.physio_config_df['Variable'][self.physio_config_df['Variable'] == output_neuron['type']].index[0]
        try:
            variable_end_idx = self.physio_config_df['Variable'].dropna().index.tolist()[
                self.physio_config_df['Variable'].dropna().index.tolist().index(variable_start_idx) + 1]
            cropped_df = self.physio_config_df.loc[variable_start_idx:variable_end_idx-1]
        except IndexError:
            cropped_df = self.physio_config_df.loc[variable_start_idx:]

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
        pass

    def _L1i(self,output_neuron):
        pass

    def _VPM(self,output_neuron):
        pass

    def _MC(self,output_neuron):
        pass

    def _SS(self,output_neuron):
        pass

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
                except TypeError:
                    raise TypeError('The syntax %s is not a valid syntax for physiological configuration file or the elements that comprise this syntax are not defined.'%df['Value'][df['Key'] == key_name].item())

        except NameError:
            new_key = df['Value'][df['Key'] == key_name].item().replace("']", "").split("['")
            return self.value_extractor(df,new_key)


# if __name__ == '__main__':
#     output_synapse = {'type':'Fixed', 'pre_group_type': 'PC', 'post_group_type': 'BC'}
#
#     syns = synapse_parser(output_synapse)
#
#     ca = np.arange(0.7, 5, 0.1)
#     rfss = syns._change_calcium(ca)
#
#     # Testing
#     pyplot.plot(ca,rfss, color='blue', lw=2)
#     pyplot.xscale('log')
#     pyplot.yscale('log')
#     pyplot.xlim([0.7, 5])
#     pyplot.ylim([0.03, 10])
#     pyplot.show()