.. |br| raw:: html

   <br />

Examples
==========



Building a new model
---------------------

A new network can be designed by using a regular spreadsheet program, such as Excel, whose output is readable by everyone taking part in the research project. The idea is that a scientist leading the project can consult an electrophysiologist or an anatomist without referring to implementation-level code. |br|
Practically, you first need to decide the system structure, e.g. how many of the six cortical layers you are going to model, and which cell groups you want to include in each layer. Cell group definition takes a single row in the Model and Network file. Connectivity parameters (connection probability, synapse type, number of synapses per connection) can then be set in the same file, with a single row for each axonal pathway. In the Physiology file, you can then set the electrophysiological parameters corresponding to each neuron group. |br|
Admittedly, a new project might need functionalities we have not implemented. New features can however be programmed in Python in the Physiology reference file (eg. synapse with STDP) and they can then be referenced in either of the two main configuration files. We try to hide away implementation details so that the complexity (amount of code) would not overwhelm project members, who are not familiar with programming. Thus, the configuration files themselves do not act as perfect blueprints of the new network. We believe such simple interfaces are necessary for fruitful interaction between scientists in any larger project. 



Porting an existing model
--------------------------

The first steps to port an existing model to CxSystem is to identify the required type of the target network and as well as define the cell group characteristics. CxSystem already has one type of multi-compartmental neuron and four types of point neurons built in which can be used as templates to replicate the neuron types in the target model. Each of the neuron groups will take a single line in the Model and Network file. The physiological parameters of the neurons should also be modified in the physiological file. In the next step, the type and direction of synaptic connections between the neuron groups should be determined. Finally, the required model and simulation parameters can be imported from one of the currently available Model and Network files in the github, or from other existing model (after filter construction) and the initial simulations can be run. |br|
As an example, we have ported the CUBA example from Brian2 documentation originally described in a review paper (Brette et al., 2007). In the brian2 implementation, this example was implemented with only a single neuron group containing 4000 neurons. We implemented this into two groups: a group containing 3200 SS cells (excitatory) and a second group containing 800 BC cells (inhibitory). 
Both excitatory and inhibitory cell sub-groups were fully connected to all the other cells. 
Next, we created a copy of physiological parameters and modified the SS and BC neuron parameters, e.g. Vr, El, Vt, etc., according to the CUBA example. The synaptic weights were also set accordingly. Finally, the essential network parameters, e.g. simulation duration, device, system mode, output folder, was set and the CxSystem was run using the two new csv files. 
