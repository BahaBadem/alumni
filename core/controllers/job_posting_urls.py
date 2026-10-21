"""
core/controllers/job_posting_urls.py - Web HTML İş & Staj İlanı Rotaları (Direct Routes)
"""

from django.urls import path
from core.controllers.job_posting_controller import JobPostingController

urlpatterns = [
    # 1. READ ALL & CREATE: Ana Görünüm
    path('', JobPostingController.as_view(), name='jobs_page'),
    path('list/', JobPostingController.as_view(), name='jobs_list'),
    path('create/', JobPostingController.as_view(), name='jobs_create'),

    # 2. DETAIL & DELETE
    path('<int:job_id>/', JobPostingController.as_view(), name='job_detail'),
    path('<int:job_id>/delete/', JobPostingController.as_view(), name='job_delete'),
]
