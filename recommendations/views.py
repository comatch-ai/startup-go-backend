from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserProfileSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import Recommendation
from .serializers import RecommendationSerializer
from .service import RecommendationService
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union) if union else 0.0

def simple_text_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    text1 = text1.lower()
    text2 = text2.lower()
    if text1 == text2:
        return 1.0
    if text1 in text2 or text2 in text1:
        return 0.5
    return 0.0

class RecommendationView(APIView):
    """
    API endpoint for recommending users based on profile similarity.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Recommend users based on industry, role, location, skills, and goals.
        """
        current_user = request.user
        if not hasattr(current_user, 'profile'):
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        current_profile = current_user.profile
        users = User.objects.filter(profile__isnull=False).exclude(id=current_user.id)

        # 权重设置
        weights = {
            'industry': 2,
            'role': 2,
            'location': 1,
            'skills': 4,
            'goals': 1,
        }

        recommendations = []
        for user in users:
            profile = user.profile
            score = 0.0

            # 行业
            if current_profile.industry and profile.industry and current_profile.industry == profile.industry:
                score += weights['industry']

            # 角色
            if current_profile.role and profile.role and current_profile.role == profile.role:
                score += weights['role']

            # 地点
            if current_profile.location and profile.location and current_profile.location == profile.location:
                score += weights['location']

            # 技能 Jaccard 相似度
            skills1 = set([s.strip().lower() for s in current_profile.skills.split(',') if s.strip()]) if current_profile.skills else set()
            skills2 = set([s.strip().lower() for s in profile.skills.split(',') if s.strip()]) if profile.skills else set()
            skill_sim = jaccard_similarity(skills1, skills2)
            score += weights['skills'] * skill_sim

            # 目标文本相似度
            goal_sim = simple_text_similarity(current_profile.goals, profile.goals)
            score += weights['goals'] * goal_sim

            if score > 0:
                recommendations.append({
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'profile': UserProfileSerializer(user).data,
                    'score': round(score, 3)
                })

        # 按得分降序排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return Response(recommendations, status=status.HTTP_200_OK)

class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def get_recommendations(self, request):
        """
        Get personalized recommendations for the current user
        """
        try:
            # 初始化服务并加载 FAISS 索引
            service = RecommendationService()
            
            # 从 Git LFS 加载索引
            repo_path = getattr(settings, 'FAISS_INDEX_REPO_PATH', os.path.join(settings.BASE_DIR, 'faiss_indices'))
            index_path = getattr(settings, 'FAISS_INDEX_PATH', 'models/faiss_index')
            branch = getattr(settings, 'FAISS_INDEX_BRANCH', 'main')
            
            success = service.load_faiss_index_from_git_lfs(
                repo_path=repo_path,
                index_path=index_path,
                branch=branch
            )
            
            if not success:
                logger.warning("Failed to load FAISS index from Git LFS, falling back to default recommendations")
            
            recommendations = service.get_recommendations_for_user(
                user_id=request.user.id,
                top_k=10
            )
            
            return Response({
                'status': 'success',
                'data': recommendations
            })
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to get recommendations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_recommendations(self, request):
        """
        Trigger recommendation model update and save index to Git LFS
        """
        try:
            service = RecommendationService()
            service.update_recommendations()
            
            # 保存更新后的索引到 Git LFS
            repo_path = getattr(settings, 'FAISS_INDEX_REPO_PATH', os.path.join(settings.BASE_DIR, 'faiss_indices'))
            index_path = getattr(settings, 'FAISS_INDEX_PATH', 'models/faiss_index')
            
            success = service.save_faiss_index_to_git_lfs(
                repo_path=repo_path,
                index_path=index_path,
                commit_message="Update FAISS index with new recommendations"
            )
            
            if not success:
                logger.warning("Failed to save FAISS index to Git LFS")
            
            return Response({
                'status': 'success',
                'message': 'Recommendations update completed'
            })
            
        except Exception as e:
            logger.error(f"Error updating recommendations: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to update recommendations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def get_faiss_status(self, request):
        """
        Get the current status of FAISS index
        """
        try:
            service = RecommendationService()
            
            # 检查索引是否已加载
            if service.index_manager is None:
                return Response({
                    'status': 'not_initialized',
                    'message': 'FAISS index not initialized'
                })
                
            # 获取索引信息
            index_info = {
                'is_initialized': service.index_manager.index is not None,
                'index_type': type(service.index_manager.index).__name__,
                'num_vectors': service.index_manager.index.ntotal if service.index_manager.index else 0,
                'dimension': service.index_manager.embedding_dim,
                'use_gpu': service.index_manager.use_gpu
            }
            
            return Response({
                'status': 'success',
                'data': index_info
            })
            
        except Exception as e:
            logger.error(f"Error getting FAISS status: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to get FAISS status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def reload_faiss_index(self, request):
        """
        Reload FAISS index from Git LFS
        """
        try:
            service = RecommendationService()
            
            # 从 Git LFS 加载索引
            repo_path = getattr(settings, 'FAISS_INDEX_REPO_PATH', os.path.join(settings.BASE_DIR, 'faiss_indices'))
            index_path = getattr(settings, 'FAISS_INDEX_PATH', 'models/faiss_index')
            branch = getattr(settings, 'FAISS_INDEX_BRANCH', 'main')
            
            success = service.load_faiss_index_from_git_lfs(
                repo_path=repo_path,
                index_path=index_path,
                branch=branch
            )
            
            if success:
                return Response({
                    'status': 'success',
                    'message': 'FAISS index reloaded successfully'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to reload FAISS index'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error reloading FAISS index: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to reload FAISS index'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_faiss_index(self, request):
        """
        Update FAISS index with current user embeddings
        """
        try:
            service = RecommendationService()
            
            # 更新索引
            if service._update_faiss_index():
                # 保存更新后的索引到 Git LFS
                repo_path = getattr(settings, 'FAISS_INDEX_REPO_PATH', os.path.join(settings.BASE_DIR, 'faiss_indices'))
                index_path = getattr(settings, 'FAISS_INDEX_PATH', 'models/faiss_index')
                
                success = service.save_faiss_index_to_git_lfs(
                    repo_path=repo_path,
                    index_path=index_path,
                    commit_message="Update FAISS index with new embeddings"
                )
                
                if success:
                    return Response({
                        'status': 'success',
                        'message': 'FAISS index updated and saved successfully'
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'Failed to save updated FAISS index'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to update FAISS index'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error updating FAISS index: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to update FAISS index'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)