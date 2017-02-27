from django.test import TestCase
from django.test import Client

class BasicLoadTestCase(TestCase):

    def test_front_page_loads(self):
        c = Client()
        r = c.get('/')
        self.assertEqual(r.status_code, 200)

    def test_about_loads(self):
        c = Client()
        r = c.get('/about')
        self.assertEqual(r.status_code, 200)

    def test_all_sponsors_loads(self):
        c = Client()
        r = c.get('/sponsors')
        self.assertEqual(r.status_code, 200)

    def test_404(self):
        c = Client()
        r = c.get('/xxx')
        self.assertEqual(r.status_code, 404)



