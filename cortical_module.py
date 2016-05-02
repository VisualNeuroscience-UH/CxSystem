__author__ = 'V_AD'
from brian2 import *
import brian2genn
import turtle


set_device('genn')



class cortical_module:
    'A customizable model of cortical module for Brian2Genn'

    def __init__(self,path):
        options = {
            '#': self.comment,
            '[G]': self.neuron_group,
            '[syn]' : int,
            '"' : float,
            '[' : array,
        }
        is_tag = ['[', '\t']
        with open (path, 'r') as f :
            for line in f:
                if line[0]  in is_tag :
                    tag = line[line.index('['):line.index(']')+1]
                    assert tag in options.keys(), 'The tag %s is not defined.'%tag
                else:
                    continue
                line = line.replace(tag, '')
                line = line.replace('\n', '')
                args = line.split(' ')
                for arg in args[1:]:
                    if arg[0] in options.keys() :
                        arg = options[arg[0]](arg)
                if line[0] in options.keys():
                    options[line[0]](args)

        print "Cortical Module initialization Done"
    # def __str__(self):
    #     print "A summary of this cortical module: "
    def neuron_group (self, *args):
        self. = customized_neuron (args[0], cell_category= args[1], namespace_type=args[2], eq_category= args[3],layers_idx=args[4]).final_neuron
    def comment(self, *args):
        pass




class custom_neuron_group:
    'A customizable neuron group of a specific type of cell'
    def __init__(self,):
        print "Neuron group initialization Done"
    # def __str__(self):
    #     print "A summary of this neuron group: "






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
        customized_neuron.instances.append(self) # this is for tracking the instance of the class
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
        self.final_neuron = {}
        self.final_neuron['type'] = cell_type
        self.final_neuron['category'] = cell_category
        self.final_neuron['namespace_type'] = namespace_type
        self.final_neuron['eq_category'] = eq_category
        self.final_neuron['soma_layer'] = layers_idx[0]
        # _comparts_tmp1 & 2 are for extracting the layer of the compartments if applicable
        self._comparts_tmp1 = array(range (layers_idx[0]-1,layers_idx[1]-1,-1))
        self._comparts_tmp2 = delete(self._comparts_tmp1,where(self._comparts_tmp1==3)) if 3 in self._comparts_tmp1 else self._comparts_tmp1
        self.final_neuron['dends_layer'] = array([0]) if self.final_neuron['type'] != 'PC'  else self._comparts_tmp2
        # number of compartments if applicable
        self.final_neuron['dend_comp_num'] = len (self.final_neuron['dends_layer']) if self.final_neuron['dends_layer'].all() != 0 else array([0])
        self.final_neuron['total_comp_num'] = self.final_neuron['dend_comp_num'] + 3 if self.final_neuron['type'] == 'PC' or  self.final_neuron['type'] == 'SS' else 1 # plus soma , proximal apical dendrite and basal dendrites which are in the same layer
        self.final_neuron['namespace'] = namespaces(self.final_neuron).final_namespace
        self.final_neuron['equation'] = equations(self.final_neuron).final_equation

        # self.final_neuron['equation'] = Equations(_eq_template_soma, gL=gL[N_comp], ge='ge_soma', geX='geX_soma',
        # gi='gi_soma', gealpha='gealpha_soma', gealphaX='gealphaX_soma', gialpha='gialpha_soma',
        # C=C[N_comp], I_dendr='Idendr_soma')

        #sorting the final dict to be neat
        print "Customized cell initialized"
    # def __str__(self):
    #     'Prints a description of the cell'
    #     print "Description of this cell:"


class namespaces (object):
    'This class embeds all parameter sets associated to all neuron types and will return it as a namespace in form of dictionary'
    def __init__(self, final_neuron):
        namespaces.category_ref = array(['multi_comp','soma_only','FS','LTS'])
        assert final_neuron['category'] in namespaces.category_ref, "Error: cell type '%s' is not defined." % final_neuron['category']
        self.final_namespace = {}
        getattr(namespaces, final_neuron['category'])(self,final_neuron)
    def multi_comp(self,final_neuron):
        '''
        :param parameters_type: The type of parameters associated to compartmental neurons. 'Generic' is the common type. Other types could be defined when discovered in literature.
        :type parameters_type: String
        :return:
        :rtype:
        '''
        namespace_type_ref = array(['generic'])
        assert final_neuron['namespace_type'] in namespace_type_ref, "Error: namespace type '%s' is not defined."%final_neuron['namespace_type']
        if final_neuron['namespace_type'] == namespace_type_ref[0]:
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
            self.final_namespace['C']= fract_areas[final_neuron['dend_comp_num']] * Cm * Area_tot_pyram * 2
            # total g_leak in compartments
            self.final_namespace['gL']= fract_areas[final_neuron['dend_comp_num']] * gl * Area_tot_pyram


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



