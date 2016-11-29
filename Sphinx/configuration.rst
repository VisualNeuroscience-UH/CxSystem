﻿.. _config_file:

Configuration File Tutorial
===========================

The configuration file is in .CSV format. There two categories of lines in the configuration file: 

* **Titles-line**: These lines, starting with *row_type* keyword, defines the column titles for all the lines between the the next line and the next *Titles-line*:

::

	row_type,sys_mode,total_synapses

This Titles-line indicates that all the lines between the next line and the next Titles-line have four types of columns:  row_type,sys_mode,total_synapses,do_optimize. In the next sections, all of these parameters will be described thoroughly. 

* **Values-line**: These lines define the column values corresponding to column titles in the last Titles-line:

::

	params,local,7000

These four values are in correspondence with the column titles of the previous Titles-line example. In other words, the last two examples defines the following values:

::

	row_type = params 
	sys_mode = local
	total_synapses = 7000

Currently there are three types of **row_type** implemented: 

* params: defines the run-time parameters of the system run (partially equivalent to the VCxrun)
* G: defines the NeuronGroup()s in the system 
* S: defines the Synapses() connecting the NeuronGroup()s in the system

In the next sections, each of these row_types has its own types of columns and are thoroughly explained with examples. Note that **mandatory** arguments are wrapped with **<>** whereas the **optional** ones are in **[]**. The corresponding **data type** is also presented using **{}**.

params
-------------------

Currently there are three configurable run-time variables implemented in the system:

	:params:  **<total_synapses>{int}:**  Defines the total number of synapses in the system.
		  
		**<sys_mode>{local, expanded}:** The system can be run in two modes: **local** and **expanded** mode.
	
		**<do_optimize>{0,1}:** In Brian2, it is not possible to define number of synapses, but only the probability. An optimization mechanism is implemented for when the synaptic connections should be defined based on specific percentages of a total number of synapses in the system. This parameter defines whether or not the synaptic connection probabilities should be determined and optimized so that they reproduce approximately the same amount of connections in the system. 

* Note1: The optimization should be used when the system is working in the **local** mode, as the catch is to determine the probabilities based on the percentages of the total number of synapses, and then expand the system to larger scales. 

* Note2: using the system in the "local" mode whilst the "do_optimized" flag is enabled will **not** run the simulation. This will only determine the probability of each connection based on the percentages and total number of synapses and creating a new .CSV file based on the the optimized probabilities. 

Example of the params Titles & Values-lines: 

::

	row_type,sys_mode,total_synapses,do_optimize
	params,local,35000,0

Monitors
--------------

Before starting describing the different row_types in the .CSV files, it is important to understand how the monitors are defined in the system. In Brian2 monitors can be assigned to a NeuronGroup() or Synapses(). Similarly, when using the configuration file, you are able to set monitors for any target line, i.e. NeuronGroup()s or Synapses(). The monitors are defined in the following way: 

If the monitor column is present in a Titles-line and the value in Values-line is not 'N/A', a monitor object will be created for the NeuronGroup() or Synapses() of that specific line. Note that it is not possible to have different clocks for monitors in Brian2GeNN. Hence, try to use the monitors wisely to prevent generating bulk data. Following tags can be used for configuring a specific monitor: 

 [Sp]:
  This tag defines the [Sp]ikeMonitor() in brian2. Example:

::

	  ...,[Sp]

The ellipsis represents the predecessor kewords in the line. 

 [St]:
  This tag defines the [St]ateMonitor() in brian2. In this case, one should define the target variable in the following way: 

::

	...,[St]<state variable1>+<state variable2> 


Similar to [Sp], the ellipsis represents the predecessor keywords in the line. State variables are separated with *+*. An example of using [Sp] alongside with a [St] with three state variables of *ge_soma*,*gi_soma*, and *vm*:

::

	...,[Sp] [St]ge_soma+gi_soma+vm

By default all of the possible indices are being monitored (record = True). However, one might intend to monitor specific indices of NeuronGroup()/Synapses(). This can be achieved by using the [rec] tag followed by the indices of interest. In the following example two state monitors are defined for *apre* and *wght* of the Synapses() object. In the former state monitor the first 20 indices are being recorded whilst in the latter (*wght*), even indices between 0 and 20 are being recorded:

::

	...,[St]apre[rec](0-20)+wght[rec](0-20-2)

Occasionally, one might want to assign a specific type of monitor to several consecutive target lines. In this case, the generic monitor(s) can be defined in the first target line and a **-->** symbol should be written at the end of the line. **-->** indicates that all the next lines should be assigned with the same monitor. For finishing this assignment, a **<--** symbol should be put at the last target line of interest. Note that it is possible to overwrite the defined monitors of some lines between the **-->** and **<--** symbols simply by adding the monitor of the interest. 

