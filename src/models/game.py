import pygame
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
    
    def openMenu(self, menu: Menu):
        self.gamePause()
        menu.open(self.screen_width, self.screen_height)

    def gamePause(self):
        pass
    
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

            self.drawBackground(screen) # Draw background and border of the map

            mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) # Get mouse pos

            pygame.draw.circle(screen, "red", (self.player_pos.x, self.player_pos.y), self.player_radius) # Draw player

            self.writeOnScreen(screen)  # Write some stuff on the screen

            self.checkKeysPressed(dt) # Update background position based on player movement

            pygame.display.flip() # flip() the display to put your work on screen

            dt = clock.tick(self.settings.fps) / 1000 # dt is delta time in seconds since last frame

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
    
    def checkKeysPressed(self, dt):
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
            m1 = Menu()
            self.openMenu(m1)

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

p1 = Player("admin","12345")
game1 = Game()
game1.gameSetup("normal","fast", 60, screeninfo.get_monitors()[0].width, screeninfo.get_monitors()[0].height, 40)
game1.gameRun(p1)