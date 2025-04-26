from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Project
import json

class ProjectAPITests(TestCase):
    def setUp(self):
        """
        Set up test data.
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create another user for testing
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create test project
        self.project = Project.objects.create(
            title='Test Project',
            tagline='Test Tagline',
            description='Test Description',
            industry='Technology',
            stage='ideation',
            startup_type='B2C',
            business_model=['Freemium', 'Subscription'],
            team_size=3,
            website='https://example.com',
            social_links={'github': 'https://github.com/test'},
            equity=25.50,  # 25.5% equity
            funding='invested',
            tech_stack=['Python', 'Django', 'React', 'AWS'],
            market_traction=['1000+ users', '20% monthly growth', 'Partnership with Tech Corp'],
            created_by=self.user
        )
        
        # Set up API client
        self.client = APIClient()
        
        # Get authentication token
        self.client.force_authenticate(user=self.user)

    def test_create_project(self):
        """
        Test creating a new project.
        """
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'tagline': 'New Tagline',
            'description': 'New Description',
            'industry': 'FinTech',
            'stage': 'prototype',
            'startup_type': 'B2B',
            'business_model': ['SaaS', 'Subscription'],
            'team_size': 2,
            'website': 'https://newproject.com',
            'social_links': {
                'github': 'https://github.com/newproject',
                'linkedin': 'https://linkedin.com/company/newproject'
            },
            'equity': 15.75,  # 15.75% equity
            'funding': 'sponsored',
            'tech_stack': ['Node.js', 'MongoDB', 'React Native', 'Firebase'],
            'market_traction': ['500+ beta users', '15% conversion rate', 'Featured in Tech News']
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Project')
        self.assertEqual(response.data['created_by']['username'], 'testuser')
        self.assertEqual(response.data['equity'], '15.75')
        self.assertEqual(response.data['funding'], 'sponsored')
        self.assertEqual(response.data['tech_stack'], ['Node.js', 'MongoDB', 'React Native', 'Firebase'])
        self.assertEqual(response.data['market_traction'], ['500+ beta users', '15% conversion rate', 'Featured in Tech News'])
        
        # Verify project ID is added to creator's profile
        self.user.profile.refresh_from_db()
        self.assertIn(response.data['id'], self.user.profile.projects)

    def test_get_project_list(self):
        """
        Test getting list of projects.
        """
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_project_detail(self):
        """
        Test getting project details.
        """
        url = reverse('project-detail', args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Project')

    def test_update_project(self):
        """
        Test updating a project.
        """
        url = reverse('project-detail', args=[self.project.id])
        data = {
            'title': 'Updated Project',
            'tagline': 'Updated Tagline',
            'description': 'Updated Description',
            'industry': 'Technology',
            'stage': 'mvp',
            'startup_type': 'B2C',
            'business_model': ['Freemium'],
            'team_size': 4
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Updated Project')
        self.assertEqual(self.project.stage, 'mvp')

    def test_delete_project(self):
        """
        Test deleting a project.
        """
        url = reverse('project-detail', args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_filter_projects(self):
        """
        Test filtering projects.
        """
        # Create another project with different industry
        Project.objects.create(
            title='Another Project',
            tagline='Another Tagline',
            description='Another Description',
            industry='Healthcare',
            stage='ideation',
            startup_type='B2B',
            business_model=['Enterprise'],
            team_size=5,
            created_by=self.user
        )
        
        # Test filtering by industry
        url = reverse('project-list')
        response = self.client.get(url, {'industry': 'Technology'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filtering by stage
        response = self.client.get(url, {'stage': 'ideation'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Test filtering by startup type
        response = self.client.get(url, {'startup_type': 'B2B'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_projects(self):
        """
        Test searching projects.
        """
        url = reverse('project-list')
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthorized_access(self):
        """
        Test unauthorized access to projects.
        """
        # Create a new client without authentication
        client = APIClient()
        
        # Test getting project list
        url = reverse('project-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test getting project details
        url = reverse('project-detail', args=[self.project.id])
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_business_model(self):
        """
        Test creating project with invalid business model.
        """
        url = reverse('project-list')
        data = {
            'title': 'Invalid Project',
            'tagline': 'Invalid Tagline',
            'description': 'Invalid Description',
            'industry': 'Technology',
            'stage': 'ideation',
            'startup_type': 'B2C',
            'business_model': ['InvalidModel'],
            'team_size': 1
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_team_size(self):
        """
        Test creating project with invalid team size.
        """
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

    def test_invalid_equity(self):
        """
        Test creating project with invalid equity percentage.
        """
        url = reverse('project-list')
        data = {
            'title': 'Invalid Project',
            'tagline': 'Invalid Tagline',
            'description': 'Invalid Description',
            'industry': 'Technology',
            'stage': 'ideation',
            'startup_type': 'B2C',
            'business_model': ['Freemium'],
            'team_size': 1,
            'equity': 150.00,  # Invalid: over 100%
            'funding': 'self_funded'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('equity', response.data)

    def test_invalid_funding(self):
        """
        Test creating project with invalid funding type.
        """
        url = reverse('project-list')
        data = {
            'title': 'Invalid Project',
            'tagline': 'Invalid Tagline',
            'description': 'Invalid Description',
            'industry': 'Technology',
            'stage': 'ideation',
            'startup_type': 'B2C',
            'business_model': ['Freemium'],
            'team_size': 1,
            'equity': 25.00,
            'funding': 'invalid_funding'  # Invalid funding type
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('funding', response.data)

    def test_invalid_tech_stack(self):
        """
        Test creating project with invalid tech stack.
        """
        url = reverse('project-list')
        data = {
            'title': 'Invalid Project',
            'tagline': 'Invalid Tagline',
            'description': 'Invalid Description',
            'industry': 'Technology',
            'stage': 'ideation',
            'startup_type': 'B2C',
            'business_model': ['Freemium'],
            'team_size': 1,
            'equity': 25.00,
            'funding': 'self_funded',
            'tech_stack': 'Not a list'  # Invalid: should be a list
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tech_stack', response.data)

    def test_invalid_market_traction(self):
        """
        Test creating project with invalid market traction.
        """
        url = reverse('project-list')
        data = {
            'title': 'Invalid Project',
            'tagline': 'Invalid Tagline',
            'description': 'Invalid Description',
            'industry': 'Technology',
            'stage': 'ideation',
            'startup_type': 'B2C',
            'business_model': ['Freemium'],
            'team_size': 1,
            'equity': 25.00,
            'funding': 'self_funded',
            'market_traction': ['Not a string', 123]  # Invalid: should be list of strings
        }
        
        response = self.client.post(url, data, format='json')
        print("Response status:", response.status_code)
        print("Response data:", response.data)
        
        # First check if we get a 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Then check if the error message is about market_traction
        self.assertIn('market_traction', response.data)
        
        # Verify that the project was not created
        self.assertEqual(Project.objects.count(), 1)  # Only the original test project should exist
