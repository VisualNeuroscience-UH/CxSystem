{% macro h_file() %}

#ifndef ENGINE_H
#define ENGINE_H

//--------------------------------------------------------------------------
/*! \file engine.h

\brief Header file containing the class definition for the engine to conveniently run a model in GeNN
*/
//--------------------------------------------------------------------------

//--------------------------------------------------------------------------
/*! \brief This class contains the methods for running the model.
 */
//--------------------------------------------------------------------------

#include <ctime>
#include "magicnetwork_model_CODE/definitions.h"

class engine
{
 public:
  NNmodel model;
  // end of data fields 

  engine();
  ~engine();
  void init(unsigned int); 
  void free_device_mem(); 
  void run(double, unsigned int); 
#ifndef CPU_ONLY
  void getStateFromGPU(); 
  void getSpikesFromGPU(); 
#endif
};

#endif
{% endmacro %}


{% macro cpp_file() %}
#ifndef _ENGINE_CC_
#define _ENGINE_CC_

double brian::_last_run_time;
double brian::_last_run_completed_fraction;

//--------------------------------------------------------------------------
/*! \file engine.cc
\brief Implementation of the engine class.
*/
//--------------------------------------------------------------------------

#include "engine.h"

engine::engine()
{
  modelDefinition(model);
  allocateMem();
  initialize();
  brian::_last_run_time= 0.0;
  brian::_last_run_completed_fraction= 0.0;
}

//--------------------------------------------------------------------------
/*! \brief Method for initialising variables
 */
//--------------------------------------------------------------------------

void engine::init(unsigned int which)
{
#ifndef CPU_ONLY
  if (which == CPU) {
  }
  if (which == GPU) {
    copyStateToDevice();
  }
#endif
}

//--------------------------------------------------------------------------
//--------------------------------------------------------------------------

engine::~engine()
{
}


//--------------------------------------------------------------------------
/*! \brief Method for simulating the model for a given period of time
 */
//--------------------------------------------------------------------------

