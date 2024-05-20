from .network import get_scoreboard, post_score, register_user, login_user, logout_user

def fetch_scoreboard():
    return get_scoreboard("scoreboard/")

def submit_score(player_name, score):
    data = {"player_name": player_name, "score": score}
    return post_score("submit-score/", data)

def submit_new_user(player_name, password1, password2, email, highscore):
    data = {"player_name": player_name, "password1": password1, "password2": password2, "email": email, "highscore": highscore}
    return register_user("register/", data)

def fetch_user(player_name, password):
    data = {"player_name": player_name, "password": password}
    return login_user("login/", data)

def submit_logout():
    return logout_user("logout/")