# noinspection PyBroadException
try:
    """works in pyscript environment only"""
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    task.current_task()
except:
    from pyscript_generated import *
    from pyscript_builtins import *