::

	...,[St]ge_soma -->
	...,N/A
	...,  
	...,[Sp] 
	..., <--

In this example, an StateMonitor() over *ge_soma* is assigned on lines 1,3,4,5 by using the **-->** and **<--** symbol. In the second line, the usage of default StateMonitor() is over-written by using the N/A keyword, indicating that the second line is not monitored. In the third line, however, this StateMonitor() is overwritten by a SpikeMonitor(). 






Input
---------

The input is defined with the "IN" keyword. Currently the video input in implemented in the cortical system. The stimuli is created using a *.mat* file. This stimuli is in form of spike and is fed to a SpikeGeneratorGroup() . This group is then connected to a relay NeuronGroup() with a synapses() object. The main purpose of the relay neurons is to have positions for input neurons (SpikeGeneratorGroup does not support positions). The input can be defined using the following keyword: 

	:params: **<idx>{int}:** Index of the NeuronGroup().

		**<input file location>:** relative path to the input .mat file. 

		**<frequency>** 

		**[monitors]** 


This is an example of defining an input for the system: 

::
	
	row_type,idx,path,freq,monitors	
	IN,0, ./V1_input_layer_2015_10_30_11_7_31.mat ,190*Hz ,[Sp]


In this example an input NeuronGroup() with index 0 is created based on the *V1_inpu.mat* file with a frequency of 190*Hz and a SpikeMonitor() is set on it.

NeuronGroup()
---------------

The NeuronGroup()s are defined using the G (as in Group) keyword. This row_type is basically used for defining the NeuronGroup()s in brian2. Following parameters are implemented for defining the NeuronGroup(): 

	:param: **<idx>{int}:** Index of the NeuronGroup().

		**<number_of_neurons>{int}:** Number of neurons in the NeuronGroup(). 

		**<neuron_type>{L1i,UMi,PC,BC,MC,SS}:** cell category of the NeuronGroup(). 

		**<layer_idx>:** Layer index of the cell groups. 

		**[threshold]:** threshold value for the neurons in the NeuronGroup(). 

		**[reset]:** reset value for the neurons in the NeuronGroup().

 		**[refractory]:** reset value for the neurons in the NeuronGroup().

 		**[net_center]:** center location of the NeuronGroup().

 		**[monitors]:** center location of the NeuronGroup().

--------------

In this section, some of the above-mentioned parameters are clarified. 

**idx:**

The index of the NeuronGroup()s are important for creating the synaptic connections between them. As it will be described in the synaptic definitions, creating a synaptic connections needs a presynaptic and postsynaptic group index that should be used directly from this index value.   

**<neuron_type>:**

The *<neuron_type>* is the category of the cells of the group, which is one of the following groups: 

+------+------------------------+
| type | Cell  Category         | 
+======+========================+
| SS   | spiny stellate         |
+------+------------------------+
| PC   | Pyramidal              |
+------+------------------------+
| BC   | Pyramidal              |
+------+------------------------+
| MC   | Martinotti             |
+------+------------------------+
| L1i  | Layer 1 inhibitory     |
+------+------------------------+
| UMi  | Unassigned Markram cell|
+------+------------------------+


The *<layer index>* argument defines the layer in which the NeuronGroup() is located. Except for PC cells, all types of neurons are defined as a soma-only neuron, hence their layer is an integer. In case of layer 2/3 using 2 is sufficient. For instance the following example defines a group of 46 SS neurons in layer 2/3: 

::

	row_type,idx,number_of_neurons,neuron_type,layer_idx
	G,1,46,SS,2

Currently PC cells are the only multi-compartmental neurons that could possibly cover more than one layer. In this case, the layer index should be defined as a list where the first element defines the soma location and the second element defines the farthest apical dendrite compartment. In the following example, a PC group of 55 neurons is defined in which the basal dendrites, soma and proximal apical dendrite is located in layer 6 and the apical dendrites covers layer layer 5 to 2: 

::

	row_type,idx,number_of_neurons,neuron_type,layer_idx
	G,2,55,PC,[6->2]


The compartment formation is then as follows: 

+------+-------------------+
| Layer| Compartment       | 
+======+===================+
|  2/3 | Apical dendrite[3]|
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

**[threshold],[reset] and [refractory]:**

By default following values are assigned to threshold, reset and refractory of any NeuronGroup(): 

- *threshold*: *vm>Vcut*
- *reset*: *vm=V_res*
- *refractory*: *4* * *ms*

Any of this variables can be overwritten by using the keyword arguments *threshold*, reset and *refractory*.  


**[net_center]:**

