import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
import scipy.io as spio
from numpy import *
import pylab as pl
from matplotlib import colors
from sympy.ntheory.factor_ import smoothness
import random as rnd
import operator
import ntpath
import os
import matplotlib.gridspec as gridspec
from scipy.sparse import csr_matrix
import numpy as np
import copy
import sys

default_mat_file_path = '/home/shohokka/PycharmProjects/CX_Output/calcium24.mat'
save_flag = 1


def _status_printer(str):
    #cleaner = ' ' * 100
    #print '\r' + cleaner + '\r' + str,
    print str

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


def nD_list_creator(*args,**kwargs):
    if len(args)>1:
        return [nD_list_creator(*args[1:],obj = kwargs['obj']) for _ in range(args[0])]
    else:
        return [copy.deepcopy(kwargs['obj']) for _ in range(args[0])]


def spike_to_fram(groups,spikes,X_axis,Y_axis,w_coord,axis_precision,smoothness=15,d_t = 0.001) :
    if smoothness%2!=1 :
        smoothness+=1
    t_min = 0
    t_max = 0
    for group in groups:
        try:
            spikes_ts_tmp = spikes[group][1]
        except:
            continue
        # min_temp = min(spikes_ts_tmp)
        # t_min = t_min if t_min < min_temp else min_temp
        try:
            max_temp = max(spikes_ts_tmp)
        except TypeError:
            max_temp = spikes_ts_tmp
        t_max = t_max if t_max > max_temp else max_temp
    ts = [round(t,int(abs(log10(d_t)))) for t in arange(t_min, t_max+d_t, d_t)]
    number_of_frames = len(ts)
    # all_frames = zeros([6,number_of_frames * smoothness, size(X_axis), size(Y_axis), 4])
    frame = csr_matrix((size(X_axis), size(Y_axis)),dtype=np.float32)
    all_frames = nD_list_creator(6,number_of_frames,3,obj=frame)
    # all_frames = nD_list_creator(6, 60, 3, obj=frame)
    number_of_groups = len(groups)

    ############ BUILDING UP THE COLORS
    # colors_ = colors.ColorConverter.colors.values()
    # del colors_[5]
    # del colors_[2]
    # colors_.extend([(0.3405586529938008, 0.77, 0.19037723714226007),(0.76405586529938008, 1, 0.19037723714226007),
    #                 (0.2,0.6,0.76),(0.1,0.8,0.86),(0.44,0.78,0.4),(0.66443704225140021, 0.84641110220126559, 1),
    #                 (0.5, 0.20304808267759977, 0.79378947410890432),(1, 0.99511009425285579, 0.082395393182125187),
    #                 (0.4, 0.58475221899639263, 0.60847054827215996),(0.2286469280288263, 0.8, 0.8),(1.0, 0.7, 0.2)])
    colors_ = [(0.8,0.01,0.01),(0.8,0.41,0.01),(0.8,0.8,0.01),(0.41,0.8,0.01),(0.01,0.8,0.01),(0.01,0.8,0.41),(0.01,0.8,0.8)
               ,(0.01,0.41,0.8),(0.2, 0.2, 1),(0.41,0.01,0.8),(0.01,0.01,0.8),(1,0.4,0.7),(0.8,0.01,0.8),(0.8,0.01,0.41),(0.62,0.62,0.62),(0.41,0.41,0.41),(0.01,0.01,0.01)]
    while len(colors_) < number_of_groups:
        tmp_color = tuple(map(operator.add, rnd.choice(colors_), random.random(3)))
        tmp_color = tuple(map(lambda x: 1 if x>1 else x,tmp_color))
        colors_.append(tmp_color)
    # if smoothness> 1 :
    #     alpha_values = list(arange(1./(smoothness),1.00001,1./(smoothness/2))) +[1]+ list(arange(1./(smoothness),1.00001,1./(smoothness/2))[::-1])
    # else:
    #     alpha_values = [1]
        # alpha_values = list([1-1./xx for xx in range(1,smoothness/2+1)]) + [1] +  list([1-1./xx for xx in range(1,smoothness/2+1)][::-1])
    coverage_range = 2 # defines how many pixels in proximity of the target pixel will be colored as well
    for group_idx,group in enumerate(groups):
        try:
            spikes_tmp = [round(t, int(abs(log10(d_t)))) for t in spikes[group][1]]
        except:
            continue
        current_layer = int(group[group.index('_L')+2:group.index('_L')+3] if not 'vpm' in group else 0)
        current_layer = current_layer-1 if current_layer>2 else current_layer
        color_value = colors_[group_idx]
        total_perc = float(group_idx) / number_of_groups * 100
        unique_times = unique(spikes_tmp)
        for action_time_idx, action_time in enumerate(unique_times ):
            current_perc = float(action_time_idx)/len(unique_times) * 100
            _status_printer('Current group: %f%% , Total: %f%% ' %(current_perc ,total_perc))
            indices = [i for i, x in enumerate(spikes_tmp) if x == action_time]
            action_potentials = [int(action_idx) for action_idx in spikes[group][0][indices]]
            frame_idx = ts.index(round(action_time, int(abs(log10(d_t)))))
            if frame_idx == 0:
                print "one found"
            for action in action_potentials:
                x_target = round(real(w_coord[group][action]), axis_precision)
                x_target_index = X_axis.index(x_target)
                y_target = round(imag(w_coord[group][action]), axis_precision)
                y_target_index = Y_axis.index(y_target)
                # for smoo in range(smoothness):
                #     all_frames[current_layer,frame_idx * smoothness + smoo,x_target_index - coverage_range:x_target_index + coverage_range,y_target_index - coverage_range:y_target_index + coverage_range,0:3] = color_value
                #     all_frames[current_layer,frame_idx * smoothness + smoo,x_target_index - coverage_range:x_target_index + coverage_range,y_target_index - coverage_range:y_target_index + coverage_range,3] = alpha_values[smoo]
                all_frames[current_layer][frame_idx][0][x_target_index - coverage_range:x_target_index + coverage_range,y_target_index - coverage_range:y_target_index + coverage_range] = float32(color_value[0])
                all_frames[current_layer][frame_idx][1][x_target_index - coverage_range:x_target_index + coverage_range,y_target_index - coverage_range:y_target_index + coverage_range] = float32(color_value[1])
                all_frames[current_layer][frame_idx][2][x_target_index - coverage_range:x_target_index + coverage_range,y_target_index - coverage_range:y_target_index + coverage_range] = float32(color_value[2])
                # all_frames[current_layer][frame_idx][3][x_target_index - coverage_range:x_target_index + coverage_range,y_target_index - coverage_range:y_target_index + coverage_range] = float32(1)

    return all_frames,colors_,ts

