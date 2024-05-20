from django.contrib.auth.backends import BaseBackend
from .models import Users

class UserProfileBackend(BaseBackend):
    def authenticate(self, username = None, password = None):
        try:
            user = Users.objects.get(player_name = username)
            if user.password == password:
                return user
        except Users.DoesNotExist:
            print("miafene")
            return None

    def get_user(self, user_id):
        try:
            return Users.objects.get(pk = user_id)
        except Users.DoesNotExist:
            return None