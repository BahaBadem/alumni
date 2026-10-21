"""
core/database/data_pools.py - Zengin ve Gerçekçi Türkçe Veri Havuzları

Harici kütüphane bağımlılığı (Faker vb.) olmaksızın saf Python ile
Alumni Portal modelleri için gerçekçi test ve tohum (seed) verileri üretir.
"""

import random
from datetime import date, timedelta
from typing import Tuple, List, Dict, Any

# ==============================================================================
# 1. KULLANICI / PROFİL VERİ HAVUZLARI
# ==============================================================================

FIRST_NAMES: Tuple[str, ...] = (
    "Ahmet", "Mehmet", "Mustafa", "Ali", "Baha", "Burak", "Emre", "Can",
    "Kerem", "Deniz", "Eren", "Kaan", "Oğuz", "Barış", "Umut", "Volkan",
    "Zeynep", "Elif", "Merve", "Selin", "Ayşe", "Fatma", "Büşra", "İrem",
    "Gamze", "Ece", "Ceren", "Derya", "Melis", "Damla", "Ezgi", "Buket",
    "Seda", "Gözde", "Cansu", "Nazlı", "Pınar", "Eylül", "Tuğba", "Hande"
)

LAST_NAMES: Tuple[str, ...] = (
    "Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım",
    "Öztürk", "Aydın", "Özdemir", "Arslan", "Doğan", "Kılıç", "Aslan",
    "Çetin", "Kara", "Koç", "Kurt", "Özkan", "Şimşek", "Polat", "Erdoğan",
    "Aksoy", "Korkmaz", "Güler", "Yalçın", "Güneş", "Bozkurt", "Ünal",
    "Keskin", "Özer", "Turan", "Yüksel", "Avcı", "Taş", "Tekin", "Coşkun"
)

CITIES: Tuple[str, ...] = (
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Eskişehir",
    "Trabzon", "Konya", "Kocaeli", "Adana", "Gaziantep", "Samsun",
    "Muğla", "Tekirdağ", "Kayseri", "Denizli", "Sakarya", "Mersin",
    "Çanakkale", "Aydın", "Diyarbakır", "Erzurum", "Balıkesir", "Manisa"
)

SCHOOLS: Tuple[str, ...] = (
    "İstanbul Teknik Üniversitesi",
    "Orta Doğu Teknik Üniversitesi",
    "Boğaziçi Üniversitesi",
    "Yıldız Teknik Üniversitesi",
    "Hacettepe Üniversitesi",
    "Ankara Üniversitesi",
    "Ege Üniversitesi",
    "Marmara Üniversitesi",
    "Gazi Üniversitesi",
    "Dokuz Eylül Üniversitesi",
    "Gebze Teknik Üniversitesi",
    "İhsan Doğramacı Bilkent Üniversitesi",
    "Koç Üniversitesi",
    "Sabancı Üniversitesi",
    "TOBB Ekonomi ve Teknoloji Üniversitesi",
    "İstanbul Üniversitesi",
    "Galatasaray Üniversitesi",
    "Çukurova Üniversitesi",
    "Karadeniz Teknik Üniversitesi",
    "Eskişehir Osmangazi Üniversitesi"
)

# ==============================================================================
# 2. DUYURU (ANNOUNCEMENT) VERİ HAVUZLARI
# ==============================================================================

ANNOUNCEMENT_AUTHORS: Tuple[str, ...] = (
    "Mezunlar Koordinatörlüğü",
    "Rektörlük",
    "Kariyer Planlama ve Mezunlar Merkezi",
    "Öğrenci İşleri Daire Başkanlığı",
    "Mühendislik Fakültesi Dekanlığı",
    "Bilgi İşlem Daire Başkanlığı",
    "Alumni Vakfı & Mezunlar Derneği",
    "Uluslararası İlişkiler Ofisi",
    "Teknoloji Transfer Ofisi (TTO)"
)

