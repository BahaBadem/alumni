"""
core/database/seeders/announcement_seeder.py - Announcement Seeder

Bu modül, veritabanına kurumsal çekirdek duyuruları ve istenilen adette
dinamik duyuru kayıtlarını idempotent olarak tohumlar.
"""

from typing import Dict, Any, Optional
from django.db import transaction
from core.models import Announcement
from core.database.base import BaseSeeder
from core.database.data_pools import SEED_ANNOUNCEMENT_TEMPLATES
from core.database.factories.announcement_factory import AnnouncementFactory


class AnnouncementSeeder(BaseSeeder):
    """
    Duyurular için Veritabanı Tohumlayıcısı (Seeder).

    Özellikler:
    - İdempotent: Kurumsal şablon duyurularını başlığa göre get_or_create ile ekler.
    - Dinamik: İstenen sayıda ek duyuru üretebilir.
    - Güvenli: Transaction korumalıdır.
    """
    name = "AnnouncementSeeder"

    def __init__(self):
        self.factory = AnnouncementFactory()

    def seed(self, count: Optional[int] = 5, **kwargs) -> Dict[str, Any]:
        """
        Duyuruları veritabanına tohumlar.

        Args:
            count (int): Çekirdek duyurulara ek olarak üretilecek dinamik duyuru adedi.

        Returns:
            Dict: {'created': int, 'existing': int, 'total': int}
        """
        created_count = 0
        existing_count = 0

        with transaction.atomic():
            # 1. Sabit Kurumsal Şablon Duyurularını Ekle (Tam İdempotent)
            for item in SEED_ANNOUNCEMENT_TEMPLATES:
                existing = Announcement.objects.filter(title=item["title"]).first()
                if not existing:
                    Announcement.objects.create(
                        title=item["title"],
                        content=item["content"],
                        author=item.get("author", "Mezunlar Koordinatörlüğü"),
                        category=item.get("category", "Genel"),
                        is_active=True,
                    )
                    created_count += 1
                else:
                    existing_count += 1

            # 2. Dinamik Duyuruları Üret
            dynamic_count = count if count is not None else 0
            if dynamic_count > 0:
                self.factory.create_batch(dynamic_count)
                created_count += dynamic_count

        total = Announcement.objects.count()
        return {
            "created": created_count,
            "existing": existing_count,
            "total": total,
        }

    def clear(self) -> int:
        """
        Tüm Announcement kayıtlarını siler.
        """
        count, _ = Announcement.objects.all().delete()
        return count
