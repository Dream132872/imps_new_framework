"""
Inversion of Control in Core layer
"""

from abc import ABC, abstractmethod

from injector import Binder, Module, inject


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
    def get_by_id(self, id: int):
        return "this is user"


class UserService2(UserServiceBase):
    @inject
    def __init__(self, roleService: RoleServiceBase) -> None:
        self.role_service = roleService

    def get_by_id(self, id: int):
        print(self.role_service.get_by_id(1))
        return "this is user 2"


class UserModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(UserServiceBase, UserService2)
        binder.bind(RoleServiceBase, RoleService)
