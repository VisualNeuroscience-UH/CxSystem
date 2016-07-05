import types
import collections
import inspect

import sympy
from sympy import Function as sympy_Function
import numpy as np
from numpy.random import randn, rand

from brian_genn_version.core.preferences import prefs
from brian_genn_version.units.fundamentalunits import (fail_for_dimension_mismatch, Unit,
                                           Quantity, get_dimensions,
                                           DIMENSIONLESS)
from brian_genn_version.core.variables import Constant
import brian_genn_version.units.unitsafefunctions as unitsafe

__all__ = ['DEFAULT_FUNCTIONS', 'Function', 'implementation']


class Function(object):
    '''
    An abstract specification of a function that can be used as part of
    model equations, etc.

    Parameters
    ----------
    pyfunc : function
        A Python function that is represented by this `Function` object.
    sympy_func : `sympy.Function`, optional
        A corresponding sympy function (if any). Allows functions to be
        interpreted by sympy and potentially make simplifications. For example,
        ``sqrt(x**2)`` could be replaced by ``abs(x)``.
    arg_units : list of `Unit`, optional
        If `pyfunc` does not provide unit information (which typically means
        that it was not annotated with a `check_units` decorator), the
        units of the arguments have to specified explicitly using this
        parameter.
    return_unit : `Unit` or callable, optional
        Same as for `arg_units`: if `pyfunc` does not provide unit information,
        this information has to be provided explictly here. `return_unit` can
        either be a specific `Unit`, if the function always returns the same
        unit, or a function of the input units, e.g. a "square" function would
        return the square of its input units, i.e. `return_unit` could be
        specified as ``lambda u: u**2``.
    stateless : bool, optional
        Whether this function does not have an internal state, i.e. if it
        always returns the same output when called with the same arguments.
        This is true for mathematical functions but not true for ``rand()``, for
        example. Defaults to ``True``.

    Notes
    -----
    If a function should be usable for code generation targets other than
    Python/numpy, implementations for these target languages have to be added
    using the `~brian_genn_version.codegen.functions.implementation` decorator or using the
    `~brian_genn_version.codegen.functions.add_implementations` function.
    '''
    def __init__(self, pyfunc, sympy_func=None, arg_units=None,
                 return_unit=None, stateless=True):
        self.pyfunc = pyfunc
        self.sympy_func = sympy_func
        self._arg_units = arg_units
        self._return_unit = return_unit
        self.stateless = stateless
        if self._arg_units is None:
            if not hasattr(pyfunc, '_arg_units'):
                raise ValueError(('The Python function "%s" does not specify '
                                  'how it deals with units, need to specify '
                                  '"arg_units" or use the "@check_units" '
                                  'decorator.') % pyfunc.__name__)
            elif pyfunc._arg_units is None:
                # @check_units sets _arg_units to None if the units aren't
                # specified for all of its arguments
                raise ValueError(('The Python function "%s" does not specify '
                                  'the units for all of its '
                                  'arguments.') % pyfunc.__name__)
            else:
                self._arg_units = pyfunc._arg_units

        if self._return_unit is None:
            if not hasattr(pyfunc, '_return_unit'):
                raise ValueError(('The Python function "%s" does not specify '
                                  'how it deals with units, need to specify '
                                  '"return_unit" or use the "@check_units" '
                                  'decorator.') % pyfunc.__name__)
            elif pyfunc._return_unit is None:
                # @check_units sets _return_unit to None if no "result=..."
                # keyword is specified.
                raise ValueError(('The Python function "%s" does not specify '
                                  'the unit for its return '
                                  'value.') % pyfunc.__name__)
            else:
                self._return_unit = pyfunc._return_unit

        #: Stores implementations for this function in a
        #: `FunctionImplementationContainer`
        self.implementations = FunctionImplementationContainer(self)

    def is_locally_constant(self, dt):
        '''
        Return whether this function (if interpreted as a function of time)
        should be considered constant over a timestep. This is most importantly
        used by `TimedArray` so that linear integration can be used. In its
        standard implementation, always returns ``False``.

        Parameters
        ----------
        dt : float
            The length of a timestep (without units).

        Returns
        -------
        constant : bool
            Whether the results of this function can be considered constant
            over one timestep of length `dt`.
        '''
        return False

    def __call__(self, *args):
        return self.pyfunc(*args)


