"""
Inversion of Control in Picture layer.
"""

from injector import Binder, Module

from picture.domain.repositories import PictureRepository
from picture.infrastructure.repositories import DjangoPictureRepository


class PictureModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(PictureRepository, DjangoPictureRepository)
