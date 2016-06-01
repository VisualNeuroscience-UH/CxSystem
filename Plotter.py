from matplotlib.pyplot import  *

def multi_y_plotter(ax, len, x,y):
    for i in range(len):
        tmp_str = ax + '.plot(x, y[%d])'%i
        exec tmp_str
