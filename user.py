"""
user.py - Veritabanı Bağımsız In-Memory CRUD Servis Katmanı (Alumni Portal)

Bu modül, harici bir veritabanı (Database) bağlantısı OLMAKSIZIN, bellek içi
(In-Memory) veri yapısı üzerinde tam teşekküllü CRUD (Create, Read, Update, Delete)
işlemlerini gerçekleştirir.
"""

from datetime import date, datetime
from threading import Lock
from typing import List, Optional, Dict, Any, Union

from model import User, ModelValidationError, UserNotFoundError, parse_date_value


# ==============================================================================
# BELLEK İÇİ VERİ DEPOSU (IN-MEMORY DATA STORE) & THREAD GÜVENLİĞİ
# ==============================================================================
_STORAGE_LOCK = Lock()
_USERS_DB: Dict[int, User] = {}
_AUTO_INCREMENT_ID: int = 1


def _generate_next_id() -> int:
    """Benzersiz ve artan bir kullanıcı ID'si üretir."""
    global _AUTO_INCREMENT_ID
    current_id = _AUTO_INCREMENT_ID
    _AUTO_INCREMENT_ID += 1
    return current_id


# ==============================================================================
# CRUD FONKSİYONLARI (CREATE, READ, UPDATE, DELETE)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. CREATE (YENİ KULLANICI OLUŞTURMA)
# ------------------------------------------------------------------------------
def create_user(
    name: str,
    birth_date: Union[str, date, datetime],
    city: str,
    school: str,
    **extra_fields
) -> User:
    """
    Veritabanı bağlantısı olmaksızın, belleğe yeni bir kullanıcı kaydeder.

    Args:
        name (str): Kullanıcının tam adı
        birth_date (str | date): Doğum tarihi (Örn: '2001-04-12' veya date objesi)
        city (str): Bulunduğu şehir
        school (str): Okuduğu veya mezun olduğu üniversite/okul
        **extra_fields: Alternatif Türkçe anahtar kelimeler ('isim', 'dogum_tarihi' vb.)

    Returns:
        User: Belleğe kaydedilen ve id atanan yeni User nesnesi.

    Raises:
        ModelValidationError: Zorunlu alanlar eksik veya format hatalıysa.
    """
    final_name = name or extra_fields.get("isim", "")
    final_bdate = birth_date or extra_fields.get("dogum_tarihi")
    final_city = city or extra_fields.get("sehir", "") or extra_fields.get("şehir", "")
    final_school = school or extra_fields.get("okul", "")

    parsed_date = parse_date_value(final_bdate)

    user = User(
        name=str(final_name).strip(),
        birth_date=parsed_date,
        city=str(final_city).strip(),
        school=str(final_school).strip(),
        created_at=datetime.now(),
    )
    user.validate(is_partial=False)

    with _STORAGE_LOCK:
        new_id = _generate_next_id()
        user.id = new_id
        _USERS_DB[new_id] = user

    return user


def add_user(user: User) -> User:
    """
    Önceden oluşturulmuş bir User nesnesini doğrular, id atar ve belleğe ekler.
    """
    user.validate(is_partial=False)
    with _STORAGE_LOCK:
        if user.id is None:
            user.id = _generate_next_id()
        _USERS_DB[user.id] = user
    return user


# ------------------------------------------------------------------------------
# 2. READ (KULLANICI BİLGİSİ OKUMA VE LİSTELEME)
# ------------------------------------------------------------------------------
def get_user_by_id(user_id: int) -> User:
    """
    Belirtilen ID'ye sahip kullanıcıyı döndürür.

    Args:
        user_id (int): Aranacak kullanıcı ID'si.

    Returns:
        User: Bulunan kullanıcı nesnesi.

    Raises:
        UserNotFoundError: Kullanıcı bulunamazsa fırlatılır.
    """
    with _STORAGE_LOCK:
        user = _USERS_DB.get(int(user_id))
    if user is None:
        raise UserNotFoundError(f"{user_id} ID'li kullanıcı bulunamadı.")
    return user


def get_user(user_id: int) -> Optional[User]:
    """
    Belirtilen ID'ye sahip kullanıcıyı güvenli şekilde döndürür.
    Kullanıcı yoksa exception fırlatmaz, None döner.
    """
    with _STORAGE_LOCK:
        return _USERS_DB.get(int(user_id))


def get_all_users() -> List[User]:
    """
    Bellekte kayıtlı olan tüm kullanıcıları liste olarak döndürür.

    Returns:
        List[User]: Kullanıcı nesneleri listesi (Kayıt sırasına göre).
    """
    with _STORAGE_LOCK:
        return list(_USERS_DB.values())


