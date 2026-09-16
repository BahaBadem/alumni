# 🎓 Alumni Portal (Alumni Management System)

A web-based Alumni Management Platform built with **Python**, **Django**, and **SQLite**, fully containerized using **Docker** and **Docker Compose**. 

Developed as a term project for the **Web Programming** course.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Getting Started with Docker](#-getting-started-with-docker)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
  - [Initial Setup (Migrations & Superuser)](#initial-setup-migrations--superuser)
- [Local Development (Without Docker)](#-local-development-without-docker)
- [Environment Variables](#-environment-variables)
- [Database & Data Persistence](#-database--data-persistence)
- [Semester Roadmap](#-semester-roadmap)
- [Useful Commands](#-useful-commands)
- [License & Academic Integrity](#-license--academic-integrity)

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
│   ├── urls.py
│   └── wsgi.py
├── accounts/              # User profiles, authentication & roles
├── directory/             # Alumni directory & search functionality
├── jobs/                  # Job board & internship listings
├── events/                # Campus and alumni events
├── static/                # Static assets (CSS, JS, images)
├── media/                 # User-uploaded files (avatars, resumes)
├── templates/             # HTML templates
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── README.md
└── requirements.txt