def sparse_to_rgba (sparse_matrix):
    arr = np.array([channel.toarray() for channel in sparse_matrix])
    arr[arr==0]= 1
    return rollaxis(arr,0,3)

filepath = default_mat_file_path
# filepath = '/home/shohokka/PycharmProjects/CX_Output/calcium20.mat'
filename = ntpath.basename(os.path.splitext(filepath)[0])
folderpath = os.path.dirname(filepath)

data = loadmat(filepath)
NNs = data['number_of_neurons']
layers_NN = zeros([6])
for group in NNs.keys():
    current_layer = int(group[group.index('_L') + 2:group.index('_L') + 3] if not 'vpm' in group else 0)
    current_layer = current_layer - 1 if current_layer > 2 else current_layer
    layers_NN[current_layer] = layers_NN[current_layer] + NNs[group]

positions = data['positions_all']
spikes = data['spikes_all']
w_coord = positions['w_coord']
groups = w_coord.keys()
min_x = 0
max_x = 0
min_y = 0
max_y = 0

for group in groups:
    min_x = min_x if min_x<min(real(w_coord[group])) else min(real(w_coord[group]))
    max_x = max_x if max_x>max(real(w_coord[group])) else max(real(w_coord[group]))
    min_y = min_y if min_y < min(imag(w_coord[group])) else min(imag(w_coord[group]))
    max_y = max_y if max_y > max(imag(w_coord[group])) else max(imag(w_coord[group]))
# d_x = 1e-4 # equal to 100um
d_x = 1e-3 # equal to 100um
min_x = round(min_x, int(abs(log10(d_x))))
max_x = round(max_x, int(abs(log10(d_x))))
min_y = round(min_y, int(abs(log10(d_x))))
max_y = round(max_y, int(abs(log10(d_x))))
axis_precision = int(abs(log10(d_x)))


X_axis = [round(cord, axis_precision) for cord in arange(min_x, max_x+d_x, d_x)]
Y_axis = [round(cord, axis_precision) for cord in arange(min_y, max_y+d_x, d_x)]

