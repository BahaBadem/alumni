"""
core/database/data_pools.py - Zengin ve Gerçekçi Türkçe Veri Havuzları

Harici kütüphane bağımlılığı (Faker vb.) olmaksızın saf Python ile
Alumni Portal modelleri için gerçekçi test ve tohum (seed) verileri üretir.
"""

import random
from datetime import date, timedelta
from typing import Tuple, List, Dict

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
