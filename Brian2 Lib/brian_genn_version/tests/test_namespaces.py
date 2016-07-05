import uuid

import sympy
import numpy
from numpy.testing.utils import assert_raises
from nose.plugins.attrib import attr

from brian_genn_version.core.variables import Constant
from brian_genn_version.groups.group import Group
from brian_genn_version.units import second, volt
from brian_genn_version.units.fundamentalunits import Unit
from brian_genn_version.units.stdunits import ms, Hz, mV
from brian_genn_version.units.unitsafefunctions import sin, log, exp
from brian_genn_version.utils.logger import catch_logs

# a simple Group for testing
class SimpleGroup(Group):
    def __init__(self, variables, namespace=None):
        self.variables = variables
        self.namespace = namespace
        # We use a unique name to get repeated warnings
        Group.__init__(self, name='simplegroup_' +
                                  str(uuid.uuid4()).replace('-','_'))

def _assert_one_warning(l):
    assert len(l) == 1, "expected one warning got %d" % len(l)
    assert l[0][0] == 'WARNING', "expected a WARNING, got %s instead" % l[0][0]


@attr('codegen-independent')
def test_default_content():
    '''
    Test that the default namespace contains standard units and functions.
    '''
    group = Group()
    # Units
    assert group.resolve('second', None).get_value_with_unit() == second
    assert group.resolve('volt', None).get_value_with_unit() == volt
    assert group.resolve('ms', None).get_value_with_unit() == ms
    assert group.resolve('Hz', None).get_value_with_unit() == Hz
    assert group.resolve('mV', None).get_value_with_unit() == mV

    # Functions
    assert group.resolve('sin', None).pyfunc == sin
    assert group.resolve('log', None).pyfunc == log
    assert group.resolve('exp', None).pyfunc == exp

    # Constants
    assert group.resolve('e').sympy_obj == sympy.E
    assert group.resolve('e').get_value() == numpy.e
    assert group.resolve('pi').sympy_obj == sympy.pi
    assert group.resolve('pi').get_value() == numpy.pi
    assert group.resolve('inf').sympy_obj == sympy.oo
    assert group.resolve('inf').get_value() == numpy.inf


@attr('codegen-independent')
def test_explicit_namespace():
    ''' Test resolution with an explicitly provided namespace '''
    group = SimpleGroup(namespace={'variable': 42}, variables={})

    # Explicitly provided
    with catch_logs() as l:
        assert group.resolve('variable').get_value_with_unit() == 42
        assert len(l) == 0

    # Value from the local namespace
    another_variable = 23
    with catch_logs() as l:
        assert group.resolve('another_variable').get_value_with_unit() == 23
        assert len(l) == 0

    # Value from an explicit run namespace
    with catch_logs() as l:
        assert group.resolve('yet_another_var',
                             run_namespace={'yet_another_var': 17}).get_value_with_unit() == 17
        assert len(l) == 0


@attr('codegen-independent')
def test_errors():
    # No explicit namespace
    group = SimpleGroup(namespace=None, variables={})
    assert_raises(KeyError, lambda: group.resolve('nonexisting_variable'))

    # Empty explicit namespace
    group = SimpleGroup(namespace={}, variables={})
    assert_raises(KeyError, lambda: group.resolve('nonexisting_variable'))


@attr('codegen-independent')
def test_resolution():
    # implicit namespace
    tau = 10*ms
    group = SimpleGroup(namespace=None, variables={})
    resolved = group.resolve_all(['tau', 'ms'], ['tau', 'ms'])
    assert len(resolved) == 2
    assert type(resolved) == type(dict())
    assert resolved['tau'].get_value_with_unit() == tau
    assert resolved['ms'].get_value_with_unit() == ms
    del tau

    # explicit namespace
    group = SimpleGroup(namespace={'tau': 20 * ms}, variables={})

    resolved = group.resolve_all(['tau', 'ms'], ['tau', 'ms'])
    assert len(resolved) == 2
    assert resolved['tau'].get_value_with_unit() == 20 * ms


@attr('codegen-independent')
def test_warning():
    from brian_genn_version.core.functions import DEFAULT_FUNCTIONS
    from brian_genn_version.units.stdunits import cm as brian_cm
    # Name in external namespace clashes with unit/function name
    exp = 23
    cm = 42
    group = SimpleGroup(namespace=None, variables={})
    with catch_logs() as l:
        resolved = group.resolve('exp')
        assert resolved == DEFAULT_FUNCTIONS['exp']
        assert len(l) == 1, 'got warnings: %s' % str(l)
        assert l[0][1].endswith('.resolution_conflict')
    with catch_logs() as l:
        resolved = group.resolve('cm')
        assert resolved.get_value_with_unit() == brian_cm
        assert len(l) == 1, 'got warnings: %s' % str(l)
        assert l[0][1].endswith('.resolution_conflict')

@attr('codegen-independent')
def test_warning_internal_variables():
    N = 5
    group1 = SimpleGroup(namespace=None,
                         variables={'N': Constant('N', Unit(1), 5)})
    group2 = SimpleGroup(namespace=None,
                         variables={'N': Constant('N', Unit(1), 7)})
    with catch_logs() as l:
        group1.resolve('N')  # should not raise a warning
        assert len(l) == 0, 'got warnings: %s' % str(l)
    with catch_logs() as l:
        group2.resolve('N')  # should raise a warning
        assert len(l) == 1, 'got warnings: %s' % str(l)
        assert l[0][1].endswith('.resolution_conflict')


if __name__ == '__main__':
    test_default_content()
    test_explicit_namespace()
    test_errors()
    test_resolution()
    test_warning()
    test_warning_internal_variables()
