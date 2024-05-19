from django.db import models
from django.contrib.auth.models import User

class ScoreBoard(models.Model):
    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    date_achieved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_name} - {self.score}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    additional_field = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username