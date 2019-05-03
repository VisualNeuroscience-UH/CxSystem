#include <stdlib.h>
#include "objects.h"
#include <ctime>
#include <time.h>

#include "run.h"
#include "brianlib/common_math.h"
#include "randomkit.h"

#include "code_objects/neurongroup_1_resetter_codeobject.h"
#include "code_objects/neurongroup_1_stateupdater_codeobject.h"
#include "code_objects/neurongroup_1_thresholder_codeobject.h"
#include "code_objects/neurongroup_resetter_codeobject.h"
#include "code_objects/neurongroup_stateupdater_codeobject.h"
#include "code_objects/neurongroup_thresholder_codeobject.h"
#include "code_objects/spikemonitor_1_codeobject.h"
#include "code_objects/spikemonitor_codeobject.h"
#include "code_objects/synapses_1_group_variable_set_conditional_codeobject.h"
#include "code_objects/synapses_1_group_variable_set_conditional_codeobject_1.h"
#include "code_objects/synapses_1_pre_codeobject.h"
#include "code_objects/synapses_1_pre_initialise_queue.h"
#include "code_objects/synapses_1_pre_push_spikes.h"
#include "code_objects/synapses_1_synapses_create_generator_codeobject.h"
#include "code_objects/synapses_2_group_variable_set_conditional_codeobject.h"
#include "code_objects/synapses_2_group_variable_set_conditional_codeobject_1.h"
#include "code_objects/synapses_2_pre_codeobject.h"
#include "code_objects/synapses_2_pre_initialise_queue.h"
#include "code_objects/synapses_2_pre_push_spikes.h"
#include "code_objects/synapses_2_synapses_create_generator_codeobject.h"
#include "code_objects/synapses_3_group_variable_set_conditional_codeobject.h"
#include "code_objects/synapses_3_group_variable_set_conditional_codeobject_1.h"
#include "code_objects/synapses_3_pre_codeobject.h"
#include "code_objects/synapses_3_pre_initialise_queue.h"
#include "code_objects/synapses_3_pre_push_spikes.h"
#include "code_objects/synapses_3_synapses_create_generator_codeobject.h"
#include "code_objects/synapses_group_variable_set_conditional_codeobject.h"
#include "code_objects/synapses_group_variable_set_conditional_codeobject_1.h"
#include "code_objects/synapses_pre_codeobject.h"
#include "code_objects/synapses_pre_initialise_queue.h"
#include "code_objects/synapses_pre_push_spikes.h"
#include "code_objects/synapses_synapses_create_generator_codeobject.h"


#include <iostream>
#include <fstream>


        void report_progress(const double elapsed, const double completed, const double start, const double duration)
        {
            if (completed == 0.0)
            {
                std::cout << "Starting simulation at t=" << start << " s for duration " << duration << " s";
            } else
            {
                std::cout << completed*duration << " s (" << (int)(completed*100.) << "%) simulated in " << elapsed << " s";
                if (completed < 1.0)
                {
                    const int remaining = (int)((1-completed)/completed*elapsed+0.5);
                    std::cout << ", estimated " << remaining << " s remaining.";
                }
            }

            std::cout << std::endl << std::flush;
        }
        


