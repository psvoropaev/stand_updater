import datetime
import re
from typing import List, Optional, Tuple

from kubernetes import watch
from kubernetes.client import CoreV1Api

from classes.schema import NameSpace


class PodWatcher:
    watcher: watch.Watch

    def __init__(
        self,
        k8s_core_api: CoreV1Api,
        k8s_skip_keywords: List[str],
        timeout_seconds: int = 300,
    ):
        self.k8s_core_api = k8s_core_api
        self.k8s_skip_keywords = k8s_skip_keywords
        self.timeout_seconds = timeout_seconds
        self.start_wait_at = datetime.datetime.now(datetime.timezone.utc)

    def _prepare_event_pod_regexp_pattern(self, project_name: str) -> re.Pattern:
        return re.compile(f"(?!.*({'|'.join(self.k8s_skip_keywords)}).*){project_name}")

    def wait_deploy_pod(
        self,
        project_name: str,
        namespace: NameSpace,
        label_selector: str,
    ) -> Tuple[Optional[str], Optional[str]]:

        regexp_pattern = self._prepare_event_pod_regexp_pattern(project_name)

        for pod_data in self.watcher.stream(
            self.k8s_core_api.list_namespaced_pod,
            namespace=namespace.k8s_name,
            label_selector=label_selector,
            field_selector="status.phase=Running",
            timeout_seconds=self.timeout_seconds,
        ):
            pod = pod_data["object"]
            if (
                self.start_wait_at < pod.metadata.creation_timestamp
                and regexp_pattern.match(pod.metadata.name)
            ):
                for container in pod.spec.containers:
                    if regexp_pattern.match(container.name):
                        return pod.metadata.name, container.name

        raise
