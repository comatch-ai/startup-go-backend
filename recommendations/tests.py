from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from users.models import Profile
import os
import shutil
import tempfile
from django.conf import settings
from .service import RecommendationService
from .faiss_utils import FAISSIndexManager

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

class FAISSViewTests(TestCase):
    def setUp(self):
        """Set up test environment"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.test_dir, 'test_repo')
        os.makedirs(self.repo_path)
        
        # 初始化 Git 仓库
        os.chdir(self.repo_path)
        os.system('git init')
        os.system('git lfs install')
        
        # 设置测试配置
        self.original_repo_path = getattr(settings, 'FAISS_INDEX_REPO_PATH', None)
        self.original_index_path = getattr(settings, 'FAISS_INDEX_PATH', None)
        settings.FAISS_INDEX_REPO_PATH = self.repo_path
        settings.FAISS_INDEX_PATH = 'test_index'
        
    def tearDown(self):
        """Clean up test environment"""
        # 恢复原始配置
        if self.original_repo_path:
            settings.FAISS_INDEX_REPO_PATH = self.original_repo_path
        if self.original_index_path:
            settings.FAISS_INDEX_PATH = self.original_index_path
            
        # 清理临时目录
        shutil.rmtree(self.test_dir)
        
    def test_get_faiss_status_not_initialized(self):
        """Test getting FAISS status when not initialized"""
        url = reverse('faiss-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'not_initialized')
        
    def test_get_faiss_status_initialized(self):
        """Test getting FAISS status when initialized"""
        # 初始化 FAISS 索引
        service = RecommendationService()
        service.index_manager = FAISSIndexManager(embedding_dim=384 + 2 + 15)
        
        url = reverse('faiss-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        self.assertIn('is_initialized', response.data['data'])
        
    def test_reload_faiss_index(self):
        """Test reloading FAISS index"""
        url = reverse('faiss-reload')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
    def test_update_faiss_index(self):
        """Test updating FAISS index"""
        url = reverse('faiss-update')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
    def test_faiss_integration(self):
        """Test full FAISS integration flow"""
        # 1. 检查初始状态
        status_url = reverse('faiss-status')
        response = self.client.get(status_url)
        self.assertEqual(response.data['status'], 'not_initialized')
        
        # 2. 更新索引
        update_url = reverse('faiss-update')
        response = self.client.post(update_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. 检查更新后的状态
        response = self.client.get(status_url)
        self.assertEqual(response.data['status'], 'success')
        
        # 4. 重新加载索引
        reload_url = reverse('faiss-reload')
        response = self.client.post(reload_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. 再次检查状态
        response = self.client.get(status_url)
        self.assertEqual(response.data['status'], 'success')

class RecommendationViewTests(TestCase):
    def setUp(self):
        """Set up test environment"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_get_recommendations(self):
        """Test getting recommendations"""
        url = reverse('recommendation-get-recommendations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        
    def test_update_recommendations(self):
        """Test updating recommendations"""
        url = reverse('recommendation-update-recommendations')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')