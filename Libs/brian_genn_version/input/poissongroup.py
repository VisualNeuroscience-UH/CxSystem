'''
Implementation of `PoissonGroup`.
'''

import numpy as np

from brian_genn_version.core.spikesource import SpikeSource
from brian_genn_version.core.variables import Variables
from brian_genn_version.units.fundamentalunits import check_units, Unit
from brian_genn_version.units.stdunits import Hz
from brian_genn_version.groups.group import Group
from brian_genn_version.groups.neurongroup import Thresholder

__all__ = ['PoissonGroup']


class PoissonGroup(Group, SpikeSource):
    '''
    Poisson spike source
    
    Parameters
    ----------
    N : int
        Number of neurons
    rates : `Quantity`, str
        Single rate, array of rates of length N, or a string expression
        evaluating to a rate
    dt : `Quantity`, optional
        The time step to be used for the simulation. Cannot be combined with
        the `clock` argument.
    clock : `Clock`, optional
        The update clock to be used. If neither a clock, nor the `dt` argument
        is specified, the `defaultclock` will be used.
    when : str, optional
        When to run within a time step, defaults to the ``'thresholds'`` slot.
    order : int, optional
        The priority of of this group for operations occurring at the same time
        step and in the same scheduling slot. Defaults to 0.
    name : str, optional
        Unique name, or use poissongroup, poissongroup_1, etc.

    '''
    add_to_magic_network = True

    @check_units(rates=Hz)
    def __init__(self, N, rates, dt=None, clock=None, when='thresholds',
                 order=0, name='poissongroup*', codeobj_class=None):

        Group.__init__(self, dt=dt, clock=clock, when=when, order=order,
                       name=name)

        self.codeobj_class = codeobj_class

        self._N = N = int(N)

        # TODO: In principle, it would be nice to support Poisson groups with
        # refactoriness, but we can't currently, since the refractoriness
        # information is reset in the state updater which we are not using
        # We could either use a specific template or simply not bother and make
        # users write their own NeuronGroup (with threshold rand() < rates*dt)
        # for more complex use cases.

        self.variables = Variables(self)
        # standard variables
        self.variables.add_constant('N', unit=Unit(1), value=self._N)
        self.variables.add_arange('i', self._N, constant=True, read_only=True)
        self.variables.add_array('_spikespace', size=N+1, unit=Unit(1),
                                 dtype=np.int32)
        self.variables.create_clock_variables(self._clock)

        # The firing rates
        self.variables.add_array('rates', size=N, unit=Hz)

        self.start = 0
        self.stop = N

        self._refractory = False

        # To avoid a warning about the local variable rates, we set the real
        # threshold condition only after creating the object
        self.events = {'spike': 'False'}
        self.thresholder = {'spike': Thresholder(self)}
        self.events = {'spike': 'rand() < rates * dt'}
        self.contained_objects.append(self.thresholder['spike'])

        self._enable_group_attributes()

        # Here we want to use the local namespace, but at the level where the
        # constructor was called
        self.rates.set_item(slice(None), rates, level=2)


    @property
    def spikes(self):
        '''
        The spikes returned by the most recent thresholding operation.
        '''
        # Note that we have to directly access the ArrayVariable object here
        # instead of using the Group mechanism by accessing self._spikespace
        # Using the latter would cut _spikespace to the length of the group
        spikespace = self.variables['_spikespace'].get_value()
        return spikespace[:spikespace[-1]]

    def __repr__(self):
        description = '{classname}({N}, rates=<...>)'
        return description.format(classname=self.__class__.__name__,
                                  N=self.N)

