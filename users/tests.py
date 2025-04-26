from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Profile
import json

class UserAPITests(TestCase):
    def setUp(self):
        """
        Set up test data.
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Set up API client
        self.client = APIClient()

    def test_user_registration(self):
        """
        Test user registration endpoint.
        """
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_user_registration_duplicate_username(self):
        """
        Test user registration with duplicate username.
        """
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Another',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_password_mismatch(self):
        """
        Test user registration with mismatched passwords.
        """
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login(self):
        """
        Test user login endpoint.
        """
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_user_login_invalid_credentials(self):
        """
        Test user login with invalid credentials.
        """
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_token_refresh(self):
        """
        Test token refresh endpoint.
        """
        # First login to get refresh token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Then try to refresh the token
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': refresh_token
        }
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_profile_creation(self):
        """
        Test profile creation endpoint.
        """
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Then create profile
        url = reverse('profile')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'profile': {
                'industry': 'Technology',
                'role': 'Software Engineer',
                'location': 'New York, USA',
                'skills': 'Python, Django, React',
                'goals': 'Build innovative solutions',
                'website': 'https://example.com',
                'social_links': {
                    'github': 'https://github.com/testuser',
                    'linkedin': 'https://linkedin.com/in/testuser'
                }
            }
        }
        
        # Since profile is automatically created by signal, we should use PUT instead of POST
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Profile.objects.count(), 1)
        print(response.data)
        self.assertEqual(response.data['profile']['industry'], 'Technology')

    def test_profile_update(self):
        """
        Test profile update endpoint.
        """
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Update profile
        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'profile': {
                'industry': 'FinTech',
                'role': 'Full Stack Developer',
                'location': 'San Francisco, USA',
                'skills': 'Python, Django, React, AWS',
                'goals': 'Lead development of innovative fintech solutions'
            }
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['profile']['industry'], 'FinTech')

    def test_profile_get(self):
        """
        Test profile retrieval endpoint.
        """
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Get profile
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['industry'], '')  # Profile is created with empty values
        self.assertEqual(response.data['profile']['role'], '')  # Profile is created with empty values
        self.assertEqual(response.data['profile']['location'], '')  # Profile is created with empty values
        self.assertEqual(response.data['profile']['skills'], '')  # Profile is created with empty values
        self.assertEqual(response.data['profile']['goals'], '')  # Profile is created with empty values

    def test_avatar_upload(self):
        """
        Test avatar upload endpoint.
        """
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Upload avatar
        url = reverse('avatar-upload')
        with open('test_avatar.jpg', 'rb') as avatar:
            data = {'avatar': avatar}
            response = self.client.post(url, data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('avatar', response.data)

    def test_unauthorized_profile_access(self):
        """
        Test unauthorized access to profile endpoints.
        """
        # Try to access profile without authentication
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to update profile without authentication
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'profile': {
                'industry': 'Technology'
            }
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
