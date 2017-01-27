from brian2 import *
import matplotlib.pyplot as plt

### PC cell
# Biophysical parameters
# Cm = 1*ufarad*cm**-2
# area_total = 25000 * um**2
# gL = (4.2e-5*siemens*cm**-2) * area_total
# EL = -70*mV
# Ee = 0*mV
# Ei = -75*mV
# DeltaT = 2*mV
# VT = -45*mV
# Vr = -70*mV
# C = Cm * area_total
# tau_e = 3*ms
# tau_i = 8*ms
# refr_time = 3*ms
#
#
# gemean = 30*nS
# gestd = 4*nS
# gimean = 150*nS
# gistd = 10*nS

### BC cell
# Biophysical parameters
C = 64*pF
tau_m = 8*ms
gL = C/tau_m
EL = -70*mV
Ee = 0*mV
Ei = -75*mV
DeltaT = 0*mV # 2*mV
VT = -45*mV
Vr = -70*mV

tau_e = 3*ms
tau_i = 8*ms
refr_time = 3*ms

# Example with fluctuating conductances
gemean = 10*nS
gestd = 0.4*nS
gimean = 40*nS
gistd = 12.5*nS

# Config with no noise
# gemean = 0*nS
# gestd = 0*nS
# gimean = 0*nS
# gistd = 0*nS

defaultclock_dt = 0.1*ms

# Stochastic equation with fluctuating synaptic conductances (set ge/gi mean/std to zero if you don't want stochasticity)
eq_PC_soma = '''
 dvm/dt = ((gL*(EL-vm) + ge * (Ee-vm) + gi * (Ei-vm) + gL * DeltaT * exp((vm-VT) / DeltaT) +I) / C) : volt
 dge/dt = -(ge-gemean)/tau_e + sqrt((2*gestd**2)/tau_e)*xi_1: siemens
 #dgealpha/dt = (ge-gealpha)/tau_e : siemens
 dgi/dt = -(gi-gimean)/tau_i + sqrt((2*gistd**2)/tau_i)*xi_2 : siemens
 #dgialpha/dt = (gi-gialpha)/tau_i : siemens
 I: amp
 '''


# Main
G = NeuronGroup(1,eq_PC_soma, threshold='vm > '+repr(VT), reset = 'vm = '+repr(Vr), refractory = refr_time, method='euler')
G.vm = EL
G.gi = gimean
G.ge = gemean

M = StateMonitor(G, ('vm','ge','gi'), record=True)
M_spikes = SpikeMonitor(G)

### Constant current
run(50 * ms)
G.I = 0*nA
run(1900 * ms)
G.I = 0*nA
run(50 * ms)

### Poisson-noise
# H = PoissonGroup(1, 0*Hz)
# S = Synapses(H,G,on_pre='ge_post += 0.85*nS')
# S.connect(i=0, j=0)
#
# I = PoissonGroup(1,10*Hz)
# S2 = Synapses(I,G,on_pre='gi_post = 0.85*nS')
# S2.connect(i=0,j=0)

### Timed spikes
# times = array([100, 200])*ms
# indices = array([0]*len(times))
# H = SpikeGeneratorGroup(1, indices, times)
# S = Synapses(H,G,on_pre='ge_post += 6*nS')
# S.connect(i=0, j=0)
# run(1000*ms)


plt.subplots(1,3)

### Membrane voltage plot
plt.subplot(1,3,1)
plt.title('$V_m$ with spikes')
plt.plot(M.t/ms, M.vm[0])
plt.plot(M_spikes.t/ms, [0*mV] * len(M_spikes.t), '.')
xlabel('Time (ms)')
ylabel('V_m (V)')
ylim([-0.075, 0.02])

### Conductance plot
plt.subplot(1,3,2)
plt.title('Conductance')
plt.plot(M.t/ms, M.ge[0], label='ge')
plt.plot(M.t/ms, M.gi[0], label='gi')
xlabel('Time (ms)')
ylabel('Conductance (S)')
#ylim([0, 50e-9])
plt.legend()

### ge/gi plot with AP threshold line
plt.subplot(1,3,3)
plt.title('Excitatory vs. inhibitory conductance')

def gi_line(x): return (-x*(Ee-VT) - gL*(EL-VT))/(Ei-VT)

x_values = np.arange(0*nS,50*nS,1*nS)
plt.plot(x_values, [gi_line(x) for x in x_values], label='$dV_m/dt = 0$')

for spike_time in M_spikes.t/defaultclock_dt:
    plt.plot(M.ge[0][spike_time], M.gi[0][spike_time], 'g.')

plt.plot(M.ge[0], M.gi[0], 'y.', alpha=0.02)
plt.axis('equal')
plt.xlabel('ge (S)')
plt.ylabel('gi (S)')
plt.legend()

plt.show()