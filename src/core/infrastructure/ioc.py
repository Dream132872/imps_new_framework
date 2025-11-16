"""
Inversion of Control in Core layer.
"""

from injector import Binder, Module

from core.domain.repositories import UserRepository
from core.domain.services import FileStorageService
from core.infrastructure.repositories import DjangoUserRepository
from core.infrastructure.services import DjangoFileStorageService


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UserRepository, DjangoUserRepository)
        binder.bind(FileStorageService, DjangoFileStorageService)
