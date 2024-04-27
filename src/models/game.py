import pygame
import math
import time
import random
import screeninfo
from typing import List, Dict
from player import User
from gamesettings import GameSettings
from gameobject import GameObject, PlayerCharacter, Weapon, Enemy, Experience, WeaponKit, HUD, Inventory, Menu

class Game():
    def __init__(self):
        self.difficultylist: List[str] = ["easy","normal","hard"]
        self.speedlist: List[str] = ["slow","normal","fast"]
        self.players: List[User] = []
        self.scoreboard: List[int] = []
    
    def setSpeed(self, speed: str) -> int:
        if speed in self.speedlist:
            if speed == "slow":
                return 100
            if speed == "normal":
                return 300
            if speed == "fast":
                return 500
        else:
            return 300
    
    def gameSetup(self, difficulty: str, speed: str, fps: int, screen_width: int, screen_height: int, game_size: int):
        self.settings: GameSettings = GameSettings(
            difficulty = difficulty, 
            speed = self.setSpeed(speed), 
            fps = fps, 
            screen_width = screen_width, 
            screen_height = screen_height,
            game_size = game_size
            )
        self.player_radius = 40 # With this only the map will be affected by game size                     #self.settings.game_size    # Bit unnecesary
        self.player_pos: pygame.Vector2 = pygame.Vector2(self.settings.screen_width / 2, self.settings.screen_height / 2)
        self.playerCharacter = PlayerCharacter(self.player_radius, self.player_pos)

        self.background: pygame.Vector2  = pygame.Vector2(self.player_pos.x, self.player_pos.y)

        base_weapon = Weapon("base weapon", 1.5, "normal", "single straight", "white", 30, 25, self.player_pos.x, self.player_pos.y)
        circle_weapon = Weapon("circle weapon", 0.3, "normal", "single circle", "white", 15, 40, 0, 0)
        self.player_weapons: List[Weapon] = [base_weapon, circle_weapon]
        self.WeaponKitGroup: pygame.sprite.Group[WeaponKit] = pygame.sprite.Group()
        self.WeaponKitCooldown = 0
        self.onpause = False
    
    def openMenu(self, menu: Menu, screen):
        self.onpause = True
        #self.openedHUD = menu
        menu.state = "ingame"
        response = menu.openInGameMenu(screen, self.settings.screen_width, self.settings.screen_height, self.onpause)
        if response == "closed":
            #self.openedHUD.run = False
            #wself.openedHUD = None
            self.onpause = False

    def gameRun(self, user: User):
        pygame.init()
        screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        clock = pygame.time.Clock()
        running = True
        dt = 0

        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if self.onpause != True:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) # Get mouse pos

                self.drawBackground(screen) # Draw background and border of the map

                pygame.draw.circle(screen, "red", (self.player_pos.x, self.player_pos.y), self.player_radius) # Draw player

                self.checkHitboxes(screen)
                #self.spawnEnemies(screen)

                self.spawnWeaponKit(screen, dt)

                self.writeOnScreen(screen, str(self.background.x)+" "+str(self.background.y))  # Write some stuff on the screen

                self.checkKeysPressed(dt, screen) # Update background position based on player movement

                self.attackCycle(screen, mouse_pos, dt)    # Drawing the weapon attacks

                pygame.display.flip() # flip() the display to put your work on screen

                dt = clock.tick(self.settings.fps) / 1000 # dt is delta time in seconds since last frame
            
            else:
                self.checkKeysPressed(dt, screen)

        pygame.quit()

    def notTouchingBorder(self, dt):
        li = []
        if (self.background.x - self.settings.screen_width + self.settings.game_size**2*2 - self.player_radius + 300 * dt)  <= self.player_pos.x:
            li.append(False)
            li.append("right")
        if (self.background.x - self.settings.screen_width + self.player_radius + 300 * dt)  >= self.player_pos.x:
            li.append(False)
            li.append("left")
        if (self.background.y - self.settings.screen_height + self.player_radius + 300 * dt)  >= self.player_pos.y:
            li.append(False)
            li.append("up")
        if (self.background.y - self.settings.screen_height + self.settings.game_size**2*2 - self.player_radius + 300 * dt)  <= self.player_pos.y:
            li.append(False)
            li.append("down")
        if len(li) == 0:
            li = [True, "nothing"]
        return list(set(li))
    
    def checkKeysPressed(self, dt, screen):
        keys = pygame.key.get_pressed()
        gate = self.notTouchingBorder(dt)   #TODO: CHECK WHAT HAPPENS WHEN >2 BUTTONS ARE PRESSED
        if keys[pygame.K_w] and keys[pygame.K_a] and "up" not in gate and "left" not in gate:
            self.background.y += self.settings.speed * dt / 2**(1/2)
            self.background.x += self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and keys[pygame.K_d] and "up" not in gate and "right" not in gate:
            self.background.y += self.settings.speed * dt / 2**(1/2)
            self.background.x -= self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and "up" not in gate:
            self.background.y += self.settings.speed * dt

        elif keys[pygame.K_s] and keys[pygame.K_a] and "down" not in gate and "left" not in gate:
            self.background.y -= self.settings.speed * dt / 2**(1/2)
            self.background.x += self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and keys[pygame.K_d] and "down" not in gate and "right" not in gate:
            self.background.y -= self.settings.speed * dt / 2**(1/2)
            self.background.x -= self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and "down" not in gate:
            self.background.y -= self.settings.speed * dt

        elif keys[pygame.K_a] and "left" not in gate:
            self.background.x += self.settings.speed * dt

        elif keys[pygame.K_d] and "right" not in gate:
            self.background.x -= self.settings.speed * dt
        
        if keys[pygame.K_ESCAPE]:
            if not self.onpause:
                m1 = Menu()
                self.openMenu(m1, screen)

    def checkHitboxes(self, screen):
        self.writeOnScreen(screen, str(self.player_pos.x)+" "+str(self.player_pos.y), self.player_pos.x, self.player_pos.y)
        for kit in self.WeaponKitGroup:
            if pygame.sprite.collide_rect(kit, self.playerCharacter):   # This is the best feature ever, although, my player is a circle and the boxes are squares...
                kit.kill()
                response = self.selectWeapon()

    def selectWeapon(self):
        time.sleep(1)
        self.onpause = True
        time.sleep(5)           #TODO SELECTING WEAPON PAGE
        self.onpause = False

    def drawBackground(self, screen):
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("#124a21")
        # Fill the smaller background surface within the screen boundaries
        background_rect = pygame.Rect(
            self.background.x - self.settings.screen_width,
            self.background.y - self.settings.screen_height,
            self.settings.game_size**2 * 2,
            self.settings.game_size**2 * 2
            )
        # Fill the smaller background surface
        pygame.draw.rect(screen, "#39ad58", background_rect)
        # Draw background lines
        for i in range(self.settings.game_size+1):
            if i == 0 or i == self.settings.game_size:
                w = 10
            else:
                w = 1
            pygame.draw.line(
                screen, 
                "black", 
                (self.background.x - self.settings.screen_width + i * self.settings.game_size * 2, self.background.y - self.settings.screen_height), 
                (self.background.x - self.settings.screen_width + i * self.settings.game_size * 2, self.background.y - self.settings.screen_height + self.settings.game_size**2 * 2),
                w)    # Vertical lines
            
            pygame.draw.line(
                screen, 
                "black", 
                (self.background.x - self.settings.screen_width, self.background.y - self.settings.screen_height + i * self.settings.game_size * 2), 
                (self.background.x - self.settings.screen_width + self.settings.game_size**2 * 2, self.background.y - self.settings.screen_height + i * self.settings.game_size * 2), 
                w)    # Horizontal lines

    def spawnWeaponKit(self, screen, dt):
        for kit in self.WeaponKitGroup:
            kit.setPositionBasedOnMovement(self.settings.speed, dt, self.notTouchingBorder(dt))
            rect = pygame.Rect(kit.position.x, kit.position.y, kit.width, kit.height)
            pygame.draw.rect(screen, "gray", rect)
            pygame.draw.rect(screen, "black", rect, 3)
            self.writeOnScreen(screen, str(kit.position.x)+" "+str(kit.position.y), kit.position.x, kit.position.y)
        if self.WeaponKitCooldown == 0:
            chance = random.random()
            if chance > 0.8:
                randpos = pygame.Vector2(
                    random.randint(round(self.background.x - self.settings.screen_width), round(self.background.x - self.settings.screen_width + self.settings.game_size**2 * 2)), 
                    random.randint(round(self.background.y - self.settings.screen_height), round(self.background.y - self.settings.screen_height + self.settings.game_size**2 * 2))
                    )
                kit = WeaponKit(randpos, 50, 50)
                self.WeaponKitGroup.add(kit)
                rect = pygame.Rect(randpos.x, randpos.y, kit.width, kit.height)
                pygame.draw.rect(screen, "gray", rect)
                pygame.draw.rect(screen, "black", rect, 3)
                self.WeaponKitCooldown = 10000
        else:
            self.WeaponKitCooldown -= 1
    
    
    def writeOnScreen(self, screen, txt, posX = 0, posY = 0):
        font = pygame.font.Font(None, 30)
        # Kinda consol log -> Write stuff on the canvas
        player_pos_text = font.render(txt, True, "black")
        screen.blit(player_pos_text, (posX, posY))
    
    def attackCycle(self, screen: pygame.Surface, mouse_pos: pygame.Vector2, dt):
        for weapon in self.player_weapons: #TODO Put them in a sprite group so that I can check for hitboxes later
            if weapon.cooldown_current <= 0:
                weapon.setOnCooldown()
                weapon.animation = True
            else:
                weapon.updateCooldown(dt)
            if weapon.animation:
                if "straight" in weapon.pattern:
                    if weapon.position_destination.x == 0 and weapon.position_destination.y == 0:
                        weapon.animation = True
                        weapon.position_destination = mouse_pos
                    distance = math.sqrt((weapon.position_destination.x - weapon.position_original.x)**2 + (weapon.position_destination.y - weapon.position_original.y)**2)
                    sinus = abs((weapon.position_destination.y - weapon.position_original.y)/distance) * self.compare_subtraction(weapon.position_destination.y,weapon.position_original.y)
                    cosinus = abs((weapon.position_destination.x - weapon.position_original.x)/distance) * self.compare_subtraction(weapon.position_destination.x,weapon.position_original.x)

                    weapon.setPositionBasedOnMovement(self.settings.speed, dt, self.notTouchingBorder(dt))

                    weapon.position.x += cosinus * weapon.speed
                    weapon.position.y += sinus * weapon.speed
                    pygame.draw.line(screen, weapon.colour, (weapon.position.x - cosinus * weapon.size, weapon.position.y - sinus * weapon.size), (weapon.position.x, weapon.position.y), 15)
                    
                    if weapon.cooldown_current <= 0:
                        weapon.animation = False
                        weapon.position_destination.x = 0
                        weapon.position_destination.y = 0
                        weapon.position.x = weapon.position_original.x
                        weapon.position.y = weapon.position_original.y
                
                if "circle" in weapon.pattern:
                    if weapon.rotation == 360:
                        weapon.rotation = 0
                    weapon.position.x = self.player_pos.x + 250 * math.cos(weapon.rotation)
                    weapon.position.y = self.player_pos.y + 250 * math.sin(weapon.rotation)
                    weapon.setPositionBasedOnMovement(self.settings.speed, dt, self.notTouchingBorder(dt))

                    pygame.draw.circle(screen, weapon.colour, (weapon.position.x, weapon.position.y), weapon.size)

                    weapon.rotation += weapon.speed * 0.001
        
    def compare_subtraction(self, a, b):
        result = a - b
        return 1 if result > 0 else -1


p1 = User("admin","12345")
game1 = Game()
game1.gameSetup(
    difficulty = "normal",
    speed = "fast", 
    fps = 60, 
    screen_width = screeninfo.get_monitors()[0].width, 
    screen_height = screeninfo.get_monitors()[0].height, 
    game_size = 40
    )
game1.gameRun(p1)