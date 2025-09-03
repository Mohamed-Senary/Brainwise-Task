from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class AccountsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse("register_user")
        self.token_url = reverse("token_obtain_pair")

        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "StrongPass123",
            "role": User.Roles.EMPLOYEE,
        }

    def test_user_can_signup(self):
        """Test user registration works"""
        response = self.client.post(self.signup_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, self.user_data["email"])

    def test_user_can_login_and_get_tokens(self):
        """Test login with valid credentials returns JWT tokens"""
        User.objects.create_user(**self.user_data)  # create user first
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.token_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_fails_with_wrong_password(self):
        """Test login fails with wrong password"""
        User.objects.create_user(**self.user_data)
        login_data = {
            "email": self.user_data["email"],
            "password": "WrongPass",
        }
        response = self.client.post(self.token_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_contains_role_claim(self):
        """Test JWT token contains role in payload"""
        user = User.objects.create_user(**self.user_data)
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.token_url, login_data, format="json")
        access_token = response.data["access"]

        # Decode without verifying signature (safe for tests)
        decoded = AccessToken(access_token)

        self.assertEqual(decoded["role"], user.role)
