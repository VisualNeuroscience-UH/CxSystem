
/*--------------------------------------------------------------------------
   Author/Modifier: Thomas Nowotny
  
   Institute: Center for Computational Neuroscience and Robotics
              University of Sussex
	      Falmer, Brighton BN1 9QJ, UK 
  
   email to:  T.Nowotny@sussex.ac.uk
  
   initial version: 2010-02-07
   
   This file contains neuron model definitions.
  
--------------------------------------------------------------------------*/

#ifndef _UTILS_H_
#define _UTILS_H_ //!< macro for avoiding multiple inclusion during compilation


//--------------------------------------------------------------------------
/*! \file utils.h

\brief This file contains standard utility functions provide within the NVIDIA CUDA software development toolkit (SDK). The remainder of the file contains a function that defines the standard neuron models.
*/
//--------------------------------------------------------------------------

#include <cstdlib> // for exit() and EXIT_FAIL / EXIT_SUCCESS
#include <iostream>
#include <map>
#include <memory>
#include <fstream>
#include <cmath>
#include <vector>
#include <string>
using namespace std;

#ifndef CPU_ONLY
#include <cuda_runtime.h>
#endif

//--------------------------------------------------------------------------
/*! \brief Function called upon the detection of an error. Outputs an error message and then exits.
 */
//--------------------------------------------------------------------------

void gennError(string error)
{
  cerr << "GeNN error: " << error << endl;
  exit(EXIT_FAILURE);
}

//--------------------------------------------------------------------------
/*! \brief Function called upon the detection of an error. Outputs an error message and then exits.
 */
//--------------------------------------------------------------------------

void gennError(const char *error)
{
  cerr << "GeNN error: " << error << endl;
  exit(EXIT_FAILURE);
}


#include "modelSpec.h"
#include "toString.h"


#ifndef CPU_ONLY
//--------------------------------------------------------------------------
/*! \brief Macro for wrapping cuda runtime function calls and catching any errors that may be thrown.
 */
//--------------------------------------------------------------------------

#define CHECK_CUDA_ERRORS(call)					           \
{								      	   \
  cudaError_t error = call;						   \
  if (error != cudaSuccess)						   \
  {                                                                        \
    fprintf(stderr, "%s: %i: cuda error %i: %s\n",			   \
	    __FILE__, __LINE__, (int)error, cudaGetErrorString(error));	   \
    exit(EXIT_FAILURE);						           \
  }									   \
}
#endif


//--------------------------------------------------------------------------
/*! \brief Function to write the comment header denoting file authorship and contact details into the generated code.
 */
//--------------------------------------------------------------------------

void writeHeader(ostream &os) 
{
  string s;
  ifstream is("../src/header.src");
  getline(is, s);
  while (is.good()) {
    os << s << endl;
    getline(is, s);
  }
  os << endl;
}


//--------------------------------------------------------------------------
//! \brief Tool for determining the size of variable types on the current architecture
//--------------------------------------------------------------------------

