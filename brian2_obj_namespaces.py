__author__ = 'V_AD'
from brian_genn_version  import *
import sys
class synapse_namespaces(object):
    '''
    This class contains all the variables that are required for the Synapses() object namespaces. There are several reference dictionaries in this class for:

    * cw: connection weights for any connection between NeuronGroup()s.
    * sp: Sparsness values for any connection between NeuronGroup()s.
    * STDP: values for A_pre, A_post, Tau_pre and Tau_post for any connection between NeuronGroup()s.
    * dist: distribution of the neurons for connection between NeuronGroup()s.

    There are also some important internal variables:

    * Cp: Synaptic potentiation coefficient according to van Rossum J Neurosci 2000
    * Cd: Synaptic depression coefficient according to van Rossum J Neurosci 2000
    * stdp_Nsweeps: 60 in papers one does multiple trials to reach +-50% change in synapse strength. A-coefficien will be divided by this number
    * stdp_max_strength_coefficient: This value is to avoid runaway plasticity.
    * conn_prob_gain: This is used for compensation of small number of neurons and thus incoming synapses

    '''
    _weights = {
        'we_e': 0.72 * nS,
        'we_e2': 0.4 * nS,
        'we_e_FS': 0.72 * nS,  # Markram et al Cell 2015
        'we_e_LTS': 0.11 * nS,  # Markram et al Cell 2015
        'we_elocal': 0.72 * nS,
        'we_eX': 0.72 * nS,
        'we_NMDA': 0.72 * nS,
        # Not real NMDA, identical to the basic AMPA.
        # Allows implementation, though :)
        'we_i': 0.83 * nS
        #                        'we_development' : 0.01 * nS,
    }
    Cp = 0.001  # 1 #0.001 # Synaptic potentiation coefficient according to van Rossum J Neurosci 2000, here relative to initial value
    Cd = 0.003  # 1 #0.003 # Synaptic depression coefficient according to van Rossum J Neurosci 2000
    # The term (3.6 etc) is the mean number of synapses/connection, from Markram Cell 2015
    gain_parameter_E = 3.6  # 0.17*3.6 # The 0.5 is for release probability/synapse
    gain_parameter_I = 13.9  # 0.6*13.9
    gain_parameter_TC = 8.1  # 0.17*8.1
    cw = {
        'cw_in_SS' : _weights['we_e']*gain_parameter_TC,
        'cw_in_PC': _weights['we_e'] * gain_parameter_TC,
        'cw_in_BC': _weights['we_e_FS']*gain_parameter_TC,
        'cw_in_L1i': _weights['we_e_FS']*gain_parameter_TC,
        'cw_in_UMi': _weights['we_e_FS'] * gain_parameter_TC,
        'cw_SS_SS': _weights['we_e']*gain_parameter_E,
        'cw_SS_PC': _weights['we_e']*gain_parameter_E,
        'cw_SS_BC':_weights['we_eX']*gain_parameter_E,
        'cw_SS_MC': _weights['we_eX']*gain_parameter_E,
        'cw_SS_L1i': _weights['we_eX']*gain_parameter_E,
        'cw_SS_UMi': _weights['we_eX'] * gain_parameter_E,
        'cw_PC_SS': _weights['we_e']*gain_parameter_E,
        'cw_PC_PC':_weights['we_e']*gain_parameter_E,
        'cw_PC_BC':_weights['we_e_FS']*gain_parameter_E,
        'cw_PC_MC':_weights['we_e_LTS']*gain_parameter_E,
        'cw_PC_L1i':_weights['we_e_FS']*gain_parameter_E,
        'cw_PC_UMi': _weights['we_e_FS'] * gain_parameter_E,
        'cw_BC_SS':_weights['we_i']*gain_parameter_I,
        'cw_BC_PC':_weights['we_i']*gain_parameter_I,
        'cw_BC_BC':_weights['we_i']*gain_parameter_I,
        'cw_BC_MC':_weights['we_i']*gain_parameter_I,
        'cw_MC_SS':_weights['we_i']*gain_parameter_I,
        'cw_MC_PC':_weights['we_i']*gain_parameter_I,
        'cw_MC_BC':_weights['we_i']*gain_parameter_I,
        'cw_MC_MC':_weights['we_i']*gain_parameter_I,
        'cw_MC_L1i':_weights['we_i']*gain_parameter_I,
        'cw_MC_UMi': _weights['we_i'] * gain_parameter_I,
        'cw_L1i_SS':_weights['we_i']*gain_parameter_I,
        'cw_L1i_PC':_weights['we_i']*gain_parameter_I,
        'cw_L1i_L1i':_weights['we_i']*gain_parameter_I,
        'cw_UMi_SS': _weights['we_i'] * gain_parameter_I,
        'cw_UMi_PC': _weights['we_i'] * gain_parameter_I,
        'cw_UMi_L1i': _weights['we_i'] * gain_parameter_I,
        'cw_UMi_BC': _weights['we_i'] * gain_parameter_I,
        'cw_UMi_MC': _weights['we_i'] * gain_parameter_I,

        }

    stdp_Nsweeps = 60  # 60 in papers one does multiple trials to reach +-50% change in synapse strength. A-coefficien will be divided by this number
    stdp_max_strength_coefficient = 15  # to avoid runaway plasticity

    conn_prob_gain = 10  # This is used for compensation of small number of neurons and thus incoming synapses
    sp = {
        'sp_in_SS': 0.0038 * conn_prob_gain, #TODO : 0.38 sparsness in input layer cause high probabilities with ilam of 0.1. Find a good combination of ilam and sp for input layer.
        'sp_in_PC': 0.38 * conn_prob_gain,
        'sp_in_BC': 0.38 * conn_prob_gain,
        'sp_in_L1i': 0.38 * conn_prob_gain,
        'sp_in_UMi': 0.38 * conn_prob_gain,
        'sp_SS_SS': 0.081 * conn_prob_gain,
        'sp_SS_PC':  0.081 * conn_prob_gain,
        'sp_SS_BC': 0.053 * conn_prob_gain,
        'sp_SS_MC': 0.058 * conn_prob_gain,
        'sp_SS_L1i': 0.053 * conn_prob_gain,
        'sp_SS_UMi': 0.053 * conn_prob_gain,
        'sp_PC_SS':0.081 * conn_prob_gain,
        'sp_PC_PC':0.081 * conn_prob_gain,
        'sp_PC_BC':0.053 * conn_prob_gain,
        'sp_PC_MC':0.058 * conn_prob_gain,
        'sp_PC_L1i':0.053 * conn_prob_gain,
        'sp_PC_UMi': 0.053 * conn_prob_gain,
        'sp_BC_SS':0.071 * conn_prob_gain,
        'sp_BC_PC': 0.05 * conn_prob_gain,
        'sp_BC_BC':0.071 * conn_prob_gain,
        'sp_BC_MC':0.071 * conn_prob_gain,
        'sp_MC_SS':0.081 * conn_prob_gain,
        'sp_MC_PC':0.081 * conn_prob_gain,
        'sp_MC_BC':0.081 * conn_prob_gain,
        'sp_MC_MC': 0.08 * conn_prob_gain,
        'sp_MC_L1i':0.081 * conn_prob_gain,
        'sp_MC_UMi': 0.081 * conn_prob_gain,
        'sp_L1i_SS': 0.071 * conn_prob_gain,
        'sp_L1i_PC': 0.071 * conn_prob_gain,
        'sp_L1i_L1i':0.05 * conn_prob_gain,
        'sp_UMi_SS': 0.071 * conn_prob_gain,
        'sp_UMi_PC': 0.071 * conn_prob_gain,
        'sp_UMi_L1i': 0.05 * conn_prob_gain,
        'sp_UMi_BC': 0.071 * conn_prob_gain,
        'sp_UMi_MC': 0.071 * conn_prob_gain,
          }
    stdp_Nsweeps = 60  # 60 in papers one does multiple trials to reach +-50% change in synapse strength. A-coefficien will be divided by this number
    stdp_max_strength_coefficient = 15  # to avoid runaway plasticity
    stdp = {# instead of inf 2^32 -1 will be used
        'stdp_in_SS_soma': [20, -21.5, 5.4 * ms, 124.7 * ms],
        'stdp_in_PC_a4':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_in_PC_a3':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_in_PC_a2':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_in_PC_a1':[20, -21.5, 5.4 * ms, 124.7 * ms],
        'stdp_in_PC_a0': [20, -21.5, 5.4 * ms, 124.7 * ms],
        'stdp_in_PC_soma': [20, -21.5, 5.4 * ms, 124.7 * ms],
        'stdp_in_PC_basal': [20, -21.5, 5.4 * ms, 124.7 * ms],
        'stdp_in_BC_soma': [-46, -56, 39.9 * ms, 39.1 * ms],
        'stdp_in_L1i_soma': [-46, -56, 39.9 * ms, 39.1 * ms],
        'stdp_in_UMi_soma': [-46, -56, 39.9 * ms, 39.1 * ms],

        'stdp_SS_SS_soma':  [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_SS_PC_a4':  [-21, 42, 15 * ms, 103.4 * ms],
        'stdp_SS_PC_a3':[7.50, 7.00, 15.00 * ms, 103.4 * ms],
        'stdp_SS_PC_a2': [36, -28, 12.5 * ms, 103.4 * ms],
        'stdp_SS_PC_a1': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_SS_PC_a0': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_SS_PC_soma': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_SS_PC_basal': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_SS_BC_soma': [-46,-56,39.9 * ms,39.1 * ms],
        'stdp_SS_MC_soma': [240,-50, 7.1 * ms,39.1 * ms],
        'stdp_SS_L1i_soma': [-46,-56,39.9 * ms,39.1 * ms],
        'stdp_SS_UMi_soma': [-46, -56, 39.9 * ms, 39.1 * ms],

        'stdp_PC_SS_soma': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_PC_PC_a4': [-21, 42, 15 * ms, 103.4 * ms],
        'stdp_PC_PC_a3': [7.50, 7.00, 15.00 * ms, 103.4 * ms],
        'stdp_PC_PC_a2': [36, -28, 12.5 * ms, 103.4 * ms],
        'stdp_PC_PC_a1': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_PC_PC_a0': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_PC_PC_soma': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_PC_PC_basal': [76, -48, 15.9 * ms, 19.3 * ms],
        'stdp_PC_BC_soma':[-46,-56,39.9 * ms,39.1 * ms],
        'stdp_PC_MC_soma': [240,-50, 7.1 * ms,39.1 * ms],
        'stdp_PC_L1i_soma': [-46, -56, 39.9 * ms, 39.1 * ms],
        'stdp_PC_UMi_soma': [-46, -56, 39.9 * ms, 39.1 * ms],

        'stdp_BC_SS_soma':  [0,0,2147483647 * ms,2147483647 * ms], # instead of inf 2^32 -1 will be used
        'stdp_BC_PC_a4': [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_BC_PC_a3':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_BC_PC_a2':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_BC_PC_a1': [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_BC_PC_a0': [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_BC_PC_soma':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_BC_PC_basal':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_BC_BC_soma': [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_BC_MC_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_MC_L1i_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_MC_UMi_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],

        'stdp_MC_SS_soma':  [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_PC_a4': [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_PC_a3':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_PC_a2':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_PC_a1': [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_PC_a0': [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_PC_soma':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_PC_basal':[0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_BC_soma': [0,0,2147483647 * ms,2147483647 * ms],
        'stdp_MC_MC_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_MC_L1i_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_MC_UMi_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],

        'stdp_L1i_SS_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a4': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a3': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a2': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a1': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a0': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_basal': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_UMi_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_L1i_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],

        'stdp_UMi_SS_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_PC_a4': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_PC_a3': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_PC_a2': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_PC_a1': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_PC_a0': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_PC_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_PC_basal': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_UMi_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_UMi_L1i_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],

    }

    _M_V1 = 2.3

    dist = {
        'ilam_in_SS': 0.1/mm,
        'ilam_in_PC': 0.01/mm, #TODO : These parameters are still to be checked, 0.01 cause high probability eventhough the shape is similar to gaussian. It would be better if we change them to some value near 1.
        'ilam_in_BC': 0.01/mm,
        'ilam_in_L1i':0.01/mm,
        'ilam_in_UMi': 0.01 / mm,

        'ilam_SS_SS':2.3 / _M_V1 / mm,
        'ilam_SS_PC': 2.3 / _M_V1 / mm,
        'ilam_SS_BC': 0.7 / _M_V1 / mm,
        'ilam_SS_MC': 0.7 / _M_V1 / mm,
        'ilam_SS_L1i': 0.7 / _M_V1 / mm,
        'ilam_SS_UMi': 0.7 / _M_V1 / mm,

        'ilam_PC_SS': 2.3 / _M_V1 / mm,
        'ilam_PC_PC': 2.3 / _M_V1 / mm,
        'ilam_PC_BC':  2.3 / _M_V1 / mm,
        'ilam_PC_MC': 2.3 / _M_V1 / mm,
        'ilam_PC_L1i':  2.3 / _M_V1 / mm,
        'ilam_PC_UMi': 2.3 / _M_V1 / mm,

        'ilam_BC_SS':2.3 / _M_V1 / mm,
        'ilam_BC_PC':2.3 / _M_V1 / mm,
        'ilam_BC_BC': 2.3 / _M_V1 / mm,
        'ilam_BC_MC': 2.3 / _M_V1 / mm,
        'ilam_BC_UMi': 2.3 / _M_V1 / mm,
        'ilam_BC_L1i': 2.3 / _M_V1 / mm,

        'ilam_MC_SS': 0.01/mm,
        'ilam_MC_PC': 0.01/mm,
        'ilam_MC_BC': 0.01/mm,
        'ilam_MC_MC': 0.01/mm,
        'ilam_MC_L1i': 0.01/mm,
        'ilam_MC_UMi': 0.01 / mm,

        'ilam_L1i_SS':2.3 / _M_V1 / mm,
        'ilam_L1i_PC': 2.3 / _M_V1 / mm,
        'ilam_L1i_L1i': 2.3 / _M_V1 / mm,
        'ilam_L1i_UMi': 2.3 / _M_V1 / mm,

        'ilam_UMi_SS': 2.3 / _M_V1 / mm,
        'ilam_UMi_PC': 2.3 / _M_V1 / mm,
        'ilam_UMi_UMi': 2.3 / _M_V1 / mm,
        'ilam_UMi_BC': 2.3 / _M_V1 / mm,
        'ilam_UMi_MC': 2.3 / _M_V1 / mm,

    }



    def __init__(self,output_synapse):
        '''
        The initialization method for namespaces() object.

        :param output_synapse: This is the dictioanry created in customized_neuron() in brian2_obj_namespaces module. This contains all the informatino about the synaptic connection. In this class, Synaptic namespace parameters are directly added to it. Following valus are set after initialization: Cp, Cd, sparseness, ilan. Other variables are then set based on the type of the synaptic connection (STDP,Fixed).
        '''
        synapse_namespaces.type_ref = array (['STDP','Fixed'])
        assert output_synapse['type'] in synapse_namespaces.type_ref, "Error: cell type '%s' is not defined." % output_synapse['type']
        self.output_namespace = {}
        self.output_namespace['Cp'] = synapse_namespaces.Cp
        self.output_namespace['Cd'] = synapse_namespaces.Cd
        self.sparseness = synapse_namespaces.sp[
            'sp_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type'])]
        self.ilam = synapse_namespaces.dist[
            'ilam_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type'])]
        getattr(synapse_namespaces,output_synapse['type'])(self,output_synapse)


    def STDP(self,output_synapse):
        '''
        The STDP method for assigning the STDP parameters to the customized_synapses() object.

        :param output_synapse:  This is the dictioanry created in customized_neuron() in brian2_obj_namespaces module. This contains all the informatino about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP valus are set in this method: Apre, Apost, Tau_pre, Tau_post, wght_max, wght0.
        '''
        self.output_namespace['Apre'], self.output_namespace['Apost'], self.output_namespace['taupre'], \
        self.output_namespace['taupost'] = synapse_namespaces.stdp['stdp_%s_%s' % (output_synapse['pre_group_type'], \
            output_synapse['post_group_type'] + output_synapse['post_comp_name'])]
        self.output_namespace['wght_max'] = synapse_namespaces.cw['cw_%s_%s'% (output_synapse['pre_group_type'],output_synapse['post_group_type'])] * synapse_namespaces.stdp_max_strength_coefficient
        self.output_namespace['wght0'] = synapse_namespaces.cw['cw_%s_%s'% (output_synapse['pre_group_type'],output_synapse['post_group_type'])]


    def Fixed(self,output_synapse):
        '''
        The Fixed method for assigning the parameters for Fixed synaptic connection to the customized_synapses() object.

        :param output_synapse: This is the dictioanry created in customized_neuron() in brian2_obj_namespaces module. This contains all the informatino about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP valus are set in this method: wght_max, wght0.
        '''

        self.output_namespace['wght_max'] = synapse_namespaces.cw['cw_%s_%s' % (output_synapse['pre_group_type'],
                                                                                output_synapse[
                                                                                    'post_group_type'])] * synapse_namespaces.stdp_max_strength_coefficient
        self.output_namespace['wght0'] = synapse_namespaces.cw[
            'cw_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type'])]



