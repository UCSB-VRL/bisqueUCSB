import pkg_resources
from paste.script import templates
from tempita import paste_script_template_renderer



class BisqueTemplate(templates.Template):
    """Bisque default template class"""

    _template_dir = 'templates'
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = 'Bisque Template'
    egg_plugins = ['PasteScript', 'Pylons', 'bqcore' ]
    vars = []
    def pre(self, command, output_dir, vars):
        """Called before template is applied."""
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        template_engine = vars.setdefault('template_engine', 'genshi')
        if template_engine == 'mako':
            # Support a Babel extractor default for Mako
            vars['babel_templates_extractor'] = \
                "('templates/**.mako', 'mako', None),\n%s#%s" % (' ' * 4,
                                                                 ' ' * 8)
        else:
            vars['babel_templates_extractor'] = ''

    def run(self, command, output_dirs, vars):
        vars.setdefault('einame', vars['project'].replace('-', '_'))
        print (vars )
        super(BisqueTemplate, self).run(command, output_dirs, vars)

class ServiceTemplate (BisqueTemplate):
    _template_dir = pkg_resources.resource_filename(
                            "bq.commands.templates",
                            "service")
    summary = "A bisque Service template"
    #use_cheetah = True


class CoreServiceTemplate (BisqueTemplate):
    _template_dir = pkg_resources.resource_filename(
                            "bq.commands.templates",
                            "core_service")
    summary = "Core Service"
    #use_cheetah = True


class ModuleTemplate (BisqueTemplate):
    _template_dir = pkg_resources.resource_filename(
                            "bq.commands.templates",
                            "module")
    summary = "Create a bisque module"
