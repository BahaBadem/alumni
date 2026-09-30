import json
from django.test import TestCase, Client


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