unsigned int theSize(string type) 
{
  unsigned int size = 0;
  if (type.find(tS("*")) != string::npos) size= sizeof(char *); // it's a pointer ... any pointer should have the same size
  if (type == "char") size = sizeof(char);
  //  if (type == "char16_t") size = sizeof(char16_t);
  //  if (type == "char32_t") size = sizeof(char32_t);
  if (type == "wchar_t") size = sizeof(wchar_t);
  if (type == "signed char") size = sizeof(signed char);
  if (type == "short") size = sizeof(short);
  if (type == "signed short") size = sizeof(signed short);
  if (type == "short int") size = sizeof(short int);
  if (type == "signed short int") size = sizeof(signed short int);
  if (type == "int") size = sizeof(int);
  if (type == "signed int") size = sizeof(signed int);
  if (type == "long") size = sizeof(long);
  if (type == "signed long") size = sizeof(signed long);
  if (type == "long int") size = sizeof(long int);
  if (type == "signed long int") size = sizeof(signed long int);
  if (type == "long long") size = sizeof(long long);
  if (type == "signed long long") size = sizeof(signed long long);
  if (type == "long long int") size = sizeof(long long int);
  if (type == "signed long long int") size = sizeof(signed long long int);
  if (type == "unsigned char") size = sizeof(unsigned char);
  if (type == "unsigned short") size = sizeof(unsigned short);
  if (type == "unsigned short int") size = sizeof(unsigned short int);
  if (type == "unsigned") size = sizeof(unsigned);
  if (type == "unsigned int") size = sizeof(unsigned int);
  if (type == "unsigned long") size = sizeof(unsigned long);
  if (type == "unsigned long int") size = sizeof(unsigned long int);
  if (type == "unsigned long long") size = sizeof(unsigned long long);
  if (type == "unsigned long long int") size = sizeof(unsigned long long int);
  if (type == "float") size = sizeof(float);
  if (type == "double") size = sizeof(double);
  if (type == "long double") size = sizeof(long double);
  if (type == "bool") size = sizeof(bool);
  if (type == "intmax_t") size= sizeof(intmax_t);
  if (type == "uintmax_t") size= sizeof(uintmax_t);
  if (type == "int8_t") size= sizeof(int8_t);
  if (type == "uint8_t") size= sizeof(uint8_t);
  if (type == "int16_t") size= sizeof(int16_t);	
  if (type == "uint16_t") size= sizeof(uint16_t);
  if (type == "int32_t") size= sizeof(int32_t);
  if (type == "uint32_t") size= sizeof(uint32_t);
  if (type == "int64_t") size= sizeof(int64_t);
  if (type == "uint64_t") size= sizeof(uint64_t);
  if (type == "int_least8_t") size= sizeof(int_least8_t);
  if (type == "uint_least8_t") size= sizeof(uint_least8_t);
  if (type == "int_least16_t") size= sizeof(int_least16_t);
  if (type == "uint_least16_t") size= sizeof(uint_least16_t);
  if (type == "int_least32_t") size= sizeof(int_least32_t);
  if (type == "uint_least32_t") size= sizeof(uint_least32_t);
  if (type == "int_least64_t") size= sizeof(int_least64_t);
  if (type == "uint_least64_t") size= sizeof(uint_least64_t);
  if (type == "int_fast8_t") size= sizeof(int_fast8_t);
  if (type == "uint_fast8_t") size= sizeof(uint_fast8_t);
  if (type == "int_fast16_t") size= sizeof(int_fast16_t);
  if (type == "uint_fast16_t") size= sizeof(uint_fast16_t);
  if (type == "int_fast32_t") size= sizeof(int_fast32_t);
  if (type == "uint_fast32_t") size= sizeof(uint_fast32_t);
  if (type == "int_fast64_t") size= sizeof(int_fast64_t);
  if (type == "uint_fast64_t") size= sizeof(uint_fast64_t);
  return size;
}

//--------------------------------------------------------------------------
//! \brief Class defining the dependent parameters of teh Rulkov map neuron.
//--------------------------------------------------------------------------


class rulkovdp : public dpclass
{
public:
	double calculateDerivedParameter(int index, vector <double> pars, double dt = 1.0) {
		switch (index) {
			case 0:
			return ip0(pars);
			case 1:
			return ip1(pars);
			case 2:
			return ip2(pars);
		}
		return -1;
	}

	double ip0(vector<double> pars) {
		return pars[0]*pars[0]*pars[1];
	}
	double ip1(vector<double> pars) {
		return pars[0]*pars[2];
	}
	double ip2(vector<double> pars) {
		return pars[0]*pars[1]+pars[0]*pars[2];
	}
};

//--------------------------------------------------------------------------
//! \brief Class defining the dependent parameter for exponential decay.
//--------------------------------------------------------------------------

class expDecayDp : public dpclass
{
public:
	double calculateDerivedParameter(int index, vector <double> pars, double dt = 1.0) {
		switch (index) {
			case 0:
			return expDecay(pars, dt);
		}
		return -1;
	}

	double expDecay(vector<double> pars, double dt) {
		return exp(-dt/pars[0]);
	}
};

vector<neuronModel> nModels; //!< Global C++ vector containing all neuron model descriptions

//--------------------------------------------------------------------------
/*! \brief Function that defines standard neuron models

The neuron models are defined and added to the C++ vector nModels that is holding all neuron model descriptions. User defined neuron models can be appended to this vector later in (a) separate function(s).
*/

