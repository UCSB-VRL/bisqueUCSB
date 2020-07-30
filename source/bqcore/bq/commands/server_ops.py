#!/usr/bin/python
import os, sys, time
from subprocess import Popen, call, PIPE, STDOUT
from urlparse import urlparse
from ConfigParser import SafeConfigParser
import shlex
import psutil

#from bq.util.commands import find_site_cfg
from bq.util.paths import find_config_path, site_cfg_path
from bq.util.dotnested import parse_nested

#from bq.commands.server_ops import root

PID_TEMPL = "bisque_%s.pid"
LOG_TEMPL = 'bisque_%s.log'
RUNNER_CMD = ['mexrunner']
SITE_CFG = 'site.cfg'
ING={ 'start': 'starting', 'stop':'stopping', 'restart':'restarting'}

# if os.name == 'nt':
#     #pylint:disable=F0401
#     import win32api, win32con
#     def kill_process(pid):
#         try:
#             handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pid)
#             win32api.TerminateProcess(handle, 0)
#             win32api.CloseHandle(handle)
#             return True
#         except Exception:
#             print 'Error terminating %s, the process might be dead' % pid
#         return False
#         #import subprocess
#         #subprocess.call(['taskkill', '/PID', str(pid), '/F'])

# else:
#     import signal
#     from bq.util.wait_pid import wait_pid
#     def kill_process(pid):
#         try:
#             pid = os.getpgid(pid)
#             os.killpg (pid, signal.SIGTERM)
#             wait_pid(pid)
#             return True
#         except OSError, e:
#             print "kill process %s failed with %s" % (pid, e)
#         return False

def kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait()
    except psutil.NoSuchProcess:
        pass

#####################################################################
# utils
# since we run in a virtualenv this *should* ok..
def exe_path(cmd):
    return os.path.join (os.path.dirname (sys.executable), cmd)

def readhostconfig (site_cfg):
    #vars = { 'here' : os.getcwd() }
    config = SafeConfigParser ()
    config.read (site_cfg)
    #root = config.get ('app:main', 'bisque.root')
    run_dir = config.get ('app:main', 'bisque.paths.run')
    service_items = config.items ('servers')
    hosts = [ x.strip() for x in config.get  ('servers', 'servers').split(',') ]

    #print "SECTION", config.has_section('servers')

    # Service spec if server.key.url = url
    # Create a dictionary for each host listed
    # h1.key.key1 = aa
    # h1.key.key2 = bb
    # => { 'h1' : { 'key' : { 'key1' : 'val', 'key2' : 'bb' }}}
    # servers = {}
    # for host_spec, val in service_items:
    #     path = host_spec.split('.')
    #     if not path[0] in hosts:
    #         continue
    #     param = path[-1]
    #     d = servers
    #     for path_el in path[:-1]:
    #         d = d.setdefault(path_el, {})
    #     d[param] = val

    servers = parse_nested (service_items, hosts)

    bisque = { 'run_dir': run_dir,  'servers': servers, 'log_dir': '.', 'pid_dir' : '.' }
    if config.has_option('servers', 'log_dir'):
        bisque['log_dir'] = os.path.join (run_dir, config.get ('servers', 'log_dir'))
    if config.has_option('servers', 'pid_dir'):
        bisque['pid_dir'] = os.path.join (run_dir, config.get ('servers', 'pid_dir'))
    if config.has_option('servers','backend'):
        bisque['backend'] = config.get ('servers', 'backend')
    if config.has_option('servers','mex_dispatcher'):
        bisque['mex_dispatcher'] = config.get ('servers', 'mex_dispatcher')
    if config.has_option('servers','logging_server'):
        bisque['logging_server'] = config.get ('servers', 'logging_server')
    return bisque


def prepare_log (logfile):
    if os.path.exists(logfile):
        oldlog = logfile + '.save'
        if os.path.exists(oldlog):
            os.remove (oldlog)
        os.rename (logfile, oldlog)
        #print ('%s -> %s' % (logfile, oldlog))
    #else:
    #    print ("No logfile %s" % logfile)

# def tail(file):
#     interval = 1.0
#     while True:
#         where = file.tell()
#         line = file.readline()
#         if not line:
#             time.sleep(interval)
#             file.seek(where)
#         else:
#             print line, # already has newline

def tail(f, window=20):
    lines = [''] * window
    count = 0
    for l in f:
        lines[count % window] = l
        count += 1
    print lines[count % window:], lines[:count % window]