int main(int argc, char **argv)
{

	brian_start();

	{
		using namespace brian;

		
                
        _array_defaultclock_dt[0] = 0.0001;
        _array_defaultclock_dt[0] = 0.0001;
        _array_defaultclock_dt[0] = 0.0001;
        
                        
                        for(int i=0; i<_num__array_neurongroup_lastspike; i++)
                        {
                            _array_neurongroup_lastspike[i] = - INFINITY;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_not_refractory; i++)
                        {
                            _array_neurongroup_not_refractory[i] = true;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_x; i++)
                        {
                            _array_neurongroup_x[i] = _static_array__array_neurongroup_x[i];
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_y; i++)
                        {
                            _array_neurongroup_y[i] = _static_array__array_neurongroup_y[i];
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_vm; i++)
                        {
                            _array_neurongroup_vm[i] = _static_array__array_neurongroup_vm[i];
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_ge_soma; i++)
                        {
                            _array_neurongroup_ge_soma[i] = 0;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_gi_soma; i++)
                        {
                            _array_neurongroup_gi_soma[i] = 0;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_1_lastspike; i++)
                        {
                            _array_neurongroup_1_lastspike[i] = - INFINITY;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_1_not_refractory; i++)
                        {
                            _array_neurongroup_1_not_refractory[i] = true;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_1_x; i++)
                        {
                            _array_neurongroup_1_x[i] = _static_array__array_neurongroup_1_x[i];
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_1_y; i++)
                        {
                            _array_neurongroup_1_y[i] = _static_array__array_neurongroup_1_y[i];
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_1_vm; i++)
                        {
                            _array_neurongroup_1_vm[i] = _static_array__array_neurongroup_1_vm[i];
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_1_ge_soma; i++)
                        {
                            _array_neurongroup_1_ge_soma[i] = 0;
                        }
                        
        
                        
                        for(int i=0; i<_num__array_neurongroup_1_gi_soma; i++)
                        {
                            _array_neurongroup_1_gi_soma[i] = 0;
                        }
                        
        _run_synapses_synapses_create_generator_codeobject();
        _run_synapses_group_variable_set_conditional_codeobject();
        _run_synapses_group_variable_set_conditional_codeobject_1();
        _run_synapses_1_synapses_create_generator_codeobject();
        _run_synapses_1_group_variable_set_conditional_codeobject();
        _run_synapses_1_group_variable_set_conditional_codeobject_1();
        _run_synapses_2_synapses_create_generator_codeobject();
        _run_synapses_2_group_variable_set_conditional_codeobject();
        _run_synapses_2_group_variable_set_conditional_codeobject_1();
        _run_synapses_3_synapses_create_generator_codeobject();
        _run_synapses_3_group_variable_set_conditional_codeobject();
        _run_synapses_3_group_variable_set_conditional_codeobject_1();
        _array_defaultclock_timestep[0] = 0L;
        _array_defaultclock_t[0] = 0.0;
        _run_synapses_1_pre_initialise_queue();
        _run_synapses_2_pre_initialise_queue();
        _run_synapses_3_pre_initialise_queue();
        _run_synapses_pre_initialise_queue();
        magicnetwork.clear();
        magicnetwork.add(&defaultclock, _run_neurongroup_1_stateupdater_codeobject);
        magicnetwork.add(&defaultclock, _run_neurongroup_stateupdater_codeobject);
        magicnetwork.add(&defaultclock, _run_neurongroup_1_thresholder_codeobject);
        magicnetwork.add(&defaultclock, _run_neurongroup_thresholder_codeobject);
        magicnetwork.add(&defaultclock, _run_spikemonitor_codeobject);
        magicnetwork.add(&defaultclock, _run_spikemonitor_1_codeobject);
        magicnetwork.add(&defaultclock, _run_synapses_1_pre_push_spikes);
        magicnetwork.add(&defaultclock, _run_synapses_1_pre_codeobject);
        magicnetwork.add(&defaultclock, _run_synapses_2_pre_push_spikes);
        magicnetwork.add(&defaultclock, _run_synapses_2_pre_codeobject);
        magicnetwork.add(&defaultclock, _run_synapses_3_pre_push_spikes);
        magicnetwork.add(&defaultclock, _run_synapses_3_pre_codeobject);
        magicnetwork.add(&defaultclock, _run_synapses_pre_push_spikes);
        magicnetwork.add(&defaultclock, _run_synapses_pre_codeobject);
        magicnetwork.add(&defaultclock, _run_neurongroup_1_resetter_codeobject);
        magicnetwork.add(&defaultclock, _run_neurongroup_resetter_codeobject);
        magicnetwork.run(1.0, report_progress, 10.0);
        #ifdef DEBUG
        _debugmsg_synapses_pre_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_synapses_2_pre_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_synapses_3_pre_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_spikemonitor_1_codeobject();
        #endif
        
        #ifdef DEBUG
        _debugmsg_synapses_1_pre_codeobject();
        #endif

	}

	brian_end();

	return 0;
}