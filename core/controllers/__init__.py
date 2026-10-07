"""
core/controllers/__init__.py - Controller Katmanı Dışa Aktarımları (MVC)
"""

from .user_controller import UserController, user_controller_view
from .api_user_controller import ApiUserController, api_user_controller_view
from .announcement_controller import AnnouncementController
from .api_announcement_controller import ApiAnnouncementController

from .user_urls import urlpatterns as user_urlpatterns
from .api_urls import urlpatterns as api_user_urlpatterns
from .announcement_urls import urlpatterns as announcement_urlpatterns
from .api_announcement_urls import urlpatterns as api_announcement_urlpatterns

__all__ = [
    "UserController",
    "user_controller_view",
    "ApiUserController",
    "api_user_controller_view",
    "AnnouncementController",
    "ApiAnnouncementController",
    "user_urlpatterns",
    "api_user_urlpatterns",
    "announcement_urlpatterns",
    "api_announcement_urlpatterns",
]
