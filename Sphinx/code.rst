Cortical System Package
====================================

The cortical system package consists of five major modules. cortical_system as the main module, creates the target cortical model based on a configuration file (Connections.txt). This configuration line is parsed in cortical module and the neurons/synapses formation of the module is created in brian2 accordingly. The thorugh description of the configuration file can be found in :ref:`config_file`. 


Cortical System module 
------------------------------------
.. module:: cortical_system
.. autoclass:: cortical_system
   :members:
   
   .. automethod:: cortical_system.cortical_system.__init__
