/*--------------------------------------------------------------------------
  Author: Thomas Nowotny
  
  Institute: Center for Computational Neuroscience and Robotics
  University of Sussex
  Falmer, Brighton BN1 9QJ, UK 
  
  email to:  T.Nowotny@sussex.ac.uk
  
  initial version: 2010-02-07
  
  --------------------------------------------------------------------------*/

//-----------------------------------------------------------------------
/*!  \file generateRunner.cc 
  
  \brief Contains functions to generate code for running the
  simulation on the GPU, and for I/O convenience functions between GPU
  and CPU space. Part of the code generation section.
*/
//--------------------------------------------------------------------------

#include "stringutils.h"

void variable_def(ofstream &os, string type, string name)
{
    os << type << " " << name << ";" << ENDL;
#ifndef CPU_ONLY
    os << type << " d_" << name << ";" << ENDL;
    os << "__device__ " << type << " dd_" << name << ";" << ENDL;
#endif
}

void extern_variable_def(ofstream &os, string type, string name)
{
    os << "extern " << type << " " << name << ";" << ENDL;
}

//--------------------------------------------------------------------------
/*!
  \brief A function that generates predominantly host-side code.

  In this function host-side functions and other code are generated,
  including: Global host variables, "allocatedMem()" function for
  allocating memories, "freeMem" function for freeing the allocated
  memories, "initialize" for initializing host variables, "gFunc" and
  "initGRaw()" for use with plastic synapses if such synapses exist in
  the model.  
*/
//--------------------------------------------------------------------------

#include <cfloat>

