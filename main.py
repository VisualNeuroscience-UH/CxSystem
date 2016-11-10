import cortical_system as CX
import os
from brian2  import *
import multiprocessing
import time
import numpy as np


# # for benchmarking :
# def multi_run (idx, working):
#     runtime_idx = (idx / 5)
#     working.value += 1
#     np.random.seed(runtime_idx)
#     print "################### Trial %d started running for %d ms ##########################" % (
#         (idx%5)+1, (1000 + (runtime_idx * 3000)))
#     cm = CX.cortical_system(os.path.dirname(os.path.realpath(__file__)) + '/Markram_config_file.csv', device = 'GeNN', runtime = (1000+(runtime_idx*3000))*ms)
#     cm.run()
#     working.value -= 1
#
# # Multiprocessing using the Process()
# if __name__ == '__main__':
#     manager = multiprocessing.Manager()
#     jobs = []
#     working = manager.Value('i',0)
#     trials = 5 * len(range(1000,22100,3000))
#     ProcessLimit = 1
#     NotDone = 1
#     while len(jobs)<trials:
#         time.sleep(3)
#         if working.value < ProcessLimit:
#             p = multiprocessing.Process(target=multi_run,args=(len(jobs),working,))
#             jobs.append(p)
#             p.start()
#     for j in jobs:
#         j.join()



###
### for 200 trials :
###
def multi_run (idx, working):
    working.value += 1
    np.random.seed(idx)
    print "################### process %d started ##########################" % idx
    cm = CX.cortical_system(os.path.dirname(os.path.realpath(__file__)) + '/Markram_config_file.csv', device = 'Cpp', runtime = 1000*ms)
    cm.run()
    working.value -= 1

# Multiprocessing using the Process()
if __name__ == '__main__':
    manager = multiprocessing.Manager()
    jobs = []
    working = manager.Value('i',0)
    trials = 200
    ProcessLimit = 20
    NotDone = 1
    while len(jobs)<trials:
        time.sleep(1)
        if working.value < ProcessLimit:
            p = multiprocessing.Process(target=multi_run,args=(len(jobs),working,))
            jobs.append(p)
            p.start()
    for j in jobs:
        j.join()