import pygame
import math
import time
import random
import screeninfo
from typing import List, Dict
from player import User
from gamesettings import GameSettings
from gameobject import GameObject, PlayerCharacter, Weapon, Bullet, Enemy, Experience, WeaponKit, HUD, Inventory, Menu

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
        self.player_radius = 40 # With this only the map will be affected by game size                     #self.settings.game_size    # Bit unnecesary
        self.player_pos: pygame.Vector2 = pygame.Vector2(self.settings.screen_width / 2, self.settings.screen_height / 2)
        self.playerCharacter = PlayerCharacter(self.player_radius, self.player_pos)

        self.background: pygame.Vector2  = pygame.Vector2(self.player_pos.x, self.player_pos.y)

        rifle = Weapon("High-tech Rifle", 1.5, "normal", "single straight", "white", 30, 25, 2.1, self.player_pos.x, self.player_pos.y)
        #energy_ball = Weapon("Energy Ball", 0.1, "energy", "constant circle", "purple", 15, 40, "inf", 0, 0)
        #boomerang = Weapon("Boomerang", 2.5, "normal", "single angled", "gray", 20, 15, "inf", self.player_pos.x, self.player_pos.y)
        flamethrower = Weapon("Flamethrower", 0.1, "fire", "constant straight", "orange", 45, 10, 0.3, self.player_pos.x, self.player_pos.y)
        #damage_field = Weapon("Damaging Field", 3, "fire", "single aoe", "red", 15, 40, 4, self.player_pos.x, self.player_pos.y)                   #TODO
        #drone = Weapon("Attack Drone", 0.1, "normal", "single pet", "white", 15, 40, "inf", self.player_pos.x, self.player_pos.y)                   #TODO                          #TODO
        #explosion = Weapon("Remote Explosion", 2.5, "energy", "single remote", "yellow", 15, 40, "inf", self.player_pos.x, self.player_pos.y)      #TODO
        pistols = Weapon("Pistols", 0.2, "normal", "multiple straight", "skyblue", 20, 20, 0.35, self.player_pos.x, self.player_pos.y)             #TODO

        self.weaponlist = [rifle, flamethrower, pistols]#rifle, energy_ball, boomerang, flamethrower, damage_field, drone, explosion, pistols]
        self.bulletBox: pygame.sprite.Group = pygame.sprite.Group()

        self.player_weapons: List[Weapon] = [rifle]
        self.WeaponKitGroup: pygame.sprite.Group[WeaponKit] = pygame.sprite.Group()
        self.WeaponKitCooldown = 0

        self.onpause = False
    
    def openMenu(self, menu: Menu, screen):
        self.onpause = True
        #self.openedHUD = menu
        menu.state = "ingame"
        response = menu.openInGameMenu(screen, self.settings.screen_width, self.settings.screen_height, self.onpause)
        if response == "closed":
            #self.openedHUD.run = False
            #wself.openedHUD = None
            self.onpause = False

    def gameRun(self, user: User):
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
            if self.onpause != True:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) # Get mouse pos

                self.drawBackground(screen) # Draw background and border of the map

                self.attackCycle(screen, mouse_pos, dt)    # Drawing the weapon attacks

                pygame.draw.circle(screen, "red", (self.player_pos.x, self.player_pos.y), self.player_radius) # Draw player

                self.checkHitboxes(screen)
                #self.spawnEnemies(screen)

                self.spawnWeaponKit(screen, dt)

                self.writeOnScreen(screen, str(self.background.x)+" "+str(self.background.y))  # Write some stuff on the screen

                self.checkKeysPressed(dt, screen) # Update background position based on player movement

                pygame.display.flip() # flip() the display to put your work on screen

                dt = clock.tick(self.settings.fps) / 1000 # dt is delta time in seconds since last frame
            
            else:
                self.checkKeysPressed(dt, screen)

        pygame.quit()

    def notTouchingBorder(self, dt):
        li = []
        if (self.background.x - self.settings.screen_width + self.settings.game_size**2*2 - self.player_radius + 300 * dt)  <= self.player_pos.x:
            li.append(False)
            li.append("right")
        if (self.background.x - self.settings.screen_width + self.player_radius + 300 * dt)  >= self.player_pos.x:
            li.append(False)
            li.append("left")
        if (self.background.y - self.settings.screen_height + self.player_radius + 300 * dt)  >= self.player_pos.y:
            li.append(False)
            li.append("up")
        if (self.background.y - self.settings.screen_height + self.settings.game_size**2*2 - self.player_radius + 300 * dt)  <= self.player_pos.y:
            li.append(False)
            li.append("down")
        if len(li) == 0:
            li = [True, "nothing"]
        return list(set(li))
    
    def checkKeysPressed(self, dt, screen):
        keys = pygame.key.get_pressed()
        gate = self.notTouchingBorder(dt)   #TODO: CHECK WHAT HAPPENS WHEN >2 BUTTONS ARE PRESSED
        if keys[pygame.K_w] and keys[pygame.K_a] and "up" not in gate and "left" not in gate:
            self.background.y += self.settings.speed * dt / 2**(1/2)
            self.background.x += self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and keys[pygame.K_d] and "up" not in gate and "right" not in gate:
            self.background.y += self.settings.speed * dt / 2**(1/2)
            self.background.x -= self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_w] and "up" not in gate:
            self.background.y += self.settings.speed * dt

        elif keys[pygame.K_s] and keys[pygame.K_a] and "down" not in gate and "left" not in gate:
            self.background.y -= self.settings.speed * dt / 2**(1/2)
            self.background.x += self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and keys[pygame.K_d] and "down" not in gate and "right" not in gate:
            self.background.y -= self.settings.speed * dt / 2**(1/2)
            self.background.x -= self.settings.speed * dt / 2**(1/2)

        elif keys[pygame.K_s] and "down" not in gate:
            self.background.y -= self.settings.speed * dt

        elif keys[pygame.K_a] and "left" not in gate:
            self.background.x += self.settings.speed * dt

        elif keys[pygame.K_d] and "right" not in gate:
            self.background.x -= self.settings.speed * dt
        
        if keys[pygame.K_ESCAPE]:
            if not self.onpause:
                m1 = Menu()
                self.openMenu(m1, screen)

    def checkHitboxes(self, screen):
        self.writeOnScreen(screen, str(self.player_pos.x)+" "+str(self.player_pos.y), self.player_pos.x, self.player_pos.y)
        for kit in self.WeaponKitGroup:
            if pygame.sprite.collide_rect(kit, self.playerCharacter):   # This is the best feature ever, although, my player is a circle and the boxes are squares...
                kit.kill()
                response = self.selectWeapon(screen)
    
    def getRandomWeapons(self):
        upgradeableWeapons = [weapon for weapon in self.weaponlist if weapon.level < 5]
        if len(upgradeableWeapons) >= 3:
            return random.sample(upgradeableWeapons, 3)
        return upgradeableWeapons
    
    def selectWeapon(self, screen):
        #time.sleep(1)
        self.onpause = True
        weaponlist = self.getRandomWeapons()
        if len(weaponlist) > 0:
            menu = Menu()
            menu.state = "weapon_selector"
            response = menu.openWeaponSelectorMenu(screen, self.settings.screen_width, self.settings.screen_height, self.onpause, weaponlist)
            if isinstance(response[1], Weapon):
                if response[1] not in self.player_weapons:
                    self.player_weapons.append(response[1])
            if response[0] == "closed":
                self.onpause = False
        else:
            self.onpause = False

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

    def spawnWeaponKit(self, screen, dt):
        for kit in self.WeaponKitGroup:
            kit.setPositionBasedOnMovement(self.settings.speed, dt, self.notTouchingBorder(dt))
            rect = pygame.Rect(kit.position.x, kit.position.y, kit.width, kit.height)
            pygame.draw.rect(screen, "gray", rect)
            pygame.draw.rect(screen, "black", rect, 3)
            self.writeOnScreen(screen, str(kit.position.x)+" "+str(kit.position.y), kit.position.x, kit.position.y)
        if self.WeaponKitCooldown == 0:
            chance = random.random()
            if chance > 0.8:
                randpos = pygame.Vector2(
                    random.randint(round(self.background.x - self.settings.screen_width), round(self.background.x - self.settings.screen_width + self.settings.game_size**2 * 2)), 
                    random.randint(round(self.background.y - self.settings.screen_height), round(self.background.y - self.settings.screen_height + self.settings.game_size**2 * 2))
                    )
                kit = WeaponKit(randpos, 50, 50)
                self.WeaponKitGroup.add(kit)
                rect = pygame.Rect(randpos.x, randpos.y, kit.width, kit.height)
                pygame.draw.rect(screen, "gray", rect)
                pygame.draw.rect(screen, "black", rect, 3)
                self.WeaponKitCooldown = 100#00 #TODO MAKE IT A SETTING/MODIFIER
        else:
            self.WeaponKitCooldown -= 1
    
    
    def writeOnScreen(self, screen, txt, posX = 0, posY = 0):
        font = pygame.font.Font(None, 30)
        # Kinda consol log -> Write stuff on the canvas
        player_pos_text = font.render(txt, True, "black")
        screen.blit(player_pos_text, (posX, posY))
    
    def attackCycle(self, screen: pygame.Surface, mouse_pos: pygame.Vector2, dt):
        for weapon in self.player_weapons:
            # if "pet" in weapon.pattern:
            #     if weapon.position_destination.x == 0 and weapon.position_destination.y == 0:
            #         weapon.position_destination.x = self.player_pos.x + 100
            #         weapon.position_destination.y = self.player_pos.y - 100
            #         weapon.position_original.x = self.player_pos.x + 100
            #         weapon.position_original.y = self.player_pos.y - 100

            #     weapon.position_original.x += ((self.player_pos.x + 100) - weapon.position_original.x)
            #     weapon.position_original.y += ((self.player_pos.y - 100) - weapon.position_original.y)

            #     distance = math.sqrt((weapon.position_destination.x - weapon.position_original.x)**2 + (weapon.position_destination.y - weapon.position_original.y)**2)
            #     sinus = abs((weapon.position_destination.y - weapon.position_original.y)/(distance+1)) * self.compare_subtraction(weapon.position_destination.y, weapon.position_original.y)
            #     cosinus = abs((weapon.position_destination.x - weapon.position_original.x)/(distance+1)) * self.compare_subtraction(weapon.position_destination.x, weapon.position_original.x)


            #     weapon.position.x += cosinus * weapon.speed
            #     weapon.position.y += sinus * weapon.speed
            #     weapon.setPositionBasedOnMovement(self.settings.speed, dt, self.notTouchingBorder(dt))

            #     pygame.draw.circle(screen, weapon.colour, (weapon.position.x, weapon.position.y), weapon.size)
            
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
                            b = Bullet(bullet_pos, bullet_pos_original, bullet_pos_destination, weapon.bulletLifeTime, False, "bullet", weapon.size)
                            b.addRotation(weapon.rotation)
                            weapon.bullets.add(b)
                else:
                    weapon.position_destination.x = 0
                    weapon.position_destination.y = 0
                    weapon.position.x = weapon.position_original.x
                    weapon.position.y = weapon.position_original.y
                    weapon.setOnCooldown()

                    bullet_pos = pygame.Vector2(weapon.position.x, weapon.position.y)
                    bullet_pos_original = pygame.Vector2(weapon.position_original.x, weapon.position_original.y)
                    bullet_pos_destination = pygame.Vector2(weapon.position_destination.x, weapon.position_destination.y)
                    b = Bullet(bullet_pos, bullet_pos_original, bullet_pos_destination, weapon.bulletLifeTime, False, "bullet", weapon.size)
                    if "angled" in weapon.pattern:
                        b.addAnimationRotation(0)
                        b.addRotation(weapon.rotation)
                    if "multiple" in weapon.pattern and random.random() > 0.975 - weapon.level * 0.065:
                        weapon.cooldown_current = 0.02
                    weapon.bullets.add(b)
            else:
                weapon.updateCooldown(dt)
            
            for bullet in weapon.bullets:
                if "straight" in weapon.pattern:
                    if bullet.position_destination.x == 0 and bullet.position_destination.y == 0:
                        bullet.position_destination = mouse_pos

                        if "constant" in weapon.pattern:
                            sign = self.getSign()
                            bullet.position_destination.x += (random.random() * sign * (85 + 15 * weapon.level))
                            bullet.position_destination.y += (random.random() * sign * (85 + 15 * weapon.level))
                        
                        if "multiple" in weapon.pattern:
                            bullet.position_destination.x += (random.randint(-1,1) * 25)
                            bullet.position_destination.y += (random.randint(-1,1) * 25)

                    distance = math.sqrt((bullet.position_destination.x - bullet.position_original.x)**2 + (bullet.position_destination.y - bullet.position_original.y)**2)
                    sinus = abs((bullet.position_destination.y - bullet.position_original.y)/distance) * self.compare_subtraction(bullet.position_destination.y, bullet.position_original.y)
                    cosinus = abs((bullet.position_destination.x - bullet.position_original.x)/distance) * self.compare_subtraction(bullet.position_destination.x, bullet.position_original.x)

                    bullet.setPositionBasedOnMovement(self.settings.speed, dt, self.notTouchingBorder(dt))

                    bullet.position.x += cosinus * weapon.speed
                    bullet.position.y += sinus * weapon.speed
                    
                    if weapon.name == "High-tech Rifle":
                        pygame.draw.line(screen, weapon.colour, (bullet.position.x - cosinus * weapon.size, bullet.position.y - sinus * weapon.size), (bullet.position.x, bullet.position.y), 15)
                        if weapon.level >= 3:
                            pygame.draw.line(screen, "yellow", (bullet.position.x - cosinus * weapon.size/1.2, bullet.position.y - sinus * weapon.size/1.2), (bullet.position.x, bullet.position.y), 15)
                        if weapon.level == 5:
                            pygame.draw.line(screen, "orange", (bullet.position.x - cosinus * weapon.size/5, bullet.position.y - sinus * weapon.size/5), (bullet.position.x, bullet.position.y), 15)
                    
                    if weapon.name == "Flamethrower":
                        width = weapon.image_projectile.get_width()
                        height = weapon.image_projectile.get_height()
                        image = pygame.transform.scale(weapon.image_projectile, (int(width * (0.25+weapon.level*0.08)), int(height * (0.55+weapon.level*0.08))))
                        image = pygame.transform.rotate(image, 180+math.acos(sinus)*self.compare_subtraction(bullet.position_destination.x, bullet.position_original.x)*180/math.pi)
                        image_x = bullet.position.x - cosinus * weapon.size
                        image_y = bullet.position.y - sinus * weapon.size
                        if self.compare_subtraction(bullet.position_destination.x, bullet.position_original.x) == -1:
                            image_x -= image.get_width() * 0.9
                        if self.compare_subtraction(bullet.position_destination.y, bullet.position_original.y) == -1:
                            image_y -= image.get_height() * 0.9
                        rect = image.get_rect()
                        rect.topleft = (image_x, image_y)
                        screen.blit(image, (rect.x, rect.y))
                        #pygame.draw.line(screen, weapon.colour, (bullet.position.x - cosinus * weapon.size, bullet.position.y - sinus * weapon.size), (bullet.position.x, bullet.position.y), 15 + round(weapon.size * 0.02 * weapon.level * 5))
                        #if weapon.level >= 3:
                        #    pygame.draw.line(screen, "orange2", (bullet.position.x - cosinus * weapon.size/1.2, bullet.position.y - sinus * weapon.size/1.2), (bullet.position.x, bullet.position.y), 15 + round(weapon.size * 0.02 * weapon.level * 5))
                        #if weapon.level == 5:
                        #    pygame.draw.line(screen, "orange3", (bullet.position.x - cosinus * weapon.size/5, bullet.position.y - sinus * weapon.size/5), (bullet.position.x, bullet.position.y), 15 + round(weapon.size * 0.02 * weapon.level * 5))
                    
                    if weapon.name == "Pistols":
                        pygame.draw.line(screen, weapon.colour, (bullet.position.x - cosinus * weapon.size, bullet.position.y - sinus * weapon.size), (bullet.position.x, bullet.position.y), 15)
                        if weapon.level >= 3:
                            pygame.draw.line(screen, "grey", (bullet.position.x - cosinus * weapon.size/1.2, bullet.position.y - sinus * weapon.size/1.2), (bullet.position.x, bullet.position.y), 15)
                        if weapon.level == 5:
                            pygame.draw.line(screen, "blue", (bullet.position.x - cosinus * weapon.size/5, bullet.position.y - sinus * weapon.size/5), (bullet.position.x, bullet.position.y), 15)
                    
                    if isinstance(bullet.lifeTime, float):
                        if bullet.lifeTime <= 0:
                            bullet.remove(weapon.bullets)
                            bullet.kill()
                        else:
                            bullet.lifeTime -= dt

                if "circle" in weapon.pattern:
                    if bullet.rotation == 360:
                        bullet.rotation = 0

                    bullet.position.x = self.player_pos.x + weapon.distance * math.cos(bullet.rotation * math.pi / 180)
                    bullet.position.y = self.player_pos.y + weapon.distance * math.sin(bullet.rotation * math.pi / 180)
                    bullet.setPositionBasedOnMovement(self.settings.speed, dt, self.notTouchingBorder(dt))

                    pygame.draw.circle(screen, weapon.colour, (bullet.position.x, bullet.position.y), weapon.size)

                    if weapon.level >= 3:
                        pygame.draw.circle(screen, "pink", (bullet.position.x, bullet.position.y), weapon.size/2)
                    if weapon.level == 5:
                        pygame.draw.circle(screen, "white", (bullet.position.x, bullet.position.y), weapon.size/4)

                    bullet.rotation += weapon.speed * 0.05
                
                if "angled" in weapon.pattern:
                    if bullet.position_destination.x == 0 and bullet.position_destination.y == 0:
                        bullet.position_destination = mouse_pos

                    center = pygame.Vector2(
                        (bullet.position_destination.x - bullet.position_original.x) / 2 + bullet.position_original.x, 
                        (bullet.position_destination.y - bullet.position_original.y) / 2 + bullet.position_original.y, 
                        )

                    bullet.position.x = center.x + (bullet.position_original.x - bullet.position_destination.x) * math.cos(bullet.rotation * math.pi / 180) * 0.8
                    bullet.position.y = center.y + (bullet.position_original.y - bullet.position_destination.y) * math.sin(bullet.rotation * math.pi / 180) * 0.8

                    bullet.setPositionBasedOnMovement(self.settings.speed, dt, self.notTouchingBorder(dt))

                    if pygame.sprite.collide_circle(bullet, self.playerCharacter) or bullet.rotation > 40:
                        rect = pygame.Rect(bullet.position.x, bullet.position.y, weapon.size*3, weapon.size*3)
                        pygame.draw.arc(screen, weapon.colour, rect, math.radians(0 + bullet.animation_rotation), math.radians(120 + weapon.level * 25 + bullet.animation_rotation), 7 + weapon.level)
                        
                        if weapon.level >= 3:
                            pygame.draw.arc(screen, "blue", rect, math.radians(0 + bullet.animation_rotation), math.radians(140 + weapon.level * 20 + bullet.animation_rotation), 2 + weapon.level)

                        if weapon.level == 5:
                            pygame.draw.arc(screen, "indianred3", rect, math.radians(0 + bullet.animation_rotation), math.radians(140 + weapon.level * 20 + bullet.animation_rotation), 2)

                    bullet.rotation += weapon.speed * 0.1 * (1 + abs(math.sin(bullet.rotation * math.pi / 180)))
                    bullet.animation_rotation += weapon.speed * 0.3 * (1 + abs(math.sin(bullet.rotation * math.pi / 180)))

                    if (pygame.sprite.collide_circle(bullet, self.playerCharacter) and bullet.rotation >= 180 ) or bullet.rotation >= 410:
                        bullet.remove(weapon.bullets)
                        bullet.kill()
        
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