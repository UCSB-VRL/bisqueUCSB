import os
import pkg_resources
import logging

log = logging.getLogger('bq.engine_service.condor_templates')


# Variables (mex_id, post_exec, post_args)
templateDAG =\
"""JOB ${mex_id}  ./${mex_id}.cmd
CONFIG ./${mex_id}.dag.config
SCRIPT POST ${mex_id} ${post_exec} ${post_args}
RETRY ${mex_id} 3
"""

templateDAGCONF = \
"""DAGMAN_LOG_ON_NFS_IS_ERROR = FALSE
"""


# Variables (script, script_args, transfers, staging, cmd_extra)
templateCMD = \
"""universe = vanilla
executable=${executable}
error = ./launcher.err
output = ./launcher.out
log = ./launcher.log
requirements = (Arch == "x86_64") && (TARGET.Name =!= LastMatchName1) && (OpSys == "LINUX") \\
%if extra_requirements:
   && (${extra_requirements})
%endif

on_exit_remove = (ExitBySignal == False)&&(ExitCode == 0)
should_transfer_files = YES
when_to_transfer_output = ON_EXIT_OR_EVICT
Notification = never
request_cpus = 1
request_memory = 1024

${condor_submit}
# store mex id for stopping
+MexID = "${mexes[0].mex_id}"

%for mex in mexes:
<%
    if not mex.executable:
        continue
%>
initialdir = ${mex.staging_path}
#transfer_input_files  = ${','.join(mex.transfers)}
#transfer_output_files = ${','.join(mex.transfers_out)}
arguments  = ${' '.join(mex.executable[1:])}
queue
%endfor
"""

LAUNCHER_SCRIPT = \
"""#!/usr/bin/env python
import sys
from bq.engine.controllers.module_run import ModuleRunner
if __name__ == "__main__":
    sys.exit(ModuleRunner().main())
"""


##### KGK  docker + condor
##### TODO
##### transfer_output_files =  module
##### transfer_input_files  =  matlab_launch or nothing...





CONDOR_TEMPLATES = {
    'condor.submit_template' : templateCMD,
    'condor.dag_config_template' : templateDAGCONF,
    'condor.dag_template' : templateDAG,
    }


# Stolen form Turbogears.view.base.py
# and modified for using in the condor engine.
#
def load_engines(wanted=None, defaults= {} ):
    """Load and initialize all templating engines.

    This is called during startup after the configuration has been loaded.
    You can call this earlier if you need the engines before startup;
    the engines will then be reloaded with the custom configuration later.

    """
    stdvars = {}
    get = defaults.get
    engine_options = {
        "cheetah.importhooks": get("cheetah.importhooks", False),
        "cheetah.precompiled": get("cheetah.precompiled", False),
#        "genshi.encoding": get("genshi.encoding", "utf-8"),
#        "genshi.default_doctype": get("genshi.default_doctype", None),
#        "genshi.lookup_errors": get("genshi.lookup_errors", "strict"),
#        "genshi.loader_callback" : get("genshi.loader_callback", None),
#         "json.skipkeys": get("json.skipkeys", False),
#         "json.sort_keys": get("json.sort_keys", False),
#         "json.check_circular": get("json.check_circular", True),
#         "json.allow_nan": get("json.allow_nan", True),
#         "json.indent": get("json.indent", None),
#         "json.separators": get("json.separators", None),
#         "json.ensure_ascii": get("json.ensure_ascii", False),
#         "json.encoding": get("json.encoding", "utf-8"),
#         "json.assume_encoding": get("json.assume_encoding", "utf-8"),
#         "json.descent_bases": get("json.descent_bases", get("turbojson.descent_bases", True)),
#        "kid.encoding": get("kid.encoding", "utf-8"),
#        "kid.assume_encoding": get("kid.assume_encoding", "utf-8"),
#        "kid.precompiled": get("kid.precompiled", False),
#        "kid.i18n.run_template_filter": get("i18n.run_template_filter", False),
#        "kid.i18n_filter": i18n_filter,
#        "kid.sitetemplate": get("tg.sitetemplate", "turbogears.view.templates.sitetemplate"),
#        "kid.reloadbases": get("kid.reloadbases", False),
        "mako.directories": get("mako.directories", []),
        "mako.output_encoding": get("mako.output_encoding", "utf-8")
    }
    engines = {}
    for entrypoint in pkg_resources.iter_entry_points(
            "python.templating.engines"):
        if wanted and entrypoint.name not in wanted:
            continue
        engine = entrypoint.load()
        engines[entrypoint.name] = engine(stdvars, engine_options)
    return engines



# Default templating engine
import mako
class CondorTemplates(object):
    """Condor script construction helper

    Used to construct condor execution scripts based
    on internal or user defined templates.

    you can define the condor submit script using
    [condor]
    condor.template_engine="mako" # cheetah, genshi..
    condot.dag_config_template=dag_config_filepath
    condot.dag_template=dag_config_filepath
    condot.submit_template=submit_filepath
    # any template engine initialization variables go here
    # i.e.
    # mako.directories = .

    Any variables contained in [condor_submit] will
    be added automatically to the condor_submitfile i.e.
    [condor_submit]
    requirements = (Memory>2048)
    request_cpus =2
    request_memory = 2048
    """
    @classmethod
    def mk_path(cls, name, mapping):
        return os.path.join('%(staging_path)s' % mapping,
                            name % mapping)

    def __init__(self, cfg):
        engine = cfg.get('condor.template_engine', 'mako')
        self.engines = load_engines(engine,  cfg)
        self.engine = self.engines[engine]
        self.template = {}
        for x in CONDOR_TEMPLATES.keys():
            path = cfg.get (x)
            if path and os.path.exists(path):
                self.template[x] = open (path).read()
            else:
                log.warn('template %s: %s not found: defaulting to internal version' % (x,path))
                self.template[x] = CONDOR_TEMPLATES[x]


    def create_file(self,output_path, template, mapping):
        try:
            f = open(output_path, 'w')

            # default templates are in mako
            if not os.path.exists(template):
                template = mako.template.Template(template)

            f.write(self.engine.render(template=template, info=mapping))
            f.close()
            return output_path
        except:
            x = mako.exceptions.text_error_template().render()
            log.exception('Bad template : %s' , x)
        return None

    def construct_launcher(self, mapping):
        self.launch_path = self.mk_path('%(mex_id)s_launch.py', mapping)
        if self.create_file(self.launch_path, LAUNCHER_SCRIPT, mapping):
            return self.launch_path
        return None


    def prepare_submit(self, mapping):
        """Create the condor required files"""
        self.dag_path = self.mk_path('%(mex_id)s.dag', mapping)
        self.create_file(self.dag_path,
                         self.template['condor.dag_template'], mapping)

        self.conf_path = self.mk_path('%(mex_id)s.dag.config', mapping)
        self.create_file(self.conf_path,
                         self.template['condor.dag_config_template'], mapping)

        self.submit_path = self.mk_path('%(mex_id)s.cmd', mapping)
        self.create_file(self.submit_path,
                         self.template['condor.submit_template'], mapping)
