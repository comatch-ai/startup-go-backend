from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model in project responses.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    """
    created_by = UserSerializer(read_only=True)
    business_model = serializers.ListField(
        child=serializers.ChoiceField(choices=Project.BUSINESS_MODEL_CHOICES),
        required=False
    )

    class Meta:
        model = Project
        fields = (
            'id',
            'title',
            'tagline',
            'description',
            'industry',
            'stage',
            'startup_type',
            'business_model',
            'team_size',
            'website',
            'social_links',
            'created_by',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_team_size(self, value):
        """
        Validate team size.
        """
        if value < 1:
            raise serializers.ValidationError("Team size must be at least 1.")
        return value

    def validate_business_model(self, value):
        """
        Validate business model choices.
        """
        valid_models = [choice[0] for choice in Project.BUSINESS_MODEL_CHOICES]
        for model in value:
            if model not in valid_models:
                raise serializers.ValidationError(
                    f"Invalid business model: {model}. Must be one of: {', '.join(valid_models)}"
                )
        return value

    def create(self, validated_data):
        """
        Create a new project.
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data) 