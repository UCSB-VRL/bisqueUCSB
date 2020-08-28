import os
import sys
import re
import pkg_resources
import optparse
import shutil

from paste.script import templates, create_distro

######################################################
# Create Command


beginning_letter = re.compile(r"^[^a-z]*")
valid_only = re.compile(r"[^a-z0-9_]")

class create(object):
    desc = "Create a template for a bisquik subproject"

    templates = "service"
    package = None
    name = None
    mount = None
    cmd_args = []

    def __init__(self, version):
        parser = optparse.OptionParser(
                    usage="%prog create [options] [project name]",
                    version="%prog " + version)

        parser.add_option("-t", "--templates",
                          help="user specific templates",
                          dest="templates", default = self.templates)
        parser.add_option("-p", "--package",
                          help="Set service package name",
                          dest="package")
        parser.add_option('-m', '--mount',
                          help="create a core system package",
                          dest="mount")
        options, args = parser.parse_args()
#        if len(args) != 1:
#            parser.error("incorrect number of arguments")

        self.__dict__.update (options.__dict__)
        if args:
            self.name = args[0]

    def run(self):
        """Create a Bisque Service/Module template"""

        # Get to toplevel directory name i.e. the project
        while not self.name:
            self.name = raw_input("Enter bisque project [egg] name: ")

        # The package name to be used internally
        while not self.package:
            package = self.name.lower()
            package = beginning_letter.sub("", package)
            package = valid_only.sub("", package)
            self.package = raw_input("Enter [python] package name  [%s]: " % package)
            if not self.package:
                self.package = package

        while not self.mount:
            mount = self.package.lower()
            mount = beginning_letter.sub("", mount)
            mount = valid_only.sub("", mount)
            self.mount = raw_input("Enter mount point (url point) [%s]: " % mount)
            if not self.mount:
                self.mount = mount



        command = create_distro.CreateDistroCommand("create")
        for template in self.templates.split(" "):
            self.cmd_args.append("--template=%s" % template)
        self.cmd_args.append(self.name)
        # Variables
        self.cmd_args.append("package=%s" % self.package)
        self.cmd_args.append("mount=%s" % self.mount)

        command.run(self.cmd_args)

class createService(create):
    desc = "Create a bisque service"
    templates = "bisque_service"
    package = None
    name = None

class createCoreService(create):
    desc = "Create a bisque core service.. it will be under  <name>/<package>/bq.<package>"
    templates = "bisque_core"
    name = None
    def run(self):
        if not os.path.exists('bqcore'):
            print "Must be run in the top level Bisque directory"
            sys.exit(1)
        super(createCoreService, self).run()


class createModule(create):
    desc = "Create a blank bisque analysis module"
    templates = "bisque_module"
    package = None
    name = None




