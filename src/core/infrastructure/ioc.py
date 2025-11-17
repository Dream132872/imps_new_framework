"""
Inversion of Control in Core layer.
"""

from injector import Binder, Module

from core.domain.repositories import UserRepository
from core.infrastructure.repositories import DjangoUserRepository


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UserRepository, DjangoUserRepository)