void genRunner(NNmodel &model, //!< Model description
	       string path, //!< path for code generation
	       ostream &mos //!< output stream for messages
    )
{
    string name;
    size_t size, tmp;
    unsigned int nt, st, pst;
    unsigned int mem = 0;
    float memremsparse= 0;
    ofstream os;
        
    string SCLR_MIN;
    string SCLR_MAX;
    if (model.ftype == tS("float")) {
	SCLR_MIN= tS(FLT_MIN)+tS("f");
	SCLR_MAX= tS(FLT_MAX)+tS("f");
    }

    if (model.ftype == tS("double")) {
	SCLR_MIN= tS(DBL_MIN);
	SCLR_MAX= tS(DBL_MAX);
    }

    for (int i= 0; i < nModels.size(); i++) {
	for (int k= 0; k < nModels[i].varTypes.size(); k++) {
	    substitute(nModels[i].varTypes[k], "scalar", model.ftype);
	}
	substitute(nModels[i].simCode, "SCALAR_MIN", SCLR_MIN);
	substitute(nModels[i].resetCode, "SCALAR_MIN", SCLR_MIN);
	substitute(nModels[i].simCode, "SCALAR_MAX", SCLR_MAX);
	substitute(nModels[i].resetCode, "SCALAR_MAX", SCLR_MAX);
	substitute(nModels[i].simCode, "scalar", model.ftype);
	substitute(nModels[i].resetCode, "scalar", model.ftype);
    }
    for (int i= 0; i < weightUpdateModels.size(); i++) {
	for (int k= 0; k < weightUpdateModels[i].varTypes.size(); k++) {
	    substitute(weightUpdateModels[i].varTypes[k], "scalar", model.ftype);
	}
	substitute(weightUpdateModels[i].simCode, "SCALAR_MIN", SCLR_MIN);
	substitute(weightUpdateModels[i].simCodeEvnt, "SCALAR_MIN", SCLR_MIN);
	substitute(weightUpdateModels[i].simLearnPost, "SCALAR_MIN", SCLR_MIN);
	substitute(weightUpdateModels[i].synapseDynamics, "SCALAR_MIN", SCLR_MIN);
	substitute(weightUpdateModels[i].simCode, "SCALAR_MAX", SCLR_MAX);
	substitute(weightUpdateModels[i].simCodeEvnt, "SCALAR_MAX", SCLR_MAX);
	substitute(weightUpdateModels[i].simLearnPost, "SCALAR_MAX", SCLR_MAX);
	substitute(weightUpdateModels[i].synapseDynamics, "SCALAR_MAX", SCLR_MAX);
	substitute(weightUpdateModels[i].simCode, "scalar", model.ftype);
	substitute(weightUpdateModels[i].simCodeEvnt, "scalar", model.ftype);
	substitute(weightUpdateModels[i].simLearnPost, "scalar", model.ftype);
	substitute(weightUpdateModels[i].synapseDynamics, "scalar", model.ftype);
    }
    for (int i= 0; i < postSynModels.size(); i++) {
	for (int k= 0; k < postSynModels[i].varTypes.size(); k++) {
	    substitute(postSynModels[i].varTypes[k], "scalar", model.ftype);
	}
	substitute(postSynModels[i].postSyntoCurrent, "SCALAR_MIN", SCLR_MIN);
	substitute(postSynModels[i].postSynDecay, "SCALAR_MIN", SCLR_MIN);
	substitute(postSynModels[i].postSyntoCurrent, "SCALAR_MAX", SCLR_MAX);
	substitute(postSynModels[i].postSynDecay, "SCALAR_MAX", SCLR_MAX);
	substitute(postSynModels[i].postSyntoCurrent, "scalar", model.ftype);
	substitute(postSynModels[i].postSynDecay, "scalar", model.ftype);
    }
    
    // generate definitions.h
    // this file contains helpful macros and is separated out so that it can also be used by other code that is compiled separately
    name= path + toString("/") + model.name + toString("_CODE/definitions.h");
    os.open(name.c_str());  
    writeHeader(os);
    os << ENDL;
    
       // write doxygen comment
    os << "//-------------------------------------------------------------------------" << ENDL;
    os << "/*! \\file definitions.h" << ENDL << ENDL;
    os << "\\brief File generated from GeNN for the model " << model.name << " containing useful Macros used for both GPU amd CPU versions." << ENDL;
    os << "*/" << ENDL;
    os << "//-------------------------------------------------------------------------" << ENDL << ENDL;
    
    os << "#ifndef DEFINITIONS_H" << ENDL;
    os << "#define DEFINITIONS_H" << ENDL;

    os << "#ifndef DT" << ENDL;
    os << "#define DT " << DT << ENDL;
    os << "#endif" << ENDL;

    for (int i= 0; i < model.neuronGrpN; i++) {
	os << "#define glbSpkShift" << model.neuronName[i];
	if (model.neuronDelaySlots[i] > 1) {
	    os << " spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i];
	}
	else {
	    os << " 0";
	}
	os << ENDL;
    }
    for (int i = 0; i < model.neuronGrpN; i++) {
      	// convenience macros for accessing spike count 
	os << "#define spikeCount_" << model.neuronName[i] << " glbSpkCnt" << model.neuronName[i];
	if ((model.neuronDelaySlots[i] > 1) && (model.neuronNeedTrueSpk[i])) {
	  os << "[spkQuePtr" << model.neuronName[i] << "]" << ENDL;
	}
	else {
	  os << "[0]" << ENDL;
	}
	// convenience macro for accessing spikes
	os << "#define spike_" << model.neuronName[i];
	if ((model.neuronDelaySlots[i] > 1) && (model.neuronNeedTrueSpk[i])) {
	  os << " (glbSpk" << model.neuronName[i] << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << "))" << ENDL;
	}
	else {
	  os << " glbSpk" << model.neuronName[i] << ENDL;
	}
      	if (model.neuronNeedSpkEvnt[i]) {
	  // convenience macros for accessing spike count 
	  os << "#define spikeEventCount_" << model.neuronName[i] << " glbSpkCntEvnt" << model.neuronName[i];
	  if (model.neuronDelaySlots[i] > 1) {
	    os << "[spkQuePtr" << model.neuronName[i] << "]" << ENDL;
	  }
	  else {
	    os << "[0]" << ENDL;
	  }
	  // convenience macro for accessing spikes
	  os << "#define spikeEvent_" << model.neuronName[i];
	  if (model.neuronDelaySlots[i] > 1) {
	    os << " (glbSpkEvnt" << model.neuronName[i] << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << "))" << ENDL;
	  }
	  else {
	    os << " glbSpkEvnt" << model.neuronName[i] << ENDL;
	  }
	}
    }

#ifndef CPU_ONLY

    // generate headers for the communication utility functions such as 
    // pullXXXStateFromDevice() etc. This is useful for the brian2genn
    // interface where we do more proper compile/link and do not want
    // to include runnerGPU.cc into all relevant code_objects (e.g.
    // spike and state monitors

    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying things to device" << ENDL << ENDL;
    for (int i = 0; i < model.neuronGrpN; i++) {
	os << "void push" << model.neuronName[i] << "StateToDevice();" << ENDL;
	os << "void push" << model.neuronName[i] << "SpikesToDevice();" << ENDL;
	os << "void push" << model.neuronName[i] << "SpikeEventsToDevice();" << ENDL;
	os << "void push" << model.neuronName[i] << "CurrentSpikesToDevice();" << ENDL;
	os << "void push" << model.neuronName[i] << "CurrentSpikeEventsToDevice();" << ENDL;
    }
    for (int i = 0; i < model.synapseGrpN; i++) {
        os << "#define push" << model.synapseName[i] << "ToDevice push" << model.synapseName[i] << "StateToDevice" << ENDL << ENDL;
	os << "void push" << model.synapseName[i] << "StateToDevice();" << ENDL;
    }
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying things from device" << ENDL << ENDL;
    
    for (int i = 0; i < model.neuronGrpN; i++) {
 	os << "void pull" << model.neuronName[i] << "StateFromDevice();" << ENDL;
	os << "void pull" << model.neuronName[i] << "SpikesFromDevice();" << ENDL;
	os << "void pull" << model.neuronName[i] << "SpikeEventsFromDevice();" << ENDL;
    	os << "void pull" << model.neuronName[i] << "CurrentSpikesFromDevice();" << ENDL;
		os << "void pull" << model.neuronName[i] << "CurrentSpikeEventsFromDevice();" << ENDL;
    }
    for (int i = 0; i < model.synapseGrpN; i++) {
	os << "#define pull" << model.synapseName[i] << "FromDevice pull" << model.synapseName[i] << "StateFromDevice" << ENDL << ENDL;
	os << "void pull" << model.synapseName[i] << "StateFromDevice();" << ENDL;
    }

    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying values to device" << ENDL;
    os << "void copyStateToDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying spikes to device" << ENDL;
    os << "void copySpikesToDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying current spikes to device" << ENDL;
    os << "void copyCurrentSpikesToDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying spike events to device" << ENDL;    
    os << "void copySpikeEventsToDevice();" << ENDL;    
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying current spikes to device" << ENDL;
    os << "void copyCurrentSpikeEventsToDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying values from device" << ENDL;
    os << "void copyStateFromDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying spikes from device" << ENDL;
    os << "void copySpikesFromDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying current spikes from device" << ENDL;
    os << "void copyCurrentSpikesFromDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying spike numbers from device (note, only use when only interested"<< ENDL;
    os << "// in spike numbers; copySpikesFromDevice() already includes this)" << ENDL;
    os << "void copySpikeNFromDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------"<< ENDL;
    os << "// global copying spikeEvents from device" << ENDL;
    os << "void copySpikeEventsFromDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying current spikeEvents from device" << ENDL;
    os << "void copyCurrentSpikeEventsFromDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying spike event numbers from device (note, only use when only interested" << ENDL;
    os << "// in spike numbers; copySpikeEventsFromDevice() already includes this)" << ENDL;
    os << "void copySpikeEventNFromDevice();" << ENDL;
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// the actual time stepping procedure" << ENDL;
    os << "void stepTimeGPU(unsigned int flags);" << ENDL;

#endif

    //---------------------------------
    // HOST AND DEVICE NEURON VARIABLES
    os << "// neuron variables" << ENDL;
    for (int i = 0; i < model.neuronGrpN; i++) {
	nt = model.neuronType[i];

	extern_variable_def(os, tS("unsigned int *"), "glbSpkCnt"+model.neuronName[i]);
	extern_variable_def(os, tS("unsigned int *"), "glbSpk"+model.neuronName[i]);
	if (model.neuronNeedSpkEvnt[i]) {
	    extern_variable_def(os, tS("unsigned int *"), "glbSpkCntEvnt"+model.neuronName[i]);
	    extern_variable_def(os, tS("unsigned int *"), "glbSpkEvnt"+model.neuronName[i]);
	}
	if (model.neuronDelaySlots[i] > 1) {
	    os << "extern unsigned int spkQuePtr" << model.neuronName[i] << ";" << ENDL;
	}
	if (model.neuronNeedSt[i]) {
	    extern_variable_def(os, model.ftype+" *", "sT"+model.neuronName[i]);
	}
	for (int k = 0, l= nModels[nt].varNames.size(); k < l; k++) {
	    extern_variable_def(os, nModels[nt].varTypes[k]+" *", nModels[nt].varNames[k]+model.neuronName[i]);
	}
	
    }
    os << ENDL;

    //----------------------------------
    // HOST AND DEVICE SYNAPSE VARIABLES

    os << "// synapse variables" << ENDL;
    for (int i = 0; i < model.synapseGrpN; i++) {
	st = model.synapseType[i];
	pst = model.postSynapseType[i];

	extern_variable_def(os, model.ftype+" *", "inSyn"+model.synapseName[i]);
	if (model.synapseGType[i] == INDIVIDUALID) {
	    extern_variable_def(os, tS("uint32_t *"), "gp"+model.synapseName[i]);
	}
	if (model.synapseConnType[i] == SPARSE) {
	    os << "extern SparseProjection C" << model.synapseName[i] << ";" << ENDL;
	}
	if (model.synapseGType[i] == INDIVIDUALG) { // not needed for GLOBALG, INDIVIDUALID
	    for (int k = 0, l = weightUpdateModels[st].varNames.size(); k < l; k++) {
		extern_variable_def(os, weightUpdateModels[st].varTypes[k]+" *", weightUpdateModels[st].varNames[k]+model.synapseName[i]);
	    }
	    for (int k = 0, l = postSynModels[pst].varNames.size(); k < l; k++) {
		extern_variable_def(os, postSynModels[pst].varTypes[k]+" *", postSynModels[pst].varNames[k]+model.synapseName[i]); 
	    }
	}
    }
    os << ENDL;
    // write global variables for the extra global neuron kernel parameters.
    // These are assumed not to be pointers, if they are the user needs to take care of allocation etc
    if (model.totalKernelParameterSize > 0) {
	os << " // memory space that holds the kernel arguments/parameters" << ENDL;
	os << "extern char kernelPara[" << model.totalKernelParameterSize << "];" << ENDL;
	for (int k = 0, l= model.kernelParameters.size(); k < l; k++) {
	    os << "extern " << model.kernelParameterTypes[k] << "& " << model.kernelParameters[k];
	    os << model.kernelParameterPopulations[k] << ";" << ENDL;
	}
	os << ENDL;
    }
    os << ENDL;
    os << "#endif" << ENDL;
    os.close();

    // generate definitions.h
    // this file contains helpful macros and is separated out so that it can also be used by other code that is compiled separately
    name= path + toString("/") + model.name + toString("_CODE/support_code.h");
    os.open(name.c_str());  
    writeHeader(os);
    os << ENDL;
    
       // write doxygen comment
    os << "//-------------------------------------------------------------------------" << ENDL;
    os << "/*! \\file support_code.h" << ENDL << ENDL;
    os << "\\brief File generated from GeNN for the model " << model.name << " containing support code provided by the user and used for both GPU amd CPU versions." << ENDL;
    os << "*/" << ENDL;
    os << "//-------------------------------------------------------------------------" << ENDL << ENDL;
    
    os << "#ifndef SUPPORT_CODE_H" << ENDL;
    os << "#define SUPPORT_CODE_H" << ENDL;
    // write the support codes
    os << "// support code for neuron and synapse models" << endl;
    for (int i= 0; i < model.neuronGrpN; i++) {
	if (nModels[model.neuronType[i]].supportCode != tS("")) {
	    os << "namespace " << model.neuronName[i] << "_neuron" << OB(11) << ENDL;
	    os << nModels[model.neuronType[i]].supportCode << ENDL;
	    os << CB(11) << " // end of support code namespace " << model.neuronName[i] << ENDL;
	}
    }
    for (int i= 0; i < model.synapseGrpN; i++) {
	if (weightUpdateModels[model.synapseType[i]].simCode_supportCode != tS("")) {
	    os << "namespace " << model.synapseName[i] << "_weightupdate_simCode " << OB(11) << ENDL;
	    os << weightUpdateModels[model.synapseType[i]].simCode_supportCode << ENDL;
	    os << CB(11) << " // end of support code namespace " << model.synapseName[i] << "_weightupdate_simCode " << ENDL;
	}
	if (weightUpdateModels[model.synapseType[i]].simLearnPost_supportCode != tS("")) {
	    os << "namespace " << model.synapseName[i] << "_weightupdate_simLearnPost " << OB(11) << ENDL;
	    os << weightUpdateModels[model.synapseType[i]].simLearnPost_supportCode << ENDL;
	    os << CB(11) << " // end of support code namespace " << model.synapseName[i] << "_weightupdate_simLearnPost " << ENDL;
	}
	if (weightUpdateModels[model.synapseType[i]].synapseDynamics_supportCode != tS("")) {
	    os << "namespace " << model.synapseName[i] << "_weightupdate_synapseDynamics " << OB(11) << ENDL;
	    os << weightUpdateModels[model.synapseType[i]].synapseDynamics_supportCode << ENDL;
	    os << CB(11) << " // end of support code namespace " << model.synapseName[i] << "_weightupdate_synapseDynamics " << ENDL;
	}
	if (postSynModels[model.postSynapseType[i]].supportCode != tS("")) {
	    os << "namespace " << model.synapseName[i] << "_postsyn " << OB(11) << ENDL;
	    os << postSynModels[model.postSynapseType[i]].supportCode << ENDL;
	    os << CB(11) << " // end of support code namespace " << model.synapseName[i] << "_postsyn " << ENDL;
	}
	
    }
    os << "#endif" << ENDL;
    os.close();
    
//    cout << "entering genRunner" << ENDL;
    name= path + toString("/") + model.name + toString("_CODE/runner.cc");
    os.open(name.c_str());  
    writeHeader(os);
    os << ENDL;

    // write doxygen comment
    os << "//-------------------------------------------------------------------------" << ENDL;
    os << "/*! \\file runner.cc" << ENDL << ENDL;
    os << "\\brief File generated from GeNN for the model " << model.name << " containing general control code." << ENDL;
    os << "*/" << ENDL;
    os << "//-------------------------------------------------------------------------" << ENDL << ENDL;

    os << "#include <cstdio>" << ENDL;
    os << "#include <cassert>" << ENDL;
    os << "#include <stdint.h>" << ENDL;
    os << "#include \"utils.h\"" << ENDL << ENDL;
    os << "#include \"numlib/simpleBit.h\"" << ENDL << ENDL;
    if (model.timing) os << "#include \"hr_time.cpp\"" << ENDL;
    os << "#define RUNNER_CC_COMPILE" << ENDL;
    os << "#include \"definitions.h\"" << ENDL;
    os << ENDL;

//    os << "#ifndef int_" << ENDL;
//    os << "#define int_(X) ((int) (X))" << ENDL;
//    os << "#endif" << ENDL;

    os << "#ifndef scalar" << ENDL;
    os << "typedef " << model.ftype << " scalar;" << ENDL;
    os << "#endif" << ENDL;
  
    os << "#ifndef SCALAR_MIN" << ENDL;
    os << "#define SCALAR_MIN " << SCLR_MIN << ENDL;
    os << "#endif" << ENDL;
  
    os << "#ifndef SCALAR_MAX" << ENDL;
    os << "#define SCALAR_MAX " << SCLR_MAX << ENDL;
    os << "#endif" << ENDL;
  os << "#define Conductance SparseProjection" << ENDL;
  os << "/*struct Conductance is deprecated. \n\
  By GeNN 2.0, Conductance is renamed as SparseProjection and contains only indexing values. \n\
  Please consider updating your user code by renaming Conductance as SparseProjection \n\
  and making g member a synapse variable.*/" << ENDL;

    // write MYRAND macro
    os << "#ifndef MYRAND" << ENDL;
    os << "#define MYRAND(Y,X) Y = Y * 1103515245 + 12345; X = (Y >> 16);" << ENDL;
    os << "#endif" << ENDL << ENDL;
    os << "#ifndef MYRAND_MAX" << ENDL;
    os << "#define MYRAND_MAX 0x0000FFFFFFFFFFFFLL" << ENDL;
    os << "#endif" << ENDL;
  if (model.timing) {
#ifndef CPU_ONLY
      os << "cudaEvent_t neuronStart, neuronStop;" << ENDL;
#endif
      os << "double neuron_tme;" << ENDL;
      os << "CStopWatch neuron_timer;" << ENDL;
      if (model.synapseGrpN > 0) {
#ifndef CPU_ONLY
	  os << "cudaEvent_t synapseStart, synapseStop;" << ENDL;
#endif
	  os << "double synapse_tme;" << ENDL;
	  os << "CStopWatch synapse_timer;" << ENDL;
      }
      if (model.lrnGroups > 0) {
#ifndef CPU_ONLY
	  os << "cudaEvent_t learningStart, learningStop;" << ENDL;
#endif
	  os << "double learning_tme;" << ENDL;
	  os << "CStopWatch learning_timer;" << ENDL;
      }
      if (model.synDynGroups > 0) {
#ifndef CPU_ONLY
	  os << "cudaEvent_t synDynStart, synDynStop;" << ENDL;
#endif
	  os << "double synDyn_tme;" << ENDL;
	  os << "CStopWatch synDyn_timer;" << ENDL;
      }
  } 

#ifndef CPU_ONLY
    // write CUDA error handler macro
    os << "#ifndef CHECK_CUDA_ERRORS" << ENDL;
    os << "#define CHECK_CUDA_ERRORS(call) {\\" << ENDL;
    os << "    cudaError_t error = call;\\" << ENDL;
    os << "    if (error != cudaSuccess) {\\" << ENDL;
    os << "        fprintf(stderr, \"%s: %i: cuda error %i: %s\\n\", __FILE__, __LINE__, (int) error, cudaGetErrorString(error));\\" << ENDL;
    os << "        exit(EXIT_FAILURE);\\" << ENDL;
    os << "    }\\" << ENDL;
    os << "}" << ENDL;
    os << "#endif" << ENDL << ENDL;

    os << "template<class T>" << ENDL;
    os << "void deviceMemAllocate(T* hostPtr, const T &devSymbol, size_t size)" << ENDL;
    os << "{" << ENDL;
    os << "    void *devptr;" << ENDL;
    os << "    CHECK_CUDA_ERRORS(cudaMalloc(hostPtr, size));" << ENDL;
    os << "    CHECK_CUDA_ERRORS(cudaGetSymbolAddress(&devptr, devSymbol));" << ENDL;
    os << "    CHECK_CUDA_ERRORS(cudaMemcpy(devptr, hostPtr, sizeof(void*), cudaMemcpyHostToDevice));" << ENDL;
    os << "}" << ENDL << ENDL;
#endif

    // write doxygen comment
    os << "//-------------------------------------------------------------------------" << ENDL;
    os << "/*! \\brief Function to convert a firing probability (per time step) " << ENDL;
    os << "to an integer of type uint64_t that can be used as a threshold for the GeNN random number generator to generate events with the given probability." << ENDL;
    os << "*/" << ENDL;
    os << "//-------------------------------------------------------------------------" << ENDL << ENDL;

    os << "void convertProbabilityToRandomNumberThreshold(" << model.ftype << " *p_pattern, " << model.RNtype << " *pattern, int N)" << ENDL;
    os << "{" << ENDL;
    os << "    " << model.ftype << " fac= pow(2.0, (double) sizeof(" << model.RNtype << ")*8-16);" << ENDL;
    os << "    for (int i= 0; i < N; i++) {" << ENDL;
    //os << "        assert(p_pattern[i] <= 1.0);" << ENDL;
    os << "        pattern[i]= (" << model.RNtype << ") (p_pattern[i]*fac);" << ENDL;
    os << "    }" << ENDL;
    os << "}" << ENDL << ENDL;

    // write doxygen comment
    os << "//-------------------------------------------------------------------------" << ENDL;
    os << "/*! \\brief Function to convert a firing rate (in kHz) " << ENDL;
    os << "to an integer of type uint64_t that can be used as a threshold for the GeNN random number generator to generate events with the given rate." << ENDL;
    os << "*/" << ENDL;
    os << "//-------------------------------------------------------------------------" << ENDL << ENDL;

    os << "void convertRateToRandomNumberThreshold(" << model.ftype << " *rateKHz_pattern, " << model.RNtype << " *pattern, int N)" << ENDL;
    os << "{" << ENDL;
    os << "    " << model.ftype << " fac= pow(2.0, (double) sizeof(" << model.RNtype << ")*8-16)*DT;" << ENDL;
    os << "    for (int i= 0; i < N; i++) {" << ENDL;
    //os << "        assert(rateKHz_pattern[i] <= 1.0);" << ENDL;
    os << "        pattern[i]= (" << model.RNtype << ") (rateKHz_pattern[i]*fac);" << ENDL;
    os << "    }" << ENDL;
    os << "}" << ENDL << ENDL;

    os << "// global variables" << ENDL;
    os << "unsigned long long iT= 0;" << ENDL;
    os << model.ftype << " t;" << ENDL;
    //---------------------------------
    // HOST AND DEVICE NEURON VARIABLES

    os << "// neuron variables" << ENDL;
#ifndef CPU_ONLY
    os << "__device__ volatile unsigned int d_done;" << ENDL;
#endif
    for (int i = 0; i < model.neuronGrpN; i++) {
	nt = model.neuronType[i];

	variable_def(os, tS("unsigned int *"), "glbSpkCnt"+model.neuronName[i]);
	variable_def(os, tS("unsigned int *"), "glbSpk"+model.neuronName[i]);
	if (model.neuronNeedSpkEvnt[i]) {
	    variable_def(os, tS("unsigned int *"), "glbSpkCntEvnt"+model.neuronName[i]);
	    variable_def(os, tS("unsigned int *"), "glbSpkEvnt"+model.neuronName[i]);
	}
	if (model.neuronDelaySlots[i] > 1) {
	    os << "unsigned int spkQuePtr" << model.neuronName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	    os << "__device__ volatile unsigned int dd_spkQuePtr" << model.neuronName[i] << ";" << ENDL;
#endif
	}
	if (model.neuronNeedSt[i]) {
	    variable_def(os, model.ftype+" *", "sT"+model.neuronName[i]);
	}
	for (int k = 0, l= nModels[nt].varNames.size(); k < l; k++) {
	    variable_def(os, nModels[nt].varTypes[k]+" *", nModels[nt].varNames[k]+model.neuronName[i]);
	}
	
    }
    os << ENDL;

    //----------------------------------
    // HOST AND DEVICE SYNAPSE VARIABLES

    os << "// synapse variables" << ENDL;
    for (int i = 0; i < model.synapseGrpN; i++) {
	st = model.synapseType[i];
	pst = model.postSynapseType[i];

	variable_def(os, model.ftype+" *", "inSyn"+model.synapseName[i]);
	if (model.synapseGType[i] == INDIVIDUALID) {
	    variable_def(os, tS("uint32_t *"), "gp"+model.synapseName[i]);
	}
	if (model.synapseConnType[i] == SPARSE) {
	    os << "SparseProjection C" << model.synapseName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	    os << "unsigned int *d_indInG" << model.synapseName[i] << ";" << ENDL;
	    os << "__device__ unsigned int *dd_indInG" << model.synapseName[i] << ";" << ENDL;
	    os << "unsigned int *d_ind" << model.synapseName[i] << ";" << ENDL;
	    os << "__device__ unsigned int *dd_ind" << model.synapseName[i] << ";" << ENDL;
	    if (model.synapseUsesSynapseDynamics[i]) {
		os << "unsigned int *d_preInd" << model.synapseName[i] << ";" << ENDL;
		os << "__device__ unsigned int *dd_preInd" << model.synapseName[i] << ";" << ENDL;
	    }
	    if (model.synapseUsesPostLearning[i]) {
		// TODO: make conditional on post-spike driven learning actually taking place
		os << "unsigned int *d_revIndInG" << model.synapseName[i] << ";" << ENDL;
		os << "__device__ unsigned int *dd_revIndInG" << model.synapseName[i] << ";" << ENDL;
		os << "unsigned int *d_revInd" << model.synapseName[i] << ";" << ENDL;
		os << "__device__ unsigned int *dd_revInd" << model.synapseName[i] << ";" << ENDL;
		os << "unsigned int *d_remap" << model.synapseName[i] << ";" << ENDL;
		os << "__device__ unsigned int *dd_remap" << model.synapseName[i] << ";" << ENDL;
	    }
#endif
	}
	if (model.synapseGType[i] == INDIVIDUALG) { // not needed for GLOBALG, INDIVIDUALID
	    for (int k = 0, l = weightUpdateModels[st].varNames.size(); k < l; k++) {
		variable_def(os, weightUpdateModels[st].varTypes[k]+" *", weightUpdateModels[st].varNames[k]+model.synapseName[i]);
	    }
	    for (int k = 0, l = postSynModels[pst].varNames.size(); k < l; k++) {
		variable_def(os, postSynModels[pst].varTypes[k]+" *", postSynModels[pst].varNames[k]+model.synapseName[i]); 
	    }
	}
    }
    os << ENDL;
    // write global variables for the extra global neuron kernel parameters.
    // These are assumed not to be pointers, if they are the user needs to take care of allocation etc
    if (model.totalKernelParameterSize > 0) {
	os << " // memory space that holds the kernel arguments/parameters" << ENDL;
	os << "char kernelPara[" << model.totalKernelParameterSize << "];" << ENDL;
#ifndef CPU_ONLY
	os << "void *d_kernelPara;" << ENDL;
	os << "__device__ char dd_kernelPara[" << model.totalKernelParameterSize << "];" << ENDL;
#endif
	unsigned int offset= 0;
	for (int k = 0, l= model.kernelParameters.size(); k < l; k++) {
	    os << model.kernelParameterTypes[k] << " &" << model.kernelParameters[k];
	    os << model.kernelParameterPopulations[k] << "= *((";
	    os << model.kernelParameterTypes[k] << " *)(kernelPara+" << offset << "));" << ENDL;
#ifndef CPU_ONLY
	    os << "__device__ " << model.kernelParameterTypes[k] << " &dd_" << model.kernelParameters[k];
	    os << model.kernelParameterPopulations[k] << "= *((";
	    os << model.kernelParameterTypes[k] << " *)(dd_kernelPara+" << offset << "));" << ENDL;
#endif	    
	    offset+= model.kernelParameterAlign;
	}
	os << ENDL;
    }
    os << ENDL;

    os << "#include \"sparseUtils.cc\"" << ENDL << ENDL;
    // include simulation kernels
#ifndef CPU_ONLY
    os << "#include \"runnerGPU.cc\"" << ENDL << ENDL;
#endif
    os << "#include \"neuronFnct.cc\"" << ENDL;
    if (model.synapseGrpN > 0) {
	os << "#include \"synapseFnct.cc\"" << ENDL;
    }


    // ---------------------------------------------------------------------
    // Function for setting the CUDA device and the host's global variables.
    // Also estimates memory usage on device ...
  
    os << "void allocateMem()" << ENDL;
    os << "{" << ENDL;
#ifndef CPU_ONLY
    os << "    CHECK_CUDA_ERRORS(cudaSetDevice(" << theDev << "));" << ENDL;
#endif
    //cout << "model.neuronGroupN " << model.neuronGrpN << ENDL;
    //os << "    " << model.ftype << " free_m, total_m;" << ENDL;
    //os << "    cudaMemGetInfo((size_t*) &free_m, (size_t*) &total_m);" << ENDL;

    if (model.timing) {
#ifndef CPU_ONLY
	os << "    cudaEventCreate(&neuronStart);" << ENDL;
	os << "    cudaEventCreate(&neuronStop);" << ENDL;
#endif
	os << "    neuron_tme= 0.0;" << ENDL;
	if (model.synapseGrpN > 0) {
#ifndef CPU_ONLY
	    os << "    cudaEventCreate(&synapseStart);" << ENDL;
	    os << "    cudaEventCreate(&synapseStop);" << ENDL;
#endif
	    os << "    synapse_tme= 0.0;" << ENDL;
	}
	if (model.lrnGroups > 0) {
#ifndef CPU_ONLY
	    os << "    cudaEventCreate(&learningStart);" << ENDL;
	    os << "    cudaEventCreate(&learningStop);" << ENDL;
#endif
	    os << "    learning_tme= 0.0;" << ENDL;
	}
	if (model.synDynGroups > 0) {
#ifndef CPU_ONLY
	    os << "    cudaEventCreate(&synDynStart);" << ENDL;
	    os << "    cudaEventCreate(&synDynStop);" << ENDL;
#endif
	    os << "    synDyn_tme= 0.0;" << ENDL;
	}
    }

    // ALLOCATE NEURON VARIABLES
    for (int i = 0; i < model.neuronGrpN; i++) {
	nt = model.neuronType[i];

	if (model.neuronNeedTrueSpk[i]) {
	    size = model.neuronDelaySlots[i];
	}
	else {
	    size = 1;
	}
	os << "    glbSpkCnt" << model.neuronName[i] << " = new unsigned int[" << size << "];" << ENDL;
#ifndef CPU_ONLY
	os << "    deviceMemAllocate(&d_glbSpkCnt" << model.neuronName[i];
	os << ", dd_glbSpkCnt" << model.neuronName[i] << ", ";
	os << size << " * sizeof(unsigned int));" << ENDL;
	mem += size * sizeof(unsigned int);
#endif
	if (model.neuronNeedTrueSpk[i]) {
	    size = model.neuronN[i] * model.neuronDelaySlots[i];
	}
	else {
	    size = model.neuronN[i];
	}
	os << "    glbSpk" << model.neuronName[i] << " = new unsigned int[" << size << "];" << ENDL;
#ifndef CPU_ONLY
	os << "    deviceMemAllocate(&d_glbSpk" << model.neuronName[i];
	os << ", dd_glbSpk" << model.neuronName[i] << ", ";
	os << size << " * sizeof(unsigned int));" << ENDL;
	mem += size * sizeof(unsigned int);
#endif
	if (model.neuronNeedSpkEvnt[i]) {
	    size = model.neuronDelaySlots[i];
	    os << "    glbSpkCntEvnt" << model.neuronName[i] << " = new unsigned int[" << size << "];" << ENDL;
#ifndef CPU_ONLY
	    os << "    deviceMemAllocate(&d_glbSpkCntEvnt" << model.neuronName[i];
	    os << ", dd_glbSpkCntEvnt" << model.neuronName[i] << ", ";
	    os << size << " * sizeof(unsigned int));" << ENDL;
	    mem += size * sizeof(unsigned int);
#endif
	    size = model.neuronN[i] * model.neuronDelaySlots[i];
	    os << "    glbSpkEvnt" << model.neuronName[i] << " = new unsigned int[" << size << "];" << ENDL;
#ifndef CPU_ONLY
	    os << "    deviceMemAllocate(&d_glbSpkEvnt" << model.neuronName[i];
	    os << ", dd_glbSpkEvnt" << model.neuronName[i] << ", ";
	    os << size << " * sizeof(unsigned int));" << ENDL;
	    mem += size * sizeof(unsigned int);
#endif
	}

	if (model.neuronNeedSt[i]) {
	    size = model.neuronN[i] * model.neuronDelaySlots[i];
	    os << "    sT" << model.neuronName[i] << " = new " << model.ftype << "[" << size << "];" << ENDL;
#ifndef CPU_ONLY
	    os << "    deviceMemAllocate(&d_sT" << model.neuronName[i];
	    os << ", dd_sT" << model.neuronName[i] << ", ";
	    os << size << " * sizeof(" << model.ftype << "));" << ENDL;
	    mem += size * theSize(model.ftype);
#endif
	}

	// Variable are queued only if they are referenced in forward synapse code.
	for (int j = 0; j < nModels[nt].varNames.size(); j++) {
	    if (model.neuronVarNeedQueue[i][j]) {
		size = model.neuronN[i] * model.neuronDelaySlots[i];
	    }
	    else {
		size = model.neuronN[i];
	    }
	    os << "    " << nModels[nt].varNames[j] << model.neuronName[i];
	    os << " = new " << nModels[nt].varTypes[j] << "[" << size << "];" << ENDL;
#ifndef CPU_ONLY
	    os << "    deviceMemAllocate(&d_" << nModels[nt].varNames[j] << model.neuronName[i];
	    os << ", dd_" << nModels[nt].varNames[j] << model.neuronName[i] << ", ";
	    os << size << " * sizeof(" << nModels[nt].varTypes[j] << "));" << ENDL;
	    mem += size * theSize(nModels[nt].varTypes[j]);
#endif
	}
	os << ENDL; 
    }

    // ALLOCATE SYNAPSE VARIABLES
    for (int i = 0; i < model.synapseGrpN; i++) {
	st = model.synapseType[i];
	pst = model.postSynapseType[i];

	size = model.neuronN[model.synapseTarget[i]];
	os << "    inSyn" << model.synapseName[i] << " = new " << model.ftype << "[" << size << "];" << ENDL;
#ifndef CPU_ONLY
	os << "    deviceMemAllocate(&d_inSyn" << model.synapseName[i];
	os << ", dd_inSyn" << model.synapseName[i];
	os << ", " << size << " * sizeof(" << model.ftype << "));" << ENDL; 
	mem += size * theSize(model.ftype);
#endif
	// note, if GLOBALG we put the value at compile time
	if (model.synapseGType[i] == INDIVIDUALID) {
	    size = (model.neuronN[model.synapseSource[i]] * model.neuronN[model.synapseTarget[i]]) / 32 + 1;
	    os << "    gp" << model.synapseName[i] << " = new uint32_t[" << size << "];" << ENDL;
#ifndef CPU_ONLY
	    os << "    deviceMemAllocate(&d_gp" << model.synapseName[i];
	    os << ", dd_gp" << model.synapseName[i];
	    os << ", " << size << " * sizeof(uint32_t));" << ENDL;
	    mem += size * sizeof(uint32_t);
#endif
	}

	// allocate user-defined weight model variables
	// if they are sparse, allocate later in the allocatesparsearrays function when we know the size of the network
	if ((model.synapseConnType[i] != SPARSE) && (model.synapseGType[i] == INDIVIDUALG)) {
	    size = model.neuronN[model.synapseSource[i]] * model.neuronN[model.synapseTarget[i]];
	    for (int k= 0, l= weightUpdateModels[st].varNames.size(); k < l; k++) {
		os << "    " << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		os << " = new " << weightUpdateModels[st].varTypes[k] << "[" << size << "];" << ENDL;
#ifndef CPU_ONLY
		os << "    deviceMemAllocate(&d_" << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		os << ", dd_" << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		os << ", " << size << " * sizeof(" << weightUpdateModels[st].varTypes[k] << "));" << ENDL; 
		mem += size * theSize(weightUpdateModels[st].varTypes[k]);
#endif
	    } 
	}

	if (model.synapseGType[i] == INDIVIDUALG) { // not needed for GLOBALG, INDIVIDUALID
	    size = model.neuronN[model.synapseTarget[i]];
	    for (int k= 0, l= postSynModels[pst].varNames.size(); k < l; k++) {
		os << "    " << postSynModels[pst].varNames[k] << model.synapseName[i];
		os << " = new " << postSynModels[pst].varTypes[k] << "[" << size << "];" << ENDL;
#ifndef CPU_ONLY
		os << "    deviceMemAllocate(&d_" << postSynModels[pst].varNames[k] << model.synapseName[i];
		os << ", dd_" << postSynModels[pst].varNames[k] << model.synapseName[i];
		os << ", " << size << " * sizeof(" << postSynModels[pst].varTypes[k] << "));" << ENDL;      
		mem += size * theSize(postSynModels[pst].varTypes[k]);
#endif
	    }
	}
	os << ENDL;
    }
#ifndef CPU_ONLY
    if (model.totalKernelParameterSize > 0) {
	os << "// Make the connection where to copy kernel arguments/parameters" << ENDL; 
	os << "CHECK_CUDA_ERRORS(cudaGetSymbolAddress((void **) &d_kernelPara, dd_kernelPara));" << ENDL;
    }
#endif
    os << "}" << ENDL << ENDL;


    // ------------------------------------------------------------------------
    // initializing variables
    // write doxygen comment
    os << "//-------------------------------------------------------------------------" << ENDL;
    os << "/*! \\brief Function to (re)set all model variables to their compile-time, homogeneous initial values." << ENDL;
    os << " Note that this typically includes synaptic weight values. The function (re)sets host side variables and copies them to the GPU device." << ENDL;
    os << "*/" << ENDL;
    os << "//-------------------------------------------------------------------------" << ENDL << ENDL;

    os << "void initialize()" << ENDL;
    os << "{" << ENDL;

    if (model.seed == 0) {
	os << "    srand((unsigned int) time(NULL));" << ENDL;
    }
    else {
	os << "    srand((unsigned int) " << model.seed << ");" << ENDL;
    }
    os << ENDL;

    // INITIALISE NEURON VARIABLES
    os << "    // neuron variables" << ENDL;
    for (int i = 0; i < model.neuronGrpN; i++) {
	nt = model.neuronType[i];

	if (model.neuronDelaySlots[i] > 1) {
	    os << "    spkQuePtr" << model.neuronName[i] << " = 0;" << ENDL;
#ifndef CPU_ONLY
	    os << "CHECK_CUDA_ERRORS(cudaMemcpyToSymbol(dd_spkQuePtr" << model.neuronName[i];
	    os << ", &spkQuePtr" << model.neuronName[i];
	    os << ", " << "sizeof(unsigned int), 0, cudaMemcpyHostToDevice));" << ENDL;	
#endif
	}

	if ((model.neuronNeedTrueSpk[i]) && (model.neuronDelaySlots[i] > 1)) {
	    os << "    for (int i = 0; i < " << model.neuronDelaySlots[i] << "; i++) {" << ENDL;
	    os << "        glbSpkCnt" << model.neuronName[i] << "[i] = 0;" << ENDL;
	    os << "    }" << ENDL;
	    os << "    for (int i = 0; i < " << model.neuronN[i] * model.neuronDelaySlots[i] << "; i++) {" << ENDL;
	    os << "        glbSpk" << model.neuronName[i] << "[i] = 0;" << ENDL;
	    os << "    }" << ENDL;
	}
	else {
	    os << "    glbSpkCnt" << model.neuronName[i] << "[0] = 0;" << ENDL;
	    os << "    for (int i = 0; i < " << model.neuronN[i] << "; i++) {" << ENDL;
	    os << "        glbSpk" << model.neuronName[i] << "[i] = 0;" << ENDL;
	    os << "    }" << ENDL;
	}

	if ((model.neuronNeedSpkEvnt[i]) && (model.neuronDelaySlots[i] > 1)) {
	    os << "    for (int i = 0; i < " << model.neuronDelaySlots[i] << "; i++) {" << ENDL;
	    os << "        glbSpkCntEvnt" << model.neuronName[i] << "[i] = 0;" << ENDL;
	    os << "    }" << ENDL;
	    os << "    for (int i = 0; i < " << model.neuronN[i] * model.neuronDelaySlots[i] << "; i++) {" << ENDL;
	    os << "        glbSpkEvnt" << model.neuronName[i] << "[i] = 0;" << ENDL;
	    os << "    }" << ENDL;
	}
	else if (model.neuronNeedSpkEvnt[i]) {
	    os << "    glbSpkCntEvnt" << model.neuronName[i] << "[0] = 0;" << ENDL;
	    os << "    for (int i = 0; i < " << model.neuronN[i] << "; i++) {" << ENDL;
	    os << "        glbSpkEvnt" << model.neuronName[i] << "[i] = 0;" << ENDL;
	    os << "    }" << ENDL;
	}

	if (model.neuronNeedSt[i]) {
	    os << "    for (int i = 0; i < " << model.neuronN[i] * model.neuronDelaySlots[i] << "; i++) {" << ENDL;
	    os << "        sT" <<  model.neuronName[i] << "[i] = -10.0;" << ENDL;
	    os << "    }" << ENDL;
	}

	for (int j = 0; j < nModels[nt].varNames.size(); j++) {
	    if (model.neuronVarNeedQueue[i][j]) {
		os << "    for (int i = 0; i < " << model.neuronN[i] * model.neuronDelaySlots[i] << "; i++) {" << ENDL;
	    }
	    else {
		os << "    for (int i = 0; i < " << model.neuronN[i] << "; i++) {" << ENDL;
	    }
	    os << "        " << nModels[nt].varNames[j] << model.neuronName[i] << "[i] = " << model.scalarExpr(model.neuronIni[i][j]) << ";" << ENDL;
	    os << "    }" << ENDL;
	}

	if (model.neuronType[i] == POISSONNEURON) {
	    os << "    for (int i = 0; i < " << model.neuronN[i] << "; i++) {" << ENDL;
	    os << "        seed" << model.neuronName[i] << "[i] = rand();" << ENDL;
	    os << "    }" << ENDL;
	}

	if ((model.neuronType[i] == IZHIKEVICH) && (DT != 1.0)) {
	    os << "    fprintf(stderr,\"WARNING: You use a time step different than 1 ms. Izhikevich model behaviour may not be robust.\\n\"); " << ENDL;
	}
    }
    os << ENDL;

    // INITIALISE SYNAPSE VARIABLES
    os << "    // synapse variables" << ENDL;
    for (int i = 0; i < model.synapseGrpN; i++) {
	st = model.synapseType[i];
	pst = model.postSynapseType[i];

	os << "    for (int i = 0; i < " << model.neuronN[model.synapseTarget[i]] << "; i++) {" << ENDL;
	os << "        inSyn" << model.synapseName[i] << "[i] = " << model.scalarExpr(0.0) << ";" << ENDL;
	os << "    }" << ENDL;

	if ((model.synapseConnType[i] != SPARSE) && (model.synapseGType[i] == INDIVIDUALG)) {
	    for (int k= 0, l= weightUpdateModels[st].varNames.size(); k < l; k++) {
		os << "    for (int i = 0; i < " << model.neuronN[model.synapseSource[i]] * model.neuronN[model.synapseTarget[i]] << "; i++) {" << ENDL;
		os << "        " << weightUpdateModels[st].varNames[k] << model.synapseName[i] << "[i] = " << model.scalarExpr(model.synapseIni[i][k]) << ";" << ENDL;
		os << "    }" << ENDL;
	    }
	}

	if (model.synapseGType[i] == INDIVIDUALG) {
	    for (int k= 0, l= postSynModels[pst].varNames.size(); k < l; k++) {
		os << "    for (int i = 0; i < " << model.neuronN[model.synapseTarget[i]] << "; i++) {" << ENDL;
		os << "        " << postSynModels[pst].varNames[k] << model.synapseName[i] << "[i] = " << model.scalarExpr(model.postSynIni[i][k]) << ";" << ENDL;
		os << "    }" << ENDL;
	    }
	}
    }
    os << ENDL << ENDL;
#ifndef CPU_ONLY
    os << "    copyStateToDevice();" << ENDL << ENDL;
    os << "    //initializeAllSparseArrays(); //I comment this out instead of removing to keep in mind that sparse arrays need to be initialised manually by hand later" << ENDL;
#endif
    os << "}" << ENDL << ENDL;


    // ------------------------------------------------------------------------
    // allocating conductance arrays for sparse matrices

    for (int i = 0; i < model.synapseGrpN; i++) {	
	if (model.synapseConnType[i] == SPARSE) {
	    os << "void allocate" << model.synapseName[i] << "(unsigned int connN)" << "{" << ENDL;
	    os << "// Allocate host side variables" << ENDL;
	    os << "  C" << model.synapseName[i] << ".connN= connN;" << ENDL;
	    os << "  C" << model.synapseName[i] << ".indInG= new unsigned int[" << model.neuronN[model.synapseSource[i]] + 1 << "];" << ENDL;
	    os << "  C" << model.synapseName[i] << ".ind= new unsigned int[connN];" << ENDL; 
	    if (model.synapseUsesSynapseDynamics[i]) {
		os << "  C" << model.synapseName[i] << ".preInd= new unsigned int[connN];" << ENDL;
	    } else {
		os << "  C" << model.synapseName[i] << ".preInd= NULL;" << ENDL;
	    }
	    if (model.synapseUsesPostLearning[i]) {
		os << "  C" << model.synapseName[i] << ".revIndInG= new unsigned int[" << model.neuronN[model.synapseTarget[i]] + 1 << "];" << ENDL;
		os << "  C" << model.synapseName[i] << ".revInd= new unsigned int[connN];" << ENDL;       
		os << "  C" << model.synapseName[i] << ".remap= new unsigned int[connN];" << ENDL;       
	    } else {
		os << "  C" << model.synapseName[i] << ".revIndInG= NULL;" << ENDL;
		os << "  C" << model.synapseName[i] << ".revInd= NULL;" << ENDL;       
		os << "  C" << model.synapseName[i] << ".remap= NULL;" << ENDL; 
	    }
	    int st= model.synapseType[i];
	    string size = "C" + model.synapseName[i]+".connN";
	    for (int k= 0, l= weightUpdateModels[st].varNames.size(); k < l; k++) {
		os  << weightUpdateModels[st].varNames[k];
		os << model.synapseName[i]<< "= new " << weightUpdateModels[st].varTypes[k] << "[" << size << "];" << ENDL;
	    }
#ifndef CPU_ONLY
	    os << "// Allocate device side variables" << ENDL;
	    os << "  deviceMemAllocate( &d_indInG" << model.synapseName[i] << ", dd_indInG" << model.synapseName[i];
	    os << ", sizeof(unsigned int) * ("<< model.neuronN[model.synapseSource[i]] + 1 <<"));" << ENDL;
	    os << "  deviceMemAllocate( &d_ind" << model.synapseName[i] << ", dd_ind" << model.synapseName[i];
	    os << ", sizeof(unsigned int) * (" << size << "));" << ENDL;
	    if (model.synapseUsesSynapseDynamics[i]) {
		os << "  deviceMemAllocate( &d_preInd" << model.synapseName[i] << ", dd_preInd" << model.synapseName[i];
		os << ", sizeof(unsigned int) * (" << size << "));" << ENDL;
	    }
	    if (model.synapseUsesPostLearning[i]) {
		os << "  deviceMemAllocate( &d_revIndInG" << model.synapseName[i] << ", dd_revIndInG" << model.synapseName[i];
		os << ", sizeof(unsigned int) * ("<< model.neuronN[model.synapseTarget[i]] + 1 <<"));" << ENDL;
		os << "  deviceMemAllocate( &d_revInd" << model.synapseName[i] << ", dd_revInd" << model.synapseName[i];
		os << ", sizeof(unsigned int) * (" << size <<"));" << ENDL;
		os << "  deviceMemAllocate( &d_remap" << model.synapseName[i] << ", dd_remap" << model.synapseName[i];
		os << ", sizeof(unsigned int) * ("<< size << "));" << ENDL;
	    }
	    for (int k= 0, l= weightUpdateModels[st].varNames.size(); k < l; k++) {     
		os << "deviceMemAllocate(&d_" << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		os << ", dd_" << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		os << ", sizeof("  << weightUpdateModels[st].varTypes[k] << ")*(" << size << "));" << ENDL;       
	    }
#endif
	    os << "}" << ENDL; 
	    os << ENDL;
	    //setup up helper fn for this (specific) popn to generate sparse from dense 
	    os << "void createSparseConnectivityFromDense" << model.synapseName[i] << "(int preN,int postN, " << model.ftype << " *denseMatrix)" << "{" << ENDL;
	    os << "    gennError(\"The function createSparseConnectivityFromDense" << model.synapseName[i] << "() has been deprecated because with the introduction of synapse models that can be fully user-defined and may not contain a conductance variable g the existence condition for synapses has become ill-defined. \\n Please use your own logic and use the general tools allocate" << model.synapseName[i] << "(), countEntriesAbove(), and setSparseConnectivityFromDense().\");" << ENDL;
	    os << "}" << ENDL;
	    os << ENDL;
	}
    }

    // ------------------------------------------------------------------------
    // initializing sparse arrays

#ifndef CPU_ONLY
    os << "void initializeAllSparseArrays() {" << ENDL;
    for (int i = 0; i < model.synapseGrpN; i++) {
	if (model.synapseConnType[i] == SPARSE) {
	    os << "size_t size;" << ENDL;
	    break;
	}
    }
    for (int i= 0; i < model.synapseGrpN; i++) {
	if (model.synapseConnType[i]==SPARSE){
	    os << "size = C" << model.synapseName[i] << ".connN;" << ENDL;
	    os << "  initializeSparseArray(C" << model.synapseName[i] << ",";
	    os << " d_ind" << model.synapseName[i] << ",";
	    os << " d_indInG" << model.synapseName[i] << ",";
	    os << model.neuronN[model.synapseSource[i]] <<");" << ENDL;
	    if (model.synapseUsesSynapseDynamics[i]) {
		os << "  initializeSparseArrayPreInd(C" << model.synapseName[i] << ",";
		os << " d_preInd" << model.synapseName[i] << ");" << ENDL;
	    }
	    if (model.synapseUsesPostLearning[i]) {
		os << "  initializeSparseArrayRev(C" << model.synapseName[i] << ",";
		os << "  d_revInd" << model.synapseName[i] << ",";
		os << "  d_revIndInG" << model.synapseName[i] << ",";
		os << "  d_remap" << model.synapseName[i] << ",";
		os << model.neuronN[model.synapseTarget[i]] <<");" << ENDL;
	    }
	    int st= model.synapseType[i];
	    for (int k= 0, l= weightUpdateModels[st].varNames.size(); k < l; k++) {
		os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_" << weightUpdateModels[st].varNames[k] << model.synapseName[i] << ", "  << weightUpdateModels[st].varNames[k] << model.synapseName[i] << ", sizeof(" << weightUpdateModels[st].varTypes[k] << ") * size , cudaMemcpyHostToDevice));" << ENDL; 
	    }
	}
    }
    os << "}" << ENDL; 
    os << ENDL;