void engine::run(double duration, //!< Duration of time to run the model for 
		  unsigned int which //!< Flag determining whether to run on GPU or CPU only
		  )
{
  std::clock_t start, current; 
  const double t_start = t;
  unsigned int pno;
  unsigned int offset= 0;

  start = std::clock();
  int riT= (int) (duration/DT+1e-2);
  double elapsed_realtime;

  for (int i= 0; i < riT; i++) {
      // report state
      t+= DT;
      {% for sm in state_monitor_models %}
      {% if sm.when == 'start' %}
      {% for var in sm.variables %}
      {% if sm.isSynaptic %}
      {% if sm.connectivity == 'DENSE' %}
      convert_dense_matrix_2_dynamic_arrays({{var}}{{sm.monitored}}, {{sm.srcN}}, {{sm.trgN}},brian::_dynamic_array_{{sm.monitored}}__synaptic_pre, brian::_dynamic_array_{{sm.monitored}}__synaptic_post, brian::_dynamic_array_{{sm.monitored}}_{{var}});
      {% else %}
      convert_sparse_synapses_2_dynamic_arrays(C{{sm.monitored}}, {{var}}{{sm.monitored}}, {{sm.srcN}}, {{sm.trgN}}, brian::_dynamic_array_{{sm.monitored}}__synaptic_pre, brian::_dynamic_array_{{sm.monitored}}__synaptic_post, brian::_dynamic_array_{{sm.monitored}}_{{var}}, b2g::FULL_MONTY);
      {% endif %}
      {% else %}
      copy_genn_to_brian({{var}}{{sm.monitored}}, brian::_array_{{sm.monitored}}_{{var}}, {{sm.N}});
      {% endif %}
      {% endfor %}
      _run_{{sm.name}}_codeobject();
      {% endif %}
      {% endfor %}
#ifndef CPU_ONLY
      if (which == GPU) {
	  stepTimeGPU();
	  t= t-DT;
	  {% for spkGen in spikegenerator_models %}
	  _run_{{spkGen.name}}_codeobject();
	  push{{spkGen.name}}SpikesToDevice();
	  {% endfor %}
	  {% for spkMon in spike_monitor_models %}
	  {% if (spkMon.notSpikeGeneratorGroup) %}
	  pull{{spkMon.neuronGroup}}SpikesFromDevice();
	  {% endif %}
	  {% endfor %}
	  {% for rateMon in rate_monitor_models %}
	  {% if (rateMon.notSpikeGeneratorGroup) %}
	  pull{{rateMon.neuronGroup}}SpikesFromDevice();
	  {% endif %}
	  {% endfor %}
	  {% for sm in state_monitor_models %}
	  pull{{sm.monitored}}StateFromDevice();
	  {% endfor %}
      }
#endif
      if (which == CPU) {
	  stepTimeCPU();
	  t= t-DT;
	  {% for spkGen in spikegenerator_models %}
	  _run_{{spkGen.name}}_codeobject();
	  {% endfor %}
      }
      // report state 
      {% for sm in state_monitor_models %}
      {% if sm.when != 'start' %}
      {% for var in sm.variables %}
      {% if sm.isSynaptic %}
      {% if sm.connectivity == 'DENSE' %}
      convert_dense_matrix_2_dynamic_arrays({{var}}{{sm.monitored}}, {{sm.srcN}}, {{sm.trgN}},brian::_dynamic_array_{{sm.monitored}}__synaptic_pre, brian::_dynamic_array_{{sm.monitored}}__synaptic_post, brian::_dynamic_array_{{sm.monitored}}_{{var}});
      {% else %}
      convert_sparse_synapses_2_dynamic_arrays(C{{sm.monitored}}, {{var}}{{sm.monitored}}, {{sm.srcN}}, {{sm.trgN}}, brian::_dynamic_array_{{sm.monitored}}__synaptic_pre, brian::_dynamic_array_{{sm.monitored}}__synaptic_post, brian::_dynamic_array_{{sm.monitored}}_{{var}}, b2g::FULL_MONTY);
      {% endif %}
      {% else %}
      copy_genn_to_brian({{var}}{{sm.monitored}}, brian::_array_{{sm.monitored}}_{{var}}, {{sm.N}});
      {% endif %}
      {% endfor %}
      _run_{{sm.name}}_codeobject();
      {% endif %}
      {% endfor %}
      // report spikes
      {% for spkMon in spike_monitor_models %}
      _run_{{spkMon.name}}_codeobject();
      {% endfor %}
      {% for rateMon in rate_monitor_models %}
      _run_{{rateMon.name}}_codeobject();
      {% endfor %}
      {% if maximum_run_time is not none %}
      current= std::clock();
      elapsed_realtime= (double) (current - start)/CLOCKS_PER_SEC;
      if (elapsed_realtime > {{maximum_run_time}}) {
	  break;
      }
      {% endif %}
  }  
  brian::_last_run_time = elapsed_realtime;
  if (duration > 0.0)
  {
      brian::_last_run_completed_fraction = (t-t_start)/duration;
  } else {
      brian::_last_run_completed_fraction = 1.0;
  }
}


#ifndef CPU_ONLY
//--------------------------------------------------------------------------
/*! \brief Method for copying all variables of the last time step from the GPU
 
  This is a simple wrapper for the convenience function copyStateFromDevice() which is provided by GeNN.
*/
//--------------------------------------------------------------------------

void engine::getStateFromGPU()
{
  copyStateFromDevice();
}

//--------------------------------------------------------------------------
/*! \brief Method for copying all spikes of the last time step from the GPU
 
  This is a simple wrapper for the convenience function copySpikesFromDevice() which is provided by GeNN.
*/
//--------------------------------------------------------------------------

void engine::getSpikesFromGPU()
{
  copySpikeNFromDevice();
  copySpikesFromDevice();
}


#endif


#endif	

{% endmacro %}
