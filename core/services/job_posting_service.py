"""
core/services/job_posting_service.py - Veritabanı Destekli İş & Staj İlanı Servis Katmanı

Bu modül, Alumni Portal projesindeki İş/Staj İlanı (JobPosting) operasyonları için
iş mantığını (Business Logic), veri doğrulamasını (Validation) ve
Django ORM veritabanı erişimini (Data Access) yönetir.
Hem doğrudan (Direct) hem de mezun ilişkili (Nested) sorgulamaları destekler.
"""

import re
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from core.models import JobPosting, UserProfile


class JobPostingValidationError(Exception):
    """İş ilanı veri doğrulama hatası."""
    pass


class JobPostingNotFoundError(Exception):
    """İş ilanı bulunamadığında fırlatılan istisna."""
    pass


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def parse_date_value(value: Any) -> Optional[date]:
    """Tarih değerini date nesnesine ayrıştırır."""
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    val_str = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            continue
    raise JobPostingValidationError(f"Geçersiz tarih formatı: '{val_str}'. Geçerli formatlar: YYYY-MM-DD, DD.MM.YYYY")


def validate_job_posting_data(
    title: Optional[str] = None,
    company_name: Optional[str] = None,
    description: Optional[str] = None,
    employment_type: Optional[str] = None,
    contact_email: Optional[str] = None,
    application_url: Optional[str] = None,
    deadline: Optional[date] = None,
    is_partial: bool = False
) -> None:
    """İş ilanı alanlarının geçerliliğini denetler."""
    valid_emp_types = [choice[0] for choice in JobPosting.EMPLOYMENT_TYPES]

    if not is_partial:
        if not title or not str(title).strip():
            raise JobPostingValidationError("Pozisyon başlığı ('title') boş bırakılamaz.")
        if not company_name or not str(company_name).strip():
            raise JobPostingValidationError("Şirket / Kurum adı ('company_name') boş bırakılamaz.")
        if not description or not str(description).strip():
            raise JobPostingValidationError("İş tanımı ('description') boş bırakılamaz.")
        if not contact_email or not str(contact_email).strip():
            raise JobPostingValidationError("İletişim / Başvuru e-postası ('contact_email') boş bırakılamaz.")

    if title is not None and len(str(title).strip()) < 3:
        raise JobPostingValidationError("Pozisyon başlığı en az 3 karakter olmalıdır.")

    if company_name is not None and len(str(company_name).strip()) < 2:
        raise JobPostingValidationError("Şirket adı en az 2 karakter olmalıdır.")

    if description is not None and len(str(description).strip()) < 10:
        raise JobPostingValidationError("İş tanımı en az 10 karakter olmalıdır.")

    if employment_type is not None and employment_type != "":
        emp_clean = str(employment_type).strip().upper()
        if emp_clean not in valid_emp_types:
            raise JobPostingValidationError(
                f"Geçersiz istihdam türü: '{employment_type}'. Geçerli türler: {', '.join(valid_emp_types)}"
            )

    if contact_email is not None and str(contact_email).strip():
        email_clean = str(contact_email).strip()
        if not EMAIL_REGEX.match(email_clean):
            raise JobPostingValidationError(f"Geçersiz e-posta formatı: '{contact_email}'.")

    if application_url is not None and str(application_url).strip():
        url_clean = str(application_url).strip()
        if not (url_clean.startswith("http://") or url_clean.startswith("https://")):
            raise JobPostingValidationError("Başvuru URL'si 'http://' veya 'https://' ile başlamalıdır.")

    if deadline is not None and not is_partial:
        today = timezone.now().date()
        if deadline < today:
            raise JobPostingValidationError("Son başvuru tarihi bugünden önce olamaz.")