#endif

    // ------------------------------------------------------------------------
    // initialization of variables, e.g. reverse sparse arrays etc. 
    // that the user would not want to worry about
    
    os << "void init" << model.name << "()" << ENDL;
    os << OB(1130) << ENDL;
    unsigned int sparseCount= 0;
    for (int i= 0; i < model.synapseGrpN; i++) {
	if (model.synapseConnType[i] == SPARSE) {
	    sparseCount++;
	    if (model.synapseUsesSynapseDynamics[i]) {
		os << "createPreIndices(" << model.neuronN[model.synapseSource[i]] << ", " << model.neuronN[model.synapseTarget[i]] << ", &C" << model.synapseName[i] << ");" << ENDL;
	    }
	    if (model.synapseUsesPostLearning[i]) {
		os << "createPosttoPreArray(" << model.neuronN[model.synapseSource[i]] << ", " << model.neuronN[model.synapseTarget[i]] << ", &C" << model.synapseName[i] << ");" << ENDL;
	    }
	}
    }
#ifndef CPU_ONLY
    if (sparseCount > 0) {
	os << "initializeAllSparseArrays();" << ENDL;
    }
#endif
    os << CB(1130) << ENDL;

    // ------------------------------------------------------------------------
    // freeing global memory structures

    os << "void freeMem()" << ENDL;
    os << "{" << ENDL;

    // FREE NEURON VARIABLES
    for (int i = 0; i < model.neuronGrpN; i++) {
	nt = model.neuronType[i];

	os << "    delete[] glbSpkCnt" << model.neuronName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	os << "    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkCnt" << model.neuronName[i] << "));" << ENDL;
#endif
	os << "    delete[] glbSpk" << model.neuronName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	os << "    CHECK_CUDA_ERRORS(cudaFree(d_glbSpk" << model.neuronName[i] << "));" << ENDL;
#endif
	if (model.neuronNeedSpkEvnt[i]) {
	    os << "    delete[] glbSpkCntEvnt" << model.neuronName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	    os << "    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkCntEvnt" << model.neuronName[i] << "));" << ENDL;
#endif
	    os << "    delete[] glbSpkEvnt" << model.neuronName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	    os << "    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkEvnt" << model.neuronName[i] << "));" << ENDL;
#endif
	}
	if (model.neuronNeedSt[i]) {
	    os << "    delete[] sT" << model.neuronName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	    os << "    CHECK_CUDA_ERRORS(cudaFree(d_sT" << model.neuronName[i] << "));" << ENDL;
#endif
	}
	for (int k= 0, l= nModels[nt].varNames.size(); k < l; k++) {
	    os << "    delete[] " << nModels[nt].varNames[k] << model.neuronName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	    os << "    CHECK_CUDA_ERRORS(cudaFree(d_" << nModels[nt].varNames[k] << model.neuronName[i] << "));" << ENDL;
#endif
	}
    }

    // FREE SYNAPSE VARIABLES
    for (int i = 0; i < model.synapseGrpN; i++) {
	st = model.synapseType[i];
	pst = model.postSynapseType[i];

	os << "    delete[] inSyn" << model.synapseName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	os << "    CHECK_CUDA_ERRORS(cudaFree(d_inSyn" << model.synapseName[i] << "));" << ENDL;
#endif
	if (model.synapseConnType[i] == SPARSE) {
	    os << "    C" << model.synapseName[i] << ".connN= 0;" << ENDL;
	    os << "    delete[] C" << model.synapseName[i] << ".indInG;" << ENDL;
	    os << "    delete[] C" << model.synapseName[i] << ".ind;" << ENDL;  
	    if (model.synapseUsesPostLearning[i]) {
		os << "    delete[] C" << model.synapseName[i] << ".revIndInG;" << ENDL;
		os << "    delete[] C" << model.synapseName[i] << ".revInd;" << ENDL;  
		os << "    delete[] C" << model.synapseName[i] << ".remap;" << ENDL;
	    }
	}
	if (model.synapseGType[i] == INDIVIDUALID) {
	    os << "    delete[] gp" << model.synapseName[i] << ";" << ENDL;
#ifndef CPU_ONLY
	    os << "    CHECK_CUDA_ERRORS(cudaFree(d_gp" << model.synapseName[i] << "));" <<ENDL;  	
#endif
	}
	if (model.synapseGType[i] == INDIVIDUALG) {
	    for (int k= 0, l= weightUpdateModels[st].varNames.size(); k < l; k++) {
		os << "    delete[] " << weightUpdateModels[st].varNames[k] << model.synapseName[i] << ";" << ENDL;
#ifndef CPU_ONLY
		os << "    CHECK_CUDA_ERRORS(cudaFree(d_" << weightUpdateModels[st].varNames[k] << model.synapseName[i] << "));" << ENDL;
#endif
	    }
	    for (int k= 0, l= postSynModels[pst].varNames.size(); k < l; k++) {
		os << "    delete[] " << postSynModels[pst].varNames[k] << model.synapseName[i] << ";" << ENDL;
#ifndef CPU_ONLY
		os << "    CHECK_CUDA_ERRORS(cudaFree(d_" << postSynModels[pst].varNames[k] << model.synapseName[i] << "));" << ENDL;
#endif
	    }
	}
    }
    os << "}" << ENDL << ENDL;


