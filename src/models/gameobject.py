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
		if self.objtype in ["enemy", "player", "experience"] or (self.objtype == "bullet" and self.weaponname == "Damaging Field"):
			self.radius = self.width / 2
			self.rect = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.width, self.height)
		else:
			self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
	
	def setHitbox(self):
		pass
	
	def setPositionBasedOnMovement(self, speed, dt, gate, rate = 1):
		keys = pygame.key.get_pressed()
		#TODO: CHECK WHAT HAPPENS WHEN >2 BUTTONS ARE PRESSED

		if keys[pygame.K_w] and keys[pygame.K_a] and "up" not in gate and "left" not in gate:
			self.position.y += speed * dt / 2**(1/2) * rate
			self.position.x += speed * dt / 2**(1/2) * rate

		elif keys[pygame.K_w] and keys[pygame.K_d] and "up" not in gate and "right" not in gate:
			self.position.y += speed * dt / 2**(1/2) * rate
			self.position.x -= speed * dt / 2**(1/2) * rate

		elif keys[pygame.K_w] and "up" not in gate:
			self.position.y += speed * dt * rate

		elif keys[pygame.K_s] and keys[pygame.K_a] and "down" not in gate and "left" not in gate:
			self.position.y -= speed * dt / 2**(1/2) * rate
			self.position.x += speed * dt / 2**(1/2) * rate

		elif keys[pygame.K_s] and keys[pygame.K_d] and "down" not in gate and "right" not in gate:
			self.position.y -= speed * dt / 2**(1/2) * rate
			self.position.x -= speed * dt / 2**(1/2) * rate

		elif keys[pygame.K_s] and "down" not in gate:
			self.position.y -= speed * dt * rate

		elif keys[pygame.K_a] and "left" not in gate:
			self.position.x += speed * dt * rate

		elif keys[pygame.K_d] and "right" not in gate:
			self.position.x -= speed * dt * rate
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
		self.experience_max: int = 150
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
		if self.experience_queue > 0:
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
	def __init__(self, name, value, cooldown, count = 0):
		self.name = name
		self.level = 0
		self.value = value
		self.cooldown_max = cooldown
		self.cooldown_current = 0
		self.count = count
		self.description = self.getDescription()

		self.loadImages()
	
	def loadImages(self):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filename_weapon = os.path.join(dirname, '../../media/images/passives/')
			self.image_base = pygame.image.load(filename_weapon + "/"+str(self.name)+"_1.jpg").convert_alpha()
			self.image_maxed = pygame.image.load(filename_weapon + "/"+str(self.name)+"_2.jpg").convert_alpha()
	
	def updateCooldown(self, dt):
		if self.cooldown_current > 0:
			self.cooldown_current -= dt
		if self.cooldown_current < 0:
			self.cooldown_current = 0
	
	def setHitbox(self, position: pygame.Vector2, radius):
		self.position = position
		self.radius = radius
		self.rect = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.radius * 2, self.radius * 2)
	
	def upgradeItem(self, player: PlayerCharacter, amount = 1):	#TODO: IMPLEMENT AMOUNT
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
		filename_passive = os.path.join(dirname, '../../media/descriptions/passives.txt')
		with open(filename_passive, "r") as f:
			cont = {}
			[cont.update(eval(line)) for line in f.readlines()]
		return eval(cont[self.name])
	
class Bullet(GameObject):
	def __init__(self, weaponnanme: str, position: pygame.Vector2, position_original: pygame.Vector2, position_destination: pygame.Vector2, lifetime: float, damage: float, crit: bool, objtype: str, width_and_height: int):
		self.weaponname = weaponnanme
		super().__init__(objtype, position, width_and_height, width_and_height)
		#self.position = position
		self.position_original = position_original
		self.position_destination = position_destination
		self.lifeTime: float = lifetime
		self.damage: float = damage
		self.crit: bool = crit

		self.enemiesHit: List[Enemy] = []

	def addRotation(self, rotation):
		self.rotation = rotation
		
	def addAnimationRotation(self, rotation):
		self.animation_rotation = rotation

