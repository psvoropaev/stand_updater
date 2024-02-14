from dependency_injector import containers, providers

from classes import (
    TargetType,
    CommitRunner,
    BranchRunner,
    TagRunner,
    MigrationType,
    AlembicMigrationManager,
    DjangoMigrationManager,
    PodWatcher,
    ProjectConfig,
    DeployProjectManager,
)


def project_manager_factory(
    config: ProjectConfig, services: "ServicesContainer"
) -> DeployProjectManager:
    factory = providers.Factory(
        DeployProjectManager,
        project_config=config,
        pod_watcher=services.pod_watcher_provider,
        gitlab_job_runner=providers.Factory(services.job_manager_provider, config.target.type),
        migration_manager=providers.Factory(services.migration_manager_provider, config.pod.migration),
    )
    return factory()


class ServicesContainer(containers.DeclarativeContainer):
    __self__ = providers.Self()
    config = providers.Configuration()
    clients = providers.DependenciesContainer()

    job_manager_provider = providers.FactoryAggregate({
        TargetType.commit: providers.Singleton(CommitRunner, gitlab_client=clients.gitlab_api_provider),
        TargetType.branch: providers.Singleton(BranchRunner, gitlab_client=clients.gitlab_api_provider),
        TargetType.tag: providers.Singleton(TagRunner, gitlab_client=clients.gitlab_api_provider),
        None: providers.Object(None),
    })

    migration_manager_provider = providers.FactoryAggregate({
        MigrationType.alembic: providers.Singleton(AlembicMigrationManager, k8s_core_api=clients.k8s_core_api_provider),
        MigrationType.django: providers.Singleton(DjangoMigrationManager, k8s_core_api=clients.k8s_core_api_provider),
        None: providers.Object(None),
    })

    pod_watcher_provider = providers.Singleton(
        PodWatcher,
        k8s_core_api=clients.k8s_core_api_provider,
        k8s_skip_keywords=config.k8s_skip_keywords,
        timeout_seconds=config.k8s_watch_timeout_seconds,
    )
    pod_watcher_provider.add_attributes(watcher=clients.watcher_provider)

    project_manager_factory_provider = providers.Factory(project_manager_factory, services=__self__)


PM_FACTORY_TYPE = providers.Factory[DeployProjectManager]
