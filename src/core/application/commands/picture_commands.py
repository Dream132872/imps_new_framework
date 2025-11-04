"""
Picture Commands for CQRS implementation.
Commands handle write operations that change the state of the system.
"""

import uuid
from dataclasses import dataclass

from shared.application.cqrs import Command


@dataclass
class DeletePictureCommand(Command):
    pk: uuid.UUID
