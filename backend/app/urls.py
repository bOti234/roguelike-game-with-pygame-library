from django.urls import path
from .views import ScoreBoardView, UserView

urlpatterns = [
    path('scoreboard/', ScoreBoardView.as_view(), name='scoreboard'),
    path('register/', UserView.register, name='register'),
    path('login/', UserView.login_view, name='login'),
    path('logout/', UserView.logout_view, name='logout'),
]