"""
core/controllers/application_urls.py - Web HTML İş & Staj Başvurusu Rotaları (Direct Routes)
"""

from django.urls import path
from core.controllers.application_controller import ApplicationController

urlpatterns = [
    # 1. READ ALL & CREATE: Ana Görünüm
    path('', ApplicationController.as_view(), name='applications_page'),
    path('list/', ApplicationController.as_view(), name='applications_list'),
    path('create/', ApplicationController.as_view(), name='applications_create'),

    # 2. DETAIL & DELETE
    path('<int:application_id>/', ApplicationController.as_view(), name='application_detail'),
    path('<int:application_id>/delete/', ApplicationController.as_view(), name='application_delete'),
]
