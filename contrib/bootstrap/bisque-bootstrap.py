#!/usr/bin/env python
import os
import sys
import subprocess
import argparse
import glob
import shutil
import urllib
import tarfile

VENV_SOURCE="https://pypi.python.org/packages/source/v/virtualenv/virtualenv-14.0.6.tar.gz"
PIP_SYS_INSTALL = [ 'pip', 'install', '-U' ]

if os.name == 'nt':
    PIP_LIST=[
        #('numpy-1.10.4+mkl-cp27-none-win_amd64.whl', 'https://biodev.ece.ucsb.edu/~bisque/wheels/numpy-1.10.4+mkl-cp27-none-win_amd64.whl'),
        #('numexpr-2.4.6-cp27-none-win_amd64.whl', 'https://biodev.ece.ucsb.edu/~bisque/wheels/numexpr-2.4.6-cp27-none-win_amd64.whl'),
        #('tables-3.2.2-cp27-none-win_amd64.whl', 'https://biodev.ece.ucsb.edu/~bisque/wheels/tables-3.2.2-cp27-none-win_amd64.whl'),
    ]
    PIP_INDEX = 'https://biodev.ece.ucsb.edu/py/bisque/win64/+simple/'
    PIP_INSTALL = [ 'pip', 'install', '-U',  '-i', PIP_INDEX ]
else:
    PIP_LIST = [
        #('numpy', None),
        #('numexpr', None),
        #('tables', None),
    ]
    PIP_INDEX = 'https://biodev.ece.ucsb.edu/py/bisque/dev/+simple/'
    PIP_INSTALL = [ 'pip', 'install', '-U',  '-i', PIP_INDEX ]

shell = False
if os.name == 'nt':
    shell = True

# installs pip wheels from a URL or pypy
def install_package(filename, URL, command=None):
    print 'Installing %s\n'%filename
    if URL is not None:
        urllib.urlretrieve (URL, filename)
    print command
    subprocess.call (command, shell=shell)
    if URL is not None:
        try:
            os.remove(filename)
        except OSError:
            print 'Warning: could not remove %s\n'%filename

# installs package using python setup file
def install_setup(filename, URL=None):
    return install_package(filename, URL, ['python', filename])

# installs package using easy_install
def install_easy(filename, URL=None):
    return install_package(filename, URL, ['easy_install', filename])

# installs package using pip wheels from a URL or pypy
def install_pip(filename, URL=None):
    return install_package(filename, URL, PIP_INSTALL + [ filename ])

def install_sys_pip(filename, URL=None):
    return install_package(filename, URL, PIP_SYS_INSTALL + [ filename ])

def install_source(filename, URL, command=None):
    if URL is not None:
        urllib.urlretrieve (URL, filename)

    tar = tarfile.open (filename)
    names = tar.getnames()
    tar.extractall()
    tar.close()
    vdir = names[0]
    print "Extracted to: %s"%vdir

    if command is not None:
        subprocess.call (command, shell=shell)
    if URL is not None:
        try:
            os.remove(filename)
        except OSError:
            print 'Warning: could not remove %s\n'%filename
    return vdir

