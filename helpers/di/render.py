from collections import defaultdict

from dependency_injector import containers, providers
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.table import Table, Column

from helpers.console.render import ProjectStatusManager


class RenderContainer(containers.DeclarativeContainer):
    statuses_store = providers.Resource(providers.Object(defaultdict(dict)))

    overall_progress = providers.Resource(
        Progress,
        "{task.description}",
        BarColumn(bar_width=1000),  # dirty hack for stretching column to 100% width
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        MofNCompleteColumn(),
        expand=True,
    )
    overall_task_id = providers.Resource(
        overall_progress.provided.add_task.call(),
        description="All tasks",
        completed=0,
        total=1,
    )

    projects_stat_table = providers.Resource(
        Table,
        Column("Project", style="cyan", no_wrap=True),
        Column("Deploy", justify="center", width=15),
        Column("Wait pod", justify="center", width=15),
        Column("Migrate", justify="center", width=15),
        expand=True,
    )

    project_status_manager_provider = providers.Singleton(ProjectStatusManager, statuses_store)
