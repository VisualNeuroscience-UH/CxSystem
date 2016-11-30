import cortical_system as CX
import os
from brian2  import *
import datetime

default_runtime = 3000*ms

time_start = datetime.datetime.now()
CM = CX.cortical_system(anatomy_and_system_config = os.path.dirname(os.path.realpath(__file__)) + '/calcium_config_file.csv',
                        physiology_config = os.path.dirname(os.path.realpath(__file__)) + '/Physiological_Parameters.csv')

time_before_run = datetime.datetime.now()
CM.run()
time_end = datetime.datetime.now()

duration_generation = int((time_before_run - time_start).total_seconds())
duration_simulation = int((time_end - time_before_run).total_seconds())
duration_total = int((time_end - time_start).total_seconds())

print 'Duration of network generation: %d min %d s' % (duration_generation//60, duration_generation%60)
print 'Duration of actual simulation: %d min %d s' % (duration_simulation//60, duration_simulation%60)
print 'TOTAL %d min %d s' % (duration_total//60, duration_total%60)
print '=> %d times realtime' % (duration_total*second / default_runtime)
