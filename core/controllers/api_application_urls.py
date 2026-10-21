"""
core/controllers/api_application_urls.py - REST API İş & Staj Başvurusu Rotaları (Direct Routes)
"""

from django.urls import path
from core.controllers.api_application_controller import ApiApplicationController

urlpatterns = [
    # 1. READ ALL & CREATE: Ana RESTful Uç Nokta
    path('', ApiApplicationController.as_view(), name='api_applications'),
    path('list/', ApiApplicationController.as_view(), name='api_applications_list_explicit'),
    path('create/', ApiApplicationController.as_view(), name='api_applications_create_explicit'),

    # 2. DETAIL, UPDATE, PATCH, DELETE: Tekil Uç Noktalar
    path('<int:application_id>/', ApiApplicationController.as_view(), name='api_application_detail'),
    path('<int:application_id>/detail/', ApiApplicationController.as_view(), name='api_application_detail_explicit'),
    path('<int:application_id>/update/', ApiApplicationController.as_view(), name='api_application_update_explicit'),
    path('<int:application_id>/patch/', ApiApplicationController.as_view(), name='api_application_patch_explicit'),
    path('<int:application_id>/delete/', ApiApplicationController.as_view(), name='api_application_delete_explicit'),
]
