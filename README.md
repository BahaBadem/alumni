# 🎓 Alumni Portal (Alumni Management System)

A web-based Alumni Management Platform built with **Python**, **Django**, and **SQLite**, fully containerized using **Docker** and **Docker Compose**. 

Developed as a term project for the **Web Programming** course.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Implemented Routes](#-implemented-routes)
- [Local Development](#-local-development)
- [Semester Roadmap](#-semester-roadmap)
- [Useful Commands](#-useful-commands)


---

## 📖 Overview

The **Alumni Portal** is designed to bridge the gap between graduates, current students, and university faculty. It provides a centralized space where alumni can stay connected with their alma mater, explore career networking opportunities, share job openings, and offer mentorship to undergraduate students.

---

## ✨ Key Features

- **🔐 Authentication & Role-Based Access Control**:
  - Distinct roles for **Students**, **Alumni**, and **Faculty / Admins**.
  - Secure registration, login, profile verification, and password reset.

- **👥 Alumni Directory & Search**:
  - Filter and search graduates by graduation year, department, current company, industry, or location.

- **💼 Career & Job Board**:
  - Alumni can post internship and job openings.
  - Students can browse and apply directly to listings.

- **🤝 Mentorship Program**:
  - Connect students with alumni working in their target industries.

- **📅 Events & Announcements**:
  - University reunions, webinars, networking nights, and faculty updates.

---

## 🛠️ Tech Stack

- **Backend Framework:** [Django](https://www.djangoproject.com/) (Python 3.11+)
- **Database:** [SQLite](https://www.sqlite.org/) (File-based database with host bind-mount persistence)
- **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **Frontend:** Django Templates, HTML5, CSS3 / Modern CSS Framework (Bootstrap / Tailwind CSS), JavaScript

---

## 📂 Project Architecture

```text
alumni-portal/
├── core/                  # Project configuration & settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── tests.py           # Unit tests
│   ├── urls.py            # URL routing configurations
│   ├── views.py           # Route views & handlers
│   └── wsgi.py
├── accounts/              # User profiles, authentication & roles
├── directory/             # Alumni directory & search functionality
├── jobs/                  # Job board & internship listings
├── events/                # Campus and alumni events
├── static/                # Static assets (CSS, JS, images)
├── media/                 # User-uploaded files (avatars, resumes)
├── templates/             # HTML templates
│   ├── index.html         # Main landing page & live route tester
│   └── about.html         # About page
├── manage.py
├── README.md
└── requirements.txt
```

---

## 🚦 Implemented Routes

| Method | Route / Pattern | View Handler | Description | Example / Return Value |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `home` | Landing page | Renders `templates/index.html` |
| `GET` | `/about/` | `about` | About page | Renders `templates/about.html` |
| `GET` | `/hello/` | `hello` | Static route | `"Hello, World!"` |
| `GET` | `/hello/<str:name>/` | `hello` | Dynamic route parameter | `/hello/Ahmet/` ➔ `"Hello, Ahmet!"` |
| `GET` | `/sum/<int:num1>/<int:num2>/` | `calculate_sum` | Dynamic integer parameters | `/sum/15/25/` ➔ `"40"` |
| `GET` | `/api/healt/` | `health_check` | Health check API (JSON) | `{"status": "ok", "message": "healthy"}` |
| `POST` | `/api/users/` | `api_users_view` | Yeni kullanıcı kaydı (isim, doğum tarihi, şehir, okul) | `201 Created` & `{"status": "success", "user": {...}}` |
| `GET` | `/api/users/` | `api_users_view` | Tüm kayıtlı kullanıcıların tüm bilgilerini JSON listeler | `200 OK` & `{"status": "success", "count": N, "users": [...]}` |
| `PUT` | `/api/users/<id>/` | `api_users_view` | Belirtilen kullanıcının tüm bilgilerini tam güncelleme | `200 OK` & `{"status": "success", "user": {...}}` |
| `PATCH` | `/api/users/<id>/` | `api_users_view` | Belirtilen kullanıcının sadece verilen alanlarını kısmi güncelleme | `200 OK` & `{"status": "success", "user": {...}}` |
| `DELETE` | `/api/users/<id>/` | `api_users_view` | Belirtilen kullanıcı kaydını silme | `200 OK` & `{"status": "success", "deleted_id": N}` |
| `GET` | `/api/swagger/` | `swagger_ui_view` | İnteraktif Swagger UI REST API dokümantasyonu | Renders `templates/swagger.html` |
| `GET` | `/api/swagger.json` | `swagger_json_view` | OpenAPI 3.0 şema çıktısı (JSON) | `swagger.json` içerik çıktısı |
| `GET` / `POST` | `/users/` | `users_page_view` | Kullanıcı kayıt ve yönetim paneli görsel arayüzü | Renders `templates/users.html` |

---

## 📄 Swagger / OpenAPI API Dokümantasyonu & Güncelleme Kuralı

Projedeki tüm REST API uç noktaları OpenAPI 3.0 standardında hazırlanmış ve **Swagger UI** ile görselleştirilmiştir.

- **Swagger Arayüzü (Web):** `http://127.0.0.1:8000/api/swagger/`
- **Şema Dosyası (JSON):** `http://127.0.0.1:8000/api/swagger.json` veya proje kök dizinindeki [`swagger.json`](./swagger.json)

> ### ⚠️ ÖNEMLİ GELİŞTİRİCİ KURALI: `swagger.json` Güncelleme Zorunluluğu
> Projeye yeni bir API ucu (endpoint) eklendiğinde, mevcut rotalarda metot/parametre değişikliği yapıldığında veya model alanlarında güncelleme olduğunda, **proje kök dizinindeki `swagger.json` dosyasının da güncellenmesi zorunludur.**
> 
> Swagger UI arayüzü doğrudan bu dosyayı dinamik olarak okuduğu için, yapılan tüm değişiklikler `swagger.json` dosyasına işlendikten sonra arayüze anında yansıyacaktır.

## 💻 Local Development

### 1. Prerequisites
- Python 3.11+
- Virtual environment (`venv`)

### 2. Setup & Run

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Start the development server
python manage.py runserver
```

Visit **`http://localhost:8000/`** in your browser.

---

## 🛠️ Useful Commands

```bash
# Run unit tests
python manage.py test core

# Check project configuration
python manage.py check

# Create a superuser / admin
python manage.py createsuperuser
```
