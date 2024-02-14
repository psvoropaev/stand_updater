from kubernetes.client import CoreV1Api
from kubernetes.stream import stream

from classes.schema import NameSpace


class MigrationManager:
    COMMAND: str = ""

    def __init__(self, k8s_core_api: CoreV1Api):
        self.k8s_core_api = k8s_core_api

    def migrate(self, pod_name: str, container_name: str, namespace: NameSpace) -> str:
        return stream(
            self.k8s_core_api.connect_get_namespaced_pod_exec,
            name=pod_name,
            namespace=namespace.k8s_name,
            command=MigrationManager.COMMAND,
            container=container_name,
            stderr=True,
            # stdout=True,
            tty=False,
        )


class DjangoMigrationManager(MigrationManager):
    COMMAND = ["python", "manage.py", "migrate"]


class AlembicMigrationManager(MigrationManager):
    COMMAND = ["alembic", "upgrade", "heads"]