def filter_users(
    name: Optional[str] = None,
    city: Optional[str] = None,
    school: Optional[str] = None
) -> List[User]:
    """
    Kullanıcıları verilen arama kriterlerine göre filtreler (Case-insensitive arama).
    """
    results: List[User] = []
    with _STORAGE_LOCK:
        all_records = list(_USERS_DB.values())

    for u in all_records:
        if name and name.lower() not in u.name.lower():
            continue
        if city and city.lower() not in u.city.lower():
            continue
        if school and school.lower() not in u.school.lower():
            continue
        results.append(u)

    return results


# ------------------------------------------------------------------------------
# 3. UPDATE (KULLANICI BİLGİLERİNİ GÜNCELLEME)
# ------------------------------------------------------------------------------
def update_user(
    user_id: int,
    name: str,
    birth_date: Union[str, date, datetime],
    city: str,
    school: str,
    **extra_fields
) -> User:
    """
    Kullanıcı bilgilerini TAM olarak günceller (PUT Mantığı - Tüm alanlar zorunlu).

    Args:
        user_id (int): Güncellenecek kullanıcının ID'si.
        name (str): Yeni isim.
        birth_date (str | date): Yeni doğum tarihi.
        city (str): Yeni şehir.
        school (str): Yeni okul.

    Returns:
        User: Güncellenmiş User nesnesi.

    Raises:
        UserNotFoundError: Kullanıcı bulunamazsa.
        ModelValidationError: Eksik alan veya geçersiz tarih girildiyse.
    """
    user = get_user_by_id(user_id)

    final_name = name or extra_fields.get("isim", "")
    final_bdate = birth_date or extra_fields.get("dogum_tarihi")
    final_city = city or extra_fields.get("sehir", "") or extra_fields.get("şehir", "")
    final_school = school or extra_fields.get("okul", "")

    parsed_date = parse_date_value(final_bdate)

    updated_candidate = User(
        id=user.id,
        name=str(final_name).strip(),
        birth_date=parsed_date,
        city=str(final_city).strip(),
        school=str(final_school).strip(),
        created_at=user.created_at,
    )
    updated_candidate.validate(is_partial=False)

    with _STORAGE_LOCK:
        _USERS_DB[user.id] = updated_candidate

    return updated_candidate


def patch_user(user_id: int, **fields) -> User:
    """
    Kullanıcı bilgilerini KISMİ olarak günceller (PATCH Mantığı - Yalnızca verilen alanlar değişir).

    Args:
        user_id (int): Güncellenecek kullanıcının ID'si.
        **fields: Güncellenmek istenen alanlar (name, city, school, birth_date vb.)

    Returns:
        User: Güncellenmiş User nesnesi.

    Raises:
        UserNotFoundError: Kullanıcı bulunamazsa.
        ModelValidationError: Hiç alan gönderilmediyse veya format geçersizse.
    """
    user = get_user_by_id(user_id)
    has_changes = False

    name_val = fields.get("name") or fields.get("isim")
    if name_val is not None and str(name_val).strip():
        user.name = str(name_val).strip()
        has_changes = True

    bdate_val = fields.get("birth_date") or fields.get("dogum_tarihi")
    if bdate_val is not None and str(bdate_val).strip():
        user.birth_date = parse_date_value(bdate_val)
        has_changes = True

    city_val = fields.get("city") or fields.get("sehir") or fields.get("şehir")
    if city_val is not None and str(city_val).strip():
        user.city = str(city_val).strip()
        has_changes = True

    school_val = fields.get("school") or fields.get("okul")
    if school_val is not None and str(school_val).strip():
        user.school = str(school_val).strip()
        has_changes = True

    if not has_changes:
        raise ModelValidationError(
            "Güncellenecek en az bir geçerli alan (isim, doğum tarihi, şehir veya okul) belirtilmelidir."
        )

    user.validate(is_partial=True)

    with _STORAGE_LOCK:
        _USERS_DB[user.id] = user

    return user


# ------------------------------------------------------------------------------
# 4. DELETE (KULLANICI SİLME)
# ------------------------------------------------------------------------------
def delete_user(user_id: int) -> User:
    """
    Belirtilen ID'ye sahip kullanıcıyı bellekten siler.

    Args:
        user_id (int): Silinecek kullanıcının ID'si.

    Returns:
        User: Silinen kullanıcı nesnesi.

    Raises:
        UserNotFoundError: Kullanıcı bulunamazsa fırlatılır.
    """
    with _STORAGE_LOCK:
        target_id = int(user_id)
        if target_id not in _USERS_DB:
            raise UserNotFoundError(f"{user_id} ID'li kullanıcı bulunamadı.")
        deleted_user = _USERS_DB.pop(target_id)

    return deleted_user


