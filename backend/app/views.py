from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views import View
from .models import ScoreBoard
import json


class UserView(View):
    @csrf_exempt
    def register(self, request):
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)
                return JsonResponse({'status': 'success', 'message': f'Account created for {username}!'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors})
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

    @csrf_exempt
    def login_view(self, request):
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return JsonResponse({'status': 'success', 'message': f'You are now logged in as {username}.'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid username or password.'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors})
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

    @csrf_exempt
    def logout_view(self, request):
        if request.method == 'POST':
            logout(request)
            return JsonResponse({'status': 'success', 'message': 'You have successfully logged out.'})
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

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