# smoothness = 1
if not os.path.isfile(os.path.join(folderpath,filename+'.npz')):
    runtime = data['runtime']*1000
    all_frames,colors_,ts = spike_to_fram(groups, spikes, X_axis, Y_axis, w_coord, axis_precision)
    savez(os.path.join(folderpath,filename),all_frames=all_frames,colors_=colors_,ts=ts)
else:
    npzfile = load(os.path.join(folderpath,filename+'.npz'))
    all_frames = npzfile ['all_frames']
    colors_ =  npzfile ['colors_']
    ts = npzfile['ts']
fig = plt.figure(figsize=(23,12))
ax_arr= []
gs = gridspec.GridSpec(3, 3,height_ratios=[3,3,1])
ax_arr.append(fig.add_subplot(gs[0]))
ax_arr.append(fig.add_subplot(gs[1]))
ax_arr.append(fig.add_subplot(gs[2]))
ax_arr.append(fig.add_subplot(gs[3]))
ax_arr.append(fig.add_subplot(gs[4]))
ax_arr.append(fig.add_subplot(gs[5]))
# ax_arr.append(fig.add_subplot(313))

# fig, ax_arr = plt.subplots(2, 3,figsize=(20,10))
im = []
titles = array(['input','Layer 1','Layer 2/3', 'Layer4','Layer 5','Layer 6'])

for plot_idx in range (0,6):
    im.append(ax_arr[plot_idx].imshow(sparse_to_rgba(all_frames[plot_idx][0]), origin='lower',
                   extent=(min_x, max_x, min_y, max_y),
                   vmin=0, vmax=groups.__len__(),cmap = "spectral"))
    ax_arr[plot_idx].set_xlim([min_x-abs(min_x)/5, max_x+max_x/5])
    ax_arr[plot_idx].set_ylim([min_y-abs(min_y)/5, max_y+max_y/5])
    ax_arr[plot_idx].set_title(titles[plot_idx])
    ax_arr[plot_idx].set_xlabel('Cortical Surface Dimension 1 [mm]')
    ax_arr[plot_idx].set_ylabel('Cortical Surface Dimension 2 [mm]')
    ax_arr[plot_idx].text(0.03,0.95,"Number of Neurons: %d"%layers_NN[plot_idx],transform=ax_arr[plot_idx].transAxes , fontsize=9, bbox={'boxstyle':'round','facecolor':'wheat','alpha':0.9} )

groups_layers = [int(group[group.index('_L')+2:group.index('_L')+3] if not 'vpm' in group else 0) for group in groups]
sorted_groups = [x for (y,x) in sorted(zip(groups_layers,groups))]
sorted_colors = [colors_[ii] for ii in [groups.index(group) for group in sorted_groups]]

for idx,group in enumerate(sorted_groups) :
    current_title = group[group.index('_')+1 :].replace('_L',' [Layer').replace('to',' to ') + ']' if not 'vpm' in group else group[group.index('_')+1 :].replace('_L',' [Layer ').replace('to',' to ')
    ax_arr[3].plot(100,100, 's',label=current_title,markersize=10, color=sorted_colors[idx])
ax_arr[3].legend(bbox_to_anchor=(0, -0.2), loc='upper left', borderaxespad=0, numpoints=1 ,ncol=6)
plt.tight_layout(pad=0.4, w_pad=-40, h_pad=1.0)
# plt.show()
class animator:
    def __init__(self,fig,data,im):
        self.fig = fig
        self.data = data
        self.i = 0
        self.im = im
    def animator (self,index):
        for im_idx in range(len(im)):
            self.im[im_idx].set_data(sparse_to_rgba(self.data[im_idx][index]))
            ax_arr[im_idx].text(0.03,0.03,"Time: %d ms"%(ts[index]*1000),transform=ax_arr[im_idx].transAxes , fontsize=9, bbox={'boxstyle':'round','facecolor':'wheat','alpha':0.9} )
            if len(ax_arr[im_idx].texts) > 2:
                ax_arr[im_idx].texts = [ax_arr[im_idx].texts[idx] for idx in [0,-1]]


        self._status_printer("Time: %d ms"%(ts[index]*1000))
    def _status_printer(self,str):
        #cleaner = ' ' * 100
        #print '\r' + cleaner + '\r' + str,
        print str


# plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'
anime = animator (fig,all_frames,im)

anim = FuncAnimation(fig, anime.animator, frames=shape(all_frames)[1],interval=100,repeat_delay=3000)

if save_flag == 1:
    anim.save(os.path.abspath(os.path.join(folderpath,filename+'.mp4')),extra_args=['-vcodec', 'libx264'])
else:
    plt.show()


