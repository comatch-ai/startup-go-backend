from django.db import models

class Recommendation(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'
        unique_together = ('user', 'project')

    def __str__(self):
        return f'Recommendation for {self.project} by {self.user}'