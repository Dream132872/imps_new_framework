"""User model/entity related mappers"""

from identity.domain.entities import User as UserEntity
from identity.infrastructure.models import User as UserModel


class UserMapper:
    """User mappers"""

    @staticmethod
    def model_to_entity(model: UserModel) -> UserEntity:
        """Converts user model instance to user entity instance"""

        return UserEntity(
            id=str(model.id),
            username=model.username,
            email=model.email,
            is_active=model.is_active,
            first_name=model.first_name,
            last_name=model.last_name,
            is_staff=model.is_staff,
            is_superuser=model.is_superuser,
            password=model.password,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def entity_to_model(entity: UserEntity) -> UserModel:
        """Converts user entity instance to user model instance"""

        return UserModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            username=entity.username,
            password=entity.password,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            is_staff=entity.is_staff,
            is_superuser=entity.is_superuser,
            is_active=entity.is_active,
        )
