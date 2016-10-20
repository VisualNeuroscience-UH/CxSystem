import cortical_system as CX
import os
from brian_genn_version  import *
import multiprocessing



def multi_run(_):
    CM = CX.cortical_system (os.path.dirname(os.path.realpath(__file__)) + '/Markram_config_file.csv' ,use_genn=0,runtime=1000*ms)
    CM.run()


# Multiprocessing using the Process()
# if __name__ == '__main__':
    # CX_jobs = []
    # for i in range(10):
    #     p = multiprocessing.Process(target=multi_run,args=(i,))
    #     CX_jobs.append(p)
    #     p.start()


# Multiprocessing using the Pool()
if __name__ == '__main__':
    trials = 200
    pool = multiprocessing.Pool(processes=30)
    pool_output = pool.map(multi_run,list(range(trials)))



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