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


def spike_to_fram(groups,spikes,X_axis,Y_axis,z_coord,axis_precision,smoothness=15,d_t = 0.001) :
    if smoothness%2!=1 :
        smoothness+=1
    ts = []
    for group in groups:
        spikes_ts_tmp = spikes[group][0][0][1]
        ts_temp = [round(t,int(abs(log10(d_t)))) for t in arange(min(spikes_ts_tmp), max(spikes_ts_tmp)+d_t, d_t)]
        ts = ts_temp if len(ts)<len(ts_temp) else ts
    number_of_frames = len(ts)
    all_frames = zeros([number_of_frames*smoothness,size(X_axis),size(Y_axis)])
    number_of_pixel_colors = smoothness/2+1
    # step = 1./number_of_pixel_colors
    colors_ = [1-1./xx for xx in range(1,number_of_pixel_colors+1)]
    colors_ = list(colors_) + list(colors_[::-1][1:])
    for idx in range(number_of_frames):
        for group in groups:
            spikes_tmp = [round(t,int(abs(log10(d_t)))) for t in spikes[group][0][0][1]]
            if ts[idx] in spikes_tmp:
                # print  "%f found" %ts[idx]
                indices =[ii for ii,xx in enumerate(spikes_tmp) if xx==ts[idx]]
                action_potentials = [int(action_idx) for action_idx in spikes[group][0][0][0][indices]]
                for action in action_potentials:
                    x_target = round(real(z_coord[group][0][0][0][action]),axis_precision)
                    x_target_index = X_axis.index(x_target)
                    y_target = round(imag(z_coord[group][0][0][0][action]), axis_precision)
                    y_target_index = Y_axis.index(y_target)
                    for smoo in range(smoothness):
                        color_value =  colors_ [smoo] * (groups.index(group)+1)
                        print '%f' %(color_value)
                        all_frames[idx*smoothness+smoo][x_target_index-1:x_target_index+1,y_target_index-1:y_target_index+1] = color_value
    return all_frames


data = scipy.io.loadmat('/home/corriel/Documents/Git_repos/CX_Output/Custom_Name_20160916_165114.mat')
positions = data['positions_all'][0]
spikes = data['spikes_all']
z_coord = positions['z_coord'][0]
dtypes = z_coord.dtype
groups = [l for l in dtypes.fields]
min_x = 0
max_x = 0
min_y = 0
max_y = 0
for group in groups:
    min_x = min_x if min_x<min(real(z_coord[group][0][0][0])) else min(real(z_coord[group][0][0][0]))
    max_x = max_x if max_x>max(real(z_coord[group][0][0][0])) else max(real(z_coord[group][0][0][0]))
    min_y = min_y if min_y < min(imag(z_coord[group][0][0][0])) else min(imag(z_coord[group][0][0][0]))
    max_y = max_y if max_y > max(imag(z_coord[group][0][0][0])) else max(imag(z_coord[group][0][0][0]))
d_x = 1e-4 # equal to 100um
min_x = round(min_x, int(abs(log10(d_x))))
max_x = round(max_x, int(abs(log10(d_x))))
min_y = round(min_y, int(abs(log10(d_x))))
max_y = round(max_y, int(abs(log10(d_x))))
axis_precision = int(abs(log10(d_x)))


X_axis = [round(cord, axis_precision) for cord in arange(min_x, max_x+d_x, d_x)]
Y_axis = [round(cord, axis_precision) for cord in arange(min_y, max_y+d_x, d_x)]

test_zs = z_coord['NG1_SS_L4'][0][0][0]

smoothness = 15
all_frames = spike_to_fram(groups, spikes, X_axis, Y_axis, z_coord, axis_precision,smoothness=smoothness)
fig, ax = plt.subplots(1, 1)
# cmap = colors.ListedColormap(['white', 'red' , 'blue' , 'black'])
# bounds=[-0.5,0.5,1.5,2.5,3.5]
# norm = colors.BoundaryNorm(bounds, cmap.N)




# im = ax.imshow(all_frames[0], origin='lower',
#                extent=(min_x-min_x/3, max_x+max_x/3, min_y-min_y/3, max_y+max_y/3),
#                vmin=0, vmax=groups.__len__(),  cmap=cmap, norm=norm)

im = ax.imshow(all_frames[0], origin='lower',
               extent=(min_x-min_x/3, max_x+max_x/3, min_y-min_y/3, max_y+max_y/3),
               vmin=0, vmax=groups.__len__(),cmap = "spectral")


class animator:
    def __init__(self,fig,data,im):
        self.fig = fig
        self.data = data
        self.i = 0
        self.im = im
    def animator (self,index):
        self.im.set_data(self.data[index])
        self._status_printer("frame %d"%(index/smoothness))
    def _status_printer(self,str):
        cleaner = ' ' * 100
        print '\r' + cleaner + '\r' + str,
# mycmap = pl.cm.jet # for example
# for entry in pl.unique(all_frames)[1:]:
#     mycolor = mycmap(entry*255/(max(asarray(all_frames).reshape(-1)) - min(asarray(all_frames).reshape(-1))))
#     pl.plot(0, 0, "-", c=mycolor, label='hello')
#
# pl.imshow(all_frames[0])
# pl.legend()



anime = animator (fig,all_frames,im)

anim = FuncAnimation(fig, anime.animator, frames=all_frames.shape[0],interval=400/smoothness)


plt.show()






