'''
Brian's logging module.

Preferences
-----------
.. document_brian_prefs:: logging
'''
import atexit
import logging
import os
import shutil
import sys
import tempfile
import time
from warnings import warn

import numpy
try:
    import scipy
except ImportError:
    scipy = None
try:
    import scipy.weave as weave
except ImportError:
    try:
        import weave
    except ImportError:
        weave = None
import sympy

import brian_genn_version
from brian_genn_version.core.preferences import prefs, BrianPreference

from .environment import running_from_ipython

__all__ = ['get_logger', 'BrianLogger', 'std_silent']

#===============================================================================
# Logging preferences
#===============================================================================

def log_level_validator(log_level):
    log_levels = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')
    return log_level.upper() in log_levels

#: Translation from string representation to number
LOG_LEVELS = {'CRITICAL': logging.CRITICAL,
              'ERROR': logging.ERROR,
              'WARNING': logging.WARNING,
              'INFO': logging.INFO,
              'DEBUG': logging.DEBUG}

prefs.register_preferences('logging', 'Logging system preferences',
    delete_log_on_exit=BrianPreference(
        default=True,
        docs=    '''
        Whether to delete the log and script file on exit.
        
        If set to ``True`` (the default), log files (and the copy of the main
        script) will be deleted after the brian process has exited, unless an
        uncaught exception occured. If set to ``False``, all log files will be kept.
        ''',
        ),
    file_log_level=BrianPreference(
        default='DEBUG',
        docs='''
        What log level to use for the log written to the log file.
        
        In case file logging is activated (see `logging.file_log`), which log
        level should be used for logging. Has to be one of CRITICAL, ERROR,
        WARNING, INFO or DEBUG.
        ''',
        validator=log_level_validator),
    console_log_level=BrianPreference(
        default='WARNING',
        docs='''
        What log level to use for the log written to the console.
        
        Has to be one of CRITICAL, ERROR, WARNING, INFO or DEBUG.
        ''',
        validator=log_level_validator),
    file_log=BrianPreference(
        default=True,
        docs= '''
        Whether to log to a file or not.
        
        If set to ``True`` (the default), logging information will be written
        to a file. The log level can be set via the `logging.file_log_level`
        preference.
        '''),
    save_script=BrianPreference(
        default=True,
        docs= '''
        Whether to save a copy of the script that is run.
        
        If set to ``True`` (the default), a copy of the currently run script
        is saved to a temporary location. It is deleted after a successful
        run (unless `logging.delete_log_on_exit` is ``False``) but is kept after
        an uncaught exception occured. This can be helpful for debugging,
        in particular when several simulations are running in parallel.
        '''),
    std_redirection = BrianPreference(
        default=True,
        docs='''
        Whether or not to redirect stdout/stderr to null at certain places.
        
        This silences a lot of annoying compiler output, but will also hide
        error messages making it harder to debug problems. You can always
        temporarily switch it off when debugging. In any case, the output
        is saved to a file and if an error occurs the name of this file
        will be printed.
        '''
        ),                           
    )

#===============================================================================
# Initial setup
#===============================================================================

def _encode(text):
    ''' Small helper function to encode unicode strings as UTF-8. ''' 
    return text.encode('UTF-8')

# get the main logger
logger = logging.getLogger('brian_genn_version')
logger.propagate = False
logger.setLevel(logging.DEBUG)

# Log to a file
TMP_LOG = FILE_HANDLER = None
if prefs['logging.file_log']:
    try:
        # Temporary filename used for logging
        TMP_LOG = tempfile.NamedTemporaryFile(prefix='brian_debug_',
                                              suffix='.log', delete=False)
        TMP_LOG = TMP_LOG.name
        FILE_HANDLER = logging.FileHandler(TMP_LOG, mode='wt')
        FILE_HANDLER.setLevel(LOG_LEVELS[prefs['logging.file_log_level'].upper()])
        FILE_HANDLER.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)s: %(message)s'))
        logger.addHandler(FILE_HANDLER)
    except IOError as ex:
        warn('Could not create log file: %s' % ex)

