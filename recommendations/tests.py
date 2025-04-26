from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from users.models import Profile

class RecommendationTests(TestCase):
    def setUp(self):
        """
        Set up test data.
        """
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user1.profile.industry = 'Technology'
        self.user1.profile.role = 'Developer'
        self.user1.profile.location = 'New York'
        self.user1.profile.skills = 'Python, Django'
        self.user1.profile.goals = 'Build innovative solutions'
        self.user1.profile.save()

        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.user2.profile.industry = 'Technology'
        self.user2.profile.role = 'Developer'
        self.user2.profile.location = 'San Francisco'
        self.user2.profile.skills = 'Python, React'
        self.user2.profile.goals = 'Contribute to open source'
        self.user2.profile.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_recommendations(self):
        """
        Test user recommendations endpoint.
        """
        url = reverse('recommendations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'user2')
        self.assertGreater(response.data[0]['score'], 0)