from unittest.mock import _get_target
from typing import List, Dict, Any, Callable, Optional
from pydantic import BaseModel, TypeAdapter


def get_target(path: str):
    target, attribute = _get_target(path)
    return target(), attribute


class Aspect(BaseModel):
    callable_path: str
    is_factory: Optional[bool] = False
    args: Optional[List[Any]] = []
    kwargs: Optional[Dict[str, Any]] = {}

    @property
    def callable_obj(self):
        target, attribute = get_target(self.callable_path)
        callable_target = getattr(target, attribute)
        if self.is_factory:
            return callable_target(*self.args, **self.kwargs)
        return callable_target


class AspectsConfig(BaseModel):
    config: Optional[Dict[str, Aspect]] = {}
    reference: Dict[str, List[str]]


ASPECTS_CONFIG_TYPE = TypeAdapter(AspectsConfig)


def apply_aspects(aspects_config: AspectsConfig):
    for target_callable_path, aspects in aspects_config.reference.items():
        target, attribute = get_target(target_callable_path)

        for aspect_name in aspects:
            aspect_config = aspects_config.config[aspect_name]
            setattr(
                target,
                attribute,
                aspect_config.callable_obj(getattr(target, attribute)),
            )
