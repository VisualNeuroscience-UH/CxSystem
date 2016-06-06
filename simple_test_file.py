__author__ = 'V_AD'
from brian2 import *
from numpy import *


inputdt=defaultclock.dt
rates = array([10,20,30,40,50]) * Hz
tmp_group = NeuronGroup(5, 'rate : Hz', threshold='rand()<rates*inputdt')
tmp_group.rate = rates
tmp_mon = SpikeMonitor(tmp_group)


run (2000*msecond)

plot(tmp_mon.t,tmp_mon.i,'b.');show()