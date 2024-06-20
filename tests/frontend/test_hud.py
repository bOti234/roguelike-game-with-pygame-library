import pygame
import threading
import time
from frontend.models.game import Game
from ..fixtures import game

def run_game(game: Game):
    game.gameStart(
        'normal',
        'normal',
        60,
        1920,
        1080
    )

# def test_manu_quit_button(game: Game):
#     pass