class Weapon(GameObject):
	def __init__(self, name: str, cooldown_max: float, dmgtype: str, pattern: str, colour: str, size: int, speed: int, bulletlifetime: Union[int, str], damage: float, position: pygame.Vector2, slow: float, knockback: float, weaken: float):
		objtype = "weapon"
		self.pattern: str = pattern
		self.name: str = name
		if self.name == "Energy Orb" or self.name == "Boomerang" or self.name == "Attack Drone":
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

		if self.name == "Damaging Field":
			self.range = 800
		
		if self.name == "Cluster Bombs":
			self.bomb_damage = 10
			self.bomb_range = 50
			self.bomb_count = 10
			self.bullet_size = 10
		
		self.status_effects = {"slow":slow, "knockback":knockback, "weaken":weaken}

		super().__init__(objtype, position, width_and_height, width_and_height)

		self.cooldown_max: float = cooldown_max
		self.cooldown_current: float = cooldown_max
		self.dmgtype: str = dmgtype
		self.level = 0
		self.colour: str = colour
		self.size: int = size
		self.speed: int = speed
		self.bulletLifeTime = bulletlifetime
		self.damage = damage
		self.bullets: pygame.sprite.Group[Bullet] = pygame.sprite.Group()
		self.position_original = pygame.Vector2(position.x, position.y)
		self.position_destination = pygame.Vector2(0,0)
		self.animation = False
		self.description = self.getDescription()

		self.loadImages()
	
	def getDescription(self):
		dirname = os.path.dirname(__file__)
		filename_desc = os.path.join(dirname, '../../media/descriptions/weapons.txt')
		with open(filename_desc, "r") as f:
			cont = {}
			[cont.update(eval(line)) for line in f.readlines()]
		return eval(cont[self.name])
	
	def loadImages(self):
		if pygame.get_init():
			dirname = os.path.dirname(__file__)
			filename_weapon = os.path.join(dirname, '../../media/images/weapons/')
			self.image_base = pygame.image.load(filename_weapon + "/"+str(self.name)+"_1.jpg").convert_alpha()
			self.image_maxed = pygame.image.load(filename_weapon + "/"+str(self.name)+"_2.jpg").convert_alpha()
			if self.name == "Flamethrower":
				filename_projectile = os.path.join(dirname, '../../media/images/projectiles/')
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
						if self.level == 3:
							self.pattern = "multiple straight"
						if self.level == 5:
							self.damage += 15
							self.speed -= 3
					
					if self.name == "Flamethrower":
						self.cooldown_max -= 0.075
						self.speed -= (2 - self.level)
						self.size += 1
						self.damage -= 9
						self.bulletLifeTime -= 0.004 * self.level
						if self.level == 5:
							self.bulletLifeTime -= 0.02

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
							self.damage += 1
					
					if "cluster" in self.pattern:
						self.cooldown_max -= 0.25
						self.bulletLifeTime += 5
						self.size += 3
						self.damage += 7
						self.bomb_damage += 5
						self.bomb_count += 4
						self.bomb_range += 22
						self.bullet_size += 3
					
					if "circle" in self.pattern:
						self.speed *= 1.1
						self.size += 5
						self.distance += 50
					
					if "angled" in self.pattern:
						self.cooldown_max -= 0.425
						self.damage += 10
						self.size += 3
						self.speed += 2
						if self.level >= 4:
							self.size += 2
							self.speed += 1
						if self.level == 5:
							self.damage += 5
					
					if "pet" in self.pattern:
						if self.level > 1:
							self.damage += 0.2 * self.level
							self.range += 50
							self.speed += 10
							self.size += 2.5
							
						if self.level == 5:
							self.range += 50
	
	def getClusters(self, bullet: Bullet):
		b = []
		r = self.bomb_count
		for i in range(r):
			angle = 360 / r
			destination = pygame.Vector2(bullet.position.x + self.bomb_range * math.cos(i * angle * math.pi / 180), bullet.position.y + self.bomb_range * math.sin(i * angle * math.pi / 180))
			position = pygame.Vector2(bullet.position.x, bullet.position.y)
			b.append(Bullet("Cluster Bombs", position, position, destination, 8 + (self.level - 1), self.bomb_damage, False, "bullet mine", self.bullet_size))
		return b

