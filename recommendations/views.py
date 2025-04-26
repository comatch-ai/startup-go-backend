from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserProfileSerializer

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

        recommendations = []
        for user in users:
            profile = user.profile
            score = 0

            # Calculate similarity score
            if current_profile.industry and current_profile.industry == profile.industry:
                score += 1
            if current_profile.role and current_profile.role == profile.role:
                score += 1
            if current_profile.location and current_profile.location == profile.location:
                score += 1
            if current_profile.skills and profile.skills:
                current_skills = set(current_profile.skills.split(','))
                other_skills = set(profile.skills.split(','))
                score += len(current_skills & other_skills)  # Intersection of skills
            if current_profile.goals and profile.goals:
                score += 1 if current_profile.goals in profile.goals or profile.goals in current_profile.goals else 0

            if score > 0:
                recommendations.append({
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'profile': UserProfileSerializer(user).data,
                    'score': score
                })

        # Sort recommendations by score in descending order
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return Response(recommendations, status=status.HTTP_200_OK)