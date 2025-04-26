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
        Create a new project.
        """
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """
        Update a project.
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a project.
        """
        instance.delete()
