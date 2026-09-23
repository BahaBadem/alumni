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



