"""
core/controllers/api_application_controller.py - REST API İş & Staj Başvurusu Controller'ı (MVC)

Bu modül, REST API istemcilerinden gelen JSON isteklerini karşılayan,
durum kodlarını (200, 201, 400, 404, 409, 405) ve JSON çıktılarını yöneten,
standart HTTP fiilleri (GET, POST, PUT, PATCH, DELETE) üzerinden
hem Doğrudan (Direct) hem de İlişkisel (Nested - Job ve User altı) rotaları yöneten
ApiApplicationController sınıfını içerir.

Doğrudan Rotalar (Direct Routes):
- GET    /api/applications/
- POST   /api/applications/
- GET    /api/applications/<id>/
- PUT    /api/applications/<id>/
- PATCH  /api/applications/<id>/
- DELETE /api/applications/<id>/

İç İçe Rotalar - İlan Altı (Nested Routes under Job):
- GET    /api/jobs/<job_id>/applications/
- POST   /api/jobs/<job_id>/applications/
- GET    /api/jobs/<job_id>/applications/<id>/
- PATCH  /api/jobs/<job_id>/applications/<id>/
- DELETE /api/jobs/<job_id>/applications/<id>/

İç İçe Rotalar - Mezun/Kullanıcı Altı (Nested Routes under User):
- GET    /api/users/<user_id>/applications/
- POST   /api/users/<user_id>/applications/
- GET    /api/users/<user_id>/applications/<id>/
- DELETE /api/users/<user_id>/applications/<id>/
"""

import json
from urllib.parse import parse_qs
from typing import Optional, Dict, Any, List
from django.http import HttpRequest, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from core.models import JobPosting, UserProfile
from core.services import application_service
from core.services.application_service import (
    ApplicationValidationError,
    ApplicationNotFoundError,
    ApplicationDuplicateError
)


def extract_json_payload(request: HttpRequest) -> Optional[Dict[str, Any]]:
    """İstekten JSON gövdesini veya form verisini ayıklar."""
    content_type = request.content_type or ""
    if "application/json" in content_type or (request.body and request.body.strip().startswith(b"{")):
        try:
            return json.loads(request.body.decode("utf-8"))
        except Exception:
            return None
    if request.POST:
        return request.POST.dict()
    if request.body:
        try:
            parsed = parse_qs(request.body.decode("utf-8"))
            return {k: v[0] for k, v in parsed.items()}
        except Exception:
            pass
    return {}


