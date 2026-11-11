# 🎓 Alumni Portal (Alumni Management System)

[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-6.1%2B-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-SQLite3%20%7C%20PostgreSQL%2016-003B57.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Container-Docker%20%26%20Compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![API Spec](https://img.shields.io/badge/OpenAPI-3.0.0-85EA2D.svg?logo=openapi-initiative&logoColor=black)](./swagger.json)
[![DDD Spec](https://img.shields.io/badge/Architecture-Domain--Driven%20Design%20(DDD)-7c3aed.svg)](./ddd.md)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(116%2F116)-brightgreen.svg)](#-test-ve-kalite-güvencesi)

> **Web Programlama (Web Programming)** dersi kapsamında geliştirilen; mezunlar, öğrenciler ve üniversite yönetimi arasında köprü kurmayı hedefleyen modern, modüler, veritabanı destekli ve yüksek standartlı bir **Mezun Yönetim Portalı** (Alumni Management Platform).

---

## 📌 İçindekiler

- [📖 Proje Hakkında ve Vizyon](#-proje-hakkında-ve-vizyon)
- [🏛️ Mimari Tasarım: Django MVT'den Temiz MVC'ye](#-mimari-tasarım-django-mvtden-temiz-mvcyeye)
  - [Sorumlulukların Ayrımı (Separation of Concerns - SoC)](#sorumlulukların-ayrımı-separation-of-concerns---soc)
  - [Katmanlı Mimari Şeması](#katmanlı-mimari-şeması)
- [📂 Proje Dizin Yapısı](#-proje-dizin-yapısı)
- [🛠️ Teknoloji Yığını](#️-teknoloji-yığını)
- [✨ Temel Özellikler](#-temel-özellikler)
  - [İş İlanı Alan Kuralları](#iş-ilanı-alan-kuralları)
- [🚦 Gerçekleştirilen Rotalar ve API Kataloğu](#-gerçekleştirilen-rotalar-ve-api-kataloğu)
  - [Web Kullanıcı Arayüzü Rotaları](#-web-kullanıcı-arayüzü-rotaları)
  - [REST API Uç Noktaları](#-rest-api-uç-noktaları)
- [🌱 Database Factory ve Idempotent Seeder Mimarisi](#-database-factory-ve-idempotent-seeder-mimarisi)
- [🐳 Docker ve Konteynerizasyon Altyapısı](#-docker-ve-konteynerizasyon-altyapısı)
- [🔐 Ortam Değişkenleri ve Güvenlik Önlemleri](#-ortam-değişkenleri-ve-güvenlik-önlemleri)
- [📐 Domain-Driven Database Design (`ddd.md`) Sözleşmesi](#-domain-driven-database-design-dddmd-sözleşmesi)
- [📄 Swagger / OpenAPI 3.0 Dokümantasyonu](#-swagger--openapi-30-dokümantasyonu)
- [💻 Yerel Kurulum ve Çalıştırma (Local Development)](#-yerel-kurulum-ve-çalıştırma-local-development)
- [Hata Yanıtları ve İstek Kayıtları](#hata-yanıtları-ve-istek-kayıtları)
- [🧪 Test ve Kalite Güvencesi](#-test-ve-kalite-güvencesi)
- [🧭 Geliştirici Kılavuzu ve Kod Standartları](#-geliştirici-kılavuzu-ve-kod-standartları)
- [🗺️ Yol Haritası (Roadmap)](#️-yol-haritası-roadmap)

---

## 📖 Proje Hakkında ve Vizyon

**Alumni Portal**, üniversite mezunlarının kariyer gelişimlerini desteklemek, mevcut öğrenciler ile mezunlar arasında mentorluk köprüleri kurmak, üniversite etkinlik ve duyurularını tek bir çatı altında toplamak amacıyla geliştirilmektedir.

Projede **Domain-Driven Design (DDD)** ilkeleri, **Temiz MVC mimarisi**, **kalıcı ilişkisel veritabanı (SQLite & PostgreSQL)**, **idempotent seeder altyapısı** ve **otomasyon testleri** esastır.

---

## 🏛️ Mimari Tasarım: Django MVT'den Temiz MVC'ye

Geleneksel Django projeleri `views.py` dosyalarında aşırı kod birikmesine (*Fat Views anti-pattern*) yol açabilir. Projemizde kurumsal standartlarda **Temiz MVC (Model-View-Controller)** ve **Servis Katmanı (Service Layer)** uygulanmıştır:

```mermaid
flowchart TD
    subgraph ClientLayer ["1. İstemci Katmanı (Client Layer)"]
        Browser["Tarayıcı (Web Arayüzü)"]
        ApiClient["REST İstemcisi (Mobil / Swagger / Postman)"]
    end

    subgraph ControllerLayer ["2. Controller / Yönlendirme Katmanı"]
        Urls["URL Router (core/urls.py)"]
        WebControllers["Web controller’ları"]
        ApiControllers["API controller’ları"]
    end

    subgraph ServiceLayer ["3. İş Mantığı / Servis Katmanı (Domain Logic)"]
        UserServices["User Services (core/user.py & in-memory)"]
        DomainServices["Duyuru, ilan ve başvuru servisleri (core/services/)"]
    end

    subgraph ModelLayer ["4. Model / Veri Katmanı (Data Access Layer)"]
        ORMModels["Django ORM (UserProfile, Announcement, JobPosting, Application)"]
        Database[("Veritabanı: SQLite3 / PostgreSQL 16")]
        Factories["Factories & Seeders (core/database/)"]
    end

    subgraph PresentationLayer ["5. View / Sunum Katmanı (Presentation)"]
        Templates["HTML Şablonları (templates/*.html)"]
        Serializers["JSON DTOs & Serializers"]
    end

    Browser -->|HTTP GET/POST| Urls
    ApiClient -->|HTTP REST İstekleri| Urls

    Urls --> WebControllers
    Urls --> ApiControllers

    WebControllers -->|İş İstekleri| DomainServices
    WebControllers -->|İş İstekleri| UserServices
    ApiControllers -->|İş İstekleri| DomainServices
    ApiControllers -->|İş İstekleri| UserServices

    DomainServices -->|ORM / SQL| ORMModels
    UserServices -->|ORM / SQL| ORMModels
    Factories -.->|Veri Tohumlama| ORMModels
    ORMModels <--> Database

    WebControllers -->|Context Data| Templates
    ApiControllers -->|DTO Data| Serializers

    Templates --> Middleware["Yanıt middleware’i (404, 5xx ve istek logger’ı)"]
    Serializers --> Middleware
    Middleware -->|HTML yanıt| Browser
    Middleware -->|JSON yanıt| ApiClient
```

### Sorumlulukların Ayrımı (Separation of Concerns - SoC)

| Klasik MVC | Django Karşılığı | Projedeki Konumu | Sorumluluk ve İlkeler |
| :--- | :--- | :--- | :--- |
| **Model (M)** | Model | `core/models.py` | Kullanıcı, duyuru, iş ilanı ve başvuru modelleri ile ORM kısıtları ve indeksler. |
| **View (V)** | Template & DTO | `templates/` & JSON DTO | **Sunum Katmanı:** HTML şablonları veya REST JSON DTO yanıtlarının hazırlanması. |
| **Controller (C)** | View & Controller | `core/controllers/` | **İstek Karşılama & Orkestrasyon:** HTTP fiillerini karşılar, yetkilendirmeyi ve servis çağrılarını yönetir. |
| **Service Layer** | Business Logic | `core/services/` | **İş Mantığı (Domain):** Validasyonlar, filtreleme algoritmaları, ACID transaction yönetimi (*Skinny Controller, Rich Service*). |
| **Middleware** | Middleware | `core/middleware.py` | Web ve API hata yanıtları ile tamamlanan isteklerin kaydı. |

---

## 📂 Proje Dizin Yapısı

Standardize edilmiş proje mimarisi aşağıdaki şekilde organize edilmiştir:

```text
alumni/
├── manage.py                   # Django yönetim aracı (CLI)
├── requirements.txt            # Python bağımlılıkları (Django, psycopg2-binary vb.)
├── swagger.json                # OpenAPI 3.0 REST API spesifikasyon sözleşmesi
├── ddd.md                      # [DDD] Domain-Driven Database Design reçetesi & sözleşmesi
├── db.sqlite3                  # Yerel SQLite3 ACID veritabanı
├── db.sqlite3.backup           # Canlı veri koruma yedeği
├── logs/
│   └── error.logs              # Uygulama başlatıldığında oluşturulan yerel 5xx kayıt dosyası
├── Dockerfile                  # Container imaj tanımı (Python 3.13-slim)
├── docker-compose.yml          # Standart Docker Compose orkestrasyonu (Web + PostgreSQL)
├── docker_compose.yml          # Docker Compose alternatif alias dosyası
├── .dockerignore               # Container build context filtre kuralları
├── .env                        # [GİZLİ] Yerel ortam değişkenleri ve secret anahtarlar (chmod 600)
├── env.example                 # Ortam değişkenleri örnek şablonu
├── .example.env                # Alternatif ortam değişkenleri şablonu
├── .env.example                # Docker uyumlu ortam değişkenleri şablonu
├── .gitignore                  # Git sızıntı önleme ve dosya dışlama kuralları
├── README.md                   # Proje ana dokümantasyonu ve mimari rehber
│
├── core/                       # Çekirdek uygulama ve proje konfigürasyonu
│   ├── __init__.py
│   ├── apps.py                 # Core uygulama yapılandırması
│   ├── settings.py             # Veritabanı, middleware, logger ve güvenlik ayarları
│   ├── middleware.py           # İstek logger'ı, ortak 404 ve 5xx guardian
│   ├── urls.py                 # Merkezi rota tanımları ve URL mapping
│   ├── admin.py                # Django Admin model kayıtları
│   ├── models.py               # UserProfile, Announcement, JobPosting ve Application
│   ├── views.py                # View yönlendirmeleri ve controller köprüleri
│   │
│   ├── controllers/            # [C] CONTROLLER KATMANI (Temiz MVC)
│   │   ├── user_controller.py             # UserController: Web HTML Kullanıcı CRUD
│   │   ├── api_user_controller.py         # ApiUserController: REST API Kullanıcı CRUD
│   │   ├── announcement_controller.py     # AnnouncementController: Web HTML Duyuru CRUD (DB Connected)
│   │   ├── api_announcement_controller.py # ApiAnnouncementController: REST API Duyuru CRUD (DB Connected)
│   │   ├── job_posting_controller.py     # Web ilan yönetimi
│   │   ├── api_job_posting_controller.py # REST API ilan yönetimi
│   │   ├── application_controller.py    # Web başvuru yönetimi
│   │   ├── api_application_controller.py # REST API başvuru yönetimi
│   │   ├── user_urls.py                   # Web User rotaları
│   │   ├── api_urls.py                    # REST API User rotaları
│   │   ├── announcement_urls.py           # Web Announcement rotaları
│   │   └── api_announcement_urls.py       # REST API Announcement rotaları
│   │
│   ├── services/               # [Service Layer] VERİTABANI SERVİS KATMANI
│   │   ├── __init__.py
│   │   ├── announcement_service.py # Duyuru işlemleri
│   │   ├── job_posting_service.py  # İlan kuralları ve işlemleri
│   │   └── application_service.py  # Başvuru kuralları ve işlemleri
│   │
│   ├── database/               # [Factory & Seeder] VERİTABANI TOHUMLAMA MİMARİSİ
│   │   ├── __init__.py
│   │   ├── base.py             # BaseFactory ve BaseSeeder soyut sınıfları
│   │   ├── data_pools.py       # Zengin Türkçe isim, şehir, okul ve duyuru havuzları
│   │   ├── factories/          # Model Factories (UserProfileFactory, AnnouncementFactory)
│   │   └── seeders/            # Idempotent Seeders (User, Announcement, DatabaseSeeder)
│   │
│   ├── management/             # DJANGO CUSTOM CLI KOMUTLARI
│   │   └── commands/
│   │       └── seed.py         # `python manage.py seed` komutu
│   │
│   ├── migrations/             # Veritabanı şema göç dosyaları
│   │   ├── 0001_initial.py     # UserProfile tablosu göçü
│   │   ├── 0002_announcement.py # Announcement tablosu göçü
│   │   ├── 0003_jobposting.py   # JobPosting tablosu göçü
│   │   ├── 0004_application.py  # Application tablosu göçü
│   │   └── 0005_job_posting_field_rules.py # Başlık sınırı ve isteğe bağlı alanlar
│   │
│   └── tests.py                # Model, rota, seeder ve middleware testleri
│
├── templates/                  # [V] VIEW KATMANI: HTML Görünümleri
│   ├── index.html              # Ana karşılama sayfası ve interaktif rota paneli
│   ├── about.html              # Proje hakkında bilgilendirme sayfası
│   ├── users.html              # Kullanıcı kayıt formu ve veri tablosu
│   ├── announcements.html      # Veritabanı destekli Duyuru Yönetim Paneli
│   ├── job_postings.html       # İlan listesi, detay ve yayınlama formu
│   ├── applications.html       # Başvuru yönetimi
│   ├── 404.html                # Ortak web 404 sayfası
│   ├── server_error.html       # Ortak web 5xx sayfası
│   └── swagger.html            # Canlı Swagger UI REST API dokümantasyon konsolu
│
├── model.py                    # Saf Python User domain modeli
├── user.py                     # In-memory User CRUD servisi
├── announcement_model.py       # Saf Python Announcement domain modeli
├── announcement.py             # In-memory Announcement CRUD servisi
├── test_controllers.py         # User Controller testleri (7 test)
├── test_announcements.py       # Announcement Controller in-memory testleri (9 test)
└── test_in_memory_user.py      # In-memory User CRUD testleri (12 test)
```

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji | Açıklama |
| :--- | :--- | :--- |
| **Backend Dili** | [Python 3.12+](https://www.python.org/) | Tip güvenliği ve modern Python özellikleri |
| **Web Çatısı** | [Django 6.1+](https://www.djangoproject.com/) | Kurumsal seviye MVC web mimarisi |
| **İlişkisel Veritabanı** | [SQLite3](https://www.sqlite.org/) / [PostgreSQL 16](https://www.postgresql.org/) | Akıllı hibrit mimari: Yerelde SQLite3, Docker'da PostgreSQL |
| **Konteynerizasyon** | [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) | İzole geliştirme ortamı ve mikro servis mimarisi |
| **Tohumlama & Test Verisi**| Custom Factory & Seeder | Modüler, tip güvenli ve %100 idempotent veri üretimi |
| **API Standartı** | [OpenAPI 3.0.0](https://swagger.io/specification/) | Endüstri standardı REST API şeması |
| **API Arayüzü** | [Swagger UI](https://swagger.io/tools/swagger-ui/) | Etkileşimli API test ve dokümantasyon konsolu |
| **Frontend** | HTML5, CSS3, JavaScript | Modern, duyarlı ve kullanıcı dostu arayüzler |
| **Test Çerçevesi** | Django Test Framework (unittest) | 116 birim ve entegrasyon testi |

---

## ✨ Temel Özellikler

- **🗄️ Veritabanı Destekli Modüller**
  - Kullanıcı profilleri, duyurular, iş ilanları ve başvurular SQLite veya PostgreSQL’de saklanır.
- **🌱 Idempotent Veritabanı Seeder Mimarisi:**
  - Tekrarlı çalıştırmalarda mükerrer kayıt üretmeyen akıllı tohumlama sistemi (`python manage.py seed`).
- **🐳 Sıfır Konfigürasyonlu Docker Altyapısı:**
  - PostgreSQL 16 veritabanı, sağlık kontrolü (`healthcheck`), kalıcı volume ve canlı reload ile tek komutta hazır.
- **🔐 Kurumsal Güvenlik ve Gizlilik Standartları:**
  - Kriptografik anahtarlar, `.env` dosya izinleri (`chmod 600`), `.gitignore` ve `.dockerignore` sızıntı korumaları.
- **🧩 Çift Dilli Parametre Desteği:**
  - Hem formlarda hem API'da Türkçe (`isim`, `dogum_tarihi`, `sehir`, `okul`, `baslik`, `icerik`) ve İngilizce (`name`, `birth_date`, `city`, `school`, `title`, `content`) tam uyumluluk.
- **🛡️ Hata Yönetimi ve İstek Kayıtları**
  - Web hataları ortak 404 ve 5xx sayfalarını kullanır. API hata yanıtları JSON döner.
  - İstekler terminalde iki satırlı tabloda görünür. 5xx kayıtları `logs/error.logs` dosyasına da eklenir.

### İş İlanı Alan Kuralları

| Alan | Kural |
| :--- | :--- |
| `title` | Zorunlu, 3–120 karakter. Üst sınır veritabanında da uygulanır. |
| `company_name` | Zorunlu, en az 2 karakter. API isteklerinde `company` adı da kabul edilir. |
| `location` | İsteğe bağlı. API isteklerinde `city` adı da kabul edilir. |
| `description` | İsteğe bağlı. Girildiğinde en az 10 karakter. |
| `contact_email` | Yeni ilan ve tam güncelleme için geçerli bir e-posta adresi zorunlu. |

Web formundan yayımlanan yeni ilanlar varsayılan olarak aktiftir. Aktif ve son başvuru tarihi geçmemiş ilanlar başvuru kabul eder. `PUT` işleminde gönderilmeyen şehir ve açıklama boşaltılır. `PATCH` işleminde gönderilmeyen alanlar korunur.

---

## 🚦 Gerçekleştirilen Rotalar ve API Kataloğu

### 🌐 Web Kullanıcı Arayüzü Rotaları

| Metot | Rota | Controller / View | CRUD Operasyonu | Çıktı / Şablon |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `home` | Landing Page | `templates/index.html` |
| `GET` | `/about/` | `about` | Bilgilendirme | `templates/about.html` |
| `GET` | `/users/` | `user_list_view` | **USER READ ALL:** Kullanıcı listesi & form | `templates/users.html` |
| `POST`| `/users/create/` | `user_create_view` | **USER CREATE:** Yeni kullanıcı kaydı | `templates/users.html` (`201`) |
| `GET` | `/users/<int:user_id>/` | `user_detail_view` | **USER READ SINGLE:** Tekil kullanıcı detayı | `templates/users.html` |
| `POST`| `/users/<int:user_id>/update/` | `user_update_view` | **USER UPDATE:** Kullanıcı güncelleme | `templates/users.html` |
| `POST`| `/users/<int:user_id>/delete/` | `user_delete_view` | **USER DELETE:** Kullanıcı silme | `templates/users.html` |
| `GET` | `/announcements/` | `AnnouncementController` | **ANNOUNCEMENT READ:** Duyuru listesi & arama | `templates/announcements.html` |
| `POST`| `/announcements/create/` | `AnnouncementController` | **ANNOUNCEMENT CREATE:** Veritabanına yeni duyuru | `templates/announcements.html` (`201`) |
| `GET` | `/announcements/<int:id>/` | `AnnouncementController` | **ANNOUNCEMENT DETAIL:** Tekil duyuru detayı | `templates/announcements.html` |
| `POST`| `/announcements/<int:id>/update/` | `AnnouncementController` | **ANNOUNCEMENT UPDATE:** Duyuru güncelleme | `templates/announcements.html` |
| `POST`| `/announcements/<int:id>/delete/` | `AnnouncementController` | **ANNOUNCEMENT DELETE:** Duyuru silme | `templates/announcements.html` |
| `GET`, `POST` | `/jobs/`, `/users/<user_id>/jobs/` | `JobPostingController` | İlan listeleme ve yayımlama | `templates/job_postings.html` |
| `GET`, `POST` | `/applications/`, `/jobs/<job_id>/applications/`, `/users/<user_id>/applications/` | `ApplicationController` | Başvuru listeleme ve oluşturma | `templates/applications.html` |

### 🚀 REST API Uç Noktaları

| Metot | Rota | Açıklama | Başarılı Yanıt |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/healt/` *(veya `/api/health/`)* | Sistem sağlık kontrolü (Health Check) | `200 OK` |
| `GET` | `/api/users/` | Tüm kullanıcıları JSON listele | `200 OK` |
| `POST`| `/api/users/` | Yeni kullanıcı kaydet (JSON body) | `201 Created` |
| `GET` | `/api/users/<int:id>/` | Tekil kullanıcı detayı | `200 OK` *(Yoksa `404`)* |
| `PUT` | `/api/users/<int:id>/` | Kullanıcıyı tam güncelle | `200 OK` *(Eksikse `400`)* |
| `PATCH`| `/api/users/<int:id>/` | Kullanıcıyı kısmi güncelle | `200 OK` |
| `DELETE`| `/api/users/<int:id>/` | Belirtilen kullanıcıyı sil | `200 OK` |
| `GET` | `/api/announcements/` | Tüm duyuruları veritabanından listele | `200 OK` |
| `POST`| `/api/announcements/` | Veritabanına yeni duyuru ekle (JSON body) | `201 Created` |
| `GET` | `/api/announcements/<int:id>/` | Tekil duyuru JSON detayı | `200 OK` *(Yoksa `404`)* |
| `PUT` | `/api/announcements/<int:id>/` | Duyuruyu tam güncelle (PUT) | `200 OK` |
| `PATCH`| `/api/announcements/<int:id>/` | Duyuruyu kısmi güncelle (PATCH) | `200 OK` |
| `DELETE`| `/api/announcements/<int:id>/` | Belirtilen duyuruyu sil (DELETE) | `200 OK` |
| `GET`, `POST` | `/api/jobs/`, `/api/users/<user_id>/jobs/` | İlanları listele veya ilan oluştur | `200 OK`, `201 Created` |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/jobs/<job_id>/`, `/api/users/<user_id>/jobs/<job_id>/` | İlanı görüntüle, güncelle veya sil | `200 OK` |
| `GET`, `POST` | `/api/applications/`, `/api/jobs/<job_id>/applications/`, `/api/users/<user_id>/applications/` | Başvuruları listele veya başvuru oluştur | `200 OK`, `201 Created` |

---

## 🌱 Database Factory ve Idempotent Seeder Mimarisi

Geliştirme ve test süreçlerinde tutarlı, gerçekçi ve tekrar çalıştırılabilir test verileri üretmek amacıyla `core/database/` altında kapsamlı bir **Factory & Seeder** mimarisi kurulmuştur:

```bash
# 1. Standart tohumlama (10 kullanıcı, 5 duyuru - İdempotent)
python manage.py seed

# 2. Özel adetlerle tohumlama
python manage.py seed --users 25 --announcements 10

# 3. Sıfırlayarak baştan temiz tohumlama (Mevcut verileri temizler ve seed eder)
python manage.py seed --fresh --no-input

# 4. Deterministik tohumlama (Tekrarlanabilir random seed)
python manage.py seed --seed 42

# 5. Sadece çekirdek verileri tohumla (0 dinamik kayıt)
python manage.py seed --users 0 --announcements 0
```

> **%100 Idempotent Güvencesi:** Çekirdek kayıtlar `filter().first()` ile sorgulanır. Komut üst üste 10 kez çalıştırılsa dahi mükerrer kayıt oluşturmaz!

---

## 🐳 Docker ve Konteynerizasyon Altyapısı

Django web imajı `python:3.13-slim` tabanını kullanır. Docker Compose, PostgreSQL 16 hazır olduğunda web konteynerinde migration’ları çalıştırır ve uygulamayı başlatır.

```bash
# Konteynerleri derleyip arka planda başlatın
docker compose up -d --build

# Canlı web loglarını izleyin
docker compose logs -f web

# Konteynerleri durdurun
docker compose down
```

- **Sağlık Kontrolü (`healthcheck`):** PostgreSQL `pg_isready` ile hazır olmadan Django ayağa kalkmaz.
- **Kalıcı Veri:** `postgres_data` volume'ü ile konteyner silinse dahi veritabanı korunur.
- **Canlı Senkronizasyon:** Kod değişiklikleri doğrudan konteyner içine yansır.

---

## 🔐 Ortam Değişkenleri ve Güvenlik Önlemleri

- Yerel ortam değişkenlerini `.env` dosyasında tutun ve dosya izinlerini `chmod 600` ile sınırlandırın.
- Git ve Docker derleme bağlamı yerel `.env` dosyasını ve `logs/` dizinini dışarıda bırakır. [`.gitignore`](./.gitignore) ve [`.dockerignore`](./.dockerignore)
- Yerel kurulum şablonu SQLite’ı seçer. [`env.example`](./env.example)

```bash
# .env dosyasını yalnızca ilk kurulumda oluşturun
test -f .env || cp env.example .env
chmod 600 .env
```

---

## 📐 Domain-Driven Database Design (`ddd.md`) Sözleşmesi

Projenin veritabanı mimarisi, ERD şeması, bounded context haritası ve veri sözlüğü kök dizindeki [**`ddd.md`**](./ddd.md) dosyasında kayıt altına alınmıştır.

> [!IMPORTANT]
> ### ⚠️ Kritik Mimari Kural: `ddd.md` Senkronizasyon Sözleşmesi
> 
> 1. Veritabanı modellerinde (`core/models.py`), migration'larda veya tablolarda yeni bir alan eklendiğinde, silindiğinde ya da değiştirildiğinde,
> 2. `README.md` dosyasında veritabanını, şemaları veya veri mimarisini ilgilendiren herhangi bir güncelleme yapıldığında,
> 3. Domain iş kuralları veya Bounded Context sınırları genişletildiğinde,
> 
> **Kök dizindeki [`ddd.md`](./ddd.md) dosyasının da EŞZAMANLI olarak güncellenmesi zorunludur.**  
> `ddd.md` bu projenin yaşayan veritabanı tasarım reçetesidir; kod ve dokümantasyon arasındaki bütünlük asla bozulamaz.

---

## 📄 Swagger / OpenAPI 3.0 Dokümantasyonu

OpenAPI 3.0 tanımı sağlık kontrolü ve kullanıcı uç noktaları ile iş ilanlarının doğrudan ve kullanıcıya bağlı `POST`, `PUT` ve `PATCH` işlemlerini kapsar. İlan istek şemaları başlık sınırını, zorunlu alanları ve isteğe bağlı şehir ile açıklama alanlarını gösterir.

- 🌐 **Swagger UI Konsolu:** [http://127.0.0.1:8000/api/swagger/](http://127.0.0.1:8000/api/swagger/)
- 📄 **OpenAPI JSON Şeması:** [http://127.0.0.1:8000/api/swagger.json](http://127.0.0.1:8000/api/swagger.json) *(veya kök dizindeki [`swagger.json`](./swagger.json))*

> ### ⚠️ Mimari Kural: `swagger.json` Güncelleme Sözleşmesi
> REST API rotalarında, parametrelerinde veya gövde şemalarında yapılan her değişiklikte [`swagger.json`](./swagger.json) dosyasının da güncellenmesi zorunludur.

---

## 💻 Yerel Kurulum ve Çalıştırma (Local Development)

### 1. Önkoşullar
- **Python 3.12 veya üzeri**
- `pip` ve `venv`

Komutları `manage.py` dosyasının bulunduğu `alumni` dizininde çalıştırın. Yerelde mevcut `.env` dosyasıyla SQLite kullanmak için `DB_ENGINE=django.db.backends.sqlite3` değerini ayarlayın. Docker Compose, web konteynerine PostgreSQL ayarlarını ve `db` servis adresini verir.

### 2. Adım Adım Kurulum

```bash
# 1. Proje dizinine girin
cd /path/to/alumni

# 2. Sanal ortamı oluşturun ve aktif edin
python3 -m venv .venv
source .venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Ortam dosyasını ilk kurulumda hazırlayın
test -f .env || cp env.example .env
chmod 600 .env

# 5. Veritabanı tablolarını uygulayın (SQLite)
python manage.py migrate

# 6. İsteğe bağlı olarak demo verisi ekleyin
python manage.py seed --users 10 --announcements 5

# 7. Geliştirme sunucusunu başlatın
python manage.py runserver
```

Tarayıcıdan erişim adresleri:
- **Ana Sayfa:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Kullanıcı Yönetimi:** [http://127.0.0.1:8000/users/](http://127.0.0.1:8000/users/)
- **Duyuru Yönetimi (DB):** [http://127.0.0.1:8000/announcements/](http://127.0.0.1:8000/announcements/)
- **İş İlanları:** [http://127.0.0.1:8000/jobs/](http://127.0.0.1:8000/jobs/)
- **Başvurular:** [http://127.0.0.1:8000/applications/](http://127.0.0.1:8000/applications/)
- **Swagger API Dokümantasyonu:** [http://127.0.0.1:8000/api/swagger/](http://127.0.0.1:8000/api/swagger/)
- **Admin Paneli:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Hata Yanıtları ve İstek Kayıtları

| Durum | Web yanıtı | REST API yanıtı |
| :--- | :--- | :--- |
| `404` | Tanımsız adresler ve bulunamayan kayıtlar, istenen URL’de ortak [404 sayfasını](./templates/404.html) gösterir. | Tanımsız API rotaları JSON hata mesajı döndürür. Tanımlı rotalarda kayıt bulunamadığında controller’ın hata mesajı kullanılır. |
| `500–599` | Guardian, asıl HTTP durum koduyla ortak [sunucu hata sayfasını](./templates/server_error.html) gösterir. | Guardian, asıl HTTP durum koduyla genel bir JSON hata mesajı döndürür. |

5xx yanıtlarında istemciye genel bir açıklama verilir ve yanıtın önbelleğe alınması engellenir. Varsa `Retry-After` başlığı korunur. İstek logger’ı son HTTP durumunu, metodu, istek yolunu ve işlem süresini terminalde iki satırda gösterir.

```text
time      method  route            res.type  duration
07.41.45  get     /olmayan-sayfa/  404       3ms
```

`500–599` aralığındaki istekler aynı biçimde `logs/error.logs` dosyasına eklenir. Dosya uygulama başlatıldığında oluşturulur. Sunucu çalışırken aşağıdaki komutlarla web ve API için `404` yanıtlarını, sağlık kontrolü için `200` yanıtını ve sunucu terminalindeki kayıtları görebilirsiniz.

```bash
curl -i http://127.0.0.1:8000/api/health/
curl -i http://127.0.0.1:8000/olmayan-sayfa/
curl -i http://127.0.0.1:8000/api/olmayan-rota/
tail -f logs/error.logs
```

---

## 🧪 Test ve Kalite Güvencesi

Proje dizininde `python manage.py test` komutuyla **116 testin** tamamını çalıştırabilirsiniz. Hata senaryoları otomatik testlerde kontrollü olarak oluşturulur.

```bash
# İş ilanı modeli ve rotaları
python manage.py test core.tests.JobPostingModelTestCase core.tests.JobPostingRoutesTestCase

# Logger, ortak 404 sayfası ve 5xx guardian
python manage.py test core.tests.RequestLoggingTestCase core.tests.NotFoundMiddlewareTestCase core.tests.ServerErrorGuardianTestCase

# Migration durumu ve model uyumu
python manage.py migrate --check
python manage.py makemigrations --check --dry-run
```

### Test Kapsamı
- **Model testleri** kullanıcı, duyuru, iş ilanı ve başvuru modellerini kapsar. İlan testleri 120 karakter sınırını ve isteğe bağlı alanları doğrular.
- **Factory & Seeder Testleri:** Nesne üretimi (`build`, `create`, `create_batch`), idempotent tekrar tohumlama, CLI `seed` komutu testi.
- **Database CRUD Entegrasyon Testleri:** Web HTML ve REST API üzerinden veritabanına yazma, okuma, güncelleme ve silme doğrulaması.
- **Swagger ve rota testleri** OpenAPI şemasına erişimi, rota yanıtlarını ve son eğik çizgi desteğini doğrular.
- **Middleware testleri** hizalı terminal kaydını, ortak web 404 sayfasını, API JSON hata yanıtlarını ve `500` ile `503` durumlarını doğrular.

---

## 🧭 Geliştirici Kılavuzu ve Kod Standartları

1. **Katman Sınırlarına Uyun:** View/Controller içinde doğrudan karmaşık SQL/iş mantığı yazmayın; `core/services/` katmanını kullanın.
2. **`ddd.md` ve `swagger.json` Senkronizasyonu:** Model veya API değiştiğinde bu iki dokümanı eşzamanlı güncelleyin.
3. **Idempotency Kuralı:** Yeni bir seeder yazdığınızda mükerrer kayıt üretmediğinden (`filter().first()` veya `get_or_create`) emin olun.
4. **Test Yazma Zorunluluğu:** Eklenen her yeni servis, model veya endpoint için karşılık gelen test senaryolarını ekleyin.

---

## 🗺️ Yol Haritası (Roadmap)

- [x] **Aşama 1: Temel Çekirdek ve Altyapı**
  - [x] Django, SQLite ve PostgreSQL Docker entegrasyonu
  - [x] Temiz MVC mimari standardizasyonu
  - [x] Kullanıcı CRUD sistemi (Web Arayüzü & REST API)
  - [x] Duyuru (Announcement) CRUD sistemi ve veritabanı bağlantısı (DB Connection)
  - [x] Domain-Driven Database Design reçetesi ([`ddd.md`](./ddd.md))
  - [x] Database Factory ve Idempotent Seeder mimarisi (`python manage.py seed`)
  - [x] Güvenlik sertleştirmesi (`.env`, `chmod 600`, `.gitignore`, `.dockerignore`)
  - [x] İstek logger’ı, ortak 404 sayfası, 5xx guardian ve hata kayıt dosyası
  - [x] Otomatik test paketi (**116 test**)
- [ ] **Aşama 2: Kimlik Doğrulama ve Rol Yönetimi**
  - [ ] JWT / Session tabanlı kullanıcı kimlik doğrulaması
  - [ ] Öğrenci, Mezun ve Akademisyen rolleri için yetkilendirme (RBAC)
- [ ] **Aşama 3: Mezun Rehberi & Gelişmiş Arama**
  - [ ] Mezuniyet yılı, bölüm, sektör ve şirkete göre filtreleme
  - [ ] LinkedIn ve profesyonel portfolyo entegrasyonları
- [x] **Aşama 4: Kariyer & İş İlanları Panosu**
  - [x] Mezunlar tarafından staj/iş ilanı paylaşımı
  - [x] Başvuru takip sistemi
- [ ] **Aşama 5: Mentorluk & Etkinlik Modülü**
  - [ ] Öğrenci - Mezun mentorluk eşleştirme sistemi
  - [ ] Üniversite etkinlikleri ve buluşma takvimi
