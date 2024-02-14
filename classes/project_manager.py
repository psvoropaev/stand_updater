import logging
from typing import List, Optional, Tuple

from classes.job import GitlabJobRunner
from classes.migration import MigrationManager
from classes.pod import PodWatcher
from classes.schema import NameSpace, ProjectConfig


class DeployProjectManager:
    def __init__(
        self,
        project_config: ProjectConfig,
        gitlab_job_runner: GitlabJobRunner,
        pod_watcher: PodWatcher,
        migration_manager: Optional[MigrationManager],
    ):
        self.project_config = project_config
        self.gitlab_job_runner = gitlab_job_runner
        self.pod_watcher = pod_watcher
        self.migration_manager = migration_manager

    def __repr__(self):
        return f"<DeployProjectManager::'{self.project_config.name}' object at {hex(id(self))}>"

    def deploy(self, namespace: NameSpace):
        self.gitlab_job_runner.play_target_job(
            project_path=f"{self.project_config.group}/{self.project_config.name}",
            target_id=self.project_config.target.id,
            namespace=namespace,
            keywords=self.project_config.keywords,
        )

    def wait_pod(self, namespace: NameSpace) -> Optional[Tuple[str, str]]:
        return self.pod_watcher.wait_deploy_pod(
            project_name=self.project_config.name,
            namespace=namespace,
            label_selector=self.project_config.pod.k8s_label_selector,
        )

    def migrate(
        self, pod_name: str, container_name: str, namespace: NameSpace
    ) -> Optional[str]:
        return self.migration_manager.migrate(
            pod_name=pod_name,
            container_name=container_name,
            namespace=namespace,
        )

    def run(self, namespace: NameSpace):

        self.deploy(namespace)
        pod_name, container_name = self.wait_pod(namespace)

        if self.migration_manager and pod_name and container_name:
            self.migrate(pod_name, container_name, namespace)
