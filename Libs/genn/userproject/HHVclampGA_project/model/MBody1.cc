/*--------------------------------------------------------------------------
   Author: Thomas Nowotny
  
   Institute: Center for Computational Neuroscience and Robotics
              University of Sussex
	      Falmer, Brighton BN1 9QJ, UK 
  
   email to:  T.Nowotny@sussex.ac.uk
  
   initial version: 2010-02-07
  
--------------------------------------------------------------------------*/

//--------------------------------------------------------------------------
/*! \file MBody1.cc

\brief This file contains the model definition of the mushroom body "MBody1" model. It is used in both the GeNN code generation and the user side simulation code (class classol, file classol_sim).
*/
//--------------------------------------------------------------------------

#define DT 0.1  //!< This defines the global time step at which the simulation will run
#include "modelSpec.h"
#include "modelSpec.cc"

double myPOI_p[4]= {
  0.1,        // 0 - firing rate
  2.5,        // 1 - refratory period
  20.0,       // 2 - Vspike
  -60.0       // 3 - Vrest
};

double myPOI_ini[4]= {
 -60.0,        // 0 - V
  0,           // 1 - seed
  -10.0,       // 2 - SpikeTime
};

// double stdMAP_p[4]= {
//   60.0,          // 0 - Vspike: spike Amplitude factor
//   3.0,           // 1 - alpha: "steepness / size" parameter
//   -2.468,        // 2 - y: "shift / excitation" parameter
//   0.0165         // 3 - beta: input sensitivity
// };

// double stdMAP_ini[2]= {
//   -60.0,         // 0 - V: initial value for membrane potential
//   -60.0          // 1 - preV: initial previous value
// };

// double myLHI_p[4]= {
//   60.0,          // 0 - Vspike: spike Amplitude factor
//   3.0,           // 1 - alpha: "steepness / size" parameter
//   -2.468,        // 2 - y: "shift / excitation" parameter
//   0.0165         // 3 - beta: input sensitivity
// };

// double myLHI_ini[2]= {
//   -60.0,         // 0 - V: initial value for membrane potential
//   -60.0          // 1 - preV: initial previous value
// };

// double myLB_p[4]= {
//   60.0,          // 0 - Vspike: spike Amplitude factor
//   3.0,           // 1 - alpha: "steepness / size" parameter
//   -2.468,        // 2 - y: "shift / excitation" parameter
//   0.0165         // 3 - beta: input sensitivity
// };

// double myLB_ini[2]= {
//   -60.0,         // 0 - V: initial value for membrane potential
//   -60.0          // 1 - preV: initial previous value
// };

double stdTM_p[7]= {
  7.15,          // 0 - gNa: Na conductance in 1/(mOhms * cm^2)
  50.0,          // 1 - ENa: Na equi potential in mV
  1.43,          // 2 - gK: K conductance in 1/(mOhms * cm^2)
  -95.0,         // 3 - EK: K equi potential in mV
  0.02672,         // 4 - gl: leak conductance in 1/(mOhms * cm^2)
  -63.563,         // 5 - El: leak equi potential in mV
  0.143        // 6 - Cmem: membr. capacity density in muF/cm^2
};


double stdTM_ini[4]= {
  -60.0,                       // 0 - membrane potential E
  0.0529324,                   // 1 - prob. for Na channel activation m
  0.3176767,                   // 2 - prob. for not Na channel blocking h
  0.5961207                    // 3 - prob. for K channel activation n
};


double myPNKC_p[3]= {
  0.0,           // 0 - Erev: Reversal potential
  -20.0,         // 1 - Epre: Presynaptic threshold potential
  1.0            // 2 - tau_S: decay time constant for S [ms]
};
//double gPNKC= 0.01;

double postExpPNKC[2]={
  1.0,            // 0 - tau_S: decay time constant for S [ms]
  0.0		  // 1 - Erev: Reversal potential
};

double myPNLHI_p[3]= {
  0.0,           // 0 - Erev: Reversal potential
  -20.0,         // 1 - Epre: Presynaptic threshold potential
  1.0            // 2 - tau_S: decay time constant for S [ms]
};

double postExpPNLHI[2]={
  1.0,            // 0 - tau_S: decay time constant for S [ms]
  0.0		  // 1 - Erev: Reversal potential
};

double myLHIKC_p[4]= {
  -92.0,          // 0 - Erev: Reversal potential
  -40.0,          // 1 - Epre: Presynaptic threshold potential
  3.0,            // 2 - tau_S: decay time constant for S [ms]
  50.0            // 3 - Vslope: Activation slope of graded release 
};
//double gLHIKC= 0.6;
double gLHIKC= 0.006;

double postExpLHIKC[2]={
  3.0,            // 0 - tau_S: decay time constant for S [ms]
  -92.0		  // 1 - Erev: Reversal potential
};

double myKCDN_p[13]= {
  0.0,           // 0 - Erev: Reversal potential
  -20.0,         // 1 - Epre: Presynaptic threshold potential
  5.0,           // 2 - tau_S: decay time constant for S [ms]
  25.0,          // 3 - TLRN: time scale of learning changes
  100.0,         // 4 - TCHNG: width of learning window
  50000.0,       // 5 - TDECAY: time scale of synaptic strength decay
  100000.0,      // 6 - TPUNISH10: Time window of suppression in response to 1/0
  100.0,         // 7 - TPUNISH01: Time window of suppression in response to 0/1
  0.06,          // 8 - GMAX: Maximal conductance achievable
  0.03,          // 9 - GMID: Midpoint of sigmoid g filter curve
  33.33,         // 10 - GSLOPE: slope of sigmoid g filter curve
  10.0,          // 11 - TAUSHiFT: shift of learning curve
  //  0.006          // 12 - GSYN0: value of syn conductance g decays to
  0.00006          // 12 - GSYN0: value of syn conductance g decays to
};

