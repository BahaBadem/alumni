"""
core/controllers/announcement_urls.py - AnnouncementController Web Rotaları (MVC)

Bu modül, AnnouncementController sınıfına ait Web HTML arayüzü rotalarını tanımlar.
"""

from django.urls import path
from core.controllers.announcement_controller import AnnouncementController

_controller = AnnouncementController()

urlpatterns = [
    # 1. READ ALL & CREATE (Ana Duyurular Sayfası)
    path('', _controller.dispatch, name='announcements_page'),
    path('list/', _controller.list, name='announcements_list'),

    # 2. CREATE (Form gönderimi)
    path('create/', _controller.create, name='announcements_create'),

    # 3. READ SINGLE (Tekil Duyuru Detayı)
    path('<int:announcement_id>/', _controller.detail, name='announcement_detail'),

    # 4. UPDATE (Duyuru Güncelleme)
    path('<int:announcement_id>/update/', _controller.update, name='announcement_update'),

    # 5. DELETE (Duyuru Silme)
    path('<int:announcement_id>/delete/', _controller.delete, name='announcement_delete'),
]
