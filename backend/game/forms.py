from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Users, Scoreboard
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Users
        fields = ['player_name', 'password1', 'password2', 'email', 'highscore']

    def clean_password(self):
        password = self.cleaned_data.get("password1")
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                self.add_error('password1', e)
        return password

class UserLoginForm(forms.Form):
    player_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ['player_name', 'password']

class UserUpdateForm(forms.ModelForm):
    player_name = forms.CharField(max_length=100)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Users
        fields = ['player_name', 'password', 'email']

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                self.add_error('password', e)
        return password

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Scoreboard
        fields = ['player_name', 'score']