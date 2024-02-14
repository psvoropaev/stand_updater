import logging.config

from dependency_injector import containers, providers
from gitlab import Gitlab
from kubernetes.client import CoreV1Api
from kubernetes.config import new_client_from_config
from kubernetes.watch import Watch


class ClientsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    k8s_core_api_provider = providers.Singleton(
        CoreV1Api,
        api_client=providers.Singleton(
            new_client_from_config,
            config_file=config.k8s_config_filename,
        ),
    )

    gitlab_api_provider = providers.Singleton(
        Gitlab,
        url=config.gitlab_url,
        private_token=config.gitlab_private_token,
    )

    watcher_provider = providers.Singleton(Watch)

    logger = providers.Singleton(logging.getLogger, "rich")

    # resources
    __init_logging_resource = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )
    __gitlab_auth_resource = providers.Resource(gitlab_api_provider.provided.auth.call())

    test_debug = providers.Resource(lambda: print("INIT RESOURCES "))
