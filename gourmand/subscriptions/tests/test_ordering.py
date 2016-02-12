from django.contrib.auth.models import User
from django.test import TestCase, Client


class BasicViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_staff(self):
        pw = 'p@ssw0rd'
        staff = User.objects.create_superuser(username='adminuser', email='email@example.com', password=pw)
        self.client.login(username=staff.username, password=pw)
        self.client.get('/reader/')

    def test_user(self):
        pw = 'p@ssw0rd'
        user = User.objects.create_user(username='user', email='email@example.com', password=pw)
        self.client.login(username=user.username, password=pw)
        self.client.get('/reader/', follow=True)
