import os
import pygame
from typing import List, Dict, Union
from ..utils.database import fetch_user, submit_new_user, submit_logout, submit_update_user, submit_score

class HUD():
	def __init__(self, screen, screen_width, screen_height):
		self.screen: pygame.Surface = screen
		self.screen_width = screen_width
		self.screen_height = screen_height

class StatBar(HUD):
	def __init__(self, screen, screen_width, screen_height, stat_type, x, y, width, height, stat_background_rgba, trasparent_screen, border_width, border_radius, stat_colour, border_colour = "black"):
		super().__init__(screen, screen_width, screen_height)
		self.stat_type = stat_type
		self.border_rect = pygame.rect.Rect(x, y, width, height)
		self.stat_rect = pygame.rect.Rect(x + border_width, y + border_width, width - border_width*2, height - border_width*2)
		self.stat_background_rgba = stat_background_rgba
		self.trasparent_screen = trasparent_screen
		self.border_colour = border_colour
		self.border_width = border_width
		self.border_radius = border_radius
		self.stat_colour = stat_colour

	def draw(self, newWidth):
		self.stat_rect.width = newWidth

		pygame.draw.rect(self.screen, self.stat_colour, self.stat_rect, 0, self.border_radius)
		pygame.draw.rect(self.screen, self.border_colour, self.border_rect, self.border_width, self.border_radius)
		
	def drawTransparent(self):
		pygame.draw.rect(self.trasparent_screen, self.stat_background_rgba, self.border_rect, 0, self.border_radius)

class Inventory(HUD):
	def __init__(self):
		pass

