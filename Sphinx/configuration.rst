.. _config_file:

Configuration File Tutorial
===========================

Each line of the configuration file that has to be interpreted, aka target line, defines either a Neuron_Group() or Synapses() in brian2. A line is considered as target line if it contains a target tag. Currently there are three target tags in the system: [IN], [G], [S] and a indexing tag, e.g. [0]. Each of these tags are thoroughly discussed later in this document. Each line that starts with the character *[* will be considered as a potential target line. Hence any other line that starts with other characters is equal to a comment line. Though you can use *#* in the beginning of the line to be tidy. 

-----------------

**indexing tag**: 

Each line should start with a indexing tag. This indexing tag is only used to make following the line numbers easier for the user. Although this indexing tag is required to be in each and every line, it does not have any effect on the line interpretation result. Example: 

::

	[0][G] ...  
	[1][G] ...  

----------------

**Monitors**: 

In Brian2 monitors can be assigned to a neuron group or synapses. When using the configuration file, you are able to set monitors for any target line, i.e. neuron groups or synapses. The monitors are defined in the following way: 

[M]: 
 If the [M]onitor tag is present in a target line, a monitor object will be created for the neuron group or synapse of that target line. Note that it is not possible to have different clocks for monitors in Brian2GeNN. Hence, try to use the monitors wisely to prevent generating bulk data. Following tags can be used for configuring a specific monitor: 

 [Sp]:
  This tag defines the [Sp]ikeMonitor() in brian2. Example:

::

	  ... [M] [Sp]

The ellipsis represents the predecessor tags in the target line. 

 [St]:
  This tag defines the [St]ateMonitor() in brian2. In this case, one should define the target variable in the following way: 

::

	... [M] [St]<state variable1>+<state variable2> 


Similar to [Sp], the ellipsis represents the predecessor tags in the target line. State variables are separated with *+*. An example of using [Sp] alongside with a [St] with three state variables of *ge_soma*,*gi_soma*, and *vm*:

::

	... [M] [Sp] [St]ge_soma+gi_soma+vm

By default all of the possible indices are being monitored (record = True). However, one might intend to monitor specific indices of neuron_group/synapses. This can be achieved by using the [rec] tag followed by the indices of interest. In the following example two state monitors are defined for *apre* and *wght* of the Synapses() object. In the former state monitor the first 20 indices are being recorded whilst in the latter (*wght*), even indices between 0 and 20 are being recorded:

::

	... [M] [St]apre[rec]arange(0,20)+wght[rec]arange(0,20,2)

Occasionally, one might want to assign a specific type of monitor to several consecutive target lines. In this case, the generic monitor(s) can be defined in the first target line and a **-->** symbol should be written at the end of the line. **-->** indicates that all the next lines should be assigned with the same monitor. For finishing this assignment, a **<--** symbol should be put at the last target line of interest. Note that it is possible to overwrite the defined monitors of some lines between the **-->** and **<--** symbols simply by adding the monitor of the interest. 

::

	... [M] [St]ge_soma -->
	... 
	... [M] [Sp] 
	... <--

In this example, an statemonitor over *ge_soma* is assigned on all four lines by using the **-->** and **<--** symbol. In the third line, however, this statemonitor is overwritten by a Spikemonitor. 

--------------------

**Input**:


Currently the video input in implemented in the cortical system. The stimuli is created using a *.mat* file. This stimuli is in form of spike and is fed to a SpikeGeneratorGroup() . This group is then connected to a relay neuron group with synapses(). The main purpose of the relay neurons is to have positions for input neurons (SpikeGeneratorGroup does not support positions). The input can be defined using the following tag: 

[IN]: 
 Defines the [IN]put of the system (video only). The format of the input line is as follows: 

::

	[index][IN] <.mat file location> <frequency> [monitors]

This is an example of defining an input for the system: 

::

	[0][IN] /home/$USER/V1_input.mat 190*Hz [M] [Sp]

In this example an input is created based on the *V1_inpu.mat* file with a frequency of 190*Hz and a SpikeMonitor is set on it.

------------------------

**Neuron Group**

[G]: 
 Defines the brian2 Neuron_Group(). The format of the NeuronGroup target line is as follows:

::

	 [index][G] <number of neurons> <cell type> <layer index> [threshold] [reset] [refractory] [cell group center] [monitors]

where the *[index]* is the line number, *<number of neurons>* is the number of neurons in that particular neuron group. The *<cell type>* is the category of the cells of the group, which is one of the following groups: 

+------+-------------------+
| type | Cell  Category    | 
+======+===================+
| SS   | Stellate cell     |
+------+-------------------+
| PC   | Pyramidal cell    |
+------+-------------------+
| BC   | Pyramidal cell    |
+------+-------------------+
| MC   | Martinotti cell   |
+------+-------------------+
| L1i  | Layer 1 inhibitory|
+------+-------------------+

The *<layer index>* argument defines the layer in which the neuron group is located. Except for PC cells, all types of neurons are defined as a soma-only neuron, hence their layer is an integer. In case of layer 2/3 using 2 is sufficient. For instance the following example defines a group of 46 SS neurons in layer 2/3: 

::

	[0][G] 46 SS 2 


Currently PC cells are the only multi compartmental neurons that could possibly cover more than one layer. In this case, the layer index should be defined as a list where the first element defines the soma location and the second element defines the farthest apical dendrite compartment. In the following example, a PC group of 55 neurons is defined in which the basal dendrites, soma and proximal apical dendrite is located in layer 6 and the apical dendrites covers layer layer 5 to 2: 

::

	[1][G] 55 PC [6,2]

The compartment formation is then as follows: 

+------+-------------------+
| Layer| Compartment       | 
+======+===================+
|  3/2 | Apical dendrite[3]|
+------+-------------------+
|  4   | Apical dendrite[2]|
+------+-------------------+
| 5    | Apical dendrite[1]|
+------+-------------------+
| 6    |Apical dendrite[0] |
+------+-------------------+
| 6    |         Soma      |
+------+-------------------+
| 6    | Basal dendrite    |
+------+-------------------+

By default following values are assigned to threshold, reset and refractory of any neurongroup: 

- *threshold*: *vm>Vcut*
- *reset*: *vm=V_res*
- *refractory*: *4* * *ms*

Any of this variables can be overwritten by using the keyword arguments [threshold], [reset] and [refractory]. As the name implies, the optional argument *[cell group center]* defines the center of the neuron group. The center can be defined with the [CN] tag followed by the center position.  If not defined, the center will be the default value of 0+0j. The following example creates a neuron group consist of 75 BC neurons located in 5+0j, with a spike monitors assigned to it: 

::

	[2][G] 75 BC 2 [CN] 5+0j [M] [Sp]

---------------------

**Synapses**

[S]:
 Defines the brian2 Synapses(). The format of the Synapses() target line is as follows: 

::

	[index][S] <receptor> <presynaptic group index> <postsynaptic group index> <synapse type>

where the *[index]* is the line number, *<receptor>* defines the receptor type, e.g. ge and gi, *<presynaptic group index>* and *<postsynaptic group index>* defines the index of the presynaptic and postsynaptic group respectively. These indices could be determined using the *indexing tag* in the neuron groups target lines. The next field defines the type of the synapse. Currently there are two types of synapses implemented: Fixed and STDP. The following example defines a excitatory STDP synaptic connection between neuron groups with indices of 2 and 4, in which the *ge* is the receptor: 

::

	[0][S] ge 2 4 STDP

In case the postsynaptic group is multi-compartmental, the target compartment should be defined using the [C] tag. Let us review this concept with an example: 

::

	[0][G] 46 SS 4
	[1][G] 50 PC [4,1]
	[2][S] ge 0 1[C]1 STDP

Clearly Neurongroup 0 is group of 46 SS cells and Neurongroup 1 is a group of 50 PC cells. The latter is multi-compartmental with a layer index of [4,1]. Hence the compartments formation are as follows: 

+------+-------------------+------+
| Comp.| Compartment  type |      |
| Index|                   | Layer| 
+======+===================+======+
|  2   | Apical dendrite[2]| 1    |
+------+-------------------+------+
| 1    | Apical dendrite[1]|3/2   |
+------+-------------------+------+
| 0    |Apical dendrite[0] | 4    |
+------+-------------------+------+
| 0    |         Soma      | 4    |
+------+-------------------+------+
| 0    | Basal dendrite    | 4    |
+------+-------------------+------+


The synapses() object is targeting the 1st compartment of the PC cells, i.e.  Apical dendrite[1]. Consider the following example in which the target is the compartment number 0 in the target neuron group:


::

	[2][S] ge 0 1[C]0012 STDP


As you can see, the compartment *[C]0* is followed by three numbers *012*. This indicates that the among the three sub-compartments inside the compartment number 0, i.e. Basal dendrite, Soma and Apical dendrite[0], indices of 0,1 and 2 are being targeted. Regardless of the layer, the indices of these three compartments are always as:

+------+-------------------+
| Comp.| Compartment  type |
| Index|                   |
+======+===================+
| 2    |Apical dendrite[0] |
+------+-------------------+
| 1    |         Soma      |
+------+-------------------+
| 0    | Basal dendrite    |
+------+-------------------+

So for instance, in case an inhibitory connection tends to target the soma only, the synaptic definition should be changed to:


::

	[2][S] ge 0 1[C]01 STDP


If both basal dendrite and apical dendrite[0] was being targeted, the syntax should change to: 


::

	[2][S] ge 0 1[C]002 STDP