def create_job_posting(
    title: str,
    company_name: str,
    description: str,
    employment_type: str = "FULL_TIME",
    location: str = "İstanbul / Hibrit",
    salary_range: Optional[str] = None,
    contact_email: str = "",
    application_url: Optional[str] = None,
    is_active: bool = True,
    deadline: Optional[Union[str, date]] = None,
    poster_id: Optional[int] = None,
    **extra_fields
) -> JobPosting:
    """
    Veritabanına yeni bir iş/staj ilanı kaydeder (CREATE).
    Türkçe ve İngilizce parametreleri destekler.
    """
    final_title = str(title or extra_fields.get("baslik", "") or extra_fields.get("is_basligi", "")).strip()
    final_company = str(company_name or extra_fields.get("sirket", "") or extra_fields.get("sirket_adi", "")).strip()
    final_description = str(description or extra_fields.get("aciklama", "") or extra_fields.get("is_tanimi", "")).strip()
    final_emp_type = str(employment_type or extra_fields.get("is_tipi", "") or extra_fields.get("calisma_sekli", "FULL_TIME")).strip().upper()
    final_location = str(location or extra_fields.get("konum", "") or extra_fields.get("sehir", "İstanbul / Hibrit")).strip()
    final_salary = salary_range or extra_fields.get("maas_araligi") or extra_fields.get("maas")
    final_email = str(contact_email or extra_fields.get("iletisim_eposta", "") or extra_fields.get("email", "")).strip()
    final_url = application_url or extra_fields.get("basvuru_linki") or extra_fields.get("basvuru_adresi")
    
    raw_active = is_active if "is_active" in locals() else extra_fields.get("aktif_mi", True)
    if isinstance(raw_active, str):
        final_is_active = raw_active.lower() in ("1", "true", "yes", "on")
    else:
        final_is_active = bool(raw_active)

    raw_deadline = deadline if deadline is not None else extra_fields.get("son_basvuru_tarihi")
    parsed_deadline = parse_date_value(raw_deadline) if raw_deadline else None

    target_poster_id = poster_id if poster_id is not None else extra_fields.get("ilan_sahibi_id") or extra_fields.get("kullanici_id")
    poster_instance = None
    if target_poster_id:
        try:
            poster_instance = UserProfile.objects.get(id=int(target_poster_id))
        except (UserProfile.DoesNotExist, ValueError):
            raise JobPostingValidationError(f"İlan sahibi kullanıcı (ID: {target_poster_id}) bulunamadı.")

    validate_job_posting_data(
        title=final_title,
        company_name=final_company,
        description=final_description,
        employment_type=final_emp_type,
        contact_email=final_email,
        application_url=final_url,
        deadline=parsed_deadline,
        is_partial=False
    )

    job = JobPosting.objects.create(
        poster=poster_instance,
        title=final_title,
        company_name=final_company,
        description=final_description,
        employment_type=final_emp_type,
        location=final_location,
        salary_range=final_salary,
        contact_email=final_email,
        application_url=final_url,
        is_active=final_is_active,
        deadline=parsed_deadline
    )
    return job


def get_all_job_postings(active_only: bool = False, limit: Optional[int] = None) -> List[JobPosting]:
    """Tüm iş ilanlarını döner."""
    qs = JobPosting.objects.select_related("poster").all()
    if active_only:
        qs = qs.filter(is_active=True)
    if limit and limit > 0:
        qs = qs[:limit]
    return list(qs)


def get_job_posting_by_id(job_id: int) -> JobPosting:
    """Tekil bir ilanı ID'sine göre getirir."""
    try:
        return JobPosting.objects.select_related("poster").get(id=job_id)
    except JobPosting.DoesNotExist:
        raise JobPostingNotFoundError(f"{job_id} ID'li iş ilanı bulunamadı.")


def get_job_postings_by_user(user_id: int, active_only: bool = False) -> List[JobPosting]:
    """Belirli bir mezuna/kullanıcıya ait iş ilanlarını döner (Nested Query)."""
    if not UserProfile.objects.filter(id=user_id).exists():
        raise UserProfile.DoesNotExist(f"{user_id} ID'li kullanıcı bulunamadı.")
    
    qs = JobPosting.objects.select_related("poster").filter(poster_id=user_id)
    if active_only:
        qs = qs.filter(is_active=True)
    return list(qs)


