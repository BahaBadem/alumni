"""
announcement_model.py - Veritabanı Bağımsız Announcement Domain Modeli (Alumni Portal)

Bu modül, harici veritabanı (Django ORM, SQLite vb.) bağımlılığı OLMAKSIZIN,
saf Python (dataclass) ile tasarlanmış Duyuru (Announcement) modelini ve
veri doğrulama mantığını içerir.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


class AnnouncementValidationError(Exception):
    """Duyuru veri doğrulaması başarısız olduğunda fırlatılan özel istisna."""
    pass


class AnnouncementNotFoundError(Exception):
    """İstenen duyuru bulunamadığında fırlatılan özel istisna."""
    pass


@dataclass
class Announcement:
    """
    Veritabanından bağımsız saf Python Duyuru Domain Modeli.

    Alanlar:
        id (int): Benzersiz duyuru kimliği
        title (str): Duyuru başlığı
        content (str): Duyuru metni / açıklaması
        author (str): Duyuruyu yayınlayan kişi/birim (Örn: Mezunlar Ofisi, Rektörlük)
        category (str): Kategori (Genel, Kariyer, Etkinlik, Mezun Buluşması vb.)
        is_active (bool): Duyurunun yayında olup olmadığı
        created_at (datetime): Yayınlanma zamanı
    """
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    author: str = "Mezunlar Koordinatörlüğü"
    category: str = "Genel"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self, is_partial: bool = False) -> None:
        """
        Duyuru alanlarının geçerliliğini denetler.
        """
        if not is_partial:
            if not self.title or not str(self.title).strip():
                raise AnnouncementValidationError("Duyuru başlığı ('title') boş bırakılamaz.")
            if not self.content or not str(self.content).strip():
                raise AnnouncementValidationError("Duyuru içeriği ('content') boş bırakılamaz.")
            if not self.author or not str(self.author).strip():
                raise AnnouncementValidationError("Yayınlayan birim / yazar ('author') boş bırakılamaz.")

        if self.title is not None and len(str(self.title).strip()) < 3:
            raise AnnouncementValidationError("Duyuru başlığı en az 3 karakter olmalıdır.")

        if self.content is not None and len(str(self.content).strip()) < 5:
            raise AnnouncementValidationError("Duyuru içeriği en az 5 karakter olmalıdır.")

    def to_dict(self) -> Dict[str, Any]:
        """Modeli JSON serileştirmeye ve API çıktılarına uygun Python sözlüğüne dönüştürür."""
        created_str = self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        return {
            "id": self.id,
            "title": self.title,
            "baslik": self.title,
            "content": self.content,
            "icerik": self.content,
            "author": self.author,
            "yazar": self.author,
            "category": self.category,
            "kategori": self.category,
            "is_active": self.is_active,
            "aktif_mi": self.is_active,
            "created_at": created_str,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], announcement_id: Optional[int] = None) -> "Announcement":
        """Python sözlüğünden (dict) Announcement nesnesi oluşturur."""
        title = str(data.get("title") or data.get("baslik") or "").strip()
        content = str(data.get("content") or data.get("icerik") or "").strip()
        author = str(data.get("author") or data.get("yazar") or "Mezunlar Koordinatörlüğü").strip()
        category = str(data.get("category") or data.get("kategori") or "Genel").strip()
        
        is_active_val = data.get("is_active")
        if is_active_val is None:
            is_active_val = data.get("aktif_mi", True)
        if isinstance(is_active_val, str):
            is_active = is_active_val.lower() in ("true", "1", "yes", "on", "evet")
        else:
            is_active = bool(is_active_val)

        target_id = announcement_id or data.get("id") or data.get("announcement_id")

        return cls(
            id=int(target_id) if target_id is not None else None,
            title=title,
            content=content,
            author=author,
            category=category,
            is_active=is_active,
        )

    def __repr__(self) -> str:
        return f"<Announcement id={self.id} title='{self.title[:30]}' category='{self.category}'>"
