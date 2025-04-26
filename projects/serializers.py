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
    tech_stack = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    market_traction = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
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
            'equity',
            'funding',
            'tech_stack',
            'market_traction',
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

    def validate_equity(self, value):
        """
        Validate equity percentage.
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError("Equity must be between 0 and 100.")
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

    def validate_tech_stack(self, value):
        """
        Validate tech stack items.
        """
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Tech stack must be a list of strings.")
        for item in value:
            if not isinstance(item, str):
                raise serializers.ValidationError("Each tech stack item must be a string.")
        return value

    def validate_market_traction(self, value):
        """
        Validate market traction items.
        """
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Market traction must be a list of strings.")
        for item in value:
            if not isinstance(item, str):
                raise serializers.ValidationError("Each market traction item must be a string.")
        return value

    def validate(self, data):
        """
        Validate the entire data set.
        """
        # Validate tech_stack
        tech_stack = data.get('tech_stack', [])
        if not isinstance(tech_stack, list):
            raise serializers.ValidationError({"tech_stack": "Tech stack must be a list of strings."})
        for item in tech_stack:
            if not isinstance(item, str):
                raise serializers.ValidationError({"tech_stack": "Each tech stack item must be a string."})

        # Validate market_traction
        market_traction = data.get('market_traction', [])
        if not isinstance(market_traction, list):
            raise serializers.ValidationError({"market_traction": "Market traction must be a list of strings."})
        for item in market_traction:
            if not isinstance(item, str):
                raise serializers.ValidationError({"market_traction": "Each market traction item must be a string."})

        return data

    def create(self, validated_data):
        """
        Create a new project.
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data) 