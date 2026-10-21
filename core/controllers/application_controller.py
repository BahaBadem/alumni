"""
core/controllers/application_controller.py - Web HTML İş & Staj Başvurusu Controller'ı (MVC)

Bu modül, web tarayıcısından gelen HTTP isteklerini karşılayan,
templates/applications.html görsel yönetim şablonunu render eden ve
başvurular üzerinde hem Doğrudan (Direct) hem de İlişkisel (Nested: Job & User altı)
CRUD operasyonlarını icra eden ApplicationController sınıfını içerir.

Rotalar:
- Doğrudan (Direct):
    GET  /applications/
    POST /applications/create/
    GET  /applications/<id>/
    POST /applications/<id>/delete/
- İlan Altı (Job-Nested):
    GET  /jobs/<job_id>/applications/
    POST /jobs/<job_id>/applications/create/
    GET  /jobs/<job_id>/applications/<id>/
    POST /jobs/<job_id>/applications/<id>/delete/
- Mezun Altı (User-Nested):
    GET  /users/<user_id>/applications/
    POST /users/<user_id>/applications/create/
    GET  /users/<user_id>/applications/<id>/
    POST /users/<user_id>/applications/<id>/delete/
"""

from typing import Optional
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from core.models import UserProfile, JobPosting, Application
from core.services import application_service
from core.services.application_service import (
    ApplicationValidationError,
    ApplicationNotFoundError,
    ApplicationDuplicateError
)


