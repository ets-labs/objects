"""Photos bundle."""

from dependency_injector import containers
from dependency_injector import providers

from . import entities
from . import repositories


class Photos(containers.DeclarativeContainer):
    """Photos bundle container."""

    database = providers.Dependency()
    file_storage = providers.Dependency()

    photo = providers.Factory(entities.Photo)
    photo_repository = providers.Singleton(repositories.PhotoRepository,
                                           object_factory=photo.provider,
                                           fs=file_storage,
                                           db=database)
