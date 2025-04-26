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

    def test_invalid_team_size(self):
        """
        Test creating project with invalid team size.
        """
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        url = reverse('project-list')
        data = {
            'title': 'Invalid Project',
            'tagline': 'Invalid Tagline',
            'description': 'Invalid Description',
            'industry': 'Technology',
            'stage': 'ideation',
            'startup_type': 'B2C',
            'business_model': ['Freemium'],
            'team_size': 0
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_profile(self):
        """
        Test getting a user's profile by username.
        """
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Get profile by username
        url = reverse('user-profile', args=['testuser'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['profile']['industry'], '')
        self.assertEqual(response.data['profile']['role'], '')
        self.assertEqual(response.data['profile']['location'], '')

    def test_get_nonexistent_user_profile(self):
        """
        Test getting profile for a non-existent user.
        """
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Try to get profile for non-existent user
        url = reverse('user-profile', args=['nonexistentuser'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found')

    def test_get_user_profile_unauthorized(self):
        """
        Test getting user profile without authentication.
        """
        # Create a new client without authentication
        client = APIClient()
        
        # Try to get profile without authentication
        url = reverse('user-profile', args=['testuser'])
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile_list(self):
        """
        Test getting list of all user profiles.
        """
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Get all profiles
        url = reverse('user-profile-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one user in test setup

    def test_get_user_profile_list_with_filters(self):
        """
        Test getting filtered list of user profiles.
        """
        # Create another user with different profile
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Update the existing profile (created by signal)
        other_user.profile.industry = 'Healthcare'
        other_user.profile.role = 'Doctor'
        other_user.profile.location = 'Boston, USA'
        other_user.profile.skills = 'Medicine, Research'
        other_user.profile.startup_stage = 'ideation'
        other_user.profile.save()
        
        # First login to get token
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        
        # Test filtering by industry
        url = reverse('user-profile-list')
        response = self.client.get(url, {'industry': 'Healthcare'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['profile']['industry'], 'Healthcare')
        
        # Test filtering by role
        response = self.client.get(url, {'role': 'Doctor'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['profile']['role'], 'Doctor')
        
        # Test filtering by location
        response = self.client.get(url, {'location': 'Boston, USA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['profile']['location'], 'Boston, USA')
        
        # Test filtering by skills
        response = self.client.get(url, {'skills': 'Medicine'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'otheruser')
        
        # Test filtering by startup stage
        response = self.client.get(url, {'startup_stage': 'ideation'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'otheruser')
        
        # Test multiple filters
        response = self.client.get(url, {
            'industry': 'Healthcare',
            'role': 'Doctor',
            'location': 'Boston, USA'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'otheruser')

    def test_get_user_profile_list_unauthorized(self):
        """
        Test getting user profile list without authentication.
        """
        # Create a new client without authentication
        client = APIClient()
        
        # Try to get profile list without authentication
        url = reverse('user-profile-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
