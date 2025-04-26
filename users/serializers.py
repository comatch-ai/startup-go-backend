from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.
    """
    friends = serializers.ListField(child=serializers.IntegerField(), read_only=True)

    class Meta:
        model = Profile
        fields = (
            'bio', 
            'avatar', 
            'industry',
            'role',
            'location', 
            'skills',
            'goals',
            'website', 
            'social_links', 
            'projects',
            'experience_years',
            'startup_stage',
            'seeking_roles',
            'friends',
        )
        extra_kwargs = {
            'bio': {'required': False},
            'avatar': {'required': False},
            'industry': {'required': False},
            'role': {'required': False},
            'location': {'required': False},
            'skills': {'required': False},
            'goals': {'required': False},
            'website': {'required': False},
            'social_links': {'required': False},
            'projects': {'required': False},
            'experience_years': {'required': False},
            'startup_stage': {'required': False},
            'seeking_roles': {'required': False},
            # 'friends': {'required': False},
        }

    def validate_skills(self, value):
        """
        Validate skills field.
        """
        if value and len(value) > 1000:  # Arbitrary limit, adjust as needed
            raise serializers.ValidationError("Skills description is too long.")
        return value

    def validate_goals(self, value):
        """
        Validate goals field.
        """
        if value and len(value) > 1000:  # Arbitrary limit, adjust as needed
            raise serializers.ValidationError("Goals description is too long.")
        return value

    def validate_experience_years(self, value):
        """
        Validate experience_years field.
        """
        if value < 0:
            raise serializers.ValidationError("Experience years cannot be negative.")
        return value

    def validate_startup_stage(self, value):
        """
        Validate startup_stage field.
        """
        valid_stages = [choice[0] for choice in Profile.STAGE_CHOICES]
        if value and value not in valid_stages:
            raise serializers.ValidationError(f"Invalid startup stage. Must be one of: {', '.join(valid_stages)}")
        return value

    def validate_seeking_roles(self, value):
        """
        Validate seeking_roles field.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Seeking roles must be a list.")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for combining User and Profile data.
    """
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile')
        read_only_fields = ('id', 'username', 'email')

    def create(self, validated_data):
        """
        Create a new profile for an existing user.
        
        Args:
            validated_data: Dictionary containing profile data
            
        Returns:
            User: User instance with updated profile
        """
        profile_data = validated_data.pop('profile', {})
        user = self.context['request'].user
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update Profile fields
        profile = user.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        return user

    def update(self, instance, validated_data):
        """
        Update an existing user profile.
        """
        profile_data = validated_data.pop('profile', {})
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update Profile fields
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate_username(self, value):
        """
        Check if username is already taken.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, attrs):
        """
        Validate that both passwords match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance with an associated profile.
        """
        validated_data.pop('password2')
        try:
            # Create the user
            user = User.objects.create_user(**validated_data)
            
            # Ensure profile exists
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)
            
            return user
        except IntegrityError:
            raise serializers.ValidationError({"username": "A user with this username already exists."})

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True) 