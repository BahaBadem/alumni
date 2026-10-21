"""
core/database/seeders/job_posting_seeder.py - JobPosting Seeder

Bu modül, veritabanına kurumsal çekirdek iş & staj ilanlarını ve istenilen adette
dinamik kariyer fırsatı kayıtlarını idempotent olarak tohumlar.
"""

import random
from datetime import date, timedelta
from typing import Dict, Any, Optional
from django.db import transaction
from core.models import JobPosting, UserProfile
from core.database.base import BaseSeeder
from core.database.data_pools import SEED_JOB_TEMPLATES
from core.database.factories.job_posting_factory import JobPostingFactory


class JobPostingSeeder(BaseSeeder):
    """
    İş & Staj İlanları için Veritabanı Tohumlayıcısı (Seeder).

    Özellikler:
    - İdempotent: Kurumsal şablon ilanlarını (title + company_name) kontrolüyle ekler, tekrar çalıştırıldığında mükerrer kayıt üretmez.
    - Dinamik: İstenen sayıda ek kariyer fırsatı üretebilir.
    - İlişkisel: İlanları sistemdeki mevcut mezun profillerine (`poster`) dengeli şekilde bağlar.
    - Güvenli: Transaction korumalıdır.
    """
    name = "JobPostingSeeder"

    def __init__(self):
        self.factory = JobPostingFactory()

    def seed(self, count: Optional[int] = 10, **kwargs) -> Dict[str, Any]:
        """
        İş ve staj ilanlarını veritabanına tohumlar.

        Args:
            count (int): Çekirdek ilanlara ek olarak üretilecek dinamik ilan adedi.

        Returns:
            Dict: {'created': int, 'existing': int, 'total': int}
        """
        created_count = 0
        existing_count = 0

        # İlanları bağlamak için mevcut mezun kimliklerini al
        user_ids = list(UserProfile.objects.values_list('id', flat=True)[:50])

        with transaction.atomic():
            # 1. Sabit Kurumsal Şablon İlanlarını Ekle (Tam İdempotent)
            for item in SEED_JOB_TEMPLATES:
                existing = JobPosting.objects.filter(
                    title=item["title"],
                    company_name=item["company_name"]
                ).first()

                if not existing:
                    # Rastgele bir mezunu ilan sahibi yap (varsa)
                    poster = None
                    if user_ids:
                        poster = UserProfile.objects.filter(id=random.choice(user_ids)).first()

                    deadline = date.today() + timedelta(days=item.get("deadline_days", 30))

                    JobPosting.objects.create(
                        poster=poster,
                        title=item["title"],
                        company_name=item["company_name"],
                        description=item["description"],
                        employment_type=item["employment_type"],
                        location=item["location"],
                        salary_range=item.get("salary_range"),
                        contact_email=item["contact_email"],
                        application_url=item.get("application_url"),
                        deadline=deadline,
                        is_active=item.get("is_active", True),
                    )
                    created_count += 1
                else:
                    existing_count += 1

            # 2. Dinamik İlanları Üret
            dynamic_count = count if count is not None else 0
            if dynamic_count > 0:
                self.factory.create_batch(dynamic_count)
                created_count += dynamic_count

        total = JobPosting.objects.count()
        return {
            "created": created_count,
            "existing": existing_count,
            "total": total,
        }

    def clear(self) -> int:
        """
        Tüm JobPosting kayıtlarını siler.
        """
        count, _ = JobPosting.objects.all().delete()
        return count
