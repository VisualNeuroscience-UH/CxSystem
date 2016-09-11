'''
Definitions of theconfiguration for correctness testing.
'''
import brian_genn_version
import os
import shutil
import sys
import brian2genn
from brian_genn_version.tests.features import (Configuration, DefaultConfiguration,
                                   run_feature_tests, run_single_feature_test)

__all__ = ['GeNNConfiguration',
           'GeNNConfigurationOptimized']

class GeNNConfiguration(Configuration):
    name = 'GeNN'
    def before_run(self):
        brian_genn_version.prefs.reset_to_defaults()
        brian_genn_version.prefs.codegen.loop_invariant_optimisations = False
        brian_genn_version.prefs.devices.genn.unix_compiler_flags=''
        windows_compiler_flags=''
        brian_genn_version.set_device('genn')
        
    def after_run(self):
        if os.path.exists('GeNNworkspace'):
            shutil.rmtree('GeNNworkspace')
        brian_genn_version.device.build(directory='GeNNworkspace', compile=True, run=True,
                            use_GPU=True)

class GeNNConfigurationOptimized(Configuration):
    name = 'GeNN'
    def before_run(self):
        brian_genn_version.prefs.reset_to_defaults()
        brian_genn_version.prefs.codegen.loop_invariant_optimisations = False
        brian_genn_version.set_device('genn')
        
    def after_run(self):
        if os.path.exists('GeNNworkspace'):
            shutil.rmtree('GeNNworkspace')
        brian_genn_version.device.build(directory='GeNNworkspace', compile=True, run=True,
                            use_GPU=True)

