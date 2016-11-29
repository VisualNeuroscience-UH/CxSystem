Cortical System Package
====================================

The cortical system package consists of five major modules. CxSystem as the main module, creates the target cortical model based on a configuration file (Connections.txt). This configuration line is parsed in cortical module and the neurons/synapses formation of the module is created in brian2 accordingly. The thorugh description of the configuration file can be found in :ref:`config_file`.


Cortical System module 
------------------------------------
.. module:: CxSystem
.. autoclass:: CxSystem
   :members:
   
   .. automethod:: CxSystem.CxSystem.__init__

Brian2 Objects definitions module
------------------------------------
.. module:: brian2_obj_defs
.. autoclass:: neuron_reference
   :members:

   .. automethod:: brian2_obj_defs.neuron_reference.__init__

.. autoclass:: synapse_reference
   :members:

   .. automethod:: brian2_obj_defs.synapse_reference.__init__


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

Save data module 
------------------
.. module:: save_data
.. autoclass:: save_data
   :members:

   .. automethod:: save_data.save_data.__init__
