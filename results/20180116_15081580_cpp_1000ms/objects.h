
#ifndef _BRIAN_OBJECTS_H
#define _BRIAN_OBJECTS_H

#include "synapses_classes.h"
#include "brianlib/clocks.h"
#include "brianlib/dynamic_array.h"
#include "brianlib/stdint_compat.h"
#include "network.h"
#include "randomkit.h"
#include<vector>


namespace brian {

// In OpenMP we need one state per thread
extern std::vector< rk_state* > _mersenne_twister_states;

//////////////// clocks ///////////////////
extern Clock defaultclock;

//////////////// networks /////////////////
extern Network magicnetwork;

//////////////// dynamic arrays ///////////
extern std::vector<int32_t> _dynamic_array_spikemonitor_1_i;
extern std::vector<double> _dynamic_array_spikemonitor_1_t;
extern std::vector<int32_t> _dynamic_array_spikemonitor_i;
extern std::vector<double> _dynamic_array_spikemonitor_t;
extern std::vector<int32_t> _dynamic_array_synapses_1__synaptic_post;
extern std::vector<int32_t> _dynamic_array_synapses_1__synaptic_pre;
extern std::vector<double> _dynamic_array_synapses_1_delay;
extern std::vector<double> _dynamic_array_synapses_1_lastupdate;
extern std::vector<int32_t> _dynamic_array_synapses_1_N_incoming;
extern std::vector<int32_t> _dynamic_array_synapses_1_N_outgoing;
extern std::vector<double> _dynamic_array_synapses_1_wght;
extern std::vector<int32_t> _dynamic_array_synapses_2__synaptic_post;
extern std::vector<int32_t> _dynamic_array_synapses_2__synaptic_pre;
extern std::vector<double> _dynamic_array_synapses_2_delay;
extern std::vector<double> _dynamic_array_synapses_2_lastupdate;
extern std::vector<int32_t> _dynamic_array_synapses_2_N_incoming;
extern std::vector<int32_t> _dynamic_array_synapses_2_N_outgoing;
extern std::vector<double> _dynamic_array_synapses_2_wght;
extern std::vector<int32_t> _dynamic_array_synapses_3__synaptic_post;
extern std::vector<int32_t> _dynamic_array_synapses_3__synaptic_pre;
extern std::vector<double> _dynamic_array_synapses_3_delay;
extern std::vector<double> _dynamic_array_synapses_3_lastupdate;
extern std::vector<int32_t> _dynamic_array_synapses_3_N_incoming;
extern std::vector<int32_t> _dynamic_array_synapses_3_N_outgoing;
extern std::vector<double> _dynamic_array_synapses_3_wght;
extern std::vector<int32_t> _dynamic_array_synapses__synaptic_post;
extern std::vector<int32_t> _dynamic_array_synapses__synaptic_pre;
extern std::vector<double> _dynamic_array_synapses_delay;
extern std::vector<double> _dynamic_array_synapses_lastupdate;
extern std::vector<int32_t> _dynamic_array_synapses_N_incoming;
extern std::vector<int32_t> _dynamic_array_synapses_N_outgoing;
extern std::vector<double> _dynamic_array_synapses_wght;

//////////////// arrays ///////////////////
extern double *_array_defaultclock_dt;
extern const int _num__array_defaultclock_dt;
extern double *_array_defaultclock_t;
extern const int _num__array_defaultclock_t;
extern int64_t *_array_defaultclock_timestep;
extern const int _num__array_defaultclock_timestep;
extern int32_t *_array_neurongroup_1__spikespace;
extern const int _num__array_neurongroup_1__spikespace;
extern double *_array_neurongroup_1_ge_soma;
extern const int _num__array_neurongroup_1_ge_soma;
extern double *_array_neurongroup_1_gi_soma;
extern const int _num__array_neurongroup_1_gi_soma;
extern int32_t *_array_neurongroup_1_i;
extern const int _num__array_neurongroup_1_i;
extern double *_array_neurongroup_1_lastspike;
extern const int _num__array_neurongroup_1_lastspike;
extern char *_array_neurongroup_1_not_refractory;
extern const int _num__array_neurongroup_1_not_refractory;
extern double *_array_neurongroup_1_vm;
extern const int _num__array_neurongroup_1_vm;
extern double *_array_neurongroup_1_x;
extern const int _num__array_neurongroup_1_x;
extern double *_array_neurongroup_1_y;
extern const int _num__array_neurongroup_1_y;
extern int32_t *_array_neurongroup__spikespace;
extern const int _num__array_neurongroup__spikespace;
extern double *_array_neurongroup_ge_soma;
extern const int _num__array_neurongroup_ge_soma;
extern double *_array_neurongroup_gi_soma;
extern const int _num__array_neurongroup_gi_soma;
extern int32_t *_array_neurongroup_i;
extern const int _num__array_neurongroup_i;
extern double *_array_neurongroup_lastspike;
extern const int _num__array_neurongroup_lastspike;
extern char *_array_neurongroup_not_refractory;
extern const int _num__array_neurongroup_not_refractory;
extern double *_array_neurongroup_vm;
extern const int _num__array_neurongroup_vm;
extern double *_array_neurongroup_x;
extern const int _num__array_neurongroup_x;
extern double *_array_neurongroup_y;
extern const int _num__array_neurongroup_y;
extern int32_t *_array_spikemonitor_1__source_idx;
extern const int _num__array_spikemonitor_1__source_idx;
extern int32_t *_array_spikemonitor_1_count;
extern const int _num__array_spikemonitor_1_count;
extern int32_t *_array_spikemonitor_1_N;
extern const int _num__array_spikemonitor_1_N;
extern int32_t *_array_spikemonitor__source_idx;
extern const int _num__array_spikemonitor__source_idx;
extern int32_t *_array_spikemonitor_count;
extern const int _num__array_spikemonitor_count;
extern int32_t *_array_spikemonitor_N;
extern const int _num__array_spikemonitor_N;
extern int32_t *_array_synapses_1_N;
extern const int _num__array_synapses_1_N;
extern int32_t *_array_synapses_2_N;
extern const int _num__array_synapses_2_N;
extern int32_t *_array_synapses_3_N;
extern const int _num__array_synapses_3_N;
extern int32_t *_array_synapses_N;
extern const int _num__array_synapses_N;

//////////////// dynamic arrays 2d /////////

/////////////// static arrays /////////////
extern double *_static_array__array_neurongroup_1_vm;
extern const int _num__static_array__array_neurongroup_1_vm;
extern double *_static_array__array_neurongroup_1_x;
extern const int _num__static_array__array_neurongroup_1_x;
extern double *_static_array__array_neurongroup_1_y;
extern const int _num__static_array__array_neurongroup_1_y;
extern double *_static_array__array_neurongroup_vm;
extern const int _num__static_array__array_neurongroup_vm;
extern double *_static_array__array_neurongroup_x;
extern const int _num__static_array__array_neurongroup_x;
extern double *_static_array__array_neurongroup_y;
extern const int _num__static_array__array_neurongroup_y;

//////////////// synapses /////////////////
// synapses
extern SynapticPathway<double> synapses_pre;
// synapses_1
extern SynapticPathway<double> synapses_1_pre;
// synapses_2
extern SynapticPathway<double> synapses_2_pre;
// synapses_3
extern SynapticPathway<double> synapses_3_pre;

// Profiling information for each code object
extern double neurongroup_1_resetter_codeobject_profiling_info;
extern double neurongroup_1_stateupdater_codeobject_profiling_info;
extern double neurongroup_1_thresholder_codeobject_profiling_info;
extern double neurongroup_resetter_codeobject_profiling_info;
extern double neurongroup_stateupdater_codeobject_profiling_info;
extern double neurongroup_thresholder_codeobject_profiling_info;
extern double spikemonitor_1_codeobject_profiling_info;
extern double spikemonitor_codeobject_profiling_info;
extern double synapses_1_group_variable_set_conditional_codeobject_profiling_info;
extern double synapses_1_group_variable_set_conditional_codeobject_1_profiling_info;
extern double synapses_1_pre_codeobject_profiling_info;
extern double synapses_1_pre_initialise_queue_profiling_info;
extern double synapses_1_pre_push_spikes_profiling_info;
extern double synapses_1_synapses_create_generator_codeobject_profiling_info;
extern double synapses_2_group_variable_set_conditional_codeobject_profiling_info;
extern double synapses_2_group_variable_set_conditional_codeobject_1_profiling_info;
extern double synapses_2_pre_codeobject_profiling_info;
extern double synapses_2_pre_initialise_queue_profiling_info;
extern double synapses_2_pre_push_spikes_profiling_info;
extern double synapses_2_synapses_create_generator_codeobject_profiling_info;
extern double synapses_3_group_variable_set_conditional_codeobject_profiling_info;
extern double synapses_3_group_variable_set_conditional_codeobject_1_profiling_info;
extern double synapses_3_pre_codeobject_profiling_info;
extern double synapses_3_pre_initialise_queue_profiling_info;
extern double synapses_3_pre_push_spikes_profiling_info;
extern double synapses_3_synapses_create_generator_codeobject_profiling_info;
extern double synapses_group_variable_set_conditional_codeobject_profiling_info;
extern double synapses_group_variable_set_conditional_codeobject_1_profiling_info;
extern double synapses_pre_codeobject_profiling_info;
extern double synapses_pre_initialise_queue_profiling_info;
extern double synapses_pre_push_spikes_profiling_info;
extern double synapses_synapses_create_generator_codeobject_profiling_info;

}

void _init_arrays();
void _load_arrays();
void _write_arrays();
void _dealloc_arrays();

#endif


