from brian2 import *
import matplotlib.pyplot as plt

### PC cell
# Biophysical parameters
Cm = 1*ufarad*cm**-2
area_total = 25000 * 0.75 * um**2
gL = (4.2e-5*siemens*cm**-2) * area_total
EL = -70*mV
Ee = 0*mV
Ei = -75*mV
DeltaT = 2*mV
VT = 45*mV
Vr = -70*mV
C = Cm * area_total
tau_e = 3*ms
tau_i = 8*ms


gemean = 30*nS
gestd = 4*nS
gimean = 150*nS
gistd = 10*nS

# Stochastic equation with fluctuating synaptic conductances
eq_PC_soma = '''
 dvm/dt = ((gL*(EL-vm) + gealpha * (Ee-vm) + gialpha * (Ei-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) +I) / C) : volt
 dge/dt = -(ge-gemean)/tau_e + sqrt((2*gestd**2)/tau_e)*xi_1: siemens
 dgealpha/dt = (ge-gealpha)/tau_e : siemens
 dgi/dt = -(gi-gimean)/tau_i + sqrt((2*gistd**2)/tau_i)*xi_2 : siemens
 dgialpha/dt = (gi-gialpha)/tau_i : siemens
 I: amp
 '''

# # Non-stochastic equation
# eq_PC_soma = '''
#  dvm/dt = ((gL*(EL-vm) + gealpha * (Ee-vm) + gialpha * (Ei-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) + I) / C) : volt
#  dge/dt = -ge/tau_e : siemens
#  dgealpha/dt = (ge-gealpha)/tau_e : siemens
#  dgi/dt = -gi/tau_i : siemens
#  dgialpha/dt = (gi-gialpha)/tau_i : siemens
#  I: amp
#  '''


# Main


G = NeuronGroup(1,eq_PC_soma, threshold='vm > -45*mV', reset = 'vm = -70*mV', refractory = 3*ms, method='euler')
G.vm = EL

M = StateMonitor(G, ('vm','ge','gi'), record=True)


# times = array([100, 200])*ms
# indices = array([0]*len(times))
# H = SpikeGeneratorGroup(1, indices, times)


H = PoissonGroup(1, 20*Hz)
S = Synapses(H,G,on_pre='ge_post += 300*nS')
S.connect(i=0, j=0)
run(1000*ms)

# run(100 * ms)
# G.I = 0*nA
# run(300 * ms)
# G.I = 0.5*nA
# run(100 * ms)

plt.plot(M.t/ms, M.vm[0])
# plt.plot(M.t/ms, M.ge[0])
# plt.plot(M.t/ms, M.gi[0])
xlabel('Time (ms)')
ylabel('vm')
ylim([-0.075, 0.02])
plt.show()