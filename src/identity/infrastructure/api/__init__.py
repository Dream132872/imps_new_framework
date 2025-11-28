"""
Identity API implementation.
"""

from identity.infrastructure.api.v1.views import CustomTokenObtainPairController
from shared.infrastructure.api import api_v1

api_v1.register_controllers(CustomTokenObtainPairController)
