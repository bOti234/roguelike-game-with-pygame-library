import screeninfo
import subprocess
import time
import requests
from frontend.models.game import Game
from frontend.utils.database import fetch_scoreboard, get_csrf

# Start Django server
server_process = subprocess.Popen(['python', 'backend/run_server.py'])

# Wait for the server to start up
time.sleep(3)  # Adjust the sleep time as necessary

# Check if the server is up by sending a request
try:
    response = requests.get('http://localhost:8000/pygame/scoreboard/')
    response.raise_for_status()
    print("Django server is running.")
    
    csrf_token = get_csrf()['csrf_token']
    if csrf_token:
        print(f'CSRF Token from cookies: {csrf_token}')
    else:
        print("No csrf token found in the cookies.")
except requests.ConnectionError:
    print("Failed to connect to the Django server.")
    
# Fetching high scores
scoreboard = fetch_scoreboard()
# print(high_scores)

game1 = Game(csrf_token)
game1.gameStart(
	difficulty = "normal",
	speed = "normal", 
	fps = 60, 
	screen_width = screeninfo.get_monitors()[0].width, 
	screen_height = screeninfo.get_monitors()[0].height, 
	game_size = 40
	)

# At the end of your script, make sure to terminate the server process
print("Stopping Django server")
server_process.terminate()