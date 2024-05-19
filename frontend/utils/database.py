from .network import get_data, post_data

def fetch_scoreboard():
    return get_data("scoreboard/")

def submit_score(player_name, score):
    data = {"player_name": player_name, "score": score}
    return post_data("submit-score/", data)