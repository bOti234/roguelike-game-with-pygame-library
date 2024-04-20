import pygame
import sys

class GameObject():
    def __init__(self, objtype):
        self.objtype = objtype

class Weapon(GameObject):
    def __init__(self):
        pass

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

            # Button class
            class Button:
                def __init__(self, x, y, width, height, text):
                    self.rect = pygame.Rect(x, y, width, height)
                    self.text = text

                def draw(self):
                    pygame.draw.rect(screen, GRAY, self.rect)
                    text_surface = font.render(self.text, True, BLACK)
                    text_rect = text_surface.get_rect(center=self.rect.center)
                    screen.blit(text_surface, text_rect)

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