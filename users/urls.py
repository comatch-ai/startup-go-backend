from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    ProfileView,
    AvatarUploadView,
    UserProfileView,
    UserProfileListView
)

urlpatterns = [
    # User registration endpoint
   
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # User login endpoint
    
    path('login/', UserLoginView.as_view(), name='login'),
    
    # Profile management endpoints
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='avatar-upload'),
    path('users/<str:username>/profile/', UserProfileView.as_view(), name='user-profile'),
    path('users/profiles/', UserProfileListView.as_view(), name='user-profile-list'),
] 