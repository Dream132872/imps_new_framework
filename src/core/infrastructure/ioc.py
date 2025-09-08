"""
Inversion of Control in Core layer
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from injector import Binder, Inject, Module, SingletonScope


class RoleServiceBase(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> str:
        pass


class RoleService(RoleServiceBase):
    def get_by_id(self, id: int) -> str:
        return "role"


class UserServiceBase(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> str:
        pass


class UserService(UserServiceBase):
    def __init__(self, roleService: Inject[RoleServiceBase]) -> None:
        self.role_service = roleService
        print("this is user service")

    def get_by_id(self, id: int):
        print(self.role_service.get_by_id(1))
        return "this is user 2"


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(RoleServiceBase, RoleService, SingletonScope)
        binder.bind(UserServiceBase, UserService, SingletonScope)
