#include "objects.h"
#include "code_objects/neurongroup_stateupdater_codeobject.h"
#include "brianlib/common_math.h"
#include "brianlib/stdint_compat.h"
#include<cmath>
#include<ctime>
#include<iostream>
#include<fstream>

////// SUPPORT CODE ///////
namespace {
 	
 double _randn(const int _vectorisation_idx) {
     return rk_gauss(brian::_mersenne_twister_states[0]);
 }
 inline int _brian_mod(int ux, int uy)
 {
     const int x = (int)ux;
     const int y = (int)uy;
     return ((x%y)+y)%y;
 }
 inline long _brian_mod(int ux, long uy)
 {
     const long x = (long)ux;
     const long y = (long)uy;
     return ((x%y)+y)%y;
 }
 inline long long _brian_mod(int ux, long long uy)
 {
     const long long x = (long long)ux;
     const long long y = (long long)uy;
     return ((x%y)+y)%y;
 }
 inline float _brian_mod(int ux, float uy)
 {
     const float x = (float)ux;
     const float y = (float)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(int ux, double uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(int ux, long double uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long _brian_mod(long ux, int uy)
 {
     const long x = (long)ux;
     const long y = (long)uy;
     return ((x%y)+y)%y;
 }
 inline long _brian_mod(long ux, long uy)
 {
     const long x = (long)ux;
     const long y = (long)uy;
     return ((x%y)+y)%y;
 }
 inline long long _brian_mod(long ux, long long uy)
 {
     const long long x = (long long)ux;
     const long long y = (long long)uy;
     return ((x%y)+y)%y;
 }
 inline float _brian_mod(long ux, float uy)
 {
     const float x = (float)ux;
     const float y = (float)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(long ux, double uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(long ux, long double uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long long _brian_mod(long long ux, int uy)
 {
     const long long x = (long long)ux;
     const long long y = (long long)uy;
     return ((x%y)+y)%y;
 }
 inline long long _brian_mod(long long ux, long uy)
 {
     const long long x = (long long)ux;
     const long long y = (long long)uy;
     return ((x%y)+y)%y;
 }
 inline long long _brian_mod(long long ux, long long uy)
 {
     const long long x = (long long)ux;
     const long long y = (long long)uy;
     return ((x%y)+y)%y;
 }
 inline float _brian_mod(long long ux, float uy)
 {
     const float x = (float)ux;
     const float y = (float)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(long long ux, double uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(long long ux, long double uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline float _brian_mod(float ux, int uy)
 {
     const float x = (float)ux;
     const float y = (float)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline float _brian_mod(float ux, long uy)
 {
     const float x = (float)ux;
     const float y = (float)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline float _brian_mod(float ux, long long uy)
 {
     const float x = (float)ux;
     const float y = (float)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline float _brian_mod(float ux, float uy)
 {
     const float x = (float)ux;
     const float y = (float)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(float ux, double uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(float ux, long double uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(double ux, int uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(double ux, long uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(double ux, long long uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(double ux, float uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline double _brian_mod(double ux, double uy)
 {
     const double x = (double)ux;
     const double y = (double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(double ux, long double uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(long double ux, int uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(long double ux, long uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(long double ux, long long uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(long double ux, float uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(long double ux, double uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 inline long double _brian_mod(long double ux, long double uy)
 {
     const long double x = (long double)ux;
     const long double y = (long double)uy;
     return fmod(fmod(x, y)+y, y);
 }
 #ifdef _MSC_VER
 #define _brian_pow(x, y) (pow((double)(x), (y)))
 #else
 #define _brian_pow(x, y) (pow((x), (y)))
 #endif

}

////// HASH DEFINES ///////



void _run_neurongroup_stateupdater_codeobject()
{
	using namespace brian;

    const std::clock_t _start_time = std::clock();

	///// CONSTANTS ///////////
	const int _numvm = 3200;
const int _numgi_soma = 3200;
const int _numlastspike = 3200;
const int _numnot_refractory = 3200;
const int _numge_soma = 3200;
const int _numdt = 1;
const int _numt = 1;
	///// POINTERS ////////////
 	
 double* __restrict  _ptr_array_neurongroup_vm = _array_neurongroup_vm;
 double* __restrict  _ptr_array_neurongroup_gi_soma = _array_neurongroup_gi_soma;
 double* __restrict  _ptr_array_neurongroup_lastspike = _array_neurongroup_lastspike;
 char* __restrict  _ptr_array_neurongroup_not_refractory = _array_neurongroup_not_refractory;
 double* __restrict  _ptr_array_neurongroup_ge_soma = _array_neurongroup_ge_soma;
 double*   _ptr_array_defaultclock_dt = _array_defaultclock_dt;
 double*   _ptr_array_defaultclock_t = _array_defaultclock_t;


	//// MAIN CODE ////////////
	// scalar code
	const int _vectorisation_idx = -1;
 	
 const double dt = _ptr_array_defaultclock_dt[0];
 const double _lio_1 = 4.0 * 0.001;
 const double _lio_2 = _brian_pow(dt, 0.5);
 const double _lio_3 = ((0.002 * 4.724999999999999e-10) * exp((- (-0.05)) / 0.002)) / 1.1249999999999998e-11;
 const double _lio_4 = 1.0 / 0.002;
 const double _lio_5 = ((-0.049) * 4.724999999999999e-10) / 1.1249999999999998e-11;
 const double _lio_6 = 0.0 / 1.1249999999999998e-11;
 const double _lio_7 = (-0.075) / 1.1249999999999998e-11;
 const double _lio_8 = 4.724999999999999e-10 / 1.1249999999999998e-11;
 const double _lio_9 = 1.0 / 1.1249999999999998e-11;
 const double _lio_10 = 0.0 * (_brian_pow(0.02380952380952381, -0.5));
 const double _lio_11 = (- dt) / 0.003;
 const double _lio_12 = (- dt) / 0.0083;


	const int _N = 3200;
	
	for(int _idx=0; _idx<_N; _idx++)
	{
	    // vector code
		const int _vectorisation_idx = _idx;
                
        double vm = _ptr_array_neurongroup_vm[_idx];
        double ge_soma = _ptr_array_neurongroup_ge_soma[_idx];
        double gi_soma = _ptr_array_neurongroup_gi_soma[_idx];
        const double t = _ptr_array_defaultclock_t[0];
        const double dt = _ptr_array_defaultclock_dt[0];
        const double lastspike = _ptr_array_neurongroup_lastspike[_idx];
        char not_refractory = _ptr_array_neurongroup_not_refractory[_idx];
        not_refractory = (t - lastspike) > _lio_1;
        const double xi = _lio_2 * _randn(_vectorisation_idx);
        double _vm;
        if(not_refractory)
            _vm = ((dt * ((_lio_5 + (((_lio_3 * exp(_lio_4 * vm)) + (_lio_6 * ge_soma)) + (_lio_7 * gi_soma))) - (((_lio_8 * vm) + (_lio_9 * (ge_soma * vm))) + (_lio_9 * (gi_soma * vm))))) + (_lio_10 * xi)) + vm;
        else 
            _vm = vm;
        const double _ge_soma = (_lio_11 * ge_soma) + ge_soma;
        const double _gi_soma = (_lio_12 * gi_soma) + gi_soma;
        if(not_refractory)
            vm = _vm;
        ge_soma = _ge_soma;
        gi_soma = _gi_soma;
        _ptr_array_neurongroup_ge_soma[_idx] = ge_soma;
        _ptr_array_neurongroup_gi_soma[_idx] = gi_soma;
        _ptr_array_neurongroup_vm[_idx] = vm;
        _ptr_array_neurongroup_not_refractory[_idx] = not_refractory;

	}

    const double _run_time = (double)(std::clock() -_start_time)/CLOCKS_PER_SEC;
    neurongroup_stateupdater_codeobject_profiling_info += _run_time;
}


