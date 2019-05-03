
#include "objects.h"
#include "synapses_classes.h"
#include "brianlib/clocks.h"
#include "brianlib/dynamic_array.h"
#include "brianlib/stdint_compat.h"
#include "network.h"
#include "randomkit.h"
#include<vector>
#include<iostream>
#include<fstream>

namespace brian {

std::vector< rk_state* > _mersenne_twister_states;

//////////////// networks /////////////////
Network magicnetwork;

//////////////// arrays ///////////////////
double * _array_defaultclock_dt;
const int _num__array_defaultclock_dt = 1;
double * _array_defaultclock_t;
const int _num__array_defaultclock_t = 1;
int64_t * _array_defaultclock_timestep;
const int _num__array_defaultclock_timestep = 1;
int32_t * _array_neurongroup_1__spikespace;
const int _num__array_neurongroup_1__spikespace = 801;
double * _array_neurongroup_1_ge_soma;
const int _num__array_neurongroup_1_ge_soma = 800;
double * _array_neurongroup_1_gi_soma;
const int _num__array_neurongroup_1_gi_soma = 800;
int32_t * _array_neurongroup_1_i;
const int _num__array_neurongroup_1_i = 800;
double * _array_neurongroup_1_lastspike;
const int _num__array_neurongroup_1_lastspike = 800;
char * _array_neurongroup_1_not_refractory;
const int _num__array_neurongroup_1_not_refractory = 800;
double * _array_neurongroup_1_vm;
const int _num__array_neurongroup_1_vm = 800;
double * _array_neurongroup_1_x;
const int _num__array_neurongroup_1_x = 800;
double * _array_neurongroup_1_y;
const int _num__array_neurongroup_1_y = 800;
int32_t * _array_neurongroup__spikespace;
const int _num__array_neurongroup__spikespace = 3201;
double * _array_neurongroup_ge_soma;
const int _num__array_neurongroup_ge_soma = 3200;
double * _array_neurongroup_gi_soma;
const int _num__array_neurongroup_gi_soma = 3200;
int32_t * _array_neurongroup_i;
const int _num__array_neurongroup_i = 3200;
double * _array_neurongroup_lastspike;
const int _num__array_neurongroup_lastspike = 3200;
char * _array_neurongroup_not_refractory;
const int _num__array_neurongroup_not_refractory = 3200;
double * _array_neurongroup_vm;
const int _num__array_neurongroup_vm = 3200;
double * _array_neurongroup_x;
const int _num__array_neurongroup_x = 3200;
double * _array_neurongroup_y;
const int _num__array_neurongroup_y = 3200;
int32_t * _array_spikemonitor_1__source_idx;
const int _num__array_spikemonitor_1__source_idx = 800;
int32_t * _array_spikemonitor_1_count;
const int _num__array_spikemonitor_1_count = 800;
int32_t * _array_spikemonitor_1_N;
const int _num__array_spikemonitor_1_N = 1;
int32_t * _array_spikemonitor__source_idx;
const int _num__array_spikemonitor__source_idx = 3200;
int32_t * _array_spikemonitor_count;
const int _num__array_spikemonitor_count = 3200;
int32_t * _array_spikemonitor_N;
const int _num__array_spikemonitor_N = 1;
int32_t * _array_synapses_1_N;
const int _num__array_synapses_1_N = 1;
int32_t * _array_synapses_2_N;
const int _num__array_synapses_2_N = 1;
int32_t * _array_synapses_3_N;
const int _num__array_synapses_3_N = 1;
int32_t * _array_synapses_N;
const int _num__array_synapses_N = 1;

//////////////// dynamic arrays 1d /////////
std::vector<int32_t> _dynamic_array_spikemonitor_1_i;
std::vector<double> _dynamic_array_spikemonitor_1_t;
std::vector<int32_t> _dynamic_array_spikemonitor_i;
std::vector<double> _dynamic_array_spikemonitor_t;
std::vector<int32_t> _dynamic_array_synapses_1__synaptic_post;
std::vector<int32_t> _dynamic_array_synapses_1__synaptic_pre;
std::vector<double> _dynamic_array_synapses_1_delay;
std::vector<double> _dynamic_array_synapses_1_lastupdate;
std::vector<int32_t> _dynamic_array_synapses_1_N_incoming;
std::vector<int32_t> _dynamic_array_synapses_1_N_outgoing;
std::vector<double> _dynamic_array_synapses_1_wght;
std::vector<int32_t> _dynamic_array_synapses_2__synaptic_post;
std::vector<int32_t> _dynamic_array_synapses_2__synaptic_pre;
std::vector<double> _dynamic_array_synapses_2_delay;
std::vector<double> _dynamic_array_synapses_2_lastupdate;
std::vector<int32_t> _dynamic_array_synapses_2_N_incoming;
std::vector<int32_t> _dynamic_array_synapses_2_N_outgoing;
std::vector<double> _dynamic_array_synapses_2_wght;
std::vector<int32_t> _dynamic_array_synapses_3__synaptic_post;
std::vector<int32_t> _dynamic_array_synapses_3__synaptic_pre;
std::vector<double> _dynamic_array_synapses_3_delay;
std::vector<double> _dynamic_array_synapses_3_lastupdate;
std::vector<int32_t> _dynamic_array_synapses_3_N_incoming;
std::vector<int32_t> _dynamic_array_synapses_3_N_outgoing;
std::vector<double> _dynamic_array_synapses_3_wght;
std::vector<int32_t> _dynamic_array_synapses__synaptic_post;
std::vector<int32_t> _dynamic_array_synapses__synaptic_pre;
std::vector<double> _dynamic_array_synapses_delay;
std::vector<double> _dynamic_array_synapses_lastupdate;
std::vector<int32_t> _dynamic_array_synapses_N_incoming;
std::vector<int32_t> _dynamic_array_synapses_N_outgoing;
std::vector<double> _dynamic_array_synapses_wght;

//////////////// dynamic arrays 2d /////////

/////////////// static arrays /////////////
double * _static_array__array_neurongroup_1_vm;
const int _num__static_array__array_neurongroup_1_vm = 800;
double * _static_array__array_neurongroup_1_x;
const int _num__static_array__array_neurongroup_1_x = 800;
double * _static_array__array_neurongroup_1_y;
const int _num__static_array__array_neurongroup_1_y = 800;
double * _static_array__array_neurongroup_vm;
const int _num__static_array__array_neurongroup_vm = 3200;
double * _static_array__array_neurongroup_x;
const int _num__static_array__array_neurongroup_x = 3200;
double * _static_array__array_neurongroup_y;
const int _num__static_array__array_neurongroup_y = 3200;

//////////////// synapses /////////////////
// synapses
SynapticPathway<double> synapses_pre(
		_dynamic_array_synapses_delay,
		_dynamic_array_synapses__synaptic_pre,
		0, 3200);
// synapses_1
SynapticPathway<double> synapses_1_pre(
		_dynamic_array_synapses_1_delay,
		_dynamic_array_synapses_1__synaptic_pre,
		0, 3200);
// synapses_2
SynapticPathway<double> synapses_2_pre(
		_dynamic_array_synapses_2_delay,
		_dynamic_array_synapses_2__synaptic_pre,
		0, 800);
// synapses_3
SynapticPathway<double> synapses_3_pre(
		_dynamic_array_synapses_3_delay,
		_dynamic_array_synapses_3__synaptic_pre,
		0, 800);

//////////////// clocks ///////////////////
Clock defaultclock;  // attributes will be set in run.cpp

// Profiling information for each code object
double neurongroup_1_resetter_codeobject_profiling_info = 0.0;
double neurongroup_1_stateupdater_codeobject_profiling_info = 0.0;
double neurongroup_1_thresholder_codeobject_profiling_info = 0.0;
double neurongroup_resetter_codeobject_profiling_info = 0.0;
double neurongroup_stateupdater_codeobject_profiling_info = 0.0;
double neurongroup_thresholder_codeobject_profiling_info = 0.0;
double spikemonitor_1_codeobject_profiling_info = 0.0;
double spikemonitor_codeobject_profiling_info = 0.0;
double synapses_1_group_variable_set_conditional_codeobject_profiling_info = 0.0;
double synapses_1_group_variable_set_conditional_codeobject_1_profiling_info = 0.0;
double synapses_1_pre_codeobject_profiling_info = 0.0;
double synapses_1_pre_initialise_queue_profiling_info = 0.0;
double synapses_1_pre_push_spikes_profiling_info = 0.0;
double synapses_1_synapses_create_generator_codeobject_profiling_info = 0.0;
double synapses_2_group_variable_set_conditional_codeobject_profiling_info = 0.0;
double synapses_2_group_variable_set_conditional_codeobject_1_profiling_info = 0.0;
double synapses_2_pre_codeobject_profiling_info = 0.0;
double synapses_2_pre_initialise_queue_profiling_info = 0.0;
double synapses_2_pre_push_spikes_profiling_info = 0.0;
double synapses_2_synapses_create_generator_codeobject_profiling_info = 0.0;
double synapses_3_group_variable_set_conditional_codeobject_profiling_info = 0.0;
double synapses_3_group_variable_set_conditional_codeobject_1_profiling_info = 0.0;
double synapses_3_pre_codeobject_profiling_info = 0.0;
double synapses_3_pre_initialise_queue_profiling_info = 0.0;
double synapses_3_pre_push_spikes_profiling_info = 0.0;
double synapses_3_synapses_create_generator_codeobject_profiling_info = 0.0;
double synapses_group_variable_set_conditional_codeobject_profiling_info = 0.0;
double synapses_group_variable_set_conditional_codeobject_1_profiling_info = 0.0;
double synapses_pre_codeobject_profiling_info = 0.0;
double synapses_pre_initialise_queue_profiling_info = 0.0;
double synapses_pre_push_spikes_profiling_info = 0.0;
double synapses_synapses_create_generator_codeobject_profiling_info = 0.0;

}

