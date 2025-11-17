"""
Inversion of Control in Identity layer.
"""

from injector import Binder, Module

from identity.domain.repositories import UserRepository
from identity.infrastructure.repositories import DjangoUserRepository


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UserRepository, DjangoUserRepository)

