from django.contrib.auth.models import User
from django.test import TestCase, Client


class BrandingTest(TestCase):
    def test_frontpage(self):
        pw = 'p@ssw0rd'
        user = User.objects.create_user(username='user', email='email@example.com', password=pw)
        self.client = Client()
        response = self.client.get('/')
        self.assertContains(response, 'Gourmand RSS Reader')
        self.client.login(username=user.username, password=pw)
        response = self.client.get('/')
        self.assertRedirects(response, '/reader/')
