import screeninfo
import subprocess
import time
import requests
from frontend.models.player import User
from frontend.models.game import Game
from frontend.utils.database import fetch_scoreboard

# Start Django server
server_process = subprocess.Popen(['python', 'backend/run_server.py'])

# Wait for the server to start up
time.sleep(5)  # Adjust the sleep time as necessary

# Check if the server is up by sending a request
try:
    requests.get('http://localhost:8000/pygame/scoreboard/')
    print("Django server is running.")
except requests.ConnectionError:
    print("Failed to connect to the Django server.")
    
# Fetching high scores
scoreboard = fetch_scoreboard()
# print(high_scores)

p1 = User("admin","12345")
game1 = Game()
game1.gameSetup(
	difficulty = "normal",
	speed = "normal", 
	fps = 60, 
	screen_width = screeninfo.get_monitors()[0].width, 
	screen_height = screeninfo.get_monitors()[0].height, 
	game_size = 40
	)
game1.openMainMenu()

# At the end of your script, make sure to terminate the server process
print("Stopping Django server")
server_process.terminate()