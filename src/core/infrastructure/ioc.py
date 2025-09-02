"""
Inversion of Control in Core layer
"""

from abc import ABC, abstractmethod
from injector import Binder, Inject, InjectT, Injector, Module, inject


class UserServiceBase(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> str:
        pass


class UserService(UserServiceBase):
    def get_by_id(self, id: int):
        return "this is user"


class UserService2(UserServiceBase):
    def get_by_id(self, id: int):
        return "this is user 2"


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UserServiceBase, UserService2)
