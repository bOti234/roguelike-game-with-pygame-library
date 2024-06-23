from .gameobject import Enemy, PlayerCharacter
from pygame import Vector2, sprite
import math
import random

class Event():
    def __init__(self, name, numberofenemies, event_type, duration, spawn_cooldown):    # Setting the attributes of the event
        self.name = name
        self.numberofenemies_left = numberofenemies
        self.numberofenemies = numberofenemies
        self.event_type = event_type
        self.duration_max = duration
        self.duration_left = duration
        self.enemylist: sprite.Group[Enemy] = sprite.Group()
        self.spawn_cooldown_current = spawn_cooldown
        self.spawn_cooldown_max = spawn_cooldown

    # This function sets one of the events attribute to a random point on a circle around the player 
    def getRandPos(self, player: PlayerCharacter, posX, posY):  # If an enemy spaws, they need a random position around the player
        self.randangle = 360 * random.random()
        self.randpos = Vector2(player.position.x + posX * math.sin(self.randangle * math.pi / 180), player.position.y + posY * math.cos(self.randangle * math.pi / 180))

    def populateEnemyList(self, enemylevel, player: PlayerCharacter, weaponlist, GameEnemyGroup: sprite.Group):
        #enemylevel = enemylevel if enemylevel < 30 else 30 # I changed this mechanic in gameobject.py, but I'll keep this here just in case
        if self.event_type == "cage":
            rotation = 360 / self.numberofenemies   # ⬅️This and ⬇️this makes a complete circle around the player when all enemies are spawned. 
            position = Vector2(player.position.x + 1300 * math.sin(rotation * (self.numberofenemies - self.numberofenemies_left) * math.pi / 180), 
                               player.position.y + 1300 * math.cos(rotation * (self.numberofenemies - self.numberofenemies_left) * math.pi / 180))
            level = enemylevel 
            radius = 30
            health = 200 + 75 * enemylevel
            colour = "orange"
            speed = 6
            damage = 10
            enemy = Enemy(weaponlist, position, level, radius, health, colour, damage, speed, event_type = self.event_type, targetable = False)
            enemy.position_destination = Vector2(player.position.x + 400 * math.sin(rotation * (self.numberofenemies - self.numberofenemies_left) * math.pi / 180), # The destination is 400 units from the players location at the time the enemies are spawned
                                                 player.position.y + 400 * math.cos(rotation * (self.numberofenemies - self.numberofenemies_left) * math.pi / 180)) # With this, these enemies will stand in a circle when they arrive.
        
        elif self.event_type == "chase":
            position = Vector2(player.position.x + (250 + 550 * random.random()) * random.choice([-1, 1]), player.position.y + (250 + 350 * random.random()) * random.choice([-1, 1]))
            level = 1
            radius = 25
            health = 350 + 75 * enemylevel
            colour = "gold"
            speed = 60 + enemylevel
            damage = 0
            enemy = Enemy(weaponlist, position, level, radius, health, colour, damage, speed, type = 'lootgoblin', event_type = self.event_type, targetable = True)
            enemy.position_destination = Vector2(player.position.x + (50 + 100 * random.random()) * random.choice([-1, 1]), player.position.y + (50 + 100 * random.random()) * random.choice([-1, 1]))
        
        elif self.event_type == 'dodge':
            randangle = 360 * random.random()   # Setting a random position
            position = Vector2(player.position.x + 1350 * math.sin(randangle * math.pi / 180), player.position.y + 1100 * math.cos(randangle * math.pi / 180))
            level = 0
            radius = 7
            health = 1
            colour = "black"
            speed = 200 + enemylevel * 2
            damage = player.health_max//(20 - enemylevel//2)
            enemy = Enemy(weaponlist, position, level, radius, health, colour, damage, speed, event_type = self.event_type, targetable = False)
            enemy.position_destination = Vector2(player.position.x - (position.x - player.position.x)*3, player.position.y - (position.y - player.position.y)*3)    # The destination is on the same segment as the vector between the bullet and the player, but it's on the other side of the player.
        
        elif self.event_type == 'group':
            if self.numberofenemies_left == self.numberofenemies:
                self.getRandPos(player, 1000, 750)  # Sets a random position areound the player, then spawns (⬇️) the enemies around this position, making the group more spread out
            position = Vector2(self.randpos.x + 200 * random.random() * random.choice([-1, 1]), self.randpos.y + 200 * random.random() * random.choice([-1, 1]))
            enemy = Enemy(weaponlist, position, enemylevel+5, event_type = self.event_type, targetable = True)
            enemy.position_destination = Vector2(player.position.x, player.position.y)

        elif self.event_type == 'miniboss':
            randangle = 360 * random.random()
            position = Vector2(player.position.x + 1500 * math.sin(randangle * math.pi / 180), player.position.y + 1250 * math.cos(randangle * math.pi / 180))
            level = enemylevel
            radius = 40
            health = 300 + 100 * enemylevel
            colour = "cyan"
            speed = 8 + 0.2 * enemylevel
            damage = 25 + 3 * enemylevel//2
            enemy = Enemy(weaponlist, position, level, radius, health, colour, damage, speed, type = 'miniboss', event_type = self.event_type, targetable = True)

        self.enemylist.add(enemy)
        GameEnemyGroup.add(enemy)   # Adds the enemy to both of the events group and the Game classes group
        return GameEnemyGroup


    def updateTimer(self, dt):  # if the duration reaches 0, it kills all enemies and returns True. Otherwise, it reduces the duration and returns False
        if self.duration_left > 0:
            self.duration_left -= dt
            return False
        else:
            self.duration_left = self.duration_max
            if self.event_type != 'group' and self.event_type != 'miniboss':
                for enemy in self.enemylist:
                    enemy.kill()
        return True