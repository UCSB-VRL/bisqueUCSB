# Collection of routines to be used during the bisque setup process
#
#
#

import os,sys
import shutil
import functools
import string
from subprocess import call, check_call
from bq.util.configfile import ConfigFile
from bq.util.copylink import copy_link
from bq.util.paths import find_config_path, defaults_path
from bq.util.converters import asbool
from mako.template import Template

#BISQUE_DEPS = map (functools.partial(os.path.join, '../../external'), [ "bisque.jar", "jai_codec.jar", "jai_core.jar", "jai_imageio.jar", "clibwrapper_jiio.jar"])


class SetupError(Exception):
    pass

def verbose_call (*args, **kw):
    if kw.pop('verbose',None):
        print args
    return check_call (*args, **kw)


def needs_update (output, dependency):
    """True when output doesn't exist or dependency does exists and is newer than output
    """
    return not os.path.exists (output) or (os.path.exists (dependency) and os.path.getmtime (dependency) > os.path.getmtime (output))


def ensure_matlab(params):
    'make sure matlab is enabled and in the path'

    require('runtime.matlab_home', params)
    matlab_home = params['runtime.matlab_home']
    if matlab_home not in  os.environ['PATH']:
        os.environ['PATH'] = os.path.join(matlab_home,'bin') + os.pathsep + os.environ['PATH']
        print "ADDING MATLAB TO PATH->", os.environ['PATH']

def mcc (command,  *largs, **kw):
    where = kw.pop('where', None)
    if where:
        cwd = os.getcwd()
        os.chdir(where)
    mcc = ['mcc']
    mcc += largs
    mcc.append (command)
    print " ".join (mcc)
    try:
        ret = call (mcc, shell = (os.name == "nt"))
    except OSError:
        print "Couldn't execute command %s" % (" ".join(mcc))
        print "Please check your matlab enviroment. In particular check if mcc is available and callable from the shell"
        return False
    if where:
        os.chdir (cwd)
    return ret == 0

def mex_compile (command_list, where = None, **kw):
    """mex compile a command_list a list of arguments to the matlab mex_compiler

    :param: command_list - a list of command
    :param: where - directory in which mex will be compiled"""

    if where:
        cwd = os.getcwd()
        os.chdir(where)
    mex = ['mex']
    mex.extend (command_list)
    print " ".join (mex)
    try:
        ret = call (mex, shell = (os.name == "nt"))
    except OSError:
        print "Couldn't execute command %s" % (" ".join(mex))
        print "Please check your matlab enviroment. In particular check if mcc is available and callable from the shell"
        return False
    if where:
        os.chdir (cwd)
    return ret == 0

def matlab (command, where = None, params=None):
    'run matlab with a command'
    if not require('runtime.matlab_home', params):
        return False
    if where:
        cwd = os.getcwd()
        os.chdir(where)
    call (['matlab', '-nodisplay' , '-r', command])
    if where:
        os.chdir (cwd)
    return True


def copy_files (files, dest):
    'copy a list of files to a dest'
    for f in files:
        fname = os.path.basename (f)
        dname = os.path.join (dest, fname)
        if os.path.exists (dname): os.unlink (dname)
        copy_link (f, dest)


