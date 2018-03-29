from django.test import SimpleTestCase
from django.test import Client

class BasicLoadTestCase(SimpleTestCase):

    #######################################################
    # Front page

    def test_front_page_loads(self):
        c = Client()
        r = c.get('/')
        self.assertEqual(r.status_code, 200)

    def test_front_page_all_loads(self):
        c = Client()
        r = c.get('/?all')
        self.assertEqual(r.status_code, 200)

    def test_sponsors_with_no_trials_not_shown(self):
        c = Client()
        r = c.get('/?all')
        self.assertNotContains(r, '<a href="/sponsor/unclear-sponsor-name-given">')

    def test_front_page_search_loads(self):
        c = Client()
        r = c.get('/?search')
        self.assertEqual(r.status_code, 200)

    def test_front_page_screenshot_page_loads(self):
        c = Client()
        r = c.get('/screenshot')
        self.assertEqual(r.status_code, 200)

    def test_front_page_screenshot_image_loads(self):
        c = Client()
        r = c.get('/screenshot-0003.png')
        self.assertEqual(r.status_code, 200)


    #######################################################
    # Sponsor page

    def test_sponsor_page_loads(self):
        c = Client()
        r = c.get('/sponsor/pirkanmaa-hospital')
        self.assertEqual(r.status_code, 200)

    def test_sponsor_screenshot_page_loads(self):
        c = Client()
        r = c.get('/sponsor/pirkanmaa-hospital/screenshot')
        self.assertEqual(r.status_code, 200)

    def test_sponsor_screenshot_image_loads(self):
        c = Client()
        r = c.get('/sponsor/pirkanmaa-hospital/screenshot.png')
        self.assertEqual(r.status_code, 200)


    #######################################################
    # About page

    def test_about_loads(self):
        c = Client()
        r = c.get('/about')
        self.assertEqual(r.status_code, 200)


    #######################################################
    # Error page

    def test_404(self):
        c = Client()
        r = c.get('/xxx')
        self.assertEqual(r.status_code, 404)