#############################################
##################### Neurons  #############
############################################


class neuron_namespaces (object):
    'This class embeds all parameter sets associated to all neuron types and will return it as a namespace in form of dictionary'
    def __init__(self, output_neuron):
        neuron_namespaces.type_ref = array(['PC', 'SS', 'BC', 'MC','L1i'])
        assert output_neuron['type'] in neuron_namespaces.type_ref, "Error: cell type '%s' is not defined." % output_neuron['category']
        self.output_namespace = {}
        getattr(self, '_'+ output_neuron['type'])(output_neuron)


    def _PC(self,output_neuron):
        '''
        :param parameters_type: The type of parameters associated to compartmental neurons. 'Generic' is the common type. Other types could be defined when discovered in literature.
        :type parameters_type: String
        :return:
        :rtype:
        '''
        # following 3 lines are for in case you have more than one namespace for a cell type
        # namespace_type_ref = array(['generic'])
        # assert output_neuron['namespace_type'] in namespace_type_ref, "Error: namespace type '%s' is not defined."%output_neuron['namespace_type']
        # if output_neuron['namespace_type'] == namespace_type_ref[0]:
        # Capacitance, multiplied by the compartmental area to get the final C(compartment)
        Cm=(1*ufarad*cm**-2)
        # leak conductance, -''-  Amatrudo et al, 2005 (ja muut) - tuned down to fix R_in
        gl=(4.2e-5*siemens*cm**-2)
        Area_tot_pyram = 25000 *.75* um**2
        # Fractional areas of L1, L2, L3, L4, soma & L5, respectively, adapted from Bernander et al (1994) and Williams & Stuart (2002)
        fract_areas = {
            1: array([ 0.2 ,  0.03,  0.15,  0.2 ]),
            2: array([ 0.2 ,  0.03,  0.15,  0.15,  0.2 ]),
            3: array([ 0.2 ,  0.03,  0.15,  0.09,  0.15,  0.2 ]),
            4: array([ 0.2 ,  0.03,  0.15,  0.15 ,  0.09,  0.15,  0.2 ])
            #           basal  soma   a0     a1      a2      a3    a4
        }


        # total capacitance in compartmens. The *2 comes from Markram et al Cell 2015: corrects for the deindritic spine area
        self.output_namespace['C']= fract_areas[output_neuron['dend_comp_num']] * Cm * Area_tot_pyram * 2
        # total g_leak in compartments
        self.output_namespace['gL']= fract_areas[output_neuron['dend_comp_num']] * gl * Area_tot_pyram


        self.output_namespace['Vr']=-70.11 * mV
        self.output_namespace['EL'] = -70.11 * mV
        self.output_namespace['VT']=-41.61 * mV
        self.output_namespace['V_res']=-70.11 * mV
        self.output_namespace['DeltaT']=2*mV
        self.output_namespace['Vcut'] =-25 * mV


        # Dendritic parameters, index refers to layer-specific params
        self.output_namespace['Ee']= 0*mV
        self.output_namespace['Ei']= -75*mV
        self.output_namespace['Ed']= -70.11 * mV


        # Connection parameters between compartments
        self.output_namespace['Ra']= [100,80,150,150,200] * Mohm
        self.output_namespace['tau_e'] = 1.7 * ms
        self.output_namespace['tau_eX'] = 1.7 * ms
        self.output_namespace['tau_i'] = 8.3 * ms
        # return self.final_namespace



    def _BC(self,output_neuron):
        self.output_namespace['C'] = 100 * pF  # Somatosensory cortex,
        # Beierlein 2000 - Badel et al., 2008: 90 pF

        self.output_namespace['gL'] = 10 * nS  # Beierlein 2000 -  Badel et al -> 10 nS (calculated from tau_m)
        self.output_namespace['taum'] = self.output_namespace['C'] / self.output_namespace['gL']  # Badel et al. 2008: 9 ms
        self.output_namespace['Vr'] = -67.66 * mV
        self.output_namespace['EL'] = -67.66 * mV  # mean of neuro-electro portal#-64 * mV # Badel et al. 2008
        self.output_namespace['VT'] = -38.8 * mV  # mean of neuro-electro portal#self.output_namespace['EL'] + 15  * mV # Badel et al. 2008  #15
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 1.7 * ms  # Markram Cell 2015
        self.output_namespace['tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5)



    def _L1i(self,output_neuron):
        self.output_namespace['C'] = 100 * pF  # Somatosensory cortex,
        # Beierlein 2000 - Badel et al., 2008: 90 pF

        self.output_namespace['gL'] = 10 * nS  # Beierlein 2000 -  Badel et al -> 10 nS (calculated from tau_m)
        self.output_namespace['taum'] = self.output_namespace['C'] / self.output_namespace['gL']  # Badel et al. 2008: 9 ms
        self.output_namespace['Vr'] =-67.66 * mV
        self.output_namespace['EL'] = -67.66 * mV  # mean of neuro-electro portal#-64 * mV # Badel et al. 2008
        self.output_namespace['VT'] = -38.8 * mV  # mean of neuro-electro portal#self.output_namespace['EL'] + 15  * mV # Badel et al. 2008  #15
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 1.7 * ms  # Markram Cell 2015
        self.output_namespace['tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5)

    def _UMi(self,output_neuron):
        self.output_namespace['C'] = 100 * pF  # Somatosensory cortex,
        # Beierlein 2000 - Badel et al., 2008: 90 pF

        self.output_namespace['gL'] = 10 * nS  # Beierlein 2000 -  Badel et al -> 10 nS (calculated from tau_m)
        self.output_namespace['taum'] = self.output_namespace['C'] / self.output_namespace['gL']  # Badel et al. 2008: 9 ms
        self.output_namespace['Vr'] =-67.66 * mV
        self.output_namespace['EL'] = -67.66 * mV  # mean of neuro-electro portal#-64 * mV # Badel et al. 2008
        self.output_namespace['VT'] = -38.8 * mV  # mean of neuro-electro portal#self.output_namespace['EL'] + 15  * mV # Badel et al. 2008  #15
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 1.7 * ms  # Markram Cell 2015
        self.output_namespace['tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5)



    def _MC(self,output_neuron):
        self.output_namespace['C'] = 92.1 * pF  # 92.1 +- 8.4, Paluszkiewicz 2011 J Neurophysiol
        self.output_namespace['taum'] = 21.22 * ms  # HIGHLY VARYING 21.22 +- 11.2, N=3; Tau_m = 9.7 +- 1.3 Takesian 2012 J Neurophysiol; 17.57 +- 9.24 Wang 2004 J Physiol; 36.4 +- 3.7 Paluszkiewicz 2011 J Neurophysiol
        self.output_namespace['gL'] = self.output_namespace['C'] / self.output_namespace['taum']
        #        self.output_namespace['taum'] = self.output_namespace['C'] / self.output_namespace['gL'] from FS neurons

        self.output_namespace['EL'] = -60.38 * mV  # = Vr
        self.output_namespace['VT'] = -42.29 * mV
        self.output_namespace['Vr'] = -60.38 * mV
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV # inherited from FS
        self.output_namespace['DeltaT'] = 2 * mV  # inherited from FS
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']  # inherited from FS
        self.output_namespace['Ee'] = 0 * mV  # inherited from FS
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 1.7 * ms  # Markram Cell 2015
        self.output_namespace['tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5)


    def _SS(self,output_neuron):
        # Capacitance, multiplied by the compartmental area to get the final C(compartment)
        Cm = (1 * ufarad * cm ** -2)
        # leak conductance, -''-  Amatrudo et al, 2005 (ja muut) - tuned down to fix R_in
        gl = (4.2e-5 * siemens * cm ** -2)
        Area_tot_pyram = 25000 * .75 * um ** 2
        self.output_namespace['C'] =  0.03 * Cm * Area_tot_pyram * 2 # ? is it correct to take the soma part for here
        # total g_leak in compartments
        self.output_namespace['gL'] = 0.03 * gl * Area_tot_pyram
        # print self.output_namespace['C'] / self.output_namespace['gL']
        self.output_namespace['Vr'] = -70.11 * mV
        self.output_namespace['EL'] = -70.11 * mV
        self.output_namespace['VT'] = -41.61 * mV
        self.output_namespace['V_res'] = -70.11 * mV
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = -25 * mV

        # Dendritic parameters, index refers to layer-specific params
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['Ed'] = -70.11 * mV

        # Connection parameters between compartments
        self.output_namespace['Ra'] = 80 * Mohm
        self.output_namespace['tau_e'] = 1.7 * ms
        self.output_namespace['tau_eX'] = 1.7 * ms
        self.output_namespace['tau_i'] = 8.3 * ms
        # return self.final_namespace