class Menu(HUD):
	def __init__(self, screen, screen_width, screen_height):
		super().__init__(screen, screen_width, screen_height)
		self.opened = False
		self.state = None

	def openMainMenu(self, csrf_token, userdata = None):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../assets/images/buttons/')
			play_img = pygame.image.load(filename+"/button_play.png").convert_alpha()
			quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()
			back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

			#create button instances
			scale = 0.2
			font = pygame.font.Font(None, 30)
			menuX = self.screen_width/4
			menuY = self.screen_height/5
			
			play_button = Button(self.screen_width/2 - play_img.get_width()/2 * scale, menuY + 175, play_img, scale)
			quit_button = Button(self.screen_width/2 - quit_img.get_width()/2 * scale, menuY + 475, quit_img, scale)

			if userdata:
				logout_img = pygame.image.load(filename+"/button_logout.png").convert_alpha()
				update_img = pygame.image.load(filename+"/button_updateuser.png").convert_alpha()

				welocme_text_box = pygame.Rect(self.screen_width/2 - font.size("Welcome back, "+userdata["player_name"]+"!")[0]/2, menuY + 50, font.size("Welcome back, "+userdata["player_name"]+"!")[0], font.get_linesize()*2)
				welocme_text_button = Button(welocme_text_box.x, welocme_text_box.y, [font, "Welcome back, "+userdata["player_name"]+"!", "white", welocme_text_box], 1)
				
				highscore_text_box = pygame.Rect(self.screen_width/2 - font.size("Current highscore: "+str(userdata["highscore"]))[0]/2, menuY + 50 + font.get_linesize()*2 + 1, font.size("Current highscore: "+str(userdata["highscore"]))[0], font.get_linesize()*2)
				highscore_text_button = Button(highscore_text_box.x, highscore_text_box.y, [font, "Current highscore: "+str(userdata["highscore"]), "white", highscore_text_box], 1)
				
				
				log_button = Button(self.screen_width/2 - logout_img.get_width()/2 * scale, menuY + 275, logout_img, scale)
				user_button = Button(self.screen_width/2 - update_img.get_width()/2 * scale, menuY + 375, update_img, scale)
			else:
				login_img = pygame.image.load(filename+"/button_login.png").convert_alpha()
				create_img = pygame.image.load(filename+"/button_createuser.png").convert_alpha()

				welocme_text_box = pygame.Rect(self.screen_width/2 - font.size("Play as guest!")[0]/2, menuY + 50, font.size("Play as guest!")[0], font.get_linesize()*2)
				welocme_text_button = Button(welocme_text_box.x, welocme_text_box.y, [font, "Play as guest!", "white", welocme_text_box], 1)
				log_button = Button(self.screen_width/2 - login_img.get_width()/2 * scale, menuY + 275, login_img, scale)
				user_button = Button(self.screen_width/2 - create_img.get_width()/2 * scale, menuY + 375, create_img, scale)

			username_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 100, 30 * font.size("_")[0], font.get_linesize()*2, font, "username", "username...")
			password_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 175, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password...")
			password2_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 250, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password again...")
			email_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 325, 30 * font.size("_")[0], font.get_linesize()*2, font, "email", "email address...")
			back_button = Button(self.screen_width/2 - back_img.get_width()/2 * scale, self.screen_height/4 + 475, back_img, scale)

			#game loop
			run = True
			logchange = False
			button_timeout = 100
			while run:
				if button_timeout > 0:
					button_timeout -= 1
				self.screen.fill("black")
				window = pygame.Rect(menuX, menuY, self.screen_width - 2*menuX, self.screen_height - 2*menuY)
				pygame.draw.rect(self.screen, (52, 78, 91), window)

				#check menu state
				if self.state == "inMainMenu":
					welocme_text_button.drawText(self.screen)
					if userdata:
						highscore_text_button.drawText(self.screen)

					#draw pause screen buttons
					if play_button.draw(self.screen):
						return ("start game", userdata)
					
					if log_button.draw(self.screen):
						if userdata:
							response = submit_logout(userdata['player_name'], csrf_token)
							if response['status'] == 'success':
								userdata = None
								logchange = True
								run = False
						else:
							log_button.rect.y = menuY + 400
							self.state = "logInMenu"

					if user_button.draw(self.screen):
						if userdata:
							user_button.rect.y = menuY + 450
							self.state = 'updateMenu'
						else:
							user_button.rect.y = menuY + 450
							self.state = "createMenu"

					if quit_button.draw(self.screen):
						if button_timeout <= 0:
							run = False
							return ("exit", userdata)
				
				if self.state == "logInMenu":
					username_textbox.draw(self.screen), password_textbox.draw(self.screen)

					if log_button.draw(self.screen):
						response = fetch_user(username_textbox.text, password_textbox.text, csrf_token)
						if response["status"] == "error":
							username_textbox.reset(), password_textbox.reset(), password2_textbox.reset(), email_textbox.reset()
							self.state == "logInMenu"
							button_timeout = 100
						else:
							userdata = response["userdata"]
							print(userdata)
							self.state = "inMainMenu"
							logchange = True
							run = False

					if back_button.draw(self.screen):
						log_button.rect.y = menuY + 275
						self.state = "inMainMenu"
						button_timeout = 100

				if self.state == "updateMenu":
					username_textbox.draw(self.screen), password_textbox.draw(self.screen), email_textbox.draw(self.screen)

					if user_button.draw(self.screen):
						username = username_textbox.text if username_textbox.text != "" else userdata['player_name']
						password = password_textbox.text if password_textbox.text != "" else userdata['password']
						email = email_textbox.text if email_textbox.text != "" else userdata['email']
						response = submit_update_user(userdata['player_name'], username, password, email, csrf_token)
						if response["status"] == "error":
							print(response['message'])
							username_textbox.reset(), password_textbox.reset(), email_textbox.reset()
							self.state == "updateMenu"
							button_timeout = 100
						else:
							userdata = response["userdata"]
							self.state = "inMainMenu"
							logchange = True
							run = False
					
					if back_button.draw(self.screen):
						user_button.rect.y = menuY + 375
						self.state = "inMainMenu"
						button_timeout = 100

				if self.state == "createMenu":
					username_textbox.draw(self.screen), password_textbox.draw(self.screen), password2_textbox.draw(self.screen), email_textbox.draw(self.screen)

					if user_button.draw(self.screen):
						response = submit_new_user(username_textbox.text, password_textbox.text, password2_textbox.text, email_textbox.text, 0, csrf_token)
						if response["status"] == "error":
							username_textbox.reset(), password_textbox.reset(), password2_textbox.reset(), email_textbox.reset()
							self.state == "createMenu"
							button_timeout = 100
						else:
							userdata = response["userdata"]
							self.state = "inMainMenu"
							logchange = True
							run = False

					if back_button.draw(self.screen):
						user_button.rect.y = menuY + 375
						self.state = "inMainMenu"
						button_timeout = 100
				
				#event handler
				for event in pygame.event.get():
					if self.state == "logInMenu" or self.state == "createMenu" or self.state == 'updateMenu':
						username_textbox.handle_event(event)
						password_textbox.handle_event(event)
						if self.state == "createMenu" or self.state == 'updateMenu':
							email_textbox.handle_event(event)
							if self.state == "createMenu":
								password2_textbox.handle_event(event)
							
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

			if logchange:
				return self.openMainMenu(csrf_token, userdata)

	def openInGameMenu(self):
		if pygame.get_init():

			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../assets/images/buttons/')
			resume_img = pygame.image.load(filename+"/button_resume.png").convert_alpha()
			options_img = pygame.image.load(filename+"/button_options.png").convert_alpha()
			quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()
			video_img = pygame.image.load(filename+"/button_video.png").convert_alpha()
			audio_img = pygame.image.load(filename+"/button_audio.png").convert_alpha()
			keys_img = pygame.image.load(filename+"/button_keys.png").convert_alpha()
			back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

			#create button instances
			scale = 0.2
			resume_button = Button(self.screen_width/2 - resume_img.get_width()/2 * scale, self.screen_height/4 + 125, resume_img, scale)
			options_button = Button(self.screen_width/2 - options_img.get_width()/2 * scale, self.screen_height/4 + 250, options_img, scale)
			quit_button = Button(self.screen_width/2 - quit_img.get_width()/2 * scale, self.screen_height/4 + 375, quit_img, scale)
			video_button = Button(self.screen_width/2 - video_img.get_width()/2 * scale, self.screen_height/4 + 75, video_img, scale)
			audio_button = Button(self.screen_width/2 - audio_img.get_width()/2 * scale, self.screen_height/4 + 200, audio_img, scale)
			keys_button = Button(self.screen_width/2 - keys_img.get_width()/2 * scale, self.screen_height/4 + 325, keys_img, scale)
			back_button = Button(self.screen_width/2 - back_img.get_width()/2 * scale, self.screen_height/4 + 450, back_img, scale)

			#game loop
			run = True
			while run:
				window = pygame.Rect(self.screen_width/4, self.screen_height/4, self.screen_width/2, self.screen_height/2)
				pygame.draw.rect(self.screen, (52, 78, 91), window)

				#check menu state
				if self.state == "ingame":
					#draw pause screen buttons
					if resume_button.draw(self.screen):
						return "closed"
					if options_button.draw(self.screen):
						self.state = "options"
					if quit_button.draw(self.screen):
						run = False
						return "return to main menu"
				#check if the options menu is open
				if self.state == "options":
					#draw the different options buttons
					if video_button.draw(self.screen):
						print("Video Settings")
					if audio_button.draw(self.screen):
						print("Audio Settings")
					if keys_button.draw(self.screen):
						print("Change Key Bindings")
					if back_button.draw(self.screen):
						self.state = "ingame"

				#event handler
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

	def openDeathMenu(self, userdata, gamescore, csrf_token):
		if pygame.get_init():
			if userdata:
				if gamescore > userdata['highscore']:
					response = submit_score(userdata['player_name'], gamescore, csrf_token)
					if response['status'] == 'error':
						print(response['message'])
					else:
						userdata.update({'highscore':gamescore})

			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../assets/images/buttons/')
			quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()
			playagain_img = pygame.image.load(filename+"/button_playagain.png").convert_alpha()
			back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

			#create button instances
			scale = 0.2
			font = pygame.font.Font(None, 30)
			menuX = self.screen_width/4
			menuY = self.screen_height/5

			if userdata:
				deathmessage = "You are dead, "+str(userdata["player_name"])+"."
				curr_score_message = "Current highscore: "+str(userdata["highscore"])+"."
				achieved_score_message = "Achieved score: "+str(gamescore)+"."

				deathmessage_box = pygame.Rect(self.screen_width/2 - font.size(deathmessage)[0]/2, menuY + 50, font.size(deathmessage)[0], font.get_linesize()*2)
				deathmessage_button = Button(deathmessage_box.x, deathmessage_box.y, [font, deathmessage, "white", deathmessage_box], 1)

				curr_score_message_box = pygame.Rect(self.screen_width/2 - font.size(curr_score_message)[0]/2, menuY + 50 + font.get_linesize()*2 + 1, font.size(curr_score_message)[0], font.get_linesize()*2)
				curr_score_message_button = Button(curr_score_message_box.x, curr_score_message_box.y, [font, curr_score_message, "white", curr_score_message_box], 1)

				achieved_score_message_box = pygame.Rect(self.screen_width/2 - font.size(achieved_score_message)[0]/2, menuY + 50 + font.get_linesize()*4 + 2, font.size(achieved_score_message)[0], font.get_linesize()*2)
				achieved_score_message_button = Button(achieved_score_message_box.x, achieved_score_message_box.y, [font, achieved_score_message, "white", achieved_score_message_box], 1)
				
			else:
				deathmessage = "You are dead, guest."
				curr_score_message = "Achieved score: "+str(gamescore)+"."
				achieved_score_message = "If you wish to save your score, then login or create a new profile!"

				deathmessage_box = pygame.Rect(self.screen_width/2 - font.size(deathmessage)[0]/2, menuY + 50, font.size(deathmessage)[0], font.get_linesize()*2)
				deathmessage_button = Button(deathmessage_box.x, deathmessage_box.y, [font, deathmessage, "white", deathmessage_box], 1)

				curr_score_message_box = pygame.Rect(self.screen_width/2 - font.size(curr_score_message)[0]/2, menuY + 50 + font.get_linesize()*2 + 1, font.size(curr_score_message)[0], font.get_linesize()*2)
				curr_score_message_button = Button(curr_score_message_box.x, curr_score_message_box.y, [font, curr_score_message, "white", curr_score_message_box], 1)

				achieved_score_message_box = pygame.Rect(self.screen_width/2 - font.size(achieved_score_message)[0]/2, menuY + 50 + font.get_linesize()*4 + 2, font.size(achieved_score_message)[0], font.get_linesize()*2)
				achieved_score_message_button = Button(achieved_score_message_box.x, achieved_score_message_box.y, [font, achieved_score_message, "white", achieved_score_message_box], 1)
				
				create_img = pygame.image.load(filename+"/button_createuser.png").convert_alpha()
				login_img = pygame.image.load(filename+"/button_login.png").convert_alpha()
				login_button = Button(self.screen_width/2 - login_img.get_width()/2 * scale, menuY + 175, login_img, scale)
				create_button = Button(self.screen_width/2 - create_img.get_width()/2 * scale, menuY + 275, create_img, scale)

			username_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 100, 30 * font.size("_")[0], font.get_linesize()*2, font, "username", "username...")
			password_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 175, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password...")
			password2_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 250, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password again...")
			email_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 325, 30 * font.size("_")[0], font.get_linesize()*2, font, "email", "email address...")
			
			playagain_button = Button(self.screen_width/2 - playagain_img.get_width()/2 * scale, menuY + 375, playagain_img, scale)
			quit_button = Button(self.screen_width/2 - quit_img.get_width()/2 * scale, menuY + 475, quit_img, scale)
			back_button = Button(self.screen_width/2 - back_img.get_width()/2 * scale, self.screen_height/4 + 475, back_img, scale)

			#game loop
			run = True
			logchange = False
			button_timeout = 100
			while run:
				if button_timeout > 0:
					button_timeout -= 1
				self.screen.fill("black")
				window = pygame.Rect(menuX, menuY, self.screen_width - 2*menuX, self.screen_height - 2*menuY)
				pygame.draw.rect(self.screen, (52, 78, 91), window)

				#check menu state
				if self.state == "playerdead":
					deathmessage_button.drawText(self.screen), curr_score_message_button.drawText(self.screen), achieved_score_message_button.drawText(self.screen)

					if playagain_button.draw(self.screen):
						run = False
						return ("return to main menu", userdata)
					
					if not userdata:
						if login_button.draw(self.screen):
							login_button.rect.y = menuY + 400
							self.state = "logInMenu"

						if create_button.draw(self.screen):
							create_button.rect.y = menuY + 400
							self.state = "createMenu"
				
					if quit_button.draw(self.screen):
							if button_timeout <= 0:
								run = False
								return ("exit", userdata)
				
				if self.state == "logInMenu":
					username_textbox.draw(self.screen), password_textbox.draw(self.screen)

					if login_button.draw(self.screen):
						response = fetch_user(username_textbox.text, password_textbox.text, csrf_token)
						if response["status"] == "error":
							username_textbox.reset(), password_textbox.reset(), password2_textbox.reset(), email_textbox.reset()
							self.state == "logInMenu"
							button_timeout = 100
						else:
							userdata = response["userdata"]
							self.state = "playerdead"
							logchange = True
							run = False
					
					if back_button.draw(self.screen):
						login_button.rect.y = menuY + 375
						self.state = "playerdead"
						button_timeout = 100

				if self.state == "createMenu":
					username_textbox.draw(self.screen), password_textbox.draw(self.screen), password2_textbox.draw(self.screen), email_textbox.draw(self.screen)

					if create_button.draw(self.screen):
						response = submit_new_user(username_textbox.text, password_textbox.text, password2_textbox.text, email_textbox.text, 0, csrf_token)
						if response["status"] == "error":
							username_textbox.reset(), password_textbox.reset(), password2_textbox.reset(), email_textbox.reset()
							self.state == "createMenu"
							button_timeout = 100
						else:
							userdata = response["userdata"]
							self.state = "playerdead"
							logchange = True
							run = False

					if back_button.draw(self.screen):
						create_button.rect.y = menuY + 375
						self.state = "playerdead"
						button_timeout = 100
						
				#event handler
				for event in pygame.event.get():
					if self.state == "logInMenu" or self.state == "createMenu":
						username_textbox.handle_event(event)
						password_textbox.handle_event(event)
						if self.state == "createMenu":
							email_textbox.handle_event(event)
							password2_textbox.handle_event(event)
							
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

			if logchange:
				return self.openDeathMenu(userdata, gamescore, csrf_token)
	
	def openItemSelectorMenu(self, itemlist):   #: List[Union[Weapon, Passive]]
		if pygame.get_init():
			# Load button images for menu buttons selection
			for item in itemlist:
				item.loadImages()

			# Create button instances for weapon selection
			images: List[pygame.Surface] = []
			for i in range(len(itemlist)):
				font = pygame.font.Font(None, 30)
				text = font.render(itemlist[i].name, True, "black")
				self.screen.blit(text, (0, 300 + 50 * i))
				
				if itemlist[i].level < 4:
					images.append(itemlist[i].image_base)
				else:
					images.append(itemlist[i].image_maxed)

			font = pygame.font.Font(None, 30)
			if len(itemlist) == 1:
				item_button1 = Button(self.screen_width / 2 - images[0].get_width() * 0.1 / 2 + 400, self.screen_height / 4 + 250, images[0], 0.1)
				text_box1 = pygame.Rect(self.screen_width / 4 - 150, self.screen_height / 4 + 250, self.screen_width / 4 - images[0].get_width() * 0.1 / 2 + 550, images[0].get_height() * 0.1)
				text_button1 = Button(self.screen_width / 4 - 150, self.screen_height / 4 + 250, [font, itemlist[0].description, "white", text_box1], 1)

			elif len(itemlist) == 2:
				item_button1 = Button(self.screen_width / 2 - images[0].get_width() * 0.1 / 2 + 400, self.screen_height / 4 + 150, images[0], 0.1)
				text_box1 = pygame.Rect(self.screen_width / 4 - 150, self.screen_height / 4 + 150, self.screen_width / 4 - images[0].get_width() * 0.1 / 2 + 550, images[0].get_height() * 0.1)
				text_button1 = Button(self.screen_width / 4 - 150, self.screen_height / 4 + 150, [font, itemlist[0].description, "white", text_box1], 1)

				item_button2 = Button(self.screen_width / 2 - images[1].get_width() * 0.1 / 2 + 400, self.screen_height / 4 + 350, images[1], 0.1)
				text_box2 = pygame.Rect(self.screen_width / 4 - 150, self.screen_height / 4 + 350, self.screen_width / 4 - images[1].get_width() * 0.1 / 2 + 550, images[1].get_height() * 0.1)
				text_button2 = Button(self.screen_width / 4 - 150, self.screen_height / 4 + 350, [font, itemlist[1].description, "white", text_box2], 1)
			
			elif len(itemlist) == 3:
				item_button1 = Button(self.screen_width / 2 - images[0].get_width() * 0.1 / 2 + 400, self.screen_height / 4 + 50, images[0], 0.1)
				text_box1 = pygame.Rect(self.screen_width / 4 - 150, self.screen_height / 4 + 50, self.screen_width / 4 - images[0].get_width() * 0.1 / 2 + 550, images[0].get_height() * 0.1)
				text_button1 = Button(self.screen_width / 4 - 150, self.screen_height / 4 + 50, [font, itemlist[0].description, "white", text_box1], 1)

				item_button2 = Button(self.screen_width / 2 - images[1].get_width() * 0.1 / 2 + 400, self.screen_height / 4 + 250, images[1], 0.1)
				text_box2 = pygame.Rect(self.screen_width / 4 - 150, self.screen_height / 4 + 250, self.screen_width / 4 - images[1].get_width() * 0.1 / 2 + 550, images[1].get_height() * 0.1)
				text_button2 = Button(self.screen_width / 4 - 150, self.screen_height / 4 + 250, [font, itemlist[1].description, "white", text_box2], 1)

				item_button3 = Button(self.screen_width / 2 - images[2].get_width() * 0.1 / 2 + 400, self.screen_height / 4 + 450, images[2], 0.1)
				text_box3 = pygame.Rect(self.screen_width / 4 - 150, self.screen_height / 4 + 450, self.screen_width / 4 - images[2].get_width() * 0.1 / 2 + 550, images[2].get_height() * 0.1)
				text_button3 = Button(self.screen_width / 4 - 150, self.screen_height / 4 + 450, [font, itemlist[2].description, "white", text_box3], 1)

			# Game loop
			run = True
			while run:
				window = pygame.Rect(self.screen_width / 4 - 200, self.screen_height / 4, self.screen_width / 2 + 400, self.screen_height / 2)
				pygame.draw.rect(self.screen, (52, 78, 91), window)

				# Check menu state
				if self.state == "weapon_selector" or self.state == "passive_selector":
					# Draw item selection buttons
					if len(itemlist) > 0:
						if item_button1.draw(self.screen) or text_button1.drawText(self.screen):
							return ["closed", itemlist[0]]
					if len(itemlist) > 1:
						if item_button2.draw(self.screen) or text_button2.drawText(self.screen):
							return ["closed", itemlist[1]]
					if len(itemlist) > 2:
						if item_button3.draw(self.screen) or text_button3.drawText(self.screen):
							return ["closed", itemlist[2]]

				# Event handler
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

