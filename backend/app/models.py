from django.db import models
from django.contrib.auth.models import BaseUserManager

class ScoreBoard(models.Model):
    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    date_achieved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_name} - {self.score}"


class UserProfileManager(BaseUserManager):
    def create_user(self, player_name, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(player_name=player_name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Users(models.Model):
    player_name = models.CharField(max_length = 100, unique=True)
    password = models.CharField(max_length = 100)
    email = models.CharField(max_length = 100, unique=True)
    highscore = models.IntegerField()
    date_achieved = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) 

    USERNAME_FIELD = 'player_name'
    REQUIRED_FIELDS = []
    is_anonymous = False
    is_authenticated = False

    objects = UserProfileManager()

    def __str__(self):
        return self.player_name

    def check_password(self, password):
        if self.password == password:
            return True
        return False