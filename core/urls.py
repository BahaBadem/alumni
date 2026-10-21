"""
URL configuration for core project (MVC Architecture).

Bu modül, projenin merkezi rota yapılandırmasını (Root URLconf) içerir.
User ve Announcement modüllerinin Web ve API operasyonları doğrudan Controller
ve View katmanlarına bağlanmıştır.
"""

from django.contrib import admin
from django.urls import path, include

# Demo & Dokümantasyon View'ları
from .views import (
    home, about, hello, calculate_sum, health_check,
    swagger_ui_view, swagger_json_view,
    # Web CRUD View Fonksiyonları
    user_list_view, user_create_view, user_detail_view,
    user_update_view, user_delete_view, user_web_view,
    # API CRUD View Fonksiyonları
    api_user_list_view, api_user_create_view, api_user_detail_view,
    api_user_update_view, api_user_patch_view, api_user_delete_view,
    user_api_view,
)

# Announcement Controller Sınıfları
from core.controllers.announcement_controller import AnnouncementController
from core.controllers.api_announcement_controller import ApiAnnouncementController

# Job Posting Controller Sınıfları (Direct & Nested)
from core.controllers.job_posting_controller import JobPostingController
from core.controllers.api_job_posting_controller import ApiJobPostingController

# Application Controller Sınıfları (Direct & Nested)
from core.controllers.application_controller import ApplicationController
from core.controllers.api_application_controller import ApiApplicationController

