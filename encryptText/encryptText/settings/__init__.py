import os

if os.path.exists(os.path.join(os.path.dirname(__file__), 'local.py')):
    from .local import *
else:
    from .demo import *