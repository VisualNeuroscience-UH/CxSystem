Cortical System Package
====================================

The cortical system package consists of five major modules. cortical_system as the main module, creates the target cortical model based on a configuration file (Connections.txt). This configuration line is parsed in cortical module and the neurons/synapses formation of the module is created in brian2 accordingly. The thorugh description of the configuration file can be found in :ref:`config_file`. 


Cortical System module 
------------------------------------
.. module:: cortical_system
.. autoclass:: cortical_system
   :members:
   
   .. automethod:: cortical_system.cortical_system.__init__

Brian2 Objects definitions module
------------------------------------
.. module:: brian2_obj_defs
.. autoclass:: customized_neuron
   :members:

   .. automethod:: brian2_obj_defs.customized_neuron.__init__ 

.. autoclass:: customized_synapse
   :members:

   .. automethod:: brian2_obj_defs.customized_synapse.__init__ 


Brian2 objects namespaces module
------------------------------------
.. module:: brian2_obj_namespaces
.. autoclass:: synapse_namespaces
   :members:

   .. automethod:: brian2_obj_namespaces.synapse_namespaces.__init__ 

Stimuli module
----------------
.. module:: stimuli
.. autoclass:: stimuli
   :members:

   .. automethod:: stimuli.stimuli.__init__
