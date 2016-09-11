'''
Brian2GeNN defines two different types of code objects, `GeNNCodeObject` and `GeNNUserCodeObject`.
`GeNNCodeObject` is the class of code objects that produce code snippets for GeNN neuron or synapse models.
`GeNNUserCodeObject` is the class of code objects that produce C++ code which is used as "user-side" code in GeNN. The class derives directly from Brian 2's `CPPStandaloneCodeObject`, using teh `CPPCodeGenerator`.
'''

from brian_genn_version.devices.cpp_standalone.codeobject import CPPStandaloneCodeObject, openmp_pragma, constant_or_scalar
from brian_genn_version.codegen.generators.cpp_generator import c_data_type, CPPCodeGenerator
from brian_genn_version.codegen.targets import codegen_targets
from brian_genn_version.codegen.templates import Templater
from .genn_generator import *

__all__ = ['GeNNCodeObject',
           'GeNNUserCodeObject']    

class GeNNCodeObject(CPPStandaloneCodeObject):
    '''
    Class of code objects that generate GeNN "code snippets"
    '''
    templater = Templater('brian2genn', env_globals={'c_data_type': c_data_type,
                                                     'openmp_pragma': openmp_pragma,
                                                     'constant_or_scalar': constant_or_scalar})
    generator_class = GeNNCodeGenerator

class GeNNUserCodeObject(CPPStandaloneCodeObject):
    '''
    Class of code objects that generate GeNN "user code"
    '''
    templater = CPPStandaloneCodeObject.templater.derive('brian2genn')
#, env_globals={'c_data_type': c_data_type,
#                                                     'openmp_pragma': openmp_pragma,
#                                                     'constant_or_scalar': constant_or_scalar})
    generator_class = CPPCodeGenerator

codegen_targets.add(GeNNCodeObject)
codegen_targets.add(GeNNUserCodeObject)
