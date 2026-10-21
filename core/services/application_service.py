"""
core/services/application_service.py - Veritabanı Destekli İş & Staj Başvurusu Servis Katmanı

Bu modül, Alumni Portal projesindeki İş/Staj Başvurusu (Application) operasyonları için
iş mantığını (Business Logic), veri doğrulamasını (Validation) ve
Django ORM veritabanı erişimini (Data Access) yönetir.
Hem doğrudan (Direct) hem de ilana/kullanıcıya bağlı (Nested) sorgulamaları destekler.
"""

from typing import List, Optional, Dict, Any, Union
from django.db import transaction, IntegrityError
from django.db.models import Q
from core.models import Application, JobPosting, UserProfile


class ApplicationValidationError(Exception):
    """Başvuru veri doğrulama veya iş kuralı hatası."""
    pass


class ApplicationNotFoundError(Exception):
    """Başvuru kaydı bulunamadığında fırlatılan istisna."""
    pass


class ApplicationDuplicateError(ApplicationValidationError):
    """Aynı ilana mükerrer başvuru yapıldığında fırlatılan istisna."""
    pass


def validate_application_data(
    job_id: Optional[int] = None,
    applicant_id: Optional[int] = None,
    status: Optional[str] = None,
    resume_url: Optional[str] = None,
    cover_letter: Optional[str] = None,
    is_partial: bool = False
) -> None:
    """Başvuru alanlarının geçerliliğini ve iş kurallarını denetler."""
    valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]

    if not is_partial:
        if not job_id:
            raise ApplicationValidationError("Başvurulacak iş ilanı ('job_id') belirtilmelidir.")
        if not applicant_id:
            raise ApplicationValidationError("Başvuru yapan mezun ('applicant_id') belirtilmelidir.")

    if job_id is not None:
        try:
            job = JobPosting.objects.get(id=int(job_id))
            if not is_partial and not job.is_active:
                raise ApplicationValidationError("Bu ilan yayında değil veya başvuruya kapatılmıştır.")
            if not is_partial and job.is_expired:
                raise ApplicationValidationError("Bu ilanın son başvuru tarihi geçmiştir.")
        except (JobPosting.DoesNotExist, ValueError):
            raise ApplicationValidationError(f"{job_id} ID'li iş ilanı bulunamadı.")

    if applicant_id is not None:
        try:
            UserProfile.objects.get(id=int(applicant_id))
        except (UserProfile.DoesNotExist, ValueError):
            raise ApplicationValidationError(f"{applicant_id} ID'li mezun / kullanıcı bulunamadı.")

    if status is not None and status != "":
        clean_status = str(status).strip().upper()
        if clean_status not in valid_statuses:
            raise ApplicationValidationError(
                f"Geçersiz başvuru durumu: '{status}'. Geçerli durumlar: {', '.join(valid_statuses)}"
            )

    if resume_url is not None and str(resume_url).strip():
        url_clean = str(resume_url).strip()
        if not (url_clean.startswith("http://") or url_clean.startswith("https://")):
            raise ApplicationValidationError("Özgeçmiş / CV bağlantısı 'http://' veya 'https://' ile başlamalıdır.")

    if cover_letter is not None and len(str(cover_letter).strip()) > 3000:
        raise ApplicationValidationError("Ön yazı en fazla 3000 karakter olabilir.")


def create_application(
    job_id: int,
    applicant_id: int,
    cover_letter: str = "",
    resume_url: Optional[str] = None,
    status: str = "PENDING",
    **extra_fields
) -> Application:
    """
    Yeni bir iş/staj başvurusu kaydeder (CREATE).
    Mükerrer başvuru kontrolü yapar.
    """
    final_job_id = int(job_id or extra_fields.get("ilan_id") or extra_fields.get("is_ilani_id"))
    final_applicant_id = int(applicant_id or extra_fields.get("basvuran_id") or extra_fields.get("kullanici_id") or extra_fields.get("mezun_id"))
    final_cover = str(cover_letter or extra_fields.get("on_yazi", "") or extra_fields.get("motivasyon_mektubu", "")).strip()
    final_resume = resume_url or extra_fields.get("cv_linki") or extra_fields.get("ozgecmis_linki") or None
    final_status = str(status or extra_fields.get("durum", "PENDING")).strip().upper()

    # Mükerrer başvuru kontrolü
    if Application.objects.filter(job_id=final_job_id, applicant_id=final_applicant_id).exists():
        raise ApplicationDuplicateError(
            f"{final_applicant_id} ID'li mezun {final_job_id} ID'li ilana zaten başvuruda bulunmuştur."
        )

    validate_application_data(
        job_id=final_job_id,
        applicant_id=final_applicant_id,
        status=final_status,
        resume_url=final_resume,
        cover_letter=final_cover,
        is_partial=False
    )

    try:
        application = Application.objects.create(
            job_id=final_job_id,
            applicant_id=final_applicant_id,
            cover_letter=final_cover,
            resume_url=final_resume,
            status=final_status
        )
        return application
    except IntegrityError as exc:
        raise ApplicationDuplicateError("Aynı ilana mükerrer başvuru yapılamaz.") from exc


