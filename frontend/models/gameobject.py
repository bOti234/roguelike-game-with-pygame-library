from typing import List, Dict, Union
import pygame
import os
import math
from ..utils.database import fetch_user, submit_new_user

class GameObject(pygame.sprite.Sprite):
	def __init__(self, objtype: str, position, width: int, height: int):
		pygame.sprite.Sprite.__init__(self)
		self.objtype: str = objtype
		self.position: pygame.Vector2 = position
		self.width = width
		self.height = height
		if self.objtype in ["enemy", "player", "experience"] or ("bullet" in self.objtype and (self.weaponname == "Energy Orb" or self.weaponname == "Damaging Field" or "Scatter" in self.weaponname)):
			self.radius = self.width / 2
			if self.objtype == "enemy":
				self.rect = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.width, self.height)
			else:
				self.rect = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.width, self.height)
		else:
			self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
	
	def setHitbox(self):
		pass
	
	def setPositionBasedOnMovement(self, speed, dt, rate = 1):
		keys = pygame.key.get_pressed()
		#TODO: CHECK WHAT HAPPENS WHEN >2 BUTTONS ARE PRESSED
		if keys[pygame.K_w]:# and "up" not in gate:
			self.position.y += speed * dt * rate

		if keys[pygame.K_a]:# and "left" not in gate:
			self.position.x += speed * dt * rate

		if keys[pygame.K_s]:# and "down" not in gate:
			self.position.y -= speed * dt * rate

		if keys[pygame.K_d]:# and "right" not in gate:
			self.position.x -= speed * dt * rate

		if [keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d]].count(True) == 2:
			if keys[pygame.K_w] and keys[pygame.K_a]:# and "up" not in gate and "left" not in gate:
				self.position.y += speed * rate * ( dt / 2**(1/2) -  dt)
				self.position.x += speed * rate * ( dt / 2**(1/2) -  dt)

			if keys[pygame.K_w] and keys[pygame.K_d]:# and "up" not in gate and "right" not in gate:
				self.position.y += speed * rate * ( dt / 2**(1/2) -  dt)
				self.position.x -= speed * rate * ( dt / 2**(1/2) -  dt)

			if keys[pygame.K_s] and keys[pygame.K_a]:# and "down" not in gate and "left" not in gate:
				self.position.y -= speed * rate * ( dt / 2**(1/2) -  dt)
				self.position.x += speed * rate * ( dt / 2**(1/2) -  dt)

			if keys[pygame.K_s] and keys[pygame.K_d]:# and "down" not in gate and "right" not in gate:
				self.position.y -= speed * rate * ( dt / 2**(1/2) -  dt)
				self.position.x -= speed * rate * ( dt / 2**(1/2) -  dt)
		if self.objtype in ["enemy", "experience"] or (self.objtype == "bullet" and self.weaponname == "Energy Orb"):
			self.rect = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.width, self.height)
		else:
			self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)

