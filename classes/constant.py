from enum import Enum


class TargetType(Enum):
    branch = "branch"
    commit = "commit"
    tag = "tag"


class MigrationType(Enum):
    alembic = "alembic"
    django = "django"
