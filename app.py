import subprocess
import time
import requests
import screeninfo
from frontend.models.game import Game

game = Game()

def createServer():
    # Start Django server
    server_process = subprocess.Popen(['python', 'backend/run_server.py'])

    # Wait for the server to start up
    time.sleep(2)  # Adjust the sleep time as necessary

    # Check if the server is up by sending a request
    try:
        response = requests.get('http://localhost:8000/pygame/gettoken/')
        response.raise_for_status()
        print("Django server is running.")
    except requests.ConnectionError:
        print("Failed to connect to the Django server.")

    return server_process


if __name__ == "__main__":
    server_process = createServer()
    game.gameStart(
        difficulty = "normal",
        speed = "normal", 
        fps = 60, 
        screen_width = screeninfo.get_monitors()[0].width,
        screen_height = screeninfo.get_monitors()[0].height
    )

    # At the end of your script, we terminate the server process
    print("Stopping Django server")
    server_process.terminate()