class ApiApplicationController:
    """
    REST API İş & Staj Başvurusu Controller'ı (MVC - Controller Katmanı).
    Doğrudan ve Nested (Job & User) rotaların tamamını yönetir.
    """

    def __init__(self):
        self.service = application_service

    # --------------------------------------------------------------------------
    # 1. READ / LIST (Direct, Job-Nested, User-Nested)
    # --------------------------------------------------------------------------
    def list(
        self,
        request: HttpRequest,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> JsonResponse:
        """Başvuruları listeler."""
        try:
            status_param = request.GET.get("status") or request.GET.get("durum")
            
            # Job-Nested: /api/jobs/<job_id>/applications/
            if job_id is not None:
                if not JobPosting.objects.filter(id=job_id).exists():
                    return JsonResponse({"status": "error", "message": f"{job_id} ID'li iş ilanı bulunamadı."}, status=404)
                apps = self.service.get_applications_by_job(job_id=job_id, status=status_param)
                nested_context = "job"
            # User-Nested: /api/users/<user_id>/applications/
            elif user_id is not None:
                if not UserProfile.objects.filter(id=user_id).exists():
                    return JsonResponse({"status": "error", "message": f"{user_id} ID'li kullanıcı bulunamadı."}, status=404)
                apps = self.service.get_applications_by_user(user_id=user_id, status=status_param)
                nested_context = "user"
            # Direct: /api/applications/
            else:
                applicant_filter = request.GET.get("applicant_id") or request.GET.get("basvuran_id")
                job_filter = request.GET.get("job_id") or request.GET.get("ilan_id")
                keyword = request.GET.get("q") or request.GET.get("arama")

                if any([applicant_filter, job_filter, status_param, keyword]):
                    apps = self.service.filter_applications(
                        job_id=int(job_filter) if job_filter else None,
                        applicant_id=int(applicant_filter) if applicant_filter else None,
                        status=status_param,
                        keyword=keyword
                    )
                else:
                    apps = self.service.get_all_applications(status=status_param)
                nested_context = None

            data = [a.to_dict() for a in apps]
            res = {
                "status": "success",
                "count": len(data),
                "applications": data,
                "basvurular": data
            }
            if nested_context == "job":
                res["job_id"] = job_id
                res["nested"] = "job"
            elif nested_context == "user":
                res["user_id"] = user_id
                res["nested"] = "user"

            return JsonResponse(res, status=200)

        except (JobPosting.DoesNotExist, UserProfile.DoesNotExist) as not_found:
            return JsonResponse({"status": "error", "message": str(not_found)}, status=404)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 2. DETAIL (Direct, Job-Nested, User-Nested)
    # --------------------------------------------------------------------------
    def detail(
        self,
        request: HttpRequest,
        application_id: int,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> JsonResponse:
        """Tekil başvuru detayını döner."""
        try:
            if job_id is not None and not JobPosting.objects.filter(id=job_id).exists():
                return JsonResponse({"status": "error", "message": f"{job_id} ID'li iş ilanı bulunamadı."}, status=404)
            if user_id is not None and not UserProfile.objects.filter(id=user_id).exists():
                return JsonResponse({"status": "error", "message": f"{user_id} ID'li kullanıcı bulunamadı."}, status=404)

            app = self.service.get_application_by_id(application_id)

            if job_id is not None and app.job_id != job_id:
                return JsonResponse({"status": "error", "message": f"{application_id} ID'li başvuru {job_id} ID'li ilana ait değil."}, status=404)
            if user_id is not None and app.applicant_id != user_id:
                return JsonResponse({"status": "error", "message": f"{application_id} ID'li başvuru {user_id} ID'li kullanıcıya ait değil."}, status=404)

            data = app.to_dict()
            return JsonResponse({
                "status": "success",
                "application": data,
                "basvuru": data
            }, status=200)

        except ApplicationNotFoundError:
            return JsonResponse({"status": "error", "message": f"{application_id} ID'li başvuru bulunamadı."}, status=404)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 3. CREATE (Direct, Job-Nested, User-Nested)
    # --------------------------------------------------------------------------
    def create(
        self,
        request: HttpRequest,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> JsonResponse:
        """Yeni başvuru oluşturur."""
        payload = extract_json_payload(request)
        if payload is None or not payload:
            return JsonResponse({"status": "error", "message": "Geçersiz veya boş başvuru verisi."}, status=400)

        try:
            # Nested rota kontrolleri
            if job_id is not None:
                payload["job_id"] = job_id
            if user_id is not None:
                payload["applicant_id"] = user_id

            created_app = self.service.create_application(**payload)
            data = created_app.to_dict()
            return JsonResponse({
                "status": "success",
                "message": "İş başvurusu başarıyla alındı.",
                "application": data,
                "basvuru": data
            }, status=201)

        except ApplicationDuplicateError as dup_err:
            return JsonResponse({"status": "error", "message": str(dup_err)}, status=409)
        except ApplicationValidationError as val_err:
            return JsonResponse({"status": "error", "message": str(val_err)}, status=400)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 4. UPDATE (PUT /api/applications/<id>/)
    # --------------------------------------------------------------------------
    def update(
        self,
        request: HttpRequest,
        application_id: int,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> JsonResponse:
        """Başvuruyu tam olarak günceller."""
        payload = extract_json_payload(request)
        if payload is None or not payload:
            return JsonResponse({"status": "error", "message": "Geçersiz veya boş güncelleme verisi."}, status=400)

        try:
            app = self.service.get_application_by_id(application_id)
            if job_id is not None and app.job_id != job_id:
                return JsonResponse({"status": "error", "message": f"Başvuru bu ilana ait değil."}, status=404)
            if user_id is not None and app.applicant_id != user_id:
                return JsonResponse({"status": "error", "message": f"Başvuru bu kullanıcıya ait değil."}, status=404)

            updated = self.service.update_application(application_id, **payload)
            data = updated.to_dict()
            return JsonResponse({
                "status": "success",
                "message": "Başvuru başarıyla güncellendi.",
                "application": data,
                "basvuru": data
            }, status=200)

        except ApplicationNotFoundError:
            return JsonResponse({"status": "error", "message": f"{application_id} ID'li başvuru bulunamadı."}, status=404)
        except ApplicationValidationError as val_err:
            return JsonResponse({"status": "error", "message": str(val_err)}, status=400)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 5. PARTIAL UPDATE (PATCH /api/applications/<id>/ veya nested)
    # --------------------------------------------------------------------------
    def patch(
        self,
        request: HttpRequest,
        application_id: int,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> JsonResponse:
        """Başvuru durumunu veya ön yazısını kısmi günceller."""
        payload = extract_json_payload(request)
        if payload is None or not payload:
            return JsonResponse({"status": "error", "message": "Geçersiz veya boş kısmi güncelleme verisi."}, status=400)

        try:
            app = self.service.get_application_by_id(application_id)
            if job_id is not None and app.job_id != job_id:
                return JsonResponse({"status": "error", "message": f"Başvuru bu ilana ait değil."}, status=404)
            if user_id is not None and app.applicant_id != user_id:
                return JsonResponse({"status": "error", "message": f"Başvuru bu kullanıcıya ait değil."}, status=404)

            patched = self.service.patch_application(application_id, **payload)
            data = patched.to_dict()
            return JsonResponse({
                "status": "success",
                "message": "Başvuru başarıyla güncellendi (kısmi).",
                "application": data,
                "basvuru": data
            }, status=200)

        except ApplicationNotFoundError:
            return JsonResponse({"status": "error", "message": f"{application_id} ID'li başvuru bulunamadı."}, status=404)
        except ApplicationValidationError as val_err:
            return JsonResponse({"status": "error", "message": str(val_err)}, status=400)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 6. DELETE (DELETE /api/applications/<id>/ veya nested)
    # --------------------------------------------------------------------------
    def delete(
        self,
        request: HttpRequest,
        application_id: int,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> JsonResponse:
        """Başvuruyu kalıcı olarak siler / iptal eder."""
        try:
            app = self.service.get_application_by_id(application_id)
            if job_id is not None and app.job_id != job_id:
                return JsonResponse({"status": "error", "message": f"Başvuru bu ilana ait değil."}, status=404)
            if user_id is not None and app.applicant_id != user_id:
                return JsonResponse({"status": "error", "message": f"Başvuru bu kullanıcıya ait değil."}, status=404)

            self.service.delete_application(application_id)
            return JsonResponse({
                "status": "success",
                "message": f"{application_id} ID'li başvuru başarıyla silindi."
            }, status=200)

        except ApplicationNotFoundError:
            return JsonResponse({"status": "error", "message": f"{application_id} ID'li başvuru bulunamadı."}, status=404)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # ENTRY POINT & DISPATCHER
    # --------------------------------------------------------------------------
    def dispatch(
        self,
        request: HttpRequest,
        application_id: Optional[int] = None,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> JsonResponse:
        """HTTP metoduna göre yönlendirir."""
        method = request.method
        if method == "GET":
            if application_id is not None:
                return self.detail(request, application_id=application_id, job_id=job_id, user_id=user_id)
            return self.list(request, job_id=job_id, user_id=user_id)
        elif method == "POST":
            return self.create(request, job_id=job_id, user_id=user_id)
        elif method == "PUT":
            if application_id is None:
                return JsonResponse({"status": "error", "message": "PUT işlemi için başvuru ID gereklidir."}, status=400)
            return self.update(request, application_id=application_id, job_id=job_id, user_id=user_id)
        elif method == "PATCH":
            if application_id is None:
                return JsonResponse({"status": "error", "message": "PATCH işlemi için başvuru ID gereklidir."}, status=400)
            return self.patch(request, application_id=application_id, job_id=job_id, user_id=user_id)
        elif method == "DELETE":
            if application_id is None:
                return JsonResponse({"status": "error", "message": "DELETE işlemi için başvuru ID gereklidir."}, status=400)
            return self.delete(request, application_id=application_id, job_id=job_id, user_id=user_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST", "PUT", "PATCH", "DELETE"])

    @classmethod
    def as_view(cls, **initkwargs):
        """Django Class-Based View standardında görünüm fonksiyonu üretir."""
        def view(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        return csrf_exempt(view)
