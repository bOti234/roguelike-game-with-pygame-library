import os
import pygame
from typing import List, Dict, Union
from .gameobject import PlayerCharacter, Weapon, Passive
from ..utils.database import fetch_user, submit_new_user, submit_logout, submit_update_user, submit_score

class HUD():
	def __init__(self, screen, screen_width, screen_height, test = None):
		self.screen: pygame.Surface = screen
		self.screen_width = screen_width
		self.screen_height = screen_height

		if test is not None:
			self.test = test
		else:
			self.test = {'mode': False, 'data': None}

class StatBar(HUD):
	def __init__(self, screen, screen_width, screen_height, stat_type, x, y, width, height, stat_background_rgba, trasparent_screen, border_width, border_radius, stat_colour, border_colour = "black", test = None):
		super().__init__(screen, screen_width, screen_height, test)
		self.stat_type = stat_type
		self.border_rect = pygame.rect.Rect(x, y, width, height)
		self.stat_rect = pygame.rect.Rect(x + border_width, y + border_width, width - border_width*2, height - border_width*2)
		self.stat_background_rgba = stat_background_rgba
		self.trasparent_screen = trasparent_screen
		self.border_colour = border_colour
		self.border_width = border_width
		self.border_radius = border_radius
		self.stat_colour = stat_colour

	# def __eq__(self, other):
	# 	if not isinstance(other, StatBar):
	# 		return 'Error, class mismatch'
	# 	if self.stat_type == other.stat_type:
	# 		return True
	# 	return False

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
	def __init__(self, screen, screen_width, screen_height, test = None):
		super().__init__(screen, screen_width, screen_height, test)
		self.opened = False
		self.state = None

	def openMainMenu(self, csrf_token, sizeratio_x, sizeratio_y, userdata = None):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../assets/images/buttons/')
			play_img = pygame.image.load(filename+"/button_play.png").convert_alpha()
			quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()
			back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

			#create button instances
			scale = 0.2 * sizeratio_x
			font = pygame.font.Font(None, round(30 * sizeratio_x))
			menuX = self.screen_width/4
			menuY = self.screen_height/5
			
			play_button = Button(self.screen_width/2 - play_img.get_width()/2 * scale, menuY + 175 * sizeratio_y, play_img, scale)
			quit_button = Button(self.screen_width/2 - quit_img.get_width()/2 * scale, menuY + 475 * sizeratio_y, quit_img, scale)

			if userdata:
				logout_img = pygame.image.load(filename+"/button_logout.png").convert_alpha()
				update_img = pygame.image.load(filename+"/button_updateuser.png").convert_alpha()

				welocme_text_box = pygame.Rect(self.screen_width/2 - font.size("Welcome back, "+userdata["player_name"]+"!")[0]/2, menuY + 50 * sizeratio_y, font.size("Welcome back, "+userdata["player_name"]+"!")[0], font.get_linesize()*2)
				welocme_text_button = Button(welocme_text_box.x, welocme_text_box.y, [font, "Welcome back, "+userdata["player_name"]+"!", "white", welocme_text_box], 1)
				
				highscore_text_box = pygame.Rect(self.screen_width/2 - font.size("Current highscore: "+str(userdata["highscore"]))[0]/2, menuY + 50 * sizeratio_y + font.get_linesize()*2 + 1, font.size("Current highscore: "+str(userdata["highscore"]))[0], font.get_linesize()*2)
				highscore_text_button = Button(highscore_text_box.x, highscore_text_box.y, [font, "Current highscore: "+str(userdata["highscore"]), "white", highscore_text_box], 1)
				
				
				log_button = Button(self.screen_width/2 - logout_img.get_width()/2 * scale, menuY + 275 * sizeratio_y, logout_img, scale)
				user_button = Button(self.screen_width/2 - update_img.get_width()/2 * scale, menuY + 375 * sizeratio_y, update_img, scale)
			else:
				login_img = pygame.image.load(filename+"/button_login.png").convert_alpha()
				create_img = pygame.image.load(filename+"/button_createuser.png").convert_alpha()

				welocme_text_box = pygame.Rect(self.screen_width/2 - font.size("Play as guest!")[0]/2, menuY + 50 * sizeratio_y, font.size("Play as guest!")[0], font.get_linesize()*2)
				welocme_text_button = Button(welocme_text_box.x, welocme_text_box.y, [font, "Play as guest!", "white", welocme_text_box], 1)
				log_button = Button(self.screen_width/2 - login_img.get_width()/2 * scale, menuY + 275 * sizeratio_y, login_img, scale)
				user_button = Button(self.screen_width/2 - create_img.get_width()/2 * scale, menuY + 375 * sizeratio_y, create_img, scale)

			username_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 100 * sizeratio_y, 30 * font.size("_")[0], font.get_linesize()*2, font, "username", "username...")
			password_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 175 * sizeratio_y, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password...")
			password2_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 250 * sizeratio_y, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password again...")
			email_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 325 * sizeratio_y, 30 * font.size("_")[0], font.get_linesize()*2, font, "email", "email address...")
			back_button = Button(self.screen_width/2 - back_img.get_width()/2 * scale, self.screen_height/4 + 475 * sizeratio_y, back_img, scale)

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
							log_button.rect.y = menuY + 400 * sizeratio_y
							self.state = "logInMenu"

					if user_button.draw(self.screen):
						if userdata:
							user_button.rect.y = menuY + 450 * sizeratio_y
							self.state = 'updateMenu'
						else:
							user_button.rect.y = menuY + 450 * sizeratio_y
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
						log_button.rect.y = menuY + 275 * sizeratio_y
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
						user_button.rect.y = menuY + 375 * sizeratio_y
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
						user_button.rect.y = menuY + 375 * sizeratio_y
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

				if self.test['mode']:
					return ('test', userdata)

			if logchange:
				return self.openMainMenu(csrf_token, userdata)

	def openInGameMenu(self, sizeratio_x, sizeratio_y, mastervolume, musicvolume, gamesoundvolume):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../assets/images/buttons/')
			resume_img = pygame.image.load(filename+"/button_resume.png").convert_alpha()
			options_img = pygame.image.load(filename+"/button_options.png").convert_alpha()
			quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()
			video_img = pygame.image.load(filename+"/button_video.png").convert_alpha()
			audio_img = pygame.image.load(filename+"/button_audio.png").convert_alpha()
			apply_img = pygame.image.load(filename+"/button_apply.png").convert_alpha()
			back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

			#create button instances
			scale = 0.2 * sizeratio_x
			font = pygame.font.Font(None, round(30 * sizeratio_x))
			resume_button = Button(self.screen_width/2 - resume_img.get_width()/2 * scale, self.screen_height/4 + 125 * sizeratio_y, resume_img, scale)
			options_button = Button(self.screen_width/2 - options_img.get_width()/2 * scale, self.screen_height/4 + 250 * sizeratio_y, options_img, scale)
			quit_button = Button(self.screen_width/2 - quit_img.get_width()/2 * scale, self.screen_height/4 + 375 * sizeratio_y, quit_img, scale)
			video_button = Button(self.screen_width/2 - video_img.get_width()/2 * scale, self.screen_height/4 + 75 * sizeratio_y, video_img, scale)
			audio_button = Button(self.screen_width/2 - audio_img.get_width()/2 * scale, self.screen_height/4 + 200 * sizeratio_y, audio_img, scale)
			apply_button = Button(self.screen_width/2 - apply_img.get_width()/2 * scale, self.screen_height/4 + 350 * sizeratio_y, apply_img, scale)
			back_button = Button(self.screen_width/2 - back_img.get_width()/2 * scale, self.screen_height/4 + 450 * sizeratio_y, back_img, scale)

			sliders = {
				'master_volume_slider': Slider('Master', pygame.Vector2(self.screen_width / 2 - 250 * sizeratio_x, self.screen_height / 2 - 200 * sizeratio_y), 500 * sizeratio_x, 30 * sizeratio_y, font, mastervolume, 0, 100),
				'music_volume_slider': Slider('Music', pygame.Vector2(self.screen_width / 2 - 250 * sizeratio_x, self.screen_height / 2 - 100 * sizeratio_y), 500 * sizeratio_x, 30 * sizeratio_y, font, musicvolume, 0, 100),
				'gamesound_volume_slider': Slider('Game sounds', pygame.Vector2(self.screen_width / 2 - 250 * sizeratio_x, self.screen_height / 2), 500 * sizeratio_x, 30 * sizeratio_y, font, gamesoundvolume, 0, 100)
			}

			resolution_options = [
				{'width': 3840, 'height': 2160},
				{'width': 2560, 'height': 1600},
				{'width': 2560, 'height': 1440},
				{'width': 1920, 'height': 1200},
				{'width': 1920, 'height': 1080},
				{'width': 1600, 'height': 1200},
				{'width': 1600, 'height': 900},
				{'width': 1366, 'height': 768},
				{'width': 1280 , 'height': 720},
				{'width': 800 , 'height': 600}
			]
			video_dropdown = Dropdown('Screen resolution', pygame.Vector2(self.screen_width / 2 - 200 * sizeratio_x, self.screen_height / 2 - 200 * sizeratio_y), 400 * sizeratio_x, 35 * sizeratio_y, resolution_options, font, self.screen_width, self.screen_height)

			#game loop
			run = True
			while run:
				window = pygame.Rect(self.screen_width/4, self.screen_height/4, self.screen_width/2, self.screen_height/2)
				pygame.draw.rect(self.screen, (52, 78, 91), window)

				#check menu state
				if self.state == "ingame":
					#draw pause screen buttons
					if resume_button.draw(self.screen):
						return ("closed", None)
					if options_button.draw(self.screen):
						self.state = "options"
					if quit_button.draw(self.screen):
						run = False
						return ("return to main menu", None)
				#check if the options menu is open
				if self.state == "options":
					#draw the different options buttons
					if video_button.draw(self.screen):
						self.state = 'video settings'
					if audio_button.draw(self.screen):
						self.state = 'audio settings'
					if back_button.draw(self.screen):
						self.state = "ingame"

				if self.state == 'video settings':
					if video_dropdown.draw(self.screen):
						run = False
						return ('video setting', video_dropdown.chosen_option)

					if not video_dropdown.clicked:
						if apply_button.draw(self.screen):
							run = False
							return ('video setting final', video_dropdown.chosen_option)

						if back_button.draw(self.screen):
							self.state = "options"
							return ('video setting final', {'width':self.screen_width, 'height':self.screen_height})

				if self.state == 'audio settings':
					mouse_pos = pygame.mouse.get_pos()
					mouse = pygame.mouse.get_pressed()
					for slider in sliders.values():
						if slider.container_rect.collidepoint(mouse_pos):
							if mouse[0]:
								slider.grabbed = True
						if not mouse[0]:
							slider.grabbed = False
						if slider.button_rect.collidepoint(mouse_pos):  
							slider.hover()
						if slider.grabbed:
							slider.move_slider(mouse_pos)
							slider.hover()
						else:
							slider.hovered = False
						slider.render(self.screen)
						slider.display_value(self.screen)

					if apply_button.draw(self.screen) and slider.grabbed == False:
						run = False
						return ('audio setting', sliders['master_volume_slider'].get_value()/100, sliders['music_volume_slider'].get_value()/100, sliders['gamesound_volume_slider'].get_value()/100)

					if back_button.draw(self.screen) and slider.grabbed == False:
						self.state = "options"

				#event handler
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

				if self.test['mode']:
					return 'test'

	def openItemListMenu(self, sizeratio_x, sizeratio_y, passivelist: List[Passive], weaponlist: List[Weapon], player_passivelist: Dict[str,Passive], player_weaponlist: Dict[str,Weapon]):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../assets/images/buttons/')
			resume_img = pygame.image.load(filename+"/button_resume.png").convert_alpha()

			font = pygame.font.Font(None, round(30 * sizeratio_x))
			menuX = self.screen_width/12
			menuY = self.screen_height/5
			scale_image = 0.05 * sizeratio_x
			scale_button = 0.2 * sizeratio_x
			resume_button = Button(self.screen_width/2 - resume_img.get_width()/2 * scale_button, self.screen_height - menuY - 125 * sizeratio_y, resume_img, scale_button)

			# Create button instances for weapon selection
			passive_images: List[pygame.Surface] = []
			weapon_images: List[pygame.Surface] = []
			itembuttons: List[Button] = []
			textbuttons: List[Button] = []
			for i in range(len(passivelist)):
				passivelist[i].loadImages()
				if passivelist[i].level < 4:
					passive_images.append(passivelist[i].image_base)
				else:
					passive_images.append(passivelist[i].image_maxed)
				total_image_length = passive_images[i].get_width() * scale_image * len(passivelist)
				gap = (self.screen_width - 2*menuX - total_image_length) / (len(passivelist) + 1) + passive_images[i].get_width() * scale_image
				item_button = Button(menuX + (i+1)*gap - passive_images[i].get_width() * scale_image, menuY + 150 * sizeratio_y, passive_images[i], scale_image)
				if passivelist[i] in player_passivelist.values():
					item_button.addBorder(3, 'yellow', (10, 10, 10, 10), (3, 3, 3, 3))

				itembuttons.append(item_button)

				if item_button.rect.x + 250 * sizeratio_x + passive_images[i].get_width()/2 * scale_image > self.screen_width - menuX:
					text_box_x = item_button.rect.x - 500 * sizeratio_x + passive_images[i].get_width()*2 * scale_image
				elif item_button.rect.x - 250 * sizeratio_x < menuX:
					text_box_x = item_button.rect.x
				else:
					text_box_x = item_button.rect.x - 250 * sizeratio_x + passive_images[i].get_width()/2 * scale_image

				text_box = pygame.Rect(text_box_x, item_button.rect.y + passive_images[i].get_height() * scale_image + 10, 500 * sizeratio_x, passive_images[i].get_height() * scale_image)
				text_button = Button(text_box_x, item_button.rect.y + passive_images[i].get_height() * scale_image + 10, [font, passivelist[i].description, "white", text_box], 1)
				textbuttons.append(text_button)

			for i in range(len(weaponlist)):
				weaponlist[i].loadImages()
				if weaponlist[i].level < 4:
					weapon_images.append(weaponlist[i].image_base)
				else:
					weapon_images.append(weaponlist[i].image_maxed)
				total_image_length = weapon_images[i].get_width() * scale_image * len(weaponlist)
				gap = (self.screen_width - 2*menuX - total_image_length) / (len(weaponlist) + 1) + weapon_images[i].get_width() * scale_image
				item_button = Button(menuX + (i+1)*gap - weapon_images[i].get_width() * scale_image, menuY + 375 * sizeratio_y, weapon_images[i], scale_image)
				if weaponlist[i] in player_weaponlist.values():
					item_button.addBorder(3, 'yellow', (10, 10, 10, 10), (3, 3, 3, 3))

				itembuttons.append(item_button)

				if item_button.rect.x + 250 * sizeratio_x + weapon_images[i].get_width()/2 * scale_image > self.screen_width - menuX:
					text_box_x = item_button.rect.x - 500 * sizeratio_x + weapon_images[i].get_width() * scale_image
				elif item_button.rect.x - 250 * sizeratio_x < menuX:
					text_box_x = item_button.rect.x
				else:
					text_box_x = item_button.rect.x - 250 * sizeratio_x + weapon_images[i].get_width()/2 * scale_image
				
				text_box = pygame.Rect(text_box_x, item_button.rect.y + weapon_images[i].get_height() * scale_image + 10, 500 * sizeratio_x, weapon_images[i].get_height() * scale_image)
				text_button = Button(text_box_x, item_button.rect.y + weapon_images[i].get_height() * scale_image + 10, [font, weaponlist[i].description, "white", text_box], 1)
				textbuttons.append(text_button)


			# Game loop
			run = True
			while run:
				window = pygame.Rect(menuX, menuY, self.screen_width - 2*menuX, self.screen_height - 2*menuY)
				pygame.draw.rect(self.screen, (52, 78, 91), window)

				# Check menu state
				if self.state == "inventory":
					# Draw item selection buttons
					for i, button in enumerate(itembuttons):
						if button.draw(self.screen, True):
							textbuttons[i].drawText(self.screen)
					
					if resume_button.draw(self.screen):
						run = False
						return 'Resume game'

				# Event handler
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

				if self.test['mode']:
					return 'test'

					
	
	def openDeathMenu(self, sizeratio_x, sizeratio_y, userdata, gamescore, csrf_token):
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
			scale = 0.2 * sizeratio_x
			font = pygame.font.Font(None, round(30 * sizeratio_x))
			menuX = self.screen_width/4
			menuY = self.screen_height/5

			if userdata:
				deathmessage = "You are dead, "+str(userdata["player_name"])+"."
				curr_score_message = "Current highscore: "+str(userdata["highscore"])+"."
				achieved_score_message = "Achieved score: "+str(gamescore)+"."

				deathmessage_box = pygame.Rect(self.screen_width/2 - font.size(deathmessage)[0]/2, menuY + 50 * sizeratio_y, font.size(deathmessage)[0], font.get_linesize()*2)
				deathmessage_button = Button(deathmessage_box.x, deathmessage_box.y, [font, deathmessage, "white", deathmessage_box], 1)

				curr_score_message_box = pygame.Rect(self.screen_width/2 - font.size(curr_score_message)[0]/2, menuY + 50 * sizeratio_y + font.get_linesize()*2 + 1, font.size(curr_score_message)[0], font.get_linesize()*2)
				curr_score_message_button = Button(curr_score_message_box.x, curr_score_message_box.y, [font, curr_score_message, "white", curr_score_message_box], 1)

				achieved_score_message_box = pygame.Rect(self.screen_width/2 - font.size(achieved_score_message)[0]/2, menuY + 50 * sizeratio_y + font.get_linesize()*4 + 2, font.size(achieved_score_message)[0], font.get_linesize()*2)
				achieved_score_message_button = Button(achieved_score_message_box.x, achieved_score_message_box.y, [font, achieved_score_message, "white", achieved_score_message_box], 1)
				
			else:
				deathmessage = "You are dead, guest."
				curr_score_message = "Achieved score: "+str(gamescore)+"."
				achieved_score_message = "If you wish to save your score, then login or create a new profile!"

				deathmessage_box = pygame.Rect(self.screen_width/2 - font.size(deathmessage)[0]/2, menuY + 50 * sizeratio_y, font.size(deathmessage)[0], font.get_linesize()*2)
				deathmessage_button = Button(deathmessage_box.x, deathmessage_box.y, [font, deathmessage, "white", deathmessage_box], 1)

				curr_score_message_box = pygame.Rect(self.screen_width/2 - font.size(curr_score_message)[0]/2, menuY + 50 * sizeratio_y + font.get_linesize()*2 + 1, font.size(curr_score_message)[0], font.get_linesize()*2)
				curr_score_message_button = Button(curr_score_message_box.x, curr_score_message_box.y, [font, curr_score_message, "white", curr_score_message_box], 1)

				achieved_score_message_box = pygame.Rect(self.screen_width/2 - font.size(achieved_score_message)[0]/2, menuY + 50 * sizeratio_y + font.get_linesize()*4 + 2, font.size(achieved_score_message)[0], font.get_linesize()*2)
				achieved_score_message_button = Button(achieved_score_message_box.x, achieved_score_message_box.y, [font, achieved_score_message, "white", achieved_score_message_box], 1)
				
				create_img = pygame.image.load(filename+"/button_createuser.png").convert_alpha()
				login_img = pygame.image.load(filename+"/button_login.png").convert_alpha()
				login_button = Button(self.screen_width/2 - login_img.get_width()/2 * scale, menuY + 175 * sizeratio_y, login_img, scale)
				create_button = Button(self.screen_width/2 - create_img.get_width()/2 * scale, menuY + 275 * sizeratio_y, create_img, scale)

			username_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 100 * sizeratio_y, 30 * font.size("_")[0], font.get_linesize()*2, font, "username", "username...")
			password_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 175 * sizeratio_y, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password...")
			password2_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 250 * sizeratio_y, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password again...")
			email_textbox = TextBox(self.screen_width/2 - 30 * font.size("_")[0]/2, self.screen_height/4 + 325 * sizeratio_y, 30 * font.size("_")[0], font.get_linesize()*2, font, "email", "email address...")
			
			playagain_button = Button(self.screen_width/2 - playagain_img.get_width()/2 * scale, menuY + 375 * sizeratio_y, playagain_img, scale)
			quit_button = Button(self.screen_width/2 - quit_img.get_width()/2 * scale, menuY + 475 * sizeratio_y, quit_img, scale)
			back_button = Button(self.screen_width/2 - back_img.get_width()/2 * scale, self.screen_height/4 + 475 * sizeratio_y, back_img, scale)

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
							login_button.rect.y = menuY + 400 * sizeratio_y
							self.state = "logInMenu"

						if create_button.draw(self.screen):
							create_button.rect.y = menuY + 400 * sizeratio_y
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
						login_button.rect.y = menuY + 375 * sizeratio_y
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
						create_button.rect.y = menuY + 375 * sizeratio_y
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

				if self.test['mode']:
					return ('test', userdata)

			if logchange:
				return self.openDeathMenu(userdata, gamescore, csrf_token)
	
	def openItemSelectorMenu(self, sizeratio_x, sizeratio_y, itemlist: List[Union[Passive, Weapon]]):   #: List[Union[Weapon, Passive]]
		if pygame.get_init():
			# Load button images for menu buttons selection
			for item in itemlist:
				item.loadImages()

			# Create button instances for weapon selection
			images: List[pygame.Surface] = []
			scale = 0.1 * sizeratio_x
			font = pygame.font.Font(None, round(30 * sizeratio_x))
			menuX = self.screen_width/5
			menuY = self.screen_height/5
			for i in range(len(itemlist)):
				text = font.render(itemlist[i].name, True, "black")
				self.screen.blit(text, (0, 300 + 50 * i))
				
				if itemlist[i].level < 4:
					images.append(itemlist[i].image_base)
				else:
					images.append(itemlist[i].image_maxed)

			buttonlist: List[Button] = []
			textbuttonlist: List[Button] = []
			y_diff = (self.screen_height - 2*menuY - len(itemlist) * images[0].get_height() * scale) // (len(itemlist) + 1) + images[0].get_height() * scale
			for i, item in enumerate(itemlist):
				item_button = Button(self.screen_width - menuX - images[0].get_width() * scale - 10 * sizeratio_x, menuY - images[i].get_height() * scale + y_diff * (i+1), images[i], scale)
				text_box = pygame.Rect(menuX + 10 * sizeratio_x, menuY - images[i].get_height()/2 * scale + y_diff * (i+1), self.screen_width - 2 * menuX - 50 * sizeratio_x - images[i].get_height() * scale, images[i].get_height() * scale)
				text_button = Button(menuX + 10 * sizeratio_x, menuY - images[i].get_height()/2 * scale + y_diff * (i+1), [font, itemlist[i].description, "white", text_box], 1)

				buttonlist.append(item_button)
				textbuttonlist.append(text_button)

			# Game loop
			run = True
			while run:
				window = pygame.Rect(menuX, menuY, self.screen_width - 2*menuX, self.screen_height - 2*menuY)
				pygame.draw.rect(self.screen, (52, 78, 91), window)

				# Check menu state
				if self.state == "weapon_selector" or self.state == "passive_selector":
					# Draw item selection buttons
					for i, item in enumerate(itemlist):
						if buttonlist[i].draw(self.screen) or textbuttonlist[i].drawText(self.screen):
							return ["closed", itemlist[i]]

				# Event handler
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

				if self.test['mode']:
					return ('test', itemlist[0])

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

		self.border = None
		self.rect.topleft = (x, y)
		self.clicked = False
		self.timeout = 5
	
	def addBorder(self, width: int = 1, colour: str = 'black', radius: tuple = (0, 0, 0, 0), padding: tuple = (0, 0, 0, 0)):
		rect = pygame.Rect(self.rect.x - padding[2], self.rect.y - padding[0], self.rect.width + padding[2] + padding[3], self.rect.height + padding[0] + padding[1])
		self.border = {
			'width': width,
			'colour': colour,
			'radius': radius,
			'padding': padding,
			'rect': rect
		}

	def draw(self, surface: pygame.Surface, hovercheck = False):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()
		if hovercheck:
			if self.rect.collidepoint(pos):
				action = True
			else:
				action = False

		else:
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

		if self.border:
			pygame.draw.rect(surface, self.border['colour'], self.border['rect'], self.border['width'], 
					border_top_left_radius = self.border['radius'][0], border_top_right_radius = self.border['radius'][1],
					border_bottom_left_radius = self.border['radius'][2], border_bottom_right_radius = self.border['radius'][3])

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

