'''
A dummy package to allow importing numpy and the unit-aware replacements of
numpy functions without having to know which functions are overwritten.

This can be used for example as ``import brian_genn_version.numpy_ as np``
'''
from numpy import *
from brian_genn_version.units.unitsafefunctions import *

# These will not be imported with a wildcard import to not overwrite the
# builtin names (mimicking the numpy behaviour)
from __builtin__ import bool, int, long, float, complex, object, unicode, str
from numpy.core import round, abs, max, min

import numpy
import brian_genn_version.units.unitsafefunctions as brian_genn_version_functions
__all__ = []
__all__.extend(numpy.__all__)
__all__.extend(brian_genn_version_functions.__all__)