void prepareStandardModels()
{
  neuronModel n;
  //Rulkov neurons
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("preV"));
  n.varTypes.push_back(tS("scalar"));
  n.pNames.push_back(tS("Vspike"));
  n.pNames.push_back(tS("alpha"));
  n.pNames.push_back(tS("y"));
  n.pNames.push_back(tS("beta"));
  n.dpNames.push_back(tS("ip0"));
  n.dpNames.push_back(tS("ip1"));
  n.dpNames.push_back(tS("ip2"));
  n.simCode= tS("    if ($(V) <= 0) {\n\
      $(preV)= $(V);\n\
      $(V)= $(ip0)/(($(Vspike)) - $(V) - ($(beta))*$(Isyn)) +($(ip1));\n\
    }\n\
    else {\n\
      if (($(V) < $(ip2)) && ($(preV) <= 0)) {\n\
        $(preV)= $(V);\n\
        $(V)= $(ip2);\n\
      }\n\
      else {\n\
        $(preV)= $(V);\n\
        $(V)= -($(Vspike));\n\
      }\n\
    }\n");

  n.thresholdConditionCode = tS("$(V) >= $(ip2)");

  n.dps = new rulkovdp();

  nModels.push_back(n);
  MAPNEURON= nModels.size()-1;

  // Poisson neurons
  n.varNames.clear();
  n.varTypes.clear();
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("seed"));
  n.varTypes.push_back(tS("uint64_t"));
  n.varNames.push_back(tS("spikeTime"));
  n.varTypes.push_back(tS("scalar"));
  n.pNames.clear();
  n.pNames.push_back(tS("therate"));
  n.pNames.push_back(tS("trefract"));
  n.pNames.push_back(tS("Vspike"));
  n.pNames.push_back(tS("Vrest"));
  n.dpNames.clear();
  n.extraGlobalNeuronKernelParameters.push_back(tS("rates"));
  n.extraGlobalNeuronKernelParameterTypes.push_back(tS("uint64_t *"));
  n.extraGlobalNeuronKernelParameters.push_back(tS("offset"));
  n.extraGlobalNeuronKernelParameterTypes.push_back(tS("unsigned int"));
  n.simCode= tS("    uint64_t theRnd;\n\
    if ($(V) > $(Vrest)) {\n\
      $(V)= $(Vrest);\n\
    }\n\
    else {\n\
      if ($(t) - $(spikeTime) > ($(trefract))) {\n\
        MYRAND($(seed),theRnd);\n\
        if (theRnd < *($(rates)+$(offset)+$(id))) {\n			\
          $(V)= $(Vspike);\n\
          $(spikeTime)= $(t);\n\
        }\n\
      }\n\
    }\n");

  n.thresholdConditionCode = tS("$(V) >= $(Vspike)");
  n.dps= NULL;
  nModels.push_back(n);
  POISSONNEURON= nModels.size()-1;

