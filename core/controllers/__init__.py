"""
core/controllers/__init__.py - Controller Katmanı Dışa Aktarımları (MVC)
"""

from .user_controller import UserController, user_controller_view
from .api_user_controller import ApiUserController, api_user_controller_view
from .announcement_controller import AnnouncementController
from .api_announcement_controller import ApiAnnouncementController
from .job_posting_controller import JobPostingController
from .api_job_posting_controller import ApiJobPostingController
from .application_controller import ApplicationController
from .api_application_controller import ApiApplicationController

from .user_urls import urlpatterns as user_urlpatterns
from .api_urls import urlpatterns as api_user_urlpatterns
from .announcement_urls import urlpatterns as announcement_urlpatterns
from .api_announcement_urls import urlpatterns as api_announcement_urlpatterns
from .job_posting_urls import urlpatterns as job_posting_urlpatterns
from .api_job_posting_urls import urlpatterns as api_job_posting_urlpatterns
from .application_urls import urlpatterns as application_urlpatterns
from .api_application_urls import urlpatterns as api_application_urlpatterns

__all__ = [
    "UserController",
    "user_controller_view",
    "ApiUserController",
    "api_user_controller_view",
    "AnnouncementController",
    "ApiAnnouncementController",
    "JobPostingController",
    "ApiJobPostingController",
    "ApplicationController",
    "ApiApplicationController",
    "user_urlpatterns",
    "api_user_urlpatterns",
    "announcement_urlpatterns",
    "api_announcement_urlpatterns",
    "job_posting_urlpatterns",
    "api_job_posting_urlpatterns",
    "application_urlpatterns",
    "api_application_urlpatterns",
]
