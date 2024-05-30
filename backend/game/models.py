from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

class UsersManager(BaseUserManager):
    def create_user(self, email, player_name, password=None, highscore = 0):
        if not email:
            raise ValueError('The Email field must be set')
        if not player_name:
            raise ValueError('The Player Name field must be set')
        email = self.normalize_email(email)
        user = self.model(email = email, player_name = player_name, highscore = highscore)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, player_name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser has to have is_staff being True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser has to have is_superuser being True')
        
        user = self.create_user(email = email, player_name = player_name, password = password, **extra_fields)
        user.is_admin = True
        user.save(using=self._db)
        return user

class Users(AbstractBaseUser):
    player_name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    highscore = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UsersManager()

    USERNAME_FIELD = 'player_name'

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin
    
    class Meta:
        db_table = 'Users'

class Scoreboard(models.Model):
    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    date_achieved = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.player_name} - {self.score}'
    
    class Meta:
        db_table = 'Scoreboard'