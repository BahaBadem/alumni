"""
core/database/factories/job_posting_factory.py - JobPosting Model Factory

Bu modül, testler ve seeder operasyonları için gerçekçi JobPosting (İş & Staj İlanı)
model örnekleri üretmek üzere Factory Pattern uygular.
"""

import random
from typing import Dict, Any, Optional
from core.models import JobPosting, UserProfile
from core.database.base import BaseFactory
from core.database.data_pools import (
    COMPANIES,
    JOB_TITLES,
    SEED_JOB_TEMPLATES,
    get_random_company,
    get_random_job_title,
    get_random_employment_type,
    get_random_salary_range,
    get_random_location,
    get_random_future_deadline,
)


def _slugify(text: str) -> str:
    """Şirket ve pozisyon adlarından e-posta ve URL uyumlu slug üretir."""
    tr_map = str.maketrans("çğışöüÇĞİŞÖÜ ", "cgisouCGISOU-")
    clean = text.translate(tr_map).lower()
    return "".join(c for c in clean if c.isalnum() or c == "-").strip("-")


class JobPostingFactory(BaseFactory[JobPosting]):
    """
    JobPosting ORM modeli için nesne üreteci (Factory).

    Kullanım:
        factory = JobPostingFactory()
        job_in_memory = factory.build()
        job_in_db = factory.create(employment_type="INTERNSHIP")
        batch_jobs = factory.create_batch(5)
    """
    model_class = JobPosting

    def definition(self) -> Dict[str, Any]:
        """Varsayılan gerçekçi iş & staj ilanı alan tanımları."""
        # %60 olasılıkla detaylı kurumsal şablonlardan, %40 olasılıkla dinamik kombinasyondan üret
        use_template = random.random() < 0.60
        
        if use_template:
            tpl = random.choice(SEED_JOB_TEMPLATES)
            title = tpl["title"]
            company_name = tpl["company_name"]
            description = tpl["description"]
            employment_type = tpl["employment_type"]
            location = tpl["location"]
            salary_range = tpl["salary_range"]
            contact_email = tpl["contact_email"]
            application_url = tpl["application_url"]
            deadline = get_random_future_deadline(min_days=15, max_days=tpl.get("deadline_days", 45))
        else:
            company_name = get_random_company()
            title = get_random_job_title()
            comp_slug = _slugify(company_name)
            title_slug = _slugify(title)
            
            employment_type = get_random_employment_type()
            location = get_random_location()
            salary_range = get_random_salary_range()
            contact_email = f"kariyer@{comp_slug}.com.tr"
            application_url = f"https://{comp_slug}.com/kariyer/{title_slug}"
            deadline = get_random_future_deadline(min_days=10, max_days=60)
            description = (
                f"{company_name} bünyesinde görevlendirilmek üzere {title} arayışımız bulunmaktadır. "
                f"Adayların modern teknolojilere yatkın, takım çalışmasına açık ve problem çözme "
                f"yeteneği yüksek olması beklenmektedir. İlgilenen mezunlarımızın başvurularını bekleriz."
            )

        # Mevcut bir mezun/kullanıcıyı poster olarak ata (varsa)
        poster: Optional[UserProfile] = None
        user_ids = list(UserProfile.objects.values_list('id', flat=True)[:50])
        if user_ids:
            poster = UserProfile.objects.filter(id=random.choice(user_ids)).first()

        return {
            "poster": poster,
            "title": title,
            "company_name": company_name,
            "description": description,
            "employment_type": employment_type,
            "location": location,
            "salary_range": salary_range,
            "contact_email": contact_email,
            "application_url": application_url,
            "is_active": True,
            "deadline": deadline,
        }
