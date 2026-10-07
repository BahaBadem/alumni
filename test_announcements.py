"""
test_announcements.py - Announcement Modülü Birim ve Entegrasyon Testleri

Harici veritabanı gerektirmeyen (In-Memory) Announcement Domain Modeli,
AnnouncementController (Web) ve ApiAnnouncementController (REST API)
kapsamlı testleri.
"""

import os
import json
import unittest
import django
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from announcement_model import (
    Announcement,
    AnnouncementValidationError,
    AnnouncementNotFoundError,
)
import announcement as announcement_service
from core.controllers.announcement_controller import AnnouncementController
from core.controllers.api_announcement_controller import ApiAnnouncementController


class AnnouncementModelTestCase(unittest.TestCase):
    """Announcement domain model testleri."""

    def test_model_creation_and_to_dict(self):
        ann = Announcement(
            id=1,
            title="Mezun Günü 2026",
            content="Geleneksel mezun buluşması yapılacaktır.",
            author="Rektörlük",
            category="Etkinlik",
            is_active=True,
        )
        data = ann.to_dict()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["title"], "Mezun Günü 2026")
        self.assertEqual(data["baslik"], "Mezun Günü 2026")
        self.assertEqual(data["category"], "Etkinlik")
        self.assertTrue(data["is_active"])

    def test_from_dict(self):
        ann = Announcement.from_dict({
            "baslik": "Staj Programı",
            "icerik": "Yaz dönemi staj başvuruları başlamıştır.",
            "yazar": "Kariyer",
            "kategori": "Kariyer",
            "aktif_mi": True
        }, announcement_id=5)
        self.assertEqual(ann.id, 5)
        self.assertEqual(ann.title, "Staj Programı")
        self.assertEqual(ann.category, "Kariyer")

    def test_validation_error_on_empty_title_or_content(self):
        ann = Announcement(title="", content="Detay metni")
        with self.assertRaises(AnnouncementValidationError):
            ann.validate()

        ann2 = Announcement(title="Başlık", content="")
        with self.assertRaises(AnnouncementValidationError):
            ann2.validate()


class AnnouncementCrudServiceTestCase(unittest.TestCase):
    """announcement.py In-Memory CRUD operasyonları testleri."""

    def setUp(self):
        announcement_service.clear_storage()

    def tearDown(self):
        announcement_service.clear_storage()

    def test_create_and_get(self):
        ann = announcement_service.create_announcement(
            title="Yeni Duyuru",
            content="Duyuru içeriği açıklaması...",
            author="Test Birimi",
            category="Genel"
        )
        self.assertIsNotNone(ann.id)
        self.assertEqual(announcement_service.count_announcements(), 1)

        fetched = announcement_service.get_announcement_by_id(ann.id)
        self.assertEqual(fetched.title, "Yeni Duyuru")

    def test_update_and_patch(self):
        ann = announcement_service.create_announcement("Eski Başlık", "Eski İçerik", "Yazar")
        
        # PUT (Tam güncelleme)
        updated = announcement_service.update_announcement(
            announcement_id=ann.id,
            title="Yeni Başlık",
            content="Yeni İçerik",
            author="Yeni Yazar",
            category="Kariyer"
        )
        self.assertEqual(updated.title, "Yeni Başlık")
        self.assertEqual(updated.category, "Kariyer")

        # PATCH (Kısmi güncelleme)
        patched = announcement_service.patch_announcement(ann.id, title="Yalnız Başlık Değişti")
        self.assertEqual(patched.title, "Yalnız Başlık Değişti")
        self.assertEqual(patched.category, "Kariyer")

    def test_delete(self):
        ann = announcement_service.create_announcement("Silinecek", "Silinecek içerik", "Yazar")
        self.assertEqual(announcement_service.count_announcements(), 1)
        deleted = announcement_service.delete_announcement(ann.id)
        self.assertEqual(deleted.id, ann.id)
        self.assertEqual(announcement_service.count_announcements(), 0)

        with self.assertRaises(AnnouncementNotFoundError):
            announcement_service.get_announcement_by_id(ann.id)