//#define KCDNGSYN0 0.006
double postExpKCDN[2]={
  5.0,            // 0 - tau_S: decay time constant for S [ms]
  0.0		  // 1 - Erev: Reversal potential
};

double myDNDN_p[4]= {
  -92.0,        // 0 - Erev: Reversal potential
  -30.0,        // 1 - Epre: Presynaptic threshold potential 
  8.0,          // 2 - tau_S: decay time constant for S [ms]
  50.0          // 3 - Vslope: Activation slope of graded release 
};
//double gDNDN= 0.04;
double gDNDN= 0.01;


double postExpDNDN[2]={
  8.0,            // 0 - tau_S: decay time constant for S [ms]
  -92.0		  // 1 - Erev: Reversal potential
};

double *postSynV = NULL;



#include "../../userproject/include/sizes.h"

//--------------------------------------------------------------------------
/*! \brief This function defines the MBody1 model, and it is a good example of how networks should be defined.
 */
//--------------------------------------------------------------------------

void modelDefinition(NNmodel &model) 
{
  neuronModel n;
  // HH neurons with adjustable parameters (introduced as variables)
  n.varNames.clear();
  n.varTypes.clear();
  n.varNames.push_back(tS("V"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("m"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("h"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("n"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("gNa"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("ENa"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("gK"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("Ek"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("gl"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("El"));
  n.varTypes.push_back(tS("double"));
  n.varNames.push_back(tS("C"));
  n.varTypes.push_back(tS("double"));

  n.simCode= tS("   double Imem;\n\
    unsigned int mt;\n\
    double mdt= DT/25.0;\n\
    __shared__ double shStepVG;\n\
    if (threadIdx.x == 0) shStepVG= d_stepVG;\n\
    __syncthreads();\n\
    for (mt=0; mt < 25; mt++) {\n\
      Isyn= 1000.0*(shStepVG-$(V));\n\
      Imem= -($(m)*$(m)*$(m)*$(h)*$(gNa)*($(V)-($(ENa)))+\n\
              $(n)*$(n)*$(n)*$(n)*$(gK)*($(V)-($(EK)))+\n\
              $(gl)*($(V)-($(El)))-Isyn);\n\
      double _a= (3.5+0.1*$(V)) / (1.0-exp(-3.5-0.1*$(V)));\n\
      double _b= 4.0*exp(-($(V)+60.0)/18.0);\n\
      $(m)+= (_a*(1.0-$(m))-_b*$(m))*mdt;\n\
      _a= 0.07*exp(-$(V)/20.0-3.0);\n\
      _b= 1.0 / (exp(-3.0-0.1*$(V))+1.0);\n\
      $(h)+= (_a*(1.0-$(h))-_b*$(h))*mdt;\n\
      _a= (-0.5-0.01*$(V)) / (exp(-5.0-0.1*$(V))-1.0)\n\
      _b= 0.125*exp(-($(V)+60.0)/80.0);\n\
      $(n)+= (_a*(1.0-$(n))-_b*$(n))*mdt;\n\
      $(V)+= Imem/$(C)*mdt;\n\
    }\n");

  n.thresholdConditionCode = tS("$(V) > 20");//TODO check this, to get better value

  nModels.push_back(n);

  model.setName("MBody1");
  model.addNeuronPopulation("PN", _NAL, POISSONNEURON, myPOI_p, myPOI_ini);
  model.addNeuronPopulation("KC", _NMB, TRAUBMILES, stdTM_p, stdTM_ini);
  model.addNeuronPopulation("LHI", _NLHI, TRAUBMILES, stdTM_p, stdTM_ini);
  model.addNeuronPopulation("DN", _NLB, TRAUBMILES, stdTM_p, stdTM_ini);
  
  model.addSynapsePopulation("PNKC", NSYNAPSE, DENSE, INDIVIDUALG, NO_DELAY, EXPDECAY, "PN", "KC", myPNKC_p, postSynV,postExpPNKC);
  model.addSynapsePopulation("PNLHI", NSYNAPSE, ALLTOALL, INDIVIDUALG, NO_DELAY, EXPDECAY, "PN", "LHI", myPNLHI_p, postSynV, postExpPNLHI);
  model.addSynapsePopulation("LHIKC", NGRADSYNAPSE, ALLTOALL, GLOBALG, NO_DELAY, EXPDECAY, "LHI", "KC", myLHIKC_p, postSynV, postExpLHIKC);
  model.setSynapseG("LHIKC", gLHIKC);
  model.addSynapsePopulation("KCDN", LEARN1SYNAPSE, ALLTOALL, INDIVIDUALG, NO_DELAY, EXPDECAY, "KC", "DN", myKCDN_p, postSynV, postExpKCDN);
  model.addSynapsePopulation("DNDN", NGRADSYNAPSE, ALLTOALL, GLOBALG, NO_DELAY, EXPDECAY, "DN", "DN", myDNDN_p, postSynV, postExpDNDN);
  model.setSynapseG("DNDN", gDNDN);
}
