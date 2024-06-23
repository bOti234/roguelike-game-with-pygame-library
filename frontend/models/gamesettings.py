# These are the game setting. 
# I could've included these in the Game class, but it's jsut nicer to keep the settings values in a separate class. 

class GameSettings():
	def __init__(self, difficulty: str = "normal", speed: int = 300, fps: int = 60, screen_width: int = 800, screen_height: int = 600, game_size: int = 40):
		self.difficulty: str = difficulty
		self.speed: int = speed
		self.fps: int = fps
		self.screen_width: int = screen_width
		self.screen_height: int = screen_height
		self.fullscreen_width: int = screen_width
		self.fullscreen_height: int = screen_height
		self.game_size: int = game_size
		self.mastervolume = 0.5 	# If the music gets really annoying (and it probably will 😅), you can just set this to 0. You can also change the volume within the game.
		self.musicvolume = 0.5
		self.gamesoundvolume = 0.5