import pygame
import sys

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
        self.dist = 0
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
        pass

    def open(self, screen_width, screen_height):
        if pygame.get_init():
            # Set up the screen
            screen_width = 800
            screen_height = 600
            screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Pygame Menu")

            # Colors
            WHITE = (255, 255, 255)
            BLACK = (0, 0, 0)
            GRAY = (200, 200, 200)

            # Fonts
            font = pygame.font.Font(None, 36)

            # Create a template button
            template_button = Button(300, 250, 200, 50, "Template Button")

            # Main loop
            running = True
            while running:
                # Event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # Clear the screen
                screen.fill(WHITE)

                # Draw the template button
                template_button.draw()

                # Update the display
                pygame.display.flip()

            # Quit Pygame
            pygame.quit()
            sys.exit()

# Button class
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, screen, colour1, colour2, font):
        pygame.draw.rect(screen, colour1, self.rect)
        text_surface = font.render(self.text, True, colour2)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)