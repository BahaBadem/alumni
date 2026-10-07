"""
announcement.py - Veritabanı Bağımsız In-Memory CRUD Servis Katmanı (Alumni Portal)

Bu modül, harici veritabanı (Database) bağlantısı OLMAKSIZIN, bellek içi
(In-Memory) veri yapısı üzerinde duyurular için tam teşekküllü CRUD
(Create, Read, Update, Delete) operasyonlarını gerçekleştirir.
"""

from datetime import datetime
from threading import Lock
from typing import List, Optional, Dict, Any

from announcement_model import (
    Announcement,
    AnnouncementValidationError,
    AnnouncementNotFoundError,
)


# ==============================================================================
# BELLEK İÇİ VERİ DEPOSU (IN-MEMORY DATA STORE) & THREAD GÜVENLİĞİ
# ==============================================================================
_STORAGE_LOCK = Lock()
_ANNOUNCEMENTS_DB: Dict[int, Announcement] = {}
_AUTO_INCREMENT_ID: int = 1


def _generate_next_id() -> int:
    """Benzersiz ve artan bir duyuru ID'si üretir."""
    global _AUTO_INCREMENT_ID
    current_id = _AUTO_INCREMENT_ID
    _AUTO_INCREMENT_ID += 1
    return current_id


# ==============================================================================
# CRUD FONKSİYONLARI (CREATE, READ, UPDATE, DELETE)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. CREATE (YENİ DUYURU OLUŞTURMA)
# ------------------------------------------------------------------------------
def create_announcement(
    title: str,
    content: str,
    author: str = "Mezunlar Koordinatörlüğü",
    category: str = "Genel",
    is_active: bool = True,
    **extra_fields
) -> Announcement:
    """
    Veritabanı bağlantısı olmaksızın belleğe yeni bir duyuru kaydeder.
    """
    final_title = title or extra_fields.get("baslik", "")
    final_content = content or extra_fields.get("icerik", "")
    final_author = author or extra_fields.get("yazar", "Mezunlar Koordinatörlüğü")
    final_category = category or extra_fields.get("kategori", "Genel")
    
    is_active_val = is_active if is_active is not None else extra_fields.get("aktif_mi", True)
    if isinstance(is_active_val, str):
        final_is_active = is_active_val.lower() in ("true", "1", "yes", "on", "evet")
    else:
        final_is_active = bool(is_active_val)

    announcement = Announcement(
        title=str(final_title).strip(),
        content=str(final_content).strip(),
        author=str(final_author).strip(),
        category=str(final_category).strip(),
        is_active=final_is_active,
        created_at=datetime.now(),
    )
    announcement.validate(is_partial=False)

    with _STORAGE_LOCK:
        new_id = _generate_next_id()
        announcement.id = new_id
        _ANNOUNCEMENTS_DB[new_id] = announcement

    return announcement


# ------------------------------------------------------------------------------
# 2. READ (DUYURU OKUMA VE LİSTELEME)
# ------------------------------------------------------------------------------
def get_announcement_by_id(announcement_id: int) -> Announcement:
    """Belirtilen ID'ye sahip duyuruyu döndürür. Yoksa AnnouncementNotFoundError fırlatır."""
    with _STORAGE_LOCK:
        ann = _ANNOUNCEMENTS_DB.get(int(announcement_id))
    if ann is None:
        raise AnnouncementNotFoundError(f"{announcement_id} ID'li duyuru bulunamadı.")
    return ann


def get_announcement(announcement_id: int) -> Optional[Announcement]:
    """Belirtilen ID'ye sahip duyuruyu güvenli döndürür. Yoksa None döner."""
    with _STORAGE_LOCK:
        return _ANNOUNCEMENTS_DB.get(int(announcement_id))


def get_all_announcements(only_active: bool = False) -> List[Announcement]:
    """Bellekte kayıtlı tüm duyuruları en yeni ilk sırada olacak şekilde döndürür."""
    with _STORAGE_LOCK:
        items = list(_ANNOUNCEMENTS_DB.values())
    if only_active:
        items = [a for a in items if a.is_active]
    # En yeni duyurular üstte (ID azalan sırada)
    return sorted(items, key=lambda x: x.id or 0, reverse=True)


def filter_announcements(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    author: Optional[str] = None
) -> List[Announcement]:
    """Duyuruları anahtar kelime, kategori veya yazara göre filtreler."""
    with _STORAGE_LOCK:
        items = list(_ANNOUNCEMENTS_DB.values())

    results = []
    for a in items:
        if keyword:
            kw = keyword.lower()
            if kw not in a.title.lower() and kw not in a.content.lower():
                continue
        if category and category.lower() != "tümü" and category.lower() not in a.category.lower():
            continue
        if author and author.lower() not in a.author.lower():
            continue
        results.append(a)

    return sorted(results, key=lambda x: x.id or 0, reverse=True)