def check_running (pid_file):
    if os.path.exists(pid_file):
        print "Warning you appear to be restarting another BISQUIK process"
        print "Please stop that process before starting another"
        print "Try to stop previous running instance (Y/n)"
        a = raw_input()
        if a == '' or a[0].upper() == "Y":
            return True
        else:
            return False


def paster_command(command, options, cfgopt, processes, cfg_file = None, *args):
    def verbose(msg):
        if options.verbose:
            print msg

    paster_verbose = '-v' if options.verbose else '-q'
    verbose ("%s bisque on %s .. please wait" % (ING[command], cfgopt['port']))
    server_cmd = [exe_path('paster'), 'serve', paster_verbose]
    server_cmd.extend (['--log-file', cfgopt['logfile'], '--pid-file', cfgopt['pidfile'],
                        #                   '--deamon',
                        ])

    if command in ('start', 'restart'):
        prepare_log (cfgopt['logfile'])

    if options.reload:
        server_cmd.append ('--reload')
    server_cmd.extend ([
            #os.path.join(cfgopt['site_dir'], 'server.ini'),
            cfg_file or '',
            command,
            #'services_enabled=%s' % cfgopt['services_enabled'],
            #'services_disabled=%s' % cfgopt['services_disabled'],
            #'server=%s' % cfgopt['url'],
            #'http_port=%s' % cfgopt['port'],
            #'http_host=%s' % cfgopt['host'],
            #'rooturl=%s' % cfgopt['root'],
            #'sitecfg=%s' % cfgopt['site_cfg'],
            ])
    server_cmd.extend (args)
    verbose ('Executing: %s' % ' '.join(server_cmd))
    if not options.dryrun:
        if os.name != 'nt':
            processes.append(Popen(server_cmd))
        else:
            with open(os.devnull, 'wb') as DEVNULL:
                processes.append(Popen(server_cmd, stdout=DEVNULL, stderr=DEVNULL))
    return processes

def uwsgi_command(command, options, cfgopt, processes,  cfg_file = None, *args):
    def verbose(msg):
        if options.verbose:
            print msg

    if command is 'stop':
        pidfile = cfgopt['pidfile']
        uwsgi_cmd = [exe_path('uwsgi'), '--stop', pidfile]
        #processes.append(Popen(uwsgi_cmd,shell=True,stdout=sys.stdout))

        verbose('Executing: ' + ' '.join(uwsgi_cmd))
        if not options.dryrun:
            if  call(uwsgi_cmd) != 0:
                print "Stop failed .. process already dead?"
            if os.path.exists (pidfile):
                os.remove (pidfile)
    elif command is 'start':
        #uwsgi_opts = cfgopt['uwsgi']
        uwsgi_cmd = [exe_path('uwsgi'), '--ini-paste', cfg_file,
#                     '--env', 'LC_ALL=en_US.UTF-8',
#                     '--env', 'LANG=en_US.UTF-8',
                     '--daemonize', cfgopt['logfile'],
                     '--pidfile', cfgopt['pidfile']]
        uwsgi_cmd.extend (args)
        verbose('Executing: ' + ' '.join(uwsgi_cmd))
        if not options.dryrun:
            if call(uwsgi_cmd) != 0:
                print "Start failed"
    return processes


def logger_command(command, cfgopt, processes):
    pidfile = os.path.join(cfgopt['pid_dir'], 'bisque_logger.pid')

    launcher  = shlex.split (cfgopt['logging_server'])

    print "%s logging service" % ING[command]
    if command is 'start':
        with open(os.devnull, 'w') as fnull:
            #logger = Popen(cfgopt['logging_server'], stdout=fnull, stderr=fnull, shell=True)
            logger = Popen([exe_path (launcher[0])] + launcher[1:],  shell= (os.name == 'nt') )
        if logger.returncode is None and logger.pid:
            with open(pidfile, 'w') as pd:
                pd.write("%s\n" % logger.pid)
        else:
            print "log_service pid %s with code %s" % (logger.pid, logger.returncode)
        processes.append(logger)
    elif command is 'stop':
        if  os.path.exists (pidfile):
            with open(pidfile, 'r') as pd:
                pid = int (pd.read())
            kill_process (pid)
            os.remove (pidfile)
        else:
            print "No pid file for logging server"


BACKENDS = {
    'paster' : paster_command,
    'uwsgi'  : uwsgi_command
}

