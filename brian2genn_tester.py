from brian2 import *
import brian2genn

# set_device('genn')
#set_device('cpp_standalone')

eqs = '''
dgeX_a2/dt = -geX_a2/tau_eX : siemens
dgeX_a0/dt = -geX_a0/tau_eX : siemens
dgeX_a1/dt = -geX_a1/tau_eX : siemens
Idendr_basal = 10.0*nsiemens*(vm - vm_basal) : amp
dvm/dt = 0.0888888888888889*(236.25*DeltaT*psiemens*exp((-VT + vm)/DeltaT) + Idendr_soma + gealphaX_soma*(Ee - vm) + gealpha_soma*(Ee - vm) + gialpha_soma*(Ei - vm) + 236.25*psiemens*(EL - vm))/pfarad : volt (unless refractory)
dvm_a0/dt = 0.0133333333333333*(Idendr_a0 + gealphaX_a0*(Ee - vm_a0) + gealpha_a0*(Ee - vm_a0) + gialpha_a0*(Ei - vm_a0) + 1.575*nsiemens*(EL - vm_a0))/pfarad : volt
dvm_a1/dt = 0.0888888888888889*(Idendr_a1 + gealphaX_a1*(Ee - vm_a1) + gealpha_a1*(Ee - vm_a1) + gialpha_a1*(Ei - vm_a1) + 236.25*psiemens*(EL - vm_a1))/pfarad : volt
dvm_a2/dt = 0.0177777777777778*(Idendr_a2 + gealphaX_a2*(Ee - vm_a2) + gealpha_a2*(Ee - vm_a2) + gialpha_a2*(Ei - vm_a2) + 1.18125*nsiemens*(EL - vm_a2))/pfarad : volt
dgi_soma/dt = -gi_soma/tau_i : siemens
Idendr_a1 = 10.0*nsiemens*(vm_a0 - vm_a1) + 12.5*nsiemens*(-vm_a1 + vm_a2) : amp
Idendr_a0 = 12.5*nsiemens*(vm - vm_a0) + 6.66666667*nsiemens*(-vm_a0 + vm_a1) : amp
Idendr_a2 = 5.0*nsiemens*(vm_a1 - vm_a2) : amp
dgealphaX_basal/dt = (geX_basal - gealphaX_basal)/tau_eX : siemens
dgealpha_basal/dt = (ge_basal - gealpha_basal)/tau_e : siemens
dgealpha_a2/dt = (ge_a2 - gealpha_a2)/tau_e : siemens
dgealpha_a0/dt = (ge_a0 - gealpha_a0)/tau_e : siemens
dgealpha_a1/dt = (ge_a1 - gealpha_a1)/tau_e : siemens
dgialpha_soma/dt = (gi_soma - gialpha_soma)/tau_i : siemens
dgi_a1/dt = -gi_a1/tau_i : siemens
dgi_a0/dt = -gi_a0/tau_i : siemens
dgi_a2/dt = -gi_a2/tau_i : siemens
dgialpha_basal/dt = (gi_basal - gialpha_basal)/tau_i : siemens
dgealpha_soma/dt = (ge_soma - gealpha_soma)/tau_e : siemens
dge_soma/dt = -ge_soma/tau_e : siemens
dgeX_basal/dt = -geX_basal/tau_eX : siemens
dgialpha_a2/dt = (gi_a2 - gialpha_a2)/tau_i : siemens
dgialpha_a0/dt = (gi_a0 - gialpha_a0)/tau_i : siemens
dgialpha_a1/dt = (gi_a1 - gialpha_a1)/tau_i : siemens
dgealphaX_soma/dt = (geX_soma - gealphaX_soma)/tau_eX : siemens
dvm_basal/dt = 0.0133333333333333*(Idendr_basal + gealphaX_basal*(Ee - vm_basal) + gealpha_basal*(Ee - vm_basal) + gialpha_basal*(Ei - vm_basal) + 1.575*nsiemens*(EL - vm_basal))/pfarad : volt
dgi_basal/dt = -gi_basal/tau_i : siemens
dgeX_soma/dt = -geX_soma/tau_eX : siemens
dge_basal/dt = -ge_basal/tau_e : siemens
dge_a1/dt = -ge_a1/tau_e : siemens
dge_a0/dt = -ge_a0/tau_e : siemens
dge_a2/dt = -ge_a2/tau_e : siemens
dgealphaX_a2/dt = (geX_a2 - gealphaX_a2)/tau_eX : siemens
dgealphaX_a1/dt = (geX_a1 - gealphaX_a1)/tau_eX : siemens
dgealphaX_a0/dt = (geX_a0 - gealphaX_a0)/tau_eX : siemens
Idendr_soma = 12.5*nsiemens*(-vm + vm_a0) + 10.0*nsiemens*(-vm + vm_basal) : amp
'''
names = {'C': array([ 75.  ,  11.25,  56.25,  56.25,  75.  ]) * pfarad,
 'DeltaT': 2. * mvolt,
 'EL': -70.11 * mvolt,
 'Ed': -70.11 * mvolt,
 'Ee': 0. * volt,
 'Ei': -75. * mvolt,
 'Ra': array([ 100.,   80.,  150.,  150.,  200.]) * Mohm,
 'VT': -41.61 * mvolt,
 'V_res': -70.11 * mvolt,
 'Vcut': -25. * mvolt,
 'Vr': -70.11 * mvolt,
 'gL': array([ 1.575  ,  0.23625,  1.18125,  1.18125,  1.575  ]) * nsiemens,
 'tau_e': 1.7 * msecond,
 'tau_eX': 1.7 * msecond,
 'tau_i': 8.3 * msecond}