# Save a copy of the script
TMP_SCRIPT = None
if prefs['logging.save_script']:
    if len(sys.argv[0]) and not running_from_ipython():
        try:
            tmp_file = tempfile.NamedTemporaryFile(prefix='brian_script_',
                                                   suffix='.py',
                                                   delete=False)
            with tmp_file:
                # Timestamp
                tmp_file.write(_encode(u'# %s\n' % time.asctime()))
                # Command line arguments
                tmp_file.write(_encode(u'# Run as: %s\n\n' % (' '.join(sys.argv))))
                # The actual script file
                # TODO: We are copying the script file as it is, this might clash
                # with the encoding we used for the comments added above
                with open(os.path.abspath(sys.argv[0]), 'rb') as script_file:
                    shutil.copyfileobj(script_file, tmp_file)    
                TMP_SCRIPT = tmp_file.name
        except IOError as ex:
            warn('Could not copy script file to temp directory: %s' % ex)

# create console handler with a higher log level
CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setLevel(LOG_LEVELS[prefs['logging.console_log_level'].upper()])
CONSOLE_HANDLER.setFormatter(logging.Formatter('%(levelname)-8s %(name)s: %(message)s'))

# add the handler to the logger
logger.addHandler(CONSOLE_HANDLER)

# We want to log all warnings
logging.captureWarnings(True)  # pylint: disable=E1101
# Manually connect to the warnings logger so that the warnings end up in
# the log file. Note that connecting to the console handler here means
# duplicated warning messages in the ipython notebook, but not doing so
# would mean that they are not displayed at all in the standard ipython
# interface...
warn_logger = logging.getLogger('py.warnings')
warn_logger.addHandler(CONSOLE_HANDLER)
if FILE_HANDLER is not None:
    warn_logger.addHandler(FILE_HANDLER)

# Put some standard info into the log file
logger.debug('Logging to file: %s, copy of main script saved as: %s' %
             (TMP_LOG, TMP_SCRIPT))
logger.debug('Python interpreter: %s' % sys.executable)
logger.debug('Platform: %s' % sys.platform)
version_infos = {'brian': brian_genn_version.__version__,
                 'numpy': numpy.__version__,
                 'scipy': scipy.__version__ if scipy else 'not installed',
                 'weave': weave.__version__ if weave else 'not installed',
                 'sympy': sympy.__version__,
                 'python': sys.version,
                 }
for _name, _version in version_infos.iteritems():
    logger.debug('{name} version is: {version}'.format(name=_name,
                                                       version=str(_version)))


UNHANDLED_ERROR_MESSAGE = ('Brian 2 encountered an unexpected error. '
'If you think this is bug in Brian 2, please report this issue either to the '
'mailing list at <http://groups.google.com/group/brian-development/>, '
'or to the issue tracker at <https://github.com/brian-team/brian_genn_version/issues>.')


def brian_excepthook(exc_type, exc_obj, exc_tb):
    '''
    Display a message mentioning the debug log in case of an uncaught
    exception.
    '''
    # Do not catch Ctrl+C
    if exc_type == KeyboardInterrupt:
        return
    BrianLogger.exception_occured = True

    message = UNHANDLED_ERROR_MESSAGE
    if TMP_LOG is not None:
        message += (' Please include this file with debug information in your '
                    'report: {} ').format(TMP_LOG)
    if TMP_SCRIPT is not None:
        message += (' Additionally, you can also include a copy '
                    'of the script that was run, available '
                    'at: {}').format(TMP_SCRIPT)
    if hasattr(std_silent, 'dest_fname_stdout'):
        message += (' You can also include a copy of the '
                    'redirected std stream outputs, available at '
                    '{stdout} and {stderr}').format(
                        stdout=std_silent.dest_fname_stdout,
                        stderr=std_silent.dest_fname_stderr)
    message += ' Thanks!'  # very important :)

    logger.error(message, exc_info=(exc_type, exc_obj, exc_tb))


def clean_up_logging():
    '''
    Shutdown the logging system and delete the debug log file if no error
    occured.
    '''
    logging.shutdown()
    if not BrianLogger.exception_occured and prefs['logging.delete_log_on_exit']:
        if TMP_LOG is not None:
            try:
                os.remove(TMP_LOG)
            except (IOError, OSError) as exc:
                warn('Could not delete log file: %s' % exc)
        if TMP_SCRIPT is not None:
            try:
                os.remove(TMP_SCRIPT)
            except (IOError, OSError) as exc:
                warn('Could not delete copy of script file: %s' % exc)
        std_silent.close()


