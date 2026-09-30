from datetime import datetime
import json
from urllib.parse import parse_qs
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile


def parse_date(date_str):
    """Farklı tarih formatlarını ayrıştırıp date objesine dönüştürür."""
    if not date_str:
        return None
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except (ValueError, AttributeError):
            pass
    return None


def get_request_data(request):
    """POST, PUT, PATCH isteklerinden JSON veya form verisini çıkarır."""
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


def home(request):
    """
    Kök dizine (localhost:8000/) gelen istekleri yakalayıp 
    geçici ana sayfa şablonunu (index.html) render eden view fonksiyonu.
    """
    return render(request, "index.html")


def about(request):
    """
    /about/ rotasına gelen istekleri yakalayıp 
    geçici hakkında sayfasını (about.html) render eden view fonksiyonu.
    """
    return render(request, "about.html")



def hello(request, name="World"):
    """
    /hello rotasında 'Hello, World!',
    /hello/<name>/ rotasında dinamik olarak 'Hello, {name}!' basan view fonksiyonu.
    """
    return HttpResponse(f"Hello, {name}!")


def calculate_sum(request, num1, num2):
    """
    /sum/<num1>/<num2>/ rotasına gelen iki sayının toplamını ekrana basan view fonksiyonu.
    """
    total = num1 + num2
    return HttpResponse(str(total))


@require_http_methods(["GET"])
def health_check(request):
    """
    /api/healt veya /api/health rotasına GET isteği atıldığında 
    JSON formatında durum bilgisi döndüren view fonksiyonu.
    """
    return JsonResponse({
        "status": "ok",
        "message": "healthy"
    })


@csrf_exempt
def api_users_view(request, user_id=None):
    """
    /api/users rotasını yöneten REST API endpoint'i:
    - GET:   Tüm kullanıcıları veya belirli bir kullanıcıyı (user_id) JSON formatında listeler.
    - POST:  Yeni bir kullanıcı kaydeder (isim, doğum tarihi, şehir, okul).
    - PUT:   Kullanıcı bilgilerini tamamen günceller (tüm alanlar zorunlu).
    - PATCH: Kullanıcı bilgilerini kısmi olarak günceller (yalnızca gönderilen alanlar değişir).
    - DELETE: Kullanıcıyı siler.
    """
    if request.method == "GET":
        if user_id is not None:
            try:
                user = UserProfile.objects.get(id=user_id)
                return JsonResponse({
                    "status": "success",
                    "user": user.to_dict()
                }, status=200)
            except UserProfile.DoesNotExist:
                return JsonResponse({
                    "status": "error",
                    "message": f"{user_id} ID'li kullanıcı bulunamadı."
                }, status=404)

        users = UserProfile.objects.all()
        user_list = [u.to_dict() for u in users]
        return JsonResponse({
            "status": "success",
            "count": len(user_list),
            "users": user_list
        }, status=200)

    data = get_request_data(request)
    if data is None:
        return JsonResponse({"status": "error", "message": "Geçersiz JSON formatı."}, status=400)

    if request.method == "POST":
        name = str(data.get("name") or data.get("isim") or "").strip()
        birth_date_raw = str(data.get("birth_date") or data.get("dogum_tarihi") or "").strip()
        city = str(data.get("city") or data.get("sehir") or data.get("şehir") or "").strip()
        school = str(data.get("school") or data.get("okul") or "").strip()

        # Doğrulama: Tüm hücreler dolu mu?
        if not (name and birth_date_raw and city and school):
            return JsonResponse({
                "status": "error",
                "message": "Lütfen tüm hücreleri (isim, doğum tarihi, şehir, okul) eksiksiz doldurunuz."
            }, status=400)

        # Doğum tarihi kontrolü
        birth_date = parse_date(birth_date_raw)
        if not birth_date:
            return JsonResponse({
                "status": "error",
                "message": "Geçersiz doğum tarihi formatı. Lütfen YYYY-AA-GG (Örn: 2000-01-15) formatında giriniz."
            }, status=400)

        # Veritabanına kayıt
        user = UserProfile.objects.create(
            name=name,
            birth_date=birth_date,
            city=city,
            school=school
        )

        return JsonResponse({
            "status": "success",
            "message": "Kullanıcı başarıyla kaydedildi.",
            "user": user.to_dict()
        }, status=201)

    elif request.method == "PUT":
        target_id = user_id or data.get("id") or data.get("user_id")
        if not target_id:
            return JsonResponse({
                "status": "error",
                "message": "Güncellenecek kullanıcı ID'si belirtilmelidir (URL: /api/users/<id>/ veya JSON: 'id')."
            }, status=400)

        try:
            user = UserProfile.objects.get(id=target_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": f"{target_id} ID'li kullanıcı bulunamadı."
            }, status=404)

        name = str(data.get("name") or data.get("isim") or "").strip()
        birth_date_raw = str(data.get("birth_date") or data.get("dogum_tarihi") or "").strip()
        city = str(data.get("city") or data.get("sehir") or data.get("şehir") or "").strip()
        school = str(data.get("school") or data.get("okul") or "").strip()

        # PUT tam güncelleme bekler
        if not (name and birth_date_raw and city and school):
            return JsonResponse({
                "status": "error",
                "message": "PUT metodu tam güncelleme gerektirir. Lütfen tüm alanları (isim, doğum tarihi, şehir, okul) eksiksiz gönderiniz veya kısmi güncelleme için PATCH metodunu kullanınız."
            }, status=400)

        birth_date = parse_date(birth_date_raw)
        if not birth_date:
            return JsonResponse({
                "status": "error",
                "message": "Geçersiz doğum tarihi formatı. Lütfen YYYY-AA-GG (Örn: 2000-01-15) formatında giriniz."
            }, status=400)

        user.name = name
        user.birth_date = birth_date
        user.city = city
        user.school = school
        user.save()

        return JsonResponse({
            "status": "success",
            "message": "Kullanıcı bilgileri başarıyla güncellendi (PUT).",
            "user": user.to_dict()
        }, status=200)

    elif request.method == "PATCH":
        target_id = user_id or data.get("id") or data.get("user_id")
        if not target_id:
            return JsonResponse({
                "status": "error",
                "message": "Kısmi güncellenecek kullanıcı ID'si belirtilmelidir (URL: /api/users/<id>/ veya JSON: 'id')."
            }, status=400)

        try:
            user = UserProfile.objects.get(id=target_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": f"{target_id} ID'li kullanıcı bulunamadı."
            }, status=404)

        has_changes = False

        if "name" in data or "isim" in data:
            new_name = str(data.get("name") or data.get("isim") or "").strip()
            if new_name:
                user.name = new_name
                has_changes = True

        if "birth_date" in data or "dogum_tarihi" in data:
            raw_bdate = str(data.get("birth_date") or data.get("dogum_tarihi") or "").strip()
            if raw_bdate:
                parsed_bdate = parse_date(raw_bdate)
                if not parsed_bdate:
                    return JsonResponse({
                        "status": "error",
                        "message": "Geçersiz doğum tarihi formatı. Lütfen YYYY-AA-GG (Örn: 2000-01-15) formatında giriniz."
                    }, status=400)
                user.birth_date = parsed_bdate
                has_changes = True

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

    elif request.method == "DELETE":
        target_id = user_id or (data and (data.get("id") or data.get("user_id"))) or request.GET.get("id") or request.GET.get("user_id")

        # İsteğe bağlı olarak tüm kayıtları silme (?all=true)
        if (request.GET.get("all") == "true" or (data and data.get("all") is True)) and not target_id:
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
            return JsonResponse({
                "status": "error",
                "message": f"{target_id} ID'li kullanıcı bulunamadı."
            }, status=404)

    return HttpResponseNotAllowed(["GET", "POST", "PUT", "PATCH", "DELETE"])


