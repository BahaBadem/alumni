"""
core/database/seeders/user_seeder.py - UserProfile Seeder

Bu modül, veritabanına temel/deterministik kullanıcı profillerini ve
istenilen adette dinamik demo kullanıcılarını idempotent olarak tohumlar.
"""

from datetime import date
from typing import Dict, Any, Optional
from django.db import transaction
from core.models import UserProfile
from core.database.base import BaseSeeder
from core.database.factories.user_factory import UserProfileFactory


class UserProfileSeeder(BaseSeeder):
    """
    Kullanıcı Profilleri için Veritabanı Tohumlayıcısı (Seeder).

    Özellikler:
    - İdempotent: Sabit çekirdek kayıtları get_or_create ile ekler, mükerrer üretmez.
    - Dinamik Genişletilebilir: İstenilen adette rastgele kullanıcı üretebilir.
    - Güvenli: İşlemleri transaction.atomic altında icra eder.
    """
    name = "UserProfileSeeder"

    # Her kurulumda bulunması hedeflenen sabit çekirdek profiller
    CORE_USERS = [
        {
            "name": "Ahmet Baha Badem",
            "birth_date": date(2001, 4, 12),
            "city": "İstanbul",
            "school": "İstanbul Teknik Üniversitesi",
        },
        {
            "name": "Elif Demir",
            "birth_date": date(1999, 7, 20),
            "city": "Ankara",
            "school": "Orta Doğu Teknik Üniversitesi",
        },
        {
            "name": "Mehmet Kaya",
            "birth_date": date(1997, 11, 5),
            "city": "İzmir",
            "school": "Boğaziçi Üniversitesi",
        },
        {
            "name": "Zeynep Yıldız",
            "birth_date": date(2000, 3, 15),
            "city": "Eskişehir",
            "school": "Yıldız Teknik Üniversitesi",
        },
        {
            "name": "Can Çelik",
            "birth_date": date(1998, 9, 28),
            "city": "Bursa",
            "school": "Hacettepe Üniversitesi",
        },
    ]

    def __init__(self):
        self.factory = UserProfileFactory()

    def seed(self, count: Optional[int] = 10, **kwargs) -> Dict[str, Any]:
        """
        Kullanıcı profillerini veritabanına tohumlar.

        Args:
            count (int): Çekirdek profillere ek olarak üretilecek rastgele profil sayısı.

        Returns:
            Dict: {'created': int, 'existing': int, 'total': int}
        """
        created_count = 0
        existing_count = 0

        with transaction.atomic():
            # 1. Sabit Çekirdek Kullanıcıları Ekle (Tam İdempotent)
            for user_data in self.CORE_USERS:
                existing = UserProfile.objects.filter(
                    name=user_data["name"],
                    birth_date=user_data["birth_date"],
                ).first()

                if not existing:
                    UserProfile.objects.create(
                        name=user_data["name"],
                        birth_date=user_data["birth_date"],
                        city=user_data["city"],
                        school=user_data["school"],
                    )
                    created_count += 1
                else:
                    existing_count += 1

            # 2. Dinamik Kullanıcıları Üret
            dynamic_count = count if count is not None else 0
            if dynamic_count > 0:
                self.factory.create_batch(dynamic_count)
                created_count += dynamic_count

        total = UserProfile.objects.count()
        return {
            "created": created_count,
            "existing": existing_count,
            "total": total,
        }

    def clear(self) -> int:
        """
        Tüm UserProfile kayıtlarını siler.
        """
        count, _ = UserProfile.objects.all().delete()
        return count
