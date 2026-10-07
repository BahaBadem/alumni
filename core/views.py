"""
core/views.py - Merkezi Görünüm (View Layer) ve Controller Delegasyonları (MVC)

Bu modül, MVC mimarisindeki View (Sunum / Presentation) katmanını temsil eder.
Kullanıcı yönetimi için tüm CRUD operasyonlarını (Create, Read, Update, Delete)
hem Web HTML hem de REST API seviyesinde controller view fonksiyonları olarak sunar.
"""

import json
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# MVC Controller Sınıfları
from core.controllers.user_controller import UserController
from core.controllers.api_user_controller import ApiUserController

# Singleton Controller Örnekleri (Orkestrasyon & İş Mantığı)
_api_user_controller = ApiUserController(use_in_memory=False)
_web_user_controller = UserController(use_in_memory=False)


# ==============================================================================
# DEMO & STATİK SAYFA VİEW'LARI
# ==============================================================================
def home(request: HttpRequest) -> HttpResponse:
    """
    Kök dizine (/) gelen istekleri yakalayıp 
    ana sayfa şablonunu (index.html) render eden view fonksiyonu.
    """
    return render(request, "index.html")


def about(request: HttpRequest) -> HttpResponse:
    """
    /about/ rotasına gelen istekleri yakalayıp 
    hakkında sayfasını (about.html) render eden view fonksiyonu.
    """
    return render(request, "about.html")


def hello(request: HttpRequest, name: str = "World") -> HttpResponse:
    """
    /hello rotasında 'Hello, World!',
    /hello/<name>/ rotasında dinamik olarak 'Hello, {name}!' basan view fonksiyonu.
    """
    return HttpResponse(f"Hello, {name}!")


def calculate_sum(request: HttpRequest, num1: int, num2: int) -> HttpResponse:
    """
    /sum/<num1>/<num2>/ rotasına gelen iki sayının toplamını ekrana basan view fonksiyonu.
    """
    total = num1 + num2
    return HttpResponse(str(total))


@require_http_methods(["GET"])
def health_check(request: HttpRequest) -> JsonResponse:
    """
    /api/healt veya /api/health rotasına GET isteği atıldığında 
    JSON formatında durum bilgisi döndüren view fonksiyonu.
    """
    return JsonResponse({
        "status": "ok",
        "message": "healthy"
    })


# ==============================================================================
# 🌐 WEB HTML CONTROLLER VIEW FONKSİYONLARI (CRUD)
# ==============================================================================

# 1. READ (Tümünü Listele)
@csrf_exempt
def user_list_view(request: HttpRequest) -> HttpResponse:
    """[CRUD: READ ALL] Kullanıcı listesini ve formunu HTML olarak sunar."""
    return _web_user_controller.list(request)


# 2. CREATE (Yeni Kullanıcı Oluştur)
@csrf_exempt
def user_create_view(request: HttpRequest) -> HttpResponse:
    """[CRUD: CREATE] Form üzerinden yeni kullanıcı kaydı oluşturur (POST)."""
    if request.method == "POST":
        return _web_user_controller.create(request)
    return _web_user_controller.list(request)


# 3. READ (Tekil Kullanıcı Detayı)
@csrf_exempt
def user_detail_view(request: HttpRequest, user_id: int) -> HttpResponse:
    """[CRUD: READ SINGLE] Belirtilen kullanıcının detayını HTML olarak sunar."""
    return _web_user_controller.detail(request, user_id=user_id)


# 4. UPDATE (Kullanıcı Güncelle)
@csrf_exempt
def user_update_view(request: HttpRequest, user_id: int) -> HttpResponse:
    """[CRUD: UPDATE] Belirtilen kullanıcının bilgilerini günceller."""
    return _web_user_controller.update(request, user_id=user_id)


# 5. DELETE (Kullanıcı Sil)
@csrf_exempt
def user_delete_view(request: HttpRequest, user_id: int) -> HttpResponse:
    """[CRUD: DELETE] Belirtilen kullanıcıyı siler."""
    return _web_user_controller.delete(request, user_id=user_id)


