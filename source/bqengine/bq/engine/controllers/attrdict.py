######################################
# dict allowing field access to elements
class AttrDict(dict):
    "dictionary allowing access to elements as field"

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError
    def __setattr__(self, name, value):
        self[name] = value
        return value

    def __getstate__(self):
        return self.items()

    def __setstate__(self, items):
        for key, val in items:
            self[key] = val
