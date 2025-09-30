"""
Inversion of Control in Core layer.
"""

from injector import Binder, Module

from core.application.services import DjangoFileStorageService
from core.domain.repositories import PictureRepository, UserRepository
from core.domain.services import FileStorageService
from core.infrastructure.repositories import (
    DjangoPictureRepository,
    DjangoUserRepository,
)


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UserRepository, DjangoUserRepository)
        binder.bind(PictureRepository, DjangoPictureRepository)
        binder.bind(FileStorageService, DjangoFileStorageService)