ANNOUNCEMENT_CATEGORIES: Tuple[str, ...] = (
    "Genel",
    "Kariyer",
    "Etkinlik",
    "Mezun Buluşması",
    "Burs & Staj",
    "Akademi & Araştırma",
    "Sosyal Sorumluluk"
)

# Gerçekçi kurumsal duyuru içerik şablonları (Başlık, Kategori, İçerik, Yazar)
SEED_ANNOUNCEMENT_TEMPLATES: List[Dict[str, str]] = [
    {
        "title": "2026 Geleneksel Mezunlar Günü ve Pilav Şenliği",
        "category": "Mezun Buluşması",
        "author": "Mezunlar Koordinatörlüğü",
        "content": (
            "Sevgili Mezunlarımız, bu yıl 25.sini düzenleyeceğimiz Geleneksel Mezunlar Günü "
            "ve Pilav Şenliği, 24 Mayıs Pazar günü üniversitemiz Merkez Kampüsü'nde gerçekleştirilecektir. "
            "Tüm dönem mezunlarımızı, ailelerini ve kıymetli hocalarımızı aramızda görmekten onur duyarız. "
            "Kayıt ve katılım rozetleri için lütfen profilinizi güncelleyiniz."
        ),
    },
    {
        "title": "Global Teknoloji Şirketleri ile İlkbahar Staj & İş Fırsatları",
        "category": "Kariyer",
        "author": "Kariyer Planlama ve Mezunlar Merkezi",
        "content": (
            "Mezunlarımız ve son sınıf öğrencilerimiz için hazırlanan 2026 İlkbahar Kariyer Zirvesi kapsamında, "
            "yurtiçi ve yurtdışı 40'tan fazla lider teknoloji firması doğrudan başvuru kabul etmektedir. "
            "Yazılım geliştirme, veri bilimi ve ürün yönetimi pozisyonları için portalımız üzerinden özgeçmişinizi iletebilirsiniz."
        ),
    },
    {
        "title": "Mezun-Öğrenci Mentorluk Programı 4. Dönem Başvuruları Başladı",
        "category": "Burs & Staj",
        "author": "Alumni Vakfı & Mezunlar Derneği",
        "content": (
            "Sektörde tecrübe kazanmış değerli mezunlarımız ile geleceğe adım atan lisans öğrencilerimizi buluşturan "
            "Mentorluk Programımızın yeni dönemi açılmıştır. Ayda en az 2 görüşme taahhüdü ile genç meslektaşlarınıza "
            "rehberlik etmek isteyen tüm mezunlarımızın başvurularını bekliyoruz."
        ),
    },
    {
        "title": "Mezun Bilgi ve İletişim Sistemi (Alumni Portal) v2.0 Yayında!",
        "category": "Genel",
        "author": "Bilgi İşlem Daire Başkanlığı",
        "content": (
            "Üniversitemiz Mezun Bilgi Sistemi modern mimari, REST API altyapısı ve yenilenen arayüzü ile hizmete girmiştir. "
            "Kişisel bilgilerinizi kontrol ederek eksik alanlarınızı tamamlamanızı rica ederiz. İletişim kopukluklarını önlemek "
            "adına e-posta ve telefon bilgilerinizi güncel tutunuz."
        ),
    },
    {
        "title": "Girişimci Mezunlar Zirvesi ve Melek Yatırımcı Buluşması",
        "category": "Etkinlik",
        "author": "Teknoloji Transfer Ofisi (TTO)",
        "content": (
            "Kendi girişimini kurmuş veya start-up ekosisteminde yer alan mezunlarımız, 12 Kasım günü Teknokent Konferans "
            "Salonu'nda melek yatırımcı ağları ve risk sermayesi temsilcileri ile buluşuyor. Proje sunumları ve networking seansı "
            "için sınırlı kontenjan açılmıştır."
        ),
    },
    {
        "title": "Yurtdışı Yüksek Lisans ve Doktora Bursları Bilgilendirme Semineri",
        "category": "Akademi & Araştırma",
        "author": "Uluslararası İlişkiler Ofisi",
        "content": (
            "Fulbright, Jean Monnet ve DAAD başta olmak üzere uluslararası lisansüstü burs programları hakkında mezunlarımıza "
            "yönelik çevrimiçi seminer düzenlenecektir. Başvuru süreci, niyet mektubu hazırlığı ve referans şartları detaylandırılacaktır."
        ),
    },
]