void _init_arrays()
{
	using namespace brian;

    // Arrays initialized to 0
	_array_defaultclock_dt = new double[1];
    
	for(int i=0; i<1; i++) _array_defaultclock_dt[i] = 0;

	_array_defaultclock_t = new double[1];
    
	for(int i=0; i<1; i++) _array_defaultclock_t[i] = 0;

	_array_defaultclock_timestep = new int64_t[1];
    
	for(int i=0; i<1; i++) _array_defaultclock_timestep[i] = 0;

	_array_neurongroup_1__spikespace = new int32_t[801];
    
	for(int i=0; i<801; i++) _array_neurongroup_1__spikespace[i] = 0;

	_array_neurongroup_1_ge_soma = new double[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_ge_soma[i] = 0;

	_array_neurongroup_1_gi_soma = new double[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_gi_soma[i] = 0;

	_array_neurongroup_1_i = new int32_t[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_i[i] = 0;

	_array_neurongroup_1_lastspike = new double[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_lastspike[i] = 0;

	_array_neurongroup_1_not_refractory = new char[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_not_refractory[i] = 0;

	_array_neurongroup_1_vm = new double[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_vm[i] = 0;

	_array_neurongroup_1_x = new double[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_x[i] = 0;

	_array_neurongroup_1_y = new double[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_y[i] = 0;

	_array_neurongroup__spikespace = new int32_t[3201];
    
	for(int i=0; i<3201; i++) _array_neurongroup__spikespace[i] = 0;

	_array_neurongroup_ge_soma = new double[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_ge_soma[i] = 0;

	_array_neurongroup_gi_soma = new double[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_gi_soma[i] = 0;

	_array_neurongroup_i = new int32_t[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_i[i] = 0;

	_array_neurongroup_lastspike = new double[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_lastspike[i] = 0;

	_array_neurongroup_not_refractory = new char[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_not_refractory[i] = 0;

	_array_neurongroup_vm = new double[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_vm[i] = 0;

	_array_neurongroup_x = new double[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_x[i] = 0;

	_array_neurongroup_y = new double[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_y[i] = 0;

	_array_spikemonitor_1__source_idx = new int32_t[800];
    
	for(int i=0; i<800; i++) _array_spikemonitor_1__source_idx[i] = 0;

	_array_spikemonitor_1_count = new int32_t[800];
    
	for(int i=0; i<800; i++) _array_spikemonitor_1_count[i] = 0;

	_array_spikemonitor_1_N = new int32_t[1];
    
	for(int i=0; i<1; i++) _array_spikemonitor_1_N[i] = 0;

	_array_spikemonitor__source_idx = new int32_t[3200];
    
	for(int i=0; i<3200; i++) _array_spikemonitor__source_idx[i] = 0;

	_array_spikemonitor_count = new int32_t[3200];
    
	for(int i=0; i<3200; i++) _array_spikemonitor_count[i] = 0;

	_array_spikemonitor_N = new int32_t[1];
    
	for(int i=0; i<1; i++) _array_spikemonitor_N[i] = 0;

	_array_synapses_1_N = new int32_t[1];
    
	for(int i=0; i<1; i++) _array_synapses_1_N[i] = 0;

	_array_synapses_2_N = new int32_t[1];
    
	for(int i=0; i<1; i++) _array_synapses_2_N[i] = 0;

	_array_synapses_3_N = new int32_t[1];
    
	for(int i=0; i<1; i++) _array_synapses_3_N[i] = 0;

	_array_synapses_N = new int32_t[1];
    
	for(int i=0; i<1; i++) _array_synapses_N[i] = 0;


	// Arrays initialized to an "arange"
	_array_neurongroup_1_i = new int32_t[800];
    
	for(int i=0; i<800; i++) _array_neurongroup_1_i[i] = 0 + i;

	_array_neurongroup_i = new int32_t[3200];
    
	for(int i=0; i<3200; i++) _array_neurongroup_i[i] = 0 + i;

	_array_spikemonitor_1__source_idx = new int32_t[800];
    
	for(int i=0; i<800; i++) _array_spikemonitor_1__source_idx[i] = 0 + i;

	_array_spikemonitor__source_idx = new int32_t[3200];
    
	for(int i=0; i<3200; i++) _array_spikemonitor__source_idx[i] = 0 + i;


	// static arrays
	_static_array__array_neurongroup_1_vm = new double[800];
	_static_array__array_neurongroup_1_x = new double[800];
	_static_array__array_neurongroup_1_y = new double[800];
	_static_array__array_neurongroup_vm = new double[3200];
	_static_array__array_neurongroup_x = new double[3200];
	_static_array__array_neurongroup_y = new double[3200];

	// Random number generator states
	for (int i=0; i<1; i++)
	    _mersenne_twister_states.push_back(new rk_state());
}

void _load_arrays()
{
	using namespace brian;

	ifstream f_static_array__array_neurongroup_1_vm;
	f_static_array__array_neurongroup_1_vm.open("static_arrays/_static_array__array_neurongroup_1_vm", ios::in | ios::binary);
	if(f_static_array__array_neurongroup_1_vm.is_open())
	{
		f_static_array__array_neurongroup_1_vm.read(reinterpret_cast<char*>(_static_array__array_neurongroup_1_vm), 800*sizeof(double));
	} else
	{
		std::cout << "Error opening static array _static_array__array_neurongroup_1_vm." << endl;
	}
	ifstream f_static_array__array_neurongroup_1_x;
	f_static_array__array_neurongroup_1_x.open("static_arrays/_static_array__array_neurongroup_1_x", ios::in | ios::binary);
	if(f_static_array__array_neurongroup_1_x.is_open())
	{
		f_static_array__array_neurongroup_1_x.read(reinterpret_cast<char*>(_static_array__array_neurongroup_1_x), 800*sizeof(double));
	} else
	{
		std::cout << "Error opening static array _static_array__array_neurongroup_1_x." << endl;
	}
	ifstream f_static_array__array_neurongroup_1_y;
	f_static_array__array_neurongroup_1_y.open("static_arrays/_static_array__array_neurongroup_1_y", ios::in | ios::binary);
	if(f_static_array__array_neurongroup_1_y.is_open())
	{
		f_static_array__array_neurongroup_1_y.read(reinterpret_cast<char*>(_static_array__array_neurongroup_1_y), 800*sizeof(double));
	} else
	{
		std::cout << "Error opening static array _static_array__array_neurongroup_1_y." << endl;
	}
	ifstream f_static_array__array_neurongroup_vm;
	f_static_array__array_neurongroup_vm.open("static_arrays/_static_array__array_neurongroup_vm", ios::in | ios::binary);
	if(f_static_array__array_neurongroup_vm.is_open())
	{
		f_static_array__array_neurongroup_vm.read(reinterpret_cast<char*>(_static_array__array_neurongroup_vm), 3200*sizeof(double));
	} else
	{
		std::cout << "Error opening static array _static_array__array_neurongroup_vm." << endl;
	}
	ifstream f_static_array__array_neurongroup_x;
	f_static_array__array_neurongroup_x.open("static_arrays/_static_array__array_neurongroup_x", ios::in | ios::binary);
	if(f_static_array__array_neurongroup_x.is_open())
	{
		f_static_array__array_neurongroup_x.read(reinterpret_cast<char*>(_static_array__array_neurongroup_x), 3200*sizeof(double));
	} else
	{
		std::cout << "Error opening static array _static_array__array_neurongroup_x." << endl;
	}
	ifstream f_static_array__array_neurongroup_y;
	f_static_array__array_neurongroup_y.open("static_arrays/_static_array__array_neurongroup_y", ios::in | ios::binary);
	if(f_static_array__array_neurongroup_y.is_open())
	{
		f_static_array__array_neurongroup_y.read(reinterpret_cast<char*>(_static_array__array_neurongroup_y), 3200*sizeof(double));
	} else
	{
		std::cout << "Error opening static array _static_array__array_neurongroup_y." << endl;
	}
}

void _write_arrays()
{
	using namespace brian;

	ofstream outfile__array_defaultclock_dt;
	outfile__array_defaultclock_dt.open("results\\_array_defaultclock_dt_-1140024149", ios::binary | ios::out);
	if(outfile__array_defaultclock_dt.is_open())
	{
		outfile__array_defaultclock_dt.write(reinterpret_cast<char*>(_array_defaultclock_dt), 1*sizeof(_array_defaultclock_dt[0]));
		outfile__array_defaultclock_dt.close();
	} else
	{
		std::cout << "Error writing output file for _array_defaultclock_dt." << endl;
	}
	ofstream outfile__array_defaultclock_t;
	outfile__array_defaultclock_t.open("results\\_array_defaultclock_t_1759474182", ios::binary | ios::out);
	if(outfile__array_defaultclock_t.is_open())
	{
		outfile__array_defaultclock_t.write(reinterpret_cast<char*>(_array_defaultclock_t), 1*sizeof(_array_defaultclock_t[0]));
		outfile__array_defaultclock_t.close();
	} else
	{
		std::cout << "Error writing output file for _array_defaultclock_t." << endl;
	}
	ofstream outfile__array_defaultclock_timestep;
	outfile__array_defaultclock_timestep.open("results\\_array_defaultclock_timestep_-1004407120", ios::binary | ios::out);
	if(outfile__array_defaultclock_timestep.is_open())
	{
		outfile__array_defaultclock_timestep.write(reinterpret_cast<char*>(_array_defaultclock_timestep), 1*sizeof(_array_defaultclock_timestep[0]));
		outfile__array_defaultclock_timestep.close();
	} else
	{
		std::cout << "Error writing output file for _array_defaultclock_timestep." << endl;
	}
	ofstream outfile__array_neurongroup_1__spikespace;
	outfile__array_neurongroup_1__spikespace.open("results\\_array_neurongroup_1__spikespace_2142100267", ios::binary | ios::out);
	if(outfile__array_neurongroup_1__spikespace.is_open())
	{
		outfile__array_neurongroup_1__spikespace.write(reinterpret_cast<char*>(_array_neurongroup_1__spikespace), 801*sizeof(_array_neurongroup_1__spikespace[0]));
		outfile__array_neurongroup_1__spikespace.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1__spikespace." << endl;
	}
	ofstream outfile__array_neurongroup_1_ge_soma;
	outfile__array_neurongroup_1_ge_soma.open("results\\_array_neurongroup_1_ge_soma_1606228111", ios::binary | ios::out);
	if(outfile__array_neurongroup_1_ge_soma.is_open())
	{
		outfile__array_neurongroup_1_ge_soma.write(reinterpret_cast<char*>(_array_neurongroup_1_ge_soma), 800*sizeof(_array_neurongroup_1_ge_soma[0]));
		outfile__array_neurongroup_1_ge_soma.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1_ge_soma." << endl;
	}
	ofstream outfile__array_neurongroup_1_gi_soma;
	outfile__array_neurongroup_1_gi_soma.open("results\\_array_neurongroup_1_gi_soma_-790861237", ios::binary | ios::out);
	if(outfile__array_neurongroup_1_gi_soma.is_open())
	{
		outfile__array_neurongroup_1_gi_soma.write(reinterpret_cast<char*>(_array_neurongroup_1_gi_soma), 800*sizeof(_array_neurongroup_1_gi_soma[0]));
		outfile__array_neurongroup_1_gi_soma.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1_gi_soma." << endl;
	}
	ofstream outfile__array_neurongroup_1_i;
	outfile__array_neurongroup_1_i.open("results\\_array_neurongroup_1_i_775089035", ios::binary | ios::out);
	if(outfile__array_neurongroup_1_i.is_open())
	{
		outfile__array_neurongroup_1_i.write(reinterpret_cast<char*>(_array_neurongroup_1_i), 800*sizeof(_array_neurongroup_1_i[0]));
		outfile__array_neurongroup_1_i.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1_i." << endl;
	}
	ofstream outfile__array_neurongroup_1_lastspike;
	outfile__array_neurongroup_1_lastspike.open("results\\_array_neurongroup_1_lastspike_-1039752064", ios::binary | ios::out);
	if(outfile__array_neurongroup_1_lastspike.is_open())
	{
		outfile__array_neurongroup_1_lastspike.write(reinterpret_cast<char*>(_array_neurongroup_1_lastspike), 800*sizeof(_array_neurongroup_1_lastspike[0]));
		outfile__array_neurongroup_1_lastspike.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1_lastspike." << endl;
	}
	ofstream outfile__array_neurongroup_1_not_refractory;
	outfile__array_neurongroup_1_not_refractory.open("results\\_array_neurongroup_1_not_refractory_-1963006162", ios::binary | ios::out);
	if(outfile__array_neurongroup_1_not_refractory.is_open())
	{
		outfile__array_neurongroup_1_not_refractory.write(reinterpret_cast<char*>(_array_neurongroup_1_not_refractory), 800*sizeof(_array_neurongroup_1_not_refractory[0]));
		outfile__array_neurongroup_1_not_refractory.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1_not_refractory." << endl;
	}
	ofstream outfile__array_neurongroup_1_vm;
	outfile__array_neurongroup_1_vm.open("results\\_array_neurongroup_1_vm_78194556", ios::binary | ios::out);
	if(outfile__array_neurongroup_1_vm.is_open())
	{
		outfile__array_neurongroup_1_vm.write(reinterpret_cast<char*>(_array_neurongroup_1_vm), 800*sizeof(_array_neurongroup_1_vm[0]));
		outfile__array_neurongroup_1_vm.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1_vm." << endl;
	}
	ofstream outfile__array_neurongroup_1_x;
	outfile__array_neurongroup_1_x.open("results\\_array_neurongroup_1_x_775089050", ios::binary | ios::out);
	if(outfile__array_neurongroup_1_x.is_open())
	{
		outfile__array_neurongroup_1_x.write(reinterpret_cast<char*>(_array_neurongroup_1_x), 800*sizeof(_array_neurongroup_1_x[0]));
		outfile__array_neurongroup_1_x.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1_x." << endl;
	}
	ofstream outfile__array_neurongroup_1_y;
	outfile__array_neurongroup_1_y.open("results\\_array_neurongroup_1_y_775089051", ios::binary | ios::out);
	if(outfile__array_neurongroup_1_y.is_open())
	{
		outfile__array_neurongroup_1_y.write(reinterpret_cast<char*>(_array_neurongroup_1_y), 800*sizeof(_array_neurongroup_1_y[0]));
		outfile__array_neurongroup_1_y.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_1_y." << endl;
	}
	ofstream outfile__array_neurongroup__spikespace;
	outfile__array_neurongroup__spikespace.open("results\\_array_neurongroup__spikespace_-1758913567", ios::binary | ios::out);
	if(outfile__array_neurongroup__spikespace.is_open())
	{
		outfile__array_neurongroup__spikespace.write(reinterpret_cast<char*>(_array_neurongroup__spikespace), 3201*sizeof(_array_neurongroup__spikespace[0]));
		outfile__array_neurongroup__spikespace.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup__spikespace." << endl;
	}
	ofstream outfile__array_neurongroup_ge_soma;
	outfile__array_neurongroup_ge_soma.open("results\\_array_neurongroup_ge_soma_877507005", ios::binary | ios::out);
	if(outfile__array_neurongroup_ge_soma.is_open())
	{
		outfile__array_neurongroup_ge_soma.write(reinterpret_cast<char*>(_array_neurongroup_ge_soma), 3200*sizeof(_array_neurongroup_ge_soma[0]));
		outfile__array_neurongroup_ge_soma.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_ge_soma." << endl;
	}
	ofstream outfile__array_neurongroup_gi_soma;
	outfile__array_neurongroup_gi_soma.open("results\\_array_neurongroup_gi_soma_812013241", ios::binary | ios::out);
	if(outfile__array_neurongroup_gi_soma.is_open())
	{
		outfile__array_neurongroup_gi_soma.write(reinterpret_cast<char*>(_array_neurongroup_gi_soma), 3200*sizeof(_array_neurongroup_gi_soma[0]));
		outfile__array_neurongroup_gi_soma.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_gi_soma." << endl;
	}
	ofstream outfile__array_neurongroup_i;
	outfile__array_neurongroup_i.open("results\\_array_neurongroup_i_2145055853", ios::binary | ios::out);
	if(outfile__array_neurongroup_i.is_open())
	{
		outfile__array_neurongroup_i.write(reinterpret_cast<char*>(_array_neurongroup_i), 3200*sizeof(_array_neurongroup_i[0]));
		outfile__array_neurongroup_i.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_i." << endl;
	}
	ofstream outfile__array_neurongroup_lastspike;
	outfile__array_neurongroup_lastspike.open("results\\_array_neurongroup_lastspike_1742817534", ios::binary | ios::out);
	if(outfile__array_neurongroup_lastspike.is_open())
	{
		outfile__array_neurongroup_lastspike.write(reinterpret_cast<char*>(_array_neurongroup_lastspike), 3200*sizeof(_array_neurongroup_lastspike[0]));
		outfile__array_neurongroup_lastspike.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_lastspike." << endl;
	}
	ofstream outfile__array_neurongroup_not_refractory;
	outfile__array_neurongroup_not_refractory.open("results\\_array_neurongroup_not_refractory_-803800032", ios::binary | ios::out);
	if(outfile__array_neurongroup_not_refractory.is_open())
	{
		outfile__array_neurongroup_not_refractory.write(reinterpret_cast<char*>(_array_neurongroup_not_refractory), 3200*sizeof(_array_neurongroup_not_refractory[0]));
		outfile__array_neurongroup_not_refractory.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_not_refractory." << endl;
	}
	ofstream outfile__array_neurongroup_vm;
	outfile__array_neurongroup_vm.open("results\\_array_neurongroup_vm_994722506", ios::binary | ios::out);
	if(outfile__array_neurongroup_vm.is_open())
	{
		outfile__array_neurongroup_vm.write(reinterpret_cast<char*>(_array_neurongroup_vm), 3200*sizeof(_array_neurongroup_vm[0]));
		outfile__array_neurongroup_vm.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_vm." << endl;
	}
	ofstream outfile__array_neurongroup_x;
	outfile__array_neurongroup_x.open("results\\_array_neurongroup_x_2145055868", ios::binary | ios::out);
	if(outfile__array_neurongroup_x.is_open())
	{
		outfile__array_neurongroup_x.write(reinterpret_cast<char*>(_array_neurongroup_x), 3200*sizeof(_array_neurongroup_x[0]));
		outfile__array_neurongroup_x.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_x." << endl;
	}
	ofstream outfile__array_neurongroup_y;
	outfile__array_neurongroup_y.open("results\\_array_neurongroup_y_2145055869", ios::binary | ios::out);
	if(outfile__array_neurongroup_y.is_open())
	{
		outfile__array_neurongroup_y.write(reinterpret_cast<char*>(_array_neurongroup_y), 3200*sizeof(_array_neurongroup_y[0]));
		outfile__array_neurongroup_y.close();
	} else
	{
		std::cout << "Error writing output file for _array_neurongroup_y." << endl;
	}
	ofstream outfile__array_spikemonitor_1__source_idx;
	outfile__array_spikemonitor_1__source_idx.open("results\\_array_spikemonitor_1__source_idx_-616616315", ios::binary | ios::out);
	if(outfile__array_spikemonitor_1__source_idx.is_open())
	{
		outfile__array_spikemonitor_1__source_idx.write(reinterpret_cast<char*>(_array_spikemonitor_1__source_idx), 800*sizeof(_array_spikemonitor_1__source_idx[0]));
		outfile__array_spikemonitor_1__source_idx.close();
	} else
	{
		std::cout << "Error writing output file for _array_spikemonitor_1__source_idx." << endl;
	}
	ofstream outfile__array_spikemonitor_1_count;
	outfile__array_spikemonitor_1_count.open("results\\_array_spikemonitor_1_count_580397266", ios::binary | ios::out);
	if(outfile__array_spikemonitor_1_count.is_open())
	{
		outfile__array_spikemonitor_1_count.write(reinterpret_cast<char*>(_array_spikemonitor_1_count), 800*sizeof(_array_spikemonitor_1_count[0]));
		outfile__array_spikemonitor_1_count.close();
	} else
	{
		std::cout << "Error writing output file for _array_spikemonitor_1_count." << endl;
	}
	ofstream outfile__array_spikemonitor_1_N;
	outfile__array_spikemonitor_1_N.open("results\\_array_spikemonitor_1_N_1019764221", ios::binary | ios::out);
	if(outfile__array_spikemonitor_1_N.is_open())
	{
		outfile__array_spikemonitor_1_N.write(reinterpret_cast<char*>(_array_spikemonitor_1_N), 1*sizeof(_array_spikemonitor_1_N[0]));
		outfile__array_spikemonitor_1_N.close();
	} else
	{
		std::cout << "Error writing output file for _array_spikemonitor_1_N." << endl;
	}
	ofstream outfile__array_spikemonitor__source_idx;
	outfile__array_spikemonitor__source_idx.open("results\\_array_spikemonitor__source_idx_-919329681", ios::binary | ios::out);
	if(outfile__array_spikemonitor__source_idx.is_open())
	{
		outfile__array_spikemonitor__source_idx.write(reinterpret_cast<char*>(_array_spikemonitor__source_idx), 3200*sizeof(_array_spikemonitor__source_idx[0]));
		outfile__array_spikemonitor__source_idx.close();
	} else
	{
		std::cout << "Error writing output file for _array_spikemonitor__source_idx." << endl;
	}
	ofstream outfile__array_spikemonitor_count;
	outfile__array_spikemonitor_count.open("results\\_array_spikemonitor_count_-2061135364", ios::binary | ios::out);
	if(outfile__array_spikemonitor_count.is_open())
	{
		outfile__array_spikemonitor_count.write(reinterpret_cast<char*>(_array_spikemonitor_count), 3200*sizeof(_array_spikemonitor_count[0]));
		outfile__array_spikemonitor_count.close();
	} else
	{
		std::cout << "Error writing output file for _array_spikemonitor_count." << endl;
	}
	ofstream outfile__array_spikemonitor_N;
	outfile__array_spikemonitor_N.open("results\\_array_spikemonitor_N_264380251", ios::binary | ios::out);
	if(outfile__array_spikemonitor_N.is_open())
	{
		outfile__array_spikemonitor_N.write(reinterpret_cast<char*>(_array_spikemonitor_N), 1*sizeof(_array_spikemonitor_N[0]));
		outfile__array_spikemonitor_N.close();
	} else
	{
		std::cout << "Error writing output file for _array_spikemonitor_N." << endl;
	}
	ofstream outfile__array_synapses_1_N;
	outfile__array_synapses_1_N.open("results\\_array_synapses_1_N_266374089", ios::binary | ios::out);
	if(outfile__array_synapses_1_N.is_open())
	{
		outfile__array_synapses_1_N.write(reinterpret_cast<char*>(_array_synapses_1_N), 1*sizeof(_array_synapses_1_N[0]));
		outfile__array_synapses_1_N.close();
	} else
	{
		std::cout << "Error writing output file for _array_synapses_1_N." << endl;
	}
	ofstream outfile__array_synapses_2_N;
	outfile__array_synapses_2_N.open("results\\_array_synapses_2_N_-589006250", ios::binary | ios::out);
	if(outfile__array_synapses_2_N.is_open())
	{
		outfile__array_synapses_2_N.write(reinterpret_cast<char*>(_array_synapses_2_N), 1*sizeof(_array_synapses_2_N[0]));
		outfile__array_synapses_2_N.close();
	} else
	{
		std::cout << "Error writing output file for _array_synapses_2_N." << endl;
	}
	ofstream outfile__array_synapses_3_N;
	outfile__array_synapses_3_N.open("results\\_array_synapses_3_N_-1188385825", ios::binary | ios::out);
	if(outfile__array_synapses_3_N.is_open())
	{
		outfile__array_synapses_3_N.write(reinterpret_cast<char*>(_array_synapses_3_N), 1*sizeof(_array_synapses_3_N[0]));
		outfile__array_synapses_3_N.close();
	} else
	{
		std::cout << "Error writing output file for _array_synapses_3_N." << endl;
	}
	ofstream outfile__array_synapses_N;
	outfile__array_synapses_N.open("results\\_array_synapses_N_1362906799", ios::binary | ios::out);
	if(outfile__array_synapses_N.is_open())
	{
		outfile__array_synapses_N.write(reinterpret_cast<char*>(_array_synapses_N), 1*sizeof(_array_synapses_N[0]));
		outfile__array_synapses_N.close();
	} else
	{
		std::cout << "Error writing output file for _array_synapses_N." << endl;
	}

	ofstream outfile__dynamic_array_spikemonitor_1_i;
	outfile__dynamic_array_spikemonitor_1_i.open("results\\_dynamic_array_spikemonitor_1_i_-411468532", ios::binary | ios::out);
	if(outfile__dynamic_array_spikemonitor_1_i.is_open())
	{
        if (! _dynamic_array_spikemonitor_1_i.empty() )
        {
			outfile__dynamic_array_spikemonitor_1_i.write(reinterpret_cast<char*>(&_dynamic_array_spikemonitor_1_i[0]), _dynamic_array_spikemonitor_1_i.size()*sizeof(_dynamic_array_spikemonitor_1_i[0]));
		    outfile__dynamic_array_spikemonitor_1_i.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_spikemonitor_1_i." << endl;
	}
	ofstream outfile__dynamic_array_spikemonitor_1_t;
	outfile__dynamic_array_spikemonitor_1_t.open("results\\_dynamic_array_spikemonitor_1_t_-411468527", ios::binary | ios::out);
	if(outfile__dynamic_array_spikemonitor_1_t.is_open())
	{
        if (! _dynamic_array_spikemonitor_1_t.empty() )
        {
			outfile__dynamic_array_spikemonitor_1_t.write(reinterpret_cast<char*>(&_dynamic_array_spikemonitor_1_t[0]), _dynamic_array_spikemonitor_1_t.size()*sizeof(_dynamic_array_spikemonitor_1_t[0]));
		    outfile__dynamic_array_spikemonitor_1_t.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_spikemonitor_1_t." << endl;
	}
	ofstream outfile__dynamic_array_spikemonitor_i;
	outfile__dynamic_array_spikemonitor_i.open("results\\_dynamic_array_spikemonitor_i_1519461390", ios::binary | ios::out);
	if(outfile__dynamic_array_spikemonitor_i.is_open())
	{
        if (! _dynamic_array_spikemonitor_i.empty() )
        {
			outfile__dynamic_array_spikemonitor_i.write(reinterpret_cast<char*>(&_dynamic_array_spikemonitor_i[0]), _dynamic_array_spikemonitor_i.size()*sizeof(_dynamic_array_spikemonitor_i[0]));
		    outfile__dynamic_array_spikemonitor_i.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_spikemonitor_i." << endl;
	}
	ofstream outfile__dynamic_array_spikemonitor_t;
	outfile__dynamic_array_spikemonitor_t.open("results\\_dynamic_array_spikemonitor_t_1519461395", ios::binary | ios::out);
	if(outfile__dynamic_array_spikemonitor_t.is_open())
	{
        if (! _dynamic_array_spikemonitor_t.empty() )
        {
			outfile__dynamic_array_spikemonitor_t.write(reinterpret_cast<char*>(&_dynamic_array_spikemonitor_t[0]), _dynamic_array_spikemonitor_t.size()*sizeof(_dynamic_array_spikemonitor_t[0]));
		    outfile__dynamic_array_spikemonitor_t.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_spikemonitor_t." << endl;
	}
	ofstream outfile__dynamic_array_synapses_1__synaptic_post;
	outfile__dynamic_array_synapses_1__synaptic_post.open("results\\_dynamic_array_synapses_1__synaptic_post_-963181353", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_1__synaptic_post.is_open())
	{
        if (! _dynamic_array_synapses_1__synaptic_post.empty() )
        {
			outfile__dynamic_array_synapses_1__synaptic_post.write(reinterpret_cast<char*>(&_dynamic_array_synapses_1__synaptic_post[0]), _dynamic_array_synapses_1__synaptic_post.size()*sizeof(_dynamic_array_synapses_1__synaptic_post[0]));
		    outfile__dynamic_array_synapses_1__synaptic_post.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_1__synaptic_post." << endl;
	}
	ofstream outfile__dynamic_array_synapses_1__synaptic_pre;
	outfile__dynamic_array_synapses_1__synaptic_pre.open("results\\_dynamic_array_synapses_1__synaptic_pre_1278332923", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_1__synaptic_pre.is_open())
	{
        if (! _dynamic_array_synapses_1__synaptic_pre.empty() )
        {
			outfile__dynamic_array_synapses_1__synaptic_pre.write(reinterpret_cast<char*>(&_dynamic_array_synapses_1__synaptic_pre[0]), _dynamic_array_synapses_1__synaptic_pre.size()*sizeof(_dynamic_array_synapses_1__synaptic_pre[0]));
		    outfile__dynamic_array_synapses_1__synaptic_pre.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_1__synaptic_pre." << endl;
	}
	ofstream outfile__dynamic_array_synapses_1_delay;
	outfile__dynamic_array_synapses_1_delay.open("results\\_dynamic_array_synapses_1_delay_590499080", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_1_delay.is_open())
	{
        if (! _dynamic_array_synapses_1_delay.empty() )
        {
			outfile__dynamic_array_synapses_1_delay.write(reinterpret_cast<char*>(&_dynamic_array_synapses_1_delay[0]), _dynamic_array_synapses_1_delay.size()*sizeof(_dynamic_array_synapses_1_delay[0]));
		    outfile__dynamic_array_synapses_1_delay.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_1_delay." << endl;
	}
	ofstream outfile__dynamic_array_synapses_1_lastupdate;
	outfile__dynamic_array_synapses_1_lastupdate.open("results\\_dynamic_array_synapses_1_lastupdate_1707784897", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_1_lastupdate.is_open())
	{
        if (! _dynamic_array_synapses_1_lastupdate.empty() )
        {
			outfile__dynamic_array_synapses_1_lastupdate.write(reinterpret_cast<char*>(&_dynamic_array_synapses_1_lastupdate[0]), _dynamic_array_synapses_1_lastupdate.size()*sizeof(_dynamic_array_synapses_1_lastupdate[0]));
		    outfile__dynamic_array_synapses_1_lastupdate.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_1_lastupdate." << endl;
	}
	ofstream outfile__dynamic_array_synapses_1_N_incoming;
	outfile__dynamic_array_synapses_1_N_incoming.open("results\\_dynamic_array_synapses_1_N_incoming_973132123", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_1_N_incoming.is_open())
	{
        if (! _dynamic_array_synapses_1_N_incoming.empty() )
        {
			outfile__dynamic_array_synapses_1_N_incoming.write(reinterpret_cast<char*>(&_dynamic_array_synapses_1_N_incoming[0]), _dynamic_array_synapses_1_N_incoming.size()*sizeof(_dynamic_array_synapses_1_N_incoming[0]));
		    outfile__dynamic_array_synapses_1_N_incoming.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_1_N_incoming." << endl;
	}
	ofstream outfile__dynamic_array_synapses_1_N_outgoing;
	outfile__dynamic_array_synapses_1_N_outgoing.open("results\\_dynamic_array_synapses_1_N_outgoing_1810713537", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_1_N_outgoing.is_open())
	{
        if (! _dynamic_array_synapses_1_N_outgoing.empty() )
        {
			outfile__dynamic_array_synapses_1_N_outgoing.write(reinterpret_cast<char*>(&_dynamic_array_synapses_1_N_outgoing[0]), _dynamic_array_synapses_1_N_outgoing.size()*sizeof(_dynamic_array_synapses_1_N_outgoing[0]));
		    outfile__dynamic_array_synapses_1_N_outgoing.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_1_N_outgoing." << endl;
	}
	ofstream outfile__dynamic_array_synapses_1_wght;
	outfile__dynamic_array_synapses_1_wght.open("results\\_dynamic_array_synapses_1_wght_-703687670", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_1_wght.is_open())
	{
        if (! _dynamic_array_synapses_1_wght.empty() )
        {
			outfile__dynamic_array_synapses_1_wght.write(reinterpret_cast<char*>(&_dynamic_array_synapses_1_wght[0]), _dynamic_array_synapses_1_wght.size()*sizeof(_dynamic_array_synapses_1_wght[0]));
		    outfile__dynamic_array_synapses_1_wght.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_1_wght." << endl;
	}
	ofstream outfile__dynamic_array_synapses_2__synaptic_post;
	outfile__dynamic_array_synapses_2__synaptic_post.open("results\\_dynamic_array_synapses_2__synaptic_post_-1564430042", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_2__synaptic_post.is_open())
	{
        if (! _dynamic_array_synapses_2__synaptic_post.empty() )
        {
			outfile__dynamic_array_synapses_2__synaptic_post.write(reinterpret_cast<char*>(&_dynamic_array_synapses_2__synaptic_post[0]), _dynamic_array_synapses_2__synaptic_post.size()*sizeof(_dynamic_array_synapses_2__synaptic_post[0]));
		    outfile__dynamic_array_synapses_2__synaptic_post.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_2__synaptic_post." << endl;
	}
	ofstream outfile__dynamic_array_synapses_2__synaptic_pre;
	outfile__dynamic_array_synapses_2__synaptic_pre.open("results\\_dynamic_array_synapses_2__synaptic_pre_-1879746540", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_2__synaptic_pre.is_open())
	{
        if (! _dynamic_array_synapses_2__synaptic_pre.empty() )
        {
			outfile__dynamic_array_synapses_2__synaptic_pre.write(reinterpret_cast<char*>(&_dynamic_array_synapses_2__synaptic_pre[0]), _dynamic_array_synapses_2__synaptic_pre.size()*sizeof(_dynamic_array_synapses_2__synaptic_pre[0]));
		    outfile__dynamic_array_synapses_2__synaptic_pre.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_2__synaptic_pre." << endl;
	}
	ofstream outfile__dynamic_array_synapses_2_delay;
	outfile__dynamic_array_synapses_2_delay.open("results\\_dynamic_array_synapses_2_delay_-479552353", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_2_delay.is_open())
	{
        if (! _dynamic_array_synapses_2_delay.empty() )
        {
			outfile__dynamic_array_synapses_2_delay.write(reinterpret_cast<char*>(&_dynamic_array_synapses_2_delay[0]), _dynamic_array_synapses_2_delay.size()*sizeof(_dynamic_array_synapses_2_delay[0]));
		    outfile__dynamic_array_synapses_2_delay.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_2_delay." << endl;
	}
	ofstream outfile__dynamic_array_synapses_2_lastupdate;
	outfile__dynamic_array_synapses_2_lastupdate.open("results\\_dynamic_array_synapses_2_lastupdate_-1470996972", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_2_lastupdate.is_open())
	{
        if (! _dynamic_array_synapses_2_lastupdate.empty() )
        {
			outfile__dynamic_array_synapses_2_lastupdate.write(reinterpret_cast<char*>(&_dynamic_array_synapses_2_lastupdate[0]), _dynamic_array_synapses_2_lastupdate.size()*sizeof(_dynamic_array_synapses_2_lastupdate[0]));
		    outfile__dynamic_array_synapses_2_lastupdate.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_2_lastupdate." << endl;
	}
	ofstream outfile__dynamic_array_synapses_2_N_incoming;
	outfile__dynamic_array_synapses_2_N_incoming.open("results\\_dynamic_array_synapses_2_N_incoming_-1634487590", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_2_N_incoming.is_open())
	{
        if (! _dynamic_array_synapses_2_N_incoming.empty() )
        {
			outfile__dynamic_array_synapses_2_N_incoming.write(reinterpret_cast<char*>(&_dynamic_array_synapses_2_N_incoming[0]), _dynamic_array_synapses_2_N_incoming.size()*sizeof(_dynamic_array_synapses_2_N_incoming[0]));
		    outfile__dynamic_array_synapses_2_N_incoming.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_2_N_incoming." << endl;
	}
	ofstream outfile__dynamic_array_synapses_2_N_outgoing;
	outfile__dynamic_array_synapses_2_N_outgoing.open("results\\_dynamic_array_synapses_2_N_outgoing_975598952", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_2_N_outgoing.is_open())
	{
        if (! _dynamic_array_synapses_2_N_outgoing.empty() )
        {
			outfile__dynamic_array_synapses_2_N_outgoing.write(reinterpret_cast<char*>(&_dynamic_array_synapses_2_N_outgoing[0]), _dynamic_array_synapses_2_N_outgoing.size()*sizeof(_dynamic_array_synapses_2_N_outgoing[0]));
		    outfile__dynamic_array_synapses_2_N_outgoing.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_2_N_outgoing." << endl;
	}
	ofstream outfile__dynamic_array_synapses_2_wght;
	outfile__dynamic_array_synapses_2_wght.open("results\\_dynamic_array_synapses_2_wght_1392099683", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_2_wght.is_open())
	{
        if (! _dynamic_array_synapses_2_wght.empty() )
        {
			outfile__dynamic_array_synapses_2_wght.write(reinterpret_cast<char*>(&_dynamic_array_synapses_2_wght[0]), _dynamic_array_synapses_2_wght.size()*sizeof(_dynamic_array_synapses_2_wght[0]));
		    outfile__dynamic_array_synapses_2_wght.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_2_wght." << endl;
	}
	ofstream outfile__dynamic_array_synapses_3__synaptic_post;
	outfile__dynamic_array_synapses_3__synaptic_post.open("results\\_dynamic_array_synapses_3__synaptic_post_-1633234287", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_3__synaptic_post.is_open())
	{
        if (! _dynamic_array_synapses_3__synaptic_post.empty() )
        {
			outfile__dynamic_array_synapses_3__synaptic_post.write(reinterpret_cast<char*>(&_dynamic_array_synapses_3__synaptic_post[0]), _dynamic_array_synapses_3__synaptic_post.size()*sizeof(_dynamic_array_synapses_3__synaptic_post[0]));
		    outfile__dynamic_array_synapses_3__synaptic_post.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_3__synaptic_post." << endl;
	}
	ofstream outfile__dynamic_array_synapses_3__synaptic_pre;
	outfile__dynamic_array_synapses_3__synaptic_pre.open("results\\_dynamic_array_synapses_3__synaptic_pre_-80833351", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_3__synaptic_pre.is_open())
	{
        if (! _dynamic_array_synapses_3__synaptic_pre.empty() )
        {
			outfile__dynamic_array_synapses_3__synaptic_pre.write(reinterpret_cast<char*>(&_dynamic_array_synapses_3__synaptic_pre[0]), _dynamic_array_synapses_3__synaptic_pre.size()*sizeof(_dynamic_array_synapses_3__synaptic_pre[0]));
		    outfile__dynamic_array_synapses_3__synaptic_pre.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_3__synaptic_pre." << endl;
	}
	ofstream outfile__dynamic_array_synapses_3_delay;
	outfile__dynamic_array_synapses_3_delay.open("results\\_dynamic_array_synapses_3_delay_-259141906", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_3_delay.is_open())
	{
        if (! _dynamic_array_synapses_3_delay.empty() )
        {
			outfile__dynamic_array_synapses_3_delay.write(reinterpret_cast<char*>(&_dynamic_array_synapses_3_delay[0]), _dynamic_array_synapses_3_delay.size()*sizeof(_dynamic_array_synapses_3_delay[0]));
		    outfile__dynamic_array_synapses_3_delay.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_3_delay." << endl;
	}
	ofstream outfile__dynamic_array_synapses_3_lastupdate;
	outfile__dynamic_array_synapses_3_lastupdate.open("results\\_dynamic_array_synapses_3_lastupdate_-288536077", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_3_lastupdate.is_open())
	{
        if (! _dynamic_array_synapses_3_lastupdate.empty() )
        {
			outfile__dynamic_array_synapses_3_lastupdate.write(reinterpret_cast<char*>(&_dynamic_array_synapses_3_lastupdate[0]), _dynamic_array_synapses_3_lastupdate.size()*sizeof(_dynamic_array_synapses_3_lastupdate[0]));
		    outfile__dynamic_array_synapses_3_lastupdate.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_3_lastupdate." << endl;
	}
	ofstream outfile__dynamic_array_synapses_3_N_incoming;
	outfile__dynamic_array_synapses_3_N_incoming.open("results\\_dynamic_array_synapses_3_N_incoming_1687833717", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_3_N_incoming.is_open())
	{
        if (! _dynamic_array_synapses_3_N_incoming.empty() )
        {
			outfile__dynamic_array_synapses_3_N_incoming.write(reinterpret_cast<char*>(&_dynamic_array_synapses_3_N_incoming[0]), _dynamic_array_synapses_3_N_incoming.size()*sizeof(_dynamic_array_synapses_3_N_incoming[0]));
		    outfile__dynamic_array_synapses_3_N_incoming.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_3_N_incoming." << endl;
	}
	ofstream outfile__dynamic_array_synapses_3_N_outgoing;
	outfile__dynamic_array_synapses_3_N_outgoing.open("results\\_dynamic_array_synapses_3_N_outgoing_-631655989", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_3_N_outgoing.is_open())
	{
        if (! _dynamic_array_synapses_3_N_outgoing.empty() )
        {
			outfile__dynamic_array_synapses_3_N_outgoing.write(reinterpret_cast<char*>(&_dynamic_array_synapses_3_N_outgoing[0]), _dynamic_array_synapses_3_N_outgoing.size()*sizeof(_dynamic_array_synapses_3_N_outgoing[0]));
		    outfile__dynamic_array_synapses_3_N_outgoing.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_3_N_outgoing." << endl;
	}
	ofstream outfile__dynamic_array_synapses_3_wght;
	outfile__dynamic_array_synapses_3_wght.open("results\\_dynamic_array_synapses_3_wght_-1417596084", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_3_wght.is_open())
	{
        if (! _dynamic_array_synapses_3_wght.empty() )
        {
			outfile__dynamic_array_synapses_3_wght.write(reinterpret_cast<char*>(&_dynamic_array_synapses_3_wght[0]), _dynamic_array_synapses_3_wght.size()*sizeof(_dynamic_array_synapses_3_wght[0]));
		    outfile__dynamic_array_synapses_3_wght.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_3_wght." << endl;
	}
	ofstream outfile__dynamic_array_synapses__synaptic_post;
	outfile__dynamic_array_synapses__synaptic_post.open("results\\_dynamic_array_synapses__synaptic_post_-2071470647", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses__synaptic_post.is_open())
	{
        if (! _dynamic_array_synapses__synaptic_post.empty() )
        {
			outfile__dynamic_array_synapses__synaptic_post.write(reinterpret_cast<char*>(&_dynamic_array_synapses__synaptic_post[0]), _dynamic_array_synapses__synaptic_post.size()*sizeof(_dynamic_array_synapses__synaptic_post[0]));
		    outfile__dynamic_array_synapses__synaptic_post.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses__synaptic_post." << endl;
	}
	ofstream outfile__dynamic_array_synapses__synaptic_pre;
	outfile__dynamic_array_synapses__synaptic_pre.open("results\\_dynamic_array_synapses__synaptic_pre_1905778921", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses__synaptic_pre.is_open())
	{
        if (! _dynamic_array_synapses__synaptic_pre.empty() )
        {
			outfile__dynamic_array_synapses__synaptic_pre.write(reinterpret_cast<char*>(&_dynamic_array_synapses__synaptic_pre[0]), _dynamic_array_synapses__synaptic_pre.size()*sizeof(_dynamic_array_synapses__synaptic_pre[0]));
		    outfile__dynamic_array_synapses__synaptic_pre.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses__synaptic_pre." << endl;
	}
	ofstream outfile__dynamic_array_synapses_delay;
	outfile__dynamic_array_synapses_delay.open("results\\_dynamic_array_synapses_delay_1821183226", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_delay.is_open())
	{
        if (! _dynamic_array_synapses_delay.empty() )
        {
			outfile__dynamic_array_synapses_delay.write(reinterpret_cast<char*>(&_dynamic_array_synapses_delay[0]), _dynamic_array_synapses_delay.size()*sizeof(_dynamic_array_synapses_delay[0]));
		    outfile__dynamic_array_synapses_delay.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_delay." << endl;
	}
	ofstream outfile__dynamic_array_synapses_lastupdate;
	outfile__dynamic_array_synapses_lastupdate.open("results\\_dynamic_array_synapses_lastupdate_4523959", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_lastupdate.is_open())
	{
        if (! _dynamic_array_synapses_lastupdate.empty() )
        {
			outfile__dynamic_array_synapses_lastupdate.write(reinterpret_cast<char*>(&_dynamic_array_synapses_lastupdate[0]), _dynamic_array_synapses_lastupdate.size()*sizeof(_dynamic_array_synapses_lastupdate[0]));
		    outfile__dynamic_array_synapses_lastupdate.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_lastupdate." << endl;
	}
	ofstream outfile__dynamic_array_synapses_N_incoming;
	outfile__dynamic_array_synapses_N_incoming.open("results\\_dynamic_array_synapses_N_incoming_610014733", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_N_incoming.is_open())
	{
        if (! _dynamic_array_synapses_N_incoming.empty() )
        {
			outfile__dynamic_array_synapses_N_incoming.write(reinterpret_cast<char*>(&_dynamic_array_synapses_N_incoming[0]), _dynamic_array_synapses_N_incoming.size()*sizeof(_dynamic_array_synapses_N_incoming[0]));
		    outfile__dynamic_array_synapses_N_incoming.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_N_incoming." << endl;
	}
	ofstream outfile__dynamic_array_synapses_N_outgoing;
	outfile__dynamic_array_synapses_N_outgoing.open("results\\_dynamic_array_synapses_N_outgoing_-1789242953", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_N_outgoing.is_open())
	{
        if (! _dynamic_array_synapses_N_outgoing.empty() )
        {
			outfile__dynamic_array_synapses_N_outgoing.write(reinterpret_cast<char*>(&_dynamic_array_synapses_N_outgoing[0]), _dynamic_array_synapses_N_outgoing.size()*sizeof(_dynamic_array_synapses_N_outgoing[0]));
		    outfile__dynamic_array_synapses_N_outgoing.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_N_outgoing." << endl;
	}
	ofstream outfile__dynamic_array_synapses_wght;
	outfile__dynamic_array_synapses_wght.open("results\\_dynamic_array_synapses_wght_1600494520", ios::binary | ios::out);
	if(outfile__dynamic_array_synapses_wght.is_open())
	{
        if (! _dynamic_array_synapses_wght.empty() )
        {
			outfile__dynamic_array_synapses_wght.write(reinterpret_cast<char*>(&_dynamic_array_synapses_wght[0]), _dynamic_array_synapses_wght.size()*sizeof(_dynamic_array_synapses_wght[0]));
		    outfile__dynamic_array_synapses_wght.close();
		}
	} else
	{
		std::cout << "Error writing output file for _dynamic_array_synapses_wght." << endl;
	}


	// Write profiling info to disk
	ofstream outfile_profiling_info;
	outfile_profiling_info.open("results/profiling_info.txt", ios::out);
	if(outfile_profiling_info.is_open())
	{
	outfile_profiling_info << "neurongroup_1_resetter_codeobject\t" << neurongroup_1_resetter_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "neurongroup_1_stateupdater_codeobject\t" << neurongroup_1_stateupdater_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "neurongroup_1_thresholder_codeobject\t" << neurongroup_1_thresholder_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "neurongroup_resetter_codeobject\t" << neurongroup_resetter_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "neurongroup_stateupdater_codeobject\t" << neurongroup_stateupdater_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "neurongroup_thresholder_codeobject\t" << neurongroup_thresholder_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "spikemonitor_1_codeobject\t" << spikemonitor_1_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "spikemonitor_codeobject\t" << spikemonitor_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_1_group_variable_set_conditional_codeobject\t" << synapses_1_group_variable_set_conditional_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_1_group_variable_set_conditional_codeobject_1\t" << synapses_1_group_variable_set_conditional_codeobject_1_profiling_info << std::endl;
	outfile_profiling_info << "synapses_1_pre_codeobject\t" << synapses_1_pre_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_1_pre_initialise_queue\t" << synapses_1_pre_initialise_queue_profiling_info << std::endl;
	outfile_profiling_info << "synapses_1_pre_push_spikes\t" << synapses_1_pre_push_spikes_profiling_info << std::endl;
	outfile_profiling_info << "synapses_1_synapses_create_generator_codeobject\t" << synapses_1_synapses_create_generator_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_2_group_variable_set_conditional_codeobject\t" << synapses_2_group_variable_set_conditional_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_2_group_variable_set_conditional_codeobject_1\t" << synapses_2_group_variable_set_conditional_codeobject_1_profiling_info << std::endl;
	outfile_profiling_info << "synapses_2_pre_codeobject\t" << synapses_2_pre_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_2_pre_initialise_queue\t" << synapses_2_pre_initialise_queue_profiling_info << std::endl;
	outfile_profiling_info << "synapses_2_pre_push_spikes\t" << synapses_2_pre_push_spikes_profiling_info << std::endl;
	outfile_profiling_info << "synapses_2_synapses_create_generator_codeobject\t" << synapses_2_synapses_create_generator_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_3_group_variable_set_conditional_codeobject\t" << synapses_3_group_variable_set_conditional_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_3_group_variable_set_conditional_codeobject_1\t" << synapses_3_group_variable_set_conditional_codeobject_1_profiling_info << std::endl;
	outfile_profiling_info << "synapses_3_pre_codeobject\t" << synapses_3_pre_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_3_pre_initialise_queue\t" << synapses_3_pre_initialise_queue_profiling_info << std::endl;
	outfile_profiling_info << "synapses_3_pre_push_spikes\t" << synapses_3_pre_push_spikes_profiling_info << std::endl;
	outfile_profiling_info << "synapses_3_synapses_create_generator_codeobject\t" << synapses_3_synapses_create_generator_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_group_variable_set_conditional_codeobject\t" << synapses_group_variable_set_conditional_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_group_variable_set_conditional_codeobject_1\t" << synapses_group_variable_set_conditional_codeobject_1_profiling_info << std::endl;
	outfile_profiling_info << "synapses_pre_codeobject\t" << synapses_pre_codeobject_profiling_info << std::endl;
	outfile_profiling_info << "synapses_pre_initialise_queue\t" << synapses_pre_initialise_queue_profiling_info << std::endl;
	outfile_profiling_info << "synapses_pre_push_spikes\t" << synapses_pre_push_spikes_profiling_info << std::endl;
	outfile_profiling_info << "synapses_synapses_create_generator_codeobject\t" << synapses_synapses_create_generator_codeobject_profiling_info << std::endl;
	outfile_profiling_info.close();
	} else
	{
	    std::cout << "Error writing profiling info to file." << std::endl;
	}

	// Write last run info to disk
	ofstream outfile_last_run_info;
	outfile_last_run_info.open("results/last_run_info.txt", ios::out);
	if(outfile_last_run_info.is_open())
	{
		outfile_last_run_info << (Network::_last_run_time) << " " << (Network::_last_run_completed_fraction) << std::endl;
		outfile_last_run_info.close();
	} else
	{
	    std::cout << "Error writing last run info to file." << std::endl;
	}
}

void _dealloc_arrays()
{
	using namespace brian;


	// static arrays
	if(_static_array__array_neurongroup_1_vm!=0)
	{
		delete [] _static_array__array_neurongroup_1_vm;
		_static_array__array_neurongroup_1_vm = 0;
	}
	if(_static_array__array_neurongroup_1_x!=0)
	{
		delete [] _static_array__array_neurongroup_1_x;
		_static_array__array_neurongroup_1_x = 0;
	}
	if(_static_array__array_neurongroup_1_y!=0)
	{
		delete [] _static_array__array_neurongroup_1_y;
		_static_array__array_neurongroup_1_y = 0;
	}
	if(_static_array__array_neurongroup_vm!=0)
	{
		delete [] _static_array__array_neurongroup_vm;
		_static_array__array_neurongroup_vm = 0;
	}
	if(_static_array__array_neurongroup_x!=0)
	{
		delete [] _static_array__array_neurongroup_x;
		_static_array__array_neurongroup_x = 0;
	}
	if(_static_array__array_neurongroup_y!=0)
	{
		delete [] _static_array__array_neurongroup_y;
		_static_array__array_neurongroup_y = 0;
	}
}

