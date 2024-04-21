import pygame
import math
import time
import screeninfo
from typing import List, Dict
from player import Player
from gamesettings import GameSettings
from gameobject import GameObject, Weapon, Enemy, Collectible, HUD, Inventory, Menu

class Game():
    def __init__(self):
        self.difficultylist: List[str] = ["easy","normal","hard"]
        self.speedlist: List[str] = ["slow","normal","fast"]
        self.players: List[Player] = []
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
        self.player_radius = self.settings.game_size    # Bit unnecesary
        self.player_pos: pygame.Vector2 = pygame.Vector2(self.settings.screen_width / 2, self.settings.screen_height / 2)
        self.background: pygame.Vector2  = pygame.Vector2(self.player_pos.x, self.player_pos.y)

        base_weapon = Weapon("base weapon", 1.5, "normal", "single straight", "white", 30, 25, self.player_pos.x, self.player_pos.y)
        self.player_weapons: List[Weapon] = [base_weapon]
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

    def gameRun(self, player: Player):
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

                self.writeOnScreen(screen)  # Write some stuff on the screen

                self.checkKeysPressed(dt, screen) # Update background position based on player movement

                self.attackCycle(screen, mouse_pos, dt)    # Drawing the weapon attacks

                pygame.display.flip() # flip() the display to put your work on screen

                dt = clock.tick(self.settings.fps) / 1000 # dt is delta time in seconds since last frame
            
            else:
                self.checkKeysPressed(dt, screen)

        pygame.quit()

    def notTouchingBorder(self, dt):
        if (self.background.x - self.settings.screen_width + self.settings.game_size**2*2 - self.player_radius + 300 * dt)  <= self.player_pos.x:
            return [False, "right"]
        if (self.background.x - self.settings.screen_width + self.player_radius + 300 * dt)  >= self.player_pos.x:
            return [False, "left"]
        if (self.background.y - self.settings.screen_height + self.player_radius + 300 * dt)  >= self.player_pos.y:
            return [False, "up"]
        if (self.background.y - self.settings.screen_height + self.settings.game_size**2*2 - self.player_radius + 300 * dt)  <= self.player_pos.y:
            return [False, "down"]
        else:
            return [True, "nothing"]
    
    def checkKeysPressed(self, dt, screen):
        keys = pygame.key.get_pressed()
        gate = self.notTouchingBorder(dt)   #TODO: CHECK WHAT HAPPENS WHEN >2 BUTTONS ARE PRESSED
        if keys[pygame.K_w] and keys[pygame.K_a] and gate[1] != "up" and gate[1] != "left":
            self.background.y += self.settings.speed * dt / 2**(1/2)
            self.background.x += self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and keys[pygame.K_d] and gate[1] != "up" and gate[1] != "right":
            self.background.y += self.settings.speed * dt / 2**(1/2)
            self.background.x -= self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and gate[1] != "up":
            self.background.y += self.settings.speed * dt

        elif keys[pygame.K_s] and keys[pygame.K_a] and gate[1] != "down" and gate[1] != "left":
            self.background.y -= self.settings.speed * dt / 2**(1/2)
            self.background.x += self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and keys[pygame.K_d] and gate[1] != "down" and gate[1] != "right":
            self.background.y -= self.settings.speed * dt / 2**(1/2)
            self.background.x -= self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and gate[1] != "down":
            self.background.y -= self.settings.speed * dt

        elif keys[pygame.K_a] and gate[1] != "left":
            self.background.x += self.settings.speed * dt

        elif keys[pygame.K_d] and gate[1] != "right":
            self.background.x -= self.settings.speed * dt
        
        if keys[pygame.K_ESCAPE]:
            if not self.onpause:
                m1 = Menu()
                self.openMenu(m1, screen)

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

    def writeOnScreen(self, screen):
        pass
        #font = pygame.font.Font(None, 30)
        # Kinda consol log -> Write stuff on the canvas
        # player_pos_text = font.render("", True, "black")
        #screen.blit(player_pos_text, (0, 0))
    
    def attackCycle(self, screen: pygame.Surface, mouse_pos: pygame.Vector2, dt):
        for weapon in self.player_weapons:
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
        
    def compare_subtraction(self, a, b):
        result = a - b
        return 1 if result > 0 else -1


p1 = Player("admin","12345")
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