# ==============================================================================
# 3. YARDIMCI VERİ ÜRETİCİLERİ
# ==============================================================================

def get_random_name() -> str:
    """Rastgele gerçekçi ad ve soyad üretir."""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def get_random_city() -> str:
    """Rastgele bir şehir seçer."""
    return random.choice(CITIES)


def get_random_school() -> str:
    """Rastgele bir üniversite seçer."""
    return random.choice(SCHOOLS)


def get_random_birth_date(min_age: int = 21, max_age: int = 55) -> date:
    """
    Belirli yaş aralığında rastgele mantıklı bir doğum tarihi üretir.
    """
    today = date.today()
    start_date = today - timedelta(days=max_age * 365)
    end_date = today - timedelta(days=min_age * 365)
    
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(max(1, days_between_dates))
    
    return start_date + timedelta(days=random_number_of_days)


def get_random_announcement_author() -> str:
    """Rastgele bir duyuru yayıncısı seçer."""
    return random.choice(ANNOUNCEMENT_AUTHORS)


def get_random_announcement_category() -> str:
    """Rastgele bir duyuru kategorisi seçer."""
    return random.choice(ANNOUNCEMENT_CATEGORIES)


# ==============================================================================
# 4. İŞ & STAJ İLANI (JOB POSTING) VERİ HAVUZLARI
# ==============================================================================

COMPANIES: Tuple[str, ...] = (
    "Trendyol Tech", "Getir", "Hepsiburada", "Baykar Teknoloji", "Aselsan",
    "Havelsan", "Turkcell Teknoloji", "Vodafone Türkiye", "Garanti BBVA Teknoloji",
    "Akbank LAB", "Yapı Kredi Teknoloji", "Insider", "Dream Games", "Peak Games",
    "Yemeksepeti", "Logo Yazılım", "Softtech", "TUSAŞ (TAI)", "Papara", "Midas",
    "Amazon Web Services (AWS)", "Microsoft Türkiye", "Google Cloud TR", "Siemens Türkiye"
)

JOB_TITLES: Tuple[str, ...] = (
    "Kıdemli Backend Geliştirici (Python / Django)",
    "Full Stack Yazılım Mühendisi (React & Node.js)",
    "Frontend Geliştirici (Vue.js / TypeScript)",
    "Mobil Uygulama Geliştiricisi (Flutter & iOS)",
    "Yapay Zeka ve Büyük Dil Modeli (LLM) Mühendisi",
    "Veri Mühendisi & Veri Ambarı Mimarı",
    "DevOps & Bulut Altyapı Mühendisi (AWS / Kubernetes)",
    "Siber Güvenlik Uzmanı & Sızma Testi Analisti",
    "Yazılım Test Otomasyon Mühendisi (QA)",
    "Teknik Ürün Yöneticisi (Technical Product Manager)",
    "Yazılım Mühendisliği Yaz Stajyeri (2026)",
    "Veri Bilimi ve Analitik Stajyeri (Uzaktan)",
    "UI/UX Ürün Tasarımcısı",
    "Sistem ve Ağ Güvenliği Yöneticisi",
    "Veritabanı Yöneticisi (PostgreSQL / Redis DBA)"
)

SALARY_RANGES: Tuple[str, ...] = (
    "60.000 TL - 85.000 TL",
    "80.000 TL - 110.000 TL",
    "100.000 TL - 140.000 TL",
    "130.000 TL - 180.000 TL",
    "160.000 TL - 220.000 TL",
    "Asgari Ücret + Yol + Yemek (Stajyer)",
    "Mülakat Aşamasında Belirlenecektir"
)

