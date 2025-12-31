from shared.infrastructure.api import api_v1

from .views import PictureController

api_v1.register_controllers(PictureController)