# Ana Web Görünüm Giriş Noktası (Dispatcher)
@csrf_exempt
def user_web_view(request: HttpRequest, user_id: int = None) -> HttpResponse:
    """Web MVC ana giriş noktası (GET ve POST yönlendirmesi)."""
    return _web_user_controller.dispatch(request, user_id=user_id)


# ==============================================================================
# 🚀 REST API CONTROLLER VIEW FONKSİYONLARI (CRUD)
# ==============================================================================

# 1. READ (JSON Liste)
@csrf_exempt
def api_user_list_view(request: HttpRequest) -> JsonResponse:
    """[CRUD: READ ALL] Tüm kullanıcıları JSON listesi olarak döner (GET /api/users/)."""
    return _api_user_controller.list(request)


# 2. CREATE (JSON ile Yeni Kayıt)
@csrf_exempt
def api_user_create_view(request: HttpRequest) -> JsonResponse:
    """[CRUD: CREATE] JSON payload ile yeni kullanıcı oluşturur (POST /api/users/)."""
    return _api_user_controller.create(request)


# 3. READ (Tekil JSON Detay)
@csrf_exempt
def api_user_detail_view(request: HttpRequest, user_id: int) -> JsonResponse:
    """[CRUD: READ SINGLE] Tekil kullanıcının detayını JSON olarak döner (GET /api/users/<id>/)."""
    return _api_user_controller.detail(request, user_id=user_id)


# 4. UPDATE - PUT (Tam Güncelleme)
@csrf_exempt
def api_user_update_view(request: HttpRequest, user_id: int) -> JsonResponse:
    """[CRUD: UPDATE - PUT] Kullanıcı bilgilerini tamamen günceller (PUT /api/users/<id>/)."""
    return _api_user_controller.update(request, user_id=user_id)


# 5. UPDATE - PATCH (Kısmi Güncelleme)
@csrf_exempt
def api_user_patch_view(request: HttpRequest, user_id: int) -> JsonResponse:
    """[CRUD: UPDATE - PATCH] Kullanıcı bilgilerini kısmi günceller (PATCH /api/users/<id>/)."""
    return _api_user_controller.partial_update(request, user_id=user_id)


# 6. DELETE (Silme)
@csrf_exempt
def api_user_delete_view(request: HttpRequest, user_id: int = None) -> JsonResponse:
    """[CRUD: DELETE] Kullanıcıyı siler (DELETE /api/users/<id>/)."""
    return _api_user_controller.delete(request, user_id=user_id)


# Ana API Görünüm Giriş Noktası (Dispatcher)
@csrf_exempt
def user_api_view(request: HttpRequest, user_id: int = None) -> JsonResponse:
    """REST API ana giriş noktası (GET, POST, PUT, PATCH, DELETE yönlendirmesi)."""
    return _api_user_controller.dispatch(request, user_id=user_id)


# Geriye dönük uyumluluk takma adları (Backward Compatibility Aliases)
users_page_view = user_web_view
api_users_view = user_api_view


# ==============================================================================
# SWAGGER & API DOKÜMANTASYON VİEW'LARI
# ==============================================================================
def swagger_ui_view(request: HttpRequest) -> HttpResponse:
    """
    /api/swagger rotasında Swagger UI arayüzünü render eden view.
    """
    return render(request, "swagger.html")


def swagger_json_view(request: HttpRequest) -> JsonResponse:
    """
    /api/swagger.json rotasında kök dizindeki swagger.json dosyasını
    okuyup JSON formatında döndüren view.
    Dosyada bir güncelleme yapıldığında anında arayüze yansır.
    """
    from django.conf import settings
    swagger_file_path = settings.BASE_DIR / "swagger.json"
    if not swagger_file_path.exists():
        return JsonResponse({"error": "swagger.json dosyası bulunamadı."}, status=404)

    with open(swagger_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return JsonResponse(data, safe=False)
