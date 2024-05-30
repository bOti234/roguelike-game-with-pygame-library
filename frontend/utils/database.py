from .network import get_scoreboard, post_score, register_user, login_user, logout_user, update_user, get_csrf_token

def fetch_scoreboard():
    return get_scoreboard("scoreboard/")

def submit_score(player_name, score, csrf_token):
    data = {"player_name": player_name, "score": score}
    return post_score("update_score/", data, csrf_token)

def submit_new_user(player_name, password1, password2, email, highscore, csrf_token):
    data = {"player_name": player_name, "password1": password1, "password2": password2, "email": email, "highscore": highscore}
    return register_user("register/", data, csrf_token)

def fetch_user(player_name, password, csrf_token):
    data = {"player_name": player_name, "password": password}
    return login_user(endpoint = "login/", data = data, csrf_token = csrf_token)

def submit_update_user(old_player_name, player_name, password, email, csrf_token):
    data = {"old_player_name": old_player_name, "player_name": player_name, "password1": password, "password2": password, "email": email}
    return update_user('update/', data, csrf_token)

def submit_logout(player_name, csrf_token):
    data = {"player_name": player_name}
    return logout_user("logout/", data, csrf_token)

def get_csrf():
    return get_csrf_token('gettoken/')