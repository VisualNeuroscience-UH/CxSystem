/*--------------------------------------------------------------------------
   Author: Thomas Nowotny
  
   Institute: Center for Computational Neuroscience and Robotics
              University of Sussex
	      Falmer, Brighton BN1 9QJ, UK 
  
   email to:  T.Nowotny@sussex.ac.uk
  
   initial version: 2010-02-07
   
   This file contains neuron model declarations.
  
--------------------------------------------------------------------------*/

#ifndef _MODELSPEC_H_
#define _MODELSPEC_H_ //!< macro for avoiding multiple inclusion during compilation

//--------------------------------------------------------------------------
/*! \file modelSpec.h

\brief Header file that contains the class (struct) definition of neuronModel for 
defining a neuron model and the class definition of NNmodel for defining a neuronal network model. 
Part of the code generation and generated code sections.
*/
//--------------------------------------------------------------------------

#include <vector>
#include <string>
using namespace std;
#include "global.h"
#include "sparseProjection.h"

void initGeNN();

unsigned int GeNNReady= 0;

//neuronType
unsigned int MAPNEURON; //!< variable attaching the name "MAPNEURON" 
unsigned int POISSONNEURON; //!< variable attaching the name "POISSONNEURON" 
unsigned int TRAUBMILES_FAST; //!< variable attaching the name "TRAUBMILES_FAST" 
unsigned int TRAUBMILES_ALTERNATIVE; //!< variable attaching the name "TRAUBMILES_ALTERNATIVE" 
unsigned int TRAUBMILES_SAFE; //!< variable attaching the name "TRAUBMILES_SAFE" 
unsigned int TRAUBMILES; //!< variable attaching the name "TRAUBMILES" 
unsigned int TRAUBMILES_PSTEP;//!< variable attaching the name "TRAUBMILES_PSTEP" 
unsigned int IZHIKEVICH; //!< variable attaching the name "IZHIKEVICH" 
unsigned int IZHIKEVICH_V; //!< variable attaching the name "IZHIKEVICH_V" 
unsigned int SPIKESOURCE; //!< variable attaching the name "SPIKESOURCE"
#define MAXNRN 7 // maximum number of neuron types: SpineML needs to know this

#define SYNTYPENO 4

//synapseType
unsigned int NSYNAPSE;  //!< Variable attaching  the name NSYNAPSE to predefined synapse type 0, which is a non-learning synapse
unsigned int NGRADSYNAPSE; //!< Variable attaching  the name NGRADSYNAPSE to predefined synapse type 1 which is a graded synapse wrt the presynaptic voltage
unsigned int LEARN1SYNAPSE; //!< Variable attaching  the name LEARN1SYNAPSE to the predefined synapse type 2 which is a learning using spike timing; uses a primitive STDP rule for learning

//connectivity of the network (synapseConnType)
#define ALLTOALL 0  //!< Macro attaching the label "ALLTOALL" to connectivity type 0 
#define DENSE 1 //!< Macro attaching the label "DENSE" to connectivity type 1
#define SPARSE 2//!< Macro attaching the label "SPARSE" to connectivity type 2

//conductance type (synapseGType)
#define INDIVIDUALG 0  //!< Macro attaching the label "INDIVIDUALG" to method 0 for the definition of synaptic conductances
#define GLOBALG 1 //!< Macro attaching the label "GLOBALG" to method 1 for the definition of synaptic conductances
#define INDIVIDUALID 2 //!< Macro attaching the label "INDIVIDUALID" to method 2 for the definition of synaptic conductances

#define NO_DELAY 0 //!< Macro used to indicate no synapse delay for the group (only one queue slot will be generated)

#define NOLEARNING 0 //!< Macro attaching the label "NOLEARNING" to flag 0 
#define LEARNING 1 //!< Macro attaching the label "LEARNING" to flag 1 

