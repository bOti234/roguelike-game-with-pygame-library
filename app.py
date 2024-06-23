import subprocess
import time
import requests
import screeninfo
from frontend.models.game import Game

game = Game()

def createServer():
    # Starting the Django server
    server_process = subprocess.Popen(['python', 'run_server.py'])

    # Waiting for the server to start up
    time.sleep(2)

    # Checking if the server is up by sending a request
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
        screen_width = screeninfo.get_monitors()[0].width,  # ⬅️Setting the screen width to fullscreen
        screen_height = screeninfo.get_monitors()[0].height # ⬅️Setting the screen height to fullscreen
    )

    # At the end of your script, we terminate the server process
    print("Stopping Django server")
    server_process.terminate()