class Slider():
	def __init__(self, name: str, position: pygame.Vector2, width, height, font: pygame.font.Font, initial_val: float, min: int, max: int):
		self.name = name
		self.position = position
		self.container_rect = pygame.Rect(self.position.x, self.position.y, width, height)
		self.hovered = False
		self.grabbed = False
		self.font = font

		self.min = min
		self.max = max
		self.initial_val = self.container_rect.width * initial_val # <- percentage

		self.buttonstates = {
			True:"white",
			False:"black"
		}

		
		self.button_rect = pygame.Rect(self.position.x + self.initial_val - 5, self.position.y, 10, self.container_rect.height)

		# label
		self.text_label = self.font.render(str(int(self.get_value())), True, "white", None)
		self.label_rect = self.text_label.get_rect(center = (self.position.x + self.container_rect.width + 20, self.position.y + 10))

		# name
		self.text_name = self.font.render(str(self.name), True, "white", None)
		self.name_rect = self.text_name.get_rect(center = (self.position.x + self.container_rect.width/2, self.position.y - 15))
		
	def move_slider(self, mouse_pos):
		pos = mouse_pos[0]
		if pos < self.position.x:
			pos = self.position.x
		if pos > self.position.x + self.container_rect.width:
			pos = self.position.x + self.container_rect.width
		self.button_rect.centerx = pos

	def hover(self):
		self.hovered = True

	def render(self, screen):
		pygame.draw.rect(screen, "darkgray", self.container_rect)
		pygame.draw.rect(screen, self.buttonstates[self.hovered], self.button_rect)

	def get_value(self):
		val_range = self.position.x + self.container_rect.width - self.position.x - 1
		button_val = self.button_rect.centerx - self.position.x
		return (button_val/val_range)*(self.max-self.min)+self.min
	
	def display_value(self, screen):
		self.text_label = self.font.render(str(int(self.get_value())), True, "white", None)
		screen.blit(self.text_label, self.label_rect)
		screen.blit(self.text_name, self.name_rect)


