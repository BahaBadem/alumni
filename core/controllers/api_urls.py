"""
core/controllers/api_urls.py - ApiUserController REST API Rotaları (MVC)

Bu modül, ApiUserController sınıfına ait tüm REST API rotalarını tanımlar.
Döngüsel bağımlılığı önlemek için doğrudan ApiUserController metotlarını bağlar.
"""

from django.urls import path
from core.controllers.api_user_controller import ApiUserController

_api_controller = ApiUserController(use_in_memory=False)

urlpatterns = [
    # 1. READ ALL & CREATE: Ana RESTful uç nokta
    path('', _api_controller.dispatch, name='api_users'),
    path('list/', _api_controller.list, name='api_users_list_explicit'),
    path('create/', _api_controller.create, name='api_users_create_explicit'),

    # 2. READ SINGLE, UPDATE, PATCH, DELETE: Tekil RESTful uç nokta
    path('<int:user_id>/', _api_controller.dispatch, name='api_user_detail'),
    path('<int:user_id>/detail/', _api_controller.detail, name='api_user_detail_explicit'),
    path('<int:user_id>/update/', _api_controller.update, name='api_user_update_explicit'),
    path('<int:user_id>/patch/', _api_controller.partial_update, name='api_user_patch_explicit'),
    path('<int:user_id>/delete/', _api_controller.delete, name='api_user_delete_explicit'),
]
