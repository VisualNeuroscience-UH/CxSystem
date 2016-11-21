import numpy as np
import matplotlib.pyplot as plt
import pickle
import zlib
import os
from brian2 import *

time_for_visualization=np.array([0,0.09]) +17
time_for_visualization = time_for_visualization + 0.0001 # To accept 0 as starting point. Rounding error for the end.
dt = 0.01 * ms
plot_dt = 0.1 * ms


# data_file_name = '../CX_OUTPUT/CX_Output_20161108_11000084_Python_1000ms.gz'
directory = '/opt/Laskenta/Output/CX_Output'
data_file_name = max([os.path.join(directory,files) for files in os.listdir(directory)], key=os.path.getmtime)
neuron_groups = ['NG0_relay_video', 'NG1_PC_L4toL2', 'NG3_BC_L4', 'NG2_PC_L2toL1', 'NG4_BC_L2']


with open(data_file_name, 'rb') as compressed_data_file:
    pickled_data = zlib.decompress(compressed_data_file.read())
    data_dictionary = pickle.loads(pickled_data)

positions = data_dictionary['positions_all']
spikes_all = data_dictionary['spikes_all']
vm_all = data_dictionary['vm_all']

plt.figure()

for plot_index, neuron_group in enumerate(neuron_groups):

    N_columns = 3
    plt.subplot(len(neuron_groups), N_columns, plot_index * N_columns + 1)
    plt.plot(np.real(positions['w_coord'][neuron_group]), np.imag(positions['w_coord'][neuron_group]), '.')
    plt.title('%s positions' % neuron_group)

    spikes=spikes_all[neuron_group]
    plt.subplot(len(neuron_groups), N_columns, plot_index * N_columns + 2)
    # plt.plot(spikes[1][::100],spikes[0][::100], '.k')
    plt.plot(spikes[1],spikes[0], '.k')
    plt.xlim([time_for_visualization[0],time_for_visualization[1]])
    plt.title('%s spikes' % neuron_group)

    if neuron_group in vm_all.keys():
        membrane_voltages = vm_all[neuron_group]
        plt.subplot(len(neuron_groups), N_columns, plot_index * N_columns + 3)
        N_time_points = len(membrane_voltages[0])


        data_indices_for_plot = np.array([time_for_visualization[0] * (1 * second) / dt, time_for_visualization[1]  * (1 * second) / dt], dtype=int)
        subsample_step = int(plot_dt / dt)
        subsampled_data_epoch_for_plot = membrane_voltages[:,data_indices_for_plot[0]:data_indices_for_plot[1]:subsample_step]
        time_vector = np.arange(time_for_visualization[0],time_for_visualization[1], plot_dt / (1 * second))
        plt.plot(time_vector,subsampled_data_epoch_for_plot.T, '-')

        plt.title('%s vm' % neuron_group)

plt.show()