class Dropdown():
	def __init__(self, name: str, position: pygame.Vector2, width, height, options, font: pygame.font.Font, screen_width, screen_height):
		self.name = name
		self.position = position
		self.main_rect = pygame.Rect(self.position.x, self.position.y, width, height)
		self.main_border_rect = pygame.Rect(self.position.x-3, self.position.y-3, width+6, height+6)
		self.options = options
		self.font = font
		self.clicked = False
		self.timeout = 5

		current_res = [item for item in self.options if item['width'] == screen_width and item['height'] == screen_height]
		self.chosen_option = self.options[0] if len(current_res) == 0 else current_res[0]

		self.buttonstates = {
			True:"red",
			False:"black"
		}

		self.options_rect = pygame.Rect(self.position.x, self.position.y, width, height * (len(self.options) + 1))

		# name
		self.text_name = self.font.render(str(self.name), True, "white", None)
		self.name_rect = self.text_name.get_rect(center = (self.position.x + self.main_rect.width/2, self.position.y - 15))

	def draw(self, screen):
		pos = pygame.mouse.get_pos()
		if self.timeout == 0:
			if self.main_rect.collidepoint(pos):
				if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
					self.timeout = 5
					self.clicked = True
					return False

			elif self.options_rect.collidepoint(pos):
				if pygame.mouse.get_pressed()[0] == 1 and self.clicked == True:
					option_step = (pos[1] - self.position.y) // self.main_rect.height - 1
					self.chosen_option = self.options[int(option_step)]
					self.timeout = 5
					self.clicked = False
					return True

			else:
				if pygame.mouse.get_pressed()[0] == 1 and self.clicked == True:
					self.timeout = 5
					self.clicked = False
					return False

		else:
			if pygame.mouse.get_pressed()[0] == 0:
				self.timeout -= 1

		#draw button on self.screen
		pygame.draw.rect(screen, self.buttonstates[self.clicked], self.main_border_rect)
		pygame.draw.rect(screen, "grey", self.main_rect)

		main_text = self.font.render(str(self.chosen_option['width'])+' x '+str(self.chosen_option['height']), True, "black", None)
		main_text_rect = main_text.get_rect(center = (self.main_rect.x + self.main_rect.width/2, self.main_rect.y + 10))
		screen.blit(main_text, main_text_rect)

		if self.clicked:
			for i, option in enumerate(self.options):
				curr_option_rect = pygame.rect.Rect(self.position.x, self.position.y +  + self.main_rect.height * (i+1), self.main_rect.width, self.main_rect.height)
				curr_option_border_rect = pygame.rect.Rect(self.position.x - 1, self.position.y +  + self.main_rect.height * (i+1) - 1, self.main_rect.width + 2, self.main_rect.height + 2)
				
				pygame.draw.rect(screen, "black", curr_option_border_rect)
				pygame.draw.rect(screen, "grey", curr_option_rect)
				curr_option_text = self.font.render(str(option['width'])+' x '+str(option['height']), True, "black", None)
				curr_option_text_rect = curr_option_text.get_rect(center = (curr_option_rect.x + curr_option_rect.width/2, curr_option_rect.y + 10))
				screen.blit(curr_option_text, curr_option_text_rect)