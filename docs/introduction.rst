.. |br| raw:: html

   <br />

Introduction
==============================

CxSystem is a cerebral cortex simulation framework, which operates on personal computers. It has been tested \
with a simplification of a recently published comprehensive cortical microcircuit model [1]_.
The CxSystem aims at easy testing and buildup of diverse models at single cell resolution. |br|
It reuses components of earlier work [2]_, but the code has been completely \
rewritten to be dynamically compiled from configuration files, and to run on C++ and GeNN [3]_ \
devices. Implemented on the top of the Python-based Brian2 simulator [4]_, CxSystem supports the \
main goal of Brian, i.e. minimizing development time, by providing the user with a simplified interface. |br|
The two configuration files, easily modifiable with regular spreadsheet programs, have a biologically meaningful syntax \
and are appropriate for life scientists who are unaccustomed to computer programming. CxSystem is available at GitHub (https://github.com/sivanni/CXSystem_Git).

|br|
|br|

.. [1] Markram, H., Muller, E., Ramaswamy, S., Reimann, M. W., Abdellah, M., Sanchez, C. A., … Schürmann, F. (2015). Reconstruction and Simulation of Neocortical Microcircuitry. Cell, 163(2), 456–492. http://doi.org/10.1016/j.cell.2015.09.029
.. [2] Heikkinen, H., Sharifian, F., Vigário, R., & Vanni, S. (2015). Feedback to distal dendrites links fMRI signals to neural receptive fields in a spiking network model of the visual cortex. Journal of Neurophysiology, 114(1), 57–69. http://doi.org/10.1152/jn.00169.2015
.. [3] Yavuz, E., Turner, J., & Nowotny, T. (2016). GeNN: a code generation framework for accelerated brain simulations. Scientific Reports, 6(1), 18854. http://doi.org/10.1038/srep18854
.. [4] Goodman, D., & Brette, R. (2009). The Brian simulator   . Frontiers in Neuroscience
