import os
import yaml
import random

path = os.path.dirname(__file__)

class Parser(object):
    def __init__(self, cfg, args=None, update=True):
        fname = os.path.join(path, '../experiments', 'settings.yaml')
        self.from_file(fname)

        fname = os.path.join(path, '../experiments', cfg + '.yaml')
        self.from_file(fname, args)

        if not hasattr(self, 'seed') or not self.seed:
            self.seed = random.randint(1, 2**32-1)

        if update:
            with open(fname, 'w') as f:
                yaml.dump(vars(self), f, default_flow_style=False)


    def __str__(self):
        attrs = sorted(vars(self))
        attrs = map(
                lambda x:'%s: %s\n' % (x.ljust(20), str(getattr(self, x))),
                attrs)
        return ''.join(attrs)

    def from_file(self, fname, args=None):
        with open(fname) as f:
            S = yaml.load(f)

        if args: S.update(**vars(args))

        for key, value in S.items():
            setattr(self, key, value)

    def getdir(self):
        # name + net + config + loss + fold
        # config should have name + net??
        #name = (self.cfg, 'fold' + str(self.fold))
        #name = (self.name, self.net, self.opt,
        #        str(self.schedule).replace(' ', ''),
        #        self.criterion,
        #        'fold' + str(self.fold))
        #name = '_'.join(name)
        checkpoint_dir = os.path.join(self.train_dir, self.cfg)
        return checkpoint_dir

    def makedir(self):
        checkpoint_dir = self.getdir()
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

        fname = os.path.join(checkpoint_dir, 'cfg.txt')
        with open(fname, 'w') as f:
            f.write(str(self))

        return checkpoint_dir