class PlayerCharacter(GameObject):
	def __init__(self, radius, position: pygame.Vector2, health, speed):
		objtype = "player"
		super().__init__(objtype, pygame.Vector2(position.x, position.y), radius*2, radius*2)

		self.buffs: Dict[str, Union[int, float, Dict[str, Union[int, float]]]] = {
			"damage percentage":{},
			"damage flat": {},
			"health percentage": {},
			"health flat": {},
			"speed percentage": {},
			"speed flat": {},
			"health regen": 0.0,
			"barrier": 0.0,
			"dodge count": 0,
			"gunslinger": 0,
		}

		self.level = 1
		self.health_max_base = health
		self.speed_base = speed
		self.setStats()
		self.health_current = self.health_max
		self.hitCooldown = 0
		self.experience_max: int = 500
		self.experience_current: int = 0
		self.experience_queue: int = 0
	
	def setStats(self):
		flatbuff_health = sum([0]+[val for val in self.buffs["health flat"].values()])
		percbuff_health = math.prod([1 + val for val in self.buffs["health percentage"].values()])
		
		flatbuff_speed = sum([0]+[val for val in self.buffs["speed flat"].values()])
		percbuff_speed = math.prod([1 + val for val in self.buffs["speed percentage"].values()])

		self.health_max = (self.health_max_base + (self.level - 1) * 10 + flatbuff_health) * percbuff_health
		self.speed = (self.speed_base + (self.level - 1) * 25 + flatbuff_speed) * percbuff_speed

	def updateBuffs(self, value, buffname, passive = None):
		if passive:
			self.buffs[buffname].update({passive: value})
		else:
			self.buffs.update({buffname: value})
	
	def updateExperience(self):
		n = 0
		while self.experience_queue > self.experience_max:
			n += 1
			self.experience_queue -= int(self.experience_max)
			self.experience_max = int(round(self.experience_max * 1.2))
		if self.experience_queue > 10:
			self.experience_current += ((self.experience_queue // 100) + 10)
			self.experience_queue -= ((self.experience_queue // 100) + 10)
		elif self.experience_queue >= 1:
			self.experience_current += ((self.experience_queue // 100) + 1)
			self.experience_queue -= ((self.experience_queue // 100) + 1)
		if self.experience_current >= self.experience_max:
			n += 1
			self.experience_current -= int(self.experience_max)
			self.experience_max = int(round(self.experience_max * 1.2))
		self.level += n
		self.setStats()
		return n

class Passive():
	def __init__(self, name, value, cooldown):
		self.name = name
		self.level = 0
		self.value = value
		self.cooldown_max = cooldown
		self.cooldown_current = 0
		if self.name == "Gunslinger":
			self.count = 1
		else:
			self.count = 0
		self.description = self.getDescription()

		self.loadImages()
	
	def loadImages(self):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filepath_pasive = os.path.join(dirname, '../../assets/images/passives/')
			self.image_base = pygame.image.load(filepath_pasive + "/"+str(self.name)+"_1.jpg").convert_alpha()
			self.image_maxed = pygame.image.load(filepath_pasive + "/"+str(self.name)+"_2.jpg").convert_alpha()
	
	def updateCooldown(self, dt):
		if self.cooldown_current > 0:
			self.cooldown_current -= dt
		if self.cooldown_current < 0:
			self.cooldown_current = 0
	
	def setHitbox(self, position: pygame.Vector2, radius):
		self.position = position
		self.radius = radius
		self.rect = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.radius * 2, self.radius * 2)
	
	def upgradeItem(self, player: PlayerCharacter, amount = 1):
		for i in range(amount):
			if self.level < 5:
				self.level += 1
			
			if self.name == "Health Regeneration":
				if self.level > 1:
					self.value += 1
					self.cooldown_max -= 1
				player.updateBuffs(self.value, "health regen")
			
			if self.name == "Protective Barrier":
				if self.level > 1:
					self.value += 5
					self.cooldown_max -= 1
				player.updateBuffs(self.value, "barrier")

			if self.name == "Greater Strength":
				if self.level > 1:
					self.value += 0.05
					player.updateBuffs(self.value, "damage percentage", self.name)
				if self.level == 5:
					player.updateBuffs(1, "damage flat", self.name)

			if self.name == "Dodge":
				if self.level > 1:
					self.value += 1
					self.cooldown_max -= 1

			if self.name == "Crit rate":
				if self.level > 1:
					self.value += 0.05
			
			if self.name == "Gunslinger":
				if self.level > 1:
					self.value += 5
					self.count += 1
				player.updateBuffs(self.value, "gunslinger")

			if self.name == "Berserk":
				if self.level > 1:
					self.value += 0.2
				player.updateBuffs(self.value, "damage percentage", self.name)
			
			if self.name == "Greater Vitality":
				if self.level > 1:
					self.value += 10
				player.updateBuffs(self.value, "health flat", self.name)
				if self.level == 5:
					player.updateBuffs(0.2, "health percentage", self.name)
			
			if  self.name == "Slowing Aura":
				if self.level > 1:
					self.value += 0.1
				self.setHitbox(player.position, self.value * 5 + 49 + 50 * self.level)

	def getDescription(self):
		dirname = os.path.dirname(__file__)
		filename_passive = os.path.join(dirname, '../../assets/descriptions/passives.txt')
		with open(filename_passive, "r") as f:
			cont = {}
			[cont.update(eval(line)) for line in f.readlines()]
		return eval(cont[self.name])
	
class Bullet(GameObject):
	def __init__(self, weaponnanme: str, position: pygame.Vector2, position_original: pygame.Vector2, position_destination: pygame.Vector2, lifetime: float, damage: float, pierce: int, crit: bool, objtype: str, width_and_height: int):
		self.weaponname = weaponnanme
		super().__init__(objtype, position, width_and_height, width_and_height)
		#self.position = position
		self.position_original = position_original
		self.position_destination = position_destination
		self.lifeTime: float = lifetime
		self.damage: float = damage
		self.pierce: int = pierce
		self.crit: bool = crit

		self.enemiesHit: List[Enemy] = []

	def addRotation(self, rotation):
		self.rotation = rotation
		
	def addAnimationRotation(self, rotation):
		self.animation_rotation = rotation

class Weapon(GameObject):
	def __init__(self, name: str, cooldown_max: float, dmgtype: str, pattern: str, colour: str, size: int, speed: int, bulletlifetime: Union[int, str], charge: int, damage: float, pierce: float, position: pygame.Vector2, slow: float, knockback: float, weaken: float):
		objtype = "weapon"
		self.pattern: str = pattern
		self.name: str = name
		if self.name == "Energy Orb" or self.name == "Boomerang" or self.name == "Attack Drone" or self.name == "Homing Arrow":
			self.rotation = 0
			self.distance = 150
			position.x -= size
			position.y -= size
			width_and_height = size
		else:
			self.rotation = None
			self.distance = None
			width_and_height = size

		self.range = None
		if self.name == "Attack Drone":
			self.range = 300

		if self.name == "Homing Arrow":
			self.range = 500
			self.pathlist: List[pygame.Vector2] = []

		if self.name == "Damaging Field":
			self.range = 800
		
		if self.name == "Cluster Bombs":
			self.projectile_damage = 10
			self.projectile_range = 50
			self.projectile_count = 10
			self.projectile_size = 10

		if self.name == "Scatter Rifle":
			self.projectile_damage = 10
			self.projectile_range = 350
			self.projectile_count = 5
			self.projectile_size = 10

		
		self.status_effects = {"slow":slow, "knockback":knockback, "weaken":weaken}

		super().__init__(objtype, position, width_and_height, width_and_height)

		self.cooldown_max: float = cooldown_max
		self.cooldown_current: float = cooldown_max
		self.dmgtype: str = dmgtype
		self.level: int = 0
		self.colour: str = colour
		self.size: int = size
		self.speed: int = speed
		self.bulletLifeTime: float = bulletlifetime
		self.charge_max: int = charge
		self.charge_current: int = charge
		self.damage: float = damage
		self.pierce: int = pierce
		self.bullets: pygame.sprite.Group[Bullet] = pygame.sprite.Group()
		self.position_original = pygame.Vector2(position.x, position.y)
		self.position_destination = pygame.Vector2(0,0)
		self.animation: bool = False
		self.description = self.getDescription()

		self.loadImages()
	
	def getDescription(self):	#TODO: LOOK UP GINGA AND i18n!!!!!!!!!!!!!!!
		dirname = os.path.dirname(__file__)
		filename_desc = os.path.join(dirname, '../../assets/descriptions/weapons.txt')
		with open(filename_desc, "r") as f:
			cont = {}
			[cont.update(eval(line)) for line in f.readlines()]
		return eval(cont[self.name])
	
	def loadImages(self):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filename_weapon = os.path.join(dirname, '../../assets/images/weapons/')
			self.image_base = pygame.image.load(filename_weapon + "/"+str(self.name)+"_1.jpg").convert_alpha()
			self.image_maxed = pygame.image.load(filename_weapon + "/"+str(self.name)+"_2.jpg").convert_alpha()
			if self.name == "Flamethrower":
				filename_projectile = os.path.join(dirname, '../../assets/images/projectiles/')
				self.image_projectile = pygame.image.load(filename_projectile + "/"+str(self.name)+"_projectile.png").convert_alpha()
			else:
				self.image_projectile = None
		else:
			self.image_base, self.image_maxed, self.image_projectile = None, None, None
			

	def updateCooldown(self, dt):
		if self.cooldown_current > 0:
			self.cooldown_current -= dt
		if self.cooldown_current < 0:
			self.cooldown_current = 0
	
	def setOnCooldown(self):
		if self.cooldown_current <= 0:
			self.cooldown_current = self.cooldown_max
	
	def upgradeItem(self, player = None, amount = 1):
		for i in range(amount):
			if self.level < 5:
				self.level += 1

				if self.level > 1:
					if "straight" in self.pattern:
						self.damage += 10
						self.speed += 4
						self.size += 2
					
					if self.name == "High-tech Rifle":
						self.cooldown_max -= 0.1 * (5 - self.level)
						self.pierce += 1
						if self.level >= 3:
							self.charge_max += 1
						if self.level == 5:
							self.damage += 15
							self.speed -= 3
							self.pierce += 1
					
					if self.name == "Flamethrower":
						self.cooldown_max -= 0.075
						self.speed -= (2 - self.level)
						self.size += 1
						self.damage -= 9
						self.bulletLifeTime -= 0.004 * self.level
						if self.level > 2:
							self.pierce += 1
						if self.level == 5:
							self.bulletLifeTime -= 0.01
							self.cooldown_max += 0.045
							self.pierce -= 1

					if self.name == "Damaging Field":
						self.status_effects["slow"] += 0.1
						self.size += 50
						self.damage += 0.15
						self.cooldown_max -= 0.1
						self.bulletLifeTime += 0.3
					
					if self.name == "Pistols":
						self.speed -= 3
						self.cooldown_max -= 0.02
						self.bulletLifeTime += 0.05
						self.damage -= 4 - self.level
						if self.level >= 4:
							self.charge_max += 1
							self.damage += 1
							self.pierce += 1
					
					if "cluster" in self.pattern:
						self.cooldown_max -= 0.25
						self.bulletLifeTime += 5
						self.size += 3
						self.damage += 7
						self.projectile_damage += 5
						self.projectile_count += 4
						self.projectile_range += 22
						self.projectile_size += 3

					if self.name == "Scatter Rifle":
						self.cooldown_max -= 0.225
						self.bulletLifeTime += 0.05
						self.size += 5
						self.damage += 10
						self.pierce += 1
						self.projectile_damage += 7
						self.projectile_count += 2
						self.projectile_range += 50
						self.projectile_size += 5
					
					if self.name == "Energy Orb":
						self.speed *= 1.1
						self.size += 5
						self.distance += 50
						self.cooldown_max -= 0.75
						self.pierce += 2
						self.bulletLifeTime += 2.75
						if self.level == 5:
							self.bulletLifeTime += 5
					
					if self.name == "Boomerang":
						self.cooldown_max -= 0.425
						self.damage += 10
						self.size += 3
						self.speed += 2
						self.pierce += 2
						if self.level >= 4:
							self.size += 2
							self.speed += 1
						if self.level == 5:
							self.damage += 5
					
					if self.name == "Attack Drone":
						self.damage += 0.2 * self.level
						self.pierce += 1
						self.range += 50
						self.speed += 10
						self.size += 2.5
							
						if self.level == 5:
							self.range += 50
					
					if self.name == "Homing Arrow":
						self.damage += 2
						self.range += 50
						self.speed += 5
						self.size += 2

	
	def getClusters(self, bullet: Bullet):
		b = []
		r = self.projectile_count
		for i in range(r):
			angle = 360 / r
			destination = pygame.Vector2(bullet.position.x + self.projectile_range * math.cos(i * angle * math.pi / 180), bullet.position.y + self.projectile_range * math.sin(i * angle * math.pi / 180))
			position = pygame.Vector2(bullet.position.x, bullet.position.y)
			b.append(Bullet("Cluster Bombs", position, position, destination, 8 + (self.level - 1), self.projectile_damage, self.pierce, False, "bullet mine", self.projectile_size))
		return b
	
	def getScatters(self, bullet: Bullet):
		b = []
		r = self.projectile_count
		for i in range(r):
			angle = 360 / r
			destination = pygame.Vector2(bullet.position.x + self.projectile_range * math.cos(i * angle * math.pi / 180), bullet.position.y + self.projectile_range * math.sin(i * angle * math.pi / 180))
			position = pygame.Vector2(bullet.position.x, bullet.position.y)
			b.append(Bullet("Scatter Rifle", position, position, destination, 1.2, self.projectile_damage, self.pierce - 1,False, "bullet scatter", self.projectile_size))
		return b

class Enemy(GameObject):

	def __init__(self, position: pygame.Vector2, level = 1, radius: float = 30, health: float = 30, colour = "red", damage: float = 10, speed: float = 10, weakness = "energy", type = "normal"):
		objtype = "enemy"
		super().__init__(objtype, position, radius * 2, radius * 2)

		self.position_original = pygame.Vector2(position.x, position.y)
		self.position_destination = pygame.Vector2(0,0)
		self.level = level
		if self.level > 21:
			self.level = 21
		self.radius = radius
		self.health = health + (self.level - 1) * 5
		self.colour = colour
		self.damage = damage + (self.level - 1) * 1
		self.speed = speed + (self.level - 1) * 2
		self.weakness = weakness
		self.type = type
		self.hitCooldown = 0


	def setStatusDict(self, weaponlist: List[Weapon]):
		self.status_effects: Dict[str, Dict[str, Union[bool, float, int]]] = {}
		for weapon in weaponlist:
			self.status_effects.update({weapon.name:{"active":False, "duration":0.0}})
  
	def updateStatusDict(self, dt):
		for attr in self.status_effects.values():
			if attr["active"]:
				if attr["duration"] <= 0:
					attr["duration"] = 0.0
					attr["active"] = False
				else:
					attr["duration"] -= dt

class Experience(GameObject):
	def __init__(self, position: pygame.Vector2, radius, colour, value):
		objtype = "experience"
		width_and_height = radius * 2
		super().__init__(objtype, position, width_and_height, width_and_height)

		self.position_original = pygame.Vector2(position.x, position.y)
		self.position_destination = pygame.Vector2(0,0)
		self.speed = 10
		self.radius = radius
		self.colour = colour
		self.value = value
		self.min_distance = 200

		self.r = 254
		self.g = 0
		self.b = 0
	
	def setMinDistance(self, dist):
		self.min_distance = dist

class Item(GameObject):
	def __init__(self, objtype, position, width, height):
		super().__init__(objtype, position, width, height)

class WeaponKit(Item):
	def __init__(self, position, width = 50, height = 50):
		objtype = "weaponkit"
		self.colour = "gray"
		super().__init__(objtype, position, width, height)

class HealthKit(Item):
	def __init__(self, position, width = 30, height = 30):
		objtype = "healthkit"
		self.colour = "green"
		self.lifetime = 30
		super().__init__(objtype, position, width, height)

class Magnet(Item):
	def __init__(self, randpos, width = 50, height = 50):
		objtype = "magnet"
		self.colour = "red"
		super().__init__(objtype, randpos, width, height)

class HUD(GameObject):
	def __init__(self, objtype):
		pass
		#super().__init__(objtype)


class Inventory(HUD):
	def __init__(self):
		pass

class Menu(HUD):
	def __init__(self):
		self.opened = False
		self.state = None

	def openMainMenu(self, screen, screen_width: int, screen_height: int, userdata = None):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../assets/images/buttons/')
			resume_img = pygame.image.load(filename+"/button_resume.png").convert_alpha()
			login_img = pygame.image.load(filename+"/button_login.png").convert_alpha()
			create_img = pygame.image.load(filename+"/button_createuser.png").convert_alpha()
			quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()

			back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

			#create button instances
			scale = 0.2
			font = pygame.font.Font(None, 30)
			resume_button = Button(screen_width/2 - resume_img.get_width()/2 * scale, screen_height/4 + 50, resume_img, scale)
			login_button = Button(screen_width/2 - login_img.get_width()/2 * scale, screen_height/4 + 175, login_img, scale)
			create_button = Button(screen_width/2 - create_img.get_width()/2 * scale, screen_height/4 + 300, create_img, scale)
			quit_button = Button(screen_width/2 - quit_img.get_width()/2 * scale, screen_height/4 + 425, quit_img, scale)

			#userdata_textbutton = Button()

			username_textbox = TextBox(screen_width/2 - 30 * font.size("_")[0]/2, screen_height/4 + 100, 30 * font.size("_")[0], font.get_linesize()*2, font, "username", "username...")
			password_textbox = TextBox(screen_width/2 - 30 * font.size("_")[0]/2, screen_height/4 + 175, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password...")
			password2_textbox = TextBox(screen_width/2 - 30 * font.size("_")[0]/2, screen_height/4 + 250, 30 * font.size("_")[0], font.get_linesize()*2, font, "password", "password again...")
			email_textbox = TextBox(screen_width/2 - 30 * font.size("_")[0]/2, screen_height/4 + 325, 30 * font.size("_")[0], font.get_linesize()*2, font, "email", "email address...")
			back_button = Button(screen_width/2 - back_img.get_width()/2 * scale, screen_height/4 + 475, back_img, scale)

			#game loop
			run = True
			button_timeout = 100
			while run:
				if button_timeout > 0:
					button_timeout -= 1
				screen.fill("black")
				window = pygame.Rect(screen_width/4, screen_height/4, screen_width/2, screen_height/2)
				pygame.draw.rect(screen, (52, 78, 91), window)

				#check menu state
				if self.state == "inMainMenu":
					#draw pause screen buttons
					if resume_button.draw(screen):
						return "start game"
					
					if login_button.draw(screen):
						login_button.rect.y = screen_height/4 + 400
						self.state = "logInMenu"

					if create_button.draw(screen):
						create_button.rect.y = screen_height/4 + 400
						self.state = "createMenu"

					if quit_button.draw(screen):
						if button_timeout <= 0:
							run = False
							return "exit"
				
				if self.state == "logInMenu":
					username_textbox.draw(screen), password_textbox.draw(screen)

					if login_button.draw(screen):
						response = fetch_user(username_textbox.text, password_textbox.text)
						if response["status"] == "error":
							username_textbox.reset(), password_textbox.reset(), password2_textbox.reset(), email_textbox.reset()
							self.state == "logInMenu"
							button_timeout = 100
						else:
							userdata = response["userdata"]
							login_button.rect.y = screen_height/4 + 175
							self.state = "inMainMenu"
							button_timeout = 100

					if back_button.draw(screen):
						login_button.rect.y = screen_height/4 + 175
						self.state = "inMainMenu"
						button_timeout = 100

				if self.state == "createMenu":
					username_textbox.draw(screen), password_textbox.draw(screen), password2_textbox.draw(screen), email_textbox.draw(screen)

					if create_button.draw(screen):
						response = submit_new_user(username_textbox.text, password_textbox.text, password2_textbox.text, email_textbox.text, 0)
						if response["status"] == "error":
							username_textbox.reset(), password_textbox.reset(), password2_textbox.reset(), email_textbox.reset()
							self.state == "createMenu"
							button_timeout = 100
						else:
							userdata = response["userdata"]
							create_button.rect.y = screen_height/4 + 300
							self.state = "inMainMenu"
							button_timeout = 100

					if back_button.draw(screen):
						create_button.rect.y = screen_height/4 + 300
						self.state = "inMainMenu"
						button_timeout = 100


				#event handler
				for event in pygame.event.get():
					if self.state == "logInMenu" or self.state == "createMenu":
						username_textbox.handle_event(event)
						password_textbox.handle_event(event)
						if self.state == "createMenu":
							password2_textbox.handle_event(event)
							email_textbox.handle_event(event)
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

	def openInGameMenu(self, screen, screen_width: int, screen_height: int):
		if pygame.get_init():

			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../assets/images/buttons/')
			resume_img = pygame.image.load(filename+"/button_resume.png").convert_alpha()
			options_img = pygame.image.load(filename+"/button_options.png").convert_alpha()
			quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()
			video_img = pygame.image.load(filename+"/button_video.png").convert_alpha()
			audio_img = pygame.image.load(filename+"/button_audio.png").convert_alpha()
			keys_img = pygame.image.load(filename+"/button_keys.png").convert_alpha()
			back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

			#create button instances
			scale = 0.2
			resume_button = Button(screen_width/2 - resume_img.get_width()/2 * scale, screen_height/4 + 125, resume_img, scale)
			options_button = Button(screen_width/2 - options_img.get_width()/2 * scale, screen_height/4 + 250, options_img, scale)
			quit_button = Button(screen_width/2 - quit_img.get_width()/2 * scale, screen_height/4 + 375, quit_img, scale)
			video_button = Button(screen_width/2 - video_img.get_width()/2 * scale, screen_height/4 + 75, video_img, scale)
			audio_button = Button(screen_width/2 - audio_img.get_width()/2 * scale, screen_height/4 + 200, audio_img, scale)
			keys_button = Button(screen_width/2 - keys_img.get_width()/2 * scale, screen_height/4 + 325, keys_img, scale)
			back_button = Button(screen_width/2 - back_img.get_width()/2 * scale, screen_height/4 + 450, back_img, scale)

			#game loop
			run = True
			while run:
				window = pygame.Rect(screen_width/4, screen_height/4, screen_width/2, screen_height/2)
				pygame.draw.rect(screen, (52, 78, 91), window)

				#check menu state
				if self.state == "ingame":
					#draw pause screen buttons
					if resume_button.draw(screen):
						return "closed"
					if options_button.draw(screen):
						self.state = "options"
					if quit_button.draw(screen):
						run = False
						return "return to main menu"
				#check if the options menu is open
				if self.state == "options":
					#draw the different options buttons
					if video_button.draw(screen):
						print("Video Settings")
					if audio_button.draw(screen):
						print("Audio Settings")
					if keys_button.draw(screen):
						print("Change Key Bindings")
					if back_button.draw(screen):
						self.state = "ingame"

				#event handler
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

	def openItemSelectorMenu(self, screen: pygame.Surface, screen_width: int, screen_height: int, itemlist: List[Union[Weapon, Passive]]):
		if pygame.get_init():
			# Load button images for menu buttons selection
			for item in itemlist:
				item.loadImages()

			# Create button instances for weapon selection
			images: List[pygame.Surface] = []
			for i in range(len(itemlist)):
				font = pygame.font.Font(None, 30)
				text = font.render(itemlist[i].name, True, "black")
				screen.blit(text, (0, 300 + 50 * i))
				
				if itemlist[i].level < 4:
					images.append(itemlist[i].image_base)
				else:
					images.append(itemlist[i].image_maxed)

			font = pygame.font.Font(None, 30)
			if len(itemlist) == 1:
				item_button1 = Button(screen_width / 2 - images[0].get_width() * 0.1 / 2 + 400, screen_height / 4 + 250, images[0], 0.1)
				text_box1 = pygame.Rect(screen_width / 4 - 150, screen_height / 4 + 250, screen_width / 4 - images[0].get_width() * 0.1 / 2 + 550, images[0].get_height() * 0.1)
				text_button1 = Button(screen_width / 4 - 150, screen_height / 4 + 250, [font, itemlist[0].description, "white", text_box1], 1)

			elif len(itemlist) == 2:
				item_button1 = Button(screen_width / 2 - images[0].get_width() * 0.1 / 2 + 400, screen_height / 4 + 150, images[0], 0.1)
				text_box1 = pygame.Rect(screen_width / 4 - 150, screen_height / 4 + 150, screen_width / 4 - images[0].get_width() * 0.1 / 2 + 550, images[0].get_height() * 0.1)
				text_button1 = Button(screen_width / 4 - 150, screen_height / 4 + 150, [font, itemlist[0].description, "white", text_box1], 1)

				item_button2 = Button(screen_width / 2 - images[1].get_width() * 0.1 / 2 + 400, screen_height / 4 + 350, images[1], 0.1)
				text_box2 = pygame.Rect(screen_width / 4 - 150, screen_height / 4 + 350, screen_width / 4 - images[1].get_width() * 0.1 / 2 + 550, images[1].get_height() * 0.1)
				text_button2 = Button(screen_width / 4 - 150, screen_height / 4 + 350, [font, itemlist[1].description, "white", text_box2], 1)
			
			elif len(itemlist) == 3:
				item_button1 = Button(screen_width / 2 - images[0].get_width() * 0.1 / 2 + 400, screen_height / 4 + 50, images[0], 0.1)
				text_box1 = pygame.Rect(screen_width / 4 - 150, screen_height / 4 + 50, screen_width / 4 - images[0].get_width() * 0.1 / 2 + 550, images[0].get_height() * 0.1)
				text_button1 = Button(screen_width / 4 - 150, screen_height / 4 + 50, [font, itemlist[0].description, "white", text_box1], 1)

				item_button2 = Button(screen_width / 2 - images[1].get_width() * 0.1 / 2 + 400, screen_height / 4 + 250, images[1], 0.1)
				text_box2 = pygame.Rect(screen_width / 4 - 150, screen_height / 4 + 250, screen_width / 4 - images[1].get_width() * 0.1 / 2 + 550, images[1].get_height() * 0.1)
				text_button2 = Button(screen_width / 4 - 150, screen_height / 4 + 250, [font, itemlist[1].description, "white", text_box2], 1)

				item_button3 = Button(screen_width / 2 - images[2].get_width() * 0.1 / 2 + 400, screen_height / 4 + 450, images[2], 0.1)
				text_box3 = pygame.Rect(screen_width / 4 - 150, screen_height / 4 + 450, screen_width / 4 - images[2].get_width() * 0.1 / 2 + 550, images[2].get_height() * 0.1)
				text_button3 = Button(screen_width / 4 - 150, screen_height / 4 + 450, [font, itemlist[2].description, "white", text_box3], 1)

			# Game loop
			run = True
			while run:
				window = pygame.Rect(screen_width / 4 - 200, screen_height / 4, screen_width / 2 + 400, screen_height / 2)
				pygame.draw.rect(screen, (52, 78, 91), window)

				# Check menu state
				if self.state == "weapon_selector" or self.state == "passive_selector":
					# Draw item selection buttons
					if len(itemlist) > 0:
						if item_button1.draw(screen) or text_button1.drawText(screen):
							return ["closed", itemlist[0]]
					if len(itemlist) > 1:
						if item_button2.draw(screen) or text_button2.drawText(screen):
							return ["closed", itemlist[1]]
					if len(itemlist) > 2:
						if item_button3.draw(screen) or text_button3.drawText(screen):
							return ["closed", itemlist[2]]

				# Event handler
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False

				pygame.display.update()

class Button():
	def __init__(self, x, y, image: Union[pygame.Surface, List[Union[pygame.font.Font, str, pygame.Rect]]], scale):
		if isinstance(image, list):
			self.font = image[0]
			self.text = image[1]
			self.colour = image[2]
			self.rect = image[3]
		else:
			width = image.get_width()
			height = image.get_height()
			self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
			self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False
		self.timeout = 5
	
	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.timeout == 0:
			if self.rect.collidepoint(pos):
				if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
					self.clicked = True
					action = True

			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

		else:
			if pygame.mouse.get_pressed()[0] == 0:
				self.timeout -= 1

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

	def drawText(self, surface, aa=False, bkg=None):
		text = self.text
		y = self.rect.top
		lineSpacing = -2

		# get the height of the font
		fontHeight = self.font.size("Tg")[1]

		while text:
			i = 1

			# determine if the row of text will be outside our area
			if y + fontHeight > self.rect.bottom:
				break

			# determine maximum width of line
			while self.font.size(text[:i])[0] < self.rect.width and i < len(text):
				i += 1

			# if we've wrapped the text, then adjust the wrap to the last word      
			if i < len(text): 
				i = text.rfind(" ", 0, i) + 1

			# render the line and blit it to the surface
			if bkg:
				image = self.font.render(text[:i], 1, self.colour, bkg)
				image.set_colorkey(bkg)
			else:
				image = self.font.render(text[:i], aa, self.colour)
			
			surface.blit(image, (self.rect.left, y))
			y += fontHeight + lineSpacing

			# remove the text we just blitted
			text = text[i:]

		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		
		return action
	

class TextBox():
	def __init__(self, x, y, width, height, font, texttype, placeholder_text, text_colour = (0, 0, 0), placeholder_colour = (150, 150, 150), active_colour = (255, 0, 0), bg_colour = (255, 255, 255)):
		self.rect = pygame.Rect(x, y, width, height)
		self.font: pygame.font.Font = font
		self.type = texttype
		self.placeholder_text = placeholder_text
		self.text_colour = text_colour
		self.placeholder_colour = placeholder_colour
		self.active_colour = active_colour
		self.bg_colour = bg_colour
		self.text = ""
		self.active = False
		self.render_text = placeholder_text
		self.cursor_show = False
		self.cursor_timer = 500
		self.hovered = False

	def reset(self):
		self.text = ""
		self.active = False
		self.cursor_show = False
		self.cursor_timer = 500
		self.hovered = False

	def handle_event(self, event):
		pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:
			# If the user clicked on the text box rect
			if self.rect.collidepoint(pos):
				# Toggle the active variable
				self.active = True
			else:
				self.active = False
		
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_RETURN:
					print(self.text)	# TODO: REQUEST A LOG IN
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode
		
		self.render_text = self.text if self.text != "" else self.placeholder_text

	def draw(self, surface: pygame.Surface):
		# Draw the background
		pygame.draw.rect(surface, self.bg_colour, self.rect)

		# Draw the text
		colour = self.placeholder_colour if self.text == "" else self.text_colour
		if self.type == "password" and self.text != "":
			final_text = ""
			for i in range(len(self.render_text)):
				final_text += "•"
		else:
			final_text = self.render_text
		text_surface = self.font.render(final_text, True, colour)
		surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

		# Draw the border
		if self.active:
			pygame.draw.rect(surface, self.active_colour, self.rect, 3)
			if self.cursor_show:
				text_size = 6
				if self.text != "":
					for letter in final_text:
						text_size += self.font.size(letter)[0]
				pygame.draw.line(surface, (0,0,0), (self.rect.x + text_size, self.rect.y + 4), (self.rect.x + text_size, self.rect.y + self.rect.height - 20), 2)
		else:
			pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
		
		if self.cursor_timer <= 0:
			self.cursor_show = not self.cursor_show
			self.cursor_timer = 500
		else:
			self.cursor_timer -= 1