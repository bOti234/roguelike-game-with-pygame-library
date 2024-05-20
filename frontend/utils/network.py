import requests

BASE_URL = "http://localhost:8000/pygame/"

def register_user(endpoint, data):
    response = requests.post(BASE_URL + endpoint, json = data)
    if response.status_code == 201 or response.status_code == 400:
        return response.json()
    else:
        response.raise_for_status()
        return "Error"

def login_user(endpoint, data):
    response = requests.post(BASE_URL + endpoint, json = data)
    if response.status_code == 201 or response.status_code == 400:
        return response.json()
    else:
        response.raise_for_status()
        return "Error"

def logout_user(endpoint):
    response = requests.post(BASE_URL + endpoint)
    if response.status_code == 201:
        return response.json()
    else:
        response.raise_for_status()

def get_scoreboard(endpoint):
    response = requests.get(BASE_URL + endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def post_score(endpoint, data):
    response = requests.post(BASE_URL + endpoint, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        response.raise_for_status()