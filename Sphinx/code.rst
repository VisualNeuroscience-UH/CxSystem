Cortical System Package
====================================

The cortical system package consists of five major modules. cortical_module as the main module, creates the target cortical model based on a configuration file (Connections.txt). This configuration line is parsed in cortical module and the neurons/synapses formation of the module is created in brian2 accordingly. 

Configuration file
------------------------------------
Each line of the configuration file that has to be interpretted, aka target line, defines either a Neuron_Group() or Synapses() in brian2. A line is considered as target line if it contains a target tag. Currently there are three target tags in the system: [IN], [G], [S] and a numbering tag, e.g. [0]. Each of these tags are thoroughly discussed later in this document. Each line that starts with the character *[* will be considered as a potential target line. Hence any other line that starts with other characters is equal to a comment line. Though you can use *#* in the beginning of the line to be tidy. 

Numbering tag: Each line should start with a numbering tag. This numbering tag is only used to make following the line numbers easier for the user. Although this numbering tag is required to be in each and every line, it doesn't have any effect on the line interpretation result.  

[IN]: Defines the [IN]put of the system (video only). The format of the input line is as follows: 

::

	[Number][IN] <.mat file location> <frequency> [monitors]

[G]: Defines the brian2 Neuron_Group(). The format of the input line is as follows:

::

	 [Number][G] <number of neurons> <cell type> <cell layer> <cell group center> [monitors]


[S]: Defines the brian2 Synapses(). 

Cortical System module 
------------------------------------
.. module:: cortical_module
.. autoclass:: cortical_module
   :members:
   
   .. automethod:: cortical_module.cortical_module.__init__
