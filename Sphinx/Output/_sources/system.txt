How The System works
====================

The implemented system employs the Brian2GeNN python module to generate GeNN (GPU enhanced Neuronal Network simulation environment) code for eventually running the brian2 codes on GeNN. In order to understand how this system works, one should initially understand how Brian2GeNN restrains brian2. Most of the exclusions are presented in `Brian2GeNN documentation
<http://brian2genn.readthedocs.io/en/latest/introduction/exclusions.html>`_. Perhaps the most effective limitation is lack of support for using Multiple networks in brian2, i.e. only the *magic network* can be used. Using the *magic network*, only the "visible" objects that are explicitly defined in the code will be collected. In other words, any brian2 object that is created in a custom class, will not be collected and will eventually raise an error. Two solutions are available for this issue: 

**- Build a Syntax Bank:**

In this method, a syntax string is built for all brian2 internal objects. These syntaxes are then run after the main object call. Suppose the cortical system object is named *CX* and a NeuronGroup() object called *NG* is created in a method inside the *CX*: 

::

	NG = NeuronGroup(1, eqs)
	
As mentioned earlier, *NG* will not be collected for magic network as it is inside a method of *CX*. However, we can "anticipate" a syntax for this neuron group and save it in a syntax bank attribute in *CX*: 

::

	syn1 = "NG = NeuronGroup(1, eqs)"
	CX.syntax_bank = append(CX.syntax_bank, syn1) 

All of the elements of this *CX.syntax_bank* can then be iterated and run using the dynamic compiler, i.e. **exec** command. Note that all the sub objects of an syntax should be saved in syntax_bank as well. For instance, the last example will raise an error since *eqs* is not defined. Hence, before running the *syn1*, one should initially run the syntax for *eqs* object. 

This method has a fundamental limitations: first, the syntax bank should run in a hierarchical manner. In previous example, the syntax for *eqs* should be run before *syn1*. Similarly, NeuronGroup() syntaxes should be run before Synapses() and synapses.connect() should be run after Synapses(). This process is in need of a "manual" coding in the main file for running the codes in a hierarchical manner which cause untidiness.

Both current and next approach will then need a prefix for name of the objects. For instance, all of the NeuronGroup() should have a prefix of *NG* which is followed by a number based on the index of the neuron group. 

For each neuron group, similar prefixes are also needed for variables such as: 

  + Number of neurons in each group: *NN*
  + Equation: *NE*
  + Threshold value: *NT*
  + Reset value: *NRes*
  + Refraction value: *NRef*
  + Namespace: *NS*

Several prefixes are also demanded for Synapses() objects:

  + Synaptic object: *S*
  + Synaptic equation: *SE*
  + Pre Synaptic group equation: *SPre*
  + Post Synaptic group equation: *SPost*
  + Namespace: *SNS*
  + .connect(): *SC*
  + weight: *SW*

And similar prefixes for monitors: 

  + Spike Monitors: *SpMon*
  + State Monitors: *StMon* 

**- Update Globals():**

Although mentioned as a dangerous method in the literature, updating the Globals() directly, is a practical approach in our case. This method is partially similar to previous method as it also needs all the prefixes and corresponding variables. However, the variables does not have to *wait* inside the syntax bank to be run after the main object call. They can be implicitly executed inside the main object and still become "visible" to the magic network by putting them in Globals(). In this case, the user does not have to face a manual syntax-executer outside of the main object call. 

Accordingly, most of the *exec* commands inside the main object cortical_system() are creating the required variable and making them visible to *magic network* of brian2 by updating the Globals() and putting them inside that. In the following example, the NG0 is put in the Globals(): 

::

	globals().update({'NG0':NG0})

Fig.1 illustrates the schematic of the cortical system internal component: 

.. figure:: ../main_uml.png
   :align: center 

   Fig.1 simplified UML diagram of the cortical system