class Button():
	def __init__(self, x, y, image: Union[pygame.Surface, List[Union[pygame.font.Font, str, pygame.Rect]]], scale):
		if isinstance(image, list):
			self.font = image[0]
			self.text = image[1]
			self.colour = image[2]
			self.rect = image[3]
		else:
			width = image.get_width()
			height = image.get_height()
			self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
			self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False
		self.timeout = 5
	
	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.timeout == 0:
			if self.rect.collidepoint(pos):
				if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
					self.clicked = True
					action = True

			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

		else:
			if pygame.mouse.get_pressed()[0] == 0:
				self.timeout -= 1

		#draw button on self.screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

	def drawText(self, surface, aa=False, bkg=None):
		text = self.text
		y = self.rect.top
		lineSpacing = -2

		# get the height of the font
		fontHeight = self.font.size("Tg")[1]

		while text:
			i = 1

			# determine if the row of text will be outside our area
			if y + fontHeight > self.rect.bottom:
				break

			# determine maximum width of line
			while self.font.size(text[:i])[0] < self.rect.width and i < len(text):
				i += 1

			# if we've wrapped the text, then adjust the wrap to the last word      
			if i < len(text): 
				i = text.rfind(" ", 0, i) + 1

			# render the line and blit it to the surface
			if bkg:
				image = self.font.render(text[:i], 1, self.colour, bkg)
				image.set_colorkey(bkg)
			else:
				image = self.font.render(text[:i], aa, self.colour)
			
			surface.blit(image, (self.rect.left, y))
			y += fontHeight + lineSpacing

			# remove the text we just blitted
			text = text[i:]

		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		
		return action
	

