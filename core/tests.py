import json
from io import StringIO
from django.test import TestCase, Client
from django.core.management import call_command
from core.models import UserProfile, Announcement
from core.database.factories import UserProfileFactory, AnnouncementFactory
from core.database.seeders import UserProfileSeeder, AnnouncementSeeder, DatabaseSeeder
from core.services import announcement_service
from announcement_model import AnnouncementValidationError, AnnouncementNotFoundError


class HomeRouteTestCase(TestCase):
    def test_home_route_renders_main_page(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, 'Alumni Portal')

    def test_about_route_renders_about_page(self):
        client = Client()
        response = client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')
        self.assertContains(response, 'Hakkımızda')



    def test_hello_route_returns_hello_world(self):
        client = Client()
        response = client.get('/hello/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Hello, World!')

    def test_hello_dynamic_name(self):
        client = Client()
        response = client.get('/hello/Ahmet/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Hello, Ahmet!')

        response2 = client.get('/hello/Baha/')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.content.decode('utf-8'), 'Hello, Baha!')

    def test_sum_route(self):
        client = Client()
        response = client.get('/sum/5/10/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '15')

        # Test without trailing slash
        response_no_slash = client.get('/sum/12/8')
        self.assertEqual(response_no_slash.status_code, 200)
        self.assertEqual(response_no_slash.content.decode('utf-8'), '20')


class HealthCheckRouteTestCase(TestCase):
    def test_health_check_healt_with_slash(self):
        client = Client()
        response = client.get('/api/healt/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')
        self.assertEqual(data.get('message'), 'healthy')

    def test_health_check_healt_without_slash(self):
        client = Client()
        response = client.get('/api/healt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')

    def test_health_check_health_with_slash(self):
        client = Client()
        response = client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')

    def test_health_check_post_method_not_allowed(self):
        client = Client()
        response = client.post('/api/healt/')
        self.assertEqual(response.status_code, 405)


class UsersRouteTestCase(TestCase):
    def test_get_users_page_renders_form_and_cells(self):
        client = Client()
        response = client.get('/users/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users.html')
        self.assertContains(response, 'İsim')
        self.assertContains(response, 'Doğum Tarihi')
        self.assertContains(response, 'Şehir')
        self.assertContains(response, 'Okul')

    def test_get_users_page_without_slash(self):
        client = Client()
        response = client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users.html')

    def test_post_api_users_json_payload(self):
        client = Client()
        payload = {
            'name': 'Ahmet Baha',
            'birth_date': '2001-05-15',
            'city': 'İstanbul',
            'school': 'İstanbul Teknik Üniversitesi'
        }
        response = client.post(
            '/api/users/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data['user']['name'], 'Ahmet Baha')
        self.assertEqual(data['user']['city'], 'İstanbul')
        self.assertEqual(data['user']['school'], 'İstanbul Teknik Üniversitesi')

    def test_post_api_users_without_slash(self):
        client = Client()
        payload = {
            'name': 'Baha Badem',
            'birth_date': '2000-04-10',
            'city': 'Ankara',
            'school': 'Hacettepe'
        }
        response = client.post(
            '/api/users',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_post_api_users_form_data(self):
        client = Client()
        response = client.post('/api/users/', {
            'name': 'Mehmet Öz',
            'birth_date': '1999-10-20',
            'city': 'Ankara',
            'school': 'ODTÜ'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data['user']['name'], 'Mehmet Öz')

    def test_get_api_users_lists_all_info(self):
        client = Client()
        # Add 2 users first via POST /api/users/
        client.post('/api/users/', {
            'name': 'Ali Can',
            'birth_date': '1998-02-14',
            'city': 'İzmir',
            'school': 'Ege Üniversitesi'
        })
        client.post('/api/users/', {
            'name': 'Ayşe Demir',
            'birth_date': '2002-07-21',
            'city': 'Bursa',
            'school': 'Uludağ Üniversitesi'
        })

        # Now GET /api/users/
        response = client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data.get('count'), 2)
        users = data.get('users', [])
        self.assertEqual(len(users), 2)
        # Check all fields exist in list items
        first = users[0]
        self.assertIn('id', first)
        self.assertIn('name', first)
        self.assertIn('birth_date', first)
        self.assertIn('city', first)
        self.assertIn('school', first)

    def test_get_api_users_without_slash(self):
        client = Client()
        response = client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_post_api_users_missing_fields_error(self):
        client = Client()
        response = client.post('/api/users/', {
            'name': 'Eksik Kullanıcı'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'error')

    def test_post_api_users_invalid_date_error(self):
        client = Client()
        response = client.post('/api/users/', {
            'name': 'Test',
            'birth_date': 'invalid-date',
            'city': 'Ankara',
            'school': 'ODTÜ'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'error')

    def test_put_api_users_full_update(self):
        client = Client()
        # Create a user first
        create_res = client.post(
            '/api/users/',
            data=json.dumps({
                'name': 'Eski İsim',
                'birth_date': '2000-01-01',
                'city': 'Eski Şehir',
                'school': 'Eski Okul'
            }),
            content_type='application/json'
        )
        user_id = create_res.json()['user']['id']

        # Update via PUT /api/users/<user_id>/
        put_payload = {
            'name': 'Yeni İsim',
            'birth_date': '1995-12-12',
            'city': 'Yeni Şehir',
            'school': 'Yeni Okul'
        }
        response = client.put(
            f'/api/users/{user_id}/',
            data=json.dumps(put_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data['user']['name'], 'Yeni İsim')
        self.assertEqual(data['user']['birth_date'], '1995-12-12')
        self.assertEqual(data['user']['city'], 'Yeni Şehir')
        self.assertEqual(data['user']['school'], 'Yeni Okul')

    def test_put_api_users_missing_field_error(self):
        client = Client()
        create_res = client.post(
            '/api/users/',
            data=json.dumps({
                'name': 'Test İsim',
                'birth_date': '2000-01-01',
                'city': 'Ankara',
                'school': 'ODTÜ'
            }),
            content_type='application/json'
        )
        user_id = create_res.json()['user']['id']

        # Missing 'school' and 'city' in PUT
        response = client.put(
            f'/api/users/{user_id}/',
            data=json.dumps({'name': 'Sadece İsim'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('status'), 'error')

    def test_patch_api_users_partial_update_city(self):
        client = Client()
        create_res = client.post(
            '/api/users/',
            data=json.dumps({
                'name': 'Baha Badem',
                'birth_date': '2001-04-12',
                'city': 'Ankara',
                'school': 'Hacettepe Üniversitesi'
            }),
            content_type='application/json'
        )
        user_id = create_res.json()['user']['id']

        # PATCH: Only change city
        response = client.patch(
            f'/api/users/{user_id}/',
            data=json.dumps({'city': 'İstanbul'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data['user']['city'], 'İstanbul')
        # Check name and school remained unchanged
        self.assertEqual(data['user']['name'], 'Baha Badem')
        self.assertEqual(data['user']['school'], 'Hacettepe Üniversitesi')

    def test_patch_api_users_partial_update_school_via_body_id(self):
        client = Client()
        create_res = client.post(
            '/api/users/',
            data=json.dumps({
                'name': 'Can Yılmaz',
                'birth_date': '1999-03-15',
                'city': 'İzmir',
                'school': 'Ege Üniversitesi'
            }),
            content_type='application/json'
        )
        user_id = create_res.json()['user']['id']

        # PATCH to /api/users/ with ID inside payload
        response = client.patch(
            '/api/users/',
            data=json.dumps({'id': user_id, 'school': 'Dokuz Eylül Üniversitesi'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user']['school'], 'Dokuz Eylül Üniversitesi')
        self.assertEqual(data['user']['city'], 'İzmir')

    def test_put_patch_not_found(self):
        client = Client()
        response = client.patch(
            '/api/users/99999/',
            data=json.dumps({'city': 'Bursa'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_api_user_by_url(self):
        client = Client()
        create_res = client.post(
            '/api/users/',
            data=json.dumps({
                'name': 'Silinecek Kullanıcı',
                'birth_date': '2000-01-01',
                'city': 'Konya',
                'school': 'Selçuk Üniversitesi'
            }),
            content_type='application/json'
        )
        user_id = create_res.json()['user']['id']

        # Delete user via DELETE /api/users/<user_id>/
        response = client.delete(f'/api/users/{user_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data.get('deleted_id'), user_id)

        # Confirm user no longer exists
        get_res = client.get(f'/api/users/{user_id}/')
        self.assertEqual(get_res.status_code, 404)

    def test_delete_api_user_by_body_id(self):
        client = Client()
        create_res = client.post(
            '/api/users/',
            data=json.dumps({
                'name': 'Gövdeden Silinecek',
                'birth_date': '1997-06-10',
                'city': 'Antalya',
                'school': 'Akdeniz Üniversitesi'
            }),
            content_type='application/json'
        )
        user_id = create_res.json()['user']['id']

        response = client.delete(
            '/api/users/',
            data=json.dumps({'id': user_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')

    def test_delete_not_found(self):
        client = Client()
        response = client.delete('/api/users/99999/')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data.get('status'), 'error')

    def test_delete_missing_id_error(self):
        client = Client()
        response = client.delete('/api/users/')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data.get('status'), 'error')

    def test_api_users_invalid_method(self):
        client = Client()
        response = client.trace('/api/users/')
        self.assertEqual(response.status_code, 405)


class SwaggerRouteTestCase(TestCase):
    def test_swagger_ui_with_slash(self):
        client = Client()
        response = client.get('/api/swagger/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'swagger.html')
        self.assertContains(response, 'Swagger API Docs')

    def test_swagger_ui_without_slash(self):
        client = Client()
        response = client.get('/api/swagger')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'swagger.html')

    def test_swagger_json_endpoint(self):
        client = Client()
        response = client.get('/api/swagger.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data.get('openapi'), '3.0.0')
        self.assertIn('/api/healt/', data.get('paths', {}))
        self.assertIn('/api/users/', data.get('paths', {}))
        self.assertIn('Health', [t['name'] for t in data.get('tags', [])])
        self.assertIn('Users', [t['name'] for t in data.get('tags', [])])


class AnnouncementModelTestCase(TestCase):
    """core/models.py içerisindeki Announcement ORM modeli birim testleri."""

    def test_announcement_creation_and_defaults(self):
        ann = Announcement.objects.create(
            title="Kariyer Fuarı 2026",
            content="Tüm mezun ve öğrencilerimiz davetlidir.",
        )
        self.assertIsNotNone(ann.id)
        self.assertEqual(ann.author, "Mezunlar Koordinatörlüğü")
        self.assertEqual(ann.category, "Genel")
        self.assertTrue(ann.is_active)
        self.assertIn("Kariyer Fuarı 2026", str(ann))

    def test_announcement_to_dict_bilingual(self):
        ann = Announcement.objects.create(
            title="Mezun Buluşması",
            content="Geleneksel mezun buluşması kampüste yapılacaktır.",
            author="Rektörlük",
            category="Etkinlik",
            is_active=True,
        )
        data = ann.to_dict()
        # İngilizce alanlar
        self.assertEqual(data["id"], ann.id)
        self.assertEqual(data["title"], "Mezun Buluşması")
        self.assertEqual(data["content"], "Geleneksel mezun buluşması kampüste yapılacaktır.")
        self.assertEqual(data["author"], "Rektörlük")
        self.assertEqual(data["category"], "Etkinlik")
        self.assertTrue(data["is_active"])
        # Türkçe alias alanlar
        self.assertEqual(data["baslik"], "Mezun Buluşması")
        self.assertEqual(data["icerik"], "Geleneksel mezun buluşması kampüste yapılacaktır.")
        self.assertEqual(data["yazar"], "Rektörlük")
        self.assertEqual(data["kategori"], "Etkinlik")
        self.assertTrue(data["aktif_mi"])


class DatabaseFactoryAndSeederTestCase(TestCase):
    """Database Factory ve Seeder mimarisinin kapsamlı birim ve entegrasyon testleri."""

    def test_user_profile_factory_build_and_create(self):
        factory = UserProfileFactory()
        
        # build: Sadece hafızada, DB ID'si olmamalı
        built_user = factory.build(city="İzmir")
        self.assertIsNone(built_user.id)
        self.assertEqual(built_user.city, "İzmir")
        self.assertTrue(len(built_user.name) >= 3)

        # create: Veritabanına yazılmalı, ID atanmalı
        created_user = factory.create(city="Bursa")
        self.assertIsNotNone(created_user.id)
        self.assertEqual(created_user.city, "Bursa")
        self.assertTrue(UserProfile.objects.filter(id=created_user.id).exists())

    def test_announcement_factory_build_and_create(self):
        factory = AnnouncementFactory()

        # build
        built_ann = factory.build(category="Kariyer")
        self.assertIsNone(built_ann.id)
        self.assertEqual(built_ann.category, "Kariyer")
        self.assertTrue(built_ann.is_active)

        # create
        created_ann = factory.create(category="Etkinlik")
        self.assertIsNotNone(created_ann.id)
        self.assertEqual(created_ann.category, "Etkinlik")
        self.assertTrue(Announcement.objects.filter(id=created_ann.id).exists())

    def test_factory_batch_operations(self):
        user_factory = UserProfileFactory()
        ann_factory = AnnouncementFactory()

        # build_batch
        built_users = user_factory.build_batch(3)
        self.assertEqual(len(built_users), 3)
        for u in built_users:
            self.assertIsNone(u.id)

        # create_batch
        created_anns = ann_factory.create_batch(4)
        self.assertEqual(len(created_anns), 4)
        for a in created_anns:
            self.assertIsNotNone(a.id)

    def test_user_seeder_idempotency(self):
        seeder = UserProfileSeeder()

        # 1. Çalıştırma (Çekirdek kullanıcılar eklenir)
        report1 = seeder.seed(count=0)
        self.assertEqual(report1["created"], len(UserProfileSeeder.CORE_USERS))
        self.assertEqual(report1["existing"], 0)

        # 2. Çalıştırma (Çekirdek kullanıcılar mükerrer eklenmemeli)
        report2 = seeder.seed(count=0)
        self.assertEqual(report2["created"], 0)
        self.assertEqual(report2["existing"], len(UserProfileSeeder.CORE_USERS))

    def test_announcement_seeder_idempotency(self):
        seeder = AnnouncementSeeder()

        # 1. Çalıştırma
        report1 = seeder.seed(count=0)
        self.assertTrue(report1["created"] > 0)
        self.assertEqual(report1["existing"], 0)

        # 2. Çalıştırma
        report2 = seeder.seed(count=0)
        self.assertEqual(report2["created"], 0)
        self.assertEqual(report2["existing"], report1["created"])

    def test_master_database_seeder_and_clear(self):
        master = DatabaseSeeder()
        report = master.seed(users_count=3, announcements_count=2)
        self.assertEqual(report["status"], "success")
        self.assertTrue(report["users"]["total"] >= 3)
        self.assertTrue(report["announcements"]["total"] >= 2)

        # Temizleme testi
        deleted = master.clear()
        self.assertTrue(deleted > 0)
        self.assertEqual(UserProfile.objects.count(), 0)
        self.assertEqual(Announcement.objects.count(), 0)

    def test_seed_management_command(self):
        out = StringIO()
        call_command(
            "seed",
            users=2,
            announcements=2,
            no_input=True,
            stdout=out
        )
        output = out.getvalue()
        self.assertIn("VERİTABANI TOHUMLAMA", output)
        self.assertIn("BAŞARIYLA TAMAMLANDI", output)


class AnnouncementDatabaseCrudTestCase(TestCase):
    """
    Announcement CRUD operasyonlarının doğrudan veritabanı (Django ORM / SQLite)
    üzerinde çalıştığını doğrulayan kapsamlı entegrasyon testleri.
    """

    def setUp(self):
        self.client = Client()

    def test_announcement_db_service_crud(self):
        # 1. CREATE via DB service
        ann = announcement_service.create_announcement(
            title="DB Test Duyurusu",
            content="Veritabanına doğrudan yazılan duyuru içeriği...",
            author="Bilgi İşlem",
            category="Genel",
            is_active=True
        )
        self.assertIsNotNone(ann.id)
        self.assertTrue(Announcement.objects.filter(id=ann.id).exists())

        # 2. READ via DB service
        fetched = announcement_service.get_announcement(ann.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "DB Test Duyurusu")

        # 3. UPDATE / PATCH via DB service
        patched = announcement_service.patch_announcement(ann.id, title="Güncellenmiş DB Duyurusu")
        self.assertEqual(patched.title, "Güncellenmiş DB Duyurusu")
        
        # Veritabanında güncellendiğini teyit et
        db_record = Announcement.objects.get(id=ann.id)
        self.assertEqual(db_record.title, "Güncellenmiş DB Duyurusu")

        # 4. DELETE via DB service
        announcement_service.delete_announcement(ann.id)
        self.assertFalse(Announcement.objects.filter(id=ann.id).exists())

    def test_web_announcement_crud_via_db(self):
        # 1. CREATE via Web Form (POST)
        res_post = self.client.post("/announcements/create/", data={
            "title": "Web DB Entegrasyon Duyurusu",
            "content": "Web arayüzünden veritabanına eklenen duyuru metni.",
            "author": "Rektörlük",
            "category": "Etkinlik",
            "is_active": "true"
        })
        self.assertEqual(res_post.status_code, 201)
        
        # Veritabanında kaydın oluştuğunu teyit et
        created_ann = Announcement.objects.filter(title="Web DB Entegrasyon Duyurusu").first()
        self.assertIsNotNone(created_ann)
        self.assertEqual(created_ann.category, "Etkinlik")

        # 2. READ via Web List (GET)
        res_get = self.client.get("/announcements/")
        self.assertEqual(res_get.status_code, 200)
        self.assertContains(res_get, "Web DB Entegrasyon Duyurusu")

        # 3. DELETE via Web (POST _method=DELETE)
        res_del = self.client.post(f"/announcements/{created_ann.id}/delete/", data={"_method": "DELETE"})
        self.assertEqual(res_del.status_code, 200)
        self.assertFalse(Announcement.objects.filter(id=created_ann.id).exists())

    def test_api_announcement_crud_via_db(self):
        # 1. CREATE via REST API (POST)
        payload = {
            "title": "REST API DB Duyurusu",
            "content": "REST API ile veritabanına kaydedilen duyuru.",
            "author": "Kariyer Merkezi",
            "category": "Kariyer",
            "is_active": True
        }
        res_post = self.client.post(
            "/api/announcements/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(res_post.status_code, 201)
        post_data = res_post.json()
        self.assertEqual(post_data.get("status"), "success")
        ann_id = post_data["announcement"]["id"]

        # Veritabanında kontrol
        self.assertTrue(Announcement.objects.filter(id=ann_id).exists())

        # 2. DETAIL via REST API (GET)
        res_detail = self.client.get(f"/api/announcements/{ann_id}/")
        self.assertEqual(res_detail.status_code, 200)
        self.assertEqual(res_detail.json()["announcement"]["title"], "REST API DB Duyurusu")

        # 3. PATCH via REST API (PATCH)
        res_patch = self.client.patch(
            f"/api/announcements/{ann_id}/",
            data=json.dumps({"title": "API ile Başlık Değişti"}),
            content_type="application/json"
        )
        self.assertEqual(res_patch.status_code, 200)
        
        # Veritabanında güncellendiğini doğrula
        refreshed = Announcement.objects.get(id=ann_id)
        self.assertEqual(refreshed.title, "API ile Başlık Değişti")

        # 4. DELETE via REST API (DELETE)
        res_del = self.client.delete(f"/api/announcements/{ann_id}/")
        self.assertEqual(res_del.status_code, 200)
        self.assertFalse(Announcement.objects.filter(id=ann_id).exists())


