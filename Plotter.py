from matplotlib.pyplot import  *
from brian_genn_version  import *

def multi_y_plotter(ax, len, variable,item,title):

    for i in range(len):
        tmp_str = 'ax.plot(item.t/ms, item.%s[%d])'%(variable,i);exec tmp_str
        tmp_str = "ax.set_title('%s')" % (title);exec tmp_str