def matlab_setup(main_path, files = [], bisque_deps = False, dependency_dir = "mbuild",  params = {}, **kw):
    'prepare a matlab script for execution  by compiling with mcc'

    ensure_matlab(params)
    #mcc -m -C -R -nodisplay -R -nojvm -nocache maizeG.m
    #m Macro that generates a C stand-alone application. This is
    #equivalent to the options "-W main -T link:exe", which can be
    #found in the file
    #<MATLAB>/toolbox/compiler/bundles/macro_option_m.

    #C For stand-alone applications and shared libraries, generate a
    #separate CTF archive. If this option is not specified, the CTF
    #will be embedded within the stand-alone application or library.

    # -R Specify the run-time options for the MATLAB Common Runtime
    # (MCR) usage: mcc -m -R -nojvm,<args>,-nojit,<args> -v foo.m


    rest = []

    if isinstance(main_path, list):
        mpath = main_path.pop(0)
        rest = main_path
        main_path = mpath

    ext_map = { 'nt' : '.exe' }
    if main_path.endswith (".m"):
        main_path = main_path [0:-2]

    main_name = os.path.basename(main_path)
    #if bisque_deps:
    #    files.extend (BISQUE_DEPS)
    if len(files):
        copy_files (files, '.')
    if not os.path.exists (dependency_dir):
        os.mkdir (dependency_dir)

    source = main_path + '.m'
    main = main_name + ext_map.get(os.name, '')
    ctf  = main_name + '.ctf'
    if not (needs_update (ctf, source) or needs_update(main, source)
            or needs_update(ctf, "+bq") or needs_update(ctf, "+bim")):
        print "Skipping matlab compilation %s is newer than %s" % (ctf, source)
        return 0

    if  mcc(source, '-d', dependency_dir, '-m', '-C', '-R', '-nodisplay', '-R', '-nosplash', *rest):
        if os.path.exists (main):
            os.unlink (main)
        shutil.copyfile(os.path.join(dependency_dir, main), main)
        if os.path.exists (ctf):
            os.unlink (ctf)
        shutil.copyfile(os.path.join(dependency_dir, ctf), ctf)
        shutil.rmtree (dependency_dir)
        os.chmod (main, 0744)
        return 0
    return 1


def python_setup(scripts,  package_scripts =True, dependency_dir = 'pydist', params = None ):
    """compile python dependencies into a package using pyinstaller

    if package_script is true then a runner scripts will be generated
    for each script
    """
    cmd = [ 'pyinstaller', '--clean', '--noconfirm', '--distpath', dependency_dir ]
    #fr = bbfreeze.Freezer(dependency_dir)
    #fr.include_py = False
    if not isinstance(scripts, list):
        scripts = [ scripts ]

    # check if python code is newer than dependency_dir (pydist)
    #if not any  (needs_update(dependency_dir, x) for x in scripts):
    #    print "Skipping python  compilation %s is newer than %s" % (dependency_dir, scripts)
    #    return 0
    # if we need to compile, then compile cleanly
    if os.path.exists (dependency_dir):
        shutil.rmtree (dependency_dir)

    data = dict(params or {})
    for script in scripts:
        cmd.append (script)

    check_call (cmd)

    # read default path from site.cfg (TG config not initialized yet when this runs)
    #site_config = read_config('site.cfg', "app:main")
    #filename = os.path.abspath(os.path.join(site_config['bisque.paths.default'], 'templates/python_launcher.tmpl').replace('\\', '/'))
    filename = find_config_path ('templates/python_launcher.tmpl', config_dir='config-defaults').replace('\\', '/')
    print "TEMPLATE", filename
    for script in scripts:
        script_name = os.path.splitext(script)[0]
        data['script'] = os.path.join('.', dependency_dir, script_name, script_name)
        # THIS os.path.join needs to be replaced by pkg_resources or pkg_util
        # when the toplevel is packaged
        try:
            template = Template(filename=filename)
            with open(script_name, 'wb') as f:
                f.write(template.render(script = data['script']))
                os.chmod (script_name, 0744)
                return 0
        except Exception,e:
            print ("Could not create python launcher script %s" % e)


def ensure_binary(exe):
    'make sure executable is available to the module'
    # pylint: disable=no-name-in-module, import-error, no-member
    import distutils.spawn
    p = distutils.spawn.find_executable(exe)
    if p is None:
        raise SetupError("Executable required but not found: %s" % exe)

def require(expression, params, throws = True):
    """Require everying in expression

    Can be in simple variable in params or a callable of
    the form f (params) which returns boolean
    """

    valid = True
    params = params or {}
    if not isinstance(expression,list):
        expression = [ expression ]

    for e in expression:
        if callable(e):
            if not e(params):
                valid = False
                break
        if isinstance(e, basestring):
            if not bool(params.get(e, False)):
                valid = False
                break

    if not valid and throws:
        raise SetupError("required expression failed %s" % expression)

    return valid