def run_bootstrap():
    parser = argparse.ArgumentParser(description='Boostrap bisque')
    parser.add_argument("--repo", default="http://biodev.ece.ucsb.edu/hg/bisque-stable")
    parser.add_argument("bqenv", nargs="?", default="bqenv")
    parser.add_argument('install', nargs="?", default='server', choices=['server', 'engine'])
    args = parser.parse_args()


    # check python version
    if not sys.version_info[:2] == (2, 7):
        print "BisQue requires python 2.7.X but found %s, aborting install..."%(sys.version)
        if os.name == 'nt':
            print "We suggest installing ActivePython 2.7 from http://www.activestate.com/"
        return 1

    # check 64bit python
    if sys.maxsize <= 2**32:
        print "BisQue requires 64bit python, aborting install..."
        return 1


    print "\n----------------------------------------------------------"
    print 'Fetch virtual environment for BisQue installation'
    print "----------------------------------------------------------\n"
    vdir = install_source(os.path.basename(VENV_SOURCE), VENV_SOURCE)

    print "\n----------------------------------------------------------"
    print 'Creating virtual environment for BisQue installation'
    print "----------------------------------------------------------\n"

    if os.name != 'nt':
        r = subprocess.call(["python", "%s/virtualenv.py"%vdir, args.bqenv])
        activate = os.path.join(args.bqenv, 'bin', 'activate_this.py')
    else:
        # due to a bug in the windows python (~2.7.8) virtual env can't install pip and setuptools
        # so we have to first create a virtualenv without setuptools and pip and then
        # install them into the virtualenv
        r = subprocess.call(["python", "%s/virtualenv.py"%vdir, args.bqenv, '--no-setuptools'])
        activate = os.path.join(args.bqenv, 'Scripts', 'activate_this.py')
    if r != 0:
        print 'virtualenv is missing, it needs to be pre-installed with your python version, aborting...'
        return

    print 'Activating virtual environment using: %s\n'%activate
    try:
        execfile (activate, dict(__file__=activate))
    except Exception:
        print "Could not activate Virtual Environment, it needs to be pre-installed with your python version..."
        return 1

    os.environ['VIRTUAL_ENV'] = os.path.abspath(args.bqenv)

    # install pip and setuptools if under windows, due to a bug
    if os.name == 'nt':
        print "\n----------------------------------------------------------"
        print 'Re-Installing pip and setuptools to fix virtualenv error under windows'
        print "----------------------------------------------------------\n"
        install_setup("get-pip.py", "https://bootstrap.pypa.io/get-pip.py")
        install_easy('pywin32-219.win-amd64-py2.7.exe', "https://biodev.ece.ucsb.edu/~bisque/wheels/pywin32-219.win-amd64-py2.7.exe")
    else:
        #install_sys_pip('pip==8.0.3')
        install_sys_pip('pip')
        install_sys_pip('setuptools')

    print "\n----------------------------------------------------------"
    print 'Installing additional packages'
    print "----------------------------------------------------------\n"
    for pkg,URL in PIP_LIST:
        install_pip(pkg, URL)

    print "\n----------------------------------------------------------"
    print 'Ensure Mercurial installation'
    print "----------------------------------------------------------\n"
    try:
       r = subprocess.call(['hg', '--version'], shell=shell)
    except Exception:
       r = 1
    if r != 0:
        if os.name == 'nt':
            #install_pip('mercurial-3.7.1-cp27-none-win_amd64.whl', "https://biodev.ece.ucsb.edu/~bisque/wheels/mercurial-3.7.1-cp27-none-win_amd64.whl")
            install_pip('mercurial')
        else:
            install_pip('mercurial')

    # check if we need to fetch the source-code
    fn = 'requirements.txt'
    if os.path.exists(fn) is not True:
        print "********************************"
        print "**     Fetching BisQue        **"
        print "********************************"
        print "Cloning: ", args.repo
        print
        subprocess.call(['hg', 'clone', args.repo, 'tmp'], shell=shell)
        for df in glob.glob('tmp/*') + glob.glob('tmp/.hg*'):
            if not os.path.exists(os.path.basename(df)):
                shutil.move (df, os.path.basename(df))


    print "********************************"
    print "**  Installing requirements   **"
    print "********************************"
    print
    print
    #subprocess.call(['pip', 'install', '--trusted-host', 'biodev.ece.ucsb.edu', '-i', 'http://biodev.ece.ucsb.edu/py/bisque/dev/+simple', 'Paste==1.7.5.1+bisque2'], shell=shell)
    #subprocess.call(['pip', 'install', '--trusted-host', 'biodev.ece.ucsb.edu', '-r', 'requirements.txt'], shell=shell)
    #subprocess.call(['pip', 'install', '-r', 'requirements.txt', '--trusted-host=biodev.ece.ucsb.edu'], shell=shell)
    subprocess.call(['pip', 'install', '-r', 'requirements.txt', '-i', PIP_INDEX], shell=shell)

    print "**************************************************************"
    print "To finish installation, please, execute the following commands"
    print "Use 'server' for a full BisQue server"
    print "Use 'engine' to run a module serving a remote BisQue"
    print "Please visit:"
    print "  http://biodev.ece.ucsb.edu/projects/bisquik/wiki/InstallationInstructions"
    print "for more information"
    print "*************************************************************\n"
    if os.name == 'nt':
        print "bqenv\\Scripts\\activate.bat"
    else:
        print "source bqenv/bin/activate"

    print "paver setup    [server|engine]"
    print "bq-admin setup [server|engine]"
    print "bq-admin deploy public"


    # dima: we should run all the above mentioned commands right here
    #args.install




if __name__=="__main__":
    run_bootstrap()
