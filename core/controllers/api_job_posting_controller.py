"""
core/controllers/api_job_posting_controller.py - REST API İş & Staj İlanı Controller'ı (MVC)

Bu modül, REST API istemcilerinden gelen JSON isteklerini karşılayan,
durum kodlarını (200, 201, 400, 404, 405) ve JSON çıktılarını yöneten,
standart HTTP fiilleri (GET, POST, PUT, PATCH, DELETE) üzerinden
hem Doğrudan (Direct) hem de İç İçe (Nested) rotaları yöneten ApiJobPostingController
sınıfını içerir.

Doğrudan Rotalar (Direct Routes):
- GET    /api/jobs/
- POST   /api/jobs/
- GET    /api/jobs/<id>/
- PUT    /api/jobs/<id>/
- PATCH  /api/jobs/<id>/
- DELETE /api/jobs/<id>/

İç İçe Rotalar (Nested Routes - User Altı):
- GET    /api/users/<user_id>/jobs/
- POST   /api/users/<user_id>/jobs/
- GET    /api/users/<user_id>/jobs/<job_id>/
- PUT    /api/users/<user_id>/jobs/<job_id>/
- PATCH  /api/users/<user_id>/jobs/<job_id>/
- DELETE /api/users/<user_id>/jobs/<job_id>/
"""

