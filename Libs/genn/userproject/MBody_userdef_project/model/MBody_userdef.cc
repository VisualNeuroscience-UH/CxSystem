/*--------------------------------------------------------------------------
   Author: Thomas Nowotny
  
   Institute: Center for Computational Neuroscience and Robotics
              University of Sussex
	      Falmer, Brighton BN1 9QJ, UK 
  
   email to:  T.Nowotny@sussex.ac.uk
  
   initial version: 2010-02-07
  
--------------------------------------------------------------------------*/

//--------------------------------------------------------------------------
/*! \file MBody_userdef.cc

\brief This file contains the model definition of the mushroom body model.
 tis used in the GeNN code generation and the user side simulation code 
(class classol, file classol_sim). 
*/
//--------------------------------------------------------------------------

#define DT 0.1  //!< This defines the global time step at which the simulation will run
#include "modelSpec.h"
#include "modelSpec.cc"
#include "sizes.h"

//uncomment the following line to turn on timing measures (Linux/MacOS only)
#define TIMING   

double myPOI_p[4]= {
  0.1,        // 0 - firing rate
  2.5,        // 1 - refratory period
  20.0,       // 2 - Vspike
  -60.0       // 3 - Vrest
};

double myPOI_ini[3]= {
 -60.0,        // 0 - V
  0,           // 1 - seed
  -10.0        // 2 - SpikeTime
};

double stdTM_p[7]= {
  7.15,          // 0 - gNa: Na conductance in 1/(mOhms * cm^2)
  50.0,          // 1 - ENa: Na equi potential in mV
  1.43,          // 2 - gK: K conductance in 1/(mOhms * cm^2)
  -95.0,         // 3 - EK: K equi potential in mV
  0.02672,       // 4 - gl: leak conductance in 1/(mOhms * cm^2)
  -63.563,       // 5 - El: leak equi potential in mV
  0.143          // 6 - Cmem: membr. capacity density in muF/cm^2
};


double stdTM_ini[4]= {
  -60.0,                       // 0 - membrane potential E
  0.0529324,                   // 1 - prob. for Na channel activation m
  0.3176767,                   // 2 - prob. for not Na channel blocking h
  0.5961207                    // 3 - prob. for K channel activation n
};

double *myPNKC_p= NULL;

double myPNKC_ini[1]= {
  0.01            // 0 - g: initial synaptic conductance
};

double postExpPNKC[2]={
  1.0,            // 0 - tau_S: decay time constant for S [ms]
  0.0		  // 1 - Erev: Reversal potential
};

double *myPNLHI_p= NULL;

double myPNLHI_ini[1]= {
    0.0          // 0 - g: initial synaptic conductance
};

double postExpPNLHI[2]={
  1.0,            // 0 - tau_S: decay time constant for S [ms]
  0.0		  // 1 - Erev: Reversal potential
};

double myLHIKC_p[2]= {
  -40.0,          // 0 - Epre: Presynaptic threshold potential
  50.0            // 1 - Vslope: Activation slope of graded release 
};

double myLHIKC_ini[1] = {
    1.0/_NLHI   // 0 - g: initial synaptic conductance
};

double postExpLHIKC[2]={
  1.5,            // 0 - tau_S: decay time constant for S [ms]
  -92.0		  // 1 - Erev: Reversal potential
};

double myKCDN_p[11]= {
  -20.0,         // 1 - Epre: Presynaptic threshold potential
  50.0,          // 3 - TLRN: time scale of learning changes
  50.0,         // 4 - TCHNG: width of learning window
  50000.0,       // 5 - TDECAY: time scale of synaptic strength decay
  100000.0,      // 6 - TPUNISH10: Time window of suppression in response to 1/0
  200.0,         // 7 - TPUNISH01: Time window of suppression in response to 0/1
  0.015,          // 8 - GMAX: Maximal conductance achievable
  0.0075,          // 9 - GMID: Midpoint of sigmoid g filter curve
  33.33,         // 10 - GSLOPE: slope of sigmoid g filter curve
  10.0,          // 11 - TAUSHiFT: shift of learning curve
  0.00006          // 12 - GSYN0: value of syn conductance g decays to
};

