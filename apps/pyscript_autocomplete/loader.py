import os

if os.getenv("PYSCRIPT_DEV"):
    from .pyscript_builtins import *
