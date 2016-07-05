from numpy.testing.utils import assert_equal, assert_raises
from nose import with_setup
from nose.plugins.attrib import attr

from brian_genn_version import *
from brian_genn_version.devices.device import restore_device

@attr('standalone-compatible')
@with_setup(teardown=restore_device)
def test_poissoninput():
    # Test extreme cases and do a very basic test of an intermediate case, we
    # don't want tests to be stochastic
    G = NeuronGroup(10, '''x : volt
                           y : volt
                           y2 : volt
                           z : volt
                           z2 : volt
                           w : 1''')
    G.w = 0.5

    never_update = PoissonInput(G, 'x', 100, 0*Hz, weight=1*volt)
    always_update = PoissonInput(G, 'y', 50, 1/defaultclock.dt, weight=2*volt)
    always_update2 = PoissonInput(G, 'y2', 50, 1/defaultclock.dt, weight='1*volt + 1*volt')
    sometimes_update = PoissonInput(G, 'z', 10000, 50*Hz, weight=0.5*volt)
    sometimes_update2 = PoissonInput(G, 'z2', 10000, 50*Hz, weight='w*volt')

    mon = StateMonitor(G, ['x', 'y', 'y2', 'z', 'z2'], record=True, when='end')

    run(1*ms)
    assert_equal(0, mon.x[:])
    assert_equal(np.tile((1+np.arange(mon.y[:].shape[1]))*50*2*volt, (10, 1)),
                 mon.y[:])
    assert_equal(np.tile((1+np.arange(mon.y[:].shape[1]))*50*2*volt, (10, 1)),
                 mon.y2[:])
    assert all(np.var(mon.z[:], axis=1) > 0)  # variability over time
    assert all(np.var(mon.z[:], axis=0) > 0)  # variability over neurons
    assert all(np.var(mon.z2[:], axis=1) > 0)  # variability over time
    assert all(np.var(mon.z2[:], axis=0) > 0)  # variability over neurons


@attr('codegen-independent')
def test_poissoninput_errors():
    # Targeting non-existing variable
    G = NeuronGroup(10, '''x : volt
                           y : 1''')
    assert_raises(KeyError, lambda: PoissonInput(G, 'z', 100, 100*Hz, weight=1.0))

    # Incorrect units
    assert_raises(DimensionMismatchError,
                  lambda: PoissonInput(G, 'x', 100, 100*Hz, weight=1.0))
    assert_raises(DimensionMismatchError,
                  lambda: PoissonInput(G, 'y', 100, 100*Hz, weight=1.0*volt))

    # dt change
    old_dt = defaultclock.dt
    inp = PoissonInput(G, 'x', 100, 100*Hz, weight=1*volt)
    defaultclock.dt = 2 * old_dt
    net = Network(collect())
    assert_raises(NotImplementedError, lambda: net.run(0*ms))
    defaultclock.dt = old_dt


if __name__ == '__main__':
    # test_poissoninput()
    # restore_device()
    test_poissoninput_errors()
