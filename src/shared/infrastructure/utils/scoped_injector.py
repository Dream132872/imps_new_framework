"""Implement scoped scope in django-injector"""

from typing import Any

from injector import Provider, Scope

from shared.infrastructure.context import request_scope


class ScopedProvider(Provider):
    """Custom provider that handles instance creation for scoped services.

    This provider wraps the original provider and handles the actual
    instance creation logic, separating concerns from the Scope class.
    """

    def __init__(self, original_provider: Any, scope_key: str = ""):
        """Initialize the scoped provider.

        Args:
            original_provider: The original provider (e.g., ClassProvider) that knows how to create instances.
        """
        self._original_provider = original_provider
        self._scoped_key = scope_key

    def get(self, injector: Any) -> Any:
        """Create an instance using the original provider.

        Args:
            injector: The injector instance to use for dependency injection

        Returns:
            The created instance
        """
        # Call the original provider's get method to create the instance
        # The original provider handles dependency injection
        # If instance doesn't exist in scope, create it using the scoped provider
        scope = request_scope.get()
        if self._scoped_key not in scope:
            # Wrap the provider in ScopedProvider to handle instance creation
            scope[self._scoped_key] = self._original_provider.get(injector)

        return scope[self._scoped_key]


class PerRequestScope(Scope):
    def __init__(self, injector: Any = None):
        """Initialize ScopedScope with an optional injector.

        Args:
            injector: The injector instance. If None, will be retrieved when needed.
        """
        self._injector = injector

    def get(self, key: Any, provider: Any) -> Any:
        """Get or create an instance scoped to the current request.

        Args:
            key: The binding key (typically a class type)
            provider: A provider object (e.g., ClassProvider) that creates the instance

        Returns:
            The scoped instance for the current request
        """
        # Use the key as the dictionary key (convert to string if not hashable)
        return ScopedProvider(
            provider,
            f"__{key.__name__}__" if isinstance(key, type) else f"__{str(key)}__",
        )
