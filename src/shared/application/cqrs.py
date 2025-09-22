"""
Base CQRS (Command Query Responsibility Segregation) infrastructure.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from adrf.mixins import sync_to_async

from shared.application.exceptions import ConfigurationError
from shared.infrastructure.ioc import get_injector

# Type variables for generic commands and queries
C = TypeVar("C")  # Command type
Q = TypeVar("Q")  # Query type
R = TypeVar("R")  # Result type


class Command(ABC):
    """Base class for all commands."""

    def __init__(self):
        self.command_id = str(uuid.uuid4())
        self.timestamp = uuid.uuid1().time


class CommandHandler(ABC, Generic[C, R]):
    """Base class for command handlers."""

    @abstractmethod
    def handle(self, command: C) -> R:
        """Handle a command and return a result."""
        pass


class CommandBus:
    """Command bus for dispatching commands to their handlers."""

    def __init__(self) -> None:
        self.injector = get_injector()

    def registr_handler(self, command_type: type[Command], handler: CommandHandler):
        """Register a command handler."""
        self.injector.binder.bind(command_type, handler)

    def _get_handler(self, command: Command) -> CommandHandler:
        command_type = type(command)
        try:
            handler = self.injector.get(command_type)
        except Exception as e:
            err_msg = (
                f"An exception occured when trying to get {command_type}, error: {e}"
            )
            raise ConfigurationError(err_msg)

        return handler  # type: ignore

    def dispatch(self, command: Command) -> Any:
        """Dispatch a command to it's handler."""
        return self._get_handler(command).handle(command)

    async def dispatch_async(self, command: Command) -> Any:
        """Dispatch a command to it's handler asyncronously."""
        handler = self._get_handler(command)
        return await sync_to_async(handler.handle)(command)


@dataclass
class Query(ABC):
    """Base class for all queries."""

    def __post_init__(self) -> None:
        self.query_id = str(uuid.uuid4())
        self.timestamp = uuid.uuid1().time

        if hasattr(self, "page"):
            page = getattr(self, "page")
            if page is not None and page < 1:
                self.page = 1

        if hasattr(self, "page_size"):
            page_size = getattr(self, "page_size")
            if page_size is not None and page_size < 1:
                self.page_size = 1


class QueryHandler(ABC, Generic[Q, R]):
    """Base class for query handlers."""

    @abstractmethod
    def handle(self, query: Q) -> R:
        """Handle a query and return a result."""
        pass


class QueryBus:
    """Query bus for dispatching queries to their handlers."""

    def __init__(self) -> None:
        self.injector = get_injector()

    def register_handler(self, query_type: type[Query], handler: type[QueryHandler]):
        """Register a query handler."""
        self.injector.binder.bind(query_type, handler)

    def _get_handler(self, query: Query) -> QueryHandler:
        query_type = type(query)
        try:
            handler = self.injector.get(query_type)
        except Exception as e:
            err_msg = (
                f"An exception occured when trying to get {query_type}, error: {e}"
            )
            raise ConfigurationError(err_msg)

        return handler  # type: ignore

    def dispatch(self, query: Query) -> Any:
        """Dispatch a query to it's handler."""
        return self._get_handler(query).handle(query)

    async def dispatch_async(self, query: Query) -> Any:
        """Dispatch a query to it's handler async."""
        handler = self._get_handler(query)
        return await sync_to_async(handler.handle)(query)


# Global command and query buses
command_bus = CommandBus()
query_bus = QueryBus()


def register_command_handler(
    command_type: type[Command], handler: CommandHandler
) -> None:
    """Register a command handler with the global command bus"""
    command_bus.registr_handler(command_type, handler)


def register_query_handler(
    query_type: type[Query], handler: type[QueryHandler]
) -> None:
    """Register a query handler with the global query bus"""
    query_bus.register_handler(query_type, handler)


def dispatch_command(command: Command) -> Any:
    """Dispatch a command using the global command bus"""
    return command_bus.dispatch(command)


async def dispatch_command_async(command: Command) -> Any:
    """Dispatch a command asyncronously using the global command bus"""
    return await command_bus.dispatch_async(command)


def dispatch_query(query: Query) -> Any:
    """Dispatch a query using the global query bus"""
    return query_bus.dispatch(query)


async def dispatch_query_async(query: Query) -> Any:
    """Dispatch a query asyncronously using the global query bus"""
    return await query_bus.dispatch_async(query)
