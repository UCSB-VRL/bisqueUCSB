#
#
#
import logging

class ModuleEnvironmentError(Exception):
    """For errors while setting up or tearing down environments
    """
    pass


class ModuleEnvironment(object):
    """The default Env (users can derive from this) which
    reads the module config
    """
    name = ""

    def __init__(self, runner):
        pass

    def setup_environment(self, runner):
        """Prepare the module enviroment before the actual run
        """

    def teardown_environment(self, runner):
        """Cleanup the module environentm
        """


def strtobool(x):
    return {"true": True, "false": False}.get(x.lower(), False)

def strtolist(x, sep=','):
    if isinstance(x, basestring):
        return [ s.strip() for s in x.split(sep)]
    return x

class BaseEnvironment (ModuleEnvironment):
    """A BaseEnvironment is a helper script for running bisque modules.

    An enviroment provide a framework for constructing a runtime
    environment for a module that will work several platforms,

    Base class for creating module environment which can process MEX
    amd MODULE arguments.
    """
    name   ="Base"
    config = {}   # Element of this environment found in the configuration file

    def __init__(self, runner):
        super(BaseEnvironment, self).__init__(runner)
        self.log = logging.getLogger ('bq.engine.base_env')


    def process_config (self, runner):
        """An environment is allowed to operate on runners configuration
        variables before the actual command is run.

        The default version ensure the types of the config variables
        is respected and the defaults values are setup.  Some environments
        will take over this responsibility
        """
        for k,v in self.config.items():
            if  hasattr(runner, k):
                v = self.strtotype (getattr(runner, k), type(v))
            setattr(runner, k, v)

    def strtotype(self, value, value_type):
        if value_type==str:
            return value
        if value_type==bool:
            return strtobool(value)
        if value_type==list:
            return strtolist(value)

        raise ModuleEnvironmentError("Illegal conversion of %s to type %s" % (value, value_type))

    def parse_mex_inputs (self, module, mex):
        """Scan the module definition and the mex and match input
        parameters creating a list in the proper order
        """

        # Pass through module definition looking for inputs
        # for each input find the corresponding tag in the mex
        # Warn about missing inputs
        input_nodes = []
        for mi in module.xpath ('./tag[@name="formal-input"]'):
            # pull type off and markers off
            param_name = mi.get('value').split(':')[0].strip('$')
            found = mex.xpath ('./tag[@name="%s"]'%param_name)
            if not found:
                self.log.warn ('missing input for parameter %s' , mi.get('value'))
            input_nodes += found
        for i, node in enumerate(input_nodes):
            if 'index' in node.keys():
                continue
            node.set ('index', str(i))

        input_nodes.sort (lambda n1,n2: cmp(int(n1.get('index')), int(n2.get('index'))))
        return input_nodes


    def setup_environment(self, runner):
        """Prepare the module enviroment before the actual run
        """

    def teardown_environment(self, runner):
        """Cleanup the module environentm
        """