#define EXITSYN 0 //!< Macro attaching the label "EXITSYN" to flag 0 (excitatory synapse)
#define INHIBSYN 1 //!< Macro attaching the label "INHIBSYN" to flag 1 (inhibitory synapse)

#define TRUE 1 //!< Macro attaching the label "TRUE" to value 1
#define FALSE 0 //!< Macro attaching the label "FALSE" to value 0

#define CPU 0 //!< Macro attaching the label "CPU" to flag 0
#define GPU 1 //!< Macro attaching the label "GPU" to flag 1

#define GENN_FLOAT 0  //!< Macro attaching the label "GENN_FLOAT" to flag 0. Used by NNModel::setPrecision()
#define GENN_DOUBLE 1  //!< Macro attaching the label "GENN_DOUBLE" to flag 1. Used by NNModel::setPrecision()

#define AUTODEVICE -1  //!< Macro attaching the label AUTODEVICE to flag -1. Used by setGPUDevice

// for purposes of STDP
#define SPK_THRESH_STDP 0.0f //!< Macro defining the spiking threshold for the purposes of STDP
//#define MAXSPKCNT 50000

//postsynaptic parameters
unsigned int EXPDECAY; //default - exponential decay
unsigned int IZHIKEVICH_PS; //empty postsynaptic rule for the Izhikevich model.
// currently values >1 will be defined by code generation.
#define MAXPOSTSYN 2 // maximum number of postsynaptic integration: SpineML needs to know this

class dpclass {
public:
  virtual double calculateDerivedParameter(int index, vector < double > pars, double dt = 1.0) {return -1;}
};

//! \brief class (struct) for specifying a neuron model.
struct neuronModel
{
    string simCode; /*!< \brief Code that defines the execution of one timestep of integration of the neuron model
		    The code will refer to $(NN) for the value of the variable with name "NN". It needs to refer to the predefined variable "ISYN", i.e. contain $(ISYN), if it is to receive input. */
    string thresholdConditionCode; /*!< \brief Code evaluating to a bool (e.g. "V > 20") that defines the condition for a true spike in the described neuron model */
    string resetCode; /*!< \brief Code that defines the reset action taken after a spike occurred. This can be empty */
    string supportCode; //!< \brief Support code is made available within the neuron kernel definition file and is meant to contain user defined device functions that are used in the neuron codes. Hash defines are also allowed if appropriately safeguarded against multiple definition by using #ifndef; functions should be declared as "__host__ __device__" to be available for both GPU and CPU versions
    vector<string> varNames; //!< Names of the variables in the neuron model
    vector<string> tmpVarNames; //!< never used
    vector<string> varTypes; //!< Types of the variable named above, e.g. "float". Names and types are matched by their order of occurrence in the vector.
    vector<string> tmpVarTypes; //!< never used
    vector<string> pNames; //!< Names of (independent) parameters of the model. 
    vector<string> dpNames; /*!< \brief Names of dependent parameters of the model.      
			      The dependent parameters are functions of independent parameters that enter into the neuron model. To avoid unecessary computational overhead, these parameters are calculated at compile time and inserted as explicit values into the generated code. See method NNmodel::initDerivedNeuronPara for how this is done.*/ 
    vector<string> extraGlobalNeuronKernelParameters; //!< Additional parameter in the neuron kernel; it is translated to a population specific name but otherwise assumed to be one parameter per population rather than per neuron.
    vector<string> extraGlobalNeuronKernelParameterTypes; //!< Additional parameters in the neuron kernel; they are translated to a population specific name but otherwise assumed to be one parameter per population rather than per neuron.
    dpclass * dps; //!< \brief Derived parameters
    bool needPreSt; //!< \brief Whether presynaptic spike times are needed or not
    bool needPostSt; //!< \brief Whether postsynaptic spike times are needed or not
};

/*! \brief Structure to hold the information that defines a post-synaptic model (a model of how synapses affect post-synaptic neuron variables, classically in the form of a synaptic current). It also allows to define an equation for the dynamics that can be applied to the summed synaptic input variable "insyn".
 */

