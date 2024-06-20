import json
import pytest
import os
import django
from django.test import TestCase
from django.urls import reverse
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.roguelikegame.settings")
django.setup()

from backend.game.models import Scoreboard, Users

class UserViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_data = {
            'player_name': 'testuser',
            'password': 'testPass123',
            'email': 'unique.testuser@example.com',
            'highscore': 0
        }
        self.user = Users.objects.create_user(**self.user_data)
        self.client.login(player_name = self.user_data['player_name'], password = self.user_data['password'])

    def test_register_view(self):
        url = reverse('register')
        data = {
            'player_name': 'newuser',
            'password1': 'newPass123',
            'password2': 'newPass123',
            'email': 'newuser@example.com',
            'highscore': 0
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('userdata', response.json())

        # Test for invalid registration
        response_invalid = self.client.post(url, json.dumps({'invalid': 'data'}), content_type='application/json')
        self.assertEqual(response_invalid.status_code, 400)
        self.assertIn('errors', response_invalid.json())

    def test_login_view(self):
        url = reverse('login')
        data = {
            'player_name': self.user_data['player_name'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('userdata', response.json())

        # Test for invalid login
        data_invalid = {
            'player_name': 'invaliduser',
            'password': 'invalidPass123'
        }
        response_invalid = self.client.post(url, json.dumps(data_invalid), content_type='application/json')
        self.assertEqual(response_invalid.status_code, 400)
        self.assertIn('errors', response_invalid.json())

    def test_update_user_view(self):
        url = reverse('update')
        data = {
            'old_player_name': self.user_data['player_name'],
            'player_name': 'updated_user',
            'password1': 'newPass123',
            'password2': 'newPass123',
            'email': 'updated_user@example.com',
            'highscore': 100
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('userdata', response.json())
        self.assertEqual(response.json()['userdata']['player_name'], 'updated_user')
        self.assertEqual(response.json()['userdata']['email'], 'updated_user@example.com')
        self.assertEqual(response.json()['userdata']['highscore'], 100)

        # Test for invalid update
        invalid_data = {
            'old_player_name': 'nonexistent_player',
            'player_name': 'invalid_user',
            'password1': 'newPass123',
            'password2': 'newPass123',
            'email': 'invalid_user@example.com',
            'highscore': 200
        }
        response_invalid = self.client.post(url, json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response_invalid.status_code, 400)
        self.assertIn('errors', response_invalid.json())

    def test_logout_view(self):
        self.client.login(username=self.user_data['player_name'], password=self.user_data['password'])
        url = reverse('logout')
        data = {'player_name': self.user_data['player_name']}
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

class ScoreboardViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_data = {
            'player_name': 'testuser',
            'password': 'testPass123',
            'email': 'unique.testuser@example.com',
            'highscore': 0
        }
        self.user = Users.objects.create_user(**self.user_data)
        self.client.login(username = self.user_data['player_name'], password = self.user_data['password'])
        self.scoreboard_entry, created = Scoreboard.objects.get_or_create(player_name=self.user_data['player_name'], defaults={'score': 0})

    def test_add_score_view(self):
        url = reverse('add_score')
        data = {
            'player_name': self.user_data['player_name'],
            'score': 100
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # Test for invalid score addition
        response_invalid = self.client.post(url, json.dumps({'invalid': 'data'}), content_type='application/json')
        self.assertEqual(response_invalid.status_code, 400)

    def test_update_score_view(self):
        
        url = reverse('update_score')
        data = {
            'player_name': self.user_data['player_name'],
            'score': 150
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.scoreboard_entry.refresh_from_db()
        assert self.scoreboard_entry.score == data['score']

        # Test for invalid score update
        invalid_data = {
            'player_name': 'nonexistent_player',
            'score': 150
        }
        response_invalid = self.client.post(url, json.dumps(invalid_data), content_type='application/json')
        self.assertEqual(response_invalid.status_code, 400)

    def test_get_scoreboard_view(self):
        url = reverse('scoreboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('scoreboard', response.json())

    def test_get_csrf_token_view(self):
        url = reverse('gettoken')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('csrf_token', response.json())
        self.assertIsNotNone(response.json()['csrf_token'])