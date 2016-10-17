import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
import scipy.io
from numpy import *
import pylab as pl
from matplotlib import colors
from sympy.ntheory.factor_ import smoothness
import random as rnd
import operator
import ntpath
import os

def _status_printer(str):
    cleaner = ' ' * 100
    print '\r' + cleaner + '\r' + str,


def spike_to_fram(groups,spikes,X_axis,Y_axis,w_coord,axis_precision,runtime,smoothness=15,d_t = 0.001) :
    if smoothness%2!=1 :
        smoothness+=1
    t_min = 0
    t_max = 0
    for group in groups:
        try:
            spikes_ts_tmp = spikes[group][0][0][1]
        except:
            continue
        # min_temp = min(spikes_ts_tmp)
        # t_min = t_min if t_min < min_temp else min_temp
        max_temp = max(spikes_ts_tmp)
        t_max = t_max if t_max > max_temp else max_temp
    ts = [round(t,int(abs(log10(d_t)))) for t in arange(t_min, t_max+d_t, d_t)]
    number_of_frames = len(ts)
    all_frames = zeros([number_of_frames*smoothness,size(X_axis),size(Y_axis),4])
    number_of_groups = len(groups)

    ############ BUILDING UP THE COLORS
    colors_ = colors.ColorConverter.colors.values()
    del colors_[2]
    colors_.extend([(0.76405586529938008, 1, 0.19037723714226007),(1, 1, 0.76055023945491484),(0.062061436708711004, 1, 0.86121671615825279),(1, 0.60415383899256947, 1),(0.66443704225140021, 0.84641110220126559, 1),(1, 0.20304808267759977, 0.79378947410890432),(1, 0.99511009425285579, 0.082395393182125187),(1, 0.58475221899639263, 0.60847054827215996),(0.7286469280288263, 1, 1),(1.0, 0.7, 0.2)])
    while len(colors_) < number_of_groups:
        tmp_color = tuple(map(operator.add, rnd.choice(colors_), random.random(3)))
        tmp_color = tuple(map(lambda x: 1 if x>1 else x,tmp_color))
        colors_.append(tmp_color)
    if smoothness> 1 :
        alpha_values = list(arange(1./(smoothness),1.00001,1./(smoothness/2))) +[1]+ list(arange(1./(smoothness),1.00001,1./(smoothness/2))[::-1])
    else:
        alpha_values = [1]
        # alpha_values = list([1-1./xx for xx in range(1,smoothness/2+1)]) + [1] +  list([1-1./xx for xx in range(1,smoothness/2+1)][::-1])
    for group_idx,group in enumerate(groups):
        try:
            spikes_tmp = [round(t, int(abs(log10(d_t)))) for t in spikes[group][0][0][1]]
        except:
            continue
        color_value = colors_[group_idx]
        total_perc = float(group_idx) / number_of_groups * 100
        unique_times = unique(spikes_tmp)
        for action_time_idx, action_time in enumerate(unique_times ):
            current_perc = float(action_time_idx)/len(unique_times) * 100
            _status_printer('Current group: %f%% , Total: %f%% ' %(current_perc ,total_perc))
            indices = [i for i, x in enumerate(spikes_tmp) if x == action_time]
            action_potentials = [int(action_idx) for action_idx in spikes[group][0][0][0][indices]]
            frame_idx = ts.index(round(action_time, int(abs(log10(d_t)))))
            for action in action_potentials:
                x_target = round(real(w_coord[group][0][0][0][action]), axis_precision)
                x_target_index = X_axis.index(x_target)
                y_target = round(imag(w_coord[group][0][0][0][action]), axis_precision)
                y_target_index = Y_axis.index(y_target)
                for smoo in range(smoothness):
                    all_frames[frame_idx * smoothness + smoo,x_target_index - 1:x_target_index + 1,y_target_index - 1:y_target_index + 1,0:3] = color_value
                    all_frames[frame_idx * smoothness + smoo,x_target_index - 1:x_target_index + 1,y_target_index - 1:y_target_index + 1,3] = alpha_values[smoo]

    return all_frames,colors_,ts

