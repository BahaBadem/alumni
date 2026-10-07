"""
core/controllers/user_controller.py - Web HTML Arayüzü Controller'ı (MVC)

Bu modül, web tarayıcısından gelen HTTP isteklerini (HTML formları ve sayfalar)
karşılayan, şablonları (templates/users.html) render eden ve CRUD operasyonlarını
yöneten Web Controller sınıfını (UserController) içerir.
"""

from datetime import datetime
from typing import Optional, Any
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Hem Django ORM hem de In-Memory desteği
from core.models import UserProfile
import user as in_memory_service
from model import parse_date_value, ModelValidationError, UserNotFoundError


def parse_date_str(val: Any) -> Optional[datetime.date]:
    """Tarih girdisini date nesnesine çevirir."""
    if not val:
        return None
    try:
        return parse_date_value(val)
    except Exception:
        return None


class UserController:
    """
    Web Arayüzü Kullanıcı Controller'ı (MVC - Controller Katmanı).
    
    Sorumlulukları:
    - templates/users.html şablonuna kullanıcı listesini aktarmak (Read)
    - Web formundan gelen POST isteğiyle yeni kayıt oluşturmak (Create)
    - Kullanıcı detayını göstermek (Read Single)
    - Kullanıcı bilgilerini güncellemek (Update)
    - Kullanıcı kaydını silmek (Delete)
    """

    def __init__(self, use_in_memory: bool = False):
        """
        Args:
            use_in_memory (bool): True ise harici veritabanı olmadan bellek içi
                                  (user.py) deposunu kullanır. False ise Django ORM kullanır.
        """
        self.use_in_memory = use_in_memory

    # --------------------------------------------------------------------------
    # CRUD: 1. CREATE (YENİ KULLANICI OLUŞTURMA)
    # --------------------------------------------------------------------------
    def create(self, request: HttpRequest) -> HttpResponse:
        """
        HTML formundan gönderilen verilerle yeni bir kullanıcı oluşturur (POST).
        Eksik veya hatalı alanda form verilerini koruyarak hata mesajıyla sayfayı render eder.
        """
        name = str(request.POST.get("name") or request.POST.get("isim", "")).strip()
        birth_date_raw = str(request.POST.get("birth_date") or request.POST.get("dogum_tarihi", "")).strip()
        city = str(request.POST.get("city") or request.POST.get("sehir", "") or request.POST.get("şehir", "")).strip()
        school = str(request.POST.get("school") or request.POST.get("okul", "")).strip()

        form_data = {
            "name": name,
            "birth_date": birth_date_raw,
            "city": city,
            "school": school,
        }

        # Validasyon 1: Zorunlu alan kontrolü
        if not (name and birth_date_raw and city and school):
            users = self._get_all_users_list()
            return render(request, "users.html", {
                "users": users,
                "error": "Lütfen tüm hücreleri (İsim, Doğum Tarihi, Şehir, Okul) eksiksiz doldurunuz.",
                "form_data": form_data,
            }, status=400)

        # Validasyon 2: Tarih formatı kontrolü
        birth_date = parse_date_str(birth_date_raw)
        if not birth_date:
            users = self._get_all_users_list()
            return render(request, "users.html", {
                "users": users,
                "error": "Geçersiz doğum tarihi formatı. Lütfen YYYY-AA-GG formatında giriniz.",
                "form_data": form_data,
            }, status=400)

        # Kayıt işlemi (ORM veya In-Memory)
        if self.use_in_memory:
            new_user = in_memory_service.create_user(
                name=name, birth_date=birth_date, city=city, school=school
            )
            user_name = new_user.name
        else:
            new_user = UserProfile.objects.create(
                name=name,
                birth_date=birth_date,
                city=city,
                school=school,
            )
            user_name = new_user.name

        users = self._get_all_users_list()
        return render(request, "users.html", {
            "users": users,
            "success": f"'{user_name}' adlı kullanıcı başarıyla kaydedildi!",
        }, status=201)

    # --------------------------------------------------------------------------
    # CRUD: 2. READ (LİSTELEME VE DETAY GÖRÜNTÜLEME)
    # --------------------------------------------------------------------------
    def read(self, request: HttpRequest, user_id: Optional[int] = None) -> HttpResponse:
        """
        Kullanıcı listesini (veya tekil kullanıcı detayını) getirip users.html şablonunu render eder.
        """
        if user_id is not None:
            return self.detail(request, user_id)
        return self.list(request)

    def list(self, request: HttpRequest) -> HttpResponse:
        """Tüm kullanıcıları listeler."""
        users = self._get_all_users_list()
        return render(request, "users.html", {"users": users})

    def detail(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """Tek bir kullanıcının detayını döndürür/gösterir."""
        user = self._get_user_by_id(user_id)
        if not user:
            users = self._get_all_users_list()
            return render(request, "users.html", {
                "users": users,
                "error": f"{user_id} ID'li kullanıcı bulunamadı.",
            }, status=404)
        return render(request, "users.html", {"user": user, "users": [user]})

    # --------------------------------------------------------------------------
    # CRUD: 3. UPDATE (GÜNCELLEME)
    # --------------------------------------------------------------------------
    def update(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """Kullanıcı bilgilerini form üzerinden günceller."""
        user = self._get_user_by_id(user_id)
        if not user:
            return render(request, "users.html", {
                "users": self._get_all_users_list(),
                "error": f"{user_id} ID'li kullanıcı bulunamadı.",
            }, status=404)

        name = request.POST.get("name") or request.POST.get("isim")
        birth_date_raw = request.POST.get("birth_date") or request.POST.get("dogum_tarihi")
        city = request.POST.get("city") or request.POST.get("sehir") or request.POST.get("şehir")
        school = request.POST.get("school") or request.POST.get("okul")

        if self.use_in_memory:
            updated = in_memory_service.patch_user(
                user_id=user_id,
                name=name,
                birth_date=birth_date_raw,
                city=city,
                school=school,
            )
        else:
            if name:
                user.name = str(name).strip()
            if birth_date_raw:
                bdate = parse_date_str(birth_date_raw)
                if bdate:
                    user.birth_date = bdate
            if city:
                user.city = str(city).strip()
            if school:
                user.school = str(school).strip()
            user.save()

        users = self._get_all_users_list()
        return render(request, "users.html", {
            "users": users,
            "success": f"{user_id} ID'li kullanıcı bilgileri güncellendi.",
        })

    # --------------------------------------------------------------------------
    # CRUD: 4. DELETE (SİLME)
    # --------------------------------------------------------------------------
    def delete(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """Belirtilen kullanıcıyı siler."""
        try:
            if self.use_in_memory:
                in_memory_service.delete_user(user_id)
            else:
                user = UserProfile.objects.get(id=user_id)
                user.delete()
            users = self._get_all_users_list()
            return render(request, "users.html", {
                "users": users,
                "success": f"{user_id} ID'li kullanıcı silindi.",
            })
        except Exception:
            users = self._get_all_users_list()
            return render(request, "users.html", {
                "users": users,
                "error": f"{user_id} ID'li kullanıcı bulunamadı veya silinemedi.",
            }, status=404)

    # --------------------------------------------------------------------------
    # CONTROLLER ENTRY POINT / DISPATCHER
    # --------------------------------------------------------------------------
    def dispatch(self, request: HttpRequest, user_id: Optional[int] = None) -> HttpResponse:
        """
        HTTP isteğini method türüne göre ilgili CRUD metoduna yönlendirir.
        """
        if request.method == "POST":
            # Silme aksiyonu kontrolü (örn. POST ile silme talebi)
            action = request.POST.get("_method") or request.POST.get("action")
            if action == "DELETE" and user_id:
                return self.delete(request, user_id)
            if action in ("PUT", "PATCH") and user_id:
                return self.update(request, user_id)
            return self.create(request)
        elif request.method == "GET":
            return self.read(request, user_id)
        else:
            return HttpResponseNotAllowed(["GET", "POST"])

    @classmethod
    def as_view(cls, **initkwargs):
        """Django Class-Based View standardında rotaya bağlanabilen görünüm fonksiyonu üretir."""
        def view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)
        view.view_class = cls
        return csrf_exempt(view)

    # --------------------------------------------------------------------------
    # YARDIMCI / INTERNAL METOTLAR
    # --------------------------------------------------------------------------
    def _get_all_users_list(self):
        """Veri deposundan tüm kullanıcıları çeker."""
        if self.use_in_memory:
            return in_memory_service.get_all_users()
        return UserProfile.objects.all()

    def _get_user_by_id(self, user_id: int):
        """ID ile tekil kullanıcı çeker."""
        if self.use_in_memory:
            return in_memory_service.get_user(user_id)
        try:
            return UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return None


# Kolay view fonksiyonu sarmalayıcısı
@csrf_exempt
def user_controller_view(request: HttpRequest, user_id: Optional[int] = None) -> HttpResponse:
    """Django urls.py için UserController view handler fonksiyonu."""
    controller = UserController(use_in_memory=False)
    return controller.dispatch(request, user_id=user_id)