// ------------------------------------------------------------------------
//! \brief Method for cleaning up and resetting device while quitting GeNN

  os << "void exitGeNN(){" << ENDL;  
  os << "  freeMem();" << ENDL;
#ifndef CPU_ONLY
  os << "  cudaDeviceReset();" << ENDL;
#endif
  os << "}" << ENDL;


  os << "// ------------------------------------------------------------------------" << ENDL;
  os << "// Throw an error for \"old style\" time stepping calls" << ENDL;
    os << "template <class T>" << ENDL;
    os << "void stepTimeCPU(T arg1, ...)" << ENDL;
    os << OB(101) << ENDL;
    os << "gennError(\"Since GeNN 2.2 the call to step time has changed to not take any arguments. You appear to attempt to pass arguments. This is no longer supported. See the GeNN 2.2. release notes and the manual for examples how to pass data like, e.g., Poisson rates and direct inputs, that were previously handled through arguments.\");" << ENDL; 
    os << CB(101) << endl;
    
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// the actual time stepping procedure" << ENDL;

    os << "void stepTimeCPU()" << ENDL;
    os << "{" << ENDL;

    if (model.synapseGrpN > 0) {
	if (model.synDynGroups > 0) {
	    if (model.timing) os << "        synDyn_timer.startTimer();" << ENDL;
	    os << "        calcSynapseDynamicsCPU(t);" << ENDL;         
	    if (model.timing) {
		os << "        synDyn_timer.stopTimer();" << ENDL;
		os << "        synDyn_tme+= synDyn_timer.getElapsedTime();" << ENDL;
	    }
	}
	if (model.timing) os << "        synapse_timer.startTimer();" << ENDL;
	os << "        calcSynapsesCPU(t);" << ENDL;
	if (model.timing) {
	    os << "        synapse_timer.stopTimer();" << ENDL;
	    os << "        synapse_tme+= synapse_timer.getElapsedTime();"<< ENDL;
	}
	if (model.lrnGroups > 0) {
	    if (model.timing) os << "        learning_timer.startTimer();" << ENDL;
	    os << "        learnSynapsesPostHost(t);" << ENDL;
	    if (model.timing) {
		os << "        learning_timer.stopTimer();" << ENDL;
		os << "        learning_tme+= learning_timer.getElapsedTime();" << ENDL;
	    }
	}
    }
    if (model.timing) os << "    neuron_timer.startTimer();" << ENDL;
    os << "    calcNeuronsCPU(t);" << ENDL;
    if (model.timing) {
	os << "    neuron_timer.stopTimer();" << ENDL;
	os << "    neuron_tme+= neuron_timer.getElapsedTime();" << ENDL;
    }
    os << "iT++;" << ENDL;
    os << "t= iT*DT;" << ENDL;
    os << "}" << ENDL;
    os.close();


    // ------------------------------------------------------------------------
    // finish up

