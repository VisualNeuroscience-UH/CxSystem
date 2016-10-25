import cortical_system as CX
import os
from brian_genn_version  import *
import datetime

default_runtime = 500*ms

#CM = CX.cortical_system (os.path.dirname(os.path.realpath(__file__)) + '/pandas_playground/generated_config_file_henri.csv',
#                         use_genn=0,runtime=500*ms )
time_start = datetime.datetime.now()
CM = CX.cortical_system (os.path.dirname(os.path.realpath(__file__)) + '/Markram_config_file.csv',
                         use_genn=0,runtime=default_runtime )

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


################ Draw Everything

# for group in CM.monitor_name_bank:
#     mon_num = len(CM.monitor_name_bank[group])
#     exec "f, axarr = plt.subplots(%d, sharex=True)" % mon_num
#     for item_idx, item in enumerate(CM.monitor_name_bank[group]):
#         if 'SpMon' in item:
#             if len(CM.monitor_name_bank[group]) == 1:
#                 exec "axarr.plot(%s.t/ms,%s.i,'.k')" % (item, item);
#                 exec "axarr.set_title('%s')" % (item);
#             else:
#                 exec "axarr[%d].plot(%s.t/ms,%s.i,'.k')" % (item_idx, item, item)
#                 exec "axarr[%d].set_title('%s')" % (item_idx, item)
#         elif 'StMon' in item:
#             underscore = item.index('__')
#             variable = item[underscore + 2:]
#             exec 'y_num=len(%s.%s)' % (item, variable)
#             try:
#                 exec "CM.multi_y_plotter(axarr[%d] , y_num , '%s',%s , '%s')" % (item_idx, variable, item, item)
#             except:
#                 exec "CM.multi_y_plotter(axarr , y_num , '%s',%s , '%s')" % (variable, item, item)
# show()
