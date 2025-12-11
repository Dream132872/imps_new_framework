"""User DTO mapper"""

from identity.application.dtos import UserDTO
from identity.domain.entities import User as UserEntity


class UserDTOMapper:
    """User dto mapper"""

    @staticmethod
    def to_dto(user: UserEntity) -> UserDTO:
        """Converts a domain entity to dto"""

        return UserDTO(
            id=str(user.id),
            username=user.username,
            email=user.email.value if user.email else "",
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def list_to_dto(users: list[UserEntity]) -> list[UserDTO]:
        """Converts user entities to dtos"""

        return [UserDTOMapper.to_dto(user) for user in users]