class equations (object):
    '''
    Creates instances of equations which can be used in any cell. Determination of whether or not the output\
    equation matches the nature of neuron, is to the user. Equations other than Fast Spiking, Low Threshold Spiking, \
    Multi-Compartmental neurons and soma-only neurons should be defined in this class.
    '''
    def __init__(self, final_neuron):
        '''
        :param eq_category: The spiking pattern in the neuron ['multi_comp','soma_only','FS','LTS'].
        :type eq_category: String
        :param comparts: Number of Compartments in case the requested equation is 'multi_comp'.
        :type comparts: int
        :return:
        :rtype:
        '''
        equations.all_eq_types = array(['multi_comp','soma_only','FS','LTS'])
        assert final_neuron['eq_category'] in equations.all_eq_types, "Equation type '%s' is not defined." % final_neuron['eq_category']
        self.final_equation = ''
        getattr(equations, final_neuron['eq_category'])(self,final_neuron)


    # def __str__(self):
    #     'prints a description of the equation'
    #     print "Description of Equation"

    def multi_comp (self, final_neuron) :
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
                C=final_neuron['namespace']['C'][0], gL=final_neuron['namespace']['gL'][0],
                gi="gi_basal", geX="geX_basal", gialpha="gialpha_basal", gealphaX="gealphaX_basal",I_dendr="Idendr_basal"))
        self.final_equation += Equations (eq_template_soma, gL=final_neuron['namespace']['gL'][1],
                ge='ge_soma', geX='geX_soma', gi='gi_soma', gealpha='gealpha_soma', gealphaX='gealphaX_soma',
                gialpha='gialpha_soma', C=final_neuron['namespace']['C'][1], I_dendr='Idendr_soma')
        for _ii in range (final_neuron['dend_comp_num']+1): # extra dendritic compartment in the same level of soma
            self.final_equation+=Equations(eq_template_dend, vm = "vm_a%d" %_ii, C=final_neuron['namespace']['C'][_ii],
            gL=final_neuron['namespace']['gL'][_ii],ge="ge_a%d" %_ii, gi="gi_a%d" %_ii, geX="geX_a%d" %_ii,
            gealpha="gealpha_a%d" %_ii, gialpha="gialpha_a%d" %_ii, gealphaX="gealphaX_a%d" %_ii,I_dendr="Idendr_a%d" %_ii)

        # basal self connection
        self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself)  : amp',
                         gapre=1/(final_neuron['namespace']['Ra'][0]),
                         I_dendr="Idendr_basal", vmself= "vm_basal", vmpre= "vm")
        self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself)  + gapost*(vmpost-vmself) : amp',
                         gapre=1/(final_neuron['namespace']['Ra'][1]),
                         gapost=1/(final_neuron['namespace']['Ra'][0]),
                         I_dendr="Idendr_soma" , vmself= "vm",
                         vmpre= "vm_a0", vmpost= "vm_basal")
        self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself) + gapost*(vmpost-vmself) : amp',
                                 gapre=1/(final_neuron['namespace']['Ra'][2]),
                                 gapost=1/(final_neuron['namespace']['Ra'][1]),
                                 I_dendr="Idendr_a0" , vmself= "vm_a0" ,vmpre= "vm_a1" , vmpost= "vm")

        for _ii in arange(1,final_neuron['dend_comp_num']):
            self.final_equation += Equations('I_dendr = gapre*(vmpre-vmself) + gapost*(vmpost-vmself) : amp',
                             gapre=1/(final_neuron['namespace']['Ra'][_ii]),
                             gapost=1/(final_neuron['namespace']['Ra'][_ii-1]),
                             I_dendr="Idendr_a%d" %_ii, vmself= "vm_a%d" %_ii,
                             vmpre= "vm_a%d" %(_ii+1), vmpost= "vm_a%d" %(_ii-1))

        self.final_equation += Equations('I_dendr = gapost*(vmpost-vmself) : amp',
                         I_dendr="Idendr_a%d"%final_neuron['dend_comp_num'] , gapost=1/(final_neuron['namespace']['Ra'][-1]),
                         vmself= "vm_a%d"%final_neuron['dend_comp_num'], vmpost= "vm_a%d"%(final_neuron['dend_comp_num']-1))


cortical_module ('/home/corriel/Desktop/test.txt')
p = customized_neuron ('PC', cell_category= 'multi_comp', namespace_type='generic', eq_category= 'multi_comp',layers_idx=array([4,1])).final_neuron
N1 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])
N2 = NeuronGroup(1000, model=p['equation'], threshold='vm>Vcut', reset='vm=V_res', refractory = '2 * ms', namespace = p['namespace'])



run(101*ms)
device.build(directory='shortEX',
            compile=True,
             run=True,
             use_GPU=True)
# p = customized_equation ('PC' , array([6,4]))
# print p.final_neuron
# print help(customized_equation)
