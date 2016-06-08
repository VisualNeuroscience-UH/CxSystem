# __author__ = 'V_AD'
# from brian2 import *
# from numpy import *
#
#
# inputdt=defaultclock.dt
# rates = array([10,20,30,40,50]) * Hz
# tmp_group = NeuronGroup(5, 'rate : Hz', threshold='rand()<rates*inputdt')
# tmp_group.rate = rates
# tmp_mon = SpikeMonitor(tmp_group)
#
#
# run (2000*msecond)
#
# plot(tmp_mon.t,tmp_mon.i,'b.');show()


from brian2 import *
import time

# BrianLogger.log_level_debug()
class creator():
    def __init__(self):
        print "hi"
    def create(self):

        taum = 20 * ms
        taue = 5 * ms
        taui = 10 * ms
        Vt = -50 * mV
        Vr = -60 * mV
        El = -49 * mV

        eqs = '''
        dv/dt  = (ge+gi-(v-El))/taum : volt (unless refractory)
        dge/dt = -ge/taue : volt (unless refractory)
        dgi/dt = -gi/taui : volt (unless refractory)
        '''

        P = NeuronGroup(4000, eqs, threshold='v>Vt', reset='v=Vr', refractory=5 * ms)
        P.v = Vr
        P.ge = 0 * mV
        P.gi = 0 * mV

        we = (60 * 0.27 / 10) * mV # excitatory synaptic weight (voltage)
        wi = (-20 * 4.5 / 10) * mV # inhibitory synaptic weight
        Ce = Synapses(P, P, 'w:1', pre='ge += we')
        Ci = Synapses(P, P, 'w:1', pre='gi += wi')
        Ce.connect('i<3200', p=0.02)
        Ci.connect('i>=3200', p=0.02)
        P.v = Vr + rand(len(P)) * (Vt - Vr)
        globals().update({'P':P})
q = creator()
q.create()
s_mon = SpikeMonitor(P)
run(1 * second)
plot(s_mon.t/ms, s_mon.i, '.k')
xlabel('Time (ms)')
ylabel('Neuron index')
show()
