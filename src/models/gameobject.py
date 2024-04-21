import pygame
import os

class GameObject():
    def __init__(self, objtype):
        self.objtype = objtype

class Weapon(GameObject):
    def __init__(self, name: str, cooldown_max: float, dmgtype: str, pattern: str, colour: str, size: int, speed: int, x: int, y: int):
        self.name: str = name
        self.cooldown_max: float = cooldown_max
        self.cooldown_current: float = cooldown_max
        self.dmgtype: str = dmgtype
        self.pattern: str = pattern
        self.colour: str = colour
        self.size: int = size
        self.speed: int = speed
        self.position_original = pygame.Vector2(x,y)
        self.position = pygame.Vector2(x,y)
        self.position_destination = pygame.Vector2(0,0)
        self.animation = False

    def updateCooldown(self, dt):
        if self.cooldown_current > 0:
            self.cooldown_current -= dt
        if self.cooldown_current < 0:
            self.cooldown_current = 0
    
    def setOnCooldown(self):
        if self.cooldown_current <= 0:
            self.cooldown_current = self.cooldown_max
    
    def setPositionBasedOnMovement(self, speed, dt, gate):
        keys = pygame.key.get_pressed()
        #TODO: CHECK WHAT HAPPENS WHEN >2 BUTTONS ARE PRESSED
        if keys[pygame.K_w] and keys[pygame.K_a] and gate[1] != "up" and gate[1] != "left":
            self.position.y += speed * dt / 2**(1/2)
            self.position.x += speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and keys[pygame.K_d] and gate[1] != "up" and gate[1] != "right":
            self.position.y += speed * dt / 2**(1/2)
            self.position.x -= speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and gate[1] != "up":
            self.position.y += speed * dt

        elif keys[pygame.K_s] and keys[pygame.K_a] and gate[1] != "down" and gate[1] != "left":
            self.position.y -= speed * dt / 2**(1/2)
            self.position.x += speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and keys[pygame.K_d] and gate[1] != "down" and gate[1] != "right":
            self.position.y -= speed * dt / 2**(1/2)
            self.position.x -= speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and gate[1] != "down":
            self.position.y -= speed * dt

        elif keys[pygame.K_a] and gate[1] != "left":
            self.position.x += speed * dt

        elif keys[pygame.K_d] and gate[1] != "right":
            self.position.x -= speed * dt


class Enemy(GameObject):
    def __init__(self):
        pass

class Collectible(GameObject):
    def __init__(self):
        pass

class HUD(GameObject):
    def __init__(self, objtype):
        pass
        #super().__init__(objtype)


class Inventory(HUD):
    def __init__(self):
        pass

class Menu(HUD):
    def __init__(self):
        self.opened = False
        self.state = None


    def openInGameMenu(self, screen, screen_width: int, screen_height: int, paused):
        if pygame.get_init():

            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, '../../images/')
            resume_img = pygame.image.load(filename+"/button_resume.png").convert_alpha()
            options_img = pygame.image.load(filename+"/button_options.png").convert_alpha()
            quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()
            video_img = pygame.image.load(filename+"/button_video.png").convert_alpha()
            audio_img = pygame.image.load(filename+"/button_audio.png").convert_alpha()
            keys_img = pygame.image.load(filename+"/button_keys.png").convert_alpha()
            back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

            #create button instances
            resume_button = Button(screen_width/2 - resume_img.get_width()/2, screen_height/4 + 125, resume_img, 1)
            options_button = Button(screen_width/2 - options_img.get_width()/2, screen_height/4 + 250, options_img, 1)
            quit_button = Button(screen_width/2 - quit_img.get_width()/2, screen_height/4 + 375, quit_img, 1)
            video_button = Button(screen_width/2 - video_img.get_width()/2, screen_height/4 + 75, video_img, 1)
            audio_button = Button(screen_width/2 - audio_img.get_width()/2, screen_height/4 + 200, audio_img, 1)
            keys_button = Button(screen_width/2 - keys_img.get_width()/2, screen_height/4 + 325, keys_img, 1)
            back_button = Button(screen_width/2 - back_img.get_width()/2, screen_height/4 + 450, back_img, 1)

            #game loop
            run = True
            while run:
                window = pygame.Rect(screen_width/4, screen_height/4, screen_width/2, screen_height/2)
                pygame.draw.rect(screen, (52, 78, 91), window)

                #check if game is paused
                if paused == True:
                    #check menu state
                    if self.state == "ingame":
                        #draw pause screen buttons
                        if resume_button.draw(screen):
                            paused = False
                            return "closed"
                        if options_button.draw(screen):
                            self.state = "options"
                        if quit_button.draw(screen):
                            run = False
                            pygame.quit()
                    #check if the options menu is open
                    if self.state == "options":
                        #draw the different options buttons
                        if video_button.draw(screen):
                            print("Video Settings")
                        if audio_button.draw(screen):
                            print("Audio Settings")
                        if keys_button.draw(screen):
                            print("Change Key Bindings")
                        if back_button.draw(screen):
                            self.state = "ingame"

                #event handler
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False

                pygame.display.update()

class Button():
	def __init__(self, x, y, image: pygame.image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
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

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action