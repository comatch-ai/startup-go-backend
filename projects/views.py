from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project
from .serializers import ProjectSerializer
from .filters import ProjectFilter

# Create your views here.

class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'tagline', 'description', 'industry']
    ordering_fields = ['created_at', 'updated_at', 'team_size']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return all projects.
        """
        return Project.objects.all()

    def perform_create(self, serializer):
        """
        Create a new project and add it to the creator's profile.
        """
        project = serializer.save(created_by=self.request.user)
        
        # Add project ID to creator's profile
        profile = self.request.user.profile
        if not profile.projects:
            profile.projects = []
        profile.projects.append(str(project.id))
        profile.save()

    def perform_update(self, serializer):
        """
        Update a project.
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a project and remove it from the creator's profile.
        """
        # Remove project ID from creator's profile
        profile = instance.created_by.profile
        if profile.projects and str(instance.id) in profile.projects:
            profile.projects.remove(str(instance.id))
            profile.save()
        
        # Delete the project
        instance.delete()
