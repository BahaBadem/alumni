"""
test_controllers.py - UserController ve ApiUserController Birim Testleri
Hem In-Memory hem de Django HTTP Request/Response senaryolarını test eder.
"""

import unittest
from django.test import RequestFactory
from django.conf import settings
import os
import django

# Django ayarlarını yükle
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from core.controllers.user_controller import UserController
from core.controllers.api_user_controller import ApiUserController
import user as in_memory_service


class ControllersUnitTestCase(unittest.TestCase):
    """UserController ve ApiUserController doğrudan birim testleri."""

    def setUp(self):
        self.factory = RequestFactory()
        in_memory_service.clear_storage()
        # In-Memory modunda çalışan controller örnekleri
        self.web_controller = UserController(use_in_memory=True)
        self.api_controller = ApiUserController(use_in_memory=True)

    def tearDown(self):
        in_memory_service.clear_storage()

    # --------------------------------------------------------------------------
    # API USER CONTROLLER TESTS
    # --------------------------------------------------------------------------
    def test_api_controller_create_and_read(self):
        # 1. CREATE
        post_req = self.factory.post(
            "/api/users/",
            data='{"name": "Ahmet Test", "birth_date": "2000-01-01", "city": "Ankara", "school": "Hacettepe"}',
            content_type="application/json"
        )
        res_create = self.api_controller.create(post_req)
        self.assertEqual(res_create.status_code, 201)
        import json
        data_create = json.loads(res_create.content)
        self.assertEqual(data_create["status"], "success")
        user_id = data_create["user"]["id"]

        # 2. READ (Detail)
        get_req = self.factory.get(f"/api/users/{user_id}/")
        res_get = self.api_controller.detail(get_req, user_id=user_id)
        self.assertEqual(res_get.status_code, 200)
        data_get = json.loads(res_get.content)
        self.assertEqual(data_get["user"]["name"], "Ahmet Test")

        # 3. READ (List)
        list_req = self.factory.get("/api/users/")
        res_list = self.api_controller.list(list_req)
        self.assertEqual(res_list.status_code, 200)
        data_list = json.loads(res_list.content)
        self.assertEqual(data_list["count"], 1)

    def test_api_controller_update_and_patch(self):
        # Önce kullanıcı oluştur
        u = in_memory_service.create_user("Eski", "2000-01-01", "Ankara", "Gazi")

        # PUT (Tam güncelleme)
        put_req = self.factory.put(
            f"/api/users/{u.id}/",
            data='{"name": "Yeni Tam", "birth_date": "1995-05-05", "city": "İzmir", "school": "Ege"}',
            content_type="application/json"
        )
        res_put = self.api_controller.update(put_req, user_id=u.id)
        self.assertEqual(res_put.status_code, 200)
        import json
        self.assertEqual(json.loads(res_put.content)["user"]["name"], "Yeni Tam")

        # PATCH (Kısmi güncelleme)
        patch_req = self.factory.patch(
            f"/api/users/{u.id}/",
            data='{"city": "Bursa"}',
            content_type="application/json"
        )
        res_patch = self.api_controller.partial_update(patch_req, user_id=u.id)
        self.assertEqual(res_patch.status_code, 200)
        self.assertEqual(json.loads(res_patch.content)["user"]["city"], "Bursa")

    def test_api_controller_delete(self):
        u = in_memory_service.create_user("Silinecek", "2000-01-01", "Konya", "Selçuk")
        del_req = self.factory.delete(f"/api/users/{u.id}/")
        res_del = self.api_controller.delete(del_req, user_id=u.id)
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(in_memory_service.count_users(), 0)

    # --------------------------------------------------------------------------
    # WEB USER CONTROLLER TESTS
    # --------------------------------------------------------------------------
    def test_web_controller_create_and_list(self):
        # 1. CREATE via Form POST
        post_req = self.factory.post("/users/", data={
            "name": "Web Form Kullanıcısı",
            "birth_date": "1998-09-15",
            "city": "Eskişehir",
            "school": "Anadolu Üniversitesi"
        })
        res_post = self.web_controller.create(post_req)
        self.assertEqual(res_post.status_code, 201)
        self.assertEqual(in_memory_service.count_users(), 1)

        # 2. READ via GET
        get_req = self.factory.get("/users/")
        res_get = self.web_controller.list(get_req)
        self.assertEqual(res_get.status_code, 200)

    def test_web_controller_validation_error(self):
        # Eksik alan ile POST
        post_req = self.factory.post("/users/", data={"name": "Sadece İsim"})
        res_post = self.web_controller.create(post_req)
        self.assertEqual(res_post.status_code, 400)

    # --------------------------------------------------------------------------
    # VIEW LAYERS (user_web_view & user_api_view) GET & POST TESTS
    # --------------------------------------------------------------------------
    def test_view_layers_get_and_post(self):
        import json
        from core.views import user_web_view, user_api_view

        # 1. user_web_view GET
        get_web = self.factory.get('/users/')
        res_web_get = user_web_view(get_web)
        self.assertEqual(res_web_get.status_code, 200)

        # 2. user_web_view POST
        post_web = self.factory.post('/users/', data={
            'name': 'Web Katmanı Testi',
            'birth_date': '1999-01-01',
            'city': 'Ankara',
            'school': 'Hacettepe'
        })
        res_web_post = user_web_view(post_web)
        self.assertIn(res_web_post.status_code, [200, 201])

        # 3. user_api_view GET
        get_api = self.factory.get('/api/users/')
        res_api_get = user_api_view(get_api)
        self.assertEqual(res_api_get.status_code, 200)
        api_data = json.loads(res_api_get.content)
        self.assertEqual(api_data['status'], 'success')

        # 4. user_api_view POST
        post_api = self.factory.post(
            '/api/users/',
            data=json.dumps({
                'name': 'API Katmanı Testi',
                'birth_date': '2001-05-15',
                'city': 'İstanbul',
                'school': 'İTÜ'
            }),
            content_type='application/json'
        )
        res_api_post = user_api_view(post_api)
        self.assertEqual(res_api_post.status_code, 201)
        created_data = json.loads(res_api_post.content)
        self.assertEqual(created_data['status'], 'success')
        self.assertEqual(created_data['user']['name'], 'API Katmanı Testi')

    # --------------------------------------------------------------------------
    # TÜM AYRIŞTIRILMIŞ CRUD CONTROLLER VIEW FONKSİYONLARININ TESTLERİ
    # --------------------------------------------------------------------------
    def test_all_crud_controller_views(self):
        import json
        from core.views import (
            user_list_view, user_create_view, user_detail_view, user_update_view, user_delete_view,
            api_user_list_view, api_user_create_view, api_user_detail_view,
            api_user_update_view, api_user_patch_view, api_user_delete_view
        )

        # 1. API CREATE
        create_req = self.factory.post(
            '/api/users/create/',
            data=json.dumps({
                'name': 'Birim CRUD Kullanıcı',
                'birth_date': '2000-01-01',
                'city': 'İzmir',
                'school': 'Dokuz Eylül'
            }),
            content_type='application/json'
        )
        res_create = api_user_create_view(create_req)
        self.assertEqual(res_create.status_code, 201)
        user_id = json.loads(res_create.content)['user']['id']

        # 2. API READ SINGLE (Detail)
        detail_req = self.factory.get(f'/api/users/{user_id}/detail/')
        res_detail = api_user_detail_view(detail_req, user_id=user_id)
        self.assertEqual(res_detail.status_code, 200)

        # 3. API READ ALL (List)
        list_req = self.factory.get('/api/users/list/')
        res_list = api_user_list_view(list_req)
        self.assertEqual(res_list.status_code, 200)

        # 4. API UPDATE (PUT)
        update_req = self.factory.put(
            f'/api/users/{user_id}/update/',
            data=json.dumps({
                'name': 'Birim CRUD Güncel',
                'birth_date': '1998-02-02',
                'city': 'Ankara',
                'school': 'Bilkent'
            }),
            content_type='application/json'
        )
        res_update = api_user_update_view(update_req, user_id=user_id)
        self.assertEqual(res_update.status_code, 200)

        # 5. API PATCH
        patch_req = self.factory.patch(
            f'/api/users/{user_id}/patch/',
            data=json.dumps({'city': 'Antalya'}),
            content_type='application/json'
        )
        res_patch = api_user_patch_view(patch_req, user_id=user_id)
        self.assertEqual(res_patch.status_code, 200)

        # 6. WEB READ ALL & DETAIL
        web_list = user_list_view(self.factory.get('/users/list/'))
        self.assertEqual(web_list.status_code, 200)
        web_detail = user_detail_view(self.factory.get(f'/users/{user_id}/'), user_id=user_id)
        self.assertEqual(web_detail.status_code, 200)

        # 7. API DELETE
        del_req = self.factory.delete(f'/api/users/{user_id}/delete/')
        res_del = api_user_delete_view(del_req, user_id=user_id)
        self.assertEqual(res_del.status_code, 200)


if __name__ == "__main__":
    unittest.main()
