from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Profile model that extends the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    website = models.URLField(max_length=200, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    projects = models.JSONField(default=list, blank=True)  # List of project IDs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a profile when a new user is created.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the profile when the user is saved.
    """
    instance.profile.save()
