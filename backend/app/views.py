import json
import hashlib
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views import View
from .models import ScoreBoard, Users
from django.utils.decorators import method_decorator


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Users
        fields = ("player_name", "password1", "password2", "email")

class CustomUserLoginForm(forms.Form):
    player_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):

    def post(self, request, *args, **kwargs):
        if 'register' in request.path:
            return self.register(request)
        elif 'login' in request.path:
            return self.login_view(request)
        elif 'logout' in request.path:
            return self.logout_view(request)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

    def register(self, request):
        data = json.loads(request.body)
        form = CustomUserCreationForm(data)
        print(data)
        if form.is_valid():
            form.save()
            hashed_password = hashlib.md5(data["password1"].encode()).hexdigest()
            user = authenticate(username = data["player_name"], password = hashed_password)
            if user is not None:
                new_user = Users(player_name = data["player_name"], password = hashed_password, email = data["email"], highscore = data["highscore"], is_active = True)
                new_user.save()
                login(request, new_user)
                user_profile_data = {
                    'player_name': new_user.player_name,
                    'email': new_user.email,
                    'highscore': new_user.highscore
                }
                return JsonResponse({'status': 'success', 'message': f'Account created for {data["player_name"]}!', "userdata": user_profile_data}, status = 201)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid username, password or email.'}, status = 400)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status = 400)

    def login_view(self, request):
        data = json.loads(request.body)
        form = CustomUserLoginForm(data)
        print(data)
        if form.is_valid():
            hashed_password = hashlib.md5(data["password"].encode()).hexdigest()
            user = authenticate(username = data["player_name"], password = hashed_password)
            if user is not None:
                login(request, user)
                user_profile_data = {
                    'player_name': user.player_name,
                    'email': user.email,
                    'highscore': user.highscore
                }
                return JsonResponse({'status': 'success', 'message': f'You are now logged in as {data["player_name"]}!', "userdata": user_profile_data}, status = 201)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid username or password.'}, status = 400)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status = 400)

    def logout_view(self, request):
        logout(request)
        return JsonResponse({'status': 'success', 'message': 'You have successfully logged out.'})

class ScoreBoardView(View):

    def get(self, request):
        scores = ScoreBoard.objects.all().values('player_name', 'score')
        scores_list = list(scores)
        return JsonResponse(scores_list, safe=False)

    @csrf_exempt
    def post(self, request):
        try:
            data = json.loads(request.body)
            new_score = ScoreBoard(player_name=data['player_name'], score=data['score'])
            new_score.save()
            return JsonResponse({'status': 'success'}, status=201)
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)