// Traub and Miles HH neurons TRAUBMILES_FAST - Original fast implementation, using 25 inner iterations. There are singularities in this model, which can be  easily hit in float precision.  
  n.varNames.clear();
  n.varTypes.clear();
  n.extraGlobalNeuronKernelParameters.clear();
  n.extraGlobalNeuronKernelParameterTypes.clear();
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("m"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("h"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("n"));
  n.varTypes.push_back(tS("scalar"));
  n.pNames.clear();
  n.pNames.push_back(tS("gNa"));
  n.pNames.push_back(tS("ENa"));
  n.pNames.push_back(tS("gK"));
  n.pNames.push_back(tS("EK"));
  n.pNames.push_back(tS("gl"));
  n.pNames.push_back(tS("El"));
  n.pNames.push_back(tS("C"));
  n.dpNames.clear();
  n.simCode= tS("   scalar Imem;\n\
    unsigned int mt;\n\
    scalar mdt= DT/25.0;\n\
    for (mt=0; mt < 25; mt++) {\n\
      Imem= -($(m)*$(m)*$(m)*$(h)*$(gNa)*($(V)-($(ENa)))+\n\
              $(n)*$(n)*$(n)*$(n)*$(gK)*($(V)-($(EK)))+\n\
              $(gl)*($(V)-($(El)))-$(Isyn));\n\
      scalar _a= 0.32*(-52.0-$(V))/(exp((-52.0-$(V))/4.0)-1.0);\n\
      scalar _b= 0.28*($(V)+25.0)/(exp(($(V)+25.0)/5.0)-1.0);\n\
      $(m)+= (_a*(1.0-$(m))-_b*$(m))*mdt;\n\
      _a= 0.128*exp((-48.0-$(V))/18.0);\n\
      _b= 4.0 / (exp((-25.0-$(V))/5.0)+1.0);\n\
      $(h)+= (_a*(1.0-$(h))-_b*$(h))*mdt;\n\
      _a= 0.032*(-50.0-$(V))/(exp((-50.0-$(V))/5.0)-1.0);\n\
      _b= 0.5*exp((-55.0-$(V))/40.0);\n\
      $(n)+= (_a*(1.0-$(n))-_b*$(n))*mdt;\n\
      $(V)+= Imem/$(C)*mdt;\n\
    }\n");

  n.thresholdConditionCode = tS("$(V) > 0.0");//TODO check this, to get better value
  n.dps= NULL;
  nModels.push_back(n);
  TRAUBMILES_FAST= nModels.size()-1;

// Traub and Miles HH neurons TRAUBMILES_ALTERNATIVE - Using a workaround to avoid singularity: adding the munimum numerical value of the floating point precision used. 
  n.varNames.clear();
  n.varTypes.clear();
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("m"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("h"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("n"));
  n.varTypes.push_back(tS("scalar"));
  n.pNames.clear();
  n.pNames.push_back(tS("gNa"));
  n.pNames.push_back(tS("ENa"));
  n.pNames.push_back(tS("gK"));
  n.pNames.push_back(tS("EK"));
  n.pNames.push_back(tS("gl"));
  n.pNames.push_back(tS("El"));
  n.pNames.push_back(tS("C"));
  n.dpNames.clear();
  n.simCode= tS("   scalar Imem;\n\
    unsigned int mt;\n\
    scalar mdt= DT/25.0;\n\
    for (mt=0; mt < 25; mt++) {\n\
      Imem= -($(m)*$(m)*$(m)*$(h)*$(gNa)*($(V)-($(ENa)))+\n\
              $(n)*$(n)*$(n)*$(n)*$(gK)*($(V)-($(EK)))+\n\
              $(gl)*($(V)-($(El)))-$(Isyn));\n\
      scalar volatile _tmp= abs(exp((-52.0-$(V))/4.0)-1.0);\n\
      scalar _a= 0.32*abs(-52.0-$(V))/(_tmp+SCALAR_MIN);\n\
      _tmp= abs(exp(($(V)+25.0)/5.0)-1.0);\n\
      scalar _b= 0.28*abs($(V)+25.0)/(_tmp+SCALAR_MIN);\n\
      $(m)+= (_a*(1.0-$(m))-_b*$(m))*mdt;\n\
      _a= 0.128*exp((-48.0-$(V))/18.0);\n\
      _b= 4.0 / (exp((-25.0-$(V))/5.0)+1.0);\n\
      $(h)+= (_a*(1.0-$(h))-_b*$(h))*mdt;\n\
      _tmp= abs(exp((-50.0-$(V))/5.0)-1.0);\n\
      _a= 0.032*abs(-50.0-$(V))/(_tmp+SCALAR_MIN); \n\
      _b= 0.5*exp((-55.0-$(V))/40.0);\n\
      $(n)+= (_a*(1.0-$(n))-_b*$(n))*mdt;\n\
      $(V)+= Imem/$(C)*mdt;\n\
    }\n");

  n.thresholdConditionCode = tS("$(V) > 0");//TODO check this, to get better value
  n.dps= NULL;
  nModels.push_back(n);
  TRAUBMILES_ALTERNATIVE= nModels.size()-1;

// Traub and Miles HH neurons TRAUBMILES_SAFE - Using IF statements to check if a value that a singularity would be hit. If so, value calculated by L'Hospital rule is used. TRAUBMILES method points to this model.
  n.varNames.clear();
  n.varTypes.clear();
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("m"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("h"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("n"));
  n.varTypes.push_back(tS("scalar"));
  n.pNames.clear();
  n.pNames.push_back(tS("gNa"));
  n.pNames.push_back(tS("ENa"));
  n.pNames.push_back(tS("gK"));
  n.pNames.push_back(tS("EK"));
  n.pNames.push_back(tS("gl"));
  n.pNames.push_back(tS("El"));
  n.pNames.push_back(tS("C"));
  n.dpNames.clear();
  n.simCode= tS("   scalar Imem;\n\
    unsigned int mt;\n\
    scalar mdt= DT/25.0;\n\
    for (mt=0; mt < 25; mt++) {\n\
      Imem= -($(m)*$(m)*$(m)*$(h)*$(gNa)*($(V)-($(ENa)))+\n\
              $(n)*$(n)*$(n)*$(n)*$(gK)*($(V)-($(EK)))+\n\
              $(gl)*($(V)-($(El)))-$(Isyn));\n\
      scalar _a;\n\
      if (lV == -52.0) _a= 1.28;\n\
      else _a= 0.32*(-52.0-$(V))/(exp((-52.0-$(V))/4.0)-1.0);\n\
      scalar _b;\n\
      if (lV == -25.0) _b= 1.4;\n\
      else _b= 0.28*($(V)+25.0)/(exp(($(V)+25.0)/5.0)-1.0);\n\
      $(m)+= (_a*(1.0-$(m))-_b*$(m))*mdt;\n\
      _a= 0.128*exp((-48.0-$(V))/18.0);\n\
      _b= 4.0 / (exp((-25.0-$(V))/5.0)+1.0);\n\
      $(h)+= (_a*(1.0-$(h))-_b*$(h))*mdt;\n\
      if (lV == -50.0) _a= 0.16;\n\
      else _a= 0.032*(-50.0-$(V))/(exp((-50.0-$(V))/5.0)-1.0);\n\
      _b= 0.5*exp((-55.0-$(V))/40.0);\n\
      $(n)+= (_a*(1.0-$(n))-_b*$(n))*mdt;\n\
      $(V)+= Imem/$(C)*mdt;\n\
    }\n");

  n.thresholdConditionCode = tS("$(V) > 0.0");//TODO check this, to get better value.
  n.dps= NULL;
  nModels.push_back(n);
  TRAUBMILES_SAFE= nModels.size()-1;
  TRAUBMILES= TRAUBMILES_SAFE;

// Traub and Miles HH neurons TRAUBMILES_PSTEP - same as TRAUBMILES_SAFE but the number of inner loops can be set as a parameter.
  n.varNames.clear();
  n.varTypes.clear();
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("m"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("h"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("n"));
  n.varTypes.push_back(tS("scalar"));
  n.pNames.clear();
  n.pNames.push_back(tS("gNa"));
  n.pNames.push_back(tS("ENa"));
  n.pNames.push_back(tS("gK"));
  n.pNames.push_back(tS("EK"));
  n.pNames.push_back(tS("gl"));
  n.pNames.push_back(tS("El"));
  n.pNames.push_back(tS("C"));
  n.pNames.push_back(tS("ntimes"));
  n.dpNames.clear();
  n.simCode= tS("   scalar Imem;\n\
    unsigned int mt;\n\
    scalar mdt= DT/scalar($(ntimes));\n\
    for (mt=0; mt < $(ntimes); mt++) {\n\
      Imem= -($(m)*$(m)*$(m)*$(h)*$(gNa)*($(V)-($(ENa)))+\n\
              $(n)*$(n)*$(n)*$(n)*$(gK)*($(V)-($(EK)))+\n\
              $(gl)*($(V)-($(El)))-$(Isyn));\n\
      scalar _a;\n\
      if (lV == -52.0) _a= 1.28;\n\
      else _a= 0.32*(-52.0-$(V))/(exp((-52.0-$(V))/4.0)-1.0);\n\
      scalar _b;\n\
      if (lV == -25.0) _b= 1.4;\n\
      else _b= 0.28*($(V)+25.0)/(exp(($(V)+25.0)/5.0)-1.0);\n\
      $(m)+= (_a*(1.0-$(m))-_b*$(m))*mdt;\n\
      _a= 0.128*exp((-48.0-$(V))/18.0);\n\
      _b= 4.0 / (exp((-25.0-$(V))/5.0)+1.0);\n\
      $(h)+= (_a*(1.0-$(h))-_b*$(h))*mdt;\n\
      if (lV == -50.0) _a= 0.16;\n\
      else _a= 0.032*(-50.0-$(V))/(exp((-50.0-$(V))/5.0)-1.0);\n\
      _b= 0.5*exp((-55.0-$(V))/40.0);\n\
      $(n)+= (_a*(1.0-$(n))-_b*$(n))*mdt;\n\
      $(V)+= Imem/$(C)*mdt;\n\
    }\n");

  n.thresholdConditionCode = tS("$(V) > 0.0");//TODO check this, to get better value
  n.dps= NULL;
  nModels.push_back(n);
  TRAUBMILES_PSTEP= nModels.size()-1;

 //Izhikevich neurons
  n.varNames.clear();
  n.varTypes.clear();
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("scalar"));  
  n.varNames.push_back(tS("U"));
  n.varTypes.push_back(tS("scalar"));
  n.pNames.clear();
  //n.pNames.push_back(tS("Vspike"));
  n.pNames.push_back(tS("a")); // time scale of U
  n.pNames.push_back(tS("b")); // sensitivity of U
  n.pNames.push_back(tS("c")); // after-spike reset value of V
  n.pNames.push_back(tS("d")); // after-spike reset value of U
  n.dpNames.clear(); 
  //TODO: replace the resetting in the following with BRIAN-like threshold and resetting 
  n.simCode= tS("    if ($(V) >= 30.0){\n\
      $(V)=$(c);\n\
		  $(U)+=$(d);\n\
    } \n\
    $(V)+=0.5*(0.04*$(V)*$(V)+5.0*$(V)+140.0-$(U)+$(Isyn))*DT; //at two times for numerical stability\n\
    $(V)+=0.5*(0.04*$(V)*$(V)+5.0*$(V)+140.0-$(U)+$(Isyn))*DT;\n\
    $(U)+=$(a)*($(b)*$(V)-$(U))*DT;\n\
   //if ($(V) > 30.0){   //keep this only for visualisation -- not really necessaary otherwise \n	\
   //  $(V)=30.0; \n\
   //}\n\
   ");
    
  n.thresholdConditionCode = tS("$(V) >= 29.99");

 /*  n.resetCode=tS("//reset code is here\n ");
      $(V)=$(c);\n\
		  $(U)+=$(d);\n\
  */
  nModels.push_back(n);
  IZHIKEVICH= nModels.size()-1;

//Izhikevich neurons with variable parameters
  n.varNames.clear();
  n.varTypes.clear();
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("scalar"));  
  n.varNames.push_back(tS("U"));
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("a")); // time scale of U
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("b")); // sensitivity of U
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("c")); // after-spike reset value of V
  n.varTypes.push_back(tS("scalar"));
  n.varNames.push_back(tS("d")); // after-spike reset value of U
  n.varTypes.push_back(tS("scalar"));
  n.pNames.clear();
  n.dpNames.clear(); 
  //TODO: replace the resetting in the following with BRIAN-like threshold and resetting 
  n.simCode= tS("    if ($(V) >= 30.0){\n\
      $(V)=$(c);\n\
		  $(U)+=$(d);\n\
    } \n\
    $(V)+=0.5*(0.04*$(V)*$(V)+5.0*$(V)+140.0-$(U)+$(Isyn))*DT; //at two times for numerical stability\n\
    $(V)+=0.5*(0.04*$(V)*$(V)+5.0*$(V)+140.0-$(U)+$(Isyn))*DT;\n\
    $(U)+=$(a)*($(b)*$(V)-$(U))*DT;\n\
    //if ($(V) > 30.0){      //keep this only for visualisation -- not really necessaary otherwise \n\
    //  $(V)=30.0; \n\
    //}\n\
    ");
  n.thresholdConditionCode = tS("$(V) > 29.99");
  n.dps= NULL;
  nModels.push_back(n);
  IZHIKEVICH_V= nModels.size()-1;
  
  //Spike Source ("empty" neuron that does nothing - spikes need to be copied in explicitly from host code)
  n.varNames.clear();
  n.varTypes.clear();
  n.pNames.clear();
  n.dpNames.clear(); 
  n.simCode= tS("");
  n.thresholdConditionCode = tS("0");
  n.dps= NULL;
  nModels.push_back(n);
  SPIKESOURCE= nModels.size()-1;

  #include "extra_neurons.h"

}




