#import shutil
#import urlparse
import os
import sys
#import tarfile
#import urllib2
#import glob
#from urlparse import urlparse

import paver
from paver.easy import path, Bunch, options, sh, task, needs, consume_args
import paver.misctasks
from paver.setuputils import setup as python_setup
from setuptools.dist import Distribution

paver.setuputils.install_distutils_tasks()


def generate_data_files (toplevel, filters=None):
    'make a pair (dir, [list-of-files] ) for all dirs in toplevel'
    return ([ (toplevel, list (path(toplevel).walkfiles())) ]
            + [ (str(d), list ( d.walkfiles())) for d in path(toplevel).walkdirs() ])




options(
    setup = dict (
       name='BisQue',
        version="0.5.9",
        author="Center for BioImage Informatics, UCSB",
        author_email = "info@bioimage.ucsb.edu",
        #data_files = [ ('config-defaults', glob.glob ('config-defaults/*') )],
        #data_files =  generate_data_files ('./contrib') +  generate_data_files ('./config-defaults'),
    ),
    virtualenv=Bunch(
        packages_to_install=['pip'],
        paver_command_line="required"
    ),
    sphinx = Bunch(
        builddir = "build",
        sourcedir = "docs/source"
        ),
    license=Bunch(
        extensions = set([
                ("py", "#"), ("js", "//")
                ]),
        exclude=set([
                './ez_setup',
                './data',
                './tg2env',
                './docs',
                # Things we don't want to add our license tag to
                ])
        ),
)

feature_subdirs = ['bqfeature' ]
server_subdirs=['bqapi', 'bqcore', 'bqserver', 'bqengine' ]
engine_subdirs=['bqapi', 'bqcore', 'bqengine' ]

PREINSTALLS = {'features' : ['numpy==1.9.1',
                             '-r bqfeature/requirements.txt',
                             'tables==3.1.1']
               }

all_packages = set(feature_subdirs + server_subdirs + engine_subdirs)

#################################################################


def getanswer(question, default, help=None):
    import textwrap
    if "\n" in question:
        question = textwrap.dedent (question)
    while 1:
        ans =  raw_input ("%s [%s]? " % (question, default))

        if ans=='?':
            if help is not None:
                print textwrap.dedent(help)
            else:
                print "Sorry no help available currently."
            continue
        y_n = ['Y', 'y', 'N', 'n']
        if default in y_n and ans in y_n:
            ans = ans.upper()

        if ans == '': ans = default
        break
    return ans

########################################################


def process_options(options):
    if hasattr(options, 'installing'):
        return
    installing = None
    if len(options.args) :
        installing = options.args[0]
    else:
        installing = 'server'

    if installing not in ('engine', 'server', 'features', 'all'):
        installing =  getanswer("install [server, engine or features", "engine",
"""server installs component to run a basic bisque server
engine will provide just enough components to run a module engine,
all will install everything including the feature service""")

    if installing not in ('engine', 'server', 'features', 'all'):
        print "Must choose 'engine', 'server', or 'features'"
        sys.exit(1)

    preinstalls = PREINSTALLS.get (installing, [])

    for package in preinstalls:
        #sh ("pip install -i https://biodev.ece.ucsb.edu/py/bisque/dev/+simple %s" % package)
        sh ("pip install %s" % package)

    subdirs  = dict (engine = engine_subdirs,
                     server = server_subdirs,
                     features = feature_subdirs,
                     all = all_packages) [ installing]
    print "installing all components from  %s" % subdirs
    options.subdirs = subdirs
    options.installing = installing




def install_prereqs (options):
    "Ensure required packages are installed"
    pass

def install_postreqs (options):
    "Install or Modify any packages post installation"
    pass


#############################################################
#@cmdopts([('engine', 'e', 'install only the engine')])
@task
@consume_args
def setup(options):
    'install local version and setup local packages'
    process_options(options)
    install_prereqs(options)
    setup_developer(options)
    #install_postreqs(options)
    print '\nNow run:\nbq-admin setup %s' % ( 'engine' if options.installing =='engine' else '' )



@task
@consume_args
def setup_developer(options):
    process_options(options)
    #top = os.getcwd()
    for dr in options.subdirs:
        app_dir = path('.') / dr
        if os.path.exists(app_dir):
            #sh('pip install -i https://biodev.ece.ucsb.edu/py/bisque/dev/+simple -e %s' % app_dir)
            sh('pip install -e %s' % app_dir)
            #os.chdir(app_dir)
            #sh('python setup.py develop')
            #os.chdir(top)

#@task
#@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
#def sdist():
#    """Overrides sdist to make sure that our setup.py is generated."""
#    sh('tar -czf dist/bisque-modules-%s.tgz --exclude="*.pyc" --exclude="*~" --exclude="*.ctf" --exclude="*pydist" --exclude="UNPORTED" modules' % VERSION)