def get_all_applications(status: Optional[str] = None, limit: Optional[int] = None) -> List[Application]:
    """Tüm başvuruları döner."""
    qs = Application.objects.select_related("job", "applicant").all()
    if status:
        qs = qs.filter(status=status.strip().upper())
    if limit and limit > 0:
        qs = qs[:limit]
    return list(qs)


def get_application_by_id(application_id: int) -> Application:
    """Tekil bir başvuruyu getirir."""
    try:
        return Application.objects.select_related("job", "applicant").get(id=application_id)
    except Application.DoesNotExist:
        raise ApplicationNotFoundError(f"{application_id} ID'li başvuru bulunamadı.")


def get_applications_by_job(job_id: int, status: Optional[str] = None) -> List[Application]:
    """Belirli bir ilana yapılmış tüm başvuruları döner (Nested Query)."""
    if not JobPosting.objects.filter(id=job_id).exists():
        raise JobPosting.DoesNotExist(f"{job_id} ID'li iş ilanı bulunamadı.")

    qs = Application.objects.select_related("job", "applicant").filter(job_id=job_id)
    if status:
        qs = qs.filter(status=status.strip().upper())
    return list(qs)


def get_applications_by_user(user_id: int, status: Optional[str] = None) -> List[Application]:
    """Belirli bir mezunun/öğrencinin yaptığı tüm başvuruları döner (Nested Query)."""
    if not UserProfile.objects.filter(id=user_id).exists():
        raise UserProfile.DoesNotExist(f"{user_id} ID'li kullanıcı bulunamadı.")

    qs = Application.objects.select_related("job", "applicant").filter(applicant_id=user_id)
    if status:
        qs = qs.filter(status=status.strip().upper())
    return list(qs)


def update_application_status(application_id: int, status: str) -> Application:
    """Bir başvurunun statüsünü günceller (PENDING, IN_REVIEW, ACCEPTED, REJECTED, WITHDRAWN)."""
    app = get_application_by_id(application_id)
    clean_status = str(status).strip().upper()
    valid_statuses = [c[0] for c in Application.STATUS_CHOICES]
    if clean_status not in valid_statuses:
        raise ApplicationValidationError(
            f"Geçersiz durum: '{status}'. Geçerli durumlar: {', '.join(valid_statuses)}"
        )
    app.status = clean_status
    app.save()
    return app


def update_application(
    application_id: int,
    status: str,
    cover_letter: str = "",
    resume_url: Optional[str] = None,
    **extra_fields
) -> Application:
    """Bir başvuruyu tam olarak günceller (PUT)."""
    app = get_application_by_id(application_id)
    final_status = str(status or extra_fields.get("durum", app.status)).strip().upper()
    final_cover = str(cover_letter or extra_fields.get("on_yazi", "") or extra_fields.get("motivasyon_mektubu", "")).strip()
    final_resume = resume_url or extra_fields.get("cv_linki") or extra_fields.get("ozgecmis_linki") or None

    validate_application_data(
        job_id=app.job_id,
        applicant_id=app.applicant_id,
        status=final_status,
        resume_url=final_resume,
        cover_letter=final_cover,
        is_partial=False
    )

    app.status = final_status
    app.cover_letter = final_cover
    app.resume_url = final_resume
    app.save()
    return app


def patch_application(application_id: int, **fields_to_update) -> Application:
    """Bir başvurunun belirli alanlarını kısmi günceller (PATCH)."""
    app = get_application_by_id(application_id)

    aliases = {
        "durum": "status",
        "basvuru_durumu": "status",
        "on_yazi": "cover_letter",
        "motivasyon_mektubu": "cover_letter",
        "cv_linki": "resume_url",
        "ozgecmis_linki": "resume_url",
    }
    normalized = {}
    for k, v in fields_to_update.items():
        key = aliases.get(k, k)
        normalized[key] = v

    if "status" in normalized and normalized["status"]:
        normalized["status"] = str(normalized["status"]).strip().upper()

    validate_application_data(
        job_id=app.job_id,
        applicant_id=app.applicant_id,
        status=normalized.get("status"),
        resume_url=normalized.get("resume_url"),
        cover_letter=normalized.get("cover_letter"),
        is_partial=True
    )

    for field, val in normalized.items():
        if hasattr(app, field) and field not in ("id", "job_id", "applicant_id"):
            setattr(app, field, val)

    app.save()
    return app


def delete_application(application_id: int) -> bool:
    """Bir başvuruyu siler (DELETE)."""
    app = get_application_by_id(application_id)
    app.delete()
    return True


def withdraw_application(application_id: int) -> Application:
    """Başvuruyu geri çeker (WITHDRAWN)."""
    return update_application_status(application_id, "WITHDRAWN")


def filter_applications(
    job_id: Optional[int] = None,
    applicant_id: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[Application]:
    """Kriterlere göre başvuruları filtreler."""
    qs = Application.objects.select_related("job", "applicant").all()

    if job_id is not None:
        qs = qs.filter(job_id=job_id)

    if applicant_id is not None:
        qs = qs.filter(applicant_id=applicant_id)

    if status:
        qs = qs.filter(status=status.strip().upper())

    if keyword:
        k = keyword.strip()
        qs = qs.filter(
            Q(cover_letter__icontains=k) |
            Q(job__title__icontains=k) |
            Q(applicant__name__icontains=k)
        )

    return list(qs)
