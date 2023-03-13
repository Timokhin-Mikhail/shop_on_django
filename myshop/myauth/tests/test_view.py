from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="admin", password="admin", )

    def test_login_page(self):
        response = self.client.get(reverse('myauth:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "myauth/login.html")
        self.client.login(username="admin", password="admin")
        response = self.client.get(reverse('myauth:login'))
        self.assertEqual(response.status_code, 302)

    def test_logout_page(self):
        response = self.client.get(reverse('myauth:logout'))
        self.assertEqual(response.status_code, 302)

    def test_registr_page(self):
        response = self.client.get(reverse('myauth:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "myauth/register.html")