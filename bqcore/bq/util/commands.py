import os

config_dirs = ('.', './config', '/etc/bisque')

def asbool(v):
  return str(v).lower() in ("yes", "true", "t", "1")

def find_site_cfg(cfg_file):
    paths = list(config_dirs)
    # Also check if we are in standard virtualenv layout
    if os.environ.get('VIRTUAL_ENV', '').endswith('bqenv'):
        paths.append (os.path.join (os.path.dirname (os.environ.get ('VIRTUAL_ENV')), 'config'))
    for dp in paths:
        site_cfg = os.path.join(dp, cfg_file)
        if os.path.exists(site_cfg):
            return site_cfg
    return None