#ifndef CPU_ONLY
    mos << "Global memory required for core model: " << mem/1e6 << " MB. " << ENDL;
    mos << deviceProp[theDev].totalGlobalMem << " for device " << theDev << ENDL;  
  
    if (memremsparse != 0) {
	int connEstim = int(memremsparse / (theSize(model.ftype) + sizeof(unsigned int)));
	mos << "Remaining mem is " << memremsparse/1e6 << " MB." << ENDL;
	mos << "You may run into memory problems on device" << theDev;
	mos << " if the total number of synapses is bigger than " << connEstim;
	mos << ", which roughly stands for " << int(connEstim/model.sumNeuronN[model.neuronGrpN - 1]);
	mos << " connections per neuron, without considering any other dynamic memory load." << ENDL;
    }
    else {
	if (0.5 * deviceProp[theDev].totalGlobalMem < mem) {
	    mos << "memory required for core model (" << mem/1e6;
	    mos << "MB) is more than 50% of global memory on the chosen device";
	    mos << "(" << deviceProp[theDev].totalGlobalMem/1e6 << "MB)." << ENDL;
	    mos << "Experience shows that this is UNLIKELY TO WORK ... " << ENDL;
	}
    }
#endif
}


#ifndef CPU_ONLY

//----------------------------------------------------------------------------
/*!
  \brief A function to generate the code that simulates the model on the GPU

  The function generates functions that will spawn kernel grids onto the GPU (but not the actual kernel code which is generated in "genNeuronKernel()" and "genSynpaseKernel()"). Generated functions include "copyGToDevice()", "copyGFromDevice()", "copyStateToDevice()", "copyStateFromDevice()", "copySpikesFromDevice()", "copySpikeNFromDevice()" and "stepTimeGPU()". The last mentioned function is the function that will initialize the execution on the GPU in the generated simulation engine. All other generated functions are "convenience functions" to handle data transfer from and to the GPU.
*/
//----------------------------------------------------------------------------

