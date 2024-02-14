from typing import List, Optional

from pydantic import BaseModel
from classes.constant import MigrationType, TargetType


class TargetConfig(BaseModel):
    type: TargetType
    id: str


class PodSchema(BaseModel):
    migration: Optional[MigrationType] = None
    k8s_label_selector: str


class ProjectConfig(BaseModel):
    name: str
    group: str
    target: TargetConfig
    pod: Optional[PodSchema] = None
    keywords: Optional[List[str]] = None


class NameSpace(BaseModel):
    k8s_name: str
    gitlab_name: str
