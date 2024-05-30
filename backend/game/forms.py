from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Users, Scoreboard

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Users
        fields = ['player_name', 'password1', 'password2', 'email']

class UserLoginForm(forms.Form):
    player_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ['player_name', 'password']

class UserUpdateForm(forms.Form):
    player_name = forms.CharField(max_length=100)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Users
        fields = ['player_name', 'password', 'email']

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Scoreboard
        fields = ['score']