import pytest
import pygame

def pytest_sessionfinish(session, exitstatus):
    if pygame.get_init():
        pygame.quit()
    print("\n\nAll tests finished!\n")