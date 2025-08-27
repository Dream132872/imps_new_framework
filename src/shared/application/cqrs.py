"""
Base CQRS (Command Query Responsibility Segregation) infrastructure.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Type, TypeVar

from asgiref.sync import sync_to_async

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

    @abstractmethod
    async def handle_async(self, command: C) -> R:
        """Handle a command asyncronously and return a result."""
        pass


class CommandBus:
    """Command bus for dispatching commands to their handlers."""

    def __init__(self):
        self._handlers: Dict[Type[Command], CommandHandler] = {}

    def registr_handler(self, command_type: Type[Command], handler: CommandHandler):
        """Register a command handler."""
        self._handlers[command_type] = handler

    def dispatch(self, command: Command) -> Any:
        """Dispatch a command to it's handler."""
        command_type = type(command)
        if not command_type in self._handlers:
            raise ValueError(f"No handler registered for type: {command_type}")

        handler = self._handlers[command_type]
        return handler.handle(command)

    async def dispatch_async(self, command: Command) -> Any:
        """Dispatch a command to it's handler asyncronously."""
        command_type = type(command)
        if not command_type in self._handlers:
            raise ValueError(f"No handler registered for type: {command_type}")

        handler = self._handlers[command_type]
        return await handler.handle_async(command)


class Query(ABC):
    """Base class for all queries."""

    def __init__(self):
        self.query_id = str(uuid.uuid4())
        self.timestamp = uuid.uuid1().time


class QueryHandler(ABC, Generic[Q, R]):
    """Base class for query handlers."""

    @abstractmethod
    def handle(self, query: Q) -> R:
        """Handle a query and return a result."""
        pass

    @abstractmethod
    async def handle_async(self, query: Q) -> R:
        """Handle a query and return a result."""
        pass


class QueryBus:
    """Query bus for dispatching queries to their handlers."""

    def __init__(self):
        self._handlers: Dict[Type[Query], QueryHandler] = {}

    def register_handler(self, query_type: Type[Query], handler: QueryHandler):
        """Register a query handler."""
        self._handlers[query_type] = handler

    def dispatch(self, query: Query) -> Any:
        query_type = type(query)
        if not query_type in self._handlers:
            raise ValueError(f"No handler registered for query type: {query_type}")

        handler = self._handlers[query_type]
        return handler.handle(query)

    async def dispatch_async(self, query: Query) -> Any:
        query_type = type(query)
        if not query_type in self._handlers:
            raise ValueError(f"No handler registered for query type: {query_type}")

        handler = self._handlers[query_type]
        return await handler.handle_async(query)


# Global command and query buses
command_bus = CommandBus()
query_bus = QueryBus()


def register_command_handler(command_type: Type[Command], handler: CommandHandler):
    """Register a command handler with the global command bus"""
    command_bus.registr_handler(command_type, handler)


def register_query_handler(query_type: Type[Query], handler: QueryHandler):
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