sys.excepthook = brian_excepthook
atexit.register(clean_up_logging)


class HierarchyFilter(object):
    '''
    A class for suppressing all log messages in a subtree of the name hierarchy.
    Does exactly the opposite as the `logging.Filter` class, which allows
    messages in a certain name hierarchy to *pass*.
    
    Parameters
    ----------
    name : str
        The name hiearchy to suppress. See `BrianLogger.suppress_hierarchy` for
        details.
    '''

    def __init__(self, name):
        self.orig_filter = logging.Filter(name)
    
    def filter(self, record):
        '''
        Filter out all messages in a subtree of the name hierarchy.
        '''
        # do the opposite of what the standard filter class would do
        return not self.orig_filter.filter(record)


class NameFilter(object):
    '''
    A class for suppressing log messages ending with a certain name.
    
    Parameters
    ----------
    name : str
        The name to suppress. See `BrianLogger.suppress_name` for details.
    '''
    
    def __init__(self, name):
        self.name = name
    
    def filter(self, record):
        '''
        Filter out all messages ending with a certain name.
        '''
        # The last part of the name
        record_name = record.name.split('.')[-1]
        return self.name != record_name


class BrianLogger(object):
    '''
    Convenience object for logging. Call `get_logger` to get an instance of
    this class.
    
    Parameters
    ----------
    name : str
        The name used for logging, normally the name of the module.
    '''
    
    # : Class attribute to remember whether any exception occured
    exception_occured = False
    
    # : Class attribute for remembering log messages that should only be
    # : displayed once
    _log_messages = set()

    def __init__(self, name):
        self.name = name

    def _log(self, log_level, msg, name_suffix, once):
        '''
        Log an entry.
        
        Parameters
        ----------
        log_level : {'debug', 'info', 'warn', 'error'}
            The level with which to log the message.
        msg : str
            The log message.
        name_suffix : str
            A suffix that will be added to the logger name.
        once : bool
            Whether to suppress identical messages if they are logged again.
        '''
        name = self.name
        if name_suffix:
            name += '.' + name_suffix
        
        if once:
            # Check whether this exact message has already been displayed 
            log_tuple = (name, log_level, msg)
            if log_tuple in BrianLogger._log_messages:
                return
            else:
                BrianLogger._log_messages.add(log_tuple)
        
        the_logger = logging.getLogger(name)
        {'debug': the_logger.debug,
         'info': the_logger.info,
         'warn': the_logger.warn,
         'error': the_logger.error}.get(log_level)(msg)

    def debug(self, msg, name_suffix=None, once=False):
        '''
        Log a debug message.
        
        Parameters
        ----------
        msg : str
            The message to log.
        name_suffix : str, optional
            A suffix to add to the name, e.g. a class or function name.
        once : bool, optional
            Whether this message should be logged only once and not repeated
            if sent another time. 
        '''
        self._log('debug', msg, name_suffix, once)

    def info(self, msg, name_suffix=None, once=False):
        '''
        Log an info message.
        
        Parameters
        ----------
        msg : str
            The message to log.
        name_suffix : str, optional
            A suffix to add to the name, e.g. a class or function name.
        once : bool, optional
            Whether this message should be logged only once and not repeated
            if sent another time. 
        '''
        self._log('info', msg, name_suffix, once)

    def warn(self, msg, name_suffix=None, once=False):
        '''
        Log a warn message.
        
        Parameters
        ----------
        msg : str
            The message to log.
        name_suffix : str, optional
            A suffix to add to the name, e.g. a class or function name.
        once : bool, optional
            Whether this message should be logged only once and not repeated
            if sent another time. 
        '''
        self._log('warn', msg, name_suffix, once)

    def error(self, msg, name_suffix=None, once=False):
        '''
        Log an error message.
        
        Parameters
        ----------
        msg : str
            The message to log.
        name_suffix : str, optional
            A suffix to add to the name, e.g. a class or function name.
        once : bool, optional
            Whether this message should be logged only once and not repeated
            if sent another time. 
        '''
        self._log('error', msg, name_suffix, once)

    @staticmethod
    def _suppress(filterobj, filter_log_file):
        '''
        Apply a filter object to log messages.
        
        Parameters
        ----------
        filterobj : `logging.Filter`
            A filter object to apply to log messages.
        filter_log_file : bool
            Whether the filter also applies to log messages in the log file.
        '''
        CONSOLE_HANDLER.addFilter(filterobj)
        
        if filter_log_file:
            FILE_HANDLER.addFilter(filterobj)

    @staticmethod
    def suppress_hierarchy(name, filter_log_file=False):
        '''
        Suppress all log messages in a given hiearchy.
        
        Parameters
        ----------
        name : str
            Suppress all log messages in the given `name` hierarchy. For
            example, specifying ``'brian_genn_version'`` suppresses all messages logged
            by Brian, specifying ``'brian_genn_version.codegen'`` suppresses all messages
            generated by the code generation modules.
        filter_log_file : bool, optional
            Whether to suppress the messages also in the log file. Defaults to
            ``False`` meaning that suppressed messages are not displayed on
            the console but are still saved to the log file.
        '''
        
        suppress_filter = HierarchyFilter(name)
        
        BrianLogger._suppress(suppress_filter, filter_log_file)

    @staticmethod
    def suppress_name(name, filter_log_file=False):
        '''
        Suppress all log messages with a given name.
        
        Parameters
        ----------
        name : str
            Suppress all log messages ending in the given `name`. For
            example, specifying ``'resolution_conflict'`` would suppress
            messages with names such as
            ``brian_genn_version.equations.codestrings.CodeString.resolution_conflict`` or
            ``brian_genn_version.equations.equations.Equations.resolution_conflict``.
        filter_log_file : bool, optional
            Whether to suppress the messages also in the log file. Defaults to
            ``False`` meaning that suppressed messages are not displayed on
            the console but are still saved to the log file.
        '''
        suppress_filter = NameFilter(name)
        
        BrianLogger._suppress(suppress_filter, filter_log_file)

    @staticmethod
    def log_level_debug():
        '''
        Set the log level to "debug".
        '''
        CONSOLE_HANDLER.setLevel(logging.DEBUG)

    @staticmethod
    def log_level_info():
        '''
        Set the log level to "info".
        '''        
        CONSOLE_HANDLER.setLevel(logging.INFO)

    @staticmethod
    def log_level_warn():
        '''
        Set the log level to "warn".
        '''        
        CONSOLE_HANDLER.setLevel(logging.INFO)

    @staticmethod
    def log_level_error():
        '''
        Set the log level to "error".
        '''        
        CONSOLE_HANDLER.setLevel(logging.INFO)


