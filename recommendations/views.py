from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserProfileSerializer

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