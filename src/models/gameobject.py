from typing import List, Dict, Union
import pygame
import os

class GameObject(pygame.sprite.Sprite):
    def __init__(self, objtype: str, position, width: int, height: int):
        pygame.sprite.Sprite.__init__(self)
        self.objtype: str = objtype
        self.position: pygame.Vector2 = position
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
    
    def setHitbox(self):
        pass
    
    def setPositionBasedOnMovement(self, speed, dt, gate):
        keys = pygame.key.get_pressed()
        #TODO: CHECK WHAT HAPPENS WHEN >2 BUTTONS ARE PRESSED

        if keys[pygame.K_w] and keys[pygame.K_a] and "up" not in gate and "left" not in gate:
            self.position.y += speed * dt / 2**(1/2)
            self.position.x += speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and keys[pygame.K_d] and "up" not in gate and "right" not in gate:
            self.position.y += speed * dt / 2**(1/2)
            self.position.x -= speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and "up" not in gate:
            self.position.y += speed * dt

        elif keys[pygame.K_s] and keys[pygame.K_a] and "down" not in gate and "left" not in gate:
            self.position.y -= speed * dt / 2**(1/2)
            self.position.x += speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and keys[pygame.K_d] and "down" not in gate and "right" not in gate:
            self.position.y -= speed * dt / 2**(1/2)
            self.position.x -= speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and "down" not in gate:
            self.position.y -= speed * dt

        elif keys[pygame.K_a] and "left" not in gate:
            self.position.x += speed * dt

        elif keys[pygame.K_d] and "right" not in gate:
            self.position.x -= speed * dt
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)

class PlayerCharacter(GameObject):
    def __init__(self, radius, position):
        objtype = "player"
        super().__init__(objtype, pygame.Vector2(position.x-radius, position.y-radius), radius*2, radius*2)
        self.radius = radius

class Weapon(GameObject):
    def __init__(self, name: str, cooldown_max: float, dmgtype: str, pattern: str, colour: str, size: int, speed: int, bulletlifetime: Union[int, str], x: int, y: int):
        objtype = "weapon"
        self.pattern: str = pattern
        position = pygame.Vector2(x,y)
        if "circle" in self.pattern or "angled" in self.pattern:
            self.rotation = 0
            self.distance = 150
            position.x -= size
            position.y -= size
            width_and_height = size
        else:
            self.rotation = None
            self.distance = None
            width_and_height = size

        super().__init__(objtype, position, width_and_height, width_and_height)

        self.name: str = name
        self.cooldown_max: float = cooldown_max
        self.cooldown_current: float = cooldown_max
        self.dmgtype: str = dmgtype
        self.level = 0
        self.colour: str = colour
        self.size: int = size
        self.speed: int = speed
        self.bulletLifeTime = bulletlifetime
        self.bullets: pygame.sprite.Group[Bullet] = pygame.sprite.Group()
        self.position_original = pygame.Vector2(x,y)
        self.position_destination = pygame.Vector2(0,0)
        self.animation = False

        self.loadImages()
    
    def loadImages(self):
        if pygame.get_init():
            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, '../../images/weapons/')
            self.image_base = pygame.image.load(filename + "/"+str(self.name)+"_1.jpg").convert_alpha()
            self.image_maxed = pygame.image.load(filename + "/"+str(self.name)+"_2.jpg").convert_alpha()

    def updateCooldown(self, dt):
        if self.cooldown_current > 0:
            self.cooldown_current -= dt
        if self.cooldown_current < 0:
            self.cooldown_current = 0
    
    def setOnCooldown(self):
        if self.cooldown_current <= 0:
            self.cooldown_current = self.cooldown_max
    
    def upgradeWeapon(self):
        if self.level < 5:
            self.level += 1

        if "straight" in self.pattern:
            self.speed += 4
            self.size += 2
        
        if self.name == "High-tech Rifle":
            self.cooldown_max -= 0.1 * (5 - self.level)
            if self.level == 3:
                self.pattern = "multiple straight"
            if self.level == 5:
                self.speed -= 3
        
        if self.name == "Flamethrower":
            self.cooldown_max -= 0.02
            self.speed -= (1 - self.level)
            self.size += 1
            self.bulletLifeTime -= 0.025
            if self.level == 5:
                self.cooldown_max += 0.01
                self.bulletLifeTime += 0.02
        
        if self.name == "Pistols":
            self.speed -= 3
            self.cooldown_max -= 0.02
            self.bulletLifeTime += 0.05
            
        
        if "circle" in self.pattern:
            self.speed *= 1.1
            self.size += 5
            self.distance += 50
        
        if "angled" in self.pattern:
            self.cooldown_max -= 0.35
            self.size += 2
            self.speed += 2
            if self.level >= 4:
                self.size += 1
                self.speed += 1
    
