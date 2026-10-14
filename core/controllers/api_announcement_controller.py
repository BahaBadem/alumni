"""
core/controllers/api_announcement_controller.py - REST API Duyuru Controller'ı (MVC)

Bu modül, REST API istemcilerinden gelen JSON isteklerini karşılayan,
durum kodlarını (200, 201, 400, 404, 405) ve JSON çıktılarını yöneten,
standart HTTP fiilleri (GET, POST, PUT, PATCH, DELETE) üzerinden tam CRUD
operasyonlarını icra eden ApiAnnouncementController sınıfını içerir.

Veritabanı (Django ORM) veya bellek içi (In-Memory) deposunu destekler.
Varsayılan olarak veritabanı (Database Connection) modunda çalışır.
"""

import json
from urllib.parse import parse_qs
from typing import Optional, Dict, Any
from django.http import HttpRequest, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

# Veritabanı ve In-Memory Servis Katmanları
from core.services import announcement_service as db_service
import announcement as in_memory_service
from announcement_model import AnnouncementValidationError, AnnouncementNotFoundError


def extract_json_payload(request: HttpRequest) -> Optional[Dict[str, Any]]:
    """İstekten JSON gövdesini veya form verisini ayıklar."""
    content_type = request.content_type or ""
    if "application/json" in content_type or (request.body and request.body.strip().startswith(b"{")):
        try:
            return json.loads(request.body.decode("utf-8"))
        except Exception:
            return None
    if request.POST:
        return request.POST.dict()
    if request.body:
        try:
            parsed = parse_qs(request.body.decode("utf-8"))
            return {k: v[0] for k, v in parsed.items()}
        except Exception:
            pass
    return {}


