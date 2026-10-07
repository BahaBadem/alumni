"""
core/controllers/api_user_controller.py - REST API Controller'ı (MVC)

Bu modül, REST API istemcilerinden gelen JSON/HTTP isteklerini karşılayan,
durum kodlarını (200, 201, 400, 404, 405) ve JSON çıktılarını yöneten,
standart HTTP fiilleri (GET, POST, PUT, PATCH, DELETE) üzerinden tam CRUD
operasyonlarını icra eden ApiUserController sınıfını içerir.
"""

import json
from urllib.parse import parse_qs
from typing import Optional, Dict, Any
from django.http import HttpRequest, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

# Model ve In-Memory Servis Entegrasyonu
from core.models import UserProfile
import user as in_memory_service
from model import parse_date_value, ModelValidationError, UserNotFoundError


def extract_request_payload(request: HttpRequest) -> Optional[Dict[str, Any]]:
    """
    POST, PUT, PATCH, DELETE isteklerinden JSON veya form gövdesini ayıklar.
    Geçersiz JSON formatında None döndürür.
    """
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


class ApiUserController:
    """
    REST API Kullanıcı Controller'ı (MVC - Controller Katmanı).

    Desteklenen CRUD Operasyonları:
    - CREATE: POST /api/users/ (201 Created)
    - READ:   GET /api/users/ & GET /api/users/<id>/ (200 OK)
    - UPDATE: PUT /api/users/<id>/ (Tam güncelleme) (200 OK)
    - PATCH:  PATCH /api/users/<id>/ (Kısmi güncelleme) (200 OK)
    - DELETE: DELETE /api/users/<id>/ & DELETE /api/users/?all=true (200 OK)
    """

    def __init__(self, use_in_memory: bool = False):
        """
        Args:
            use_in_memory (bool): True ise in-memory deposunu (user.py) kullanır.
                                  False ise Django ORM (UserProfile) kullanır.
        """
        self.use_in_memory = use_in_memory

    # --------------------------------------------------------------------------
    # CRUD: 1. CREATE (POST /api/users/)
    # --------------------------------------------------------------------------
    def create(self, request: HttpRequest) -> JsonResponse:
        """
        Yeni bir kullanıcı oluşturur (POST).
        Tüm alanlar (isim, doğum tarihi, şehir, okul) zorunludur.
        """
        data = extract_request_payload(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

        name = str(data.get("name") or data.get("isim") or "").strip()
        birth_date_raw = str(data.get("birth_date") or data.get("dogum_tarihi") or "").strip()
        city = str(data.get("city") or data.get("sehir") or data.get("şehir") or "").strip()
        school = str(data.get("school") or data.get("okul") or "").strip()

        # Doğrulama: Eksik alan kontrolü
        if not (name and birth_date_raw and city and school):
            return JsonResponse({
                "status": "error",
                "message": "Lütfen tüm hücreleri (isim, doğum tarihi, şehir, okul) eksiksiz doldurunuz."
            }, status=400)

        # Doğrulama: Tarih formatı kontrolü
        try:
            birth_date = parse_date_value(birth_date_raw)
            if not birth_date:
                raise ValueError()
        except Exception:
            return JsonResponse({
                "status": "error",
                "message": "Geçersiz doğum tarihi formatı. Lütfen YYYY-AA-GG (Örn: 2000-01-15) formatında giriniz."
            }, status=400)

        if self.use_in_memory:
            new_user = in_memory_service.create_user(
                name=name, birth_date=birth_date, city=city, school=school
            )
            user_data = new_user.to_dict()
        else:
            orm_user = UserProfile.objects.create(
                name=name, birth_date=birth_date, city=city, school=school
            )
            user_data = orm_user.to_dict()

        return JsonResponse({
            "status": "success",
            "message": "Kullanıcı başarıyla kaydedildi.",
            "user": user_data
        }, status=201)

    # --------------------------------------------------------------------------
    # CRUD: 2. READ (GET /api/users/ & GET /api/users/<id>/)
    # --------------------------------------------------------------------------
    def read(self, request: HttpRequest, user_id: Optional[int] = None) -> JsonResponse:
        """Kullanıcıları listeler veya tekil kullanıcı detayını getirir."""
        if user_id is not None:
            return self.detail(request, user_id)
        return self.list(request)

    def list(self, request: HttpRequest) -> JsonResponse:
        """Tüm kayıtlı kullanıcıları JSON listesi halinde döndürür."""
        if self.use_in_memory:
            users_list = [u.to_dict() for u in in_memory_service.get_all_users()]
        else:
            users_list = [u.to_dict() for u in UserProfile.objects.all()]

        return JsonResponse({
            "status": "success",
            "count": len(users_list),
            "users": users_list
        }, status=200)

    def detail(self, request: HttpRequest, user_id: int) -> JsonResponse:
        """Belirtilen ID'ye sahip tekil kullanıcıyı getirir."""
        if self.use_in_memory:
            user = in_memory_service.get_user(user_id)
            if not user:
                return JsonResponse({
                    "status": "error",
                    "message": f"{user_id} ID'li kullanıcı bulunamadı."
                }, status=404)
            return JsonResponse({"status": "success", "user": user.to_dict()}, status=200)
        else:
            try:
                orm_user = UserProfile.objects.get(id=user_id)
                return JsonResponse({"status": "success", "user": orm_user.to_dict()}, status=200)
            except UserProfile.DoesNotExist:
                return JsonResponse({
                    "status": "error",
                    "message": f"{user_id} ID'li kullanıcı bulunamadı."
                }, status=404)

    # --------------------------------------------------------------------------
    # CRUD: 3. UPDATE (PUT & PATCH /api/users/<id>/)
    # --------------------------------------------------------------------------
    def update(self, request: HttpRequest, user_id: Optional[int] = None) -> JsonResponse:
        """
        Kullanıcı bilgilerini TAM olarak günceller (PUT).
        Tüm alanlar (isim, doğum tarihi, şehir, okul) zorunludur.
        """
        data = extract_request_payload(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

        target_id = user_id or data.get("id") or data.get("user_id")
        if not target_id:
            return JsonResponse({
                "status": "error",
                "message": "Güncellenecek kullanıcı ID'si belirtilmelidir (URL: /api/users/<id>/ veya JSON: 'id')."
            }, status=400)

        name = str(data.get("name") or data.get("isim") or "").strip()
        birth_date_raw = str(data.get("birth_date") or data.get("dogum_tarihi") or "").strip()
        city = str(data.get("city") or data.get("sehir") or data.get("şehir") or "").strip()
        school = str(data.get("school") or data.get("okul") or "").strip()

        if not (name and birth_date_raw and city and school):
            return JsonResponse({
                "status": "error",
                "message": "PUT metodu tam güncelleme gerektirir. Lütfen tüm alanları (isim, doğum tarihi, şehir, okul) eksiksiz gönderiniz veya kısmi güncelleme için PATCH metodunu kullanınız."
            }, status=400)

        try:
            birth_date = parse_date_value(birth_date_raw)
            if not birth_date:
                raise ValueError()
        except Exception:
            return JsonResponse({
                "status": "error",
                "message": "Geçersiz doğum tarihi formatı. Lütfen YYYY-AA-GG (Örn: 2000-01-15) formatında giriniz."
            }, status=400)

        if self.use_in_memory:
            try:
                updated = in_memory_service.update_user(
                    user_id=int(target_id),
                    name=name,
                    birth_date=birth_date,
                    city=city,
                    school=school
                )
                user_data = updated.to_dict()
            except UserNotFoundError:
                return JsonResponse({"status": "error", "message": f"{target_id} ID'li kullanıcı bulunamadı."}, status=404)
        else:
            try:
                orm_user = UserProfile.objects.get(id=target_id)
            except UserProfile.DoesNotExist:
                return JsonResponse({"status": "error", "message": f"{target_id} ID'li kullanıcı bulunamadı."}, status=404)

            orm_user.name = name
            orm_user.birth_date = birth_date
            orm_user.city = city
            orm_user.school = school
            orm_user.save()
            user_data = orm_user.to_dict()

        return JsonResponse({
            "status": "success",
            "message": "Kullanıcı bilgileri başarıyla güncellendi (PUT).",
            "user": user_data
        }, status=200)

    def partial_update(self, request: HttpRequest, user_id: Optional[int] = None) -> JsonResponse:
        """
        Kullanıcı bilgilerini KISMİ olarak günceller (PATCH).
        Yalnızca istekte gönderilen alanlar değiştirilir.
        """
        data = extract_request_payload(request)
        if data is None:
            return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

        target_id = user_id or data.get("id") or data.get("user_id")
        if not target_id:
            return JsonResponse({
                "status": "error",
                "message": "Kısmi güncellenecek kullanıcı ID'si belirtilmelidir (URL: /api/users/<id>/ veya JSON: 'id')."
            }, status=400)

        if self.use_in_memory:
            try:
                updated = in_memory_service.patch_user(user_id=int(target_id), **data)
                return JsonResponse({
                    "status": "success",
                    "message": "Kullanıcı bilgileri kısmi olarak güncellendi (PATCH).",
                    "user": updated.to_dict()
                }, status=200)
            except UserNotFoundError:
                return JsonResponse({"status": "error", "message": f"{target_id} ID'li kullanıcı bulunamadı."}, status=404)
            except ModelValidationError as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)
        else:
            try:
                user = UserProfile.objects.get(id=target_id)
            except UserProfile.DoesNotExist:
                return JsonResponse({"status": "error", "message": f"{target_id} ID'li kullanıcı bulunamadı."}, status=404)

            has_changes = False

            if "name" in data or "isim" in data:
                new_name = str(data.get("name") or data.get("isim") or "").strip()
                if new_name:
                    user.name = new_name
                    has_changes = True

            if "birth_date" in data or "dogum_tarihi" in data:
                raw_bdate = str(data.get("birth_date") or data.get("dogum_tarihi") or "").strip()
                if raw_bdate:
                    try:
                        parsed_bdate = parse_date_value(raw_bdate)
                        if not parsed_bdate:
                            raise ValueError()
                        user.birth_date = parsed_bdate
                        has_changes = True
                    except Exception:
                        return JsonResponse({
                            "status": "error",
                            "message": "Geçersiz doğum tarihi formatı. Lütfen YYYY-AA-GG (Örn: 2000-01-15) formatında giriniz."
                        }, status=400)

            if "city" in data or "sehir" in data or "şehir" in data:
                new_city = str(data.get("city") or data.get("sehir") or data.get("şehir") or "").strip()
                if new_city:
                    user.city = new_city
                    has_changes = True

            if "school" in data or "okul" in data:
                new_school = str(data.get("school") or data.get("okul") or "").strip()
                if new_school:
                    user.school = new_school
                    has_changes = True

            if not has_changes:
                return JsonResponse({
                    "status": "error",
                    "message": "Güncellenecek en az bir alan (isim, doğum tarihi, şehir veya okul) belirtilmelidir."
                }, status=400)

            user.save()
            return JsonResponse({
                "status": "success",
                "message": "Kullanıcı bilgileri kısmi olarak güncellendi (PATCH).",
                "user": user.to_dict()
            }, status=200)

    # --------------------------------------------------------------------------
    # CRUD: 4. DELETE (DELETE /api/users/<id>/)
    # --------------------------------------------------------------------------
    def delete(self, request: HttpRequest, user_id: Optional[int] = None) -> JsonResponse:
        """
        Kullanıcı kaydını siler (DELETE).
        Toplu silme için ?all=true parametresini destekler.
        """
        data = extract_request_payload(request)
        target_id = user_id or (data and (data.get("id") or data.get("user_id"))) or request.GET.get("id") or request.GET.get("user_id")

        # Toplu silme (?all=true)
        if (request.GET.get("all") == "true" or (data and data.get("all") is True)) and not target_id:
            if self.use_in_memory:
                deleted_count = in_memory_service.delete_all_users()
            else:
                deleted_count, _ = UserProfile.objects.all().delete()
            return JsonResponse({
                "status": "success",
                "message": f"Tüm kullanıcı kayıtları silindi ({deleted_count} kayıt).",
                "deleted_count": deleted_count
            }, status=200)

        if not target_id:
            return JsonResponse({
                "status": "error",
                "message": "Silinecek kullanıcı ID'si belirtilmelidir (URL üzerinden: /api/users/<id>/ veya JSON: 'id')."
            }, status=400)

        if self.use_in_memory:
            try:
                deleted_u = in_memory_service.delete_user(int(target_id))
                return JsonResponse({
                    "status": "success",
                    "message": f"'{deleted_u.name}' (ID: {target_id}) adlı kullanıcı başarıyla silindi.",
                    "deleted_id": int(target_id),
                    "deleted_user": deleted_u.to_dict()
                }, status=200)
            except UserNotFoundError:
                return JsonResponse({"status": "error", "message": f"{target_id} ID'li kullanıcı bulunamadı."}, status=404)
        else:
            try:
                user = UserProfile.objects.get(id=target_id)
                user_data = user.to_dict()
                user.delete()
                return JsonResponse({
                    "status": "success",
                    "message": f"'{user_data['name']}' (ID: {target_id}) adlı kullanıcı başarıyla silindi.",
                    "deleted_id": int(target_id),
                    "deleted_user": user_data
                }, status=200)
            except UserProfile.DoesNotExist:
                return JsonResponse({"status": "error", "message": f"{target_id} ID'li kullanıcı bulunamadı."}, status=404)

    # --------------------------------------------------------------------------
    # CONTROLLER ENTRY POINT / DISPATCHER
    # --------------------------------------------------------------------------
    def dispatch(self, request: HttpRequest, user_id: Optional[int] = None) -> JsonResponse:
        """
        HTTP metodunu inceleyip ilgili CRUD metoduna yönlendirir.
        """
        if request.method == "GET":
            return self.read(request, user_id)
        elif request.method == "POST":
            return self.create(request)
        elif request.method == "PUT":
            return self.update(request, user_id)
        elif request.method == "PATCH":
            return self.partial_update(request, user_id)
        elif request.method == "DELETE":
            return self.delete(request, user_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST", "PUT", "PATCH", "DELETE"])

    @classmethod
    def as_view(cls, **initkwargs):
        """Django Class-Based View standardında rotaya bağlanabilen görünüm fonksiyonu üretir."""
        def view(request: HttpRequest, *args, **kwargs) -> JsonResponse:
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        return csrf_exempt(view)


# Kolay view fonksiyonu sarmalayıcısı
@csrf_exempt
def api_user_controller_view(request: HttpRequest, user_id: Optional[int] = None) -> JsonResponse:
    """Django urls.py için ApiUserController view handler fonksiyonu."""
    controller = ApiUserController(use_in_memory=False)
    return controller.dispatch(request, user_id=user_id)