class AnnouncementControllersTestCase(unittest.TestCase):
    """AnnouncementController ve ApiAnnouncementController testleri."""

    def setUp(self):
        self.factory = RequestFactory()
        announcement_service.clear_storage()
        self.web_controller = AnnouncementController()
        self.api_controller = ApiAnnouncementController()

    def tearDown(self):
        announcement_service.clear_storage()

    # 1. WEB CONTROLLER TESTS
    def test_web_controller_create_and_list(self):
        post_req = self.factory.post("/announcements/create/", data={
            "title": "Web Üzerinden Eklenen Duyuru",
            "content": "Bu içerik web formundan gönderilmiştir.",
            "author": "Mezunlar Ofisi",
            "category": "Etkinlik",
            "is_active": "true"
        })
        res_post = self.web_controller.create(post_req)
        self.assertEqual(res_post.status_code, 201)
        self.assertEqual(announcement_service.count_announcements(), 1)

        get_req = self.factory.get("/announcements/")
        res_get = self.web_controller.list(get_req)
        self.assertEqual(res_get.status_code, 200)

    # 2. REST API CONTROLLER TESTS
    def test_api_controller_full_crud(self):
        # 1. CREATE
        post_req = self.factory.post(
            "/api/announcements/",
            data=json.dumps({
                "title": "API Duyuru Başlığı",
                "content": "API üzerinden eklenen duyuru metni.",
                "author": "Yazılım Kulübü",
                "category": "Kariyer"
            }),
            content_type="application/json"
        )
        res_post = self.api_controller.create(post_req)
        self.assertEqual(res_post.status_code, 201)
        created_json = json.loads(res_post.content)
        self.assertEqual(created_json["status"], "success")
        ann_id = created_json["announcement"]["id"]

        # 2. READ (Detail)
        get_req = self.factory.get(f"/api/announcements/{ann_id}/")
        res_detail = self.api_controller.detail(get_req, announcement_id=ann_id)
        self.assertEqual(res_detail.status_code, 200)

        # 3. UPDATE (PUT)
        put_req = self.factory.put(
            f"/api/announcements/{ann_id}/",
            data=json.dumps({
                "title": "Güncellenmiş API Başlığı",
                "content": "Tamamen yenilenmiş içerik metni.",
                "author": "Yazılım Kulübü",
                "category": "Genel"
            }),
            content_type="application/json"
        )
        res_put = self.api_controller.update(put_req, announcement_id=ann_id)
        self.assertEqual(res_put.status_code, 200)

        # 4. PATCH
        patch_req = self.factory.patch(
            f"/api/announcements/{ann_id}/",
            data=json.dumps({"category": "Mentorluk"}),
            content_type="application/json"
        )
        res_patch = self.api_controller.partial_update(patch_req, announcement_id=ann_id)
        self.assertEqual(res_patch.status_code, 200)
        self.assertEqual(json.loads(res_patch.content)["announcement"]["category"], "Mentorluk")

        # 5. DELETE
        del_req = self.factory.delete(f"/api/announcements/{ann_id}/")
        res_del = self.api_controller.delete(del_req, announcement_id=ann_id)
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(announcement_service.count_announcements(), 0)

    # 3. ROUTE REVERSE TESTS
    def test_routes_reverse(self):
        from django.urls import reverse
        self.assertEqual(reverse('announcements_page'), '/announcements/')
        self.assertEqual(reverse('announcement_detail', kwargs={'announcement_id': 1}), '/announcements/1/')
        self.assertEqual(reverse('api_announcements'), '/api/announcements/')
        self.assertEqual(reverse('api_announcement_detail', kwargs={'announcement_id': 2}), '/api/announcements/2/')


if __name__ == "__main__":
    unittest.main()
