"""
core/services/announcement_service.py - Veritabanı Destekli Duyuru Servis Katmanı

Bu modül, Alumni Portal projesindeki Duyuru (Announcement) operasyonları için
iş mantığını (Business Logic), veri doğrulamasını (Validation) ve
Django ORM veritabanı erişimini (Data Access) yönetir.
"""

from typing import List, Optional, Dict, Any
from django.db import transaction
from django.db.models import Q
from core.models import Announcement
from announcement_model import AnnouncementValidationError, AnnouncementNotFoundError


def validate_announcement_data(
    title: Optional[str] = None,
    content: Optional[str] = None,
    author: Optional[str] = None,
    is_partial: bool = False
) -> None:
    """Duyuru alanlarının geçerliliğini denetler."""
    if not is_partial:
        if not title or not str(title).strip():
            raise AnnouncementValidationError("Duyuru başlığı ('title') boş bırakılamaz.")
        if not content or not str(content).strip():
            raise AnnouncementValidationError("Duyuru içeriği ('content') boş bırakılamaz.")
        if not author or not str(author).strip():
            raise AnnouncementValidationError("Yayınlayan birim / yazar ('author') boş bırakılamaz.")

    if title is not None and len(str(title).strip()) < 3:
        raise AnnouncementValidationError("Duyuru başlığı en az 3 karakter olmalıdır.")

    if content is not None and len(str(content).strip()) < 5:
        raise AnnouncementValidationError("Duyuru içeriği en az 5 karakter olmalıdır.")


def create_announcement(
    title: str,
    content: str,
    author: str = "Mezunlar Koordinatörlüğü",
    category: str = "Genel",
    is_active: bool = True,
    **extra_fields
) -> Announcement:
    """
    Veritabanına yeni bir duyuru kaydeder (CREATE).
    """
    final_title = str(title or extra_fields.get("baslik", "")).strip()
    final_content = str(content or extra_fields.get("icerik", "")).strip()
    final_author = str(author or extra_fields.get("yazar", "Mezunlar Koordinatörlüğü")).strip()
    final_category = str(category or extra_fields.get("kategori", "Genel")).strip()

    is_active_val = is_active if is_active is not None else extra_fields.get("aktif_mi", True)
    if isinstance(is_active_val, str):
        final_is_active = is_active_val.lower() in ("true", "1", "yes", "on", "evet")
    else:
        final_is_active = bool(is_active_val)

    validate_announcement_data(final_title, final_content, final_author, is_partial=False)

    with transaction.atomic():
        announcement = Announcement.objects.create(
            title=final_title,
            content=final_content,
            author=final_author,
            category=final_category,
            is_active=final_is_active,
        )

    return announcement


def get_all_announcements(only_active: bool = False) -> List[Announcement]:
    """
    Veritabanındaki tüm duyuruları en yeniden eskiye sıralı olarak döner (READ ALL).
    """
    qs = Announcement.objects.all().order_by("-created_at")
    if only_active:
        qs = qs.filter(is_active=True)
    return list(qs)


def get_announcement_by_id(announcement_id: int) -> Announcement:
    """
    ID'si verilen duyuruyu veritabanından getirir. Bulunamazsa AnnouncementNotFoundError fırlatır.
    """
    try:
        return Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        raise AnnouncementNotFoundError(f"{announcement_id} ID'li duyuru veritabanında bulunamadı.")


def get_announcement(announcement_id: int) -> Optional[Announcement]:
    """
    ID'si verilen duyuruyu getirir; yoksa None döner (Güvenli Read).
    """
    try:
        return Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        return None


def update_announcement(
    announcement_id: int,
    title: str,
    content: str,
    author: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    **extra_fields
) -> Announcement:
    """
    Duyurunun tüm alanlarını tam olarak günceller (UPDATE - PUT).
    """
    announcement = get_announcement_by_id(announcement_id)

    final_title = str(title or extra_fields.get("baslik", "")).strip()
    final_content = str(content or extra_fields.get("icerik", "")).strip()
    final_author = str(author or extra_fields.get("yazar") or announcement.author).strip()
    final_category = str(category or extra_fields.get("kategori") or announcement.category).strip()

    is_active_val = is_active if is_active is not None else extra_fields.get("aktif_mi")
    if is_active_val is not None:
        if isinstance(is_active_val, str):
            final_is_active = is_active_val.lower() in ("true", "1", "yes", "on", "evet")
        else:
            final_is_active = bool(is_active_val)
    else:
        final_is_active = announcement.is_active

    validate_announcement_data(final_title, final_content, final_author, is_partial=False)

    announcement.title = final_title
    announcement.content = final_content
    announcement.author = final_author
    announcement.category = final_category
    announcement.is_active = final_is_active
    announcement.save()

    return announcement


def patch_announcement(
    announcement_id: int,
    **fields
) -> Announcement:
    """
    Duyurunun yalnızca iletilen alanlarını kısmi olarak günceller (UPDATE - PATCH).
    """
    announcement = get_announcement_by_id(announcement_id)

    # Alias dönüşümleri
    title = fields.get("title") or fields.get("baslik")
    content = fields.get("content") or fields.get("icerik")
    author = fields.get("author") or fields.get("yazar")
    category = fields.get("category") or fields.get("kategori")
    is_active_val = fields.get("is_active") if "is_active" in fields else fields.get("aktif_mi")

    validate_announcement_data(title, content, author, is_partial=True)

    if title is not None:
        announcement.title = str(title).strip()
    if content is not None:
        announcement.content = str(content).strip()
    if author is not None:
        announcement.author = str(author).strip()
    if category is not None:
        announcement.category = str(category).strip()
    if is_active_val is not None:
        if isinstance(is_active_val, str):
            announcement.is_active = is_active_val.lower() in ("true", "1", "yes", "on", "evet")
        else:
            announcement.is_active = bool(is_active_val)

    announcement.save()
    return announcement


def delete_announcement(announcement_id: int) -> Announcement:
    """
    ID'si verilen duyuruyu veritabanından siler (DELETE).
    """
    announcement = get_announcement_by_id(announcement_id)
    announcement.delete()
    return announcement


def delete_all_announcements() -> int:
    """
    Veritabanındaki tüm duyuruları temizler.
    """
    count, _ = Announcement.objects.all().delete()
    return count


def filter_announcements(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    only_active: bool = False
) -> List[Announcement]:
    """
    Başlık, içerik veya kategoriye göre filtreli arama yapar.
    """
    qs = Announcement.objects.all().order_by("-created_at")

    if only_active:
        qs = qs.filter(is_active=True)

    if category and category.strip() and category.strip() != "Tümü":
        qs = qs.filter(category__iexact=category.strip())

    if keyword and keyword.strip():
        k = keyword.strip()
        qs = qs.filter(Q(title__icontains=k) | Q(content__icontains=k) | Q(author__icontains=k))

    return list(qs)


def count_announcements(only_active: bool = False) -> int:
    """
    Veritabanındaki duyuru sayısını döner.
    """
    qs = Announcement.objects.all()
    if only_active:
        qs = qs.filter(is_active=True)
    return qs.count()