vector<postSynModel> postSynModels; //!< Global C++ vector containing all post-synaptic update model descriptions

//--------------------------------------------------------------------------
/*! \brief Function that prepares the standard post-synaptic models, including their variables, parameters, dependent parameters and code strings.
 */
//--------------------------------------------------------------------------

void preparePostSynModels(){
  postSynModel ps;
  
  //0: Exponential decay
  ps.varNames.clear();
  ps.varTypes.clear();
  
  ps.pNames.clear();
  ps.dpNames.clear(); 
  
  ps.pNames.push_back(tS("tau")); 
  ps.pNames.push_back(tS("E"));  
  ps.dpNames.push_back(tS("expDecay"));
  
  ps.postSynDecay=tS(" 	 $(inSyn)*=$(expDecay);\n");
  ps.postSyntoCurrent=tS("$(inSyn)*($(E)-$(V))");
  
  ps.dps = new expDecayDp;
  
  postSynModels.push_back(ps);
  EXPDECAY= postSynModels.size()-1;
  
  //1: IZHIKEVICH MODEL (NO POSTSYN RULE)
  ps.varNames.clear();
  ps.varTypes.clear();
  
  ps.pNames.clear();
  ps.dpNames.clear(); 
  
  ps.postSynDecay=tS("");
  ps.postSyntoCurrent=tS("$(inSyn); $(inSyn)= 0");
  
  postSynModels.push_back(ps);
  IZHIKEVICH_PS= postSynModels.size()-1;
 
  #include "extra_postsynapses.h"
}


