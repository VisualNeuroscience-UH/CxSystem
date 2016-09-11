import brian2genn
import brian_genn_version
from brian_genn_version.tests.features import (Configuration, DefaultConfiguration,
                                   run_feature_tests, run_single_feature_test)
from brian_genn_versiongenn.correctness_testing import GeNNConfiguration
from brian_genn_version.tests.features.synapses import *
from brian_genn_version.tests.features.neurongroup import *
from brian_genn_version.tests.features.monitors import *
from brian_genn_version.tests.features.speed import *
from brian_genn_version.tests.features.input import *
from brian_genn_version.tests.features import CPPStandaloneConfiguration
from brian_genn_version import prefs

if __name__=='__main__':
    brian_genn_version.test([], test_codegen_independent=False, test_standalone='genn')
