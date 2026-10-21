"""
core/controllers/api_job_posting_urls.py - REST API İş & Staj İlanı Rotaları (Direct Routes)
"""

from django.urls import path
from core.controllers.api_job_posting_controller import ApiJobPostingController

urlpatterns = [
    # 1. READ ALL & CREATE: Ana RESTful Uç Nokta
    path('', ApiJobPostingController.as_view(), name='api_jobs'),
    path('list/', ApiJobPostingController.as_view(), name='api_jobs_list_explicit'),
    path('create/', ApiJobPostingController.as_view(), name='api_jobs_create_explicit'),

    # 2. DETAIL, UPDATE, PATCH, DELETE: Tekil Uç Noktalar
    path('<int:job_id>/', ApiJobPostingController.as_view(), name='api_job_detail'),
    path('<int:job_id>/detail/', ApiJobPostingController.as_view(), name='api_job_detail_explicit'),
    path('<int:job_id>/update/', ApiJobPostingController.as_view(), name='api_job_update_explicit'),
    path('<int:job_id>/patch/', ApiJobPostingController.as_view(), name='api_job_patch_explicit'),
    path('<int:job_id>/delete/', ApiJobPostingController.as_view(), name='api_job_delete_explicit'),
]