def get_logger(module_name='brian_genn_version'):
    '''
    Get an object that can be used for logging.
    
    Parameters
    ----------
    module_name : str
        The name used for logging, should normally be the module name as
        returned by ``__name__``.
    
    Returns
    -------
    logger : `BrianLogger`
    '''

    return BrianLogger(module_name)


class catch_logs(object):
    '''
    A context manager for catching log messages. Use this for testing the
    messages that are logged. Defaults to catching warning/error messages and
    this is probably the only real use case for testing. Note that while this
    context manager is active, *all* log messages are suppressed. Using this
    context manager returns a list of (log level, name, message) tuples.
    
    Parameters
    ----------
    log_level : int or str, optional
        The log level above which messages are caught.
    
    Examples
    --------
    >>> logger = get_logger('brian_genn_version.logtest')
    >>> logger.warn('An uncaught warning') # doctest: +SKIP
    WARNING  brian_genn_version.logtest: An uncaught warning
    >>> with catch_logs() as l:
    ...    logger.warn('a caught warning')
    ...    print('l contains: %s' % l)
    ... 
    l contains: [('WARNING', 'brian_genn_version.logtest', 'a caught warning')]

    '''
    _entered = False
    
    def __init__(self, log_level=logging.WARN):
        self.log_list = []
        self.handler = LogCapture(self.log_list, log_level)
        self._entered = False
    
    def __enter__(self):
        if self._entered:
            raise RuntimeError('Cannot enter %r twice' % self)
        self._entered = True
        return self.log_list
    
    def __exit__(self, *exc_info):
        if not self._entered:
            raise RuntimeError('Cannot exit %r without entering first' % self)
        self.handler.uninstall()


