from django.db import models
from django.utils import timezone


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


class JobPosting(models.Model):
    """
    Alumni Portal İş ve Staj İlanı Modeli (Django ORM).
    Mezunlar veya yöneticiler tarafından paylaşılan kariyer fırsatlarını yönetir.
    Çift dilli JSON sözlüğü (TR/EN) ve zengin filtreleme yeteneklerini destekler.
    """
    EMPLOYMENT_TYPES = [
        ('FULL_TIME', 'Tam Zamanlı'),
        ('PART_TIME', 'Yarı Zamanlı'),
        ('INTERNSHIP', 'Stajyer'),
        ('REMOTE', 'Uzaktan / Remote'),
        ('HYBRID', 'Hibrit'),
        ('CONTRACT', 'Sözleşmeli / Proje Bazlı'),
    ]

    poster = models.ForeignKey(
        'UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='job_postings',
        verbose_name="İlanı Veren Mezun/Yetkili"
    )
    title = models.CharField(max_length=200, db_index=True, verbose_name="Pozisyon Başlığı")
    company_name = models.CharField(max_length=150, db_index=True, verbose_name="Şirket / Kurum Adı")
    description = models.TextField(verbose_name="İş Tanımı ve Aranan Nitelikler")
    employment_type = models.CharField(
        max_length=50,
        choices=EMPLOYMENT_TYPES,
        default='FULL_TIME',
        db_index=True,
        verbose_name="Çalışma Şekli"
    )
    location = models.CharField(max_length=100, db_index=True, verbose_name="Lokasyon / Şehir")
    salary_range = models.CharField(max_length=100, blank=True, null=True, verbose_name="Maaş Skalası")
    contact_email = models.EmailField(max_length=100, verbose_name="İletişim / Başvuru E-postası")
    application_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="Harici Başvuru URL")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Yayında mı?")
    deadline = models.DateField(blank=True, null=True, db_index=True, verbose_name="Son Başvuru Tarihi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme Tarihi")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "İş / Staj İlanı"
        verbose_name_plural = "İş / Staj İlanları"
        indexes = [
            models.Index(fields=['is_active', '-created_at'], name='core_job_active_created_idx'),
            models.Index(fields=['employment_type', 'is_active'], name='core_job_type_active_idx'),
            models.Index(fields=['location', 'is_active'], name='core_job_loc_active_idx'),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company_name} ({self.get_employment_type_display()})"

    @property
    def is_expired(self) -> bool:
        """İlanın son başvuru tarihinin geçip geçmediğini kontrol eder."""
        if self.deadline:
            return self.deadline < timezone.now().date()
        return False

    def to_dict(self):
        """
        Model örneğini hem Türkçe hem İngilizce alias destekli JSON sözlüğüne dönüştürür.
        Clean MVC / API standartları ile tam uyumludur.
        """
        deadline_str = self.deadline.strftime('%Y-%m-%d') if self.deadline else None
        created_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        updated_str = self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None

        return {
            "id": self.id,
            "poster_id": self.poster_id,
            "ilan_sahibi_id": self.poster_id,
            "title": self.title,
            "baslik": self.title,
            "is_basligi": self.title,
            "company_name": self.company_name,
            "sirket": self.company_name,
            "sirket_adi": self.company_name,
            "description": self.description,
            "aciklama": self.description,
            "is_tanimi": self.description,
            "employment_type": self.employment_type,
            "employment_type_display": self.get_employment_type_display(),
            "is_tipi": self.employment_type,
            "calisma_sekli": self.get_employment_type_display(),
            "location": self.location,
            "konum": self.location,
            "sehir": self.location,
            "salary_range": self.salary_range,
            "maas_araligi": self.salary_range,
            "contact_email": self.contact_email,
            "iletisim_eposta": self.contact_email,
            "email": self.contact_email,
            "application_url": self.application_url,
            "basvuru_linki": self.application_url,
            "is_active": self.is_active,
            "aktif_mi": self.is_active,
            "yayinda_mi": self.is_active,
            "deadline": deadline_str,
            "son_basvuru_tarihi": deadline_str,
            "is_expired": self.is_expired,
            "suresi_doldu_mu": self.is_expired,
            "created_at": created_str,
            "olusturulma_tarihi": created_str,
            "updated_at": updated_str,
            "guncellenme_tarihi": updated_str,
        }


class Application(models.Model):
    """
    Alumni Portal İş ve Staj Başvurusu Modeli (Django ORM).
    Mezun ve öğrencilerin ilanlara yaptığı başvuruları saklar.
    Mükerrer başvuru engelleme (unique_together) ve durum takibi içerir.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Beklemede'),
        ('IN_REVIEW', 'İncelemede'),
        ('ACCEPTED', 'Kabul Edildi'),
        ('REJECTED', 'Reddedildi'),
        ('WITHDRAWN', 'Geri Çekildi'),
    ]

    job = models.ForeignKey(
        'JobPosting',
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="İş İlanı"
    )
    applicant = models.ForeignKey(
        'UserProfile',
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Başvuran Mezun/Öğrenci"
    )
    cover_letter = models.TextField(blank=True, default="", verbose_name="Ön Yazı / Motivasyon")
    resume_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="Özgeçmiş / CV Linki")
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        verbose_name="Başvuru Durumu"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Başvuru Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme Tarihi")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "İş / Staj Başvurusu"
        verbose_name_plural = "İş / Staj Başvuruları"
        unique_together = [('job', 'applicant')]
        indexes = [
            models.Index(fields=['status', '-created_at'], name='core_app_status_created_idx'),
            models.Index(fields=['job', 'status'], name='core_app_job_status_idx'),
            models.Index(fields=['applicant', 'status'], name='core_app_user_status_idx'),
        ]

    def __str__(self):
        applicant_name = self.applicant.name if self.applicant_id else "Anonim"
        job_title = self.job.title if self.job_id else "İlan"
        return f"{applicant_name} -> {job_title} ({self.get_status_display()})"

    def to_dict(self):
        """
        Model örneğini hem Türkçe hem İngilizce alias destekli JSON sözlüğüne dönüştürür.
        Clean MVC / API standartları ile tam uyumludur.
        """
        created_str = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        updated_str = self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None

        job_title = None
        company_name = None
        if self.job_id:
            try:
                job_title = self.job.title
                company_name = self.job.company_name
            except Exception:
                pass

        applicant_name = None
        if self.applicant_id:
            try:
                applicant_name = self.applicant.name
            except Exception:
                pass

        return {
            "id": self.id,
            "job_id": self.job_id,
            "ilan_id": self.job_id,
            "job_title": job_title,
            "is_basligi": job_title,
            "ilan_basligi": job_title,
            "company_name": company_name,
            "sirket": company_name,
            "applicant_id": self.applicant_id,
            "basvuran_id": self.applicant_id,
            "applicant_name": applicant_name,
            "basvuran_isim": applicant_name,
            "basvuran_adi": applicant_name,
            "cover_letter": self.cover_letter,
            "on_yazi": self.cover_letter,
            "resume_url": self.resume_url,
            "cv_linki": self.resume_url,
            "status": self.status,
            "status_display": self.get_status_display(),
            "durum": self.status,
            "durum_aciklama": self.get_status_display(),
            "created_at": created_str,
            "basvuru_tarihi": created_str,
            "updated_at": updated_str,
            "guncellenme_tarihi": updated_str,
        }

