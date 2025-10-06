from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        self.signup_url = reverse('user-signup')
        self.login_url = reverse('user-login')

    def test_user_signup(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_user_signup_password_mismatch(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'differentpassword'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_user_login(self):
        # First create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        # Try to login
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_user_login_invalid_credentials(self):
        data = {
            'username': 'wronguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.profile_url = reverse('user-profile')

    def test_get_profile_authenticated(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