import json
from urllib.parse import parse_qs
from typing import Optional, Dict, Any, List
from django.http import HttpRequest, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from core.models import UserProfile
from core.services import job_posting_service
from core.services.job_posting_service import (
    JobPostingValidationError,
    JobPostingNotFoundError
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


class ApiJobPostingController:
    """
    REST API İş & Staj İlanı Controller'ı (MVC - Controller Katmanı).
    Doğrudan ve Nested rotaların tamamını yönetir.
    """

    def __init__(self):
        self.service = job_posting_service

    # --------------------------------------------------------------------------
    # 1. READ / LIST (GET /api/jobs/ veya GET /api/users/<user_id>/jobs/)
    # --------------------------------------------------------------------------
    def list(self, request: HttpRequest, user_id: Optional[int] = None) -> JsonResponse:
        """İlanları listeler. user_id verilmişse sadece o mezunun ilanlarını listeler."""
        try:
            if user_id is not None:
                # Nested route kontrolü: Kullanıcı var mı?
                if not UserProfile.objects.filter(id=user_id).exists():
                    return JsonResponse({
                        "status": "error",
                        "message": f"{user_id} ID'li kullanıcı bulunamadı."
                    }, status=404)
                
                active_param = request.GET.get("is_active") or request.GET.get("aktif_mi")
                active_only = active_param.lower() in ("1", "true", "yes") if active_param else False
                jobs = self.service.get_job_postings_by_user(user_id=user_id, active_only=active_only)
            else:
                keyword = request.GET.get("q") or request.GET.get("keyword") or request.GET.get("arama")
                emp_type = request.GET.get("employment_type") or request.GET.get("is_tipi")
                location = request.GET.get("location") or request.GET.get("konum")
                active_param = request.GET.get("is_active") or request.GET.get("aktif_mi")
                is_active = active_param.lower() in ("1", "true", "yes") if active_param else None

                if any([keyword, emp_type, location, is_active is not None]):
                    jobs = self.service.filter_job_postings(
                        keyword=keyword,
                        employment_type=emp_type,
                        location=location,
                        is_active=is_active
                    )
                else:
                    jobs = self.service.get_all_job_postings()

            data = [j.to_dict() for j in jobs]
            response_data = {
                "status": "success",
                "count": len(data),
                "job_postings": data,
                "ilanlar": data
            }
            if user_id is not None:
                response_data["user_id"] = user_id
                response_data["nested"] = True

            return JsonResponse(response_data, status=200)

        except UserProfile.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": f"{user_id} ID'li kullanıcı bulunamadı."
            }, status=404)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 2. DETAIL (GET /api/jobs/<job_id>/ veya GET /api/users/<user_id>/jobs/<job_id>/)
    # --------------------------------------------------------------------------
    def detail(self, request: HttpRequest, job_id: int, user_id: Optional[int] = None) -> JsonResponse:
        """Tekil ilan detayını döner."""
        try:
            if user_id is not None and not UserProfile.objects.filter(id=user_id).exists():
                return JsonResponse({
                    "status": "error",
                    "message": f"{user_id} ID'li kullanıcı bulunamadı."
                }, status=404)

            job = self.service.get_job_posting_by_id(job_id)

            if user_id is not None and job.poster_id != user_id:
                return JsonResponse({
                    "status": "error",
                    "message": f"{job_id} ID'li iş ilanı {user_id} ID'li kullanıcıya ait değil."
                }, status=404)

            data = job.to_dict()
            return JsonResponse({
                "status": "success",
                "job_posting": data,
                "ilan": data
            }, status=200)

        except JobPostingNotFoundError:
            return JsonResponse({
                "status": "error",
                "message": f"{job_id} ID'li iş ilanı bulunamadı."
            }, status=404)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 3. CREATE (POST /api/jobs/ veya POST /api/users/<user_id>/jobs/)
    # --------------------------------------------------------------------------
    def create(self, request: HttpRequest, user_id: Optional[int] = None) -> JsonResponse:
        """Yeni iş/staj ilanı oluşturur."""
        payload = extract_json_payload(request)
        if payload is None:
            return JsonResponse({
                "status": "error",
                "message": "Geçersiz JSON verisi."
            }, status=400)

        if not payload:
            return JsonResponse({
                "status": "error",
                "message": "İstek gövdesi (body) boş olamaz."
            }, status=400)

        try:
            # Nested route üzerinden geliyorsa poster_id'yi sabitle
            if user_id is not None:
                if not UserProfile.objects.filter(id=user_id).exists():
                    return JsonResponse({
                        "status": "error",
                        "message": f"{user_id} ID'li kullanıcı bulunamadı."
                    }, status=404)
                payload["poster_id"] = user_id

            job = self.service.create_job_posting(**payload)
            data = job.to_dict()
            return JsonResponse({
                "status": "success",
                "message": "İş ilanı başarıyla oluşturuldu.",
                "job_posting": data,
                "ilan": data
            }, status=201)

        except JobPostingValidationError as val_err:
            return JsonResponse({
                "status": "error",
                "message": str(val_err)
            }, status=400)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 4. UPDATE (PUT /api/jobs/<job_id>/ veya PUT /api/users/<user_id>/jobs/<job_id>/)
    # --------------------------------------------------------------------------
    def update(self, request: HttpRequest, job_id: int, user_id: Optional[int] = None) -> JsonResponse:
        """İlanı tam olarak günceller."""
        payload = extract_json_payload(request)
        if payload is None or not payload:
            return JsonResponse({
                "status": "error",
                "message": "Geçersiz veya boş güncelleme verisi."
            }, status=400)

        try:
            if user_id is not None:
                if not UserProfile.objects.filter(id=user_id).exists():
                    return JsonResponse({"status": "error", "message": f"{user_id} ID'li kullanıcı bulunamadı."}, status=404)
                existing = self.service.get_job_posting_by_id(job_id)
                if existing.poster_id != user_id:
                    return JsonResponse({"status": "error", "message": f"{job_id} ID'li iş ilanı {user_id} ID'li kullanıcıya ait değil."}, status=404)
                payload["poster_id"] = user_id

            updated_job = self.service.update_job_posting(job_id, **payload)
            data = updated_job.to_dict()
            return JsonResponse({
                "status": "success",
                "message": "İş ilanı başarıyla güncellendi.",
                "job_posting": data,
                "ilan": data
            }, status=200)

        except JobPostingNotFoundError:
            return JsonResponse({"status": "error", "message": f"{job_id} ID'li iş ilanı bulunamadı."}, status=404)
        except JobPostingValidationError as val_err:
            return JsonResponse({"status": "error", "message": str(val_err)}, status=400)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 5. PARTIAL UPDATE (PATCH /api/jobs/<job_id>/ veya PATCH /api/users/<user_id>/jobs/<job_id>/)
    # --------------------------------------------------------------------------
    def patch(self, request: HttpRequest, job_id: int, user_id: Optional[int] = None) -> JsonResponse:
        """İlanın belirli alanlarını kısmi günceller."""
        payload = extract_json_payload(request)
        if payload is None or not payload:
            return JsonResponse({
                "status": "error",
                "message": "Geçersiz veya boş kısmi güncelleme verisi."
            }, status=400)

        try:
            if user_id is not None:
                if not UserProfile.objects.filter(id=user_id).exists():
                    return JsonResponse({"status": "error", "message": f"{user_id} ID'li kullanıcı bulunamadı."}, status=404)
                existing = self.service.get_job_posting_by_id(job_id)
                if existing.poster_id != user_id:
                    return JsonResponse({"status": "error", "message": f"{job_id} ID'li iş ilanı {user_id} ID'li kullanıcıya ait değil."}, status=404)

            patched_job = self.service.patch_job_posting(job_id, **payload)
            data = patched_job.to_dict()
            return JsonResponse({
                "status": "success",
                "message": "İş ilanı başarıyla güncellendi (kısmi).",
                "job_posting": data,
                "ilan": data
            }, status=200)

        except JobPostingNotFoundError:
            return JsonResponse({"status": "error", "message": f"{job_id} ID'li iş ilanı bulunamadı."}, status=404)
        except JobPostingValidationError as val_err:
            return JsonResponse({"status": "error", "message": str(val_err)}, status=400)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # 6. DELETE (DELETE /api/jobs/<job_id>/ veya DELETE /api/users/<user_id>/jobs/<job_id>/)
    # --------------------------------------------------------------------------
    def delete(self, request: HttpRequest, job_id: int, user_id: Optional[int] = None) -> JsonResponse:
        """İlanı kalıcı olarak siler."""
        try:
            if user_id is not None:
                if not UserProfile.objects.filter(id=user_id).exists():
                    return JsonResponse({"status": "error", "message": f"{user_id} ID'li kullanıcı bulunamadı."}, status=404)
                existing = self.service.get_job_posting_by_id(job_id)
                if existing.poster_id != user_id:
                    return JsonResponse({"status": "error", "message": f"{job_id} ID'li iş ilanı {user_id} ID'li kullanıcıya ait değil."}, status=404)

            self.service.delete_job_posting(job_id)
            return JsonResponse({
                "status": "success",
                "message": f"{job_id} ID'li iş ilanı başarıyla silindi."
            }, status=200)

        except JobPostingNotFoundError:
            return JsonResponse({"status": "error", "message": f"{job_id} ID'li iş ilanı bulunamadı."}, status=404)
        except Exception as exc:
            return JsonResponse({"status": "error", "message": str(exc)}, status=500)

    # --------------------------------------------------------------------------
    # REST DISPATCHER & CBV KÖPRÜSÜ
    # --------------------------------------------------------------------------
    def dispatch(
        self,
        request: HttpRequest,
        job_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> JsonResponse:
        """HTTP fiiline ve rota parametrelerine göre ilgili CRUD metodunu çalıştırır."""
        method = request.method
        if method == "GET":
            if job_id is not None:
                return self.detail(request, job_id=job_id, user_id=user_id)
            return self.list(request, user_id=user_id)
        elif method == "POST":
            return self.create(request, user_id=user_id)
        elif method == "PUT":
            if job_id is None:
                return JsonResponse({"status": "error", "message": "PUT işlemi için ilan ID gereklidir."}, status=400)
            return self.update(request, job_id=job_id, user_id=user_id)
        elif method == "PATCH":
            if job_id is None:
                return JsonResponse({"status": "error", "message": "PATCH işlemi için ilan ID gereklidir."}, status=400)
            return self.patch(request, job_id=job_id, user_id=user_id)
        elif method == "DELETE":
            if job_id is None:
                return JsonResponse({"status": "error", "message": "DELETE işlemi için ilan ID gereklidir."}, status=400)
            return self.delete(request, job_id=job_id, user_id=user_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST", "PUT", "PATCH", "DELETE"])

    @classmethod
    def as_view(cls, **initkwargs):
        """Django URLconf için view callable üretir."""
        def view(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        return csrf_exempt(view)
