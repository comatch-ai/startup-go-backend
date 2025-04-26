from django.urls import path
from .views import UserRegistrationView, UserLoginView

urlpatterns = [
    # User registration endpoint
    # POST /api/users/register/
    # Request body: {
    #     "username": "testuser",
    #     "email": "test@example.com",
    #     "password": "your_password",
    #     "password2": "your_password",
    #     "first_name": "Test",
    #     "last_name": "User"
    # }
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # User login endpoint
    # POST /api/users/login/
    # Request body: {
    #     "username": "testuser",
    #     "password": "your_password"
    # }
    path('login/', UserLoginView.as_view(), name='login'),
] 