def operation(command, options, *args):
    """Run a multi-server command to start several bisque jobs
    """
    def verbose(msg):
        if options.verbose:
            print msg

    cfg_file=options.site or SITE_CFG
    site_cfg = find_config_path(cfg_file)
    if site_cfg is None:
        print "Cannot find %s.. please make sure you are in the bisque dir" % cfg_file
        return
    site_dir = os.path.dirname(os.path.abspath(site_cfg))

    verbose('using config : %s' % site_cfg)
    try:
        config = readhostconfig(site_cfg)
        verbose("SERVERS %s" % (config['servers'].keys()))
        processes = []
        cfgopt = {} # {'root': config['root']}
        cfgopt['site_dir'] = site_dir
        cfgopt['site_cfg'] = site_cfg
        cfgopt['virtualenv'] = os.getenv('VIRTUAL_ENV')
        for f in ('log_dir', 'pid_dir', 'logging_server'):
            if f in config:
                cfgopt[f] = config[f]

        if not os.path.exists (config['run_dir']):
            print "Please check your site.cfg.  bisque.paths.run is not set correctly"
            return
        os.chdir (config['run_dir'])
        # Get the backend
        backend = config.get('backend', None)
        verbose("using backend: " + str(backend))
        if backend == None:
            verbose("Backend not configured. defaulting to paster")
            backend = 'paster'
        backend_command = BACKENDS[backend]

        # Process non-server commands
        if command == 'list':
            print "ARGS: %s" % (args,)
            for server, params in  config['servers'].items():
                print "server %s  : %s " % (server, params)
            return

        if not args and 'logging_server' in cfgopt:
            if command in ('restart'):
                logger_command ('stop', cfgopt, processes)
            if command in ('start', 'restart'):
                logger_command ('start', cfgopt, processes)

        for key, serverspec in sorted(config['servers'].items()):

            if args and key not in args:
                continue

            print ING[command], key

            cfgopt['services_enabled'] = ','.join([
                l.strip() for l in serverspec.pop('services_enabled', '').split(',')])
            cfgopt['services_disabled'] = ','.join([
                l.strip() for l in serverspec.pop('services_disabled', '').split(',')])
            cfgopt['url'] = serverspec.pop('url')
            fullurl = urlparse (cfgopt['url'])
            cfgopt['host'] = fullurl[1].split(':')[0]
            cfgopt['port'] = str(fullurl.port)
            cfgopt['logfile'] = os.path.join(config['log_dir'], LOG_TEMPL % cfgopt['port'])
            cfgopt['pidfile'] = os.path.join(config['pid_dir'], PID_TEMPL % cfgopt['port'])
            cfgopt['uwsgi']  = serverspec.pop('uwsgi', None)

            cfg_file_name =  "%s_%s.cfg" % (key, backend)
            cfg_file  = find_config_path(cfg_file_name)
            if not cfg_file:
                print ("Cannot find config file %s" % cfg_file_name)
                print ("Please run bq-admin setup configuration")
                return

            if command in ('stop', 'restart'):
                error = None

                backend_command ('stop', options, cfgopt, processes, cfg_file)
                for proc in processes:
                    try:
                        proc.wait()
                    except KeyboardInterrupt:
                        error = True

                if error is not None and backend == 'paster':
                    #print 'Paste windows error while stopping process, re-running'
                    processes = paster_command('stop', options, cfgopt, processes, args)
                    for proc in processes:
                        proc.wait()
                    print 'Recovered Paste windows error and successfully stopped daemon'

                processes = []

            if command in ('start', 'restart'):
                if os.path.exists(cfgopt['pidfile']):
                    try:
                        pid= int (open (cfgopt['pidfile']).read())
                        if psutil.pid_exists (pid):
                            if options.force:
                                print 'old pid file: %s exists! restarting...' % cfgopt['pidfile']
                                operation("stop", options, cfg_file, *args)
                                time.sleep(5)
                            else:
                                print "Can't start because of existing PID file"
                                sys.exit(2)
                    except ValueError:
                        pass
                    if os.path.exists(cfgopt['pidfile']):
                        os.remove (cfgopt['pidfile'])
                processes = backend_command('start', options, cfgopt, processes, cfg_file)

        if not args and 'logging_server' in cfgopt:
            if command in ('stop'):
                logger_command ('stop', cfgopt, processes)

        if options.wait:
            for proc in processes:
                proc.wait()

    except KeyboardInterrupt:
        pass
