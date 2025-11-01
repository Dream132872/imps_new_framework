# Exception Mapping Guide

This guide explains how to map Domain exceptions to Application exceptions in the DDD architecture.

## Exception Flow

```
Domain Layer
    ↓ (raises)
DomainException (e.g., PictureNotFoundError)
    ↓ (caught & transformed in)
Application Layer
    ↓ (transforms to)
ApplicationException (e.g., ApplicationNotFoundError)
    ↓ (handled in)
Infrastructure Layer
    ↓ (converts to)
HTTP Response / UI Message
```

## Domain → Application Exception Mapping

| Domain Exception | Application Exception | HTTP Status | When to Use |
|-----------------|---------------------|-------------|-------------|
| `DomainEntityNotFoundError`<br>(e.g., `PictureNotFoundError`, `UserNotFoundError`) | `ApplicationNotFoundError` | 404 Not Found | Entity not found in repository |
| `DomainValidationError` | `ApplicationValidationError` | 400 Bad Request | Input validation failed |
| `DomainInvalidEntityError` | `ApplicationInvalidEntityError` | 400 Bad Request | Entity is in an invalid state |
| `DomainBusinessRuleViolationError` | `ApplicationBusinessRuleViolationError` | 422 Unprocessable Entity | Business rule violated |
| `DomainConcurrencyError` | `ApplicationConcurrencyError` | 409 Conflict | Optimistic locking conflict |
| Any other `DomainException` | `ApplicationError` | 500 Internal Server Error | Generic fallback |

## Usage Examples

### Option 1: Using the Exception Mapper (Recommended)

The `map_domain_exception_to_application()` utility automatically maps domain exceptions:

```python
from shared.application.exception_mapper import map_domain_exception_to_application
from core.domain.exceptions.picture import PictureNotFoundError

class DeletePictureCommandHandler:
    def handle(self, command: DeletePictureCommand) -> str:
        try:
            picture = self.uow[PictureRepository].get_by_id(command.picture_id)
            if not picture:
                raise PictureNotFoundError(f"Picture {command.picture_id} not found")
            
            self.uow[PictureRepository].delete(picture)
            return str(command.picture_id)
        except PictureNotFoundError as e:
            # Automatically maps to ApplicationNotFoundError
            raise map_domain_exception_to_application(e) from e
        except DomainValidationError as e:
            # Automatically maps to ApplicationValidationError
            raise map_domain_exception_to_application(e) from e
```

### Option 2: Manual Mapping

You can also map exceptions manually if you need custom messages or details:

```python
from shared.application.exceptions import ApplicationNotFoundError
from core.domain.exceptions.picture import PictureNotFoundError

class DeletePictureCommandHandler:
    def handle(self, command: DeletePictureCommand) -> str:
        try:
            picture = self.uow[PictureRepository].get_by_id(command.picture_id)
            if not picture:
                raise PictureNotFoundError(f"Picture {command.picture_id} not found")
            
            self.uow[PictureRepository].delete(picture)
            return str(command.picture_id)
        except PictureNotFoundError as e:
            # Manual mapping with custom message
            raise ApplicationNotFoundError(
                message=f"Picture not found: {command.picture_id}",
                details={"picture_id": command.picture_id}
            ) from e
```

### Option 3: Multiple Domain Exceptions

Handle multiple domain exceptions at once:

```python
from shared.application.exception_mapper import map_domain_exception_to_application
from shared.domain.exceptions import (
    DomainEntityNotFoundError,
    DomainValidationError,
    DomainBusinessRuleViolationError,
)

class UpdatePictureCommandHandler:
    def handle(self, command: UpdatePictureCommand) -> str:
        try:
            picture = self.uow[PictureRepository].get_by_id(command.picture_id)
            if not picture:
                raise PictureNotFoundError(f"Picture {command.picture_id} not found")
            
            # Domain validation
            if not command.title:
                raise DomainValidationError("Title is required")
            
            # Business rule check
            if picture.is_locked and not command.force:
                raise DomainBusinessRuleViolationError("Picture is locked and cannot be modified")
            
            picture.update(command.title, command.description)
            self.uow[PictureRepository].save(picture)
            return str(picture.id)
            
        except (DomainEntityNotFoundError, DomainValidationError, DomainBusinessRuleViolationError) as e:
            # Automatically maps to the correct Application exception
            raise map_domain_exception_to_application(e) from e
```

