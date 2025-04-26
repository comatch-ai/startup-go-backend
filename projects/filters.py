from django_filters import rest_framework as filters
from .models import Project

class ProjectFilter(filters.FilterSet):
    """
    Custom filter for Project model.
    """
    business_model = filters.CharFilter(method='filter_business_model')

    def filter_business_model(self, queryset, name, value):
        """
        Custom filter method for business_model JSONField.
        """
        # Convert the value to a string and use contains lookup
        return queryset.filter(business_model__contains=value)

    class Meta:
        model = Project
        fields = {
            'industry': ['exact'],
            'stage': ['exact'],
            'startup_type': ['exact'],
            'business_model': ['exact'],
        } 