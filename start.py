import screeninfo
from app import game, createServer

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