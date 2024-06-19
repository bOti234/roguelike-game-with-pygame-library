import pygame
import pytest
from frontend.models.game import Game
from app import createServer

@pytest.fixture(autouse = True)
def server():
    server_process = createServer()
    yield server_process
    server_process.terminate()
    server_process.wait()

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