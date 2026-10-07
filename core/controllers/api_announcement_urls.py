"""
core/controllers/api_announcement_urls.py - ApiAnnouncementController REST API Rotaları (MVC)

Bu modül, ApiAnnouncementController sınıfına ait REST API JSON rotalarını tanımlar.
"""

from django.urls import path
from core.controllers.api_announcement_controller import ApiAnnouncementController

_api_controller = ApiAnnouncementController()

urlpatterns = [
    # 1. READ ALL & CREATE: Ana RESTful uç nokta
    path('', _api_controller.dispatch, name='api_announcements'),
    path('list/', _api_controller.list, name='api_announcements_list_explicit'),
    path('create/', _api_controller.create, name='api_announcements_create_explicit'),

    # 2. DETAIL, UPDATE, PATCH, DELETE: Tekil RESTful uç noktalar
    path('<int:announcement_id>/', _api_controller.dispatch, name='api_announcement_detail'),
    path('<int:announcement_id>/update/', _api_controller.update, name='api_announcement_update_explicit'),
    path('<int:announcement_id>/patch/', _api_controller.partial_update, name='api_announcement_patch_explicit'),
    path('<int:announcement_id>/delete/', _api_controller.delete, name='api_announcement_delete_explicit'),
]
