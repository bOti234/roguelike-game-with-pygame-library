import pytest
import os
import django
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.roguelikegame.settings")
django.setup()

from backend.game.models import Users, Scoreboard

class UserModelTests(TestCase):

    def setUp(self):
        self.user_data = {
            'player_name': 'testuser',
            'password': 'testPass123',
            'email': 'unique.testuser@example.com',
            'highscore': 0
        }

    def test_create_user(self):
        self.assertEqual(Users.objects.count(), 0)
        user = Users.objects.create(**self.user_data)
        self.assertEqual(Users.objects.count(), 1)

    def test_update_user(self):
        user = Users.objects.create(**self.user_data)
        user.player_name = 'Updated Name'
        user.save()
        self.assertEqual(user.player_name, 'Updated Name')

    def test_delete_user(self):
        user = Users.objects.create(**self.user_data)
        self.assertEqual(Users.objects.count(), 1)
        user.delete()
        self.assertEqual(Users.objects.count(), 0)

class ScoreboardModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'player_name': 'testuser',
            'password': 'testPass123',
            'email': 'unique.testuser@example.com',
            'highscore': 0
        }
        self.user = Users.objects.create(**self.user_data)

        self.score_data = {
            'player_name': 'testuser',
            'score': 0
        }

    def test_create_score(self):
        self.assertEqual(Scoreboard.objects.count(), 0)
        score = Scoreboard.objects.create(**self.score_data)
        self.assertEqual(Scoreboard.objects.count(), 1)

    def test_update_score(self):
        score = Scoreboard.objects.create(**self.score_data)
        score.score = 100
        score.save()
        self.assertEqual(score.score, 100)

    def test_delete_score(self):
        score = Scoreboard.objects.create(**self.score_data)
        self.assertEqual(Scoreboard.objects.count(), 1)
        score.delete()
        self.assertEqual(Scoreboard.objects.count(), 0)