class TextBox():
	def __init__(self, x, y, width, height, font, texttype, placeholder_text, text_colour = (0, 0, 0), placeholder_colour = (150, 150, 150), active_colour = (255, 0, 0), bg_colour = (255, 255, 255)):
		self.rect = pygame.Rect(x, y, width, height)
		self.font: pygame.font.Font = font
		self.type = texttype
		self.placeholder_text = placeholder_text
		self.text_colour = text_colour
		self.placeholder_colour = placeholder_colour
		self.active_colour = active_colour
		self.bg_colour = bg_colour
		self.text = ""
		self.active = False
		self.render_text = placeholder_text
		self.cursor_show = False
		self.cursor_timer = 500
		self.hovered = False

	def reset(self):
		self.text = ""
		self.active = False
		self.cursor_show = False
		self.cursor_timer = 500
		self.hovered = False

	def handle_event(self, event):
		pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:
			# If the user clicked on the text box rect
			if self.rect.collidepoint(pos):
				# Toggle the active variable
				self.active = True
			else:
				self.active = False
		
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_RETURN:
					print(self.text)	# TODO: REQUEST A LOG IN
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode
		
		self.render_text = self.text if self.text != "" else self.placeholder_text

	def draw(self, surface: pygame.Surface):
		# Draw the background
		pygame.draw.rect(surface, self.bg_colour, self.rect)

		# Draw the text
		colour = self.placeholder_colour if self.text == "" else self.text_colour
		# if self.type == "password" and self.text != "":
		# 	final_text = ""
		# 	for i in range(len(self.render_text)):
		# 		final_text += "•"
		# else:
		final_text = self.render_text
		text_surface = self.font.render(final_text, True, colour)
		surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

		# Draw the border
		if self.active:
			pygame.draw.rect(surface, self.active_colour, self.rect, 3)
			if self.cursor_show:
				text_size = 6
				if self.text != "":
					for letter in final_text:
						text_size += self.font.size(letter)[0]
				pygame.draw.line(surface, (0,0,0), (self.rect.x + text_size, self.rect.y + 4), (self.rect.x + text_size, self.rect.y + self.rect.height - 20), 2)
		else:
			pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
		
		if self.cursor_timer <= 0:
			self.cursor_show = not self.cursor_show
			self.cursor_timer = 500
		else:
			self.cursor_timer -= 1