class Enemy(GameObject):
	def __init__(self, position: pygame.Vector2, level = 1, radius: float = 20, health: float = 30, colour = "red", damage: float = 10, speed: float = 10, weakness = "energy", type = "normal"):
		objtype = "enemy"
		width_and_height = radius * 2
		super().__init__(objtype, position, width_and_height, width_and_height)

		self.position_original = pygame.Vector2(position.x, position.y)
		self.position_destination = pygame.Vector2(0,0)
		self.level = level
		if self.level > 21:
			self.level = 21
		self.radius = radius + (self.level - 1) * 1.25
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
	
	def setMinDistance(self, dist):
		self.min_distance = dist

class WeaponKit(GameObject):
	def __init__(self, randpos, width = 50, height = 50):
		objtype = "weaponkit"
		super().__init__(objtype, randpos, width, height)

class Magnet(GameObject):
	def __init__(self, randpos, width, height):
		objtype = "magnet"
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


	def openInGameMenu(self, screen, screen_width: int, screen_height: int, paused):
		if pygame.get_init():

			dirname = os.path.dirname(__file__)
			filename = os.path.join(dirname, '../../media/images/buttons/')
			resume_img = pygame.image.load(filename+"/button_resume.png").convert_alpha()
			options_img = pygame.image.load(filename+"/button_options.png").convert_alpha()
			quit_img = pygame.image.load(filename+"/button_quit.png").convert_alpha()
			video_img = pygame.image.load(filename+"/button_video.png").convert_alpha()
			audio_img = pygame.image.load(filename+"/button_audio.png").convert_alpha()
			keys_img = pygame.image.load(filename+"/button_keys.png").convert_alpha()
			back_img = pygame.image.load(filename+"/button_back.png").convert_alpha()

			#create button instances
			resume_button = Button(screen_width/2 - resume_img.get_width()/2, screen_height/4 + 125, resume_img, 1)
			options_button = Button(screen_width/2 - options_img.get_width()/2, screen_height/4 + 250, options_img, 1)
			quit_button = Button(screen_width/2 - quit_img.get_width()/2, screen_height/4 + 375, quit_img, 1)
			video_button = Button(screen_width/2 - video_img.get_width()/2, screen_height/4 + 75, video_img, 1)
			audio_button = Button(screen_width/2 - audio_img.get_width()/2, screen_height/4 + 200, audio_img, 1)
			keys_button = Button(screen_width/2 - keys_img.get_width()/2, screen_height/4 + 325, keys_img, 1)
			back_button = Button(screen_width/2 - back_img.get_width()/2, screen_height/4 + 450, back_img, 1)

			#game loop
			run = True
			while run:
				window = pygame.Rect(screen_width/4, screen_height/4, screen_width/2, screen_height/2)
				pygame.draw.rect(screen, (52, 78, 91), window)

				#check if game is paused
				if paused == True:
					#check menu state
					if self.state == "ingame":
						#draw pause screen buttons
						if resume_button.draw(screen):
							paused = False
							return "closed"
						if options_button.draw(screen):
							self.state = "options"
						if quit_button.draw(screen):
							run = False
							pygame.quit()
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

	def openItemSelectorMenu(self, screen: pygame.Surface, screen_width: int, screen_height: int, paused: bool, itemlist: List[Union[Weapon, Passive]]):
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

				# Check if game is paused
				if paused:
					# Check menu state
					if self.state == "weapon_selector" or self.state == "passive_selector":
						# Draw item selection buttons
						if len(itemlist) > 0:
							if item_button1.draw(screen) or text_button1.drawText(screen):
								paused = False
								return ["closed", itemlist[0]]
						if len(itemlist) > 1:
							if item_button2.draw(screen) or text_button2.drawText(screen):
								paused = False
								return ["closed", itemlist[1]]
						if len(itemlist) > 2:
							if item_button3.draw(screen) or text_button3.drawText(screen):
								paused = False
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
	
	def draw(self, surface):
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