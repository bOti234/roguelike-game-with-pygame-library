import json
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import Users, Scoreboard
from .forms import UserCreateForm, UserLoginForm, UserUpdateForm, ScoreForm
from django.http import JsonResponse
from django.db.models import Q
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie


class UserView(View):
    form_class = UserCreateForm

    def post(self, request, *args, **kwargs):
        if 'register' in request.path:
            return self.register(request)
        elif 'login' in request.path:
            return self.login(request)
        elif 'logout' in request.path:
            return self.logout(request)
        elif 'update' in request.path:
            return self.update(request)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

    def register(self, request):
        data = json.loads(request.body)
        form = UserCreateForm(data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            userdata = {
                "player_name": user.player_name,
                "highscore": user.highscore
            }

            scoredata = {
                "player_name": user.player_name,
                "score": user.highscore
            }
            score_form = ScoreForm(scoredata)
            if score_form.is_valid():
                score_form.save()
            return JsonResponse({'status': 'success', 'message': 'Registration successful', 'userdata': userdata}, status = 201)
        return JsonResponse({'status': 'error', 'message': 'Registration failed', 'errors': form.errors}, status=400)

    def login(self, request):
        data = json.loads(request.body)
        form = UserLoginForm(data)
        if form.is_valid():
            user = authenticate(
                request = request,
                username = data['player_name'],
                password = data['password']
            )
            if user is not None:
                login(request, user)
                userdata = {
                    "player_name": user.player_name,
                    "password": data['password'],
                    'email': user.email,
                    "highscore": user.highscore
                }
                return JsonResponse({'status': 'success', 'message': 'Login successful', 'userdata': userdata}, status = 201)
        return JsonResponse({'status': 'error', 'message': 'Login failed', 'errors': form.errors}, status=400)

    def logout(self, request):
        data = json.loads(request.body)
        user = Users.objects.get(player_name = data['player_name'])
        if user.is_authenticated:
            logout(request)
            return JsonResponse({'status': 'success', 'message': 'Logout successful'}, status=200)
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=400)

    def update(self, request):
        data = json.loads(request.body)
        user = Users.objects.get(player_name = data['old_player_name'])
        if user.is_authenticated:
            form = UserCreateForm(data, instance = user)
            if form.is_valid():
                logout(request)
                updated_user = form.save()
                login(request, user)
                userdata = {
                    "player_name": updated_user.player_name,
                    "password": updated_user.password,
                    'email': updated_user.email,
                    "highscore": updated_user.highscore
                }
                return JsonResponse({'status': 'success', 'message': 'User profile updated', 'userdata': userdata}, status = 201)
            return JsonResponse({'status': 'error', 'message': 'Update failed', 'errors': form.errors}, status=400)
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=400)

class ScoreboardView(View):
    def post(self, request, *args, **kwargs):
        if 'add_score' in request.path:
            return self.add_score(request)
        elif 'update_score' in request.path:
            return self.update_score(request)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
    
    def get(self, request):
        scores = Scoreboard.objects.all().order_by('-score')
        score_list = list(scores.values('player_name', 'score', 'date_achieved'))
        return JsonResponse({'status': 'success', 'message': 'Scoreboard returned', 'scoreboard': score_list})
    
    def update_score(self, request):
        data = json.loads(request.body)
        score = Scoreboard.objects.get(player_name = data['player_name'])
        form = ScoreForm(data, instance = score)
        if form.is_valid():
            score = form.save()
            user = Users.objects.get(player_name = data['player_name'])
            user.highscore = data['score']
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Score updated successfully'}, status = 201)
        return JsonResponse({'status': 'error', 'message': 'Score update failed', 'errors': form.errors}, status=400)

    def add_score(self, request):
        data = json.loads(request.body)
        form = ScoreForm(data)
        if form.is_valid():
            score = form.save(commit=False)
            return JsonResponse({'status': 'success', 'message': 'Score added successfully'}, status = 201)
        return JsonResponse({'status': 'error', 'message': 'Score addition failed', 'errors': form.errors}, status=400)

@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token}, status = 200)