@csrf_exempt
def users_page_view(request):
    """
    /users/ rotasında görsel HTML arayüzünü (form ve tablo) sunan view.
    POST gelirse kullanıcıyı kaydedip sayfayı günceller.
    """
    if request.method == "POST":
        # HTML formundan doğrudan POST gelirse
        name = request.POST.get("name") or request.POST.get("isim", "")
        birth_date_raw = request.POST.get("birth_date") or request.POST.get("dogum_tarihi", "")
        city = request.POST.get("city") or request.POST.get("sehir", "") or request.POST.get("şehir", "")
        school = request.POST.get("school") or request.POST.get("okul", "")

        name = str(name).strip()
        birth_date_raw = str(birth_date_raw).strip()
        city = str(city).strip()
        school = str(school).strip()

        if not (name and birth_date_raw and city and school):
            users = UserProfile.objects.all()
            return render(request, "users.html", {
                "users": users,
                "error": "Lütfen tüm hücreleri (İsim, Doğum Tarihi, Şehir, Okul) eksiksiz doldurunuz.",
                "form_data": {"name": name, "birth_date": birth_date_raw, "city": city, "school": school}
            }, status=400)

        birth_date = parse_date(birth_date_raw)
        if not birth_date:
            users = UserProfile.objects.all()
            return render(request, "users.html", {
                "users": users,
                "error": "Geçersiz doğum tarihi formatı. Lütfen YYYY-AA-GG formatında giriniz.",
                "form_data": {"name": name, "birth_date": birth_date_raw, "city": city, "school": school}
            }, status=400)

        user = UserProfile.objects.create(
            name=name,
            birth_date=birth_date,
            city=city,
            school=school
        )

        users = UserProfile.objects.all()
        return render(request, "users.html", {
            "users": users,
            "success": f"'{user.name}' adlı kullanıcı başarıyla kaydedildi!"
        }, status=201)

    users = UserProfile.objects.all()
    return render(request, "users.html", {"users": users})


def swagger_ui_view(request):
    """
    /api/swagger rotasında Swagger UI arayüzünü render eden view.
    """
    return render(request, "swagger.html")


def swagger_json_view(request):
    """
    /api/swagger.json rotasında kök dizindeki swagger.json dosyasını
    okuyup JSON formatında döndüren view.
    Dosyada bir güncelleme yapıldığında anında arayüze yansır.
    """
    from django.conf import settings
    swagger_file_path = settings.BASE_DIR / "swagger.json"
    if not swagger_file_path.exists():
        return JsonResponse({"error": "swagger.json dosyası bulunamadı."}, status=404)

    with open(swagger_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return JsonResponse(data, safe=False)