//--------------------------------------------------------------------------
/*! This class defines derived parameters for the learn1synapse standard 
    weightupdate model 
*/
//--------------------------------------------------------------------------

class pwSTDP : public dpclass  //!TODO This class definition may be code-generated in a future release
{
public:
    double calculateDerivedParameter(int index, vector<double> pars, 
				    double dt)
    {		
	switch (index) {
	case 0:
	    return lim0(pars, dt);
	case 1:
	    return lim1(pars, dt);
	case 2:
	    return slope0(pars, dt);
	case 3:
	    return slope1(pars, dt);
	case 4:
	    return off0(pars, dt);
	case 5:
	    return off1(pars, dt);
	case 6:
	    return off2(pars, dt);
	}
	return -1;
    }
    
    double lim0(vector<double> pars, double dt) {
	return (1/pars[4] + 1/pars[1]) * pars[0] / (2/pars[1]);
    }
    double lim1(vector<double> pars, double dt) {
	return -((1/pars[3] + 1/pars[1]) * pars[0] / (2/pars[1]));
    }
    double slope0(vector<double> pars, double dt) {
	return -2*pars[5]/(pars[1]*pars[0]); 
    }
    double slope1(vector<double> pars, double dt) {
	return -1*slope0(pars, dt);
    }
    double off0(vector<double> pars, double dt) {
	return pars[5]/pars[4];
    }
    double off1(vector<double> pars, double dt) {
	return pars[5]/pars[1];
    }
    double off2(vector<double> pars, double dt) {
	return pars[5]/pars[3];
    }
};