struct postSynModel
{
    string postSyntoCurrent; //!< \brief Code that defines how postsynaptic update is translated to current 
    string postSynDecay; //!< \brief Code that defines how postsynaptic current decays 
    string supportCode; //!< \brief Support code is made available within the neuron kernel definition file and is meant to contain user defined device functions that are used in the neuron codes. Hash defines are also allowed if appropriately safeguarded against multiple definition by using #ifndef; functions should be declared as "__host__ __device__" to be available for both GPU and CPU versions
    vector<string> varNames; //!< Names of the variables in the postsynaptic model
    vector<string> varTypes; //!< Types of the variable named above, e.g. "float". Names and types are matched by their order of occurrence in the vector.
    vector<string> pNames; //!< Names of (independent) parameters of the model. 
    vector<string> dpNames; //!< \brief Names of dependent parameters of the model. 
    dpclass *dps; //!< \brief Derived parameters 
};

/*! \brief Structure to hold the information that defines a weightupdate model (a model of how spikes affect synaptic (and/or) (mostly) post-synaptic neuron variables. It also allows to define changes in response to post-synaptic spikes/spike-like events.
 */

class weightUpdateModel
{
public:
    string simCode; //!< \brief Simulation code that is used for true spikes (only one time step after spike detection)
  string simCodeEvnt; //!< \brief Simulation code that is used for spike events (all the instances where event threshold condition is met)
  string simLearnPost; //!< \brief Simulation code which is used in the learnSynapsesPost kernel/function, where postsynaptic neuron spikes before the presynaptic neuron in the STDP window.
  string evntThreshold; //!< \brief Simulation code for spike event detection.
  string synapseDynamics; //!< \brief Simulation code for synapse dynamics independent of spike detection
  string simCode_supportCode; //!< \brief Support code is made available within the synapse kernel definition file and is meant to contain user defined device functions that are used in the neuron codes. Hash defines are also allowed if appropriately safeguarded against multiple definition by using #ifndef; functions should be declared as "__host__ __device__" to be available for both GPU and CPU versions; note that this support code is available to simCode, evntThreshold and simCodeEvnt
  string simLearnPost_supportCode; //!< \brief Support code is made available within the synapse kernel definition file and is meant to contain user defined device functions that are used in the neuron codes. Hash defines are also allowed if appropriately safeguarded against multiple definition by using #ifndef; functions should be declared as "__host__ __device__" to be available for both GPU and CPU versions
  string synapseDynamics_supportCode; //!< \brief Support code is made available within the synapse kernel definition file and is meant to contain user defined device functions that are used in the neuron codes. Hash defines are also allowed if appropriately safeguarded against multiple definition by using #ifndef; functions should be declared as "__host__ __device__" to be available for both GPU and CPU versions
  vector<string> varNames; //!< \brief Names of the variables in the postsynaptic model
  vector<string> varTypes; //!< \brief Types of the variable named above, e.g. "float". Names and types are matched by their order of occurrence in the vector.
  vector<string> pNames; //!< \brief Names of (independent) parameters of the model. 
  vector<string> dpNames; //!< \brief Names of dependent parameters of the model. 

  vector<string> extraGlobalSynapseKernelParameters; //!< Additional parameter in the neuron kernel; it is translated to a population specific name but otherwise assumed to be one parameter per population rather than per synapse.

  vector<string> extraGlobalSynapseKernelParameterTypes; //!< Additional parameters in the neuron kernel; they are translated to a population specific name but otherwise assumed to be one parameter per population rather than per synapse.
  dpclass *dps;
  bool needPreSt; //!< \brief Whether presynaptic spike times are needed or not
  bool needPostSt; //!< \brief Whether postsynaptic spike times are needed or not
};

