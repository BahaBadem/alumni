"""
core/database/seeders/database_seeder.py - Ana Veritabanı Tohumlayıcı (Master Seeder)

Bu modül, tüm modül seeder'larını (User, Announcement vb.) tek bir çatı
altında toplayan, transaction güvenliğini sağlayan ve çalıştırma raporu
üreten orkestratör (Master Seeder) sınıfını içerir.
"""

from typing import Dict, Any, Optional
from django.db import transaction
from core.database.base import BaseSeeder
from core.database.seeders.user_seeder import UserProfileSeeder
from core.database.seeders.announcement_seeder import AnnouncementSeeder


class DatabaseSeeder(BaseSeeder):
    """
    Tüm modeller için merkezi tohumlayıcı orkestratör.

    Kullanım:
        seeder = DatabaseSeeder()
        report = seeder.seed(users_count=15, announcements_count=8)
        # veya temizleyip yeniden yüklemek için:
        report = seeder.seed_fresh(users_count=10, announcements_count=5)
    """
    name = "DatabaseSeeder"

    def __init__(self):
        self.user_seeder = UserProfileSeeder()
        self.announcement_seeder = AnnouncementSeeder()

    def seed(
        self,
        users_count: int = 10,
        announcements_count: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Tüm seeder'ları sırayla çalıştırır.

        Returns:
            Dict: Detaylı çalıştırma raporu
        """
        with transaction.atomic():
            user_report = self.user_seeder.seed(count=users_count)
            announcement_report = self.announcement_seeder.seed(count=announcements_count)

        return {
            "status": "success",
            "users": user_report,
            "announcements": announcement_report,
        }

    def clear(self) -> int:
        """
        Tüm seed verilerini temizler.
        """
        deleted_count = 0
        with transaction.atomic():
            deleted_count += self.announcement_seeder.clear()
            deleted_count += self.user_seeder.clear()
        return deleted_count

    def seed_fresh(
        self,
        users_count: int = 10,
        announcements_count: int = 5
    ) -> Dict[str, Any]:
        """
        Önce mevcut verileri temizler, ardından baştan temiz tohumlama yapar.
        """
        deleted = self.clear()
        report = self.seed(users_count=users_count, announcements_count=announcements_count)
        report["deleted_before_seed"] = deleted
        return report
