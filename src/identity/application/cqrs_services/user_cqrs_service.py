"""
CQRS Service for User.
"""

from identity.application.queries import user_queries
from identity.application.query_handlers import user_query_handlers
from shared.application.cqrs import register_query_handler

# register queries
register_query_handler(
    user_queries.GetUserByIdQuery, user_query_handlers.GetUserByIdQueryHandler
)
register_query_handler(
    user_queries.SearchUsersQuery, user_query_handlers.SearchUsersQueryHandler
)

