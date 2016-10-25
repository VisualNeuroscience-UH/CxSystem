import matplotlib.pyplot as plt
import scipy.io as spio
from collections import OrderedDict
import numpy as np
import re
import pandas as pd

default_mat_file_path = '/home/shohokka/PycharmProjects/CX_Output/calcium24.mat'

def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict

def _group_name_for_ordering(spikedata):
    corrected_name = re.sub(r'NG(\w{1})_', r'NG0\1_', spikedata[0])
    return str(corrected_name)


# RASTER PLOT
def rasterplot(filename=default_mat_file_path):
    data = loadmat(filename)
    spikedata = data['spikes_all']  # [0] -> neuron indices inside group, [1] -> spike times
    spikedata_ord = OrderedDict(sorted(spikedata.items(), key=_group_name_for_ordering ))  # TODO Order nicely


    fig = plt.figure()
    fig.suptitle(default_mat_file_path)
    for index,group_spikes in enumerate(spikedata_ord.items()[1:], start=1):
        ax = plt.subplot(16,1,index)
        plt.xlim([0, 0.5])
        ylabel = plt.ylabel(group_spikes[0])
        ylabel.set_rotation(0)
        ax.set_yticklabels([])

        try:
            ax.scatter(group_spikes[1][1], group_spikes[1][0], s=0.1)
        except IndexError:
            pass

    plt.show()


# Something completely different...
data = loadmat(default_mat_file_path)
interesting_group = 'NG7_SS_L4'

runtime = data['runtime']
spikedata = data['spikes_all']  # [0] -> neuron indices inside group, [1] -> spike times
spikedata = OrderedDict(sorted(spikedata.items(), key=_group_name_for_ordering))

#bins = np.arange(0.0, runtime+0.1, 0.01)
bins = np.arange(0.0, 0.01, 0.0001)
spikes = spikedata[interesting_group]


binned_spikes = pd.cut(spikes[1], bins)
counts = pd.value_counts(binned_spikes)
counts = counts.reindex(binned_spikes.categories)
counts.plot(kind='bar')
plt.show()
#plt.plot(bins, pd.value_counts(binned_spikes))

