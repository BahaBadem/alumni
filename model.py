"""
model.py - Veritabanı Bağımsız Domain Model Katmanı (Alumni Portal)

Bu modül, herhangi bir harici veritabanı (Django ORM, SQLite, PostgreSQL vb.)
bağımlılığı OLMAKSIZIN, saf Python (Pure Python) ile tasarlanmış User modelini
ve veri doğrulama mantığını içerir.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any, Union


class ModelValidationError(Exception):
    """Model veri doğrulaması başarısız olduğunda fırlatılan özel istisna."""
    pass


class UserNotFoundError(Exception):
    """İstenen kullanıcı bulunamadığında fırlatılan özel istisna."""
    pass


def parse_date_value(val: Union[str, date, datetime, None]) -> Optional[date]:
    """
    Farklı tiplerdeki tarih girdilerini (str, date, datetime) standart date objesine dönüştürür.
    Desteklenen formatlar: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY
    """
    if val is None or val == "":
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val

    val_str = str(val).strip()
    formats = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y")
    for fmt in formats:
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            continue

    raise ModelValidationError(
        f"Geçersiz tarih formatı: '{val}'. Lütfen 'YYYY-AA-GG' (Örn: 2000-01-15) formatında giriniz."
    )


@dataclass
class User:
    """
    Veritabanından bağımsız saf Python User Domain Modeli.

    Alanlar:
        id (int): Benzersiz kullanıcı kimliği
        name (str): Kullanıcı adı ve soyadı
        birth_date (date): Doğum tarihi
        city (str): Yaşadığı / bulunduğu şehir
        school (str): Mezun olduğu veya okuduğu okul
        created_at (datetime): Kayıt oluşturulma zamanı
    """
    id: Optional[int] = None
    name: str = ""
    birth_date: Optional[date] = None
    city: str = ""
    school: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Model ilklendirildikten sonra alan tiplerini ve zorunluluklarını doğrular."""
        if isinstance(self.birth_date, str):
            self.birth_date = parse_date_value(self.birth_date)

    def validate(self, is_partial: bool = False) -> None:
        """
        Model alanlarının geçerliliğini denetler.

        Args:
            is_partial (bool): Kısmi güncelleme (PATCH) ise sadece dolu alanları denetler.
        """
        if not is_partial:
            if not self.name or not str(self.name).strip():
                raise ModelValidationError("Kullanıcı adı ('name') boş bırakılamaz.")
            if not self.birth_date:
                raise ModelValidationError("Doğum tarihi ('birth_date') boş bırakılamaz.")
            if not self.city or not str(self.city).strip():
                raise ModelValidationError("Şehir ('city') boş bırakılamaz.")
            if not self.school or not str(self.school).strip():
                raise ModelValidationError("Okul ('school') boş bırakılamaz.")

        if self.name is not None and len(str(self.name).strip()) < 2:
            raise ModelValidationError("Kullanıcı adı en az 2 karakter olmalıdır.")

    def to_dict(self) -> Dict[str, Any]:
        """
        Modeli JSON serileştirmeye ve API çıktılarına uygun Python sözlüğüne dönüştürür.
        Hem İngilizce hem Türkçe anahtarları destekler.
        """
        bdate_str = self.birth_date.strftime("%Y-%m-%d") if self.birth_date else None
        created_str = self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None

        return {
            "id": self.id,
            "name": self.name,
            "isim": self.name,
            "birth_date": bdate_str,
            "dogum_tarihi": bdate_str,
            "city": self.city,
            "sehir": self.city,
            "school": self.school,
            "okul": self.school,
            "created_at": created_str,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], user_id: Optional[int] = None) -> "User":
        """
        Python sözlüğünden (dict) User nesnesi oluşturur.
        Hem İngilizce ('name', 'birth_date', 'city', 'school')
        hem de Türkçe ('isim', 'dogum_tarihi', 'sehir', 'okul') anahtarlarını destekler.
        """
        name = str(data.get("name") or data.get("isim") or "").strip()
        raw_bdate = data.get("birth_date") or data.get("dogum_tarihi")
        city = str(data.get("city") or data.get("sehir") or data.get("şehir") or "").strip()
        school = str(data.get("school") or data.get("okul") or "").strip()
        target_id = user_id or data.get("id") or data.get("user_id")

        parsed_bdate = parse_date_value(raw_bdate) if raw_bdate else None

        user = cls(
            id=int(target_id) if target_id is not None else None,
            name=name,
            birth_date=parsed_bdate,
            city=city,
            school=school,
        )
        return user

    def __repr__(self) -> str:
        bdate_str = self.birth_date.strftime("%Y-%m-%d") if self.birth_date else "None"
        return f"<User id={self.id} name='{self.name}' school='{self.school}' birth_date='{bdate_str}'>"
