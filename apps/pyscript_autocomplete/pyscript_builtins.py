from asyncio import Task
from typing import Any, Callable, List, Literal, Optional

from homeassistant.core import HomeAssistant, Context

hass = HomeAssistant("")

"""pyscript decorators"""


def service(*service_name, supports_response: Literal["none", "only", "optional"] = "none") -> Callable:
    ...


def state_trigger(
    *str_expr: str, state_hold=None, state_hold_false=None, state_check_now=False, kwargs=None, watch=None
) -> Callable:
    ...


def time_trigger(*args, **kwargs) -> Callable:
    ...


def event_trigger(event_type: str, str_expr=None, kwargs=None) -> Callable:
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
        ...

    @staticmethod
    def cancel(task_id: Optional[Task] = None):
        ...

    @staticmethod
    def current_task() -> Task:
        ...

    @staticmethod
    def name2id(name=None) -> Task:
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
