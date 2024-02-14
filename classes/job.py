import re
from abc import ABC
from typing import List, Optional

from gitlab.client import Gitlab
from gitlab.v4.objects.jobs import ProjectJob
from gitlab.v4.objects.projects import Project

from classes.schema import NameSpace


class GitlabJobRunner(ABC):
    MAX_ITERATION = 500

    def __init__(self, gitlab_client: Gitlab):
        self.gitlab_client = gitlab_client

    @staticmethod
    def get_target_commit_id(project: Project, target_id: str) -> Optional[str]: ...

    def get_gitlab_project(self, project_path: str) -> Project:
        return self.gitlab_client.projects.get(f"{project_path}")

    def get_target_job(
        self,
        project: Project,
        commit_id: str,
        namespace: NameSpace,
        keywords: Optional[List[str]] = None,
    ) -> Optional[ProjectJob]:
        iter_pos = 0

        for job in project.jobs.list(iterator=True):
            iter_pos += 1
            if iter_pos > self.MAX_ITERATION:
                raise StopIteration

            condition = [
                job.commit["id"] == commit_id,
                namespace.gitlab_name in job.name,
            ]
            if keywords:
                condition.append(set(re.split("[:-]", job.stage)) & set(keywords))
            if all(condition):
                return job

    def play_target_job(
        self,
        project_path: str,
        target_id: str,
        namespace: NameSpace,
        keywords: Optional[List[str]] = None,
    ):
        project = self.get_gitlab_project(project_path)
        commit_id = self.get_target_commit_id(project, target_id)
        job = self.get_target_job(project, commit_id, namespace, keywords)

        job.play()


class CommitRunner(GitlabJobRunner):
    @staticmethod
    def get_target_commit_id(project: Project, target_id: str) -> Optional[str]:
        return project.commits.get(target_id).get_id()


class BranchRunner(GitlabJobRunner):
    @staticmethod
    def get_target_commit_id(project: Project, target_id: str) -> Optional[str]:
        branch = project.branches.get(target_id)
        if not branch:
            raise
        return branch.commit["id"]


class TagRunner(GitlabJobRunner):
    @staticmethod
    def get_target_commit_id(project: Project, target_id: str) -> Optional[str]:
        tag = project.tags.get(target_id)
        if not tag:
            raise
        return tag.commit["id"]
