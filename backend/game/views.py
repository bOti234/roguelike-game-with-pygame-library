import json
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.views import View
from .models import Users, Scoreboard
from .forms import UserCreateForm, UserLoginForm, ScoreForm
from django.http import JsonResponse
from django.db.models import Q
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie


class UserView(View):
    form_class = UserCreateForm

    def post(self, request, *args, **kwargs):   # If I get a post request, I run different methods based on the requests path.
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
        data = json.loads(request.body) # Getting the dictionary with the data I sent.
        form = UserCreateForm(data) # Creating a form with the given data
        if not form.is_valid(): # Check if the data is correct (e.g. the player_name is not None, the password is valid, etc)
            return JsonResponse({'status': 'error', 'message': 'Registration failed, invalid user details', 'errors': form.errors}, status=400)   # Sending back a response
        
        user = form.save()  # Saving the user in the Users table
        login(request, user)    # Logging in the user
        userdata = {
            "player_name": user.player_name,
            "highscore": user.highscore
        }

        scoredata = {
            "player_name": user.player_name,
            "score": user.highscore
        }
        score_form = ScoreForm(scoredata)   # Creating a score form
        if score_form.is_valid():   # Checking it if it's valid
            score_form.save()   # Saving the score in the Scoreboard database
        return JsonResponse({'status': 'success', 'message': 'Registration successful', 'userdata': userdata}, status = 201)    # Sending back a response

    def login(self, request):
        data = json.loads(request.body)
        form = UserLoginForm(data)
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Login failed, invalid user details', 'errors': form.errors}, status=400)
        
        user = authenticate(    # Authenticating the user. It's not the same as form.is_valid()
            request = request,
            username = data['player_name'],
            password = data['password']
        )
        if user is None:
            return JsonResponse({'status': 'error', 'message': 'Login failed', 'errors': form.errors}, status=400)
        
        login(request, user)    # Logging in the user
        userdata = {
            "player_name": user.player_name,
            "password": data['password'],
            'email': user.email,
            "highscore": user.highscore
        }
        return JsonResponse({'status': 'success', 'message': 'Login successful', 'userdata': userdata}, status = 201)

    def logout(self, request):
        data = json.loads(request.body)
        user = Users.objects.get(player_name = data['player_name']) # Getting the user with the same name from the Users table
        if not user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=400)
        
        logout(request) # Logging out the user
        return JsonResponse({'status': 'success', 'message': 'Logout successful'}, status=200)

    def update(self, request):
        data = json.loads(request.body)
        try:
            user = Users.objects.get(player_name = data['old_player_name'])
        except Users.DoesNotExist:  # If the user with the same name doesn't exist, return an error
            return JsonResponse({'status': 'error', 'message': 'User entry does not exist!', 'errors': 'DoesNotExist'}, status=400)

        if not user.is_authenticated:   # If the user is not logged in, it returns an error
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=400)
        
        # Creating a user form with the original users instance, but with the new data. 
        # It overwrites the previous one, so it won't create a new line in the table
        update_data = {
            'player_name': data['player_name'],
            'password1': data['password1'],
            'password2': data['password2'],
            'email': data['email'],
            'highscore': user.highscore
        }
        form = UserCreateForm(update_data, instance = user)
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Update failed', 'errors': form.errors}, status=400)
        
        logout(request)
        updated_user = form.save()
        login(request, updated_user)
        userdata = {
            "player_name": updated_user.player_name,
            "password": updated_user.password,
            'email': updated_user.email,
            "highscore": updated_user.highscore
        }
        return JsonResponse({'status': 'success', 'message': 'User profile updated', 'userdata': userdata}, status = 201)
        
        

class ScoreboardView(View):
    def post(self, request, *args, **kwargs):   # Same type of method as in the UsersView
        if 'add_score' in request.path:
            return self.add_score(request)
        elif 'update_score' in request.path:
            return self.update_score(request)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
    
    def get(self, request):
        scores = Scoreboard.objects.all().order_by('-score')    # gets all score and orders by score in descending order
        score_list = list(scores.values('player_name', 'score', 'date_achieved'))   # Puts the user datas in a list of dictionaries
        return JsonResponse({'status': 'success', 'message': 'Scoreboard returned', 'scoreboard': score_list})
    
    def update_score(self, request):
        data = json.loads(request.body)
        try:
            score = Scoreboard.objects.get(player_name = data['player_name'])
        except Scoreboard.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Scoreboard entry does not exist for player'}, status=400)
        
        form = ScoreForm(data, instance = score)    # Creating a score form with the original scores instance, but with the new data. 
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Score update failed', 'errors': form.errors}, status=400)
        
        score = form.save() # Saves the new score
        score.date_achieved = timezone.now()    # Updates the date_achieved
        score.save()
        user = Users.objects.get(player_name = data['player_name'])
        user.highscore = data['score']  # Updates the score in the users row in the Users table
        user.save()     # Saving the user
        return JsonResponse({'status': 'success', 'message': 'Score updated successfully'}, status = 201)
        

    def add_score(self, request):
        data = json.loads(request.body)
        form = ScoreForm(data)
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Score addition failed', 'errors': form.errors}, status=400)
        
        score = form.save(commit=False)
        return JsonResponse({'status': 'success', 'message': 'Score added successfully'}, status = 201)

@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request) # Gets the csrf-token for any future requests. It's crazy to me how nobody else had the same issue as I had...
    return JsonResponse({'csrf_token': csrf_token}, status = 200)
