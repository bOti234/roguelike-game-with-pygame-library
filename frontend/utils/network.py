import requests

BASE_URL = "http://localhost:8000/pygame/"

def register_user(username, password1, password2):
    url = f'{BASE_URL}/register/'
    data = {'username': username, 'password1': password1, 'password2': password2}
    response = requests.post(url, data=data)
    return response.json()

def login_user(username, password):
    url = f'{BASE_URL}/login/'
    data = {'username': username, 'password': password}
    response = requests.post(url, data=data)
    return response.json()

def logout_user():
    url = f'{BASE_URL}/logout/'
    response = requests.post(url)
    return response.json()

def get_data(endpoint):
    response = requests.get(BASE_URL + endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def post_data(endpoint, data):
    response = requests.post(BASE_URL + endpoint, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        response.raise_for_status()