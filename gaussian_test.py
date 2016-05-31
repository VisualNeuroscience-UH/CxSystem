import matplotlib.pyplot as plt
import numpy as np
from numpy import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

plt.figure

x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = np.exp(-(X**2 + Y**2 )/2*(0.2*2.3)**2)

fig1 = plt.figure()
ax = fig1.gca(projection='3d')
ax.plot_surface(X,Y,Z)


# z = sqrt(X**2+Y**2)
# tmp_indices = unique(nonzero(z<5)[0])
# norm_factors = z[ix_(tmp_indices)]
# _zero_vals_at = nonzero(norm_factors == 0)[0]
# norm_factors[ix_(_zero_vals_at)] = 0.23
# _probas_i = (exp(-z[ix_(tmp_indices)] * 1) / norm_factors)

Z2 = np.exp(-(np.sqrt( X** 2 + Y ** 2)) * 0.01)


fig2 = plt.figure()
ax2 = fig2.gca(projection='3d')
ax2.plot_surface(X,Y,Z2)

plt.show()

# exp(-(sqrt((x_pre-x_post)**2+(y_pre-y_post)**2)) * %f)/(sqrt((x_pre-x_post)**2+(y_pre-y_post)**2)/mm)'