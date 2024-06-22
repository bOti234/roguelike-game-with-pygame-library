import pytest
import os
import django
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.roguelikegame.settings")
django.setup()

from backend.game.forms import Users, UserCreateForm, UserLoginForm, UserUpdateForm, ScoreForm

class UserCreateFormTests(TestCase):

    def setUp(self):
        self.user_data = {
            'player_name': 'testuser',
            'password1': 'testPass123',
            'password2': 'testPass123',
            'email': 'unique.testuser@example.com',
            'highscore': 0
        }

    def test_correct_form(self):
        form = UserCreateForm(data = self.user_data)
        self.assertTrue(form.is_valid())

    def test_incorrect_form(self):
        self.user_data['password1'] = 'not_the_same_pass'
        form = UserCreateForm(data = self.user_data)
        self.assertTrue((not form.is_valid()))

class UserLoginFormTests(TestCase):

    def setUp(self):
        self.user_data = {
            'player_name': 'testuser',
            'password': 'testPass123'
        }

    def test_correct_form(self):
        form = UserLoginForm(data = self.user_data)
        self.assertTrue(form.is_valid())

    def test_incorrect_form(self):
        self.user_data['player_name'] = ''
        form = UserLoginForm(data = self.user_data)
        self.assertTrue((not form.is_valid()))

class UserUpdateFormTests(TestCase):

    def setUp(self):
        self.user_data = {
            'player_name': 'testuser',
            'password': 'testPass123',
            'email':'unique.testuser@example.com',
        }

    def test_correct_form(self):
        form = UserUpdateForm(data = self.user_data)
        self.assertTrue(form.is_valid())

    def test_incorrect_form(self):
        self.user_data['password'] = 'short'
        form = UserUpdateForm(data = self.user_data)
        self.assertTrue((not form.is_valid()))

class ScoreFormTests(TestCase):

    def setUp(self):
        self.score_data = {
            'player_name': 'testuser',
            'score': 100
        }

    def test_correct_form(self):
        form = ScoreForm(data = self.score_data)
        self.assertTrue(form.is_valid())

    def test_incorrect_form(self):
        self.score_data['score'] = 1.1
        form = ScoreForm(data = self.score_data)
        self.assertTrue((not form.is_valid()))