

USENODE = False
if USENODE:
    from .bqnode import  *
else:
    from .bqclass import *