vector<weightUpdateModel> weightUpdateModels; //!< Global C++ vector containing all weightupdate model descriptions

//--------------------------------------------------------------------------
/*! \brief Function that prepares the standard (pre) synaptic models, including their variables, parameters, dependent parameters and code strings.
 */
//--------------------------------------------------------------------------

void prepareWeightUpdateModels()
{
  weightUpdateModel wuN, wuG, wuL;
    
    // NSYNAPSE weightupdate model: "normal" pulse coupling synapse
    wuN.varNames.clear();
    wuN.varTypes.clear();
    wuN.varNames.push_back(tS("g"));
    wuN.varTypes.push_back(tS("scalar"));
    wuN.pNames.clear();
    wuN.dpNames.clear();
    // code for presynaptic spike:
    wuN.simCode = tS("  $(addtoinSyn) = $(g);\n\
  $(updatelinsyn);\n");
    weightUpdateModels.push_back(wuN);
    NSYNAPSE= weightUpdateModels.size()-1;
    
    // NGRADSYNAPSE weightupdate model: "normal" graded synapse
    wuG.varNames.clear();
    wuG.varTypes.clear();
    wuG.varNames.push_back(tS("g"));
    wuG.varTypes.push_back(tS("scalar"));
    wuG.pNames.clear();
    wuG.pNames.push_back(tS("Epre")); 
    wuG.pNames.push_back(tS("Vslope")); 
    wuG.dpNames.clear();
    // code for presynaptic spike event 
    wuG.simCodeEvnt = tS("$(addtoinSyn) = $(g) * tanh(($(V_pre) - $(Epre)) / $(Vslope))* DT;\n\
    if ($(addtoinSyn) < 0) $(addtoinSyn) = 0.0;\n\
    $(updatelinsyn);\n");
    // definition of presynaptic spike event 
    wuG.evntThreshold = tS("$(V_pre) > $(Epre)");
    weightUpdateModels.push_back(wuG);
    NGRADSYNAPSE= weightUpdateModels.size()-1; 

    // LEARN1SYNAPSE weightupdate model: "normal" synapse with a type of STDP
    wuL.varNames.clear();
    wuL.varTypes.clear();
    wuL.varNames.push_back(tS("g")); 
    wuL.varTypes.push_back(tS("scalar"));
    wuL.varNames.push_back(tS("gRaw")); 
    wuL.varTypes.push_back(tS("scalar"));
    wuL.pNames.clear();
    wuL.pNames.push_back(tS("tLrn"));  //0
    wuL.pNames.push_back(tS("tChng")); //1
    wuL.pNames.push_back(tS("tDecay")); //2
    wuL.pNames.push_back(tS("tPunish10")); //3
    wuL.pNames.push_back(tS("tPunish01")); //4
    wuL.pNames.push_back(tS("gMax")); //5
    wuL.pNames.push_back(tS("gMid")); //6
    wuL.pNames.push_back(tS("gSlope")); //7
    wuL.pNames.push_back(tS("tauShift")); //8
    wuL.pNames.push_back(tS("gSyn0")); //9
    wuL.dpNames.clear(); 
    wuL.dpNames.push_back(tS("lim0"));
    wuL.dpNames.push_back(tS("lim1"));
    wuL.dpNames.push_back(tS("slope0"));
    wuL.dpNames.push_back(tS("slope1"));
    wuL.dpNames.push_back(tS("off0"));
    wuL.dpNames.push_back(tS("off1"));
    wuL.dpNames.push_back(tS("off2"));
    // code for presynaptic spike
    wuL.simCode = tS("$(addtoinSyn) = $(g);\n\
  $(updatelinsyn); \n				\
  scalar dt = $(sT_post) - $(t) - ($(tauShift)); \n	\
  scalar dg = 0;\n				\
  if (dt > $(lim0))  \n				\
      dg = -($(off0)) ; \n			\
  else if (dt > 0)  \n			\
      dg = $(slope0) * dt + ($(off1)); \n\
  else if (dt > $(lim1))  \n			\
      dg = $(slope1) * dt + ($(off1)); \n\
  else dg = - ($(off2)) ; \n\
  $(gRaw) += dg; \n\
  $(g)=$(gMax)/2 *(tanh($(gSlope)*($(gRaw) - ($(gMid))))+1); \n");   
  wuL.dps = new pwSTDP;
  // code for post-synaptic spike 
  wuL.simLearnPost = tS("scalar dt = $(t) - ($(sT_pre)) - ($(tauShift)); \n\
  scalar dg =0; \n\
  if (dt > $(lim0))  \n\
      dg = -($(off0)) ; \n \
  else if (dt > 0)  \n\
      dg = $(slope0) * dt + ($(off1)); \n\
  else if (dt > $(lim1))  \n\
      dg = $(slope1) * dt + ($(off1)); \n\
  else dg = -($(off2)) ; \n\
  $(gRaw) += dg; \n\
  $(g)=$(gMax)/2.0 *(tanh($(gSlope)*($(gRaw) - ($(gMid))))+1); \n");     
  wuL.needPreSt= TRUE;
  wuL.needPostSt= TRUE;

  weightUpdateModels.push_back(wuL);
  LEARN1SYNAPSE= weightUpdateModels.size()-1; 

#include "extra_weightupdates.h"
}

// bit tool macros
#include "numlib/simpleBit.h"

#endif  // _UTILS_H_
