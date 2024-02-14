import os
import sys
from dependency_injector import containers, providers
from typing import Dict, List
from pydantic import TypeAdapter
from helpers.di.aspects import AspectContainer
from helpers.di.clients import ClientsContainer
from helpers.di.render import RenderContainer
from helpers.di.services import ServicesContainer
from classes import NameSpace, ProjectConfig

config_dir_path = sys.argv[0].rsplit('/', 1)[0]

NAMESPACE_CONFIGS_TYPE = TypeAdapter(Dict[str, NameSpace])
PROJECTS_PYDANTIC_TYPE = TypeAdapter(List[ProjectConfig])


class AppContainer(containers.DeclarativeContainer):

    config = providers.Configuration(
        strict=True,
        yaml_files=[
            os.path.join(config_dir_path, "configs/app.yml"),
            os.path.join(config_dir_path, "configs/aspects.yml"),
            os.path.join(config_dir_path, "configs/namespaces.yml"),
            os.path.join(config_dir_path, "configs/logging.yml"),
            os.path.join(config_dir_path, "configs/projects.yml"),
        ],
    )
    projects_config = providers.Resource(PROJECTS_PYDANTIC_TYPE.validate_python, config.projects)
    namespaces = providers.Resource(NAMESPACE_CONFIGS_TYPE.validate_python, config.namespaces)

    clients_container = providers.Container(ClientsContainer, config=config)
    services_container = providers.Container(ServicesContainer, config=config, clients=clients_container)
    aspects_container = providers.Container(AspectContainer, config=config.aspects)
    render_container = providers.Container(RenderContainer)
