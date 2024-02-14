from dependency_injector import containers, providers

from helpers.aspects.loader import ASPECTS_CONFIG_TYPE, apply_aspects


class AspectContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    aspects_config = providers.Resource(ASPECTS_CONFIG_TYPE.validate_python, config)
    aspects_apply_provider = providers.Singleton(apply_aspects, aspects_config)
