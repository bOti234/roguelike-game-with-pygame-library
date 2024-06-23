from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Users, Scoreboard
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# A form for registering a user.
class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Users
        fields = ['player_name', 'password1', 'password2', 'email', 'highscore']

    # This is  where I validate a password. It checks if it meets all requirements. 
    # The default is, that it needs at least one number. I added that it needs at least 8 characters as well
    def clean_password(self):   
        password = self.cleaned_data.get("password1")
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                self.add_error('password1', e)
        return password


# A form for logging in the user.
class UserLoginForm(forms.Form):
    player_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ['player_name', 'password']


# A form for updating a user.
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

# A form for updating/ssaving a score in the scoreboard.
class ScoreForm(forms.ModelForm):
    class Meta:
        model = Scoreboard
        fields = ['player_name', 'score']