import screeninfo
from src.models.player import User
from src.models.game import Game

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