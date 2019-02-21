#include "objects.h"
#include "code_objects/synapses_2_synapses_create_generator_codeobject.h"
#include "brianlib/common_math.h"
#include "brianlib/stdint_compat.h"
#include<cmath>
#include<ctime>
#include<iostream>
#include<fstream>
#include "brianlib/stdint_compat.h"
#include "synapses_classes.h"

////// SUPPORT CODE ///////
namespace {
 	
 double _rand(const int _vectorisation_idx) {
     return rk_double(brian::_mersenne_twister_states[0]);
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



void _run_synapses_2_synapses_create_generator_codeobject()
{
	using namespace brian;

    const std::clock_t _start_time = std::clock();

	///// CONSTANTS ///////////
	int32_t* const _array_synapses_2_N_incoming = _dynamic_array_synapses_2_N_incoming.empty()? 0 : &_dynamic_array_synapses_2_N_incoming[0];
const int _numN_incoming = _dynamic_array_synapses_2_N_incoming.size();
int32_t* const _array_synapses_2__synaptic_post = _dynamic_array_synapses_2__synaptic_post.empty()? 0 : &_dynamic_array_synapses_2__synaptic_post[0];
const int _num_synaptic_post = _dynamic_array_synapses_2__synaptic_post.size();
int32_t* const _array_synapses_2__synaptic_pre = _dynamic_array_synapses_2__synaptic_pre.empty()? 0 : &_dynamic_array_synapses_2__synaptic_pre[0];
const int _num_synaptic_pre = _dynamic_array_synapses_2__synaptic_pre.size();
int32_t* const _array_synapses_2_N_outgoing = _dynamic_array_synapses_2_N_outgoing.empty()? 0 : &_dynamic_array_synapses_2_N_outgoing[0];
const int _numN_outgoing = _dynamic_array_synapses_2_N_outgoing.size();
const int _numN = 1;
	///// POINTERS ////////////
 	
 int32_t* __restrict  _ptr_array_synapses_2_N_incoming = _array_synapses_2_N_incoming;
 int32_t* __restrict  _ptr_array_synapses_2__synaptic_post = _array_synapses_2__synaptic_post;
 int32_t* __restrict  _ptr_array_synapses_2__synaptic_pre = _array_synapses_2__synaptic_pre;
 int32_t* __restrict  _ptr_array_synapses_2_N_outgoing = _array_synapses_2_N_outgoing;
 int32_t*   _ptr_array_synapses_2_N = _array_synapses_2_N;


    #include<iostream>


    const int _N_pre = 800;
    const int _N_post = 3200;
    _dynamic_array_synapses_2_N_incoming.resize(_N_post + 0);
    _dynamic_array_synapses_2_N_outgoing.resize(_N_pre + 0);
    int _raw_pre_idx, _raw_post_idx;
    // scalar code
    const int _vectorisation_idx = -1;
        

        

        

        

    for(int _i=0; _i<_N_pre; _i++)
	{
        bool __cond, _cond;
        _raw_pre_idx = _i + 0;
        // Some explanation of this hackery. The problem is that we have multiple code blocks.
        // Each code block is generated independently of the others, and they declare variables
        // at the beginning if necessary (including declaring them as const if their values don't
        // change). However, if two code blocks follow each other in the same C++ scope then
        // that causes a redeclaration error. So we solve it by putting each block inside a
        // pair of braces to create a new scope specific to each code block. However, that brings
        // up another problem: we need the values from these code blocks. I don't have a general
        // solution to this problem, but in the case of this particular template, we know which
        // values we need from them so we simply create outer scoped variables to copy the value
        // into. Later on we have a slightly more complicated problem because the original name
        // _j has to be used, so we create two variables __j, _j at the outer scope, copy
        // _j to __j in the inner scope (using the inner scope version of _j), and then
        // __j to _j in the outer scope (to the outer scope version of _j). This outer scope
        // version of _j will then be used in subsequent blocks.
        long _uiter_low;
        long _uiter_high;
        long _uiter_step;
        double _uiter_p;
        {
                        
            const int32_t _iter_high = 3200;
            const double _iter_p = 0.02;
            const int32_t _iter_step = 1;
            const int32_t _iter_low = 0;

            _uiter_low = _iter_low;
            _uiter_high = _iter_high;
            _uiter_step = _iter_step;
            _uiter_p = _iter_p;
        }
        if(_uiter_p==0) continue;
        const bool _jump_algo = _uiter_p<0.25;
        double _log1p;
        if(_jump_algo)
            _log1p = log(1-_uiter_p);
        else
            _log1p = 1.0; // will be ignored
        const double _pconst = 1.0/log(1-_uiter_p);
        for(int _k=_uiter_low; _k<_uiter_high; _k++)
        {
            if(_jump_algo) {
                const double _r = _rand(_vectorisation_idx);
                if(_r==0.0) break;
                const int _jump = floor(log(_r)*_pconst)*_uiter_step;
                _k += _jump;
                if(_k>=_uiter_high) continue;
            } else {
                if(_rand(_vectorisation_idx)>=_uiter_p) continue;
            }
            long __j, _j, _pre_idx, __pre_idx;
            {
                                
                const int32_t _pre_idx = _raw_pre_idx;
                const int32_t _j = _k;

                __j = _j; // pick up the locally scoped _j and store in __j
                __pre_idx = _pre_idx;
            }
            _j = __j; // make the previously locally scoped _j available
            _pre_idx = __pre_idx;
            _raw_post_idx = _j + 0;
            if(_j<0 || _j>=_N_post)
            {
                cout << "Error: tried to create synapse to neuron j=" << _j << " outside range 0 to " <<
                        _N_post-1 << endl;
                exit(1);
            }
            {
                                
                const int32_t _post_idx = _raw_post_idx;
                const int32_t i = _i;
                const char _cond = i != _k;

                __cond = _cond;
            }
            _cond = __cond;

            if(!_cond) continue;

                        
            const int32_t _post_idx = _raw_post_idx;
            const int32_t _n = 1;


            for (int _repetition=0; _repetition<_n; _repetition++) {
                _dynamic_array_synapses_2_N_outgoing[_pre_idx] += 1;
                _dynamic_array_synapses_2_N_incoming[_post_idx] += 1;
                _dynamic_array_synapses_2__synaptic_pre.push_back(_pre_idx);
                _dynamic_array_synapses_2__synaptic_post.push_back(_post_idx);
			}
		}
	}

	// now we need to resize all registered variables
	const int32_t newsize = _dynamic_array_synapses_2__synaptic_pre.size();
    _dynamic_array_synapses_2__synaptic_post.resize(newsize);
    _dynamic_array_synapses_2__synaptic_pre.resize(newsize);
    _dynamic_array_synapses_2_delay.resize(newsize);
    _dynamic_array_synapses_2_lastupdate.resize(newsize);
    _dynamic_array_synapses_2_wght.resize(newsize);
	// Also update the total number of synapses
	_ptr_array_synapses_2_N[0] = newsize;


    const double _run_time = (double)(std::clock() -_start_time)/CLOCKS_PER_SEC;
    synapses_2_synapses_create_generator_codeobject_profiling_info += _run_time;
}


