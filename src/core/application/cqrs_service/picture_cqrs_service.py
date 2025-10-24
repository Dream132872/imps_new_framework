"""
CQRS Service for Picture.
"""

from core.application.command_handlers import *
from core.application.queries.picture_queries import *
from core.application.query_handlers.picture_query_handlers import *
from shared.application.cqrs import register_query_handler

# register queries
register_query_handler(SearchPictureQuery, SearchPictureQueryHandler)
register_query_handler(SearchFirstPictureQuery, SearchFirstPictureQueryHandler)