LOCATIONS: Tuple[str, ...] = (
    "İstanbul (Hibrit)", "İstanbul (Maslak)", "İstanbul (Kadıköy)",
    "Ankara (ODTÜ Teknokent)", "Ankara (Bilkent Cyberpark)",
    "İzmir (Urla İYTE Teknopark)", "Tamamen Uzaktan (Remote - Türkiye Geneli)",
    "Hibrit (Haftada 2 Gün Ofis)", "Bursa (Görükle Teknoloji Bölgesi)"
)

SEED_JOB_TEMPLATES: List[Dict[str, Any]] = [
    {
        "title": "Kıdemli Backend Geliştirici (Python / Django)",
        "company_name": "Trendyol Tech",
        "description": (
            "Trendyol bünyesinde yüksek trafikli mikroservis mimarilerini yönetecek, "
            "Python, Django, FastAPI ve PostgreSQL konusunda deneyimli, mesajlaşma kuyrukları "
            "(Kafka / RabbitMQ) ile çalışmış takım arkadaşı arıyoruz. Docker ve Kubernetes bilgisi artıdır."
        ),
        "employment_type": "FULL_TIME",
        "location": "İstanbul (Hibrit)",
        "salary_range": "130.000 TL - 180.000 TL",
        "contact_email": "tech-recruitment@trendyol.com",
        "application_url": "https://trendyol.com/careers/backend-senior",
        "deadline_days": 45,
        "is_active": True,
    },
    {
        "title": "Full Stack Yazılım Mühendisi",
        "company_name": "Getir",
        "description": (
            "Getir teknoloji ekibinde kurye ve depo lojistik operasyon panellerinin geliştirilmesinde "
            "React, TypeScript, Node.js ve Go teknolojilerini kullanacak çevik yazılımcılar arıyoruz. "
            "CI/CD süreçleri ve AWS ortamlarında tecrübe tercih sebebidir."
        ),
        "employment_type": "HYBRID",
        "location": "İstanbul (Levent)",
        "salary_range": "100.000 TL - 140.000 TL",
        "contact_email": "talent@getir.com",
        "application_url": "https://getir.com/careers/fullstack",
        "deadline_days": 30,
        "is_active": True,
    },
    {
        "title": "Yapay Zeka ve Makine Öğrenimi Araştırmacısı",
        "company_name": "Baykar Teknoloji",
        "description": (
            "Milli havacılık ve insansız hava araçları projelerimizde otonom algılama, "
            "görüntü işleme ve derin öğrenme algoritmaları geliştirecek; PyTorch, OpenCV, CUDA "
            "ve C++ konularında güçlü araştırmacı mühendisler arıyoruz."
        ),
        "employment_type": "FULL_TIME",
        "location": "İstanbul (Özdemir Bayraktar MP)",
        "salary_range": "150.000 TL - 220.000 TL",
        "contact_email": "kariyer@baykartech.com",
        "application_url": "https://baykartech.com/tr/kariyer",
        "deadline_days": 60,
        "is_active": True,
    },
    {
        "title": "Yazılım Mühendisliği Yaz Stajyeri (2026)",
        "company_name": "Aselsan",
        "description": (
            "Üniversitelerin Bilgisayar, Elektrik-Elektronik veya Yazılım Mühendisliği bölümlerinde "
            "3. veya 4. sınıfa geçen lisans öğrencileri için Aselsan AR-GE merkezlerinde "
            "gerçek projelerde görev alacak yaz dönemi stajyerleri alınacaktır."
        ),
        "employment_type": "INTERNSHIP",
        "location": "Ankara (Macunköy)",
        "salary_range": "Asgari Ücret + Servis + Yemek",
        "contact_email": "staj@aselsan.com.tr",
        "application_url": "https://aselsan.com/tr/kariyer/staj-programi",
        "deadline_days": 20,
        "is_active": True,
    },
    {
        "title": "DevOps & Bulut Altyapı Mühendisi",
        "company_name": "Insider",
        "description": (
            "Global ölçekte milyarlarca kullanıcı etkileşimini işleyen çoklu bulut (Multi-Cloud AWS & GCP) "
            "altyapımızın yönetiminde Terraform, Kubernetes, Helm ve Prometheus kullanarak "
            "otomasyon sağlayacak DevOps mühendisi arayışımız mevcuttur."
        ),
        "employment_type": "REMOTE",
        "location": "Tamamen Uzaktan (Remote - Türkiye Geneli)",
        "salary_range": "120.000 TL - 160.000 TL",
        "contact_email": "devops-hiring@useinsider.com",
        "application_url": "https://useinsider.com/careers",
        "deadline_days": 35,
        "is_active": True,
    },
    {
        "title": "Mobil Oyun Geliştiricisi (Unity / C#)",
        "company_name": "Dream Games",
        "description": (
            "Milyonlarca oyuncunun beğenisini kazanan bulmaca oyunlarımız için Unity oyun motoru, "
            "C#, shader optimizasyonu ve oyun mekaniği tasarımı alanlarında yetenekli "
            "yazılımcılar arıyoruz. Yüksek performanslı mobil oyun kodlama deneyimi esastır."
        ),
        "employment_type": "FULL_TIME",
        "location": "İstanbul (Levent)",
        "salary_range": "140.000 TL - 200.000 TL",
        "contact_email": "jobs@dreamgames.com",
        "application_url": "https://dreamgames.com/careers",
        "deadline_days": 50,
        "is_active": True,
    },
    {
        "title": "Fintek Frontend Uzmanı (React & Tailwind)",
        "company_name": "Papara",
        "description": (
            "Papara web ve webview platformlarında kusursuz kullanıcı deneyimleri inşa edecek, "
            "React 19, Next.js, Redux Toolkit ve Tailwind CSS ile mikro-frontend mimarileri geliştirecek "
            "Frontend geliştiricileri davet ediyoruz."
        ),
        "employment_type": "HYBRID",
        "location": "İstanbul (Üsküdar)",
        "salary_range": "90.000 TL - 130.000 TL",
        "contact_email": "kariyer@papara.com",
        "application_url": "https://papara.com/kariyer",
        "deadline_days": 25,
        "is_active": True,
    },
    {
        "title": "Büyük Veri & Data Platform Stajyeri",
        "company_name": "Turkcell Teknoloji",
        "description": (
            "Milyonlarca abonenin veri akışını yöneten veri platformlarımızda Spark, Hadoop, Kafka "
            "ve SQL sorgulamaları üzerine kendini geliştirmek isteyen yeni mezun veya son sınıf "
            "öğrencileri için uzun dönemli staj fırsatı."
        ),
        "employment_type": "INTERNSHIP",
        "location": "İstanbul (Küçükyalı)",
        "salary_range": "Asgari Ücret + Yol + Yemek",
        "contact_email": "genc-yetenek@turkcell.com.tr",
        "application_url": "https://turkcell.com.tr/genc-yetenek",
        "deadline_days": 15,
        "is_active": True,
    }
]


def get_random_company() -> str:
    """Rastgele kurumsal bir şirket adı seçer."""
    return random.choice(COMPANIES)


def get_random_job_title() -> str:
    """Rastgele bir pozisyon başlığı seçer."""
    return random.choice(JOB_TITLES)


def get_random_employment_type() -> str:
    """Rastgele bir istihdam türü seçer."""
    types = ("FULL_TIME", "PART_TIME", "INTERNSHIP", "REMOTE", "HYBRID", "CONTRACT")
    return random.choice(types)


def get_random_salary_range() -> str:
    """Rastgele bir maaş aralığı seçer."""
    return random.choice(SALARY_RANGES)


def get_random_location() -> str:
    """Rastgele bir iş konumu seçer."""
    return random.choice(LOCATIONS)


def get_random_future_deadline(min_days: int = 10, max_days: int = 90) -> date:
    """Gelecekte geçerli bir son başvuru tarihi üretir."""
    days = random.randint(min_days, max_days)
    return date.today() + timedelta(days=days)