double myKCDN_ini[2]={
  0.01,            // 0 - g: synaptic conductance
  0.01,		  // 1 - graw: raw synaptic conductance
};

double postExpKCDN[2]={
  5.0,            // 0 - tau_S: decay time constant for S [ms]
  0.0		  // 1 - Erev: Reversal potential
};

double myDNDN_p[2]= {
  -30.0,         // 0 - Epre: Presynaptic threshold potential 
  50.0           // 1 - Vslope: Activation slope of graded release 
};

double myDNDN_ini[1]={
    5.0/_NLB      // 0 - g: synaptic conductance
};

double postExpDNDN[2]={
  2.5,            // 0 - tau_S: decay time constant for S [ms]
  -92.0		  // 1 - Erev: Reversal potential
};

double * postSynV = NULL;

double postSynV_EXPDECAY_EVAR[1] = {
0
};


  //define derived parameters for learn1synapse
  class pwSTDP_userdef : public dpclass  //!TODO This class definition may be code-generated in a future release
  {
    public:
      double calculateDerivedParameter(int index, vector<double> pars, double dt = DT){		
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
	  //return 1.0f/$(TPUNISH01) + 1.0f/$(TCHNG) *$(TLRN) / (2.0f/$(TCHNG));
	  return (1.0f/pars[5] + 1.0f/pars[2]) * pars[1] / (2.0f/pars[2]);
      }
      double lim1(vector<double> pars, double dt) {
	  //return 1.0f/$(TPUNISH10) + 1.0f/$(TCHNG) *$(TLRN) / (2.0f/$(TCHNG));
	  return -((1.0f/pars[4] + 1.0f/pars[2]) * pars[1] / (2.0f/pars[2]));
      }
      double slope0(vector<double> pars, double dt) {
	  //return -2.0f*$(gmax)/ ($(TCHNG)*$(TLRN)); 
	  return -2.0f*pars[6]/(pars[2]*pars[1]); 
      }
      double slope1(vector<double> pars, double dt) {
	  //return -1*slope0(pars, dt);
	  return -1*slope0(pars, dt);
      }
      double off0(vector<double> pars, double dt) {
	  //return $(gmax)/$(TPUNISH01);
	  return pars[6]/pars[5];
      }
      double off1(vector<double> pars, double dt) {
	  //return $(gmax)/$(TCHNG);
	  return pars[6]/pars[2];
      }
      double off2(vector<double> pars, double dt) {
	  //return $(gmax)/$(TPUNISH10);
			return pars[6]/pars[4];
      }
  };

//for sparse only -- we need to set them by hand if we want to do dense to sparse conversion. Sparse connectivity will only create sparse arrays.
scalar * gpPNKC = new scalar[_NAL*_NMB];
scalar * gpKCDN = new scalar[_NMB*_NLB];
//-------------------------------------

//--------------------------------------------------------------------------
/*! \brief This function defines the MBody1 model with user defined synapses. 
 */
//--------------------------------------------------------------------------

