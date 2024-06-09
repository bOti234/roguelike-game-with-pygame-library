import screeninfo
import subprocess
import time
import requests
from frontend.models.game import Game
#from frontend.utils.database import fetch_scoreboard, get_csrf

# Start Django server
server_process = subprocess.Popen(['python', 'backend/run_server.py'])

# Wait for the server to start up
time.sleep(2)  # Adjust the sleep time as necessary

# Check if the server is up by sending a request
try:
    response = requests.get('http://localhost:8000/pygame/gettoken/')
    response.raise_for_status()
    csrf_token = response.json()['csrf_token']
    print("Django server is running.")
except requests.ConnectionError:
    print("Failed to connect to the Django server.")

game1 = Game()
game1.gameStart(
	difficulty = "normal",
	speed = "normal", 
	fps = 60, 
	screen_width = screeninfo.get_monitors()[0].width,
	screen_height = screeninfo.get_monitors()[0].height,
    csrf_token = csrf_token
	)

# At the end of your script, make sure to terminate the server process
print("Stopping Django server")
server_process.terminate()