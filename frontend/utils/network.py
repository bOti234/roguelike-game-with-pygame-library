import requests

BASE_URL = "http://localhost:8000/pygame/"

# Since all functions here all look almost the same, I'm going to give a really detailed explanation, but only for the first one.

def register_user(endpoint, data, csrf_token):  # Getting the endpoint (the end of the url (here: 'register/'), the data, which is a dictionary that includes all necessary values for a registration, and the csrf-token)
    headers = { # Constructing the header for the request
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    cookies = {'csrftoken': csrf_token} # Constructing the cookies for the request. I had many problems with this csrf-token, so I'm including it in both of these.
    response = requests.post(BASE_URL + endpoint, json = data, headers = headers, cookies = cookies)    # Sending the request to the django server and waiting for a response.
    if response.status_code == 201 or response.status_code == 400:  # If the response is a message I sent (a success here is 201, an error is 400), I return the message.
        return response.json()
    else:
        response.raise_for_status() # Otherwise, I raise for status and return 'error'
        return "Error"

def login_user(endpoint, data, csrf_token):
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    cookies = {'csrftoken': csrf_token}
    response = requests.post(BASE_URL + endpoint, json = data, headers = headers, cookies = cookies)
    if response.status_code == 201 or response.status_code == 400:
        return response.json()
    else:
        response.raise_for_status()
        return "Error"

def logout_user(endpoint, data, csrf_token):
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    cookies = {'csrftoken': csrf_token}
    response = requests.post(BASE_URL + endpoint, json = data, headers = headers, cookies = cookies)
    if response.status_code == 201 or response.status_code == 400 or response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
        return "Error"

def update_user(endpoint, data, csrf_token):
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    cookies = {'csrftoken': csrf_token}
    response = requests.post(BASE_URL + endpoint, json = data, headers = headers, cookies = cookies)
    if response.status_code == 201 or response.status_code == 400:
        return response.json()
    else:
        response.raise_for_status()
        return "Error"

def get_scoreboard(endpoint):
    response = requests.get(BASE_URL + endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def post_score(endpoint, data, csrf_token):
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    cookies = {'csrftoken': csrf_token}
    response = requests.post(BASE_URL + endpoint, json = data, headers = headers, cookies = cookies)
    if response.status_code == 201:
        return response.json()
    else:
        response.raise_for_status()
        return "Error"
    
def get_csrf_token(endpoint):
    response = requests.get(BASE_URL + endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
        return "Error"