filepath = '/media/CX_Disk/CX_Output/Gain-EE1EI1.mat'
filename = ntpath.basename(os.path.splitext(filepath)[0])
folderpath = os.path.dirname(filepath)

data = scipy.io.loadmat(filepath)
positions = data['positions_all'][0]
spikes = data['spikes_all']
w_coord = positions['w_coord'][0]
dtypes = w_coord.dtype
groups = [l for l in spikes.dtype.fields]
min_x = 0
max_x = 0
min_y = 0
max_y = 0
for group in groups:
    min_x = min_x if min_x<min(real(w_coord[group][0][0][0])) else min(real(w_coord[group][0][0][0]))
    max_x = max_x if max_x>max(real(w_coord[group][0][0][0])) else max(real(w_coord[group][0][0][0]))
    min_y = min_y if min_y < min(imag(w_coord[group][0][0][0])) else min(imag(w_coord[group][0][0][0]))
    max_y = max_y if max_y > max(imag(w_coord[group][0][0][0])) else max(imag(w_coord[group][0][0][0]))
# d_x = 1e-4 # equal to 100um
d_x = 1e-3 # equal to 100um
min_x = round(min_x, int(abs(log10(d_x))))
max_x = round(max_x, int(abs(log10(d_x))))
min_y = round(min_y, int(abs(log10(d_x))))
max_y = round(max_y, int(abs(log10(d_x))))
axis_precision = int(abs(log10(d_x)))


X_axis = [round(cord, axis_precision) for cord in arange(min_x, max_x+d_x, d_x)]
Y_axis = [round(cord, axis_precision) for cord in arange(min_y, max_y+d_x, d_x)]

smoothness = 1
if not os.path.isfile(os.path.join(folderpath,filename+'_smooth%d'%smoothness+'.npz')):
    runtime = data['runtime']*1000
    all_frames,colors_,ts = spike_to_fram(groups, spikes, X_axis, Y_axis, w_coord, axis_precision,runtime,smoothness=smoothness)
    savez(os.path.join(folderpath,filename+'_smooth%d'%smoothness),all_frames=all_frames,colors_=colors_,ts=ts)
else:
    npzfile = load(os.path.join(folderpath,filename+'_smooth%d'%smoothness+'.npz'))
    all_frames = npzfile ['all_frames']
    colors_ =  npzfile ['colors_']
    ts = npzfile['ts']
fig, ax = plt.subplots(1, 1,figsize=(15,10))

im = ax.imshow(all_frames[0], origin='lower',
               extent=(min_x, max_x, min_y, max_y),
               vmin=0, vmax=groups.__len__(),cmap = "spectral")
ax.set_xlim([min_x-abs(min_x)/5, max_x+max_x/5])
ax.set_ylim([min_y-abs(min_y)/5, max_y+max_y/5])
for idx,group in enumerate(groups) :
    ax.plot(100,100, 's',label=group,markersize=10, color=colors_[idx])
pl.legend(loc='lower left', borderaxespad=0,numpoints=1,bbox_to_anchor=(1.02, 0))
class animator:
    def __init__(self,fig,data,im):
        self.fig = fig
        self.data = data
        self.i = 0
        self.im = im
    def animator (self,index):
        self.im.set_data(self.data[index])
        self._status_printer("Time: %d ms"%(ts[index]*1000/smoothness))
    def _status_printer(self,str):
        cleaner = ' ' * 100
        print '\r' + cleaner + '\r' + str,


plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'
anime = animator (fig,all_frames,im)

anim = FuncAnimation(fig, anime.animator, frames=all_frames.shape[0],interval=100,repeat_delay=3000)
plt.show()
anim.save(os.path.join(folderpath,filename+'_smooth%d'%smoothness+'.mp4'),extra_args=['-vcodec', 'libx264'])