# ------------------------------------------------------------------------------
# 3. UPDATE (DUYURU GÜNCELLEME)
# ------------------------------------------------------------------------------
def update_announcement(
    announcement_id: int,
    title: str,
    content: str,
    author: str,
    category: str = "Genel",
    is_active: bool = True,
    **extra_fields
) -> Announcement:
    """Duyuru bilgilerini tam olarak günceller (PUT Mantığı)."""
    ann = get_announcement_by_id(announcement_id)

    final_title = title or extra_fields.get("baslik", "")
    final_content = content or extra_fields.get("icerik", "")
    final_author = author or extra_fields.get("yazar", "")
    final_category = category or extra_fields.get("kategori", "Genel")

    is_active_val = is_active if is_active is not None else extra_fields.get("aktif_mi", True)
    if isinstance(is_active_val, str):
        final_is_active = is_active_val.lower() in ("true", "1", "yes", "on", "evet")
    else:
        final_is_active = bool(is_active_val)

    updated_candidate = Announcement(
        id=ann.id,
        title=str(final_title).strip(),
        content=str(final_content).strip(),
        author=str(final_author).strip(),
        category=str(final_category).strip(),
        is_active=final_is_active,
        created_at=ann.created_at,
    )
    updated_candidate.validate(is_partial=False)

    with _STORAGE_LOCK:
        _ANNOUNCEMENTS_DB[ann.id] = updated_candidate

    return updated_candidate


def patch_announcement(announcement_id: int, **fields) -> Announcement:
    """Duyuru bilgilerini kısmi olarak günceller (PATCH Mantığı)."""
    ann = get_announcement_by_id(announcement_id)
    has_changes = False

    title_val = fields.get("title") or fields.get("baslik")
    if title_val is not None and str(title_val).strip():
        ann.title = str(title_val).strip()
        has_changes = True

    content_val = fields.get("content") or fields.get("icerik")
    if content_val is not None and str(content_val).strip():
        ann.content = str(content_val).strip()
        has_changes = True

    author_val = fields.get("author") or fields.get("yazar")
    if author_val is not None and str(author_val).strip():
        ann.author = str(author_val).strip()
        has_changes = True

    category_val = fields.get("category") or fields.get("kategori")
    if category_val is not None and str(category_val).strip():
        ann.category = str(category_val).strip()
        has_changes = True

    if "is_active" in fields or "aktif_mi" in fields:
        act_val = fields.get("is_active") if "is_active" in fields else fields.get("aktif_mi")
        if isinstance(act_val, str):
            ann.is_active = act_val.lower() in ("true", "1", "yes", "on", "evet")
        else:
            ann.is_active = bool(act_val)
        has_changes = True

    if not has_changes:
        raise AnnouncementValidationError("Güncellenecek en az bir geçerli alan belirtilmelidir.")

    ann.validate(is_partial=True)

    with _STORAGE_LOCK:
        _ANNOUNCEMENTS_DB[ann.id] = ann

    return ann


# ------------------------------------------------------------------------------
# 4. DELETE (DUYURU SİLME)
# ------------------------------------------------------------------------------
def delete_announcement(announcement_id: int) -> Announcement:
    """Belirtilen ID'ye sahip duyuruyu siler."""
    with _STORAGE_LOCK:
        target_id = int(announcement_id)
        if target_id not in _ANNOUNCEMENTS_DB:
            raise AnnouncementNotFoundError(f"{announcement_id} ID'li duyuru bulunamadı.")
        deleted = _ANNOUNCEMENTS_DB.pop(target_id)
    return deleted


def delete_all_announcements() -> int:
    """Tüm duyuruları temizler."""
    with _STORAGE_LOCK:
        count = len(_ANNOUNCEMENTS_DB)
        _ANNOUNCEMENTS_DB.clear()
    return count


# ------------------------------------------------------------------------------
# 5. YARDIMCI VE TEST YÖNETİM METOTLARI
# ------------------------------------------------------------------------------
def count_announcements() -> int:
    """Kayıtlı toplam duyuru sayısı."""
    with _STORAGE_LOCK:
        return len(_ANNOUNCEMENTS_DB)


def clear_storage() -> None:
    """Belleği ve ID sayacını sıfırlar."""
    global _AUTO_INCREMENT_ID
    with _STORAGE_LOCK:
        _ANNOUNCEMENTS_DB.clear()
        _AUTO_INCREMENT_ID = 1


def seed_demo_announcements() -> List[Announcement]:
    """Başlangıç için örnek duyuruları yükler."""
    clear_storage()
    demos = [
        (
            "2026 Mezunlar Buluşması Tarihi Belli Oldu!",
            "Tüm dönem mezunlarımızın davetli olduğu Geleneksel Mezunlar Günü buluşması 15 Mayıs 2026 tarihinde Merkez Kampüs Amfitiyatro alanında gerçekleştirilecektir.",
            "Mezunlar Koordinatörlüğü",
            "Etkinlik",
            True
        ),
        (
            "Yaz Dönemi Global Şirket Staj Fırsatları",
            "Yurt dışı ve teknoloji odaklı mezunlarımızın şirketlerinde açılan yaz dönemi yazılım, veri analitiği ve ürün yönetimi staj ilanları Kariyer Portalında yayınlandı.",
            "Kariyer Merkezi",
            "Kariyer",
            True
        ),
        (
            "Mezun-Öğrenci Mentorluk Programı Başvuruları Başladı",
            "Sektörde en az 3 yıl deneyimli mezunlarımız ile son sınıf lisans öğrencilerimizi buluşturan 2026-2027 Mentorluk Programı için başvurular açılmıştır.",
            "Rektörlük Mezun İlişkileri",
            "Mentorluk",
            True
        ),
    ]
    created = []
    for title, content, author, cat, active in demos:
        created.append(create_announcement(title=title, content=content, author=author, category=cat, is_active=active))
    return created


# Başlangıçta örnek verileri tohumla (İlk yüklemede boş kalmaması için)
seed_demo_announcements()
