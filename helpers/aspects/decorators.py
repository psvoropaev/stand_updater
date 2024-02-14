from dependency_injector.wiring import Provide, inject
from typing import Callable, Dict, List
import logging

from helpers.di import AppContainer
from functools import wraps
from helpers.console.render import ProjectStatusManager, RenderStatus
from classes import ProjectConfig


@inject
def io_callable_logger(
    logger: logging.Logger = Provide[AppContainer.clients_container.logger],
    log_level: str = "INFO"
) -> Callable:
    log_level: int = logging._nameToLevel[log_level]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(log_level, f"Called : {func.__name__}({args=}, {kwargs=})")
            result = func(*args, **kwargs)
            logger.log(log_level, f"Result of {func.__name__}: {result}")
            return result
        return wrapper

    return decorator


COLUMN_CUSTOM_STATUS_MAP = {
    'migrate': lambda project_config: RenderStatus.PENDING if project_config.pod.migration else RenderStatus.SKIPPED,
}


@inject
def collect_project_method_status(
    func: Callable,
    projects_config: List[ProjectConfig] = Provide[AppContainer.projects_config],
    statuses_store: Dict = Provide[AppContainer.render_container.statuses_store],
    project_status_manager: ProjectStatusManager = Provide[AppContainer.render_container.project_status_manager_provider],
) -> Callable:
    for proj in sorted(projects_config, key=lambda x: x.name):
        custom_status = COLUMN_CUSTOM_STATUS_MAP.get(func.__name__)
        statuses_store[proj.name][func] = custom_status(proj) if custom_status else RenderStatus.PENDING

    return project_status_manager(func)