def update_job_posting(
    job_id: int,
    title: str,
    company_name: str,
    description: str,
    employment_type: str = "FULL_TIME",
    location: str = "İstanbul / Hibrit",
    salary_range: Optional[str] = None,
    contact_email: str = "",
    application_url: Optional[str] = None,
    is_active: bool = True,
    deadline: Optional[Union[str, date]] = None,
    poster_id: Optional[int] = None,
    **extra_fields
) -> JobPosting:
    """Bir ilanı baştan sona günceller (PUT)."""
    job = get_job_posting_by_id(job_id)

    final_title = str(title or extra_fields.get("baslik", "") or extra_fields.get("is_basligi", "")).strip()
    final_company = str(company_name or extra_fields.get("sirket", "") or extra_fields.get("sirket_adi", "")).strip()
    final_description = str(description or extra_fields.get("aciklama", "") or extra_fields.get("is_tanimi", "")).strip()
    final_emp_type = str(employment_type or extra_fields.get("is_tipi", "") or extra_fields.get("calisma_sekli", "FULL_TIME")).strip().upper()
    final_location = str(location or extra_fields.get("konum", "") or extra_fields.get("sehir", "İstanbul / Hibrit")).strip()
    final_salary = salary_range or extra_fields.get("maas_araligi") or extra_fields.get("maas")
    final_email = str(contact_email or extra_fields.get("iletisim_eposta", "") or extra_fields.get("email", "")).strip()
    final_url = application_url or extra_fields.get("basvuru_linki") or extra_fields.get("basvuru_adresi")

    raw_deadline = deadline if deadline is not None else extra_fields.get("son_basvuru_tarihi")
    parsed_deadline = parse_date_value(raw_deadline) if raw_deadline else None

    validate_job_posting_data(
        title=final_title,
        company_name=final_company,
        description=final_description,
        employment_type=final_emp_type,
        contact_email=final_email,
        application_url=final_url,
        deadline=parsed_deadline,
        is_partial=False
    )

    if poster_id is not None:
        if poster_id == 0 or poster_id == "":
            job.poster = None
        else:
            try:
                job.poster = UserProfile.objects.get(id=int(poster_id))
            except (UserProfile.DoesNotExist, ValueError):
                raise JobPostingValidationError(f"İlan sahibi kullanıcı (ID: {poster_id}) bulunamadı.")

    job.title = final_title
    job.company_name = final_company
    job.description = final_description
    job.employment_type = final_emp_type
    job.location = final_location
    job.salary_range = final_salary
    job.contact_email = final_email
    job.application_url = final_url
    job.is_active = is_active
    job.deadline = parsed_deadline
    job.save()
    return job


def patch_job_posting(job_id: int, **fields_to_update) -> JobPosting:
    """Bir ilanın belirli alanlarını kısmi günceller (PATCH)."""
    job = get_job_posting_by_id(job_id)

    # Alias dönüşümleri
    aliases = {
        "baslik": "title",
        "is_basligi": "title",
        "sirket": "company_name",
        "sirket_adi": "company_name",
        "aciklama": "description",
        "is_tanimi": "description",
        "is_tipi": "employment_type",
        "calisma_sekli": "employment_type",
        "konum": "location",
        "sehir": "location",
        "maas_araligi": "salary_range",
        "maas": "salary_range",
        "iletisim_eposta": "contact_email",
        "email": "contact_email",
        "basvuru_linki": "application_url",
        "basvuru_adresi": "application_url",
        "aktif_mi": "is_active",
        "yayinda_mi": "is_active",
        "son_basvuru_tarihi": "deadline",
        "ilan_sahibi_id": "poster_id",
        "kullanici_id": "poster_id",
    }
    normalized = {}
    for k, v in fields_to_update.items():
        key = aliases.get(k, k)
        normalized[key] = v

    if "deadline" in normalized:
        normalized["deadline"] = parse_date_value(normalized["deadline"])

    validate_job_posting_data(
        title=normalized.get("title"),
        company_name=normalized.get("company_name"),
        description=normalized.get("description"),
        employment_type=normalized.get("employment_type"),
        contact_email=normalized.get("contact_email"),
        application_url=normalized.get("application_url"),
        deadline=normalized.get("deadline"),
        is_partial=True
    )

    if "poster_id" in normalized:
        p_id = normalized["poster_id"]
        if p_id in (None, 0, ""):
            job.poster = None
        else:
            try:
                job.poster = UserProfile.objects.get(id=int(p_id))
            except (UserProfile.DoesNotExist, ValueError):
                raise JobPostingValidationError(f"İlan sahibi kullanıcı (ID: {p_id}) bulunamadı.")

    for field, val in normalized.items():
        if field != "poster_id" and hasattr(job, field):
            setattr(job, field, val)

    job.save()
    return job


def delete_job_posting(job_id: int) -> bool:
    """Bir ilanı kalıcı olarak siler (DELETE)."""
    job = get_job_posting_by_id(job_id)
    job.delete()
    return True


def filter_job_postings(
    keyword: Optional[str] = None,
    employment_type: Optional[str] = None,
    location: Optional[str] = None,
    is_active: Optional[bool] = None,
    poster_id: Optional[int] = None,
) -> List[JobPosting]:
    """Kriterlere göre ilanları filtreler."""
    qs = JobPosting.objects.select_related("poster").all()

    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    if poster_id is not None:
        qs = qs.filter(poster_id=poster_id)

    if employment_type:
        qs = qs.filter(employment_type__iexact=employment_type.strip())

    if location:
        qs = qs.filter(location__icontains=location.strip())

    if keyword:
        k = keyword.strip()
        qs = qs.filter(
            Q(title__icontains=k) |
            Q(company_name__icontains=k) |
            Q(description__icontains=k)
        )

    return list(qs)
