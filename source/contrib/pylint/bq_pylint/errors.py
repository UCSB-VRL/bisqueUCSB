from astroid import MANAGER
from astroid import scoped_nodes


CLASS_NO_MEMBERS = {
    'scoped_session' :  ('add', 'delete', 'flush', 'merge', 'begin_nested', 'rollback'),
}

EXPR_NO_MEMBERS = {
    'merge' : ('id', 'uri', 'value'),
}

def register(linter):
    pass



def transform(cls):
    missing_members = CLASS_NO_MEMBERS.get (cls.name, [])
    for f in missing_members:
        cls.locals[f] = [scoped_nodes.Class(f, None)]

MANAGER.register_transform(scoped_nodes.Class, transform)
#MANAGER.register_transform(scoped_nodes.Class, transform)
