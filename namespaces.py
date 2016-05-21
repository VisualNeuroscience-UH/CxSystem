__author__ = 'V_AD'
from brian2 import *

class synapse_namespaces(object):
    def __init__(self,output_synapse):
        synapse_namespaces.type_ref = array (['STDP'])
        assert output_synapse['type'] in synapse_namespaces.type_ref, "Error: cell type '%s' is not defined." % output_synapse['type']

class neuron_namespaces (object):
    'This class embeds all parameter sets associated to all neuron types and will return it as a namespace in form of dictionary'
    def __init__(self, output_neuron):
        neuron_namespaces.category_ref = array(['multi_comp','soma_only','FS','LTS'])
        assert output_neuron['category'] in neuron_namespaces.category_ref, "Error: cell type '%s' is not defined." % output_neuron['category']
        self.final_namespace = {}
        getattr(neuron_namespaces, output_neuron['category'])(self,output_neuron)
    def multi_comp(self,output_neuron):
        '''
        :param parameters_type: The type of parameters associated to compartmental neurons. 'Generic' is the common type. Other types could be defined when discovered in literature.
        :type parameters_type: String
        :return:
        :rtype:
        '''
        namespace_type_ref = array(['generic'])
        assert output_neuron['namespace_type'] in namespace_type_ref, "Error: namespace type '%s' is not defined."%output_neuron['namespace_type']
        if output_neuron['namespace_type'] == namespace_type_ref[0]:
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


            self.final_namespace = {}
            # total capacitance in compartmens. The *2 comes from Markram et al Cell 2015: corrects for the deindritic spine area
            self.final_namespace['C']= fract_areas[output_neuron['dend_comp_num']] * Cm * Area_tot_pyram * 2
            # total g_leak in compartments
            self.final_namespace['gL']= fract_areas[output_neuron['dend_comp_num']] * gl * Area_tot_pyram


            self.final_namespace['Vr']=-70.11 * mV
            self.final_namespace['EL'] = 70.11 * mV
            self.final_namespace['VT']=-41.61 * mV
            self.final_namespace['V_res']=-70.11 * mV
            self.final_namespace['DeltaT']=2*mV
            self.final_namespace['Vcut'] = -25 * mV


            # Dendritic parameters, index refers to layer-specific params
            self.final_namespace['Ee']= 0*mV
            self.final_namespace['Ei']= -75*mV
            self.final_namespace['Ed']= 70.11 * mV


            # Connection parameters between compartments
            self.final_namespace['Ra']= [100,80,150,150,200] * Mohm
            self.final_namespace['tau_e'] = 1.7 * ms
            self.final_namespace['tau_eX'] = 1.7 * ms
            self.final_namespace['tau_i'] = 8.3 * ms
            # return self.final_namespace
    def soma_only (self,parameters_type):
        parameter_ref = array(['Generic'])
