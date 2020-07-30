import os
from tg import config


def bisque_root():
    root = os.getenv('BISQUE_ROOT')
    root =   (root or config.get('bisque.paths.root') or '').replace('\\', '/')
    return root

def bisque_path(*names):
    'return a path constructed from the installation path'
    root = bisque_root()
    return os.path.join(root, *names).replace('\\', '/')

def data_path(*names):
    'return a path constructed from the data directory path'
    data = config.get('bisque.paths.data')
    data = data or os.path.join(bisque_root(), 'data')
    return os.path.join(data, *names).replace('\\', '/')

def run_path(*names):
    'return a path constructed from the data directory path'
    data = config.get('bisque.paths.run')
    data = data or os.path.join(bisque_root(), 'run')
    return os.path.join(data, *names).replace('\\', '/')

def config_path(*names):
    'return a path constructed from the config directory path'
    conf = config.get('bisque.paths.config')
    conf = conf or os.path.join(bisque_root(), 'config')
    return os.path.join(conf, *names).replace('\\', '/')

def defaults_path(*names):
    'return a path constructed from the config directory path'
    conf = config.get('bisque.paths.default')
    conf = conf or os.path.join(bisque_root(), 'config-defaults')
    return os.path.join(conf, *names).replace('\\', '/')

def find_config_path(config_file, config_dir='config'):
    """find a config from the usual places: locally, config, or /etc or by search up from current
    position

    Function will check config using the config_file name i.e.:
         site.cfg -> bisque.paths.site_cfg
         runtime-bisque.cfg -> bisque.paths.runtime_bisque_cfg

    @param config_file: The correct name of the file i.e. site.cfg or runtime-bisque_cfg
    @return: The path of the file or None if not found
    """
    cfg = config.get( ('bisque.paths.%s' % config_file).replace('-', '_').replace ('.', '_'))
    if cfg is not None:
        return cfg.replace('\\', '/')
    paths = ['.', 'config', '/etc/bisque']
    if config.get ('bisque.paths.config'):
        paths.insert (0, config.get ('bisque.paths.config'))
    for d in paths:
        site_cfg = os.path.join(d, config_file)
        if os.path.exists(site_cfg):
            return site_cfg.replace('\\', '/')
    # search hieararchy
    current = os.getcwd().split ("/")
    while current:
        current.pop ()
        config_path = os.path.join ("/".join (current), config_dir,  config_file)
        if os.path.exists (config_path):
            return config_path
    return None

def site_cfg_path():
    'find a site.cfg from the usual places: locally, config, or /etc'
    return find_config_path ('site.cfg')
