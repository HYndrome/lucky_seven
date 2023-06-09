from django.db import models
from django.conf import settings


# Create your models here.
class Meet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attend_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attend_meetings')
    name = models.CharField(max_length=50)
    content = models.CharField(max_length=300)
    date = models.DateField()

class Comment(models.Model):
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_user')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)