@task
@consume_args
def package_wheels(options):
    if not os.path.exists('./dist'):
        os.makedirs ('./dist')
    top = os.getcwd()
    for app_dir in all_packages:
        os.chdir(app_dir)
        sh('python setup.py bdist_wheel --dist-dir=../dist')
        os.chdir(top)
    sh('python setup.py bdist_wheel --dist-dir=./dist')

@task
@consume_args
def upload(options):
    top = os.getcwd()
    for app_dir in all_packages:
        os.chdir(app_dir)
        sh('devpi upload  --no-vcs --format=bdist_wheel')
        os.chdir(top)
    sh('devpi upload  --no-vcs --format=bdist_wheel')




#@task
#def test():
#    os.chdir('bqcore')
#    sh('python setup.py test')

@task
def distclean():
    'clean out all pyc and backup files'
    sh('find . -name "*.pyc" | xargs rm ')
    sh('find . -name "*~" | xargs rm ')

@task
def package():
    'create distributable packages'
    pass

@task
@needs('paver.doctools.html')
def html(options):
    """Build docs"""
    destdir = path('docs/html')
    if destdir.exists():
        destdir.rmtree()
    builtdocs = path("docs") / options.builddir / "html"
    builtdocs.move(destdir)

@task
def pastershell():
    'setup env for paster shell config/shell.ini'
    bisque_info = path('BisQue.egg-info')
    if not bisque_info.exists():
        sh ('paver egg_info')
    path ('bqcore/bqcore.egg-info/paster_plugins.txt').copy (bisque_info)
    sh ('pip install ipython==0.10')


@task
@consume_args
def pylint(options):
    import pkgutil
    import ConfigParser
    from bq.util.paths import site_cfg_path
    import bq
    site_cfg = ConfigParser.ConfigParser ()
    site_cfg.read (site_cfg_path())
    share_path = site_cfg.get ('app:main', 'bisque.paths.share')
    #args = 'bqcore/bq bqserver/bq bqengine/bq bqfeature/bq'
    opts = []
    args = []
    for arg in options.args:
        if arg.startswith('-'):
            opts.append (arg)
        else:
            args.append (arg)
    if args:
        args = " ".join(args)
    else:
        package = bq
        prefix = package.__name__ + "."
        args = [ modname for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix) ]
        args = " ".join(args)
    opts = " ".join(opts)
    sh('pylint --rcfile=%s --load-plugins=bq_pylint %s %s' % (os.path.join(share_path, '.pylintrc'), opts, args))

@task
@consume_args
def pylint_modules(options):
    args = 'modules/*/*.py'
    if options.args:
        args = " ".join(options.args)
    if os.name != 'nt':
        sh('PYTHONPATH=bqcore/bq:bqserver/bq:bqengine/bq:bqfeature/bq pylint %s --rcfile=bqcore/pylint.rc' % args)
    else:
        sh('set PYTHONPATH=bqcore\\bq;bqserver\\bq;bqengine\\bq;bqfeature\\bq & pylint %s --rcfile=bqcore\\pylint.rc' % args)


@task
@consume_args
def pyfind(options):
    args = 'bqcore/bq bqserver/bq bqengine/bq bqfeature/bq'
    sh ("find %s -name '*.py' | xargs fgrep %s" % (args, " ".join(options.args)))



class PureDistribution(Distribution):
    def is_pure(self):
        return True



@task
#@needs('setuptools.command.install')
@consume_args
def install(options):
    python_setup(
        name='BisQue',
        version="0.5.9",
        author="Center for BioImage Informatics, UCSB",
        author_email = "info@bioimage.ucsb.edu",
        distclass = PureDistribution,
        classifiers = [
            'Private :: Do Not Upload',
    #        "Development Status :: 5 - Production/Stable",
    #        "Framework :: TurboGears :: Applications",
    #        "Topic :: Scientific/Engineering :: Bio-Informatics",
    #        "License :: OSI Approved :: BSD License",
            ],
        #package_data=find_package_data(),
        include_package_data = True,
        data_files =  generate_data_files ('./contrib') +  generate_data_files ('./config-defaults'),
        #packages=find_packages(exclude=['ez_setup']),
        #packages=["bq"],
        zip_safe=False,
        setup_requires=["PasteScript >= 1.7"],
        paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'bqengine'],
        #build_top=path("build"),
        #        build_dir=lambda: options.build_top / "bisque05",
        license=Bunch(
            extensions = set([
                    ("py", "#"), ("js", "//")
                    ]),
            exclude=set([
                    './ez_setup',
                    './data',
                    './tg2env',
                    './docs',
                    # Things we don't want to add our license tag to
                    ])
            ),
        )
    #print "PATH=", os.environ.get ('PATH')
    #print "ARGS", options.args
    #options.args[0] = 'server'
    #setup(options)