DOCKERFILE="""FROM ${base_image}
MAINTAINER ${maintainer}
WORKDIR /module
$copy
CMD  [ "${command}" ]
"""

def docker_setup (image, command, base_image=None, params=None):
    #print "PARAMS:", params
    module_config = read_config('runtime-module.cfg', "command")
    docker_params = read_config('runtime-bisque.cfg', "docker")
    print "Docker ", docker_params

    # Load and setup the the environment for storage in docker container
    from bq.engine.controllers.command_run import BaseRunner

    runner = BaseRunner()
    runner.read_config() # loads runtime-module and runtime-bisuqe
    runner.load_section ("command", runner.module_cfg)
    runner.init_runstate(['staging_path=.', 'mex_id='])
    runner.create_environments()
    runner.process_config()
    runner.setup_environments(build=True)
    files = runner.mexes[0].files
    files =  [ s.strip() for s in files.split(',')] if isinstance (files, basestring) else files
    print "BUILDING", files
    runner.mexes[0].files = files

    docker_params =  runner.config
    command       =  runner.mexes[0].executable[1:]
    if base_image is None:
        import platform
        base_image = ":".join (platform.linux_distribution()[:2])

    # Must be lowercase
    if not asbool(docker_params.get('docker.enabled', False)):
        return
    image = docker_params.get ('docker.image')
    docker_hub = docker_params.get('docker.hub', '')
    docker_user = docker_params.get ('docker.hub.user', '')
    docker_pass = docker_params.get('docker.hub.password', '')
    docker_email = docker_params.get('docker.hub.email', '')
    docker_default_tag = docker_params.get ('docker.default_tag', None)
    if docker_default_tag and ':' not in image:
        image = "{}:{}".format (image, docker_default_tag)


    image = "/".join (filter (lambda x:x, [ docker_hub, docker_user, image.lower() ]))

    created_docker = False
    if not os.path.exists ('Dockerfile'):
        #files = [ x.strip() for x in module_config.get ('files','').split (",") ]
        files = runner.mexes[0].files
        dirs  = [ x for x in files if os.path.isdir(x) ]
        files = [ x for x in files if os.path.isfile(x) ]
        copies = []
        print "FILES", files
        if files:
            copies.append ( "COPY %s /module/" % " ".join (files) )
        for dr in dirs:
            copies.append ( "COPY %s /module/%s/ " % (dr, dr) )

        created_docker = True
        with open('Dockerfile', 'w') as f:
            maintainer = docker_params.get ('docker.maintainer', 'nobody@example.com')
            # check for configured base i.e docker.image.matlab_runtime
            base = docker_params.get ('docker.image.%s' % base_image, base_image)
            f.write (string.Template (DOCKERFILE).safe_substitute(base_image=base_image,
                                                                  command=command,
                                                                  maintainer=maintainer,
                                                                  copy = "\n".join (copies) ))

    print "Calling", " ".join (['docker', 'build', '-q', '-t', image , '.'])
    check_call(['docker', 'build',  '-t',  image, '.'])

    if docker_hub:
        print "Pushing %s " % ( image )
        if docker_user and docker_pass:
            check_call (['docker', 'login', '-u', docker_user, '-p', docker_pass, '-e', docker_email, docker_hub])
        check_call(['docker', 'push', image])
    if created_docker:
        os.unlink ('Dockerfile')


def read_config(filename, section= None):
    if not os.path.exists (filename):
        filename = find_config_path(filename)

    print "READING", filename
    conf =  ConfigFile(filename).get (section, asdict = True)
    config_dir = os.path.dirname (filename)
    conf['bisque.path.config'] = config_dir
    print "CONFIG", config_dir

    return conf


def load_config(filename, section= None):
    if not os.path.exists (filename):
        filename = find_config_path(filename)

    print "LOADING", filename
    return ConfigFile(filename)



class BisqueBuilder(object):
    def __init__(self, **kw):
        pass

    def python_setup (self, **kw):
        python_setup (**kw)

    def matlab_setup (self, **kw):
        matlab_setup (**kw)

    def docker_setup (self, **kw):
        docker_setup(**kw)