class ApplicationController:
    """
    Web Arayüzü İş Başvurusu Controller'ı (MVC - Controller Katmanı).
    Doğrudan (/applications/), İlan altı (/jobs/<job_id>/applications/) ve
    Mezun altı (/users/<user_id>/applications/) sayfaları render eder.
    """

    def __init__(self):
        self.service = application_service

    # --------------------------------------------------------------------------
    # 1. LIST / SEARCH (Direct, Job-Nested & User-Nested)
    # --------------------------------------------------------------------------
    def list(
        self,
        request: HttpRequest,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None,
        error: Optional[str] = None,
        success: Optional[str] = None
    ) -> HttpResponse:
        """Başvuruları listeler ve görsel arayüzü render eder."""
        target_job = None
        target_user = None

        if job_id is not None:
            try:
                target_job = JobPosting.objects.get(id=job_id)
                status_filter = request.GET.get("status")
                applications = self.service.get_applications_by_job(job_id=job_id, status=status_filter or None)
            except JobPosting.DoesNotExist:
                return render(request, "applications.html", {
                    "applications": [],
                    "jobs": JobPosting.objects.all(),
                    "users": UserProfile.objects.all(),
                    "statuses": Application.STATUS_CHOICES,
                    "target_job": None,
                    "target_user": None,
                    "error": f"{job_id} ID'li iş ilanı bulunamadı.",
                    "is_nested_job": True,
                    "is_nested_user": False
                }, status=404)

        elif user_id is not None:
            try:
                target_user = UserProfile.objects.get(id=user_id)
                status_filter = request.GET.get("status")
                applications = self.service.get_applications_by_user(user_id=user_id, status=status_filter or None)
            except UserProfile.DoesNotExist:
                return render(request, "applications.html", {
                    "applications": [],
                    "jobs": JobPosting.objects.all(),
                    "users": UserProfile.objects.all(),
                    "statuses": Application.STATUS_CHOICES,
                    "target_job": None,
                    "target_user": None,
                    "error": f"{user_id} ID'li kullanıcı / mezun bulunamadı.",
                    "is_nested_job": False,
                    "is_nested_user": True
                }, status=404)

        else:
            # Doğrudan rotada filtreleme parametreleri
            status_param = request.GET.get("status") or request.GET.get("durum")
            applicant_param = request.GET.get("applicant_id") or request.GET.get("basvuran_id")
            job_param = request.GET.get("job_id") or request.GET.get("ilan_id")
            keyword = request.GET.get("q") or request.GET.get("arama")

            if any([status_param, applicant_param, job_param, keyword]):
                applications = self.service.filter_applications(
                    job_id=int(job_param) if job_param else None,
                    applicant_id=int(applicant_param) if applicant_param else None,
                    status=status_param or None,
                    keyword=keyword or None
                )
            else:
                applications = self.service.get_all_applications()

        all_jobs = JobPosting.objects.filter(is_active=True).order_by('-created_at')
        all_users = UserProfile.objects.all().order_by('name')

        return render(request, "applications.html", {
            "applications": applications,
            "jobs": all_jobs,
            "users": all_users,
            "target_job": target_job,
            "target_user": target_user,
            "is_nested_job": job_id is not None,
            "is_nested_user": user_id is not None,
            "statuses": Application.STATUS_CHOICES,
            "error": error,
            "success": success,
        })

    # --------------------------------------------------------------------------
    # 2. DETAIL (Direct & Nested)
    # --------------------------------------------------------------------------
    def detail(
        self,
        request: HttpRequest,
        application_id: int,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """Tekil başvuru detayını gösterir."""
        try:
            app = self.service.get_application_by_id(application_id)
            if job_id is not None and app.job_id != job_id:
                return self.list(
                    request,
                    job_id=job_id,
                    error=f"{application_id} ID'li başvuru {job_id} ID'li ilana ait değil."
                )
            if user_id is not None and app.applicant_id != user_id:
                return self.list(
                    request,
                    user_id=user_id,
                    error=f"{application_id} ID'li başvuru {user_id} ID'li mezuna ait değil."
                )

            return render(request, "applications.html", {
                "selected_application": app,
                "applications": self.service.get_all_applications(),
                "jobs": JobPosting.objects.filter(is_active=True),
                "users": UserProfile.objects.all(),
                "target_job": app.job if job_id is not None else None,
                "target_user": app.applicant if user_id is not None else None,
                "is_nested_job": job_id is not None,
                "is_nested_user": user_id is not None,
                "statuses": Application.STATUS_CHOICES,
            })
        except ApplicationNotFoundError:
            return self.list(
                request,
                job_id=job_id,
                user_id=user_id,
                error=f"{application_id} ID'li başvuru bulunamadı."
            )

    # --------------------------------------------------------------------------
    # 3. CREATE (Direct, Job-Nested & User-Nested)
    # --------------------------------------------------------------------------
    def create(
        self,
        request: HttpRequest,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """Form üzerinden yeni başvuru ekler."""
        p = request.POST
        selected_job_id = job_id if job_id is not None else p.get("job_id") or p.get("ilan_id")
        selected_applicant_id = user_id if user_id is not None else p.get("applicant_id") or p.get("basvuran_id")
        cover_letter = p.get("cover_letter") or p.get("on_yazi", "")
        resume_url = p.get("resume_url") or p.get("cv_linki") or None
        status = p.get("status") or p.get("durum", "PENDING")

        try:
            self.service.create_application(
                job_id=int(selected_job_id) if selected_job_id else 0,
                applicant_id=int(selected_applicant_id) if selected_applicant_id else 0,
                cover_letter=cover_letter,
                resume_url=resume_url,
                status=status
            )
            return self.list(
                request,
                job_id=job_id,
                user_id=user_id,
                success="İş başvurunuz başarıyla kaydedildi!"
            )
        except ApplicationDuplicateError as dup_err:
            return self.list(request, job_id=job_id, user_id=user_id, error=str(dup_err))
        except (ApplicationValidationError, Exception) as exc:
            return self.list(request, job_id=job_id, user_id=user_id, error=str(exc))

    # --------------------------------------------------------------------------
    # 4. UPDATE STATUS / PATCH
    # --------------------------------------------------------------------------
    def update_status(
        self,
        request: HttpRequest,
        application_id: int,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """Başvuru durumunu günceller."""
        new_status = request.POST.get("status") or request.POST.get("durum")
        try:
            app = self.service.get_application_by_id(application_id)
            if job_id is not None and app.job_id != job_id:
                return self.list(request, job_id=job_id, error="Başvuru bu ilana ait değil.")
            if user_id is not None and app.applicant_id != user_id:
                return self.list(request, user_id=user_id, error="Başvuru bu kullanıcıya ait değil.")

            if not new_status:
                return self.list(request, job_id=job_id, user_id=user_id, error="Yeni durum belirtilmedi.")

            self.service.update_application_status(application_id, new_status)
            return self.list(
                request,
                job_id=job_id,
                user_id=user_id,
                success=f"{application_id} ID'li başvuru durumu '{new_status}' olarak güncellendi."
            )
        except ApplicationNotFoundError:
            return self.list(request, job_id=job_id, user_id=user_id, error=f"{application_id} ID'li başvuru bulunamadı.")
        except ApplicationValidationError as exc:
            return self.list(request, job_id=job_id, user_id=user_id, error=str(exc))

    # --------------------------------------------------------------------------
    # 5. DELETE (Direct & Nested)
    # --------------------------------------------------------------------------
    def delete(
        self,
        request: HttpRequest,
        application_id: int,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """Başvuruyu siler."""
        try:
            app = self.service.get_application_by_id(application_id)
            if job_id is not None and app.job_id != job_id:
                return self.list(request, job_id=job_id, error=f"{application_id} ID'li başvuru bu ilana ait değil.")
            if user_id is not None and app.applicant_id != user_id:
                return self.list(request, user_id=user_id, error=f"{application_id} ID'li başvuru bu kullanıcıya ait değil.")

            self.service.delete_application(application_id)
            return self.list(
                request,
                job_id=job_id,
                user_id=user_id,
                success=f"{application_id} ID'li başvuru başarıyla silindi."
            )
        except ApplicationNotFoundError:
            return self.list(request, job_id=job_id, user_id=user_id, error=f"{application_id} ID'li başvuru bulunamadı.")

    # --------------------------------------------------------------------------
    # ENTRY POINT / DISPATCHER
    # --------------------------------------------------------------------------
    def dispatch(
        self,
        request: HttpRequest,
        application_id: Optional[int] = None,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> HttpResponse:
        """HTTP fiili ve aksiyona göre yönlendirir."""
        if request.method == "POST":
            action = request.POST.get("_method") or request.POST.get("action")
            if action == "DELETE" and application_id:
                return self.delete(request, application_id, job_id=job_id, user_id=user_id)
            elif action == "STATUS" and application_id:
                return self.update_status(request, application_id, job_id=job_id, user_id=user_id)
            return self.create(request, job_id=job_id, user_id=user_id)
        elif request.method == "GET":
            if application_id is not None:
                # Silme kontrolü URL üzerinden de gelebilir (/delete/)
                if request.path.endswith("/delete/"):
                    return self.delete(request, application_id, job_id=job_id, user_id=user_id)
                return self.detail(request, application_id, job_id=job_id, user_id=user_id)
            return self.list(request, job_id=job_id, user_id=user_id)
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
