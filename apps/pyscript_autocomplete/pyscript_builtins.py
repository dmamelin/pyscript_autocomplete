from asyncio import Task
from typing import Any, Callable, List, Literal, Optional, Set, Union

from homeassistant.core import HomeAssistant, Context

hass = HomeAssistant("")

"""pyscript decorators"""


def service(*service_name: str, supports_response: Literal["none", "only", "optional"] = "none") -> Callable:
    ...


def state_trigger(
    *str_expr: str,
    state_hold: Optional[int] = None,
    state_hold_false: Optional[int] = None,
    state_check_now: Optional[bool] = None,
    kwargs: Optional[dict] = None,
    watch: Optional[Union[List[str], Set[str]]] = None
) -> Callable:
    ...


def state_active(str_expr: str) -> Callable:
    ...


def time_trigger(*args, **kwargs) -> Callable:
    ...


def task_unique(name: str, kill_me=False) -> Callable:
    ...


def event_trigger(event_type: str, str_expr=None, kwargs: Optional[dict] = None) -> Callable:
    ...


def time_active(*time_spec: str, hold_off: Optional[int] = None) -> Callable:
    ...


def mqtt_trigger(topic: str, str_expr: Optional[str] = None, kwargs: Optional[dict] = None) -> Callable:
    ...


def pyscript_compile() -> Callable:
    ...


def pyscript_executor() -> Callable:
    ...


# """pyscript buildins"""


class log:
    @staticmethod
    def debug(str):
        ...

    @staticmethod
    def info(str):
        ...

    @staticmethod
    def warning(str):
        ...

    @staticmethod
    def error(str):
        ...


class state:
    @staticmethod
    def delete(name: str):
        ...

    @staticmethod
    def get(name) -> Any:
        ...

    @staticmethod
    def getattr(name) -> dict[str, Any]:
        ...

    @staticmethod
    def names(domain) -> list[str]:
        ...

    @staticmethod
    def persist(entity_id, default_value=None, default_attributes=None):
        ...

    @staticmethod
    def set(name: str, value=None, new_attributes=None, **kwargs):
        ...

    @staticmethod
    def setattr(name, value):
        ...


class event:
    @staticmethod
    def fire(event_type, **kwargs):
        ...


class task:
    @staticmethod
    def create(func: Callable, *args, **kwargs) -> Task:
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-management
        """
        ...

    @staticmethod
    def cancel(task_id: Optional[Task] = None):
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-management
        """
        ...

    @staticmethod
    def current_task() -> Task:
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-management
        """
        ...

    @staticmethod
    def name2id(name=None) -> Task:
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-management
        """
        ...

    @staticmethod
    def wait(task_set: Optional[Set[Task]], **kwargs):
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-management
        """
        ...

    @staticmethod
    def add_done_callback(task_id: Task, func: Callable, *args, **kwargs):
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-management
        """
        ...

    @staticmethod
    def remove_done_callback(task_id: Task, func: Callable):
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-management
        """
        ...

    @staticmethod
    def executor(func: Callable, *args, **kwargs):
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-executor
        """
        ...

    @staticmethod
    def sleep(seconds: int):
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-sleep
        """
        ...

    @staticmethod
    def unique(task_name: str, kill_me: bool = False):
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-unique-function
        """

    @staticmethod
    def wait_until(**kwargs):
        """
        https://hacs-pyscript.readthedocs.io/en/stable/reference.html#task-waiting
        """
        ...


class pyscript(Any):
    app_config: dict[str, Any]

    @staticmethod
    def get_global_ctx() -> str:
        ...

    @staticmethod
    def set_global_ctx(new_ctx_name: str):
        ...

    @staticmethod
    def list_global_ctx() -> List[str]:
        ...

    @staticmethod
    def reload():
        ...