/*! \brief Structure to hold the information that defines synapse dynamics (a model of how synapse variables change over time, independent of or in addition to changes when spikes occur).
 */

/*===============================================================
//! \brief class NNmodel for specifying a neuronal network model.
//
================================================================*/

class NNmodel
{

public:


  // PUBLIC MODEL VARIABLES
  //========================

  string name; //!< Name of the neuronal newtwork model
  string ftype; //!< Type of floating point variables (float, double, ...; default: float)
  string RNtype; //!< Underlying type for random number generation (default: long)
  int final; //!< Flag for whether the model has been finalized
  unsigned int needSt; //!< Whether last spike times are needed at all in this network model (related to STDP)
  unsigned int needSynapseDelay; //!< Whether delayed synapse conductance is required in the network
  bool timing;
  unsigned int seed;
  unsigned int resetKernel;  //!< The identity of the kernel in which the spike counters will be reset.

  // PUBLIC NEURON VARIABLES
  //========================

  unsigned int neuronGrpN; //!< Number of neuron groups
  vector<string> neuronName; //!< Names of neuron groups
  vector<unsigned int> neuronN; //!< Number of neurons in group
  vector<unsigned int> sumNeuronN; //!< Summed neuron numbers
  vector<unsigned int> padSumNeuronN; //!< Padded summed neuron numbers
  vector<unsigned int> neuronPostSyn; //! Postsynaptic methods to the neuron
  vector<unsigned int> neuronType; //!< Types of neurons
  vector<vector<double> > neuronPara; //!< Parameters of neurons
  vector<vector<double> > dnp; //!< Derived neuron parameters
  vector<vector<double> > neuronIni; //!< Initial values of neurons
  vector<vector<unsigned int> > inSyn; //!< The ids of the incoming synapse groups
  vector<vector<unsigned int> > outSyn; //!< The ids of the outgoing synapse groups
  vector<bool> neuronNeedSt; //!< Whether last spike time needs to be saved for a group
  vector<bool> neuronNeedTrueSpk; //!< Whether spike-like events from a group are required
  vector<bool> neuronNeedSpkEvnt; //!< Whether spike-like events from a group are required
  vector<vector<bool> > neuronVarNeedQueue; //!< Whether a neuron variable needs queueing for syn code
  vector<string> neuronSpkEvntCondition; //!< Will contain the spike event condition code when spike events are used
  vector<unsigned int> neuronDelaySlots; //!< The number of slots needed in the synapse delay queues of a neuron group
  vector<int> neuronHostID; //!< The ID of the cluster node which the neuron groups are computed on
  vector<int> neuronDeviceID; //!< The ID of the CUDA device which the neuron groups are comnputed on


  // PUBLIC SYNAPSE VARIABLES
  //=========================

