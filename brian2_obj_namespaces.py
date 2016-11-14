__author__ = 'V_AD'
from brian2  import *
import sys
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

    # From Markram et al Cell 2015, Table S6. Prescribed Parameters for Synaptic Transmission, Related to Figures 9 and 10.
    EE_weights_gain = 1
    EI_weights_gain = 1
    _weights = {
        'w_TC_E-E_connections': (0.7 * EE_weights_gain) * nS, #Cruikshank et al 2007, nature neuroscience
        'w_TC_E-I_connections': (3 * EI_weights_gain) * nS,
        'w_L23PC-L23PC': 0.68 * nS, # Not used in the current model
        'w_L4Exc-L4Exc': 0.68 * nS, # Not used in the current model
        'w_L4SS-L23PC': 0.19 * nS, # Not used in the current model
        'w_L5TTPC-L5TTPC': 1.5 * nS, # Not used in the current model
        'w_L5STPC-L5STPC': 0.8 * nS, # Not used in the current model
        'w_All_other_E-E_connections': (0.72*EE_weights_gain) * nS  ,
        'w_L5TTPC-L5MC': 0.11 * nS, # Not used in the current model
        'w_L5PC-L5BC/L5ChC': 0.72 * nS, # Not used in the current model
        'w_All_other_E-I_connections': (0.43*EI_weights_gain) * nS ,
        'w_L5MC-L5TTPC': 0.75 * nS, # Not used in the current model
        'w_L23(NBC,LBC)/L23ChC-23PC': 0.91 * nS, # Not used in the current model
        'w_All_other_I-E_connections': 0.83 * nS,
        'w_All_I-I_connections': 0.83 * nS
    }

    Cp = 0.001  # 1 #0.001 # Synaptic potentiation coefficient according to van Rossum J Neurosci 2000, here relative to initial value
    Cd = 0.003  # 1 #0.003 # Synaptic depression coefficient according to van Rossum J Neurosci 2000
    conn_prob_gain = 1  # This is used for compensation of small number of neurons and thus incoming synapses
    cw = {
        'cw_in_SS': _weights['w_TC_E-E_connections'],
        'cw_in_PC': _weights['w_TC_E-E_connections'],
        'cw_in_BC': _weights['w_TC_E-I_connections'],
        'cw_in_L1i': _weights['w_TC_E-I_connections'],
        'cw_SS_SS': _weights['w_All_other_E-E_connections'],
        'cw_SS_PC': _weights['w_All_other_E-E_connections'],
        'cw_SS_BC': _weights['w_All_other_E-I_connections'],
        'cw_SS_MC': _weights['w_All_other_E-I_connections'],
        'cw_SS_L1i': _weights['w_All_other_E-I_connections'],
        'cw_PC_SS': _weights['w_All_other_E-E_connections'],
        'cw_PC_PC': _weights['w_All_other_E-E_connections'],
        'cw_PC_BC': _weights['w_All_other_E-I_connections'],
        'cw_PC_MC': _weights['w_All_other_E-I_connections'],
        'cw_PC_L1i': _weights['w_All_other_E-I_connections'],
        'cw_BC_L1i': _weights['w_All_I-I_connections'],
        'cw_BC_SS': _weights['w_All_other_I-E_connections'],
        'cw_BC_PC': _weights['w_All_other_I-E_connections'],
        'cw_BC_BC': _weights['w_All_I-I_connections'],
        'cw_BC_MC': _weights['w_All_I-I_connections'],
        'cw_MC_SS': _weights['w_All_other_I-E_connections'],
        'cw_MC_PC': _weights['w_All_other_I-E_connections'],
        'cw_MC_BC': _weights['w_All_I-I_connections'],
        'cw_MC_MC': _weights['w_All_I-I_connections'],
        'cw_MC_L1i': _weights['w_All_I-I_connections'],
        'cw_L1i_SS': _weights['w_All_other_I-E_connections'],
        'cw_L1i_BC': _weights['w_All_I-I_connections'],
        'cw_L1i_MC': _weights['w_All_I-I_connections'],
        'cw_L1i_PC': _weights['w_All_other_I-E_connections'],
        'cw_L1i_L1i': _weights['w_All_I-I_connections'],
    }


    stdp_Nsweeps = 1  # Redundant with Cp and Cd params above. The 60 in papers one does multiple trials to reach +-50% change in synapse strength. A-coefficient will be divided by this number
    stdp_max_strength_coefficient = 15  # to avoid runaway plasticity


    sp = {
        'sp_in_SS': 0.1125 , #TODO : 0.38 sparseness in input layer cause high probabilities with ilam of 0.1. Find a good combination of ilam and sp for input layer.
        'sp_in_PC': 0.1125 ,
        'sp_in_BC': 0.1125 ,
        'sp_in_L1i': 0.1125 ,
        ###########
        ########### since the probabilities are being fetched from markram data, following lines are gonna be overwritten by them
        ###########
        'sp_SS_SS': 0.081 ,
        'sp_SS_PC':  0.081 ,
        'sp_SS_BC': 0.053 ,
        'sp_SS_MC': 0.058 ,
        'sp_SS_L1i': 0.053 ,
        'sp_PC_SS':0.081 ,
        'sp_PC_PC':0.081 ,
        'sp_PC_BC':0.053 ,
        'sp_PC_MC':0.058 ,
        'sp_PC_L1i':0.053 ,
        'sp_BC_SS':0.071 ,
        'sp_BC_PC': 0.05 ,
        'sp_BC_L1i':0.005 , #todo: check this value
        'sp_BC_BC': 0.071 ,
        'sp_BC_MC':0.071 ,
        'sp_MC_SS':0.081 ,
        'sp_MC_PC':0.081 ,
        'sp_MC_BC':0.081 ,
        'sp_MC_MC': 0.08 ,
        'sp_MC_L1i':0.081 ,
        'sp_L1i_SS': 0.071 ,
        'sp_L1i_PC': 0.071 ,
        'sp_L1i_L1i':0.05 ,
        'sp_L1i_BC':0.015 ,
        'sp_L1i_MC':0.03 ,
          }

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

        'stdp_L1i_SS_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a4': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a3': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a2': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a1': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_a0': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_PC_basal': [0, 0, 2147483647 * ms, 2147483647 * ms],
        'stdp_L1i_L1i_soma': [0, 0, 2147483647 * ms, 2147483647 * ms],

    }

    lambda_LGNtoV1 = 1 / mm
    lambda_V1local = 0.81 / mm  # was 2.3 deg-1 => 1/(17*np.log(1+5+((1/2.3)/2))-17*np.log(1+5-((1/2.3)/2))),
    lambda_V1toX = 0.10 / mm  # 1 / (17 * np.log(1 + 5 + ((1 / 0.3) / 2)) - 17 * np.log(1 + 5 - ((1 / 0.3) / 2)))
    lambda_MCtoV1 = 0.10 / mm

    dist = {
        'ilam_in_SS':  lambda_LGNtoV1,
        'ilam_in_PC':  lambda_LGNtoV1,
        'ilam_in_BC':  lambda_LGNtoV1,
        'ilam_in_L1i': lambda_LGNtoV1,

        'ilam_SS_SS':  lambda_V1local,
        'ilam_SS_PC':  lambda_V1local,
        'ilam_SS_BC':  lambda_V1local,
        'ilam_SS_MC':  lambda_V1local,
        'ilam_SS_L1i': lambda_V1local,

        'ilam_PC_SS':  lambda_V1local,
        'ilam_PC_PC':  lambda_V1local,
        'ilam_PC_BC':  lambda_V1local,
        'ilam_PC_MC':  lambda_V1local,
        'ilam_PC_L1i': lambda_V1local,

        'ilam_BC_SS':  lambda_V1local,
        'ilam_BC_PC':  lambda_V1local,
        'ilam_BC_BC':  lambda_V1local,
        'ilam_BC_MC':  lambda_V1local,
        'ilam_BC_L1i': lambda_V1local,

        'ilam_MC_SS':  lambda_MCtoV1,
        'ilam_MC_PC':  lambda_MCtoV1,
        'ilam_MC_BC':  lambda_MCtoV1,
        'ilam_MC_MC':  lambda_MCtoV1,
        'ilam_MC_L1i': lambda_MCtoV1,

        'ilam_L1i_SS':  lambda_V1local,
        'ilam_L1i_PC':  lambda_V1local,
        'ilam_L1i_BC':  lambda_V1local,
        'ilam_L1i_MC':  lambda_V1local,
        'ilam_L1i_L1i': lambda_V1local
    }


    delay = { # this values are all set to 3*ms since in VCX all values are set to 3*ms
        'delay_in_SS':3.0*ms,
        'delay_in_PC': 3.0*ms,
        'delay_in_BC': 3.0*ms,
        'delay_in_L1i':3.0*ms,

        'delay_SS_SS': 3.0*ms,
        'delay_SS_PC': 3.0*ms,
        'delay_SS_BC': 3.0*ms,
        'delay_SS_MC': 3.0*ms,
        'delay_SS_L1i': 3.0*ms,

        'delay_PC_SS': 3.0*ms,
        'delay_PC_PC': 3.0*ms,
        'delay_PC_BC': 3.0*ms,
        'delay_PC_MC': 3.0*ms,
        'delay_PC_L1i': 3.0*ms,

        'delay_BC_SS': 3.0*ms,
        'delay_BC_PC': 3.0*ms,
        'delay_BC_BC': 3.0*ms,
        'delay_BC_MC': 3.0*ms,
        'delay_BC_L1i': 3.0*ms,

        'delay_MC_SS': 3.0*ms,
        'delay_MC_PC': 3.0*ms,
        'delay_MC_BC': 3.0*ms,
        'delay_MC_MC': 3.0*ms,
        'delay_MC_L1i': 3.0*ms,

        'delay_L1i_SS': 3.0*ms,
        'delay_L1i_PC': 3.0*ms,
        'delay_L1i_BC': 3.0*ms,
        'delay_L1i_MC': 3.0*ms,
        'delay_L1i_L1i': 3.0*ms,

        }

    def __init__(self,output_synapse):
        '''
        The initialization method for namespaces() object.

        :param output_synapse: This is the dictionary created in customized_neuron() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this class, Synaptic namespace parameters are directly added to it. Following values are set after initialization: Cp, Cd, sparseness, ilam. Other variables are then set based on the type of the synaptic connection (STDP,Fixed).
        '''
        synapse_namespaces.type_ref = array (['STDP','Fixed'])
        assert output_synapse['type'] in synapse_namespaces.type_ref, "Cell type '%s' is not defined." % output_synapse['type']
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

        :param output_synapse:  This is the dictionary created in customized_neuron() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP values are set in this method: Apre, Apost, Tau_pre, Tau_post, wght_max, wght0.
        '''
        self.output_namespace['Apre'], self.output_namespace['Apost'], self.output_namespace['taupre'], \
        self.output_namespace['taupost'] = synapse_namespaces.stdp['stdp_%s_%s' % (output_synapse['pre_group_type'], \
            output_synapse['post_group_type'] + output_synapse['post_comp_name'])]
        self.output_namespace['wght_max'] = synapse_namespaces.cw['cw_%s_%s'% (output_synapse['pre_group_type'],output_synapse['post_group_type'])] * synapse_namespaces.stdp_max_strength_coefficient
        std_wght = synapse_namespaces.cw['cw_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type'])] / nS
        mu_wght = std_wght / 2.
        self.output_namespace['wght0'] = '(%f * rand() + %f) * nS' % (std_wght , mu_wght)
        std_delay = synapse_namespaces.delay['delay_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type'])] / ms
        min_delay = std_delay / 2.
        self.output_namespace['delay'] = '(%f * rand() + %f) * ms' % (std_delay, min_delay)


    def Fixed(self,output_synapse):
        '''
        The Fixed method for assigning the parameters for Fixed synaptic connection to the customized_synapses() object.

        :param output_synapse: This is the dictionary created in customized_neuron() in brian2_obj_namespaces module. This contains all the information about the synaptic connection. In this method, STDP parameters are directly added to this variable. Following STDP values are set in this method: wght_max, wght0.
        '''

        self.output_namespace['wght_max'] = synapse_namespaces.cw['cw_%s_%s' % (output_synapse['pre_group_type'],
                                                                                output_synapse[
                                                                                    'post_group_type'])] * synapse_namespaces.stdp_max_strength_coefficient
        std_wght = synapse_namespaces.cw['cw_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type'])] / nS
        mu_wght = std_wght / 2.
        self.output_namespace['wght0'] = '(%f * rand() + %f) * nS' % (std_wght , mu_wght)
        std_delay = synapse_namespaces.delay['delay_%s_%s' % (output_synapse['pre_group_type'], output_synapse['post_group_type'])] / ms
        min_delay = std_delay / 2.
        self.output_namespace['delay'] = '(%f * rand() + %f) * ms' % (std_delay, min_delay)


#############################################
##################### Neurons  #############
############################################


class neuron_namespaces (object):
    'This class embeds all parameter sets associated to all neuron types and will return it as a namespace in form of dictionary'
    def __init__(self, output_neuron):
        neuron_namespaces.type_ref = array(['PC', 'SS', 'BC', 'MC','L1i','VPM'])
        assert output_neuron['type'] in neuron_namespaces.type_ref, "Cell type '%s' is not defined." % output_neuron['category']
        self.output_namespace = {}
        getattr(self, '_'+ output_neuron['type'])(output_neuron)


    def _PC(self,output_neuron):
        '''
        :param parameters_type: The type of parameters associated to compartmental neurons. 'Generic' is the common type. Other types could be defined when discovered in literature.
        :type parameters_type: String
        :return:
        :rtype:
        '''
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


        # total capacitance in compartments. The *2 comes from Markram et al Cell 2015: corrects for the dendritic spine area
        self.output_namespace['C']= fract_areas[output_neuron['dend_comp_num']] * Cm * Area_tot_pyram *2
        if output_neuron['soma_layer'] in [6]: # neuroelectro portal layer5/6 capacitance
            self.output_namespace['C'] = fract_areas[output_neuron['dend_comp_num']] * Cm * Area_tot_pyram
        # total g_leak in compartments
        self.output_namespace['gL']= fract_areas[output_neuron['dend_comp_num']] * gl * Area_tot_pyram
        self.output_namespace['taum_soma'] = self.output_namespace['C'][1] / self.output_namespace['gL'][1]
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

        # Synaptic time constants
        self.output_namespace['tau_e'] = 3 * ms  # 1.7 ms from Markram Cell 2015. This however misses NMDA contribution (12% according to Markram Cell 2015). Given this proportion and AMPA tau 3 ms and NMDA tau 200 ms(NMDA fast decay; both from Spruston JPhysiol 1995), we get double exponential decay
        self.output_namespace['tau_eX'] = 3 * ms
        self.output_namespace['tau_i'] = 8.3 * ms
        # return self.final_namespace

    def _BC(self,output_neuron):
        self.output_namespace['C'] = 100 * pF  # Somatosensory cortex,
        # # Beierlein 2000 - Badel et al., 2008: 90 pF
        # self.output_namespace['C'] = 60 * pF  # neuroelectro portal

        self.output_namespace['gL'] = 10 * nS  # Beierlein 2000 -  Badel et al -> 10 nS (calculated from tau_m)
        self.output_namespace['taum_soma'] = self.output_namespace['C'] / self.output_namespace['gL']  # Badel et al. 2008: 9 ms
        self.output_namespace['Vr'] = -67.66 * mV
        self.output_namespace['EL'] = -67.66 * mV  # mean of neuro-electro portal#-64 * mV # Badel et al. 2008
        self.output_namespace['VT'] = -38.8 * mV  # mean of neuro-electro portal#self.output_namespace['EL'] + 15  * mV # Badel et al. 2008  #15
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 3 * ms  # 1.7 ms from Markram Cell 2015. This however misses NMDA contribution (12% according to Markram Cell 2015). Given this proportion and AMPA tau 3 ms and NMDA tau 200 ms(NMDA fast decay; both from Spruston JPhysiol 1995), we get double exponential decay
        self.output_namespace['tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5), also Salin 1996 JNeurophysiol gives 8.6 ms

    def _L1i(self,output_neuron):
        self.output_namespace['gL'] = 3.2 * nS  # 3.2 nsiemens mean of cell types in L1, Muralidhar 2014 Front Neuroanat, Table 3, mean of 1/"input resistance for steady state"
        self.output_namespace['taum_soma'] =19.8 * ms  #  19.8 ms mean of cell types in L1, Muralidhar 2014 Front Neuroanat, Table 3, mean of "time constant for delta pulse"
        self.output_namespace['C'] = self.output_namespace['taum_soma'] * self.output_namespace['gL']  #
        self.output_namespace['Vr'] =-67.66 * mV
        self.output_namespace['EL'] = -67.66 * mV  #
        self.output_namespace['VT'] = -36.8 * mV  # -36.8 mV, mean of cell types in L1, Muralidhar 2014 Front Neuroanat, Table 3, mean of "ap threshold"
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  #
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 10 * ms  # 10 ms LateSpiking Chu 2003 JNeurosci,
        self.output_namespace['tau_i'] = 336.2 * ms  # 336.2 ms, mean of cell types in L1, Muralidhar 2014 Front Neuroanat, text page 10. Combination of GABA-A and GABA-B contributions. Definition of decay time different but order of magnitude right

    def _VPM(self,output_neuron):
        pass


    def _MC(self,output_neuron):
        self.output_namespace['C'] = 92.1 * pF  # 92.1 +- 8.4, Paluszkiewicz 2011 J Neurophysiol
        # self.output_namespace['C'] = 60 * pF  # neuroelectro portal

        self.output_namespace['taum_soma'] = 21.22 * ms  # HIGHLY VARYING 21.22 +- 11.2, N=3; Tau_m = 9.7 +- 1.3 Takesian 2012 J Neurophysiol; 17.57 +- 9.24 Wang 2004 J Physiol; 36.4 +- 3.7 Paluszkiewicz 2011 J Neurophysiol
        self.output_namespace['gL'] = self.output_namespace['C'] / self.output_namespace['taum_soma']
        #        self.output_namespace['taum_soma'] = self.output_namespace['C'] / self.output_namespace['gL'] from FS neurons

        self.output_namespace['EL'] = -60.38 * mV  # = Vr
        self.output_namespace['VT'] = -42.29 * mV
        self.output_namespace['Vr'] = -60.38 * mV
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV # inherited from FS
        self.output_namespace['DeltaT'] = 2 * mV  # inherited from FS
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']  # inherited from FS
        self.output_namespace['Ee'] = 0 * mV  # inherited from FS
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 3 * ms  # Markram Cell 2015
        self.output_namespace['tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5)


    def _SS(self,output_neuron):
        # Capacitance, multiplied by the compartmental area to get the final C(compartment)
        Cm = (1 * ufarad * cm ** -2)
        # leak conductance, -''-  Amatrudo et al, 2005 (ja muut) - tuned down to fix R_in
        gl = (4.2e-5 * siemens * cm ** -2)
        Area_tot_pyram = 25000 * .75 * um ** 2
        self.output_namespace['C']= 0.03 * Cm * Area_tot_pyram * 2 # 0.38 is summation of array([0.2, 0.03, 0.15])
        # self.output_namespace['C'] =  0.03 * Cm * Area_tot_pyram * 2 # ? is it correct to take the soma part for here total g_leak in compartments
        self.output_namespace['gL'] = 0.03 * gl * Area_tot_pyram # 0.38 is summation of array([0.2, 0.03, 0.15])
        # print self.output_namespace['C'] / self.output_namespace['gL']
        self.output_namespace['taum_soma'] = self.output_namespace['C'] / self.output_namespace['gL']
        self.output_namespace['Vr'] = -70 * mV
        self.output_namespace['EL'] = -70 * mV
        self.output_namespace['VT'] = -45 * mV
        self.output_namespace['V_res'] = -70 * mV
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = -25 * mV

        # Dendritic parameters, index refers to layer-specific params
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['Ed'] = -70 * mV

        # Connection parameters between compartments
        self.output_namespace['Ra'] = 80 * Mohm
        self.output_namespace['tau_e'] = 3 * ms
        self.output_namespace['tau_eX'] = 3 * ms
        self.output_namespace['tau_i'] = 8.3 * ms
        # return self.final_namespace