G_group = NeuronGroup(10, model = eqs,threshold='vm>Vcut', reset='vm=V_res', refractory = '4 * ms', namespace= names)
H_group = NeuronGroup(15, model = eqs,threshold='vm>Vcut', reset='vm=V_res', refractory = '4 * ms', namespace= names)

eq = '''wght : siemens
            dapre/dt = -apre/taupre : siemens (event-driven)
            dapost/dt = -apost/taupost : siemens (event-driven)'''
pre = '''
ge_a1_post+=wght
apre += Apre * wght0 * Cp
wght = clip(wght + apost, 0, wght_max)
'''
post = '''
apost += Apost * wght * Cd
wght = clip(wght + apre, 0, wght_max)
'''
syn_names = {'Apost': -0.215,
 'Apre': 0.2,
 'Cd': 0.3,
 'Cp': 0.1,
 'taupost': 124.7 * msecond,
 'taupre': 5.4 * msecond,
 'wght0': 5.832 * nsiemens,
 'wght_max': 87.48 * nsiemens}
# S = Synapses(G, H, model= eq,pre = pre, post=post,namespace=syn_names)
# S.connect(4,5)

indices = array([0, 1, 2])
times = array([1, 2, 3])*ms
# Ge = SpikeGeneratorGroup(3, indices, times)
# forward = Synapses(Ge,G,  connect='i==j')
# s_mon_b = StateMonitor(G_group,'vm_basal',record = 0)
# s_mon = StateMonitor(G_group,'vm',record=0)
# s_mon0 = StateMonitor(G_group,'vm_a0',record=0)
# s_mon1 = StateMonitor(G_group,'vm_a1',record=0)
# s_mon2 = StateMonitor(G_group,'vm_a2',record=0)


# run(101*ms)
# device.build(directory='tester',
#             compile=True,
#              run=True,
#              use_GPU=True)
#
# f, axarr = plt.subplots(5, sharex=True)
# axarr[0].plot(s_mon_b.t / ms, s_mon_b.vm_basal[0])
# axarr[1].plot(s_mon.t / ms, s_mon.vm[0])
# axarr[2].plot(s_mon0.t / ms, s_mon0.vm_a0[0])
# axarr[3].plot(s_mon1.t / ms, s_mon1.vm_a1[0])
# axarr[4].plot(s_mon2.t / ms, s_mon2.vm_a2[0])
# # plot(s_mon2.t / ms, s_mon2.i, '.k')
# # xlabel('Time (ms)')
# # ylabel('Neuron index')
# # figure()
# # plot(s_mon3.t / ms, s_mon3.i, '.k')
# # xlabel('Time (ms)')
# # ylabel('Neuron index')
#
# show()