void genRunnerGPU(NNmodel &model, //!< Model description 
		  string &path, //!< path for code generation
		  ostream &mos //!< output stream for messages
    )
{
    string name;
    size_t size;
    unsigned int nt, st, pst;
    ofstream os;

//    mos << "entering GenRunnerGPU" << ENDL;
    name= path + toString("/") + model.name + toString("_CODE/runnerGPU.cc");
    os.open(name.c_str());
    writeHeader(os);

    // write doxygen comment
    os << "//-------------------------------------------------------------------------" << ENDL;
    os << "/*! \\file runnerGPU.cc" << ENDL << ENDL;
    os << "\\brief File generated from GeNN for the model " << model.name << " containing the host side code for a GPU simulator version." << ENDL;
    os << "*/" << ENDL;
    os << "//-------------------------------------------------------------------------" << ENDL << ENDL;

    os << ENDL;

    if ((deviceProp[theDev].major >= 2) || (deviceProp[theDev].minor >= 3)) {
	os << "__device__ double atomicAdd(double* address, double val)" << ENDL;
	os << "{" << ENDL;
	os << "    unsigned long long int* address_as_ull =" << ENDL;
	os << "                                          (unsigned long long int*)address;" << ENDL;
	os << "    unsigned long long int old = *address_as_ull, assumed;" << ENDL;
	os << "    do {" << ENDL;
	os << "        assumed = old;" << ENDL;
	os << "        old = atomicCAS(address_as_ull, assumed, " << ENDL;
	os << "                        __double_as_longlong(val + " << ENDL;
	os << "                        __longlong_as_double(assumed)));" << ENDL;
	os << "    } while (assumed != old);" << ENDL;
	os << "    return __longlong_as_double(old);" << ENDL;
	os << "}" << ENDL << ENDL;
    }

    if (deviceProp[theDev].major < 2) {
	os << "__device__ float atomicAddoldGPU(float* address, float val)" << ENDL;
	os << "{" << ENDL;
	os << "    int* address_as_ull =" << ENDL;
	os << "                                          (int*)address;" << ENDL;
	os << "    int old = *address_as_ull, assumed;" << ENDL;
	os << "    do {" << ENDL;
	os << "        assumed = old;" << ENDL;
	os << "        old = atomicCAS(address_as_ull, assumed, " << ENDL;
	os << "                        __float_as_int(val + " << ENDL;
	os << "                        __int_as_float(assumed)));" << ENDL;
	os << "    } while (assumed != old);" << ENDL;
	os << "    return __int_as_float(old);" << ENDL;
	os << "}" << ENDL << ENDL;
    }	

    os << "#include \"neuronKrnl.cc\"" << ENDL;
    if (model.synapseGrpN > 0) {
	os << "#include \"synapseKrnl.cc\"" << ENDL;
    }

    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying things to device" << ENDL << ENDL;

    for (int i = 0; i < model.neuronGrpN; i++) {
	nt = model.neuronType[i];

	// neuron state variables
	os << "void push" << model.neuronName[i] << "StateToDevice()" << ENDL;
	os << OB(1050);

	for (int k= 0, l= nModels[nt].varNames.size(); k < l; k++) {
	    if (nModels[nt].varTypes[k].find(tS("*")) == string::npos) { // only copy non-pointers. Pointers don't transport between GPU and CPU
		if (model.neuronVarNeedQueue[i][k]) {
		    size = model.neuronN[i] * model.neuronDelaySlots[i];
		}
		else {
		    size = model.neuronN[i];	
		}
		os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_" << nModels[nt].varNames[k] << model.neuronName[i];
		os << ", " << nModels[nt].varNames[k] << model.neuronName[i];
		os << ", " << size << " * sizeof(" << nModels[nt].varTypes[k] << "), cudaMemcpyHostToDevice));" << ENDL;
	    }
	}

	os << CB(1050);
	os << ENDL;	

	// neuron spike variables
	os << "void push" << model.neuronName[i] << "SpikesToDevice()" << ENDL;
	os << OB(1060);

	if (model.neuronNeedTrueSpk[i]) {
	    size = model.neuronDelaySlots[i];
	}
	else {
	    size = 1;
	}
	os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkCnt" << model.neuronName[i];
	os << ", glbSpkCnt" << model.neuronName[i];
	os << ", " << size << " * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;

	if (model.neuronNeedTrueSpk[i]) {
	    size = model.neuronN[i] * model.neuronDelaySlots[i];
	}
	else {
	    size = model.neuronN[i];
	}
	os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpk" << model.neuronName[i];
	os << ", glbSpk" << model.neuronName[i];
	os << ", " << size << " * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;

	if (model.neuronNeedSpkEvnt[i]) {
	  os << "push" << model.neuronName[i] << "SpikeEventsToDevice();" << ENDL;
	}

	if (model.neuronNeedSt[i]) {
	    size = model.neuronN[i] * model.neuronDelaySlots[i];
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_sT" << model.neuronName[i];
	    os << ", sT" << model.neuronName[i];
	    os << ", " << size << " * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	}

	os << CB(1060);
	os << ENDL;	
	
	// neuron spike variables
	os << "void push" << model.neuronName[i] << "SpikeEventsToDevice()" << ENDL;
	os << OB(1060);

	if (model.neuronNeedSpkEvnt[i]) {
	    size = model.neuronDelaySlots[i];
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkCntEvnt" << model.neuronName[i];
	    os << ", glbSpkCntEvnt" << model.neuronName[i];
	    os << ", " << size << " * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;

	    size = model.neuronN[i] * model.neuronDelaySlots[i];
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkEvnt" << model.neuronName[i];
	    os << ", glbSpkEvnt" << model.neuronName[i];
	    os << ", " << size << " * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	}

	os << CB(1060);
	os << ENDL;	

	// current neuron spike variables
	os << "void push" << model.neuronName[i] << "CurrentSpikesToDevice()" << ENDL;
	os << OB(1061);
	
	size = model.neuronN[i];
	if ((model.neuronNeedTrueSpk[i]) && (model.neuronDelaySlots[i] > 1)) {
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkCnt" << model.neuronName[i];
	  os << "+spkQuePtr" << model.neuronName[i] << ", glbSpkCnt" << model.neuronName[i];
	  os << "+spkQuePtr" << model.neuronName[i];
	  os << ", sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpk" << model.neuronName[i];
	  os << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << ")";
	  os << ", glbSpk" << model.neuronName[i];
	  os << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << ")";
	  os << ", " << "glbSpkCnt" << model.neuronName[i] << "[spkQuePtr" << model.neuronName[i] << "] * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	}
	else {
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkCnt" << model.neuronName[i];
	  os << ", glbSpkCnt" << model.neuronName[i]; 
	  os << ", sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpk" << model.neuronName[i];
	  os << ", glbSpk" << model.neuronName[i];
	  os << ", " << "glbSpkCnt" << model.neuronName[i] << "[0] * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	}
	
	os << CB(1061);
	os << ENDL;	
	
	// current neuron spike event variables
	os << "void push" << model.neuronName[i] << "CurrentSpikeEventsToDevice()" << ENDL;
	os << OB(1062);
	
	size = model.neuronN[i];
	if (model.neuronNeedSpkEvnt[i]) {
	  if (model.neuronDelaySlots[i] > 1) {
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkCntEvnt" << model.neuronName[i];
	    os << "+spkQuePtr" << model.neuronName[i] << ", glbSpkCntEvnt" << model.neuronName[i];
	    os << "+spkQuePtr" << model.neuronName[i];
	    os << ", sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkEvnt" << model.neuronName[i];
	    os << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << ")";
	    os << ", glbSpkEvnt" << model.neuronName[i];
	    os << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << ")";
	    os << ", " << "glbSpkCnt" << model.neuronName[i] << "[spkQuePtr" << model.neuronName[i] << "] * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	  }
	  else {
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkCntEvnt" << model.neuronName[i];
	    os << ", glbSpkCntEvnt" << model.neuronName[i]; 
	    os << ", sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_glbSpkEvnt" << model.neuronName[i];
	    os << ", glbSpkEvnt" << model.neuronName[i];
	    os << ", " << "glbSpkCntEvnt" << model.neuronName[i] << "[0] * sizeof(unsigned int), cudaMemcpyHostToDevice));" << ENDL;
	  }
	}
	
	os << CB(1062);
	os << ENDL;	
    }
    // synapse variables
    for (int i = 0; i < model.synapseGrpN; i++) {
        st = model.synapseType[i];
        pst = model.postSynapseType[i];
      
        os << "void push" << model.synapseName[i] << "StateToDevice()" << ENDL;
	os << OB(1100);
	
	if (model.synapseGType[i] == INDIVIDUALG) { // INDIVIDUALG
	    if (model.synapseConnType[i] != SPARSE) {
		os << "size_t size = " << model.neuronN[model.synapseSource[i]] * model.neuronN[model.synapseTarget[i]] << ";" << ENDL;
	    }
	    else {
		os << "size_t size = C" << model.synapseName[i] << ".connN;" << ENDL;
	    }
	    for (int k= 0, l= weightUpdateModels[st].varNames.size(); k < l; k++) {
		if (weightUpdateModels[st].varTypes[k].find(tS("*")) == string::npos) { // only copy non-pointers. Pointers don't transport between GPU and CPU
		    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_" << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		    os << ", " << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		    os << ", size * sizeof(" << weightUpdateModels[st].varTypes[k] << "), cudaMemcpyHostToDevice));" << ENDL; 
		}
	    }

	    for (int k= 0, l= postSynModels[pst].varNames.size(); k < l; k++) {
		if (postSynModels[pst].varTypes[k].find(tS("*")) == string::npos) { // only copy non-pointers. Pointers don't transport between GPU and CPU
		    size = model.neuronN[model.synapseTarget[i]];
		    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_" << postSynModels[pst].varNames[k] << model.synapseName[i];
		    os << ", " << postSynModels[pst].varNames[k] << model.synapseName[i];
		    os << ", " << size << " * sizeof(" << postSynModels[pst].varTypes[k] << "), cudaMemcpyHostToDevice));" << ENDL; 
		}
	    }
	}

	else if (model.synapseGType[i] == INDIVIDUALID) { // INDIVIDUALID
	    size = (model.neuronN[model.synapseSource[i]] * model.neuronN[model.synapseTarget[i]]) / 32 + 1;
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_gp" << model.synapseName[i];
	    os << ", gp" << model.synapseName[i];
	    os << ", " << size << " * sizeof(uint32_t), cudaMemcpyHostToDevice));" << ENDL;
	}

	size = model.neuronN[model.synapseTarget[i]];
	os << "CHECK_CUDA_ERRORS(cudaMemcpy(d_inSyn" << model.synapseName[i];
	os << ", inSyn" << model.synapseName[i];
	os << ", " << size << " * sizeof(" << model.ftype << "), cudaMemcpyHostToDevice));" << ENDL; 

	os << CB(1100);
	os << ENDL;
    }


    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying things from device" << ENDL << ENDL;

    for (int i = 0; i < model.neuronGrpN; i++) {
	nt = model.neuronType[i];

	// neuron state variables
	os << "void pull" << model.neuronName[i] << "StateFromDevice()" << ENDL;
	os << OB(1050);

	for (int k= 0, l= nModels[nt].varNames.size(); k < l; k++) {
	    if (nModels[nt].varTypes[k].find(tS("*")) == string::npos) { // only copy non-pointers. Pointers don't transport between GPU and CPU
		if (model.neuronVarNeedQueue[i][k]) {
		    size = model.neuronN[i] * model.neuronDelaySlots[i];
		}
		else {
		    size = model.neuronN[i];
		}
		os << "CHECK_CUDA_ERRORS(cudaMemcpy(" << nModels[nt].varNames[k] << model.neuronName[i];
		os << ", d_" << nModels[nt].varNames[k] << model.neuronName[i];
		os << ", " << size << " * sizeof(" << nModels[nt].varTypes[k] << "), cudaMemcpyDeviceToHost));" << ENDL;
	    }
	}

	os << CB(1050);
	os << ENDL;
	
	// spike event variables
	os << "void pull" << model.neuronName[i] << "SpikeEventsFromDevice()" << ENDL;
	os << OB(1061);
	
	size = model.neuronDelaySlots[i];
	if (model.neuronNeedSpkEvnt[i]) {
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkCntEvnt" << model.neuronName[i];
	  os << ", d_glbSpkCntEvnt" << model.neuronName[i];
	  os << ", " << size << " * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	  
	  size = model.neuronN[i] * model.neuronDelaySlots[i];
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkEvnt" << model.neuronName[i];
	  os << ", d_glbSpkEvnt" << model.neuronName[i];
	  os << ", " << size << " * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	}
	
	os << CB(1061);
	os << ENDL;

	// neuron spike variables (including spike events)
	os << "void pull" << model.neuronName[i] << "SpikesFromDevice()" << ENDL;
	os << OB(1060);

	if (model.neuronNeedTrueSpk[i]) {
	    size = model.neuronDelaySlots[i];
	}
	else {
	    size = 1;
	}
	os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkCnt" << model.neuronName[i];
	os << ", d_glbSpkCnt" << model.neuronName[i];
	os << ", " << size << " * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;

	if (model.neuronNeedTrueSpk[i]) {
	    size = model.neuronN[i] * model.neuronDelaySlots[i];
	}
	else {
	    size = model.neuronN[i];
	}
	os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpk" << model.neuronName[i];
	os << ", d_glbSpk" << model.neuronName[i];
	os << ", " << size << " * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;

	if (model.neuronNeedSpkEvnt[i]) {
	  os << "pull" << model.neuronName[i] << "SpikeEventsFromDevice();" << ENDL;
	}

	if (model.neuronNeedSt[i]) {
	    size = model.neuronN[i] * model.neuronDelaySlots[i];
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(sT" << model.neuronName[i];
	    os << ", d_sT" << model.neuronName[i];
	    os << ", " << size << " * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	}

	os << CB(1060);
	os << ENDL;

	os << "void pull" << model.neuronName[i] << "CurrentSpikesFromDevice()" << ENDL;
	os << OB(1061);

	size = model.neuronN[i] ;
	if ((model.neuronNeedTrueSpk[i]) && (model.neuronDelaySlots[i] > 1)) {
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkCnt" << model.neuronName[i];
	  os << "+spkQuePtr" << model.neuronName[i] << ", d_glbSpkCnt" << model.neuronName[i];
	  os << "+spkQuePtr" << model.neuronName[i];
	  os << ", sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;

	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpk" << model.neuronName[i];
	  os << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << ")";
	  os << ", d_glbSpk" << model.neuronName[i];
	  os << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << ")";
	  os << ", " << "glbSpkCnt" << model.neuronName[i] << "[spkQuePtr" << model.neuronName[i] << "] * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	}
	else {
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkCnt" << model.neuronName[i];
	  os << ", d_glbSpkCnt" << model.neuronName[i]; 
	  os << ", sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	  os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpk" << model.neuronName[i];
	  os << ", d_glbSpk" << model.neuronName[i];
	  os << ", " << "glbSpkCnt" << model.neuronName[i] << "[0] * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	}

	os << CB(1061);
	os << ENDL;	
	
	os << "void pull" << model.neuronName[i] << "CurrentSpikeEventsFromDevice()" << ENDL;
	os << OB(1062);

	size = model.neuronN[i] ;
	if (model.neuronNeedSpkEvnt[i]) {
	  if (model.neuronDelaySlots[i] > 1) {
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkCntEvnt" << model.neuronName[i];
	    os << "+spkQuePtr" << model.neuronName[i] << ", d_glbSpkCntEvnt" << model.neuronName[i];
	    os << "+spkQuePtr" << model.neuronName[i];
	    os << ", sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	    
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkEvnt" << model.neuronName[i];
	    os << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << ")";
	    os << ", d_glbSpkEvnt" << model.neuronName[i];
	    os << "+(spkQuePtr" << model.neuronName[i] << "*" << model.neuronN[i] << ")";
	    os << ", " << "glbSpkCntEvnt" << model.neuronName[i] << "[spkQuePtr" << model.neuronName[i] << "] * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	  }
	  else {
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkCntEvnt" << model.neuronName[i];
	    os << ", d_glbSpkCntEvnt" << model.neuronName[i]; 
	    os << ", sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkEvnt" << model.neuronName[i];
	    os << ", d_glbSpkEvnt" << model.neuronName[i];
	    os << ", " << "glbSpkCntEvnt" << model.neuronName[i] << "[0] * sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
	  }
	}

	os << CB(1062);
	os << ENDL;	
    }

    // synapse variables
    for (int i = 0; i < model.synapseGrpN; i++) {
	st = model.synapseType[i];
	pst = model.postSynapseType[i];
	
	os << "void pull" << model.synapseName[i] << "StateFromDevice()" << ENDL;
	os << OB(1100);

	if (model.synapseGType[i] == INDIVIDUALG) { // INDIVIDUALG
	    if (model.synapseConnType[i] != SPARSE) {
		os << "size_t size = " << model.neuronN[model.synapseSource[i]] * model.neuronN[model.synapseTarget[i]] << ";" << ENDL;
	    }
	    else {
		os << "size_t size = C" << model.synapseName[i] << ".connN;" << ENDL;
	    }
	    for (int k= 0, l= weightUpdateModels[st].varNames.size(); k < l; k++) {
		if (weightUpdateModels[st].varTypes[k].find(tS("*")) == string::npos) { // only copy non-pointers. Pointers don't transport between GPU and CPU
		    os << "CHECK_CUDA_ERRORS(cudaMemcpy(" << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		    os << ", d_"  << weightUpdateModels[st].varNames[k] << model.synapseName[i];
		    os << ", size * sizeof(" << weightUpdateModels[st].varTypes[k] << "), cudaMemcpyDeviceToHost));" << ENDL; 
		}
	    }

	    for (int k= 0, l= postSynModels[pst].varNames.size(); k < l; k++) {
		if (postSynModels[pst].varTypes[k].find(tS("*")) == string::npos) { // only copy non-pointers. Pointers don't transport between GPU and CPU
		    size = model.neuronN[model.synapseTarget[i]];
		    os << "CHECK_CUDA_ERRORS(cudaMemcpy(" << postSynModels[pst].varNames[k] << model.synapseName[i];
		    os << ", d_"  << postSynModels[pst].varNames[k] << model.synapseName[i];
		    os << ", " << size << " * sizeof(" << postSynModels[pst].varTypes[k] << "), cudaMemcpyDeviceToHost));" << ENDL; 
		}
	    }
	}

	else if (model.synapseGType[i] == INDIVIDUALID) { // INDIVIDUALID
	    size = (model.neuronN[model.synapseSource[i]] * model.neuronN[model.synapseTarget[i]]) / 32 + 1;
	    os << "CHECK_CUDA_ERRORS(cudaMemcpy(gp" << model.synapseName[i];
	    os << ", d_gp" << model.synapseName[i];
	    os << ", " << size << " * sizeof(uint32_t), cudaMemcpyDeviceToHost));" << ENDL;
	}

	size = model.neuronN[model.synapseTarget[i]];
	os << "CHECK_CUDA_ERRORS(cudaMemcpy(inSyn" << model.synapseName[i];
	os << ", d_inSyn" << model.synapseName[i];
	os << ", " << size << " * sizeof(" << model.ftype << "), cudaMemcpyDeviceToHost));" << ENDL; 

	os << CB(1100);
	os << ENDL;
    }


    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying values to device" << ENDL;
    
    os << "void copyStateToDevice()" << ENDL;
    os << OB(1110);

    for (int i = 0; i < model.neuronGrpN; i++) {
	os << "push" << model.neuronName[i] << "StateToDevice();" << ENDL;
	os << "push" << model.neuronName[i] << "SpikesToDevice();" << ENDL;
    }

    for (int i = 0; i < model.synapseGrpN; i++) {
	os << "push" << model.synapseName[i] << "StateToDevice();" << ENDL;
    }

    os << CB(1110);
    os << ENDL;
    
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying spikes to device" << ENDL;
    
    os << "void copySpikesToDevice()" << ENDL;
    os << OB(1111);
    for (int i = 0; i < model.neuronGrpN; i++) {
      os << "push" << model.neuronName[i] << "SpikesToDevice();" << ENDL;
    }
    os << CB(1111);
   
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying current spikes to device" << ENDL;
    
    os << "void copyCurrentSpikesToDevice()" << ENDL;
    os << OB(1112);
    for (int i = 0; i < model.neuronGrpN; i++) {
      os << "push" << model.neuronName[i] << "CurrentSpikesToDevice();" << ENDL;
    }
    os << CB(1112);
   
    
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying spike events to device" << ENDL;
    
    os << "void copySpikeEventsToDevice()" << ENDL;
    os << OB(1113);
    for (int i = 0; i < model.neuronGrpN; i++) {
      os << "push" << model.neuronName[i] << "SpikeEventsToDevice();" << ENDL;
    }
    os << CB(1113);
   
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying current spikes to device" << ENDL;
    
    os << "void copyCurrentSpikeEventsToDevice()" << ENDL;
    os << OB(1114);
    for (int i = 0; i < model.neuronGrpN; i++) {
      os << "push" << model.neuronName[i] << "CurrentSpikeEventsToDevice();" << ENDL;
    }
    os << CB(1114);

    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying values from device" << ENDL;
    
    os << "void copyStateFromDevice()" << ENDL;
    os << OB(1120);
    
    for (int i = 0; i < model.neuronGrpN; i++) {
	os << "pull" << model.neuronName[i] << "StateFromDevice();" << ENDL;
	os << "pull" << model.neuronName[i] << "SpikesFromDevice();" << ENDL;
    }

    for (int i = 0; i < model.synapseGrpN; i++) {
	os << "pull" << model.synapseName[i] << "StateFromDevice();" << ENDL;
    }
    
    os << CB(1120);
    os << ENDL;


    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying spikes from device" << ENDL;
    
    os << "void copySpikesFromDevice()" << ENDL;
    os << OB(1121) << ENDL;

    for (int i = 0; i < model.neuronGrpN; i++) {
      os << "pull" << model.neuronName[i] << "SpikesFromDevice();" << ENDL;
    }
    os << CB(1121) << ENDL;
    os << ENDL;
    
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying current spikes from device" << ENDL;
    
    os << "void copyCurrentSpikesFromDevice()" << ENDL;
    os << OB(1122) << ENDL;

    for (int i = 0; i < model.neuronGrpN; i++) {
      os << "pull" << model.neuronName[i] << "CurrentSpikesFromDevice();" << ENDL;
    }
    os << CB(1122) << ENDL;
    os << ENDL;
    

    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying spike numbers from device (note, only use when only interested"<< ENDL;
    os << "// in spike numbers; copySpikesFromDevice() already includes this)" << ENDL;

    os << "void copySpikeNFromDevice()" << ENDL;
    os << OB(1123) << ENDL;

    for (int i = 0; i < model.neuronGrpN; i++) {
	if ((model.neuronNeedTrueSpk[i]) && (model.neuronDelaySlots[i] > 1)) {
	    size = model.neuronDelaySlots[i];
	}
	else {
	    size = 1;
	}
	os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkCnt" << model.neuronName[i];
	os << ", d_glbSpkCnt" << model.neuronName[i] << ", " << size << "* sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
    }

    os << CB(1123) << ENDL;
    os << ENDL;

    
    os << "// ------------------------------------------------------------------------"<< ENDL;
    os << "// global copying spikeEvents from device" << ENDL;
    
    os << "void copySpikeEventsFromDevice()" << ENDL;
    os << OB(1124) << ENDL;

    for (int i = 0; i < model.neuronGrpN; i++) {
      os << "pull" << model.neuronName[i] << "SpikeEventsFromDevice();" << ENDL;
    }
    os << CB(1124) << ENDL;
    os << ENDL;
    
    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// copying current spikeEvents from device" << ENDL;
    
    os << "void copyCurrentSpikeEventsFromDevice()" << ENDL;
    os << OB(1125) << ENDL;

    for (int i = 0; i < model.neuronGrpN; i++) {
      os << "pull" << model.neuronName[i] << "CurrentSpikeEventsFromDevice();" << ENDL;
    }
    os << CB(1125) << ENDL;
    os << ENDL;

    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// global copying spike event numbers from device (note, only use when only interested" << ENDL;
    os << "// in spike numbers; copySpikeEventsFromDevice() already includes this)" << ENDL;
    
    os << "void copySpikeEventNFromDevice()" << ENDL;
    os << OB(1126) << ENDL;

    for (int i = 0; i < model.neuronGrpN; i++) {
      if (model.neuronNeedSpkEvnt[i]) {
	if (model.neuronDelaySlots[i] > 1) {
	  size = model.neuronDelaySlots[i];
	}
	else {
	  size = 1;
	}
	os << "CHECK_CUDA_ERRORS(cudaMemcpy(glbSpkCntEvnt" << model.neuronName[i];
	os << ", d_glbSpkCntEvnt" << model.neuronName[i] << ", " << size << "* sizeof(unsigned int), cudaMemcpyDeviceToHost));" << ENDL;
      }
    }

    os << CB(1126) << ENDL;
    os << ENDL;

    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// Raise an error if previous call convention is used for stepTimeGPU" << ENDL;           
    os << "template <class T>" << ENDL;
    os << "void stepTimeGPU(T arg1, ...)" << ENDL;
    os << OB(101) << ENDL;
    os << "gennError(\"Since GeNN 2.2 the call to stepTimeGPU has changed to not take any arguments other than an optional integer argument for flags. You appear to attempt to pass arguments. This is no longer supported. See the GeNN 2.2. release notes and the manual for examples how to pass data like, e.g., Poisson rates and direct inputs, that were previously handled through arguments.\");" << ENDL; 
    os << CB(101) << endl;

    os << "// ------------------------------------------------------------------------" << ENDL;
    os << "// the actual time stepping procedure" << ENDL;
    
    os << "void stepTimeGPU(unsigned int flags= GENN_FLAGS::COPY)" << ENDL;
    os << OB(1130) << ENDL;

    if (model.synapseGrpN > 0) { 
	unsigned int synapseGridSz = model.padSumSynapseKrnl[model.synapseGrpN - 1];   
	os << "//model.padSumSynapseTrgN[model.synapseGrpN - 1] is " << model.padSumSynapseKrnl[model.synapseGrpN - 1] << ENDL; 
	synapseGridSz = synapseGridSz / synapseBlkSz;
	os << "dim3 sThreads(" << synapseBlkSz << ", 1);" << ENDL;
	os << "dim3 sGrid(" << synapseGridSz << ", 1);" << ENDL;
	os << ENDL;
    }
    if (model.lrnGroups > 0) {
	unsigned int learnGridSz = model.padSumLearnN[model.lrnGroups - 1];
	learnGridSz = ceil((float) learnGridSz / learnBlkSz);
	os << "dim3 lThreads(" << learnBlkSz << ", 1);" << ENDL;
	os << "dim3 lGrid(" << learnGridSz << ", 1);" << ENDL;
	os << ENDL;
    }

    if (model.synDynGroups > 0) {
	unsigned int synDynGridSz = model.padSumSynDynN[model.synDynGroups - 1];
	synDynGridSz = ceil((float) synDynGridSz / synDynBlkSz);
	os << "dim3 sDThreads(" << synDynBlkSz << ", 1);" << ENDL;
	os << "dim3 sDGrid(" << synDynGridSz << ", 1);" << ENDL;
	os << ENDL;
    }
	
    unsigned int neuronGridSz = model.padSumNeuronN[model.neuronGrpN - 1];
    neuronGridSz = ceil((float) neuronGridSz / neuronBlkSz);
    os << "dim3 nThreads(" << neuronBlkSz << ", 1);" << ENDL;
    if (neuronGridSz < deviceProp[theDev].maxGridSize[1]) {
	os << "dim3 nGrid(" << neuronGridSz << ", 1);" << ENDL;
    }
    else {
	int sqGridSize = ceil((float) sqrt((float) neuronGridSz));
	os << "dim3 nGrid(" << sqGridSize << ","<< sqGridSize <<");" << ENDL;
    }
    os << ENDL;
    if (model.totalKernelParameterSize > 0) {
	os << "if (flags&GENN_FLAGS::COPY == 1)" << OB(33) << ENDL;
	os << "CHECK_CUDA_ERRORS(cudaMemcpy((void *) d_kernelPara, (void *) kernelPara, " << model.totalKernelParameterSize;
	os << ", cudaMemcpyHostToDevice));" << ENDL;
	os << CB(33) << ENDL;
    }
    if (model.synapseGrpN > 0) {
	if (model.synDynGroups > 0) {
	    if (model.timing) os << "cudaEventRecord(synDynStart);" << ENDL;
	    os << "calcSynapseDynamics <<< sDGrid, sDThreads >>> (t);" << ENDL;         
	    if (model.timing) os << "cudaEventRecord(synDynStop);" << ENDL;
	}
	if (model.timing) os << "cudaEventRecord(synapseStart);" << ENDL; 
	os << "calcSynapses <<< sGrid, sThreads >>> (t);" << ENDL;
	if (model.timing) os << "cudaEventRecord(synapseStop);" << ENDL;
	if (model.lrnGroups > 0) {
	    if (model.timing) os << "cudaEventRecord(learningStart);" << ENDL;
	    os << "learnSynapsesPost <<< lGrid, lThreads >>> (t);" << ENDL;         
	    if (model.timing) os << "cudaEventRecord(learningStop);" << ENDL;
	}
    }    
    for (int i= 0; i < model.neuronGrpN; i++) { 
	if (model.neuronDelaySlots[i] > 1) {
	    os << "spkQuePtr" << model.neuronName[i] << " = (spkQuePtr" << model.neuronName[i] << " + 1) % " << model.neuronDelaySlots[i] << ";" << ENDL;
	}
    }
    if (model.timing) os << "cudaEventRecord(neuronStart);" << ENDL;
    os << "calcNeurons <<< nGrid, nThreads >>> (t);" << ENDL;
    if (model.timing) {
	os << "cudaEventRecord(neuronStop);" << ENDL;
	os << "cudaEventSynchronize(neuronStop);" << ENDL;
	os << "float tmp;" << ENDL;
	if (model.synapseGrpN > 0) {
	    os << "cudaEventElapsedTime(&tmp, synapseStart, synapseStop);" << ENDL;
	    os << "synapse_tme+= tmp/1000.0;" << ENDL;
	}
	if (model.lrnGroups > 0) {
	    os << "cudaEventElapsedTime(&tmp, learningStart, learningStop);" << ENDL;
	    os << "learning_tme+= tmp/1000.0;" << ENDL;
	}
	if (model.synDynGroups > 0) {
	    os << "cudaEventElapsedTime(&tmp, synDynStart, synDynStop);" << ENDL;
	    os << "lsynDyn_tme+= tmp/1000.0;" << ENDL;
	}
	os << "cudaEventElapsedTime(&tmp, neuronStart, neuronStop);" << ENDL;
	os << "neuron_tme+= tmp/1000.0;" << ENDL;
    }
    os << "iT++;" << ENDL;
    os << "t= iT*DT;" << ENDL;
    os << CB(1130) << ENDL;
    os.close();
    //cout << "done with generating GPU runner" << ENDL;
}

#endif