  unsigned int synapseGrpN; //!< Number of synapse groups
  vector<string> synapseName; //!< Names of synapse groups
  //vector<unsigned int>synapseNo; // !<numnber of synapses in a synapse group
  vector<unsigned int> maxConn; //!< Padded summed maximum number of connections for a neuron in the neuron groups
  vector<unsigned int> padSumSynapseKrnl; //Combination of padSumSynapseTrgN and padSumMaxConn to support both sparse and all-to-all connectivity in a model
  vector<unsigned int> synapseType; //!< Types of synapses
  vector<unsigned int> synapseConnType; //!< Connectivity type of synapses
  vector<unsigned int> synapseGType; //!< Type of specification method for synaptic conductance
  vector<unsigned int> synapseSpanType; //!< Execution order of synapses in the kernel. It determines whether synapses are executed in parallel for every postsynaptic neuron (0, default), or for every presynaptic neuron (1). 
  vector<unsigned int> synapseSource; //!< Presynaptic neuron groups
  vector<unsigned int> synapseTarget; //!< Postsynaptic neuron groups
  vector<unsigned int> synapseInSynNo; //!< IDs of the target neurons' incoming synapse variables for each synapse group
  vector<unsigned int> synapseOutSynNo; //!< The target neurons' outgoing synapse for each synapse group
  vector<bool> synapseUsesTrueSpikes; //!< Defines if synapse update is done after detection of real spikes (only one point after threshold)
  vector<bool> synapseUsesSpikeEvents; //!< Defines if synapse update is done after detection of spike events (every point above threshold)
  vector<bool> synapseUsesPostLearning; //!< Defines if anything is done in case of postsynaptic neuron spiking before presynaptic neuron (punishment in STDP etc.) 
  vector<bool> synapseUsesSynapseDynamics; //!< Defines if there is any continuos synapse dynamics defined
  vector<vector<string> > synapseSpkEvntVars; //!< Defines variable names that are needed in the SpkEvnt condition and that are pre-fetched for that purpose into shared memory
  vector<vector<double> > synapsePara; //!< parameters of synapses
  vector<vector<double> > synapseIni; //!< Initial values of synapse variables
  vector<vector<double> > dsp_w;  //!< Derived synapse parameters (weightUpdateModel only)
  vector<unsigned int> postSynapseType; //!< Types of post-synaptic model
  vector<vector<double> > postSynapsePara; //!< parameters of postsynapses
  vector<vector<double> > postSynIni; //!< Initial values of postsynaptic variables
  vector<vector<double> > dpsp;  //!< Derived postsynapse parameters
  unsigned int lrnGroups; //!< Number of synapse groups with learning
  vector<unsigned int> padSumLearnN; //!< Padded summed neuron numbers of learn group source populations
  vector<unsigned int> lrnSynGrp; //!< Enumeration of the IDs of synapse groups that learn
  vector<unsigned int> synapseDelay; //!< Global synaptic conductance delay for the group (in time steps)
  unsigned int synDynGroups; //!< Number of synapse groups that define continuous synapse dynamics
  vector<unsigned int> synDynGrp; //!< Enumeration of the IDs of synapse groups that have synapse Dynamics
  vector<unsigned int> padSumSynDynN; //!< Padded summed neuron numbers of synapse dynamics group source populations
  vector<int> synapseHostID; //!< The ID of the cluster node which the synapse groups are computed on
  vector<int> synapseDeviceID; //!< The ID of the CUDA device which the synapse groups are comnputed on

  // PUBLIC KERNEL PARAMETER VARIABLES
  //=========================
  unsigned int totalKernelParameterSize;
  unsigned int kernelParameterAlign;
  vector<string> kernelParameters;
  vector<string> kernelParameterTypes;
  vector<string> kernelParameterPopulations;
    
private:


  // PRIVATE NEURON FUNCTIONS
  //=========================

  void setNeuronName(unsigned int, const string); //!< Never used
  void setNeuronN(unsigned int, unsigned int); //!< Never used
  void setNeuronType(unsigned int, unsigned int); //!< Never used
  void setNeuronPara(unsigned int, double*); //!< Never used
  void setNeuronIni(unsigned int, double*); //!< Never used
  unsigned int findNeuronGrp(const string); //!< Find the the ID number of a neuron group by its name 
  void initDerivedNeuronPara(unsigned int); //!< Method for calculating the values of derived neuron parameters.
  void initNeuronSpecs(unsigned int); //!< Method for calculating neuron IDs, taking into account the blocksize padding between neuron populations; also initializes nThresh and neuronNeedSt for a population of neurons.


  // PRIVATE SYNAPSE FUNCTIONS
  //==========================

