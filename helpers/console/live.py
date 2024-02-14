from time import sleep
from typing import Dict

from dependency_injector.wiring import inject, Provide
from rich.console import Group
from rich.live import Live
from rich.progress import Progress
from rich.table import Table
from collections import Counter
from helpers.di import AppContainer
from helpers.console.render import RenderStatus


@inject
def prepare_render_table(
    table: Table = Provide[AppContainer.render_container.projects_stat_table],
    statuses_store: Dict = Provide[AppContainer.render_container.statuses_store],
) -> Table:
    table.rows.clear()
    # dirty fix bug of library Rich
    [column._cells.clear() for column in table.columns[1:]]

    for project_name, statuses in statuses_store.items():
        table.add_row(project_name, *[statuses[s].value for s in statuses])

    return table


@inject
def prepare_overall_progress(
    overall_progress: Progress = Provide[AppContainer.render_container.overall_progress],
    statuses_store: Dict = Provide[AppContainer.render_container.statuses_store],
) -> Progress:
    task = overall_progress.tasks[0]
    task.total = len(statuses_store) * 3
    counter = Counter(sum(map(lambda x: list(x.values()), statuses_store.values()), []))
    task.completed = task.total - (counter.get(RenderStatus.PENDING, 0) + counter.get(RenderStatus.RUNNING, 0))
    return overall_progress


def render_live():
    with Live() as live:
        while True:
            overall_progress = prepare_overall_progress()
            live.update(Group(prepare_render_table(), overall_progress), refresh=True)
            if overall_progress.finished:
                break
            sleep(0.2)

# def get_log(logger=Provide[AppContainer.clients_provider.logger]):
#     buffering_handler = logger.handlers[0]
#     log_messages = [buffering_handler.format(x) for x in buffering_handler.buffer[-20:]]
#     return Panel("\n".join(log_messages))
