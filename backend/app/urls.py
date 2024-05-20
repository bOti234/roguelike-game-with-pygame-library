from django.urls import path
from .views import ScoreBoardView, UserView

urlpatterns = [
    path('scoreboard/', ScoreBoardView.as_view(), name='scoreboard'),
    path('register/', UserView.as_view(), name='register'),
    path('login/', UserView.as_view(), name='login'),
    path('logout/', UserView.as_view(), name='logout'),
]