class Bullet(GameObject):
    def __init__(self, position: pygame.Vector2, position_original: pygame.Vector2, position_destination: pygame.Vector2, lifetime: float, crit: bool, objtype: str, width_and_height: int):
        super().__init__(objtype, position, width_and_height, width_and_height)
        self.position = position
        self.position_original = position_original
        self.position_destination = position_destination
        self.lifeTime: float = lifetime
        self.crit: bool = crit

    def addRotation(self, rotation):
        self.rotation = rotation
        
    def addAnimationRotation(self, rotation):
        self.animation_rotation = rotation


class Enemy(GameObject):
    def __init__(self):
        pass

class Experience(GameObject):
    def __init__(self):
        pass

class WeaponKit(GameObject):
    def __init__(self, randpos, width, height):
        objtype = "weaponkit"
        super().__init__(objtype, randpos, width, height)

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
            filename = os.path.join(dirname, '../../images/buttons/')
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
    
    def openWeaponSelectorMenu(self, screen, screen_width: int, screen_height: int, paused: bool, weaponlist: List[Weapon]):
        if pygame.get_init():
            # Load button images for menu buttons selection
            for weapon in weaponlist:
                weapon.loadImages()

            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, '../../images/buttons/')
            get_img = pygame.image.load(filename + "/button_select.png").convert_alpha()

            # Create button instances for weapon selection
            images: List[pygame.Surface] = []
            for i in range(len(weaponlist)):
                if weaponlist[i].level < 4:
                    images.append(weaponlist[i].image_base)
                else:
                    images.append(weaponlist[i].image_maxed)

            if len(weaponlist) == 1:
                weapon1_button = Button(screen_width / 2 - images[0].get_width() * 0.1 / 2, screen_height / 4 + 125, images[0], 0.1)
                get_button1 = Button(screen_width / 2 - get_img.get_width() / 2, screen_height / 4 + 425, get_img, 1)
            
            elif len(weaponlist) == 2:
                weapon1_button = Button(screen_width / 2 - images[0].get_width() * 0.1 / 2 - 150, screen_height / 4 + 125, images[0], 0.1)
                weapon2_button = Button(screen_width / 2 - images[1].get_width() * 0.1 / 2 + 150, screen_height / 4 + 125, images[1], 0.1)

                get_button1 = Button(screen_width / 2 - get_img.get_width() / 2 - 150, screen_height / 4 + 425, get_img, 1)
                get_button2 = Button(screen_width / 2 - get_img.get_width() / 2 + 150, screen_height / 4 + 425, get_img, 1)
            
            elif len(weaponlist) == 3:
                weapon1_button = Button(screen_width / 2 - images[0].get_width() * 0.1 / 2 - 300, screen_height / 4 + 125, images[0], 0.1)
                weapon2_button = Button(screen_width / 2 - images[1].get_width() * 0.1 / 2, screen_height / 4 + 125, images[1], 0.1)
                weapon3_button = Button(screen_width / 2 - images[2].get_width() * 0.1 / 2 + 300, screen_height / 4 + 125, images[2], 0.1)

                get_button1 = Button(screen_width / 2 - get_img.get_width() / 2 - 300, screen_height / 4 + 425, get_img, 1)
                get_button2 = Button(screen_width / 2 - get_img.get_width() / 2, screen_height / 4 + 425, get_img, 1)
                get_button3 = Button(screen_width / 2 - get_img.get_width() / 2 + 300, screen_height / 4 + 425, get_img, 1)

            # Game loop
            run = True
            while run:
                window = pygame.Rect(screen_width / 4, screen_height / 4, screen_width / 2, screen_height / 2)
                pygame.draw.rect(screen, (52, 78, 91), window)

                # Check if game is paused
                if paused:
                    # Check menu state
                    if self.state == "weapon_selector":
                        # Draw weapon selection buttons
                        if len(weaponlist) > 0:
                            weapon1_button.draw(screen)
                            if get_button1.draw(screen):
                                weaponlist[0].upgradeWeapon()
                                paused = False
                                return ["closed", weaponlist[0]]
                        if len(weaponlist) > 1:
                            weapon1_button.draw(screen), weapon2_button.draw(screen)
                            if get_button2.draw(screen):
                                weaponlist[1].upgradeWeapon()
                                paused = False
                                return ["closed", weaponlist[1]]
                        if len(weaponlist) > 2:
                            weapon1_button.draw(screen), weapon2_button.draw(screen), weapon3_button.draw(screen)
                            if get_button3.draw(screen):
                                weaponlist[2].upgradeWeapon()
                                paused = False
                                return ["closed", weaponlist[2]]

                # Event handler
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