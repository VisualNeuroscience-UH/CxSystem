import cortical_system as CX
import os
from brian2  import *
import multiprocessing
import time
import numpy as np


def multi_run (idx, working):
    working.value += 1
    np.random.seed(idx)
    print "################### process %d started ##########################" % idx
    cm = CX.cortical_system(os.path.dirname(os.path.realpath(__file__)) + '/Markram_config_file.csv', device = 'C++', runtime = 1000*ms)
    cm.run()
    working.value -= 1

# Multiprocessing using the Process()
if __name__ == '__main__':
    manager = multiprocessing.Manager()
    jobs = []
    working = manager.Value('i',0)
    trials = 200
    ProcessLimit = 30
    NotDone = 1
    while len(jobs)<trials:
        time.sleep(0.3)
        if working.value < ProcessLimit:
            p = multiprocessing.Process(target=multi_run,args=(len(jobs),working,))
            jobs.append(p)
            p.start()
    for j in jobs:
        j.join()




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