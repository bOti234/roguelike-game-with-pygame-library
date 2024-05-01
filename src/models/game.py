import pygame
import math
import time
import random
import screeninfo
from typing import List, Dict, Union
from player import User
from gamesettings import GameSettings
from gameobject import GameObject, PlayerCharacter, Passive, Weapon, Bullet, Enemy, Experience, WeaponKit, Magnet, HUD, Inventory, Menu

class Game():
    def __init__(self):
        self.difficultylist: List[str] = ["easy","normal","hard"]
        self.speedlist: List[str] = ["slow","normal","fast"]
        self.players: List[User] = []
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
        player_radius = 40 # With this only the map will be affected by game size                     #self.settings.game_size    # Bit unnecesary
        player_position: pygame.Vector2 = pygame.Vector2(self.settings.screen_width / 2, self.settings.screen_height / 2)
        self.player = PlayerCharacter(player_radius, player_position, self.settings.speed)

        self.background: pygame.Vector2  = pygame.Vector2(self.player.position.x, self.player.position.y)

        self.passivelist = self.getPassives()
        self.player_passives: List[Passive] = []

        self.weaponlist = self.getWeapons()
        self.player_weapons: List[Weapon] = []
        if len(self.weaponlist) > 0:
           self.player_weapons.append(self.weaponlist[0])
           self.player_weapons[0].upgradeItem()

        self.bulletGroup: pygame.sprite.Group[Bullet] = pygame.sprite.Group()
        self.WeaponKitGroup: pygame.sprite.Group[WeaponKit] = pygame.sprite.Group()
        self.MagnetGroup: pygame.sprite.Group[Magnet] = pygame.sprite.Group()
        self.EnemyGroup: pygame.sprite.Group[Enemy] = pygame.sprite.Group()
        self.experienceGroup: pygame.sprite.Group[Experience] = pygame.sprite.Group()

        self.WeaponKitCooldown = 0
        self.MagnetCooldown = 0
        self.EnemyCooldown = 0

        self.time = 0
        self.onpause = False
    
    def getPassives(self):
        regen = Passive(
            name = "Health Regeneration",
            value = 1,
            cooldown = 5
        )
        return [regen]
    
    def getWeapons(self):
        rifle = Weapon(
            name = "High-tech Rifle", 
            cooldown_max = 1.5, 
            dmgtype = "normal", 
            pattern = "single straight", 
            colour = "white", 
            size = 30, 
            speed = 25, 
            bulletlifetime = 2.1, 
            damage = 10, 
            position = pygame.Vector2(self.player.position.x, self.player.position.y)
        )

        energy_ball = Weapon(
            name = "Energy Ball", 
            cooldown_max=0.1, 
            dmgtype = "energy", 
            pattern = "constant circle", 
            colour = "purple", 
            size = 15, 
            speed = 40, 
            bulletlifetime = "inf", 
            damage = 15, 
            position = pygame.Vector2(0, 0)
        )

        boomerang = Weapon(
            name = "Boomerang", 
            cooldown_max = 2.5, 
            dmgtype = "normal", 
            pattern = "single angled", 
            colour = "gray", 
            size = 20, 
            speed = 15, 
            bulletlifetime = "inf", 
            damage = 15, 
            position = pygame.Vector2(self.player.position.x, self.player.position.y)
        )

        flamethrower = Weapon(
            name = "Flamethrower", 
            cooldown_max = 0.3, 
            dmgtype = "fire", 
            pattern = "constant straight", 
            colour = "orange", 
            size = 45, 
            speed = 10, 
            bulletlifetime = 0.3, 
            damage = 2, 
            position = pygame.Vector2(self.player.position.x, self.player.position.y)
        )

        damage_field = Weapon( #TODO
            name = "Damaging Field", 
            cooldown_max = 3, 
            dmgtype = "fire", 
            pattern = "single aoe", 
            colour = "red", 
            size = 15, 
            speed = 40, 
            bulletlifetime = 4, 
            damage = 1, 
            position = pygame.Vector2(self.player.position.x, self.player.position.y)
        )

        drone = Weapon( #TODO
            name = "Attack Drone", 
            cooldown_max = 0.01, 
            dmgtype = "laser", 
            pattern = "single pet", 
            colour = "white", 
            size = 15, 
            speed = 40, 
            bulletlifetime = 0.01, 
            damage = 1, 
            position = pygame.Vector2(self.player.position.x, self.player.position.y)
        )
        
        explosion = Weapon( #TODO
            name = "Remote Explosion", 
            cooldown_max = 2.5, 
            dmgtype = "energy", 
            pattern = "single remote", 
            colour = "yellow", 
            size = 15, 
            speed = 40, 
            bulletlifetime = "inf", 
            damage = 5, 
            position = pygame.Vector2(self.player.position.x, self.player.position.y)
        )
        
        pistols = Weapon(
            name = "Pistols", 
            cooldown_max = 0.2, 
            dmgtype = "normal", 
            pattern = "multiple straight", 
            colour = "skyblue", 
            size = 20, 
            speed = 20, 
            bulletlifetime = 0.35, 
            damage = 6, 
            position = pygame.Vector2(self.player.position.x, self.player.position.y)
        )

        return [drone]#rifle, energy_ball, boomerang, flamethrower, damage_field, drone, explosion, pistols]

    def openMenu(self, menu: Menu):
        self.onpause = True
        #self.openedHUD = menu
        menu.state = "ingame"
        response = menu.openInGameMenu(self.screen, self.settings.screen_width, self.settings.screen_height, self.onpause)
        if response == "closed":
            #self.openedHUD.run = False
            #wself.openedHUD = None
            self.onpause = False

    def openSelectWeaponMenu(self):
        self.onpause = True
        weaponlist = self.getRandomWeapons()
        if len(weaponlist) > 0:
            menu = Menu()
            menu.state = "weapon_selector"
            response = menu.openItemSelectorMenu(self.screen, self.settings.screen_width, self.settings.screen_height, self.onpause, weaponlist)
            if isinstance(response[1], Weapon):
                if response[1] not in self.player_weapons:
                    self.player_weapons.append(response[1])
            if response[0] == "closed":
                self.onpause = False
        else:
            self.onpause = False
    
    def getRandomWeapons(self):
        upgradeableWeapons = [weapon for weapon in self.weaponlist if weapon.level < 5]
        if len(upgradeableWeapons) >= 3:
            return random.sample(upgradeableWeapons, 3)
        return upgradeableWeapons
    
    def openLevelUpMenu(self):
        self.onpause = True
        passivelist = self.getRandomPasives()
        if len(passivelist) > 0:
            menu = Menu()
            menu.state = "passive_selector"
            response = menu.openItemSelectorMenu(self.screen, self.settings.screen_width, self.settings.screen_height, self.onpause, passivelist)
            if isinstance(response[1], Passive):
                if response[1] not in self.player_passives:
                    self.player_passives.append(response[1])
            if response[0] == "closed":
                self.onpause = False
        else:
            self.onpause = False

    def getRandomPasives(self):
        upgradeablePassives = [passive for passive in self.passivelist if passive.level < 5]
        if len(upgradeablePassives) >= 3:
            return random.sample(upgradeablePassives, 3)
        return upgradeablePassives
    
    def openDeathMenu(self):
       pass

    def gameRun(self, user: User):
        pygame.init()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        clock = pygame.time.Clock()
        running = True
        self.dt = 0

        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if self.onpause != True:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) # Get mouse pos

                self.drawBackground() # Draw background and border of the map

                self.attackCycle(mouse_pos)    # Drawing the weapon attacks

                self.drawPlayer()

                self.checkHitboxes()

                self.spawnWeaponKit()
                self.spawnMagnet()
                self.spawnEnemies()

                self.updateWeaponKitPosition()
                self.updateMagnetPosition()
                self.updateEnemyPosition()
                self.updateExperiencePosition()

                self.writeOnScreen(str(mouse_pos.x)+" "+str(mouse_pos.y), mouse_pos.x, mouse_pos.y)  # Write some stuff on the self.screen
                self.writeOnScreen(str(self.time))  # Write some stuff on the self.screen
                self.writeOnScreen(str(self.player.experience_current)+" / "+str(self.player.experience_max), 0, 200)  # Write some stuff on the self.screen

                self.drawStatBoxes()
                
                self.checkKeysPressed() # Update background position based on player movement

                pygame.display.flip() # flip() the display to put your work on self.screen

                self.dt = clock.tick(self.settings.fps) / 1000 # self.dt is delta time in seconds since last frame
                self.time += self.dt
            else:
                self.checkKeysPressed()

        pygame.quit()

    def drawPlayer(self):
        if self.player.hitCooldown > 0:     # Draw player with diff colour based on if they were hit recently or not
            self.player.hitCooldown -= self.dt
            pygame.draw.circle(self.screen, "darkmagenta", (self.player.position.x, self.player.position.y), self.player.radius) 
        else:
            pygame.draw.circle(self.screen, "skyblue", (self.player.position.x, self.player.position.y), self.player.radius)

        p = self.player.updateExperience()
        if p:
            self.openLevelUpMenu() #TODO
    
    def drawStatBoxes(self):
        hp_rect_border = pygame.Rect(self.player.position.x - self.player.radius, self.player.position.y + 55, self.player.width , 10)
        hp_rect = pygame.Rect(self.player.position.x - self.player.radius + 4, self.player.position.y + 55 + 3, (self.player.width - 4) * self.player.health_current / self.player.health_max, 10 - 6)
        hp_rect_missing = pygame.Rect(self.player.position.x + self.player.radius, self.player.position.y + 55 + 3, -(self.player.width - 4) * (1 - (self.player.health_current / self.player.health_max)), 10 - 6)
        pygame.draw.rect(self.screen, "green", hp_rect, 0, 20)
        pygame.draw.rect(self.screen, "red", hp_rect_missing, 0, 20)
        pygame.draw.rect(self.screen, "black", hp_rect_border, 3, 20)

        exp_rect_border = pygame.Rect(800, self.settings.screen_height - 100, self.settings.screen_width - 1600 , 25)
        exp_rect = pygame.Rect(800 + 4, self.settings.screen_height - 100 + 4, (self.settings.screen_width - 1600 - 4) * self.player.experience_current / self.player.experience_max , 25 - 8)
        pygame.draw.rect(self.screen, "yellow", exp_rect, 0, 20)
        pygame.draw.rect(self.screen, "black", exp_rect_border, 4, 20)
    
    def drawBackground(self):
        # fill the self.screen with a color to wipe away anything from last frame
        self.screen.fill("#124a21")
        # Fill the smaller background surface within the self.screen boundaries
        background_rect = pygame.Rect(
            self.background.x - self.settings.screen_width,
            self.background.y - self.settings.screen_height,
            self.settings.game_size**2 * 2,
            self.settings.game_size**2 * 2
            )
        # Fill the smaller background surface
        pygame.draw.rect(self.screen, "#39ad58", background_rect)
        # Draw background lines
        for i in range(self.settings.game_size+1):
            if i == 0 or i == self.settings.game_size:
                w = 10
            else:
                w = 1
            pygame.draw.line(
                self.screen, 
                "black", 
                (self.background.x - self.settings.screen_width + i * self.settings.game_size * 2, self.background.y - self.settings.screen_height), 
                (self.background.x - self.settings.screen_width + i * self.settings.game_size * 2, self.background.y - self.settings.screen_height + self.settings.game_size**2 * 2),
                w)    # Vertical lines
            
            pygame.draw.line(
                self.screen, 
                "black", 
                (self.background.x - self.settings.screen_width, self.background.y - self.settings.screen_height + i * self.settings.game_size * 2), 
                (self.background.x - self.settings.screen_width + self.settings.game_size**2 * 2, self.background.y - self.settings.screen_height + i * self.settings.game_size * 2), 
                w)    # Horizontal lines

    def notTouchingBorder(self):
        li = []
        if (self.background.x - self.settings.screen_width + self.settings.game_size**2*2 - self.player.radius + 300 * self.dt)  <= self.player.position.x:
            li.append(False)
            li.append("right")
        if (self.background.x - self.settings.screen_width + self.player.radius + 300 * self.dt)  >= self.player.position.x:
            li.append(False)
            li.append("left")
        if (self.background.y - self.settings.screen_height + self.player.radius + 300 * self.dt)  >= self.player.position.y:
            li.append(False)
            li.append("up")
        if (self.background.y - self.settings.screen_height + self.settings.game_size**2*2 - self.player.radius + 300 * self.dt)  <= self.player.position.y:
            li.append(False)
            li.append("down")
        if len(li) == 0:
            li = [True, "nothing"]
        return list(set(li))
    
    def checkKeysPressed(self):
        keys = pygame.key.get_pressed()
        gate = self.notTouchingBorder()   #TODO: CHECK WHAT HAPPENS WHEN >2 BUTTONS ARE PRESSED
        if keys[pygame.K_w] and keys[pygame.K_a] and "up" not in gate and "left" not in gate:
            self.background.y += self.settings.speed * self.dt / 2**(1/2)
            self.background.x += self.settings.speed * self.dt / 2**(1/2)

        elif keys[pygame.K_w] and keys[pygame.K_d] and "up" not in gate and "right" not in gate:
            self.background.y += self.settings.speed * self.dt / 2**(1/2)
            self.background.x -= self.settings.speed * self.dt / 2**(1/2)

        elif keys[pygame.K_w] and "up" not in gate:
            self.background.y += self.settings.speed * self.dt

        elif keys[pygame.K_s] and keys[pygame.K_a] and "down" not in gate and "left" not in gate:
            self.background.y -= self.settings.speed * self.dt / 2**(1/2)
            self.background.x += self.settings.speed * self.dt / 2**(1/2)

        elif keys[pygame.K_s] and keys[pygame.K_d] and "down" not in gate and "right" not in gate:
            self.background.y -= self.settings.speed * self.dt / 2**(1/2)
            self.background.x -= self.settings.speed * self.dt / 2**(1/2)

        elif keys[pygame.K_s] and "down" not in gate:
            self.background.y -= self.settings.speed * self.dt

        elif keys[pygame.K_a] and "left" not in gate:
            self.background.x += self.settings.speed * self.dt

        elif keys[pygame.K_d] and "right" not in gate:
            self.background.x -= self.settings.speed * self.dt
        
        if keys[pygame.K_ESCAPE]:
            if not self.onpause:
                m1 = Menu()
                self.openMenu(m1)

    def checkHitboxes(self):
        self.writeOnScreen(str(self.player.position.x)+" "+str(self.player.position.y), self.player.position.x, self.player.position.y)
        for kit in self.WeaponKitGroup:
            if pygame.sprite.collide_rect(kit, self.player):   # This is the best feature ever, although, my player is a circle and the boxes are squares...
                kit.kill()
                response = self.openSelectWeaponMenu()
        
        for magnet in self.MagnetGroup:
            if pygame.sprite.collide_rect(magnet, self.player):   # This is the best feature ever, although, my player is a circle and the boxes are squares...
                magnet.kill()
                for exp in self.experienceGroup:
                    exp.setMinDistance(10000)
        
        for enemy in self.EnemyGroup:
            for bullet in self.bulletGroup:
                if pygame.sprite.collide_rect(bullet, enemy):
                    if enemy not in bullet.enemiesHit:
                        bullet.enemiesHit.append(enemy)
                        enemy.health -= bullet.damage
                        enemy.hitCooldown = 0.5
                        if enemy.health <= 0:
                            self.spawnExperienceOrb(enemy)
                            enemy.kill()
                            if bullet.weaponname == "Attack Drone":
                                bullet.kill()

            if pygame.sprite.collide_circle(self.player, enemy):
                if self.player.hitCooldown <= 0:
                    self.player.hitCooldown = 1
                    self.player.health_current -= enemy.damage
                    if self.player.health_current <= 0:
                        self.openDeathMenu()
        
        for exp in self.experienceGroup:
            if pygame.sprite.collide_circle(exp, self.player):
                self.player.experience_queue += int(exp.value)
                exp.kill()

    def spawnWeaponKit(self):
        if len([weapon for weapon in self.weaponlist if weapon.level < 5]) > 0:
            if self.WeaponKitCooldown <= 0:
                chance = random.random()
                if chance > 0.65:
                    randpos = pygame.Vector2(
                        random.randint(round(self.background.x - self.settings.screen_width), round(self.background.x - self.settings.screen_width + self.settings.game_size**2 * 2)), 
                        random.randint(round(self.background.y - self.settings.screen_height), round(self.background.y - self.settings.screen_height + self.settings.game_size**2 * 2))
                        )
                    kit = WeaponKit(randpos, 50, 50)
                    self.WeaponKitGroup.add(kit)
                    self.WeaponKitCooldown = 30  - (self.time // 30)    #90 sec        #TODO MAKE IT A SETTING/MODIFIER
                    if self.WeaponKitCooldown < 15:
                            self.WeaponKitCooldown = 15
                else:
                    self.WeaponKitCooldown = 5
            else:
                self.WeaponKitCooldown -= self.dt
    
    def spawnMagnet(self):
        if self.MagnetCooldown <= 0:
            chance = random.random()
            if chance > 0.08:
                randpos = pygame.Vector2(
                    random.randint(round(self.background.x - self.settings.screen_width), round(self.background.x - self.settings.screen_width + self.settings.game_size**2 * 2)), 
                    random.randint(round(self.background.y - self.settings.screen_height), round(self.background.y - self.settings.screen_height + self.settings.game_size**2 * 2))
                    )
                magnet = Magnet(randpos, 50, 50)
                self.MagnetGroup.add(magnet)
                self.MagnetCooldown = 120  - (self.time // 30)  #TODO MAKE IT A SETTING/MODIFIER
                if self.MagnetCooldown < 60:
                    self.MagnetCooldown = 60
            else:
                self.MagnetCooldown = 5
        else:
            self.MagnetCooldown -= self.dt
    
    def spawnEnemies(self):
        if self.EnemyCooldown <= 0:
            for i in range(10 + int((self.time // 60) * 10)):
                chance = random.random()
                if chance > 0.3 - (self.time // 60) * 0.02:
                    randpos = pygame.Vector2(
                        random.randint(round(self.background.x - self.settings.screen_width), round(self.background.x - self.settings.screen_width + self.settings.game_size**2 * 2)), 
                        random.randint(round(self.background.y - self.settings.screen_height), round(self.background.y - self.settings.screen_height + self.settings.game_size**2 * 2))
                        )
                    enemy = Enemy(randpos, (self.time // 30) + 1)
                    self.EnemyGroup.add(enemy)
                    self.EnemyCooldown = 10 - (self.time // 60)          #TODO MAKE IT A SETTING/MODIFIER
                    if self.EnemyCooldown < 5:
                        self.EnemyCooldow = 5
        else:
            self.EnemyCooldown -= self.dt
    
    def spawnExperienceOrb(self, enemy: Enemy):
        chance = random.random()
        if chance < 0.25 and enemy.type == "miniboss":
            e = Experience(enemy.position, 20, "purple", enemy.level * 5000)
        elif (chance < 1/3 and enemy.type == "brute") or ( chance < 0.9 and enemy.type == "miniboss"):
            e = Experience(enemy.position, 16, "orange", enemy.level * 1000)
        elif chance < 0.2 or enemy.type == "brute" or enemy.type == "miniboss":
            e = Experience(enemy.position, 12, "yellow", enemy.level * 100)
        else:
            e = Experience(enemy.position, 8, "white", enemy.level * 10)
        self.experienceGroup.add(e)
    
    def updateWeaponKitPosition(self):
        for kit in self.WeaponKitGroup:
            kit.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder())
            rect = pygame.Rect(kit.position.x, kit.position.y, kit.width, kit.height)
            pygame.draw.rect(self.screen, "gray", rect)
            pygame.draw.rect(self.screen, "black", rect, 3)
            #self.writeOnScreen(self.screen, str(kit.position.x)+" "+str(kit.position.y), kit.position.x, kit.position.y)
    
    def updateMagnetPosition(self):
        for magnet in self.MagnetGroup:
            magnet.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder())
            rect = pygame.Rect(magnet.position.x, magnet.position.y, magnet.width, magnet.height)
            pygame.draw.arc(self.screen, "black", rect, math.radians(0), math.radians(180), 23)
            pygame.draw.arc(self.screen, "red", rect, math.radians(90), math.radians(180), 20)
            pygame.draw.arc(self.screen, "blue", rect, math.radians(0), math.radians(90), 20)
            pygame.draw.arc(self.screen, "black", rect, math.radians(0), math.radians(180), 3)

            pygame.draw.line(self.screen, "black", (magnet.position.x + 23/2, magnet.position.y + magnet.height / 2), (magnet.position.x + 23/2, magnet.position.y + magnet.height), 20)
            pygame.draw.line(self.screen, "red", (magnet.position.x + 19/2, magnet.position.y + magnet.height / 2), (magnet.position.x + 19/2, magnet.position.y + magnet.height), 19)
            pygame.draw.line(self.screen, "gray50", (magnet.position.x + 19/2, magnet.position.y + magnet.height * 3 / 4), (magnet.position.x + 19/2, magnet.position.y + magnet.height), 19)
            pygame.draw.line(self.screen, "black", (magnet.position.x + 1, magnet.position.y + magnet.height / 2), (magnet.position.x + 1, magnet.position.y + magnet.height), 3)

            pygame.draw.line(self.screen, "black", (magnet.position.x + magnet.width - 31/2, magnet.position.y + magnet.height / 2), (magnet.position.x + magnet.width - 31/2, magnet.position.y + magnet.height), 18)
            pygame.draw.line(self.screen, "blue", (magnet.position.x + magnet.width - 27/2, magnet.position.y + magnet.height / 2), (magnet.position.x + magnet.width - 27/2, magnet.position.y + magnet.height), 18)
            pygame.draw.line(self.screen, "gray50", (magnet.position.x + magnet.width - 27/2, magnet.position.y + magnet.height * 3 / 4), (magnet.position.x + magnet.width - 27/2, magnet.position.y + magnet.height), 18)
            pygame.draw.line(self.screen, "black", (magnet.position.x + magnet.width - 6/2, magnet.position.y + magnet.height / 2), (magnet.position.x + magnet.width - 6/2, magnet.position.y + magnet.height), 4)

            pygame.draw.line(self.screen, "black", (magnet.position.x, magnet.position.y + magnet.height), (magnet.position.x + 20, magnet.position.y + magnet.height), 2)
            pygame.draw.line(self.screen, "black", (magnet.position.x + magnet.width - 22, magnet.position.y + magnet.height), (magnet.position.x + magnet.width - 1, magnet.position.y + magnet.height), 2)
    
    def updateEnemyPosition(self):
        for enemy in self.EnemyGroup:

            enemy.position_original.x = enemy.position.x
            enemy.position_original.y = enemy.position.y
            enemy.position_destination.x = self.player.position.x
            enemy.position_destination.y = self.player.position.y
        
            distance = math.sqrt((enemy.position_destination.x - enemy.position_original.x)**2 + (enemy.position_destination.y - enemy.position_original.y)**2) + 1
            sinus = abs((enemy.position_destination.y - enemy.position_original.y)/distance) * self.compare_subtraction(enemy.position_destination.y, enemy.position_original.y)
            cosinus = abs((enemy.position_destination.x - enemy.position_original.x)/distance) * self.compare_subtraction(enemy.position_destination.x, enemy.position_original.x)


            enemy.position.x += cosinus * enemy.speed * 0.1
            enemy.position.y += sinus * enemy.speed * 0.1

            enemy.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder())
            if enemy.hitCooldown > 0:
                enemy.colour = "darkred"
                enemy.hitCooldown -= self.dt
            else:
                enemy.colour = "red"
            pygame.draw.circle(self.screen, enemy.colour, enemy.position, enemy.radius)
            pygame.draw.circle(self.screen, "black", enemy.position, enemy.radius, 3)
            #self.writeOnScreen(self.screen, str(enemy.position.x)+" "+str(enemy.position.y), enemy.position.x, enemy.position.y)
    
    def updateExperiencePosition(self):
        for exp in self.experienceGroup:
            exp.position_original.x = exp.position.x
            exp.position_original.y = exp.position.y
            exp.position_destination.x = self.player.position.x
            exp.position_destination.y = self.player.position.y
        
            distance = math.sqrt((exp.position_destination.x - exp.position_original.x)**2 + (exp.position_destination.y - exp.position_original.y)**2) + 1

            tempX = exp.position.x
            tempY = exp.position.y
            exp.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder())

            if distance < exp.min_distance:
                if tempX != exp.position.x or tempY != exp.position.y:
                    exp.position.x += (exp.position_destination.x - exp.position.x) * 0.225
                    exp.position.y += (exp.position_destination.y - exp.position.y) * 0.225
                else:
                    exp.position.x += (exp.position_destination.x - exp.position.x) * 0.075
                    exp.position.y += (exp.position_destination.y - exp.position.y) * 0.075

            

            pygame.draw.circle(self.screen, exp.colour, exp.position, exp.radius)
            pygame.draw.circle(self.screen, "black", exp.position, exp.radius, 2)
    
    def getClosestEnemy(self, weapon: Weapon, n: int = 1):
        if n > 0:
            closestEnemies = [[enemy, math.sqrt((enemy.position.x - weapon.position.x)**2 + (enemy.position.y - weapon.position.y)**2)] for enemy in self.EnemyGroup if math.sqrt((enemy.position.x - weapon.position.x)**2 + (enemy.position.y - weapon.position.y)**2) <= weapon.range]
            closestEnemies.sort(key = lambda enemy: enemy[1])
            closestEnemies = [enemy[0] for enemy in closestEnemies]
            if len(closestEnemies) >= n:
                return closestEnemies[:n]
            else:
                return closestEnemies
        else:
            return None

    def attackCycle(self, mouse_pos: pygame.Vector2):
        for weapon in self.player_weapons:
            if "pet" in weapon.pattern:
                if weapon.position_destination.x == 0 and weapon.position_destination.y == 0:
                    weapon.position_destination.x = self.player.position.x + 100
                    weapon.position_destination.y = self.player.position.y - 100

                weapon.position_original.x = weapon.position.x
                weapon.position_original.y = weapon.position.y
                weapon.position_destination.x = self.player.position.x + 200 * math.cos(weapon.rotation * math.pi / 180)
                weapon.position_destination.y = self.player.position.y - 200 * math.sin(weapon.rotation * math.pi / 180)

                weapon.position.x += (weapon.position_destination.x - weapon.position.x) * 0.035
                weapon.position.y += (weapon.position_destination.y - weapon.position.y) * 0.035

                weapon.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder(), 0.55)

            
            
            if weapon.cooldown_current <= 0:
                if "circle" in weapon.pattern:
                    if len(weapon.bullets) < (weapon.level + 1):
                        weapon.bullets.empty()
                        weapon.rotation = -360 / (weapon.level + 1)
                        for ball in range(weapon.level + 1):
                            weapon.rotation += 360 / (weapon.level + 1)

                            bullet_pos = pygame.Vector2(weapon.position.x, weapon.position.y)
                            bullet_pos_original = pygame.Vector2(weapon.position_original.x, weapon.position_original.y)
                            bullet_pos_destination = pygame.Vector2(weapon.position_destination.x, weapon.position_destination.y)
                            b = Bullet(weapon.name, bullet_pos, bullet_pos_original, bullet_pos_destination, weapon.bulletLifeTime,weapon.damage, False, "bullet", weapon.size)
                            b.addRotation(weapon.rotation)
                            weapon.bullets.add(b)
                            self.bulletGroup.add(b)
                else:
                    bullet_pos = pygame.Vector2(weapon.position.x, weapon.position.y)
                    bullet_pos_original = pygame.Vector2(weapon.position_original.x, weapon.position_original.y)

                    if "pet" in weapon.pattern:
                        closestEnemies: List[Union[Enemy, None]] = self.getClosestEnemy(weapon, weapon.level)
                        b = []
                        if closestEnemies:
                            for enemy in closestEnemies:
                                bullet_pos_destination = pygame.Vector2(enemy.position.x, enemy.position.y)
                                b.append(Bullet(weapon.name, bullet_pos, bullet_pos_original, bullet_pos_destination, weapon.bulletLifeTime, weapon.damage, False, "bullet", weapon.size))
                    else:
                        bullet_pos_destination = pygame.Vector2(weapon.position_destination.x, weapon.position_destination.y)
                        b = Bullet(weapon.name, bullet_pos, bullet_pos_original, bullet_pos_destination, weapon.bulletLifeTime, weapon.damage, False, "bullet", weapon.size)
                    weapon.setOnCooldown()
                    if "angled" in weapon.pattern:
                        b.addAnimationRotation(0)
                        b.addRotation(weapon.rotation)
                    if ("multiple" in weapon.pattern or "constant" in weapon.pattern) and random.random() > 0.975 - weapon.level * 0.065:
                        weapon.cooldown_current = 0.02
                    weapon.bullets.add(b)
                    self.bulletGroup.add(b)
            else:
                weapon.updateCooldown(self.dt)
            
            for bullet in weapon.bullets:
                if "pet" in weapon.pattern:
                    bullet.position.x = bullet.position_destination.x
                    bullet.position.y = bullet.position_destination.y

                    tempX = bullet.position.x
                    tempY = bullet.position.y
                    bullet.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder())

                    bullet.position_destination.x += bullet.position.x - tempX
                    bullet.position_destination.y += bullet.position.y - tempY

                    if weapon.level < 4:
                        pygame.draw.line(self.screen, "red", bullet.position_original, bullet.position, 2+weapon.level*2)
                    elif weapon.level == 4:
                        pygame.draw.line(self.screen, "red", bullet.position_original, bullet.position, 10)
                    else:
                        pygame.draw.line(self.screen, "darkred", bullet.position_original, bullet.position, 12)
                        pygame.draw.line(self.screen, "red", bullet.position_original, bullet.position, 3)

                    if isinstance(bullet.lifeTime, float):
                        if bullet.lifeTime <= 0:
                            bullet.remove(weapon.bullets)
                            bullet.kill()
                        else:
                            bullet.lifeTime -= self.dt

                if "straight" in weapon.pattern:
                    if bullet.position_destination.x == 0 and bullet.position_destination.y == 0:
                        bullet.position_destination.x = mouse_pos.x
                        bullet.position_destination.y = mouse_pos.y

                        if "constant" in weapon.pattern:
                            sign = self.getSign()
                            bullet.position_destination.x += (random.random() * sign * (85 + 15 * weapon.level))
                            bullet.position_destination.y += (random.random() * sign * (85 + 15 * weapon.level))
                        
                        if "multiple" in weapon.pattern:
                            bullet.position_destination.x += (random.randint(-1,1) * 25)
                            bullet.position_destination.y += (random.randint(-1,1) * 25)

                    distance = math.sqrt((bullet.position_destination.x - bullet.position_original.x)**2 + (bullet.position_destination.y - bullet.position_original.y)**2) + 1
                    sinus = abs((bullet.position_destination.y - bullet.position_original.y)/distance) * self.compare_subtraction(bullet.position_destination.y, bullet.position_original.y)
                    cosinus = abs((bullet.position_destination.x - bullet.position_original.x)/distance) * self.compare_subtraction(bullet.position_destination.x, bullet.position_original.x)

                    bullet.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder())

                    bullet.position.x += cosinus * weapon.speed
                    bullet.position.y += sinus * weapon.speed
                    
                    if weapon.name == "High-tech Rifle":
                        pygame.draw.line(self.screen, weapon.colour, (bullet.position.x - cosinus * weapon.size, bullet.position.y - sinus * weapon.size), (bullet.position.x, bullet.position.y), 15)
                        if weapon.level >= 3:
                            pygame.draw.line(self.screen, "yellow", (bullet.position.x - cosinus * weapon.size/1.2, bullet.position.y - sinus * weapon.size/1.2), (bullet.position.x, bullet.position.y), 15)
                        if weapon.level == 5:
                            pygame.draw.line(self.screen, "orange", (bullet.position.x - cosinus * weapon.size/5, bullet.position.y - sinus * weapon.size/5), (bullet.position.x, bullet.position.y), 15)
                    
                    if weapon.name == "Flamethrower":
                        width = weapon.image_projectile.get_width()
                        height = weapon.image_projectile.get_height()
                        image = pygame.transform.scale(weapon.image_projectile, (int(width * (0.25+weapon.level*0.07)), int(height * (0.55+weapon.level*0.07))))
                        image = pygame.transform.rotate(image, 180+math.acos(sinus)*self.compare_subtraction(bullet.position_destination.x, bullet.position_original.x)*180/math.pi)
                        image_x = bullet.position.x - cosinus * weapon.size
                        image_y = bullet.position.y - sinus * weapon.size
                        if self.compare_subtraction(bullet.position_destination.x, bullet.position_original.x) == -1:   #LEFT SIDE
                            if bullet.position_destination.x - bullet.position_original.x < -180:
                                image_x -= image.get_width() * 1.08
                            else:
                                image_x -= image.get_width() * 0.54
                        elif bullet.position_destination.x - bullet.position_original.x < 180:
                            image_x -= image.get_width() * 0.54

                        if self.compare_subtraction(bullet.position_destination.y, bullet.position_original.y) == -1:   #UPEER SIDE
                            if bullet.position_destination.y - bullet.position_original.y < -180:
                                image_y -= image.get_height() * 0.9
                            else: 
                                image_y -= image.get_height() * 0.4
                        elif bullet.position_destination.y - bullet.position_original.y < 180:
                            image_y -= image.get_height() * 0.4

                        rect = image.get_rect()
                        rect.topleft = (image_x, image_y)
                        self.screen.blit(image, (rect.x, rect.y))
                        #pygame.draw.line(self.screen, weapon.colour, (bullet.position.x - cosinus * weapon.size, bullet.position.y - sinus * weapon.size), (bullet.position.x, bullet.position.y), 15 + round(weapon.size * 0.02 * weapon.level * 5))
                        #if weapon.level >= 3:
                        #    pygame.draw.line(self.screen, "orange2", (bullet.position.x - cosinus * weapon.size/1.2, bullet.position.y - sinus * weapon.size/1.2), (bullet.position.x, bullet.position.y), 15 + round(weapon.size * 0.02 * weapon.level * 5))
                        #if weapon.level == 5:
                        #    pygame.draw.line(self.screen, "orange3", (bullet.position.x - cosinus * weapon.size/5, bullet.position.y - sinus * weapon.size/5), (bullet.position.x, bullet.position.y), 15 + round(weapon.size * 0.02 * weapon.level * 5))
                    
                    if weapon.name == "Pistols":
                        pygame.draw.line(self.screen, weapon.colour, (bullet.position.x - cosinus * weapon.size, bullet.position.y - sinus * weapon.size), (bullet.position.x, bullet.position.y), 15)
                        if weapon.level >= 3:
                            pygame.draw.line(self.screen, "grey", (bullet.position.x - cosinus * weapon.size/1.2, bullet.position.y - sinus * weapon.size/1.2), (bullet.position.x, bullet.position.y), 15)
                        if weapon.level == 5:
                            pygame.draw.line(self.screen, "blue", (bullet.position.x - cosinus * weapon.size/5, bullet.position.y - sinus * weapon.size/5), (bullet.position.x, bullet.position.y), 15)
                    
                    if isinstance(bullet.lifeTime, float):
                        if bullet.lifeTime <= 0:
                            bullet.remove(weapon.bullets)
                            bullet.kill()
                        else:
                            bullet.lifeTime -= self.dt

                if "circle" in weapon.pattern:
                    if bullet.rotation == 360:
                        bullet.rotation = 0

                    bullet.position.x = self.player.position.x + weapon.distance * math.cos(bullet.rotation * math.pi / 180)
                    bullet.position.y = self.player.position.y + weapon.distance * math.sin(bullet.rotation * math.pi / 180)
                    bullet.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder())

                    pygame.draw.circle(self.screen, weapon.colour, (bullet.position.x, bullet.position.y), weapon.size)

                    if weapon.level >= 3:
                        pygame.draw.circle(self.screen, "pink", (bullet.position.x, bullet.position.y), weapon.size/2)
                    if weapon.level == 5:
                        pygame.draw.circle(self.screen, "white", (bullet.position.x, bullet.position.y), weapon.size/4)

                    bullet.rotation += weapon.speed * 0.05
                
                if "angled" in weapon.pattern:
                    if bullet.position_destination.x == 0 and bullet.position_destination.y == 0:
                        bullet.position_destination.x = mouse_pos.x
                        bullet.position_destination.y = mouse_pos.y

                    center = pygame.Vector2(
                        (bullet.position_destination.x - bullet.position_original.x) / 2 + bullet.position_original.x, 
                        (bullet.position_destination.y - bullet.position_original.y) / 2 + bullet.position_original.y, 
                        )

                    bullet.position.x = center.x + (bullet.position_original.x - bullet.position_destination.x) * math.cos(bullet.rotation * math.pi / 180) * 0.8
                    bullet.position.y = center.y + (bullet.position_original.y - bullet.position_destination.y) * math.sin(bullet.rotation * math.pi / 180) * 0.8

                    bullet.setPositionBasedOnMovement(self.settings.speed, self.dt, self.notTouchingBorder())

                    if pygame.sprite.collide_circle(bullet, self.player) or bullet.rotation > 40:
                        rect = pygame.Rect(bullet.position.x, bullet.position.y, weapon.size*3, weapon.size*3)
                        pygame.draw.arc(self.screen, weapon.colour, rect, math.radians(0 + bullet.animation_rotation), math.radians(120 + weapon.level * 25 + bullet.animation_rotation), 7 + weapon.level)
                        
                        if weapon.level >= 3:
                            pygame.draw.arc(self.screen, "blue", rect, math.radians(0 + bullet.animation_rotation), math.radians(140 + weapon.level * 20 + bullet.animation_rotation), 2 + weapon.level)

                        if weapon.level == 5:
                            pygame.draw.arc(self.screen, "indianred3", rect, math.radians(0 + bullet.animation_rotation), math.radians(140 + weapon.level * 20 + bullet.animation_rotation), 2)

                    bullet.rotation += weapon.speed * 0.1 * (1 + abs(math.sin(bullet.rotation * math.pi / 180)))
                    bullet.animation_rotation += weapon.speed * 0.3 * (1 + abs(math.sin(bullet.rotation * math.pi / 180)))

                    if (pygame.sprite.collide_circle(bullet, self.player) and bullet.rotation >= 180 ) or bullet.rotation >= 410:
                        bullet.remove(weapon.bullets)
                        bullet.kill()
            if "pet" in weapon.pattern:
                pygame.draw.circle(self.screen, weapon.colour, (weapon.position.x, weapon.position.y), weapon.size)
                if weapon.level >= 3: 
                    pygame.draw.circle(self.screen, "black", (weapon.position.x, weapon.position.y), weapon.size, 3)
                
                modifierCos = weapon.size * math.cos((weapon.rotation + 30) * math.pi / 180)
                modifierSin = weapon.size * math.sin((weapon.rotation + 30) * math.pi / 180)

                pygame.draw.circle(self.screen, "grey", (weapon.position.x - modifierSin, weapon.position.y - modifierCos), weapon.size/2)
                pygame.draw.circle(self.screen, "grey", (weapon.position.x - modifierCos, weapon.position.y + modifierSin), weapon.size/2)
                pygame.draw.circle(self.screen, "grey", (weapon.position.x + modifierCos, weapon.position.y - modifierSin), weapon.size/2)
                pygame.draw.circle(self.screen, "grey", (weapon.position.x + modifierSin, weapon.position.y + modifierCos), weapon.size/2)
                if weapon.level == 5: 
                    pygame.draw.circle(self.screen, "black", (weapon.position.x - modifierSin, weapon.position.y - modifierCos), weapon.size/2, 3)
                    pygame.draw.circle(self.screen, "black", (weapon.position.x - modifierCos, weapon.position.y + modifierSin), weapon.size/2, 3)
                    pygame.draw.circle(self.screen, "black", (weapon.position.x + modifierCos, weapon.position.y - modifierSin), weapon.size/2, 3)
                    pygame.draw.circle(self.screen, "black", (weapon.position.x + modifierSin, weapon.position.y + modifierCos), weapon.size/2, 3)

                weapon.rotation += weapon.speed * 0.01
    
    def writeOnScreen(self, txt, posX = 0, posY = 0):
        font = pygame.font.Font(None, 30)
        # Kinda consol log -> Write stuff on the canvas
        text = font.render(txt, True, "black")
        self.screen.blit(text, (posX, posY))
        
    def compare_subtraction(self, a, b):
        result = a - b
        return 1 if result > 0 else -1

    def getSign(self):
        if random.random() >= 0.5:
            return -1
        return 1
        


p1 = User("admin","12345")
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