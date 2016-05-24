__author__ = 'V_AD'
from brian2 import *

class synapse_namespaces(object):
    weights = {
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
    Cp = 0.1  # 1 #0.001 # Synaptic potentiation coefficient according to van Rossum J Neurosci 2000, here relative to initial value
    Cd = 0.3  # 1 #0.003 # Synaptic depression coefficient according to van Rossum J Neurosci 2000
    # The term (3.6 etc) is the mean number of synapses/connection, from Markram Cell 2015
    gain_parameter_E = 3.6  # 0.17*3.6 # The 0.5 is for release probability/synapse
    gain_parameter_I = 13.9  # 0.6*13.9
    gain_parameter_TC = 8.1  # 0.17*8.1
    cw = {'cw01': weights['we_e'] * gain_parameter_TC,
                             # Putting this to dev gives only local sparse activation
                             'cw02a': weights['we_e_FS'] * gain_parameter_TC,
                             'cw12a': weights['we_e_FS'] * gain_parameter_E,
                             'cw12b': weights['we_e_LTS'] * gain_parameter_E,
                             'cw11': weights['we_e'] * gain_parameter_E,
                             'cw11local': weights['we_elocal'] * gain_parameter_E,
                             'cw2a1': weights['we_i'] * gain_parameter_I,  # *12,
                             'cw2b1': weights['we_i'] * gain_parameter_I,
                             'cw2a2a': weights['we_i'] * gain_parameter_I,
                             'cw2b2b': weights['we_i'] * gain_parameter_I,
                             'cwXbasalXe': weights['we_eX'] * gain_parameter_E,
                             'cw1Xe': weights['we_e'] * gain_parameter_E,
                             'cw1Xi': weights['we_eX'] * gain_parameter_E,
                             'cwXeXi': weights['we_e2'] * gain_parameter_E,
                             'cwXiXe': weights['we_i'] * gain_parameter_I,
                             'cwXe1': weights['we_NMDA'] * gain_parameter_E,
                             'cwXe2a': weights['we_eX'] * gain_parameter_E,
                             'cwXe2b': weights['we_eX'] * gain_parameter_E
                             }

    stdp_Nsweeps = 60  # 60 in papers one does multiple trials to reach +-50% change in synapse strength. A-coefficien will be divided by this number
    stdp_max_strength_coefficient = 15  # to avoid runaway plasticity
    stdp = {
        'stdp01_a4': [0, 0, inf, inf],
        # Plasticity not implemented. Elsewhere assuming connectivity to compartments a3 and a4 only.
        'stdp01_a3': [0, 0, inf, inf],
        'stdp01_a2': [0, 0, inf, inf],
        'stdp01_a1': [20 / 100., -21.5 / 100., 5.4 * ms, 124.7 * ms],  # BoD  WHY /100 , WHY not multiplied directly
        'stdp01_a0': [20 / 100., -21.5 / 100., 5.4 * ms, 124.7 * ms],  # BoD
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

    stdp_Nsweeps = 60  # 60 in papers one does multiple trials to reach +-50% change in synapse strength. A-coefficien will be divided by this number
    stdp_max_strength_coefficient = 15  # to avoid runaway plasticity

    conn_prob_gain = 10  # This is used for compensation of small number of neurons and thus incoming synapses
    sp = {'sp01': 0.38 * conn_prob_gain,
               # 3.2 x release sites, 1.5 x release probability of corticocortical connections. # Was 1 * conn_prob_gain, # the 1 is from hat. thalamocortical probability
               'sp02a': 0.38 * conn_prob_gain,  # 1 * conn_prob_gain ,
               'sp11': 0.081 * conn_prob_gain,
               # Unweighted averages of within layer connections from nmc-portal. Connections with small number of synapses dropped
               'sp12a': 0.053 * conn_prob_gain,
               # Average for E-I conn across layers, large and small baskett cells, nmc-portal
               'sp12b': 0.058 * conn_prob_gain,
               'sp2a1': 0.071 * conn_prob_gain,  # Average N synapses for I-conn, Markram et al Cell 2015
               'sp2b1': 0.081 * conn_prob_gain,
               'sp2a2a': 0.05 * conn_prob_gain,  # Average N synapses for I-conn, NMC portel
               'sp2b2b': 0.08 * conn_prob_gain,  # NMC portel
               'sp1Xe': 0.081 * conn_prob_gain,
               'spXeXi': 0.053 * conn_prob_gain,  # from basket cells only
               'spXbasalXe': .016,
               'sp1Xi': 0.053 * conn_prob_gain,  # Check connection: spreads activation like grazy
               'spXiXe': 0.071 * conn_prob_gain,
               'spXe1': 0.081 * conn_prob_gain,  # using local here, update when data available
               'spXe2a': 0.053 * conn_prob_gain,
               'spXe2b': 0.058 * conn_prob_gain
               #                   'sp_development' : 2.5  # for plastic synapses
               }

    def __init__(self,output_synapse):
            # synapse_namespaces.type_ref = array (['STDP'])
            # assert output_synapse['type'] in synapse_namespaces.type_ref, "Error: cell type '%s' is not defined." % output_synapse['type']
            # self.output_namespace = {}
            # getattr(synapse_namespaces,output_synapse['type'])(self)
            self.output_namespace = {}
            self.output_namespace['Apre'], self.output_namespace['Apost'], self.output_namespace['taupre'], \
            self.output_namespace['taupost'] = synapse_namespaces.stdp['stdp%d%d%s' % (output_synapse['pre_group_idx'], \
                output_synapse['post_group_idx'], output_synapse['post_comp_name'])]
            self.output_namespace['wght_max'] = synapse_namespaces.cw['cw%s%s'% (output_synapse['pre_group_idx'],output_synapse['post_group_idx'])] * synapse_namespaces.stdp_max_strength_coefficient
            self.output_namespace['wght0'] = synapse_namespaces.cw['cw%s%s'% (output_synapse['pre_group_idx'],output_synapse['post_group_idx'])]
            self.output_namespace['Cp'] = synapse_namespaces.Cp
            self.output_namespace['Cd'] = synapse_namespaces.Cd
            self.probabiliy = synapse_namespaces.sp['sp%d%d'%()]


            # output_synapse['namespace']['Apre'], output_synapse['namespace']['Apost'], output_synapse['namespace']['taupre'], \
            #     output_synapse['namespace']['taupost'] = synapse_namespaces.stdp['stdp%d%d%s' % (output_synapse['pre_group_idx'], \
            #     output_synapse['post_group_idx'], output_synapse['post_comp_name'])]
            # output_synapse['namespace']['wght_max'] = synapse_namespaces.cw['cw%s%s'% (output_synapse['pre_group_idx'],output_synapse['post_group_idx'])] * synapse_namespaces.stdp_max_strength_coefficient
            # output_synapse['namespace']['wght0'] = synapse_namespaces.cw['cw%s%s'% (output_synapse['pre_group_idx'],output_synapse['post_group_idx'])]
            # output_synapse['namespace']['Cp'] = synapse_namespaces.Cp
            # output_synapse['namespace']['Cd'] = synapse_namespaces.Cd




    #############################################
##################### Neurons  #############
############################################


class neuron_namespaces (object):
    'This class embeds all parameter sets associated to all neuron types and will return it as a namespace in form of dictionary'
    def __init__(self, output_neuron):
        neuron_namespaces.type_ref = array(['PC', 'SS', 'BC', 'MC'])
        assert output_neuron['type'] in neuron_namespaces.type_ref, "Error: cell type '%s' is not defined." % output_neuron['category']
        self.output_namespace = {}
        getattr(neuron_namespaces, output_neuron['type'])(self,output_neuron)



    def PC(self,output_neuron):
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
            4: array([ 0.2 ,  0.03,  0.15,  0.5 ,  0.09,  0.15,  0.2 ])
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
        self.output_namespace['Vcut'] = -25 * mV


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



    def _BC(self):
        self.output_namespace['C'] = 100 * pF  # Somatosensory cortex,
        # Beierlein 2000 - Badel et al., 2008: 90 pF

        self.output_namespace['gL'] = 10 * nS  # Beierlein 2000 -  Badel et al -> 10 nS (calculated from tau_m)
        self.output_namespace['taum'] = self.output_namespace['C'] / self.output_namespace['gL']  # Badel et al. 2008: 9 ms

        self.output_namespace['EL'] = -67.66 * mV  # mean of neuro-electro portal#-64 * mV # Badel et al. 2008
        self.output_namespace['VT'] = -38.8 * mV  # mean of neuro-electro portal#self.output_namespace['EL'] + 15  * mV # Badel et al. 2008  #15
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 1.7 * ms  # Markram Cell 2015
        self.output_namespace['tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5)



    def _L1i(self):
        self.output_namespace['C'] = 100 * pF  # Somatosensory cortex,
        # Beierlein 2000 - Badel et al., 2008: 90 pF

        self.output_namespace['gL'] = 10 * nS  # Beierlein 2000 -  Badel et al -> 10 nS (calculated from tau_m)
        self.output_namespace['taum'] = self.output_namespace['C'] / self.output_namespace[
            'gL']  # Badel et al. 2008: 9 ms

        self.output_namespace['EL'] = -67.66 * mV  # mean of neuro-electro portal#-64 * mV # Badel et al. 2008
        self.output_namespace[
            'VT'] = -38.8 * mV  # mean of neuro-electro portal#self.output_namespace['EL'] + 15  * mV # Badel et al. 2008  #15
        self.output_namespace['V_res'] = self.output_namespace[
                                             'VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV
        self.output_namespace['DeltaT'] = 2 * mV
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']
        self.output_namespace['Ee'] = 0 * mV
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 1.7 * ms  # Markram Cell 2015
        self.output_namespace[
            'tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5)



    def _MC(self):
        self.output_namespace['C'] = 92.1 * pF  # 92.1 +- 8.4, Paluszkiewicz 2011 J Neurophysiol
        self.output_namespace['taum'] = 21.22 * ms  # HIGHLY VARYING 21.22 +- 11.2, N=3; Tau_m = 9.7 +- 1.3 Takesian 2012 J Neurophysiol; 17.57 +- 9.24 Wang 2004 J Physiol; 36.4 +- 3.7 Paluszkiewicz 2011 J Neurophysiol
        self.output_namespace['gL'] = self.output_namespace['C'] / self.output_namespace['taum']
        #        self.output_namespace['taum'] = self.output_namespace['C'] / self.output_namespace['gL'] from FS neurons

        self.output_namespace['EL'] = -60.38 * mV  # = Vr
        self.output_namespace['VT'] = -42.29 * mV
        self.output_namespace['V_res'] = self.output_namespace['VT'] - 4 * mV  # -55 * mV #self.output_namespace['VT']-4*mV # inherited from FS
        self.output_namespace['DeltaT'] = 2 * mV  # inherited from FS
        self.output_namespace['Vcut'] = self.output_namespace['VT'] + 5 * self.output_namespace['DeltaT']  # inherited from FS
        self.output_namespace['Ee'] = 0 * mV  # inherited from FS
        self.output_namespace['Ei'] = -75 * mV
        self.output_namespace['tau_e'] = 1.7 * ms  # Markram Cell 2015
        self.output_namespace['tau_i'] = 8.3 * ms  # Now from Markram Cell 2015 #7 * ms # Amatrudo et al, 2012 (rise time: 2.5)


    def _SS(self):
        # Capacitance, multiplied by the compartmental area to get the final C(compartment)
        Cm = (1 * ufarad * cm ** -2)
        # leak conductance, -''-  Amatrudo et al, 2005 (ja muut) - tuned down to fix R_in
        gl = (4.2e-5 * siemens * cm ** -2)
        Area_tot_pyram = 25000 * .75 * um ** 2
        self.output_namespace['C'] =  0.03 * Cm * Area_tot_pyram * 2 # ? is it correct to take the soma part for here
        # total g_leak in compartments
        self.output_namespace['gL'] = 0.03 * gl * Area_tot_pyram

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
        self.output_namespace['Ra'] = [100, 80, 150, 150, 200] * Mohm
        self.output_namespace['tau_e'] = 1.7 * ms
        self.output_namespace['tau_eX'] = 1.7 * ms
        self.output_namespace['tau_i'] = 8.3 * ms
        # return self.final_namespace

