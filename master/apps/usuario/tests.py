from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "Passw0rd!123"
        cls.user = User.objects.create_user(
            username="u1", email="u1@mail.com", password=cls.password
        )

    def test_register_get(self):
        r = self.client.get(reverse("register"))
        self.assertEqual(r.status_code, 200)

    def test_register_creates_user_and_redirects(self):
        payload = {
            "username": "u2",
            "email": "u2@mail.com",             
            "password1": "PassA12345!",
            "password2": "PassA12345!",
        }
        r = self.client.post(reverse("register"), payload)
        self.assertEqual(r.status_code, 302)      
        self.assertTrue(User.objects.filter(username="u2").exists())

    def test_login_ok(self):
        r = self.client.post(reverse("login"), {
            "username": "u1",
            "password": self.password
        })
        self.assertEqual(r.status_code, 302)


    def test_register_duplicate_email_shows_error(self):
        User.objects.create_user(username="otro", email="dup@mail.com", password="XyZ12345!")
        r = self.client.post(reverse("register"), {
            "username": "u3",
            "email": "dup@mail.com",             # duplicado
            "password1": "PassA12345!",
            "password2": "PassA12345!",
        })
        self.assertEqual(r.status_code, 200)     # se queda en el form
        self.assertContains(r, "ya está registrado")






