from django.db import models


class UserProfile(models.Model):
    """
    Alumni Portal kullanıcı kayıt modeli.
    İsim, doğum tarihi, şehir ve okul bilgilerini saklar.
    """
    name = models.CharField(max_length=150, verbose_name="İsim")
    birth_date = models.DateField(verbose_name="Doğum Tarihi")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    school = models.CharField(max_length=200, verbose_name="Okul")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"

    def __str__(self):
        return f"{self.name} ({self.school})"

    def to_dict(self):
        date_str = self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None
        created_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        return {
            "id": self.id,
            "name": self.name,
            "isim": self.name,
            "birth_date": date_str,
            "dogum_tarihi": date_str,
            "city": self.city,
            "sehir": self.city,
            "school": self.school,
            "okul": self.school,
            "created_at": created_str,
        }


class Announcement(models.Model):
    """
    Alumni Portal Duyuru modeli (Django ORM).
    Başlık, içerik, yayınlayan birim/yazar, kategori ve aktiflik durumunu saklar.
    """
    title = models.CharField(max_length=200, verbose_name="Duyuru Başlığı")
    content = models.TextField(verbose_name="Duyuru İçeriği")
    author = models.CharField(max_length=100, default="Mezunlar Koordinatörlüğü", verbose_name="Yayınlayan")
    category = models.CharField(max_length=50, default="Genel", db_index=True, verbose_name="Kategori")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Yayında mı?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Zamanı")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Duyuru"
        verbose_name_plural = "Duyurular"

    def __str__(self):
        return f"{self.title} ({self.category})"

    def to_dict(self):
        """
        Duyuru modelini hem Türkçe hem İngilizce JSON sözlüğüne dönüştürür.
        Mevcut API ve in-memory arayüzü ile %100 uyumludur.
        """
        created_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        return {
            "id": self.id,
            "title": self.title,
            "baslik": self.title,
            "content": self.content,
            "icerik": self.content,
            "author": self.author,
            "yazar": self.author,
            "category": self.category,
            "kategori": self.category,
            "is_active": self.is_active,
            "aktif_mi": self.is_active,
            "created_at": created_str,
        }

