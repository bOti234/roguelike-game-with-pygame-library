from typing import List, Dict, Union
import pygame
import os
import math

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

		self.status_effects: Dict[str, Union[int, float, Dict[str, Union[int, float, Enemy]]]] = {
			'weaken':0.0,
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
		self.experience_max: int = 1000
		self.experience_current: int = 0
		self.experience_queue: int = 0
	
	def setStats(self):
		flatbuff_health = sum([0]+[val for val in self.status_effects["health flat"].values()])
		percbuff_health = math.prod([1 + val for val in self.status_effects["health percentage"].values()])
		
		flatbuff_speed = sum([0]+[val for val in self.status_effects["speed flat"].values()])
		percbuff_speed = math.prod([1 + val for val in self.status_effects["speed percentage"].values()])	# calculates the product

		self.health_max = (self.health_max_base + flatbuff_health) * percbuff_health
		self.speed = (self.speed_base + flatbuff_speed) * percbuff_speed

	def updateStatusEffects(self, value, statusname, passive = None):
		if passive:
			self.status_effects[statusname].update({passive: value})
		else:
			self.status_effects.update({statusname: value})
	
	def updateExperience(self):
		n = 0
		while self.experience_queue > self.experience_max:
			n += 1
			self.experience_queue -= int(self.experience_max)
			self.experience_max = int(round(self.experience_max * 1.1))
		if self.experience_queue > 10:
			self.experience_current += ((self.experience_queue // 100) + 10)
			self.experience_queue -= ((self.experience_queue // 100) + 10)
		elif self.experience_queue >= 1:
			self.experience_current += ((self.experience_queue // 100) + 1)
			self.experience_queue -= ((self.experience_queue // 100) + 1)
		if self.experience_current >= self.experience_max:
			n += 1
			self.experience_current -= int(self.experience_max)
			self.experience_max = int(round(self.experience_max * 1.1))
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
	
	def upgradeItem(self, player: PlayerCharacter, amount = 1, noTest = True):
		for i in range(amount):
			if self.level < 5:
				self.level += 1
			
			if self.name == "Health Regeneration":
				if self.level > 1:
					self.value += 5
					self.cooldown_max -= 1
				if noTest:
					player.updateStatusEffects(self.value, "health regen")
			
			if self.name == "Protective Barrier":
				if self.level > 1:
					self.value += 5
					self.cooldown_max -= 1
				if noTest:
					player.updateStatusEffects(self.value, "barrier")

			if self.name == "Greater Strength":
				if self.level > 1:
					self.value += 0.05
					if noTest:
						player.updateStatusEffects(self.value, "damage percentage", self.name)
				if self.level == 5:
					if noTest:
						player.updateStatusEffects(1, "damage flat", self.name)

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
				if noTest:
					player.updateStatusEffects(self.value, "gunslinger")

			if self.name == "Berserk":
				if self.level > 1:
					self.value += 0.2
				if noTest:
					player.updateStatusEffects(self.value, "damage percentage", self.name)
			
			if self.name == "Greater Vitality":
				if self.level > 1:
					self.value += 25
				if noTest:
					player.updateStatusEffects(self.value, "health flat", self.name)
				if self.level == 5:
					if noTest:
						player.updateStatusEffects(0.2, "health percentage", self.name)
			
			if  self.name == "Slowing Aura":
				if self.level > 1:
					self.value += 0.1
				if noTest:
					self.setHitbox(player.position, self.value * 5 + 49 + 50 * self.level)

			if self.name == 'Enhanced Wisdom':
				if self.level > 1:
					self.value += 0.08
	
	def getUpgradeValues(self, player):
		tempValue, tempCooldown = self.value, self.cooldown_max
		self.upgradeItem(player, 1, False)
		self.level -= 1
		diffValue, diffCooldown = self.value - tempValue, self.cooldown_max - tempCooldown
		self.value, self.cooldown_max = tempValue, tempCooldown
		return diffValue, diffCooldown

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
		self.points: List[pygame.Vector2] = []

	def addRotation(self, rotation):
		self.rotation = rotation
		
	def addAnimationRotation(self, rotation):
		self.animation_rotation = rotation

	def getLinePoints(self, destination: pygame.Vector2, original: pygame.Vector2):
		points_list: List[pygame.Vector2] = []

		dx = destination.x - original.x
		dy = destination.y - original.y
		steps = round(max(abs(dx), abs(dy))/17) + 1
		x_increment = dx / steps
		y_increment = dy / steps

		x, y = original.x, original.y
		for _ in range(steps + 1):
			points_list.append(pygame.Vector2(x, y))
			x += x_increment
			y += y_increment
		return points_list

class Weapon(GameObject):
	def __init__(self, name: str, cooldown_max: float, dmgtype: str, pattern: str, colour: str, size: int, speed: int, bulletlifetime: Union[int, str], range: int, charge: int, damage: float, pierce: float, position: pygame.Vector2, slow: float, knockback: float, weaken: float):
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

		super().__init__(objtype, position, width_and_height, width_and_height)

		self.range = range

		if self.name == "Homing Arrow":
			self.pathlist: List[pygame.Vector2] = []
		
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

		dirname = os.path.dirname(__file__)
		filename = os.path.join(dirname, '../../assets/audio/'+self.name+' Sound.wav')
		if os.path.isfile(filename):
			self.sound = pygame.mixer.Sound(filename)
		else:
			self.sound = None

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

					if self.name == 'Laser Beam':
						self.damage += 0.35
						self.range += 125
						self.size += 3
						self.cooldown_max -= 0.125
						self.bulletLifeTime += 0.8

					if self.name == 'Energy Sword':
						self.damage += 5
						self.range += 65
						self.size += 20
						self.bulletLifeTime += 0.02
						self.cooldown_max -= 0.1

	
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

	def __init__(self, position: pygame.Vector2, level = 1, radius: float = 30, health: float = 30, colour = "red", damage: float = 10, speed: float = 10, weakness = "energy", type = "normal", event_type = None, targetable = True):
		objtype = "enemy"
		super().__init__(objtype, position, radius * 2, radius * 2)

		self.position_original = pygame.Vector2(position.x, position.y)
		self.position_destination = pygame.Vector2(0,0)
		self.level = level
		self.event_type = event_type
		if self.level > 30:
			if event_type != 'group':
				self.level = 30
		if self.event_type == None or self.event_type == 'group':
			scale = self.level - 1
		else:
			scale = 0
		self.radius = radius
		self.health = health + scale * 5 * 3**(scale//9)
		self.colour = colour
		self.fixedcolour = colour
		self.damage = damage + scale * 1 + 2**(scale//9)
		self.speed = speed + scale * 2 + 2**(scale//9)
		self.weakness = weakness
		self.type = type
		self.targetable = targetable
		
		self.hitCooldown = 0
		self.hitSoundCooldown: float = 0


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