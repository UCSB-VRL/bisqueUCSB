"""An extension of Python's option parser.

The ``OptionParser`` class is a subclass of Python's ``optparse.OptionParser``
which has two significant additions:

 * 

"""

import logging
import logging.config
import optparse

TRACE = 5   # Trace log level.

#### Exceptions
class LogLevelError(KeyError):
    def __init__(self, level):
        self.level = level
        msg = "logging level '%s' is undefined" % level
        KeyError.__init__(self, msg)

#### Utility functions
def resolve_log_level(level):
    """Map a log level name to its corresponding number.

    I take a logging level name, integer, or numeric string, and return the
    corresponding integer log level. Strings are converted to upper case
    before lookup.

    This implicitly calls ``add_trace_level`` to ensure the TRACE level is in
    the level map.
    
    Raise ``LogLevelError`` if the name is not registered in the logging
    system.
    """
    add_trace_level()
    if isinstance(level, int):
        return level
    level = level.upper()
    if level.isdigit():
        return int(level)
    elif level in logging._levelNames:
        return logging._levelNames[level]
    raise LogLevelError(level)
    
    
def add_trace_level():
    """Add a TRACE level (%s) to Python's logging system.""" 
    __doc__ %= TRACE
    if "TRACE" not in logging._levelNames:
        logging.addLevelName(TRACE, "TRACE")
    if not hasattr(logging.Logger, "trace"):
        logging.Logger.trace = trace

def trace(self, *args, **kw):
    """Log a message at TRACE level."""
    self.log(TRACE, *args, **kw)

#### LoggingOptionParser class
class OptionParser(optparse.OptionParser):
    """A subclass of Python's ``optparse.OptionParser`` with logging options.
    """

    def __init__(self, arg_names=None, varargs_name=None, 
        usage=None, description=None, **kw):
        """

        ``arg_names``: names of the positional arguments. There must be one
        non-option argument in the command line for each name.

        ``varargs_name``: name of an attribute to receive extra non-option
        arguments. If not specified, extra arguments will not be allowed.

        ``usage``, ``description``, ``\*\*kw``: passed directly to superclass
        constructor.
        """
        add_trace_level()
        self.arg_names = arg_names or []
        self.varargs_name = varargs_name
        self.nargs_error_messages = {}
        optparse.OptionParser.__init__(self, usage=usage,
            description=description, **kw)
        self.add_option("--log", action="append",
            metavar="LEVEL or LOGGER:LEVEL",
            help="set the default log level or specified logger's level")

    def parse(self, *args, **kw):
        """Parse the command line.

        This is a wrapper around the superclass's ``.parse_args`` method.
        Any method arguments are passed directly to the superclass.

        It takes the ``options`` object returned by the superclass, and
        adds attributes for the non-option arguments as specified by
        ``arg_names`` in the constructor. So if the specification 
        is ``["a", "b"]``, it puts the first non-option argument under 
        attribute ``a``, and the second under attribute ``b``. 
        
        If ``varargs_name`` was specified in the constructor, any additional
        arguments are put in a list under that attribute. (The list will be
        empty if there are no additional arguments.)

        If there are insufficient arguments to assign to all the ``arg_names``
        attributes, or if there are excess arguments and ``varargs_name``
        is not specified, abort the program with a usage error. If an error
        message for the actual number of non-option arguments has been
        registered via ``.on_nargs_error``, print that message, otherwise
        print a default message.
        """
        opts, args = self.parse_args(*args, **kw)
        def args_len_error():
            default = "wrong number of command-line arguments"
            msg = self.nargs_error_messages.get(len(args), default)
            self.error(msg)
        for i in range(len(self.arg_names)):
            try:
                setattr(opts, self.arg_names[i], args[i])
            except IndexError:
                args_len_error()
        if self.varargs_name:
            setattr(opts, self.varargs_name, args[len(self.arg_names):])
        elif len(args) > len(self.arg_names):
            args_len_error()
        return opts

    def on_nargs_error(self, nargs, message):
        """Register an error message for this number of non-option arguments.

        If ``.parse`` finds too many or too few non-option arguments, it
        aborts the program with a usage error. This method allows you to
        register specific error messages depending on the number of 
        non-option arguments on the command line.

        ``nargs``: the number of non-option arguments.
        
        ``message``: the error message.

        Registering an error message does *not* 
        error if that many arguments exist on the command line.
        """
        self.nargs_error_messages[nargs] = message

    def init_logging_from_ini(self, filename):
        logging.config.fileConfig(filename)

    def add_logging_options(self, debug=False, quiet=False, trace=False,
        sql=False):
        """Add logging options.

        Each argument (``debug``, ``quiet``, ``trace``, ``sql``) is a 
        boolean flag to create a boolean option by that name. So if
        ``debug`` is true, 

        ``debug``: if true, create a boolena "--debug" flag.

        Pass all arguments as keywords because more may be added later.
        Each one creates a corresponding option understood by
        ``.init_logging_from_options``. 
        """
        def add(name, help):
            self.add_option(name, action="store_true", help=help)
        if debug:
            add("--debug", "enable debug logging")
        if quiet:
            add("--quiet", "disable status logging")
        if trace:
            add("--trace", "enable trace logging")
        if sql:
            add("--sql", "log SQLAlchemy statements")

    def init_logging(self, opts, log_date=False, **basic_config_kw):
        basic_config_kw.setdefault("level", logging.INFO)
        basic_config_kw.setdefault("format", 
            "%(asctime)s %(levelname)s [%(name)s] %(message)s")
        if log_date:
            basic_config_kw.setdefault("datefmt", "%Y-%m-%d %H:%M:%S")
        else:
            basic_config_kw.setdefault("datefmt", "%H:%M:%S")
        logging.basicConfig(**basic_config_kw)
        self._init_logging_from_special_options(opts)
        if opts.log:
            self._init_logging_from_specs(opts.log)

    def error(self, message, *args):
        if args:
            message %= args
        OptionParser.error(self, message)

    #### Private methods


    def _init_logging_from_special_options(self, opts):
        if getattr(opts, "quiet", False):
            logging.getLogger().setLevel(logging.WARN)
        if getattr(opts, "debug", False):
            logging.getLogger().setLevel(logging.DEBUG)
        if getattr(opts, "trace", False):
            logging.getLogger().setLevel(0)
        if getattr(opts, "sql", False):
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    def _init_logging_from_specs(self, specs):
        try:
            for spec in specs:
                parts = spec.split(":", 1)
                if len(parts) == 1:
                    logger = "__main__"
                    level = parts[0]
                else:
                    logger = parts[0]
                    level = parts[1]
                level = resolve_log_level(level)
                logging.getLogger(logger).setLevel(level)
                if logger == "__main__":
                    # Set root logger to same level.
                    logging.getLogger().setLevel(level)
        except LogLevelError, e:
            parser.error("log level '%s' not defined" % e.level)
