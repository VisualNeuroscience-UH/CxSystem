
Physiological Configuration File
=================================


The format of the physiological configuration file is different from that of the network and model configuration file in a sense that the parameters in the configuration file grow vertically. Typically there are four types of columns in a physiological configuration file:


* **Variables**: which is the first column and contains the name of the variable. Some values are in form of key:value pairs and others are just a regular variable with a value. 

::

   calcium_concentration,  ,1

This line defines a variable called calcium_concentration and sets its value to 1. Note that the key is empty.

* **Keys**: The keys for the former type of variables, i.e. those that contain key:value pairs, are defined in this column. In case the variable does not have a key, this cell in front of the variable could be left empty. 
  
* **Values**: Value will be set for either a variable with no keys, or for keys of a variable where the variable itself does not have a value, i.e. is in form of a key:value pairs.

::


   BC	,C		,100 * pF
   	,gL		,10 * nS
   	,Vr		,-67.66 * mV	
   	,EL		,-67.66 * mV
   	,VT		,-38.8 * mV
   	,DeltaT		,2 * mV	
   	,Ee		,0 * mV	
   	,Ei		,-75 * mV	
   	,tau_e		,3 * ms
   	,tau_i		,8.3 * ms
   	,taum_soma	,C/gL	
   	,V_res		,VT- 4 * mV	
   	,Vcut		,VT+ 5*DeltaT


This example defines the different parameters and corresponding values for a BC neuron. The variable in this example is BC, where keys are its parameters and values are corresponding values.

Note the following line in the above example:

::

    	taum_soma	,C/gL


The key defines the Tau_m of the soma in the BC neuron. The value however, is a formula that uses the other keys of the BC neuron, i.e. C and gL.  