class LogCapture(logging.Handler):
    '''
    A class for capturing log warnings. This class is used by
    `~brian_genn_version.utils.logger.catch_logs` to allow testing in a similar
    way as with `warnings.catch_warnings`.
    '''
    captured_loggers = ['brian_genn_version', 'py.warnings']

    def __init__(self, log_list, log_level=logging.WARN):
        logging.Handler.__init__(self, level=log_level)
        self.log_list = log_list
        # make a copy of the previous handlers
        self.handlers = {}
        for logger_name in LogCapture.captured_loggers:
            self.handlers[logger_name] = list(logging.getLogger(logger_name).handlers)
        self.install()

    def emit(self, record):
        # Append a tuple consisting of (level, name, msg) to the list of
        # warnings
        self.log_list.append((record.levelname, record.name, record.msg))
    
    def install(self):
        '''
        Install this handler to catch all warnings. Temporarily disconnect all
        other handlers.
        '''
        for logger_name in LogCapture.captured_loggers:
            the_logger = logging.getLogger(logger_name)
            for handler in self.handlers[logger_name]:
                the_logger.removeHandler(handler)
            the_logger.addHandler(self)
    
    def uninstall(self):
        '''
        Uninstall this handler and re-connect the previously installed
        handlers.
        '''
        for logger_name in LogCapture.captured_loggers:
            the_logger = logging.getLogger(logger_name)
            for handler in self.handlers[logger_name]:
                the_logger.addHandler(handler)


# See http://stackoverflow.com/questions/26126160/redirecting-standard-out-in-err-back-after-os-dup2
# for an explanation of how this function works. Note that 1 and 2 are the file
# numbers for stdout and stderr
class std_silent(object):
    '''
    Context manager that temporarily silences stdout and stderr but keeps the
    output saved in a temporary file and writes it if an exception is raised.
    '''
    dest_stdout = None
    dest_stderr = None
    def __init__(self, alwaysprint=False):
        self.alwaysprint = alwaysprint
        if not alwaysprint and std_silent.dest_stdout is None:
            if not prefs['logging.std_redirection']:
                self.alwaysprint = True
                return
            std_silent.dest_fname_stdout = tempfile.mktemp()
            std_silent.dest_fname_stderr = tempfile.mktemp()
            std_silent.dest_stdout = open(std_silent.dest_fname_stdout, 'w')
            std_silent.dest_stderr = open(std_silent.dest_fname_stderr, 'w')
        
    def __enter__(self):
        if not self.alwaysprint:
            sys.stdout.flush()
            sys.stderr.flush()
            self.orig_out_fd = os.dup(1)
            self.orig_err_fd = os.dup(2)
            os.dup2(std_silent.dest_stdout.fileno(), 1)
            os.dup2(std_silent.dest_stderr.fileno(), 2)

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.alwaysprint:
            std_silent.dest_stdout.flush()
            std_silent.dest_stderr.flush()
            if exc_type is not None:
                with open(std_silent.dest_fname_stdout, 'r') as f:
                    out = f.read()
                with open(std_silent.dest_fname_stderr, 'r') as f:
                    err = f.read()
            os.dup2(self.orig_out_fd, 1)
            os.dup2(self.orig_err_fd, 2)
            os.close(self.orig_out_fd)
            os.close(self.orig_err_fd)
            if exc_type is not None:
                sys.stdout.write(out)
                sys.stderr.write(err)
    
    @classmethod
    def close(cls):
        if std_silent.dest_stdout is not None:
            std_silent.dest_stdout.close()
            try:
                os.remove(std_silent.dest_fname_stdout)
            except (IOError, OSError):
                # TODO: this happens quite frequently - why?
                # The file objects are closed as far as Python is concerned,
                # but maybe Windows is still hanging on to them?
                pass
        if std_silent.dest_stderr is not None:
            std_silent.dest_stderr.close()
            try:
                os.remove(std_silent.dest_fname_stderr)
            except (IOError, OSError):
                pass