urlpatterns = [
    # --------------------------------------------------------------------------
    # 1. YÖNETİM & SİSTEM ROTALARI
    # --------------------------------------------------------------------------
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('about', about),

    # --------------------------------------------------------------------------
    # 2. DEMO & YARDIMCI ROTALAR
    # --------------------------------------------------------------------------
    path('hello/', hello, name='hello'),
    path('hello/<str:name>/', hello, name='hello_name'),
    path('sum/<int:num1>/<int:num2>/', calculate_sum, name='sum'),
    path('sum/<int:num1>/<int:num2>', calculate_sum),

    # --------------------------------------------------------------------------
    # 3. SAĞLIK KONTROLÜ (HEALTH CHECK)
    # --------------------------------------------------------------------------
    path('api/healt/', health_check, name='health_check'),
    path('api/healt', health_check),
    path('api/health/', health_check, name='health_check_alt'),
    path('api/health', health_check),

    # --------------------------------------------------------------------------
    # 4. API DOKÜMANTASYONU (SWAGGER / OPENAPI 3.0)
    # --------------------------------------------------------------------------
    path('api/swagger/', swagger_ui_view, name='swagger_ui'),
    path('api/swagger', swagger_ui_view),
    path('api/swagger.json', swagger_json_view, name='swagger_json'),

    # --------------------------------------------------------------------------
    # 5. USER WEB CRUD ROTALARI (HTML PRESENTATION & CONTROLLER VIEWS)
    # --------------------------------------------------------------------------
    path('users/', user_web_view, name='users_page'),
    path('users', user_web_view),
    path('users/list/', user_list_view, name='users_list'),
    path('users/create/', user_create_view, name='users_create'),
    path('users/<int:user_id>/', user_detail_view, name='user_detail'),
    path('users/<int:user_id>', user_detail_view),
    path('users/<int:user_id>/update/', user_update_view, name='user_update'),
    path('users/<int:user_id>/delete/', user_delete_view, name='user_delete'),

    # --------------------------------------------------------------------------
    # 6. USER REST API CRUD ROTALARI (JSON DTO PRESENTATION & CONTROLLER VIEWS)
    # --------------------------------------------------------------------------
    path('api/users/', user_api_view, name='api_users'),
    path('api/users', user_api_view),
    path('api/users/list/', api_user_list_view, name='api_users_list_explicit'),
    path('api/users/create/', api_user_create_view, name='api_users_create_explicit'),
    path('api/users/<int:user_id>/', user_api_view, name='api_user_detail'),
    path('api/users/<int:user_id>', user_api_view),
    path('api/users/<int:user_id>/detail/', api_user_detail_view, name='api_user_detail_explicit'),
    path('api/users/<int:user_id>/update/', api_user_update_view, name='api_user_update_explicit'),
    path('api/users/<int:user_id>/patch/', api_user_patch_view, name='api_user_patch_explicit'),
    path('api/users/<int:user_id>/delete/', api_user_delete_view, name='api_user_delete_explicit'),

    # --------------------------------------------------------------------------
    # 7. ANNOUNCEMENT WEB CRUD ROTALARI (HTML PRESENTATION)
    # --------------------------------------------------------------------------
    path('announcements/', AnnouncementController.as_view(), name='announcements_page'),
    path('announcements', AnnouncementController.as_view()),
    path('announcements/list/', AnnouncementController.as_view(), name='announcements_list'),
    path('announcements/create/', AnnouncementController.as_view(), name='announcements_create'),
    path('announcements/<int:announcement_id>/', AnnouncementController.as_view(), name='announcement_detail'),
    path('announcements/<int:announcement_id>', AnnouncementController.as_view()),
    path('announcements/<int:announcement_id>/update/', AnnouncementController.as_view(), name='announcement_update'),
    path('announcements/<int:announcement_id>/delete/', AnnouncementController.as_view(), name='announcement_delete'),

    # --------------------------------------------------------------------------
    # 8. ANNOUNCEMENT REST API CRUD ROTALARI (JSON PRESENTATION)
    # --------------------------------------------------------------------------
    path('api/announcements/', ApiAnnouncementController.as_view(), name='api_announcements'),
    path('api/announcements', ApiAnnouncementController.as_view()),
    path('api/announcements/list/', ApiAnnouncementController.as_view(), name='api_announcements_list_explicit'),
    path('api/announcements/create/', ApiAnnouncementController.as_view(), name='api_announcements_create_explicit'),
    path('api/announcements/<int:announcement_id>/', ApiAnnouncementController.as_view(), name='api_announcement_detail'),
    path('api/announcements/<int:announcement_id>', ApiAnnouncementController.as_view()),
    path('api/announcements/<int:announcement_id>/update/', ApiAnnouncementController.as_view(), name='api_announcement_update_explicit'),
    path('api/announcements/<int:announcement_id>/patch/', ApiAnnouncementController.as_view(), name='api_announcement_patch_explicit'),
    path('api/announcements/<int:announcement_id>/delete/', ApiAnnouncementController.as_view(), name='api_announcement_delete_explicit'),

    # --------------------------------------------------------------------------
    # 9. JOB POSTING DIRECT WEB CRUD ROTALARI (DOĞRUDAN WEB SUNUMU)
    # --------------------------------------------------------------------------
    path('jobs/', JobPostingController.as_view(), name='jobs_page'),
    path('jobs', JobPostingController.as_view()),
    path('jobs/list/', JobPostingController.as_view(), name='jobs_list'),
    path('jobs/create/', JobPostingController.as_view(), name='jobs_create'),
    path('jobs/<int:job_id>/', JobPostingController.as_view(), name='job_detail'),
    path('jobs/<int:job_id>', JobPostingController.as_view()),
    path('jobs/<int:job_id>/delete/', JobPostingController.as_view(), name='job_delete'),

    # --------------------------------------------------------------------------
    # 10. JOB POSTING DIRECT REST API CRUD ROTALARI (DOĞRUDAN REST API)
    # --------------------------------------------------------------------------
    path('api/jobs/', ApiJobPostingController.as_view(), name='api_jobs'),
    path('api/jobs', ApiJobPostingController.as_view()),
    path('api/jobs/list/', ApiJobPostingController.as_view(), name='api_jobs_list_explicit'),
    path('api/jobs/create/', ApiJobPostingController.as_view(), name='api_jobs_create_explicit'),
    path('api/jobs/<int:job_id>/', ApiJobPostingController.as_view(), name='api_job_detail'),
    path('api/jobs/<int:job_id>', ApiJobPostingController.as_view()),
    path('api/jobs/<int:job_id>/detail/', ApiJobPostingController.as_view(), name='api_job_detail_explicit'),
    path('api/jobs/<int:job_id>/update/', ApiJobPostingController.as_view(), name='api_job_update_explicit'),
    path('api/jobs/<int:job_id>/patch/', ApiJobPostingController.as_view(), name='api_job_patch_explicit'),
    path('api/jobs/<int:job_id>/delete/', ApiJobPostingController.as_view(), name='api_job_delete_explicit'),

    # --------------------------------------------------------------------------
    # 11. NESTED WEB CRUD ROTALARI (MEZUNA BAĞLI İÇ İÇE WEB ROTALARI)
    # --------------------------------------------------------------------------
    path('users/<int:user_id>/jobs/', JobPostingController.as_view(), name='user_jobs_page'),
    path('users/<int:user_id>/jobs', JobPostingController.as_view()),
    path('users/<int:user_id>/jobs/<int:job_id>/', JobPostingController.as_view(), name='user_job_detail_page'),

    # --------------------------------------------------------------------------
    # 12. NESTED REST API CRUD ROTALARI (MEZUNA BAĞLI İÇ İÇE REST API)
    # --------------------------------------------------------------------------
    path('api/users/<int:user_id>/jobs/', ApiJobPostingController.as_view(), name='api_user_jobs'),
    path('api/users/<int:user_id>/jobs', ApiJobPostingController.as_view()),
    path('api/users/<int:user_id>/jobs/create/', ApiJobPostingController.as_view(), name='api_user_jobs_create_explicit'),
    path('api/users/<int:user_id>/jobs/<int:job_id>/', ApiJobPostingController.as_view(), name='api_user_job_detail'),
    path('api/users/<int:user_id>/jobs/<int:job_id>', ApiJobPostingController.as_view()),
    path('api/users/<int:user_id>/jobs/<int:job_id>/update/', ApiJobPostingController.as_view(), name='api_user_job_update_explicit'),
    path('api/users/<int:user_id>/jobs/<int:job_id>/patch/', ApiJobPostingController.as_view(), name='api_user_job_patch_explicit'),
    path('api/users/<int:user_id>/jobs/<int:job_id>/delete/', ApiJobPostingController.as_view(), name='api_user_job_delete_explicit'),

    # --------------------------------------------------------------------------
    # 13. APPLICATION DIRECT WEB CRUD ROTALARI (DOĞRUDAN WEB SUNUMU)
    # --------------------------------------------------------------------------
    path('applications/', ApplicationController.as_view(), name='applications_page'),
    path('applications', ApplicationController.as_view()),
    path('applications/list/', ApplicationController.as_view(), name='applications_list'),
    path('applications/create/', ApplicationController.as_view(), name='applications_create'),
    path('applications/<int:application_id>/', ApplicationController.as_view(), name='application_detail'),
    path('applications/<int:application_id>', ApplicationController.as_view()),
    path('applications/<int:application_id>/delete/', ApplicationController.as_view(), name='application_delete'),

    # --------------------------------------------------------------------------
    # 14. APPLICATION DIRECT REST API CRUD ROTALARI (DOĞRUDAN REST API)
    # --------------------------------------------------------------------------
    path('api/applications/', ApiApplicationController.as_view(), name='api_applications'),
    path('api/applications', ApiApplicationController.as_view()),
    path('api/applications/list/', ApiApplicationController.as_view(), name='api_applications_list_explicit'),
    path('api/applications/create/', ApiApplicationController.as_view(), name='api_applications_create_explicit'),
    path('api/applications/<int:application_id>/', ApiApplicationController.as_view(), name='api_application_detail'),
    path('api/applications/<int:application_id>', ApiApplicationController.as_view()),
    path('api/applications/<int:application_id>/detail/', ApiApplicationController.as_view(), name='api_application_detail_explicit'),
    path('api/applications/<int:application_id>/update/', ApiApplicationController.as_view(), name='api_application_update_explicit'),
    path('api/applications/<int:application_id>/patch/', ApiApplicationController.as_view(), name='api_application_patch_explicit'),
    path('api/applications/<int:application_id>/delete/', ApiApplicationController.as_view(), name='api_application_delete_explicit'),

    # --------------------------------------------------------------------------
    # 15. APPLICATION NESTED WEB CRUD - JOB ALTINDA (İLAN ALTINDAKİ BAŞVURULAR)
    # --------------------------------------------------------------------------
    path('jobs/<int:job_id>/applications/', ApplicationController.as_view(), name='job_applications_page'),
    path('jobs/<int:job_id>/applications', ApplicationController.as_view()),
    path('jobs/<int:job_id>/applications/create/', ApplicationController.as_view(), name='job_applications_create'),
    path('jobs/<int:job_id>/applications/<int:application_id>/', ApplicationController.as_view(), name='job_application_detail_page'),
    path('jobs/<int:job_id>/applications/<int:application_id>', ApplicationController.as_view()),
    path('jobs/<int:job_id>/applications/<int:application_id>/delete/', ApplicationController.as_view(), name='job_application_delete'),

    # --------------------------------------------------------------------------
    # 16. APPLICATION NESTED REST API - JOB ALTINDA (İLAN ALTINDAKİ REST API)
    # --------------------------------------------------------------------------
    path('api/jobs/<int:job_id>/applications/', ApiApplicationController.as_view(), name='api_job_applications'),
    path('api/jobs/<int:job_id>/applications', ApiApplicationController.as_view()),
    path('api/jobs/<int:job_id>/applications/create/', ApiApplicationController.as_view(), name='api_job_applications_create_explicit'),
    path('api/jobs/<int:job_id>/applications/<int:application_id>/', ApiApplicationController.as_view(), name='api_job_application_detail'),
    path('api/jobs/<int:job_id>/applications/<int:application_id>', ApiApplicationController.as_view()),
    path('api/jobs/<int:job_id>/applications/<int:application_id>/update/', ApiApplicationController.as_view(), name='api_job_application_update_explicit'),
    path('api/jobs/<int:job_id>/applications/<int:application_id>/patch/', ApiApplicationController.as_view(), name='api_job_application_patch_explicit'),
    path('api/jobs/<int:job_id>/applications/<int:application_id>/delete/', ApiApplicationController.as_view(), name='api_job_application_delete_explicit'),

    # --------------------------------------------------------------------------
    # 17. APPLICATION NESTED WEB CRUD - MEZUN ALTINDA (MEZUNUN BAŞVURULARI)
    # --------------------------------------------------------------------------
    path('users/<int:user_id>/applications/', ApplicationController.as_view(), name='user_applications_page'),
    path('users/<int:user_id>/applications', ApplicationController.as_view()),
    path('users/<int:user_id>/applications/create/', ApplicationController.as_view(), name='user_applications_create'),
    path('users/<int:user_id>/applications/<int:application_id>/', ApplicationController.as_view(), name='user_application_detail_page'),
    path('users/<int:user_id>/applications/<int:application_id>', ApplicationController.as_view()),
    path('users/<int:user_id>/applications/<int:application_id>/delete/', ApplicationController.as_view(), name='user_application_delete'),

    # --------------------------------------------------------------------------
    # 18. APPLICATION NESTED REST API - MEZUN ALTINDA (MEZUNUN REST API BAŞVURULARI)
    # --------------------------------------------------------------------------
    path('api/users/<int:user_id>/applications/', ApiApplicationController.as_view(), name='api_user_applications'),
    path('api/users/<int:user_id>/applications', ApiApplicationController.as_view()),
    path('api/users/<int:user_id>/applications/create/', ApiApplicationController.as_view(), name='api_user_applications_create_explicit'),
    path('api/users/<int:user_id>/applications/<int:application_id>/', ApiApplicationController.as_view(), name='api_user_application_detail'),
    path('api/users/<int:user_id>/applications/<int:application_id>', ApiApplicationController.as_view()),
    path('api/users/<int:user_id>/applications/<int:application_id>/update/', ApiApplicationController.as_view(), name='api_user_application_update_explicit'),
    path('api/users/<int:user_id>/applications/<int:application_id>/patch/', ApiApplicationController.as_view(), name='api_user_application_patch_explicit'),
    path('api/users/<int:user_id>/applications/<int:application_id>/delete/', ApiApplicationController.as_view(), name='api_user_application_delete_explicit'),
]
