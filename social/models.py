from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models


class Account(AbstractUser, models.Model):
    user_details = JSONField(null=True)

    def __str__(self):
        return self.username


class Post(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='posts')
    date_time_created = models.DateTimeField(auto_now_add=True)
    post_title = models.CharField(max_length=255, default='', unique=True)
    post_content = models.TextField(default='')

    def __str__(self):
        return self.post_title


class Like(models.Model):
    related_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    related_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = (('related_post', 'related_user'),)
