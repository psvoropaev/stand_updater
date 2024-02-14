from enum import Enum
from functools import wraps

from rich.spinner import Spinner
from rich.text import Text
from typing import Dict


class RenderStatus(Enum):
    PENDING = Text("Pending", style="gray")
    RUNNING = Spinner(
        "dots",
        text="[magenta]In process",
    )
    COMPLETED = Text("Done", style="green bold")
    ERROR = Text("Error", style="red")
    SKIPPED = Text("Skip", style="dim")

    def __str__(self):
        return self.value


class ProjectStatusManager:
    def __init__(
        self,
        statuses_store: Dict
    ):
        self.statuses_store = statuses_store

    def process_error(self, project_name, func):
        self.statuses_store[project_name][func] = RenderStatus.ERROR
        for handler, status in self.statuses_store[project_name].items():
            if status == RenderStatus.PENDING:
                self.statuses_store[project_name][handler] = RenderStatus.SKIPPED

    def set_step_status(self, project_name, func, status: RenderStatus):
        self.statuses_store[project_name][func] = status

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            project_name = args[0].project_config.name

            self.set_step_status(project_name, func, RenderStatus.RUNNING)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                self.process_error(project_name, func)
                raise e
            else:
                self.set_step_status(project_name, func, RenderStatus.COMPLETED)

            return result

        return wrapper
