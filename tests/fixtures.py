import pygame
import pytest
from frontend.models.game import Game

@pytest.fixture(scope="module")
def pygame_setup():
    if not pygame.get_init():
        pygame.init()
    screen = pygame.display.set_mode((800, 600))
    yield screen
    if pygame.init():
        pygame.quit()

@pytest.fixture()
def game():
    Game.remove_instance()
    game = Game.get_instance()
    yield game