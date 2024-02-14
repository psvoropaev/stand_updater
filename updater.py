from threading import Thread

import click
from dependency_injector.wiring import Provide, Provider, inject, register_loader_containers

from classes import NameSpace, ProjectConfig
from helpers.console.live import render_live
from helpers.di import (
    NAMESPACE_CONFIGS_TYPE,
    PM_FACTORY_TYPE,
    AppContainer,
)


@inject
def select_namespace(
        ctx,
        param,
        value,
        namespaces: NAMESPACE_CONFIGS_TYPE = Provide[AppContainer.namespaces],
) -> NameSpace:
    return namespaces[value]


@inject
def deploy_namespace_projects(
        namespace: NameSpace,
        project_manager_factory: PM_FACTORY_TYPE = Provider[
            AppContainer.services_container.project_manager_factory_provider],
        projects_config: ProjectConfig = Provide[AppContainer.projects_config],
):
    project_managers = [project_manager_factory(config=config) for config in projects_config]

    threads = [Thread(target=p.run, args=(namespace,)) for p in project_managers]
    [t.start() for t in threads]

    render_live()


@click.command()
@click.option("--namespace", "-n", callback=select_namespace, required=True)
def main(namespace: NameSpace):
    deploy_namespace_projects(namespace)


if __name__ == "__main__":
    app = AppContainer()
    app.config.gitlab_url.from_env("GITLAB_URL")
    app.config.gitlab_private_token.from_env("GITLAB_PRIVATE_TOKEN")
    app.init_resources()
    app.check_dependencies()
    register_loader_containers(app)
    app.wire(modules=[
        __name__,
        "helpers.aspects.decorators",
        "helpers.console.live",

    ])

    app.aspects_container().aspects_apply_provider()

    main()