### Option 4: With Custom Details

Add additional context to the mapped exception:

```python
from shared.application.exception_mapper import map_domain_exception_to_application
from core.domain.exceptions.picture import PictureNotFoundError

class DeletePictureCommandHandler:
    def handle(self, command: DeletePictureCommand) -> str:
        try:
            picture = self.uow[PictureRepository].get_by_id(command.picture_id)
            if not picture:
                raise PictureNotFoundError(f"Picture {command.picture_id} not found")
            
            self.uow[PictureRepository].delete(picture)
            return str(command.picture_id)
        except PictureNotFoundError as e:
            # Map with additional details
            raise map_domain_exception_to_application(
                e,
                details={
                    "picture_id": command.picture_id,
                    "user_id": self.current_user.id,
                    "timestamp": datetime.now().isoformat()
                }
            ) from e
```

## Best Practices

1. **Always preserve the original exception** using `from e`:
   ```python
   raise map_domain_exception_to_application(e) from e
   ```
   This maintains the exception chain for debugging.

2. **Use the mapper utility** for consistency:
   - Reduces boilerplate code
   - Ensures correct mapping
   - Easy to maintain if mappings change

3. **Handle specific domain exceptions first**, then generic:
   ```python
   except PictureNotFoundError as e:
       raise map_domain_exception_to_application(e) from e
   except DomainException as e:
       raise map_domain_exception_to_application(e) from e
   except Exception as e:
       # Unexpected exceptions - wrap in generic ApplicationError
       raise ApplicationError(f"Unexpected error: {e}") from e
   ```

4. **Add context via details**:
   ```python
   raise map_domain_exception_to_application(
       e,
       details={"field": "email", "value": email, "reason": "already exists"}
   ) from e
   ```

5. **Never let Domain exceptions escape the Application layer**:
   - All domain exceptions should be caught and transformed
   - Infrastructure layer should only see Application exceptions

## Common Patterns

### Pattern 1: Simple Entity Operation
```python
try:
    entity = repository.get_by_id(id)
    if not entity:
        raise EntityNotFoundError(f"Entity {id} not found")
    return entity
except EntityNotFoundError as e:
    raise map_domain_exception_to_application(e) from e
```

### Pattern 2: Entity Creation with Validation
```python
try:
    if not command.is_valid():
        raise DomainValidationError("Invalid command data")
    entity = Entity.create(command.data)
    repository.save(entity)
    return entity.id
except (DomainValidationError, DomainInvalidEntityError) as e:
    raise map_domain_exception_to_application(e) from e
```

### Pattern 3: Business Rule Enforcement
```python
try:
    if entity.is_locked():
        raise DomainBusinessRuleViolationError("Entity is locked")
    entity.perform_action()
    repository.save(entity)
except DomainBusinessRuleViolationError as e:
    raise map_domain_exception_to_application(e) from e
```

### Pattern 4: Concurrency Handling
```python
try:
    entity = repository.get_by_id(id)
    if entity.version != command.expected_version:
        raise DomainConcurrencyError("Entity was modified by another user")
    entity.update(command.data)
    repository.save(entity)
except DomainConcurrencyError as e:
    raise map_domain_exception_to_application(e) from e
```

## Summary

- **Use `map_domain_exception_to_application()`** for automatic mapping
- **Always use `from e`** to preserve exception chain
- **Add details** when you need additional context
- **Never let Domain exceptions escape** the Application layer
- **Handle unexpected exceptions** with generic `ApplicationError`

