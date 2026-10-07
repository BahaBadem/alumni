"""
core/controllers/announcement_controller.py - Web HTML Duyuru Controller'ı (MVC)

Bu modül, web tarayıcısından gelen HTTP isteklerini karşılayan,
templates/announcements.html görsel yönetim şablonunu render eden ve
duyurular üzerinde tam CRUD operasyonlarını icra eden AnnouncementController
sınıfını içerir.
"""

from typing import Optional
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

import announcement as announcement_service
from announcement_model import AnnouncementValidationError, AnnouncementNotFoundError


class AnnouncementController:
    """
    Web Arayüzü Duyuru Controller'ı (MVC - Controller Katmanı).

    Sorumlulukları:
    - templates/announcements.html şablonuna duyuru listesini aktarmak (Read)
    - Formdan gelen POST isteğiyle yeni duyuru oluşturmak (Create)
    - Duyuru detayını göstermek (Read Single)
    - Duyuru bilgilerini güncellemek (Update)
    - Duyuru kaydını silmek (Delete)
    - Kategori ve anahtar kelimeye göre filtrelemek (Search/Filter)
    """

    # --------------------------------------------------------------------------
    # CRUD: 1. CREATE (YENİ DUYURU OLUŞTURMA)
    # --------------------------------------------------------------------------
    def create(self, request: HttpRequest) -> HttpResponse:
        """HTML formundan yeni duyuru kaydeder (POST)."""
        title = str(request.POST.get("title") or request.POST.get("baslik", "")).strip()
        content = str(request.POST.get("content") or request.POST.get("icerik", "")).strip()
        author = str(request.POST.get("author") or request.POST.get("yazar", "Mezunlar Koordinatörlüğü")).strip()
        category = str(request.POST.get("category") or request.POST.get("kategori", "Genel")).strip()
        is_active_raw = request.POST.get("is_active") or request.POST.get("aktif_mi")
        is_active = is_active_raw in ("1", "true", "on", "yes", True) if is_active_raw is not None else True

        form_data = {
            "title": title,
            "content": content,
            "author": author,
            "category": category,
            "is_active": is_active,
        }

        # Validasyon: Başlık ve İçerik kontrolü
        if not (title and content):
            announcements = announcement_service.get_all_announcements()
            return render(request, "announcements.html", {
                "announcements": announcements,
                "error": "Lütfen Duyuru Başlığı ve İçerik alanlarını eksiksiz doldurunuz.",
                "form_data": form_data,
            }, status=400)

        try:
            new_ann = announcement_service.create_announcement(
                title=title,
                content=content,
                author=author,
                category=category,
                is_active=is_active,
            )
            announcements = announcement_service.get_all_announcements()
            return render(request, "announcements.html", {
                "announcements": announcements,
                "success": f"'{new_ann.title}' başlıklı duyuru başarıyla yayınlandı!",
            }, status=201)
        except AnnouncementValidationError as e:
            announcements = announcement_service.get_all_announcements()
            return render(request, "announcements.html", {
                "announcements": announcements,
                "error": str(e),
                "form_data": form_data,
            }, status=400)

    # --------------------------------------------------------------------------
    # CRUD: 2. READ (LİSTELEME VE FİLTRELEME)
    # --------------------------------------------------------------------------
    def list(self, request: HttpRequest) -> HttpResponse:
        """Duyuruları listeler; filtreleme ve arama parametrelerini uygular."""
        keyword = request.GET.get("q") or request.GET.get("keyword")
        category = request.GET.get("category")
        
        if keyword or (category and category != "Tümü"):
            announcements = announcement_service.filter_announcements(
                keyword=keyword, category=category
            )
        else:
            announcements = announcement_service.get_all_announcements()

        return render(request, "announcements.html", {
            "announcements": announcements,
            "selected_category": category or "Tümü",
            "search_query": keyword or "",
        })

    def detail(self, request: HttpRequest, announcement_id: int) -> HttpResponse:
        """Tekil duyuru detayını görüntüler."""
        ann = announcement_service.get_announcement(announcement_id)
        if not ann:
            announcements = announcement_service.get_all_announcements()
            return render(request, "announcements.html", {
                "announcements": announcements,
                "error": f"{announcement_id} ID'li duyuru bulunamadı.",
            }, status=404)
        return render(request, "announcements.html", {
            "announcement": ann,
            "announcements": [ann],
        })

    # --------------------------------------------------------------------------
    # CRUD: 3. UPDATE (GÜNCELLEME)
    # --------------------------------------------------------------------------
    def update(self, request: HttpRequest, announcement_id: int) -> HttpResponse:
        """Duyuruyu günceller."""
        title = request.POST.get("title") or request.POST.get("baslik")
        content = request.POST.get("content") or request.POST.get("icerik")
        author = request.POST.get("author") or request.POST.get("yazar")
        category = request.POST.get("category") or request.POST.get("kategori")
        is_active_raw = request.POST.get("is_active") or request.POST.get("aktif_mi")

        try:
            kwargs = {}
            if title: kwargs["title"] = str(title).strip()
            if content: kwargs["content"] = str(content).strip()
            if author: kwargs["author"] = str(author).strip()
            if category: kwargs["category"] = str(category).strip()
            if is_active_raw is not None:
                kwargs["is_active"] = is_active_raw in ("1", "true", "on", "yes", True)

            updated = announcement_service.patch_announcement(announcement_id, **kwargs)
            announcements = announcement_service.get_all_announcements()
            return render(request, "announcements.html", {
                "announcements": announcements,
                "success": f"'{updated.title}' duyurusu başarıyla güncellendi.",
            })
        except Exception as e:
            announcements = announcement_service.get_all_announcements()
            return render(request, "announcements.html", {
                "announcements": announcements,
                "error": str(e),
            }, status=400)

    # --------------------------------------------------------------------------
    # CRUD: 4. DELETE (SİLME)
    # --------------------------------------------------------------------------
    def delete(self, request: HttpRequest, announcement_id: int) -> HttpResponse:
        """Duyuruyu siler."""
        try:
            deleted = announcement_service.delete_announcement(announcement_id)
            announcements = announcement_service.get_all_announcements()
            return render(request, "announcements.html", {
                "announcements": announcements,
                "success": f"'{deleted.title}' başlıklı duyuru silindi.",
            })
        except AnnouncementNotFoundError:
            announcements = announcement_service.get_all_announcements()
            return render(request, "announcements.html", {
                "announcements": announcements,
                "error": f"{announcement_id} ID'li duyuru bulunamadı.",
            }, status=404)

    # --------------------------------------------------------------------------
    # CONTROLLER ENTRY POINT / DISPATCHER
    # --------------------------------------------------------------------------
    def dispatch(self, request: HttpRequest, announcement_id: Optional[int] = None) -> HttpResponse:
        """HTTP metoduna ve aksiyon parametresine göre ilgili CRUD metodunu çalıştırır."""
        if request.method == "POST":
            action = request.POST.get("_method") or request.POST.get("action")
            if action == "DELETE" and announcement_id:
                return self.delete(request, announcement_id)
            if action in ("PUT", "PATCH") and announcement_id:
                return self.update(request, announcement_id)
            return self.create(request)
        elif request.method == "GET":
            if announcement_id is not None:
                return self.detail(request, announcement_id)
            return self.list(request)
        else:
            return HttpResponseNotAllowed(["GET", "POST"])

    @classmethod
    def as_view(cls, **initkwargs):
        """Django Class-Based View standardında görünüm fonksiyonu üretir."""
        def view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        return csrf_exempt(view)