class FunctionImplementation(object):
    '''
    A simple container object for function implementations.

    Parameters
    ----------
    name : str, optional
        The name of the function in the target language. Should only be
        specified if the function has to be renamed for the target language.
    code : language-dependent, optional
        A language dependent argument specifying the implementation in the
        target language, e.g. a code string or a dictionary of code strings.
    namespace : dict-like, optional
        A dictionary of mappings from names to values that should be added
        to the namespace of a `CodeObject` using the function.
    dependencies : dict-like, optional
        A mapping of names to `Function` objects, for additional functions
        needed by this function.
    dynamic : bool, optional
        Whether this `code`/`namespace` is dynamic, i.e. generated for each
        new context it is used in. If set to ``True``, `code` and `namespace`
        have to be callable with a `Group` as an argument and are expected
        to return the final `code` and `namespace`. Defaults to ``False``.
    '''
    def __init__(self, name=None, code=None, namespace=None,
                 dependencies=None, dynamic=False):
        self.name = name
        self.dependencies = dependencies
        self._code = code
        self._namespace = namespace
        self.dynamic = dynamic

    def get_code(self, owner):
        if self.dynamic:
            return self._code(owner)
        else:
            return self._code

    def get_namespace(self, owner):
        if self.dynamic:
            return self._namespace(owner)
        else:
            return self._namespace


class FunctionImplementationContainer(collections.Mapping):
    '''
    Helper object to store implementations and give access in a dictionary-like
    fashion, using `CodeGenerator` implementations as a fallback for `CodeObject`
    implementations.
    '''
    def __init__(self, function):
        self._function = function
        self._implementations = dict()

    def __getitem__(self, key):
        '''
        Find an implementation for this function that can be used by the
        `CodeObject` given as `key`. Will find implementations registered
        for `key` itself (or one of its parents), or for the `CodeGenerator`
        class that `key` uses (or one of its parents). In all cases,
        implementations registered for the corresponding names qualify as well.

        Parameters
        ----------
        key : `CodeObject`
            The `CodeObject` that will use the `Function`

        Returns
        -------
        implementation : `FunctionImplementation`
            An implementation suitable for `key`.
        '''
        fallback = getattr(key, 'generator_class', None)

        for K in [key, fallback]:        
            if K in self._implementations:
                return self._implementations[K]
            else:
                name = getattr(K, 'class_name', None)
                if name in self._implementations:
                    return self._implementations[name]
            if hasattr(K, '__bases__'):
                for cls in inspect.getmro(K):
                    if cls in self._implementations:
                        return self._implementations[cls]
                    name = getattr(cls, 'class_name', None)
                    if name in self._implementations:
                        return self._implementations[name]

        raise KeyError(('No implementation available for {key}. '
                        'Available implementations: {keys}').format(key=key,
                                                                    keys=self._implementations.keys()))

    def add_numpy_implementation(self, wrapped_func, dependencies=None,
                                 discard_units=None):
        '''
        Add a numpy implementation to a `Function`.

        Parameters
        ----------
        function : `Function`
            The function description for which an implementation should be added.
        wrapped_func : callable
            The original function (that will be used for the numpy implementation)
        dependencies : list of `Function`, optional
            A list of functions this function needs.
        discard_units : bool, optional
            See `implementation`.
        '''
        if discard_units is None:
            discard_units = prefs['codegen.runtime.numpy.discard_units']

        # Get the original function inside the check_units decorator
        if hasattr(wrapped_func,  '_orig_func'):
            orig_func = wrapped_func._orig_func
        else:
            orig_func = wrapped_func

        if discard_units:
            new_globals = dict(orig_func.func_globals)
            # strip away units in the function by changing its namespace
            for key, value in new_globals.iteritems():
                if isinstance(value, Quantity):
                    new_globals[key] = np.asarray(value)
            unitless_func = types.FunctionType(orig_func.func_code, new_globals,
                                               orig_func.func_name,
                                               orig_func.func_defaults,
                                               orig_func.func_closure)
            self._implementations['numpy'] = FunctionImplementation(name=None,
                                                                    code=unitless_func,
                                                                    dependencies=dependencies)
        else:
            def wrapper_function(*args):
                if not len(args) == len(self._function._arg_units):
                    raise ValueError(('Function %s got %d arguments, '
                                      'expected %d') % (self._function.pyfunc.__name__, len(args),
                                                        len(self._function._arg_units)))
                new_args = [Quantity.with_dimensions(arg, get_dimensions(arg_unit))
                            for arg, arg_unit in zip(args, self._function._arg_units)]
                result = orig_func(*new_args)
                return_unit = self._function._return_unit
                if return_unit is 1 or return_unit.dim is DIMENSIONLESS:
                    fail_for_dimension_mismatch(result,
                                                return_unit,
                                                'The function %s returned '
                                                '{value}, but it was expected '
                                                'to return a dimensionless '
                                                'quantity' % orig_func.__name__,
                                                value=result)
                else:
                    fail_for_dimension_mismatch(result,
                                                return_unit,
                                                ('The function %s returned '
                                                 '{value}, but it was expected '
                                                 'to return a quantity with '
                                                 'units %r') % (orig_func.__name__,
                                                                return_unit),
                                                value=result)
                return np.asarray(result)

            self._implementations['numpy'] = FunctionImplementation(name=None,
                                                                    code=wrapper_function,
                                                                    dependencies=dependencies)

    def add_implementation(self, target, code, namespace=None,
                           dependencies=None, name=None):
        self._implementations[target] = FunctionImplementation(name=name,
                                                               code=code,
                                                               dependencies=dependencies,
                                                               namespace=namespace)

    def add_dynamic_implementation(self, target, code, namespace=None,
                                   dependencies=None, name=None):
        '''
        Adds an "dynamic implementation" for this function. `code` and `namespace`
        arguments are expected to be callables that will be called in
        `Network.before_run` with the owner of the `CodeObject` as an argument.
        This allows to generate code that depends on details of the context it
        is run in, e.g. the ``dt`` of a clock.
        '''
        if not callable(code):
            raise TypeError('code argument has to be a callable, is type %s instead' % type(code))
        if namespace is not None and not callable(namespace):
            raise TypeError('namespace argument has to be a callable, is type %s instead' % type(code))
        self._implementations[target] = FunctionImplementation(name=name,
                                                               code=code,
                                                               namespace=namespace,
                                                               dependencies=dependencies,
                                                               dynamic=True)

    def __len__(self):
        return len(self._implementations)

    def __iter__(self):
        return iter(self._implementations)