  void setSynapseName(unsigned int, const string); //!< Never used
  void setSynapseType(unsigned int, unsigned int); //!< Never used
  void setSynapseSource(unsigned int, unsigned int); //!< Never used
  void setSynapseTarget(unsigned int, unsigned int); //!< Never used
  void setSynapsePara(unsigned int, double*); //!< Never used
  void setSynapseConnType(unsigned int, unsigned int); //!< Never used
  void setSynapseGType(unsigned int, unsigned int); //!< Never used
  unsigned int findSynapseGrp(const string); //< Find the the ID number of a synapse group by its name
  void initDerivedSynapsePara(unsigned int); //!< Method for calculating the values of derived synapse parameters.
  void initDerivedPostSynapsePara(unsigned int); //!< Method for calculating the values of derived postsynapse parameters.
  void registerSynapsePopulation(unsigned int); //!< Method to register a new synapse population with the inSyn list of the target neuron population

public:


  // PUBLIC MODEL FUNCTIONS
  //=======================

  NNmodel();
  ~NNmodel();
  void setName(const string); //!< Method to set the neuronal network model name

  void setPrecision(unsigned int);//!< Set numerical precision for floating point

  void setTiming(bool); //!< Set whether timers and timing commands are to be included

  void setSeed(unsigned int); //!< Set the random seed (disables automatic seeding if argument not 0).

  void checkSizes(unsigned int *, unsigned int *, unsigned int *); //< Check if the sizes of the initialized neuron and synapse groups are correct.

#ifndef CPU_ONLY
  void setGPUDevice(int); //!< Method to choose the GPU to be used for the model. If "AUTODEVICE' (-1), GeNN will choose the device based on a heuristic rule.
#endif
  string scalarExpr(const double);

  // PUBLIC NEURON FUNCTIONS
  //========================

  void addNeuronPopulation(const char *, unsigned int, unsigned int, double *, double *); //!< Method for adding a neuron population to a neuronal network model, using C style character array for the name of the population

  void addNeuronPopulation(const string, unsigned int, unsigned int, double *, double *); //!< Method for adding a neuron population to a neuronal network model, using C++ string for the name of the population

  void addNeuronPopulation(const string, unsigned int, unsigned int, vector<double>, vector<double>); //!< Method for adding a neuron population to a neuronal network model, using C++ string for the name of the population

  void setNeuronClusterIndex(const string neuronGroup, int hostID, int deviceID); //!< Function for setting which host and which device a neuron group will be simulated on

//! This function has been deprecated in GeNN 2.2
  void activateDirectInput(const string, unsigned int type);
//! This function has been deprecated in GeNN 2.2
  void setConstInp(const string, double);

  // PUBLIC SYNAPSE FUNCTIONS
  //=========================

  void addSynapsePopulation(const string name, unsigned int syntype, unsigned int conntype, unsigned int gtype, const string src, const string trg, double *p); //!< Overload of method for backwards compatibility

  void addSynapsePopulation(const char *, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, const char *, const char *, double *, double *, double *); //!< Method for adding a synapse population to a neuronal network model, using C style character array for the name of the population
  void addSynapsePopulation(const string, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, const string, const string, double *, double *, double *); //!< Overloaded version without initial variables for synapses
  void addSynapsePopulation(const string, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, const string, const string, double *,double *, double *, double *); //!< Method for adding a synapse population to a neuronal network model, using C++ string for the name of the population
  void addSynapsePopulation(const string, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, const string, const string, vector<double>, vector<double>, vector<double>, vector<double>); //!< Method for adding a synapse population to a neuronal network model, using C++ string for the name of the population

  void setSynapseG(const string, double); //!< Method for setting the conductance (g) value for a synapse population with "GLOBALG" charactertistic
  //void setSynapseNo(unsigned int,unsigned int); // !< Sets the number of connections for sparse matrices  

  void setMaxConn(const string, unsigned int); //< Set maximum connections per neuron for the given group (needed for optimization by sparse connectivity)

  void setSpanTypeToPre(const string); //!< Method for switching the execution order of synapses to pre-to-post
  
  void setSynapseClusterIndex(const string synapseGroup, int hostID, int deviceID); //!< Function for setting which host and which device a synapse group will be simulated on

  void initLearnGrps();
  void finalize();
};



#endif
