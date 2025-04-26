from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    UserProfileSerializer,
    ProfileSerializer
)
from .models import Profile
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404

# Create your views here.

class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    
    This endpoint allows new users to register with the system.
    Upon successful registration, it returns JWT tokens for authentication.
    
    Sample API Request:
    POST /api/users/register/
    {
        "username": "testuser",
        "email": "test@example.com",
        "password": "your_password",
        "password2": "your_password",
        "first_name": "Test",
        "last_name": "User"
    }
    
    Sample API Response (201 Created):
    {
        "user": {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        },
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    
    Error Response (400 Bad Request):
    {
        "username": ["A user with this username already exists."],
        "password": ["This field is required."],
        "password2": ["This field is required."]
    }
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': serializer.data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """
    API endpoint for user login.
    
    This endpoint authenticates users and returns JWT tokens upon successful login.
    
    Sample API Request:
    POST /api/users/login/
    {
        "username": "testuser",
        "password": "your_password"
    }
    
    Sample API Response (200 OK):
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    
    Error Response (401 Unauthorized):
    {
        "error": "Invalid credentials"
    }
    """
    permission_classes = (AllowAny,)

    def post(self, request):

        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    """
    API endpoint for user profile management.
    
    This endpoint allows authenticated users to:
    1. Get their profile information
    2. Create a new profile (POST)
    3. Update their profile information including:
       - Basic info (first_name, last_name)
       - Professional info (industry, role, skills)
       - Personal info (bio, goals)
       - Contact info (location, website)
       - Social links and projects
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get the current user's profile.
        
        Returns:
            Response: User profile data including all fields:
                - Basic user info (id, username, email, name)
                - Professional info (industry, role, skills)
                - Personal info (bio, goals)
                - Contact info (location, website)
                - Social links and projects
        """
        # Ensure profile exists
        if not hasattr(request.user, 'profile'):
            Profile.objects.create(user=request.user)
            
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        """
        Create or initialize the user's profile.
        
        Args:
            request: The HTTP request containing profile data
            
        Returns:
            Response: Created profile data or validation errors
            
        Note:
            This endpoint is typically called after user registration
            to initialize the profile with additional information.
        """
        # Check if profile already exists
        if hasattr(request.user, 'profile'):
            return Response(
                {'error': 'Profile already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create profile if it doesn't exist
        if not hasattr(request.user, 'profile'):
            Profile.objects.create(user=request.user)

        serializer = UserProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(
                    UserProfileSerializer(user).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update the current user's profile.
        
        Args:
            request: The HTTP request containing profile update data
            
        Returns:
            Response: Updated user profile data or validation errors
            
        Possible validation errors:
            - skills: "Skills description is too long"
            - goals: "Goals description is too long"
            - industry: "This field is required" (if required=True)
            - role: "This field is required" (if required=True)
        """
        # Ensure profile exists
        if not hasattr(request.user, 'profile'):
            Profile.objects.create(user=request.user)

        serializer = UserProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AvatarUploadView(APIView):
    """
    API endpoint for uploading user avatar.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Upload or update the user's avatar.
        
        Args:
            request: The HTTP request containing the avatar file
            
        Returns:
            Response: Avatar URL or error message
            
        Possible errors:
            - "No avatar file provided"
            - "Invalid file type" (if file validation is added)
        """
        # Ensure profile exists
        if not hasattr(request.user, 'profile'):
            Profile.objects.create(user=request.user)

        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = request.user.profile
        profile.avatar = request.FILES['avatar']
        profile.save()

        return Response({
            'avatar': profile.avatar.url
        })

class UserProfileView(APIView):
    """
    API endpoint for querying user profiles by username.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        """
        Get a user's profile by username.
        
        Args:
            request: The HTTP request
            username: The username of the user whose profile to retrieve
            
        Returns:
            Response: User profile data or error message
            
        Possible errors:
            - "User not found" (404)
            - "Profile not found" (404)
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ensure profile exists
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
            
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

class UserProfileListView(APIView):
    """
    API endpoint for listing all user profiles.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get a list of all user profiles.
        
        Args:
            request: The HTTP request
            
        Returns:
            Response: List of user profiles
            
        Query Parameters:
            - industry: Filter by industry
            - role: Filter by role
            - location: Filter by location
            - skills: Filter by skills (comma-separated)
            - startup_stage: Filter by startup stage
        """
        # Get all users with profiles
        users = User.objects.filter(profile__isnull=False)
        
        # Apply filters if provided
        industry = request.query_params.get('industry')
        if industry:
            users = users.filter(profile__industry=industry)
            
        role = request.query_params.get('role')
        if role:
            users = users.filter(profile__role=role)
            
        location = request.query_params.get('location')
        if location:
            users = users.filter(profile__location=location)
            
        skills = request.query_params.get('skills')
        if skills:
            skills_list = [skill.strip() for skill in skills.split(',')]
            for skill in skills_list:
                users = users.filter(profile__skills__icontains=skill)
                
        startup_stage = request.query_params.get('startup_stage')
        if startup_stage:
            users = users.filter(profile__startup_stage=startup_stage)
        
        # Serialize the results
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)

class AddFriendView(APIView):
    """
    API endpoint to add a friend by user ID.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        friend_id = request.data.get('friend_id')
        if not friend_id:
            return Response({'error': 'friend_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            friend = User.objects.get(id=friend_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        profile = request.user.profile
        if friend.id in profile.friends:
            return Response({'error': 'Already friends'}, status=status.HTTP_400_BAD_REQUEST)
        profile.friends.append(friend.id)
        profile.save()
        return Response({'success': f'User {friend.username} added as a friend.'}, status=status.HTTP_200_OK)

class RemoveFriendView(APIView):
    """
    API endpoint to remove a friend by user ID.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        friend_id = request.data.get('friend_id')
        if not friend_id:
            return Response({'error': 'friend_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        profile = request.user.profile
        if friend_id not in profile.friends:
            return Response({'error': 'User is not in your friends list'}, status=status.HTTP_400_BAD_REQUEST)
        profile.friends.remove(friend_id)
        profile.save()
        return Response({'success': f'User {friend_id} removed from friends.'}, status=status.HTTP_200_OK)

class FriendMatchView(APIView):
    """
    API endpoint to get mutual friends (users who are friends with the current user and vice versa).
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_id = user.id
        profile = user.profile
        friends_ids = profile.friends
        mutual_friends = []
        for fid in friends_ids:
            try:
                friend_profile = Profile.objects.get(user_id=fid)
                if user_id in friend_profile.friends:
                    mutual_friends.append(fid)
            except Profile.DoesNotExist:
                continue
        return Response({'mutual_friends': mutual_friends}, status=status.HTTP_200_OK)