def implementation(target, code=None, namespace=None, dependencies=None,
                   discard_units=None):
    '''
    A simple decorator to extend user-written Python functions to work with code
    generation in other languages.

    Parameters
    ----------
    target : str
        Name of the code generation target (e.g. ``'weave'``) for which to add
        an implementation.
    code : str or dict-like, optional
        What kind of code the target language expects is language-specific,
        e.g. C++ code allows for a dictionary of code blocks instead of a
        single string.
    namespaces : dict-like, optional
        A namespace dictionary (i.e. a mapping of names to values) that
        should be added to a `CodeObject` namespace when using this function.
    dependencies : dict-like, optional
        A mapping of names to `Function` objects, for additional functions
        needed by this function.
    discard_units: bool, optional
        Numpy functions can internally make use of the unit system. However,
        during a simulation run, state variables are passed around as unitless
        values for efficiency. If `discard_units` is set to ``False``, input
        arguments will have units added to them so that the function can still
        use units internally (the units will be stripped away from the return
        value as well). Alternatively, if `discard_units` is set to ``True``,
        the function will receive unitless values as its input. The namespace
        of the function will be altered to make references to units (e.g.
        ``ms``) refer to the corresponding floating point values so that no
        unit mismatch errors are raised. Note that this system cannot work in
        all cases, e.g. it does not work with functions that internally imports
        values (e.g. does ``from brian_genn_version import ms``) or access values with
        units indirectly (e.g. uses ``brian_genn_version.ms`` instead of ``ms``). If no
        value is given, defaults to the preference setting
        `codegen.runtime.numpy.discard_units`.

    Notes
    -----
    While it is in principle possible to provide a numpy implementation
    as an argument for this decorator, this is normally not necessary -- the
    numpy implementation should be provided in the decorated function.

    Examples
    --------
    Sample usage::

        @implementation('cpp',"""
                    #include<math.h>
                    inline double usersin(double x)
                    {
                        return sin(x);
                    }
                    """)
        def usersin(x):
            return sin(x)
    '''

    def do_user_implementation(func):
        # Allow nesting of decorators
        if isinstance(func, Function):
            function = func
        else:
            function = Function(func)

        if discard_units:  # Add a numpy implementation that discards units
            if not (target == 'numpy' and code is None):
                raise TypeError(("'discard_units' can only be set for code "
                                 "generation target 'numpy', without providing "
                                 "any code."))
            function.implementations.add_numpy_implementation(wrapped_func=func,
                                                              dependencies=dependencies,
                                                              discard_units=discard_units)
        else:
            function.implementations.add_implementation(target, code=code,
                                                        dependencies=dependencies,
                                                        namespace=namespace)
        return function
    return do_user_implementation