void modelDefinition(NNmodel &model) 
{	
    // initialize standard models
    initGeNN();
 /******************************************************************/		
  // redefine nsynapse as a user-defined syapse type 
  model.setPrecision(_FTYPE);

  postSynModel pstest;
  pstest.varNames.clear();
  pstest.varTypes.clear();

  pstest.varNames.push_back(tS("EEEE")); 
  pstest.varTypes.push_back(tS("scalar"));  

  pstest.pNames.clear();
  pstest.dpNames.clear(); 
  
  pstest.pNames.push_back(tS("tau")); 
  pstest.dpNames.push_back(tS("expDecay"));

  pstest.postSynDecay=tS(" 	 $(inSyn)*=$(expDecay);\n");
  pstest.postSyntoCurrent=tS("$(inSyn)*($(EEEE)-$(V))");

  pstest.dps = new expDecayDp;
  
  postSynModels.push_back(pstest);
  unsigned int EXPDECAY_EVAR=postSynModels.size()-1; //this is the synapse index to be used in addSynapsePopulation*/

  /*END ADDING POSTSYNAPTIC METHODS*/

  weightUpdateModel nsynapse;
  nsynapse.varNames.clear();
  nsynapse.varTypes.clear();
  nsynapse.pNames.clear();
  nsynapse.dpNames.clear();
  nsynapse.varNames.push_back(tS("g"));
  nsynapse.varTypes.push_back(tS("scalar"));
  // code for presynaptic spike:
  nsynapse.simCode = tS("$(addtoinSyn) = $(g);\n\
  $(updatelinsyn);\n\
  ");
  weightUpdateModels.push_back(nsynapse);
  unsigned int NSYNAPSE_userdef=weightUpdateModels.size()-1; //this is the synapse index to be used in addSynapsePopulation


  /******************************************************************/
  // redefine ngradsynapse as a user-defined syapse type: 
  weightUpdateModel ngradsynapse;
  ngradsynapse.varNames.clear();
  ngradsynapse.varTypes.clear();
  ngradsynapse.varNames.push_back(tS("g"));
  ngradsynapse.varTypes.push_back(tS("scalar"));
  ngradsynapse.pNames.clear();
  ngradsynapse.pNames.push_back(tS("Epre")); 
  ngradsynapse.pNames.push_back(tS("Vslope")); 
  ngradsynapse.dpNames.clear();
  // code for presynaptic spike event (defined by Epre)
  ngradsynapse.simCodeEvnt = tS("$(addtoinSyn) = $(g) * tanh(($(V_pre) - $(Epre)) / $(Vslope))* DT;\n\
    if ($(addtoinSyn) < 0) $(addtoinSyn) = 0.0;\n\
    $(updatelinsyn);\n");
  // definition of presynaptic spike event 
  ngradsynapse.evntThreshold = tS("    $(V_pre) > $(Epre)");
  weightUpdateModels.push_back(ngradsynapse);
  unsigned int NGRADSYNAPSE_userdef=weightUpdateModels.size()-1; //this is the synapse index to be used in addSynapsePopulation

  /******************************************************************/
  // redefine learn1synapse as a user-defined syapse type: 
  weightUpdateModel learn1synapse;

  learn1synapse.varNames.clear();
  learn1synapse.varTypes.clear();
  learn1synapse.varTypes.push_back(tS("scalar"));
  learn1synapse.varNames.push_back(tS("g")); 
  learn1synapse.varTypes.push_back(tS("scalar"));
  learn1synapse.varNames.push_back(tS("gRaw")); 
  learn1synapse.pNames.clear();
  learn1synapse.pNames.push_back(tS("Epre")); 
  learn1synapse.pNames.push_back(tS("tLrn"));  
  learn1synapse.pNames.push_back(tS("tChng")); 
  learn1synapse.pNames.push_back(tS("tDecay")); 
  learn1synapse.pNames.push_back(tS("tPunish10")); 
  learn1synapse.pNames.push_back(tS("tPunish01")); 
  learn1synapse.pNames.push_back(tS("gMax")); 
  learn1synapse.pNames.push_back(tS("gMid")); 
  learn1synapse.pNames.push_back(tS("gSlope")); 
  learn1synapse.pNames.push_back(tS("tauShift")); 
  learn1synapse.pNames.push_back(tS("gSyn0"));
  learn1synapse.dpNames.clear(); 
  learn1synapse.dpNames.push_back(tS("lim0"));
  learn1synapse.dpNames.push_back(tS("lim1"));
  learn1synapse.dpNames.push_back(tS("slope0"));
  learn1synapse.dpNames.push_back(tS("slope1"));
  learn1synapse.dpNames.push_back(tS("off0"));
  learn1synapse.dpNames.push_back(tS("off1"));
  learn1synapse.dpNames.push_back(tS("off2"));
  // code for presynaptic spike
  learn1synapse.simCode = tS("$(addtoinSyn) = $(g);\n\
					$(updatelinsyn); \n\
					scalar dt = $(sT_post) - t - ($(tauShift)); \n\
					scalar dg = 0;\n\
					if (dt > $(lim0))  \n\
					dg = -($(off0)) ; \n\
					else if (dt > 0.0)  \n\
					dg = $(slope0) * dt + ($(off1)); \n\
					else if (dt > $(lim1))  \n\
					dg = $(slope1) * dt + ($(off1)); \n\
					else dg = - ($(off2)) ; \n\
					$(gRaw) += dg; \n\
					$(g)=$(gMax)/2.0 *(tanh($(gSlope)*($(gRaw) - ($(gMid))))+1.0); \n\
					");     
  learn1synapse.dps = new pwSTDP_userdef;
  // code for post-synaptic spike event
  learn1synapse.simLearnPost = tS("scalar dt = t - ($(sT_pre)) - ($(tauShift)); \n\
				   scalar dg =0; \n\
				   if (dt > $(lim0))  \n\
				   dg = -($(off0)) ; \n \
				   else if (dt > 0.0)  \n\
			           dg = $(slope0) * dt + ($(off1)); \n\
				   else if (dt > $(lim1))  \n\
				   dg = $(slope1) * dt + ($(off1)); \n\
				   else dg = -($(off2)) ; \n\
				   $(gRaw) += dg; \n\
				   $(g)=$(gMax)/2.0 *(tanh($(gSlope)*($(gRaw) - ($(gMid))))+1.0); \n\
				  ");     
  // in the future, this could be auto-detected.
  learn1synapse.needPreSt= TRUE;
  learn1synapse.needPostSt= TRUE;
  weightUpdateModels.push_back(learn1synapse);
  unsigned int LEARN1SYNAPSE_userdef=weightUpdateModels.size()-1; //this is the synapse index to be used in addSynapsePopulation

  model.setName("MBody_userdef");
  model.addNeuronPopulation("PN", _NAL, POISSONNEURON, myPOI_p, myPOI_ini);
  model.addNeuronPopulation("KC", _NMB, TRAUBMILES, stdTM_p, stdTM_ini);
  model.addNeuronPopulation("LHI", _NLHI, TRAUBMILES, stdTM_p, stdTM_ini);
  model.addNeuronPopulation("DN", _NLB, TRAUBMILES, stdTM_p, stdTM_ini);
  
  model.addSynapsePopulation("PNKC", NSYNAPSE_userdef, SPARSE, INDIVIDUALG, NO_DELAY, EXPDECAY_EVAR, "PN", "KC", myPNKC_ini, myPNKC_p, postSynV_EXPDECAY_EVAR,postExpPNKC);
  model.setMaxConn("PNKC", _NMB);  
  //model.setSpanTypeToPre("PNKC");

  model.addSynapsePopulation("PNLHI", NSYNAPSE_userdef, ALLTOALL, INDIVIDUALG, NO_DELAY, EXPDECAY, "PN", "LHI", myPNLHI_ini, myPNLHI_p, postSynV, postExpPNLHI);

  model.addSynapsePopulation("LHIKC", NGRADSYNAPSE_userdef, ALLTOALL, GLOBALG, NO_DELAY, EXPDECAY, "LHI", "KC",  myLHIKC_ini, myLHIKC_p, postSynV, postExpLHIKC);

  model.addSynapsePopulation("KCDN", LEARN1SYNAPSE_userdef, SPARSE, INDIVIDUALG, NO_DELAY, EXPDECAY, "KC", "DN",  myKCDN_ini,  myKCDN_p, postSynV, postExpKCDN);
  model.setMaxConn("KCDN", _NLB); 
  //model.setSpanTypeToPre("KCDN");

  model.addSynapsePopulation("DNDN", NGRADSYNAPSE_userdef, ALLTOALL, GLOBALG, NO_DELAY, EXPDECAY, "DN", "DN", myDNDN_ini, myDNDN_p, postSynV, postExpDNDN);
  
#ifdef nGPU 
  cerr << "nGPU: " << nGPU << endl;
  model.setGPUDevice(nGPU);
#endif 
  model.setSeed(1234);
#ifdef TIMING
    model.setTiming(TRUE);
#else
    model.setTiming(FALSE);
#endif // TIMING
  model.finalize();
}
