"""
core/controllers/user_urls.py - UserController Web Rotaları (MVC)

Bu modül, UserController sınıfına ait Web HTML arayüzü rotalarını tanımlar.
Döngüsel bağımlılığı önlemek için doğrudan UserController metotlarını bağlar.
"""

from django.urls import path
from core.controllers.user_controller import UserController

_web_controller = UserController(use_in_memory=False)

urlpatterns = [
    # 1. READ ALL: Ana kullanıcı listesi ve formu
    path('', _web_controller.dispatch, name='users_page'),
    path('list/', _web_controller.list, name='users_list'),

    # 2. CREATE: Yeni kullanıcı oluşturma
    path('create/', _web_controller.create, name='users_create'),

    # 3. READ SINGLE: Tekil kullanıcı detay görünümü
    path('<int:user_id>/', _web_controller.detail, name='user_detail'),

    # 4. UPDATE: Kullanıcı güncelleme
    path('<int:user_id>/update/', _web_controller.update, name='user_update'),

    # 5. DELETE: Kullanıcı silme
    path('<int:user_id>/delete/', _web_controller.delete, name='user_delete'),
]
