from .gameobject import Enemy, PlayerCharacter
from pygame import Vector2, sprite
import math
import random

class Event():
    def __init__(self, name, numberofenemies, event_type, duration):
        self.name = name
        self.numberofenemies = numberofenemies
        self.event_type = event_type
        self.duration_max = duration
        self.duration_left = duration
        self.enemylist: sprite.Group[Enemy] = sprite.Group()

    def populateEnemyList(self, player: PlayerCharacter, weaponlist):
        for x in range(self.numberofenemies):
            if self.event_type == "cage":
                rotation = 360 / self.numberofenemies
                position = Vector2(player.position.x + 1100 * math.sin(rotation * x * math.pi / 180), player.position.y + 1100 * math.cos(rotation * x * math.pi / 180))
                radius = 30
                health = 999
                colour = "orange"
                speed = 6
                enemy = Enemy(position, 1, radius, health, colour, 10, speed, event_type = self.event_type)
                enemy.position_destination = Vector2(player.position.x + 400 * math.sin(rotation * x * math.pi / 180), player.position.y + 400 * math.cos(rotation * x * math.pi / 180))
                enemy.setStatusDict(weaponlist)
                self.enemylist.add(enemy)
            elif self.event_type == "chase":
                position = Vector2(player.position.x + (250 + 550 * random.random()) * random.choice([-1, 1]), player.position.y + (250 + 350 * random.random()) * random.choice([-1, 1]))
                radius = 25
                health = 350
                colour = "gold"
                speed = 60
                enemy = Enemy(position, 0, radius, health, colour, 0, speed, event_type = self.event_type)
                enemy.position_destination = Vector2(player.position.x + (50 + 100 * random.random()) * random.choice([-1, 1]), player.position.y + (50 + 100 * random.random()) * random.choice([-1, 1]))
                enemy.setStatusDict(weaponlist)
                self.enemylist.add(enemy)


    def updateTimer(self, dt):
        # if self.event_type == "cage":
        #     for enemy in self.enemylist:
        #         pass
        # elif self.event_type == "chase":
        #     pass

        # Counting down the event.
        if self.duration_left > 0:
            self.duration_left -= dt
            return False
        else:
            self.duration_left = self.duration_max
            for enemy in self.enemylist:
                enemy.kill()
        return True