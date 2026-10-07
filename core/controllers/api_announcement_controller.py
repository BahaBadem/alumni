"""
core/controllers/api_announcement_controller.py - REST API Duyuru Controller'ı (MVC)

Bu modül, REST API istemcilerinden gelen JSON isteklerini karşılayan,
durum kodlarını (200, 201, 400, 404, 405) ve JSON çıktılarını yöneten,
standart HTTP fiilleri (GET, POST, PUT, PATCH, DELETE) üzerinden tam CRUD
operasyonlarını icra eden ApiAnnouncementController sınıfını içerir.
"""

import json
from urllib.parse import parse_qs
from typing import Optional, Dict, Any
from django.http import HttpRequest, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

import announcement as announcement_service
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
            new_ann = announcement_service.create_announcement(
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
            items = announcement_service.filter_announcements(keyword=keyword, category=category)
        else:
            items = announcement_service.get_all_announcements(only_active=only_active)

        ann_list = [a.to_dict() for a in items]
        return JsonResponse({
            "status": "success",
            "count": len(ann_list),
            "announcements": ann_list,
        }, status=200)

    def detail(self, request: HttpRequest, announcement_id: int) -> JsonResponse:
        """Belirtilen ID'ye sahip tekil duyuruyu döndürür."""
        ann = announcement_service.get_announcement(announcement_id)
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
    # CRUD: 3. UPDATE (PUT & PATCH /api/announcements/<id>/)
    # --------------------------------------------------------------------------
    def update(self, request: HttpRequest, announcement_id: int) -> JsonResponse:
        """Duyuruyu tam günceller (PUT). Tüm alanlar zorunludur."""
        data = extract_json_payload(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

        title = str(data.get("title") or data.get("baslik") or "").strip()
        content = str(data.get("content") or data.get("icerik") or "").strip()
        author = str(data.get("author") or data.get("yazar") or "").strip()
        category = str(data.get("category") or data.get("kategori") or "Genel").strip()
        is_active = data.get("is_active", data.get("aktif_mi", True))

        if not (title and content and author):
            return JsonResponse({
                "status": "error",
                "message": "PUT metodu tam güncelleme gerektirir. 'title', 'content' ve 'author' zorunludur."
            }, status=400)

        try:
            updated = announcement_service.update_announcement(
                announcement_id=announcement_id,
                title=title,
                content=content,
                author=author,
                category=category,
                is_active=is_active,
            )
            return JsonResponse({
                "status": "success",
                "message": "Duyuru başarıyla güncellendi (PUT).",
                "announcement": updated.to_dict()
            }, status=200)
        except AnnouncementNotFoundError:
            return JsonResponse({"status": "error", "message": f"{announcement_id} ID'li duyuru bulunamadı."}, status=404)
        except AnnouncementValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    def partial_update(self, request: HttpRequest, announcement_id: int) -> JsonResponse:
        """Duyuruyu kısmi günceller (PATCH)."""
        data = extract_json_payload(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

        try:
            updated = announcement_service.patch_announcement(announcement_id=announcement_id, **data)
            return JsonResponse({
                "status": "success",
                "message": "Duyuru kısmi olarak güncellendi (PATCH).",
                "announcement": updated.to_dict()
            }, status=200)
        except AnnouncementNotFoundError:
            return JsonResponse({"status": "error", "message": f"{announcement_id} ID'li duyuru bulunamadı."}, status=404)
        except AnnouncementValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    # --------------------------------------------------------------------------
    # CRUD: 4. DELETE (DELETE /api/announcements/<id>/)
    # --------------------------------------------------------------------------
    def delete(self, request: HttpRequest, announcement_id: Optional[int] = None) -> JsonResponse:
        """Duyuru kaydını siler."""
        data = extract_json_payload(request) or {}
        target_id = announcement_id or data.get("id") or request.GET.get("id")

        if not target_id:
            return JsonResponse({
                "status": "error",
                "message": "Silinecek duyuru ID'si belirtilmelidir."
            }, status=400)

        try:
            deleted = announcement_service.delete_announcement(int(target_id))
            return JsonResponse({
                "status": "success",
                "message": f"'{deleted.title}' başlıklı duyuru silindi.",
                "deleted_id": deleted.id,
                "deleted_announcement": deleted.to_dict()
            }, status=200)
        except AnnouncementNotFoundError:
            return JsonResponse({"status": "error", "message": f"{target_id} ID'li duyuru bulunamadı."}, status=404)

    # --------------------------------------------------------------------------
    # CONTROLLER ENTRY POINT / DISPATCHER
    # --------------------------------------------------------------------------
    def dispatch(self, request: HttpRequest, announcement_id: Optional[int] = None) -> JsonResponse:
        """HTTP metoduna göre ilgili CRUD metodunu çalıştırır."""
        if request.method == "GET":
            if announcement_id is not None:
                return self.detail(request, announcement_id)
            return self.list(request)
        elif request.method == "POST":
            return self.create(request)
        elif request.method == "PUT":
            return self.update(request, announcement_id)
        elif request.method == "PATCH":
            return self.partial_update(request, announcement_id)
        elif request.method == "DELETE":
            return self.delete(request, announcement_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST", "PUT", "PATCH", "DELETE"])

    @classmethod
    def as_view(cls, **initkwargs):
        """Django Class-Based View standardında görünüm fonksiyonu üretir."""
        def view(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        return csrf_exempt(view)
