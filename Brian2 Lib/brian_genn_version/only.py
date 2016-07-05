'''
A dummy package to allow wildcard import from brian_genn_version without also importing
the pylab (numpy + matplotlib) namespace.

Usage: ``from brian_genn_version.only import *``

'''
import gc
# To minimize the problems with imports, import the packages in a sensible
# order

# The units and utils package does not depend on any other Brian package and
# should be imported first
from brian_genn_version.units import *
from brian_genn_version.utils import *
from brian_genn_version.core.tracking import *
from brian_genn_version.core.names import *
from brian_genn_version.core.spikesource import *

# The following packages only depend on something in the above set
from brian_genn_version.core.variables import linked_var
from brian_genn_version.core.functions import *
from brian_genn_version.core.preferences import *
from brian_genn_version.core.clocks import *
from brian_genn_version.equations import *

# The base class only depends on the above sets
from brian_genn_version.core.base import *

# The rest...
from brian_genn_version.core.network import *
from brian_genn_version.core.magic import *
from brian_genn_version.core.operations import *
from brian_genn_version.stateupdaters import *
from brian_genn_version.codegen import *
from brian_genn_version.core.namespace import *
from brian_genn_version.groups import *
from brian_genn_version.synapses import *
from brian_genn_version.monitors import *
from brian_genn_version.input import *
from brian_genn_version.spatialneuron import *
from brian_genn_version.devices import set_device, get_device, device
import brian_genn_version.devices.cpp_standalone as _cpp_standalone

# preferences
from brian_genn_version.core.core_preferences import *
prefs.load_preferences()
prefs.do_validation()

prefs._backup()

def restore_initial_state():
    '''
    Restores internal Brian variables to the state they are in when Brian is imported

    Resets ``defaultclock.dt = 0.1*ms``, 
    `BrianGlobalPreferences._restore` preferences, and set
    `BrianObject._scope_current_key` back to 0.
    '''
    prefs._restore()
    BrianObject._scope_current_key = 0
    defaultclock.dt = 0.1*ms
    gc.collect()

# make the test suite available via brian_genn_version.test()
from brian_genn_version.tests import run as test