def delete_all_users() -> int:
    """
    Bellekteki tüm kullanıcı kayıtlarını temizler.

    Returns:
        int: Silinen toplam kullanıcı sayısı.
    """
    with _STORAGE_LOCK:
        count = len(_USERS_DB)
        _USERS_DB.clear()
    return count


# ------------------------------------------------------------------------------
# 5. YARDIMCI VE TEST YÖNETİM METOTLARI
# ------------------------------------------------------------------------------
def count_users() -> int:
    """Bellekte kayıtlı toplam kullanıcı sayısını döndürür."""
    with _STORAGE_LOCK:
        return len(_USERS_DB)


def clear_storage() -> None:
    """Test ortamları için bellek deposunu ve ID sayacını sıfırlar."""
    global _AUTO_INCREMENT_ID
    with _STORAGE_LOCK:
        _USERS_DB.clear()
        _AUTO_INCREMENT_ID = 1


def seed_demo_users() -> List[User]:
    """Başlangıç veya test amaçlı örnek kullanıcıları belleğe ekler."""
    clear_storage()
    samples = [
        ("Ahmet Baha Badem", "2001-04-12", "Ankara", "Hacettepe Üniversitesi"),
        ("Ayşe Kaya", "1999-08-25", "İstanbul", "Boğaziçi Üniversitesi"),
        ("Mehmet Demir", "1998-11-03", "İzmir", "Ege Üniversitesi"),
    ]
    created = []
    for name, bdate, city, school in samples:
        created.append(create_user(name=name, birth_date=bdate, city=city, school=school))
    return created


# ==============================================================================
# BAĞIMSIZ ÇALIŞTIRMA VE TEST DEMOSU (CLI DEMO)
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 IN-MEMORY USER CRUD SİSTEMİ DEMO VE DOĞRULAMA")
    print("   (Database bağlantısı olmadan, saf Python ile)")
    print("=" * 60)

    # 1. Başlangıç temizliği
    clear_storage()
    print("\n[ADIM 1] Depo sıfırlandı. Toplam kullanıcı sayısı:", count_users())

    # 2. CREATE (Kullanıcılar Ekleniyor)
    print("\n[ADIM 2] Yeni kullanıcılar oluşturuluyor (CREATE)...")
    u1 = create_user("Ahmet Baha Badem", "2001-04-12", "Ankara", "Hacettepe Üniversitesi")
    print("  -> Eklendi:", u1)
    u2 = create_user("Zeynep Çelik", "2000-02-18", "İstanbul", "İTÜ")
    print("  -> Eklendi:", u2)
    u3 = create_user("Can Yılmaz", "1999-07-30", "İzmir", "ODTÜ")
    print("  -> Eklendi:", u3)
    print("  Toplam kayıt:", count_users())

    # 3. READ (Tümünü Listeleme ve ID ile Getirme)
    print("\n[ADIM 3] Kayıtlar okunuyor (READ)...")
    all_users = get_all_users()
    for idx, usr in enumerate(all_users, 1):
        print(f"  {idx}. {usr.name} | {usr.birth_date} | {usr.city} | {usr.school} (ID: {usr.id})")

    fetched_u2 = get_user_by_id(u2.id)
    print(f"  -> ID={u2.id} ile getirildi:", fetched_u2.to_dict()["name"])

    # 4. UPDATE (PUT - Tam Güncelleme)
    print("\n[ADIM 4] Kullanıcı tam güncelleniyor (UPDATE - PUT)...")
    updated_u1 = update_user(u1.id, "Ahmet Baha Badem (MSc)", "2001-04-12", "Ankara", "Hacettepe Bilgisayar")
    print("  -> Güncellendi:", updated_u1)

    # 5. PATCH (Kısmi Güncelleme)
    print("\n[ADIM 5] Kullanıcı kısmi güncelleniyor (PATCH)...")
    patched_u2 = patch_user(u2.id, city="Berlin")
    print("  -> Şehir güncellendi:", patched_u2.name, "-> Şehir:", patched_u2.city)

    # 6. DELETE (Kullanıcı Silme)
    print("\n[ADIM 6] Kullanıcı siliniyor (DELETE)...")
    deleted_user = delete_user(u3.id)
    print(f"  -> Silindi: {deleted_user.name} (ID: {deleted_user.id})")
    print("  Kalan kullanıcı sayısı:", count_users())

    # 7. Filtreleme Testi
    print("\n[ADIM 7] Filtreleme testi (City='Berlin')...")
    berlin_users = filter_users(city="Berlin")
    print("  -> Sonuçlar:", [u.name for u in berlin_users])

    print("\n" + "=" * 60)
    print("✅ TÜM IN-MEMORY CRUD FONKSİYONLARI BAŞARIYLA TAMAMLANDI!")
    print("=" * 60 + "\n")
