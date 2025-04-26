from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer

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
        "username": ["This field is required."],
        "password": ["This field is required."],
        "password2": ["This field is required."]
    }
    """
    permission_classes = (AllowAny,)

    def post(self, request):

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
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