class SymbolicConstant(Constant):
    '''
    Class for representing constants (e.g. pi) that are understood by sympy.
    '''
    def __init__(self, name, sympy_obj, value):
        super(SymbolicConstant, self).__init__(name, unit=Unit(1),
                                               value=value)
        self.sympy_obj = sympy_obj


################################################################################
# Standard functions and constants
################################################################################

# sympy does not have a log10 function, so let's define one
class log10(sympy_Function):
    nargs = 1

    @classmethod
    def eval(cls, args):
        return sympy.functions.elementary.exponential.log(args, 10)


DEFAULT_FUNCTIONS = {
    # numpy functions that have the same name in numpy and math.h
    'cos': Function(unitsafe.cos,
                    sympy_func=sympy.functions.elementary.trigonometric.cos),
    'sin': Function(unitsafe.sin,
                    sympy_func=sympy.functions.elementary.trigonometric.sin),
    'tan': Function(unitsafe.tan,
                    sympy_func=sympy.functions.elementary.trigonometric.tan),
    'cosh': Function(unitsafe.cosh,
                     sympy_func=sympy.functions.elementary.hyperbolic.cosh),
    'sinh': Function(unitsafe.sinh,
                     sympy_func=sympy.functions.elementary.hyperbolic.sinh),
    'tanh': Function(unitsafe.tanh,
                     sympy_func=sympy.functions.elementary.hyperbolic.tanh),
    'exp': Function(unitsafe.exp,
                    sympy_func=sympy.functions.elementary.exponential.exp),
    'log': Function(unitsafe.log,
                    sympy_func=sympy.functions.elementary.exponential.log),
    'log10': Function(unitsafe.log10,
                      sympy_func=log10),
    'sqrt': Function(np.sqrt,
                     sympy_func=sympy.functions.elementary.miscellaneous.sqrt,
                     arg_units=[None], return_unit=lambda u: u**0.5),
    'ceil': Function(np.ceil,
                     sympy_func=sympy.functions.elementary.integers.ceiling,
                     arg_units=[None], return_unit=lambda u: u),
    'floor': Function(np.floor,
                      sympy_func=sympy.functions.elementary.integers.floor,
                      arg_units=[None], return_unit=lambda u: u),
    # numpy functions that have a different name in numpy and math.h
    'arccos': Function(unitsafe.arccos,
                       sympy_func=sympy.functions.elementary.trigonometric.acos),
    'arcsin': Function(unitsafe.arcsin,
                       sympy_func=sympy.functions.elementary.trigonometric.asin),
    'arctan': Function(unitsafe.arctan,
                       sympy_func=sympy.functions.elementary.trigonometric.atan),
    'abs': Function(np.abs,
                    sympy_func=sympy.functions.elementary.complexes.Abs,
                    arg_units=[None], return_unit=lambda u: u),
    'sign': Function(pyfunc=np.sign, sympy_func=sympy.sign,
                     arg_units=[None], return_unit=1),
    # functions that need special treatment
    'rand': Function(pyfunc=rand, arg_units=[], return_unit=1, stateless=False),
    'randn': Function(pyfunc=randn, arg_units=[], return_unit=1, stateless=False),
    'clip': Function(pyfunc=np.clip, arg_units=[None, None, None],
                     return_unit=lambda u1, u2, u3: u1,),
    'int': Function(pyfunc=np.int_,
                    arg_units=[1], return_unit=1)
    }


DEFAULT_CONSTANTS = {'pi': SymbolicConstant('pi', sympy.pi, value=np.pi),
                     'e': SymbolicConstant('e', sympy.E, value=np.e),
                     'inf': SymbolicConstant('inf', sympy.oo, value=np.inf)}