The center of a NeuronGroup() can be defined with the net-center tag in the *Titles-line* and corresponding center position in the *Value line*.  If not defined, the center will be the default value of 0+0j. The following example creates a NeuronGroup() consist of 75 BC neurons located in 5+0j, with a spike monitors assigned to it: 

::

	row_type,idx,number_of_neurons,neuron_type,layer_idx,net_center,monitors
	G,2,75,BC,2,5+0j,[Sp]

Synapses()
---------------------

S keyword (as in Synapses)  defines the brian2 Synapses() object.  Following parameters are implemented for defining the Synapses():


	:param: **<receptor>{ge,gi}** 

		**<pre_syn_idx>{int}** 

		**<post_syn_idx>{int}** 

		**<syn_type>{Fixed,STDP}**

		**[p]:** probability 

		**[n]:** number of synapses per connection

		**[monitors]**

 		**[percentage]** percentage of the total synapses


--------------
 

where the *<receptor>* defines the receptor type, i.e. ge for excitatory and gi for inhibitory connections, *<presynaptic group index>* and *<postsynaptic group index>* defines the index of the presynaptic and postsynaptic group respectively. These indices should be determined using the *indexing tag* in the NeuronGroup()s lines. The next field defines the type of the synapse. Currently there are two types of Synapses() implemented: Fixed and STDP. The following example defines a excitatory STDP synaptic connection between NeuronGroup()s with indices of 2 and 4, in which the *ge* is the receptor: 

::

	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type
	S,ge,2,4,STDP 

In case the postsynaptic group is multi-compartmental, the target compartment should be defined using the [C] tag. Let us review this concept with an example: 

::

	row_type,idx,number_of_neurons,neuron_type,layer_idx
	G,0,46,SS,4
	G,1,50,PC,[4->1]
	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type
	S,ge,0,1[C]1,STDP

Clearly NeuronGroup() 0 is group of 46 SS cells and NeuronGroup() 1 is a group of 50 PC cells. The latter is multi-compartmental with a layer index of [4,1]. Hence the compartments formation are as follows: 

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


The synapses() object is targeting the 1st compartment of the PC cells, i.e.  Apical dendrite[1]. Consider the following example in which the target is the compartment number 0 in the target NeuronGroup():


::

	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type
	S,ge,0,1[C]0bsa,STDP


As you can see, the compartment *[C]0* is followed by three characters *bsa*. This indicates that the among the three sub-compartments inside the compartment number 0, i.e. Basal dendrite, Soma and Apical dendrite[0], letters of b,s and a are being targeted. Regardless of the layer, the indices of these three compartments are always as:

+------+-------------------+
| Comp.| Compartment  type |
| Index|                   |
+======+===================+
| a    |Apical dendrite[0] |
+------+-------------------+
| s    |         Soma      |
+------+-------------------+
| b    | Basal dendrite    |
+------+-------------------+

So for instance, in case an inhibitory connection tends to target the soma only, the synaptic definition should be changed to:


::

	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type
	S,ge,0,1[C]0s,STDP


If both basal dendrite and apical dendrite[0] was being targeted, the syntax should change to: 


::

	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type
	S,ge,0,1[C]0ba,STDP

By default the probability of the synaptic connections are determined based on the distance between the neurons, which depends on sparseness and ilam variables in the brian2_obj_namespaces module. In case the maximum probability of the connection should be overwritten, [p] tag can be used. In the following example the maximum probability of the connection is overwritten as 0.06 (6%): 

::

	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type,p
	S,ge,0,1[C]0ba,STDP,0.06

By default the number of connections that happens between a pair of neurons is also equal to 1. This can also be overwritten to another integer value by using the [n] tag. So, for having a probability of 6% over 3 connection per pair of neuron: 

::

	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type,p,n
	S,ge,0,1[C]0ba,STDP,0.06,3 


When the system is in "local" mode and do_optimize flag is 1, it is needed to define the percentage of all synapses. For instance when the total number of synapses in the system is 10000 and a synaptic group takes 20% of the connections: 

::

	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type,percentage 
	S,ge,0,1[C]0ba,STDP,0.2
	... 

This will optimize the probability of that synaptic connection in a way to have 0.2 * 10000 synapses. One might want to have multiple synapse per connection between two NeuronGroup()s. This is defined in the following example using the 'n' keyword in the *Titles-line*:


::

	row_type,receptor,pre_syn_idx,post_syn_idx,syn_type,n,percentage 
	S,ge,0,1[C]0ba,STDP,4,0.2
	... 

This example will optimize the probability of the connection in a way that there are 0.2*10000/4 connections and there are 4 synapses for each connection between the NeuronGroup()s. 
 