class ApiAnnouncementController:
    """
    REST API Duyuru Controller'ı (MVC - Controller Katmanı).

    Desteklenen CRUD Operasyonları:
    - CREATE: POST   /api/announcements/      (201 Created)
    - READ:   GET    /api/announcements/      (200 OK)
    - DETAIL: GET    /api/announcements/<id>/ (200 OK / 404)
    - UPDATE: PUT    /api/announcements/<id>/ (200 OK / 400)
    - PATCH:  PATCH  /api/announcements/<id>/ (200 OK / 400)
    - DELETE: DELETE /api/announcements/<id>/ (200 OK / 404)
    """

    def __init__(self, use_in_memory: bool = False):
        """
        Args:
            use_in_memory (bool): False ise veritabanını (Django ORM) kullanır.
                                  True ise bellek içi (In-Memory) deposunu kullanır.
        """
        self.use_in_memory = use_in_memory

    @property
    def service(self):
        """Aktif servis katmanını döndürür (DB veya In-Memory)."""
        return in_memory_service if self.use_in_memory else db_service

    # --------------------------------------------------------------------------
    # CRUD: 1. CREATE (POST /api/announcements/)
    # --------------------------------------------------------------------------
    def create(self, request: HttpRequest) -> JsonResponse:
        """Yeni bir duyuru oluşturur (POST)."""
        data = extract_json_payload(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

        title = str(data.get("title") or data.get("baslik") or "").strip()
        content = str(data.get("content") or data.get("icerik") or "").strip()
        author = str(data.get("author") or data.get("yazar") or "Mezunlar Koordinatörlüğü").strip()
        category = str(data.get("category") or data.get("kategori") or "Genel").strip()
        is_active = data.get("is_active", data.get("aktif_mi", True))

        if not (title and content):
            return JsonResponse({
                "status": "error",
                "message": "Duyuru başlığı ('title') ve içeriği ('content') zorunludur."
            }, status=400)

        try:
            new_ann = self.service.create_announcement(
                title=title,
                content=content,
                author=author,
                category=category,
                is_active=is_active,
            )
            return JsonResponse({
                "status": "success",
                "message": "Duyuru başarıyla oluşturuldu.",
                "announcement": new_ann.to_dict(),
            }, status=201)
        except AnnouncementValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    # --------------------------------------------------------------------------
    # CRUD: 2. READ (GET /api/announcements/ & GET /api/announcements/<id>/)
    # --------------------------------------------------------------------------
    def list(self, request: HttpRequest) -> JsonResponse:
        """Tüm kayıtlı duyuruları JSON listesi halinde döndürür."""
        category = request.GET.get("category")
        keyword = request.GET.get("q")
        only_active = request.GET.get("active") == "true"

        if keyword or category:
            items = self.service.filter_announcements(
                keyword=keyword, category=category, only_active=only_active
            )
        else:
            items = self.service.get_all_announcements(only_active=only_active)

        return JsonResponse({
            "status": "success",
            "count": len(items),
            "announcements": [item.to_dict() for item in items]
        }, status=200)

    def detail(self, request: HttpRequest, announcement_id: int) -> JsonResponse:
        """Tekil duyuru detayını JSON olarak döndürür."""
        ann = self.service.get_announcement(announcement_id)
        if not ann:
            return JsonResponse({
                "status": "error",
                "message": f"{announcement_id} ID'li duyuru bulunamadı."
            }, status=404)

        return JsonResponse({
            "status": "success",
            "announcement": ann.to_dict()
        }, status=200)

    # --------------------------------------------------------------------------
    # CRUD: 3. UPDATE (PUT /api/announcements/<id>/)
    # --------------------------------------------------------------------------
    def update(self, request: HttpRequest, announcement_id: int) -> JsonResponse:
        """Duyuruyu tüm alanlarıyla tam günceller (PUT)."""
        data = extract_json_payload(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

        title = str(data.get("title") or data.get("baslik") or "").strip()
        content = str(data.get("content") or data.get("icerik") or "").strip()
        author = str(data.get("author") or data.get("yazar") or "").strip()
        category = str(data.get("category") or data.get("kategori") or "").strip()
        is_active = data.get("is_active", data.get("aktif_mi"))

        if not (title and content):
            return JsonResponse({
                "status": "error",
                "message": "PUT güncellemesinde 'title' ve 'content' zorunludur."
            }, status=400)

        try:
            updated = self.service.update_announcement(
                announcement_id=announcement_id,
                title=title,
                content=content,
                author=author or None,
                category=category or None,
                is_active=is_active,
            )
            return JsonResponse({
                "status": "success",
                "message": "Duyuru başarıyla güncellendi.",
                "announcement": updated.to_dict()
            }, status=200)
        except AnnouncementNotFoundError:
            return JsonResponse({
                "status": "error",
                "message": f"{announcement_id} ID'li duyuru bulunamadı."
            }, status=404)
        except AnnouncementValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    # --------------------------------------------------------------------------
    # CRUD: 4. PATCH (PATCH /api/announcements/<id>/)
    # --------------------------------------------------------------------------
    def patch(self, request: HttpRequest, announcement_id: int) -> JsonResponse:
        """Duyuruyu kısmi olarak günceller (PATCH)."""
        data = extract_json_payload(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

        try:
            updated = self.service.patch_announcement(announcement_id, **data)
            return JsonResponse({
                "status": "success",
                "message": "Duyuru kısmi olarak güncellendi.",
                "announcement": updated.to_dict()
            }, status=200)
        except AnnouncementNotFoundError:
            return JsonResponse({
                "status": "error",
                "message": f"{announcement_id} ID'li duyuru bulunamadı."
            }, status=404)
        except AnnouncementValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    def partial_update(self, request: HttpRequest, announcement_id: int) -> JsonResponse:
        """Kısmi güncelleme (PATCH) için URLconf uyumluluk metodu."""
        return self.patch(request, announcement_id)

    # --------------------------------------------------------------------------
    # CRUD: 5. DELETE (DELETE /api/announcements/<id>/)
    # --------------------------------------------------------------------------
    def delete(self, request: HttpRequest, announcement_id: Optional[int] = None) -> JsonResponse:
        """Duyuruyu siler (DELETE)."""
        target_id = announcement_id
        if target_id is None:
            data = extract_json_payload(request)
            if data and ("id" in data or "announcement_id" in data):
                target_id = int(data.get("id") or data.get("announcement_id"))

        if target_id is None:
            return JsonResponse({
                "status": "error",
                "message": "Silinecek duyuru kimliği ('id') belirtilmelidir."
            }, status=400)

        try:
            deleted = self.service.delete_announcement(target_id)
            return JsonResponse({
                "status": "success",
                "message": f"'{deleted.title}' başlıklı duyuru silindi.",
                "deleted_id": target_id
            }, status=200)
        except AnnouncementNotFoundError:
            return JsonResponse({
                "status": "error",
                "message": f"{target_id} ID'li duyuru bulunamadı."
            }, status=404)

    # --------------------------------------------------------------------------
    # REST DISPATCHER & CBV KÖPRÜSÜ
    # --------------------------------------------------------------------------
    def dispatch(self, request: HttpRequest, announcement_id: Optional[int] = None) -> JsonResponse:
        """HTTP fiiline göre ilgili metodu çalıştırır."""
        method = request.method
        if method == "GET":
            if announcement_id is not None:
                return self.detail(request, announcement_id)
            return self.list(request)
        elif method == "POST":
            return self.create(request)
        elif method == "PUT":
            if announcement_id is None:
                return JsonResponse({"status": "error", "message": "PUT için ID gereklidir."}, status=400)
            return self.update(request, announcement_id)
        elif method == "PATCH":
            if announcement_id is None:
                return JsonResponse({"status": "error", "message": "PATCH için ID gereklidir."}, status=400)
            return self.patch(request, announcement_id)
        elif method == "DELETE":
            return self.delete(request, announcement_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST", "PUT", "PATCH", "DELETE"])

    @classmethod
    def as_view(cls, use_in_memory: bool = False, **initkwargs):
        """Django URLconf için view callable döndürür."""
        def view(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            self = cls(use_in_memory=use_in_memory, **initkwargs)
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        return csrf_exempt(view)
