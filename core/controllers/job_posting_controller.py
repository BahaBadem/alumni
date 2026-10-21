"""
core/controllers/job_posting_controller.py - Web HTML İş & Staj İlanı Controller'ı (MVC)

Bu modül, web tarayıcısından gelen HTTP isteklerini karşılayan,
templates/job_postings.html görsel yönetim şablonunu render eden ve
iş ilanları üzerinde doğrudan (Direct) ve kullanıcıya bağlı (Nested) CRUD
operasyonlarını icra eden JobPostingController sınıfını içerir.
"""

from typing import Optional
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from core.models import UserProfile, JobPosting
from core.services import job_posting_service
from core.services.job_posting_service import (
    JobPostingValidationError,
    JobPostingNotFoundError
)


class JobPostingController:
    """
    Web Arayüzü İş & Staj İlanı Controller'ı (MVC - Controller Katmanı).
    Doğrudan (/jobs/) ve Mezuna Özel (/users/<user_id>/jobs/) sayfaları render eder.
    """

    def __init__(self):
        self.service = job_posting_service

    # --------------------------------------------------------------------------
    # 1. LIST / SEARCH (Direct & Nested)
    # --------------------------------------------------------------------------
    def list(
        self,
        request: HttpRequest,
        user_id: Optional[int] = None,
        error: Optional[str] = None,
        success: Optional[str] = None
    ) -> HttpResponse:
        """İlanları listeler ve arayüzü render eder."""
        target_user = None
        if user_id is not None:
            try:
                target_user = UserProfile.objects.get(id=user_id)
                jobs = self.service.get_job_postings_by_user(user_id=user_id)
            except UserProfile.DoesNotExist:
                return render(request, "job_postings.html", {
                    "jobs": [],
                    "users": UserProfile.objects.all(),
                    "target_user": None,
                    "error": f"{user_id} ID'li mezun / kullanıcı bulunamadı.",
                    "is_nested": True
                }, status=404)
        else:
            q = request.GET.get("q", "").strip()
            emp_type = request.GET.get("employment_type", "").strip()
            location = request.GET.get("location", "").strip()
            active_param = request.GET.get("is_active")
            is_active = active_param.lower() in ("1", "true", "yes") if active_param else None

            if any([q, emp_type, location, is_active is not None]):
                jobs = self.service.filter_job_postings(
                    keyword=q or None,
                    employment_type=emp_type or None,
                    location=location or None,
                    is_active=is_active
                )
            else:
                jobs = self.service.get_all_job_postings()

        all_users = UserProfile.objects.all()

        return render(request, "job_postings.html", {
            "jobs": jobs,
            "users": all_users,
            "target_user": target_user,
            "is_nested": user_id is not None,
            "employment_types": JobPosting.EMPLOYMENT_TYPES,
            "error": error,
            "success": success,
        })

    # --------------------------------------------------------------------------
    # 2. DETAIL (Direct & Nested)
    # --------------------------------------------------------------------------
    def detail(
        self,
        request: HttpRequest,
        job_id: int,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """Tekil ilan detayını gösterir."""
        try:
            job = self.service.get_job_posting_by_id(job_id)
            if user_id is not None and job.poster_id != user_id:
                return self.list(
                    request,
                    user_id=user_id,
                    error=f"{job_id} ID'li ilan {user_id} ID'li kullanıcıya ait değil."
                )

            return render(request, "job_postings.html", {
                "selected_job": job,
                "jobs": self.service.get_all_job_postings(),
                "users": UserProfile.objects.all(),
                "is_nested": user_id is not None,
                "employment_types": JobPosting.EMPLOYMENT_TYPES,
            })
        except JobPostingNotFoundError:
            return self.list(request, user_id=user_id, error=f"{job_id} ID'li ilan bulunamadı.")

    # --------------------------------------------------------------------------
    # 3. CREATE (Direct & Nested)
    # --------------------------------------------------------------------------
    def create(
        self,
        request: HttpRequest,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """Form üzerinden yeni ilan ekler."""
        p = request.POST
        title = p.get("title") or p.get("baslik", "")
        company_name = p.get("company_name") or p.get("sirket", "")
        description = p.get("description") or p.get("aciklama", "")
        employment_type = p.get("employment_type") or p.get("is_tipi", "FULL_TIME")
        location = p.get("location") or p.get("konum", "İstanbul / Hibrit")
        salary_range = p.get("salary_range") or p.get("maas_araligi") or None
        contact_email = p.get("contact_email") or p.get("iletisim_eposta", "")
        application_url = p.get("application_url") or p.get("basvuru_linki") or None
        deadline = p.get("deadline") or p.get("son_basvuru_tarihi") or None
        is_active = p.get("is_active") in ("1", "true", "on", "yes", True)

        poster_id = user_id if user_id is not None else p.get("poster_id") or p.get("ilan_sahibi_id") or None

        try:
            self.service.create_job_posting(
                title=title,
                company_name=company_name,
                description=description,
                employment_type=employment_type,
                location=location,
                salary_range=salary_range,
                contact_email=contact_email,
                application_url=application_url,
                is_active=is_active,
                deadline=deadline,
                poster_id=poster_id
            )
            return self.list(request, user_id=user_id, success="İş ilanı başarıyla yayınlandı!")
        except (JobPostingValidationError, Exception) as exc:
            return self.list(request, user_id=user_id, error=str(exc))

    # --------------------------------------------------------------------------
    # 4. DELETE (Direct & Nested)
    # --------------------------------------------------------------------------
    def delete(
        self,
        request: HttpRequest,
        job_id: int,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """İlanı siler."""
        try:
            job = self.service.get_job_posting_by_id(job_id)
            if user_id is not None and job.poster_id != user_id:
                return self.list(request, user_id=user_id, error=f"{job_id} ID'li ilan bu kullanıcıya ait değil.")

            self.service.delete_job_posting(job_id)
            return self.list(request, user_id=user_id, success=f"{job_id} ID'li iş ilanı silindi.")
        except JobPostingNotFoundError:
            return self.list(request, user_id=user_id, error=f"{job_id} ID'li ilan bulunamadı.")

    # --------------------------------------------------------------------------
    # ENTRY POINT / DISPATCHER
    # --------------------------------------------------------------------------
    def dispatch(
        self,
        request: HttpRequest,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """HTTP fiili ve aksiyona göre yönlendirir."""
        if request.method == "POST":
            action = request.POST.get("_method") or request.POST.get("action")
            if action == "DELETE" and job_id:
                return self.delete(request, job_id, user_id=user_id)
            return self.create(request, user_id=user_id)
        elif request.method == "GET":
            if job_id is not None:
                return self.detail(request, job_id, user_id=user_id)
            return self.list(request, user_id=user_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST"])

    @classmethod
    def as_view(cls, **initkwargs):
        """Django Class-Based View standardında görünüm fonksiyonu üretir."""
        def view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        return csrf_exempt(view)
