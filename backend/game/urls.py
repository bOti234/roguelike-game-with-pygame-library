from django.urls import path
from .views import UserView, ScoreboardView, get_csrf_token

urlpatterns = [
    path('register/', UserView.as_view(), name='register'),
    path('login/', UserView.as_view(), name='login'),
    path('logout/', UserView.as_view(), name='logout'),
    path('update/', UserView.as_view(), name = 'update'),
    path('update_score/', ScoreboardView.as_view(), name='update_score'),
    path('scoreboard/', ScoreboardView.as_view(), name='scoreboard'),
    path('submit-score/', ScoreboardView.as_view(), name='add_score'),
    path('gettoken/', get_csrf_token, name = 'gettoken')
]