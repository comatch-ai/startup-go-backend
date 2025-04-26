from django.db import models
from django.contrib.auth.models import User
import uuid

class Project(models.Model):
    """
    Project model for storing startup project information.
    """
    STAGE_CHOICES = [
        ('pre_idea', 'Pre-Idea Exploration'),
        ('ideation', 'Ideation/Concept'),
        ('prototype', 'Prototype Development'),
        ('mvp', 'MVP'),
        ('pre_seed', 'Pre-Seed/Early Traction'),
        ('seed', 'Seed/Traction'),
        ('scaling', 'Scaling/Growth'),
        ('established', 'Established/Post Series-A'),
        ('expansion', 'Expansion/Post Series-B'),
        ('pivot', 'Pivot'),
    ]

    STARTUP_TYPE_CHOICES = [
        ('B2B', 'Business to Business'),
        ('B2C', 'Business to Consumer'),
        ('B2B2C', 'Business to Business to Consumer'),
        ('C2C', 'Consumer to Consumer'),
        ('B2G', 'Business to Government'),
        ('G2C', 'Government to Consumer'),
        ('Others', 'Others')
    ]

    BUSINESS_MODEL_CHOICES = [
        ('Freemium', 'Freemium'),
        ('Subscription', 'Subscription'),
        ('Marketplace', 'Marketplace'),
        ('SaaS', 'Software as a Service'),
        ('E-commerce', 'E-commerce'),
        ('Enterprise', 'Enterprise'),
        ('Advertising', 'Advertising'),
        ('Transaction', 'Transaction-based'),
        ('Licensing', 'Licensing'),
        ('Direct Sales', 'Direct Sales'),
        ('Others', 'Others')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=200)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    startup_type = models.CharField(max_length=50, choices=STARTUP_TYPE_CHOICES)
    business_model = models.JSONField(default=list)  # List of business models
    team_size = models.IntegerField(default=1)
    website = models.URLField(max_length=200, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.created_by.username}"

    class Meta:
        ordering = ['-created_at']
