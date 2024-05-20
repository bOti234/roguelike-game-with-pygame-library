import pygame
import os
import math
import time
import random
import pandas
from typing import List, Dict, Union
from .player import User
from .gamesettings import GameSettings
from .gameobject import PlayerCharacter, Passive, Weapon, Bullet, Enemy, Experience, WeaponKit, HealthKit, Magnet, HUD, Inventory, Menu
from ..utils.database import submit_score

# Example of submitting a new score
# submit_score('Player1', 5000)

class Game():
	def __init__(self):
		self.difficultylist: List[str] = ["easy","normal","hard"]
		self.speedlist: List[str] = ["slow","normal","fast"]
		self.players: List[User] = []
		self.scoreboard: List[int] = []
	
	def setSpeed(self, speed: str) -> int:
		if speed in self.speedlist:
			if speed == "slow":
				return 300
			if speed == "normal":
				return 400
			if speed == "fast":
				return 500
		else:
			return 400
	
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
		self.player = PlayerCharacter(player_radius, player_position, 50, self.settings.speed)

		self.background: pygame.Vector2  = pygame.Vector2(self.player.position.x, self.player.position.y)

		self.passivelist = self.getPassives()
		self.player_passives: Dict[str, Passive] = {}

		# passive = [passive for passive in self.passivelist if passive.name == "Slowing Aura"][0]		# This is just for testing / later with game modificators
		# self.player_passives.update({passive.name: passive})
		# self.player_passives[passive.name].upgradeItem(self.player, 5)

		self.weaponlist = self.getWeapons()
		self.player_weapons: Dict[str, Weapon] = {}
		#   I'm making this a dicitonary instead of a list. When iterating through it, it costs more as a list, but when I need a specific weapon, I can just get the value with the weapon's name as the key.
		#   That is apparently not an iteration so it's more effective than the aforementioned method.

		if len(self.weaponlist) > 0:
			self.player_weapons.update({self.weaponlist[0].name: self.weaponlist[0]})
			self.player_weapons[self.weaponlist[0].name].upgradeItem(amount = 1)

		self.bulletGroup: pygame.sprite.Group[Bullet] = pygame.sprite.Group()
		self.ItemGroup: pygame.sprite.Group[Union[WeaponKit, HealthKit, Magnet]] = pygame.sprite.Group()
		self.EnemyGroup: pygame.sprite.Group[Enemy] = pygame.sprite.Group()
		self.experienceGroup: pygame.sprite.Group[Experience] = pygame.sprite.Group()

		self.ItemGroup.add(WeaponKit(pygame.Vector2(self.player.position.x + 200, self.player.position.y + 200)))

		self.WeaponKitCooldown = 0
		self.MagnetCooldown = 0
		self.EnemyCooldown = 0

		self.time = 0
	
	def getPassives(self):
		# reach = Passive(   #TODO:
		#     name = "Increased Reach",
		#     value = 1,
		#     cooldown = 0
		# )

		# warcry = Passive(   #TODO:
		#     name = "Taunting Warcry",
		#     value = 1,
		#     cooldown = 0
		# )

		# crowdcontrol = Passive(   #TODO:
		#      name = "Crowd Control",
		#      value = 1,
		#      cooldown = 0
		# )
		dirname = os.path.dirname(__file__)
		filepath_pasive = os.path.join(dirname, "../../assets/instances/")
		passivelist = []
		table = pandas.DataFrame(pandas.read_csv(filepath_pasive+"/passives.csv"))
		for i, row in table.iterrows():
			passive = Passive(
				name = row['name'],
				value = float(row['value']),
				cooldown = int(row['cooldown']),
			)
			passivelist.append(passive)
		return passivelist

	def getWeapons(self):
		dirname = os.path.dirname(__file__)
		filepath_weapon = os.path.join(dirname, "../../assets/instances/")
		weaponlist = []
		table = pandas.DataFrame(pandas.read_csv(filepath_weapon+"/weapons.csv"))
		for i, row in table.iterrows():
			position = pygame.Vector2(float(eval(row['position'].split('(')[1].split(',')[0])), float(eval(row['position'].split(' ')[1][:-1])))
			weapon = Weapon(
				name = row['name'],
				cooldown_max = float(row['cooldown_max']),
				dmgtype = row['dmgtype'],
				pattern = row['pattern'],
				colour = row['colour'],
				size = int(row['size']),
				speed = int(row['speed']),
				bulletlifetime = float(row['bulletlifetime']) if row['bulletlifetime'] != 'inf' else str('inf'),
				charge = int(row['charge']),
				damage = float(row['damage']),
				pierce = int(row['pierce']),
				position = position,
				slow = float(row['slow']),
				knockback = float(row['knockback']),
				weaken = float(row['weaken'])
			)
			weaponlist.append(weapon)

		return weaponlist

	def openMainMenu(self):
		if not pygame.get_init():
			pygame.init()
			self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), pygame.HWSURFACE)
			pygame.display.set_caption("Epic roguelike game")
			self.traspscreen = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
		pygame.mouse.set_cursor(pygame.cursors.arrow)
		menu = Menu()
		menu.state = "inMainMenu"
		response = menu.openMainMenu(self.screen, self.settings.screen_width, self.settings.screen_height)
		if response == "start game":
			self.gameRun()
		elif response == "exit":
			self.running = False
			pygame.quit()

	def openInGameMenu(self):
		pygame.mouse.set_cursor(pygame.cursors.arrow)
		menu = Menu()
		menu.state = "ingame"
		response = menu.openInGameMenu(self.screen, self.settings.screen_width, self.settings.screen_height)
		if response == "closed":
			self.gameRun()
		elif response == "return to main menu":
			self.openMainMenu()

	def openSelectWeaponMenu(self):
		pygame.mouse.set_cursor(pygame.cursors.arrow)
		weaponlist = self.getRandomWeapons()
		if len(weaponlist) > 0:
			menu = Menu()
			menu.state = "weapon_selector"
			response, weapon = menu.openItemSelectorMenu(self.screen, self.settings.screen_width, self.settings.screen_height, weaponlist)
			if isinstance(weapon, Weapon):
				self.writeOnScreen(weapon.name, 0, 200)
				weapon.upgradeItem(self.player, 1)
				if weapon not in self.player_weapons.values():
					self.player_weapons.update({weapon.name : weapon})
			if response == "closed":
				self.gameRun()
		else:
			self.gameRun()
	
	def getRandomWeapons(self):
		upgradeableWeapons = [weapon for weapon in self.weaponlist if weapon.level < 5]
		if len(upgradeableWeapons) >= 3:
			return random.sample(upgradeableWeapons, 3)
		return upgradeableWeapons
	
	def openLevelUpMenu(self, n = 1):
		pygame.mouse.set_cursor(pygame.cursors.arrow)
		for i in range(n):
			passivelist = self.getRandomPasives()
			if len(passivelist) > 0:
				menu = Menu()
				menu.state = "passive_selector"
				response = menu.openItemSelectorMenu(self.screen, self.settings.screen_width, self.settings.screen_height, passivelist)
				if isinstance(response[1], Passive):
					response[1].upgradeItem(self.player, 1)
					if response[1] not in self.player_passives.values():
						self.player_passives.update({response[1].name: response[1]})
				if response[0] == "closed" and i == n - 1:
					self.gameRun()
				elif i != n - 1:
					window = pygame.Rect(self.settings.screen_width / 4 - 200, self.settings.screen_height / 4, self.settings.screen_width / 2 + 400, self.settings.screen_height / 2)
					pygame.draw.rect(self.screen, (52, 78, 91), window)
			else:
				self.gameRun()

	def getRandomPasives(self):
		upgradeablePassives = [passive for passive in self.passivelist if passive.level < 5]
		if len(upgradeablePassives) >= 3:
			return random.sample(upgradeablePassives, 3)
		return upgradeablePassives
	
	def openDeathMenu(self):
		pass
	
	def gameRun(self):
		#pygame.init()
		pygame.mouse.set_cursor(pygame.cursors.broken_x)
		self.getBackgroundImage()

		clock = pygame.time.Clock()
		self.running = True
		self.dt = 0

		while self.running:
			# poll for events
			# pygame.QUIT event means the user clicked X to close your window
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False

			mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) # Get mouse pos

			self.drawBackground() # Draw background and border of the map

			
			self.transparentCycle()
			self.screen.blit(self.traspscreen, (0,0))	#	-> This goes after the transparentcycle and every transparent object also goes there
			self.attackCycle(mouse_pos)    # Drawing the weapon attacks
			self.passiveCycle()
			
			self.drawPlayer()

			self.checkHitboxes()

			self.spawnWeaponKit()
			self.spawnMagnet()
			self.spawnEnemies()

			self.updateItemPosition()
			self.updatePointingArrowPosition()
			self.updateEnemyPosition()
			self.updateExperiencePosition()

			self.writeOnScreen(str(mouse_pos.x)+" "+str(mouse_pos.y), mouse_pos.x, mouse_pos.y)  # Write some stuff on the self.screen
			self.writeOnScreen(str(round(self.time)//60)+":"+str(round(self.time - 60 * (self.time // 60))), self.settings.screen_width/2 - 13, 10)  # Write some stuff on the self.screen
			self.writeOnScreen(str(self.player.experience_current)+" / "+str(self.player.experience_max), 0, 200)  # Write some stuff on the self.screen

			self.drawStatBoxes()
			
			self.checkKeysPressed() # Update background position based on player movement

			pygame.display.flip() # flip() the display to put your work on self.screen
			

			self.dt = clock.tick(self.settings.fps) / 1000 # self.dt is delta time in seconds since last frame
			self.time += self.dt
		
		pygame.quit()

	def drawPlayer(self):
		pygame.draw.rect(self.screen, "blue", self.player.rect)
		if self.player.hitCooldown > 0:     # Draw player with diff colour based on if they were hit recently or not
			self.player.hitCooldown -= self.dt
			pygame.draw.circle(self.screen, "darkmagenta", (self.player.position.x, self.player.position.y), self.player.radius) 
		else:
			pygame.draw.circle(self.screen, "skyblue", (self.player.position.x, self.player.position.y), self.player.radius)

		n = self.player.updateExperience()
		if n > 0:
			self.openLevelUpMenu(n)
			
	
	def drawStatBoxes(self):
		hp_rect_border = pygame.Rect(self.player.position.x - self.player.radius, self.player.position.y + 55, self.player.width , 10)
		hp_rect = pygame.Rect(self.player.position.x - self.player.radius + 4, self.player.position.y + 55 + 3, (self.player.width - 4) * self.player.health_current / self.player.health_max, 10 - 6)
		hp_rect_missing = pygame.Rect(self.player.position.x + self.player.radius, self.player.position.y + 55 + 3, -(self.player.width - 4) * (1 - (self.player.health_current / self.player.health_max)), 10 - 6)
		
		if "Protective Barrier" in self.player_passives.keys(): # NOOO THIS IS AN ITERATION AS WELLLL
			barrier = self.player_passives["Protective Barrier"]
			barrier_rect = pygame.Rect(self.player.position.x - self.player.radius + 4, self.player.position.y + 55 + 3, (self.player.width - 4) * (barrier.value / self.player.health_max) * self.player.buffs["barrier"] / barrier.value, 10 - 6)
		else:
			barrier = False
		
		pygame.draw.rect(self.screen, "green", hp_rect, 0, 20)
		if barrier != False:
			pygame.draw.rect(self.screen, "blue", barrier_rect, 0, 20)
		pygame.draw.rect(self.screen, "red", hp_rect_missing, 0, 20)
		pygame.draw.rect(self.screen, "black", hp_rect_border, 3, 20)
		self.writeOnScreen(str(self.player.health_max), hp_rect.x, hp_rect.y+10)

		exp_rect_border = pygame.Rect(800, self.settings.screen_height - 100, self.settings.screen_width - 1600 , 25)
		exp_rect = pygame.Rect(800 + 4, self.settings.screen_height - 100 + 4, (self.settings.screen_width - 1600 - 4) * self.player.experience_current / self.player.experience_max , 25 - 8)
		pygame.draw.rect(self.screen, "yellow", exp_rect, 0, 20)
		pygame.draw.rect(self.screen, "black", exp_rect_border, 4, 20)
	
	def getBackgroundImage(self):
		dirname = os.path.dirname(__file__)
		filename_background = os.path.join(dirname, '../../assets/images/background/')
		image = pygame.image.load(filename_background + "/background_image.png").convert_alpha()
		self.backgroundimage = pygame.transform.scale(image, (int(image.get_rect().width * 3), int(image.get_rect().height * 3)))

	def drawBackground(self):
		# fill the self.screen with a color to wipe away anything from last frame
		self.screen.fill("#124a21")
		self.traspscreen.fill((18, 74, 33, 0))
		image_rect = self.backgroundimage.get_rect()
		steps_x = self.background.x // (image_rect.width)
		steps_y = self.background.y // (image_rect.height)
		
		self.screen.blit(self.backgroundimage, (self.background.x - image_rect.width * (1 + steps_x), self.background.y - image_rect.height * (1 + steps_y)))
		self.screen.blit(self.backgroundimage, (self.background.x - image_rect.width * (1 + steps_x), self.background.y - image_rect.height * (0 + steps_y)))
		self.screen.blit(self.backgroundimage, (self.background.x - image_rect.width * (0 + steps_x), self.background.y - image_rect.height * (1 + steps_y)))
		self.screen.blit(self.backgroundimage, (self.background.x - image_rect.width * (0 + steps_x), self.background.y - image_rect.height * (0 + steps_y)))


	def notTouchingBorder(self):
		# li = []
		# if (self.background.x - self.settings.screen_width + self.settings.game_size**2*2 - self.player.radius + 300 * self.dt)  <= self.player.position.x:
		# 	li.append(False)
		# 	li.append("right")
		# if (self.background.x - self.settings.screen_width + self.player.radius + 300 * self.dt)  >= self.player.position.x:
		# 	li.append(False)
		# 	li.append("left")
		# if (self.background.y - self.settings.screen_height + self.player.radius + 300 * self.dt)  >= self.player.position.y:
		# 	li.append(False)
		# 	li.append("up")
		# if (self.background.y - self.settings.screen_height + self.settings.game_size**2*2 - self.player.radius + 300 * self.dt)  <= self.player.position.y:
		# 	li.append(False)
		# 	li.append("down")
		# if len(li) == 0:
		# 	li = [True, "nothing"]
		# return list(set(li))
		pass
	
	def checkKeysPressed(self, rate = 1):
		keys = pygame.key.get_pressed()
		#gate = self.notTouchingBorder()
		if self.running:
			if keys[pygame.K_w]:# and "up" not in gate:
				self.background.y += self.settings.speed * self.dt * rate

			if keys[pygame.K_s]:# and "down" not in gate:
				self.background.y -= self.settings.speed * self.dt * rate

			if keys[pygame.K_a]:# and "left" not in gate:
				self.background.x += self.settings.speed * self.dt * rate

			if keys[pygame.K_d]:# and "right" not in gate:
				self.background.x -= self.settings.speed * self.dt * rate

			if [keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d]].count(True) == 2:
				if keys[pygame.K_w] and keys[pygame.K_a]:# and "up" not in gate and "left" not in gate:
					self.background.y += self.settings.speed * rate * ( self.dt / 2**(1/2) -  self.dt)
					self.background.x += self.settings.speed * rate * ( self.dt / 2**(1/2) -  self.dt)

				if keys[pygame.K_w] and keys[pygame.K_d]:# and "up" not in gate and "right" not in gate:
					self.background.y += self.settings.speed * rate * ( self.dt / 2**(1/2) -  self.dt)
					self.background.x -= self.settings.speed * rate * ( self.dt / 2**(1/2) -  self.dt)

				if keys[pygame.K_s] and keys[pygame.K_a]:# and "down" not in gate and "left" not in gate:
					self.background.y -= self.settings.speed * rate * ( self.dt / 2**(1/2) -  self.dt)
					self.background.x += self.settings.speed * rate * ( self.dt / 2**(1/2) -  self.dt)

				if keys[pygame.K_s] and keys[pygame.K_d]:# and "down" not in gate and "right" not in gate:
					self.background.y -= self.settings.speed * rate * ( self.dt / 2**(1/2) -  self.dt)
					self.background.x -= self.settings.speed * rate * ( self.dt / 2**(1/2) -  self.dt)

		if keys[pygame.K_ESCAPE]:
			if self.running:
				self.openInGameMenu()

	def checkHitboxes(self):
		self.writeOnScreen(str(self.player.position.x)+" "+str(self.player.position.y), self.player.position.x, self.player.position.y)
		for item in self.ItemGroup:
			if pygame.sprite.collide_rect(item, self.player):   # This is the best feature ever, although, my player is a circle and the boxes are squares...
				item.kill()
				if item.objtype == "weaponkit":
					response = self.openSelectWeaponMenu()
				elif item.objtype == "healthkit":
					self.player.health_current += 10
					if self.player.health_current > self.player.health_max:
						self.player.health_current = self.player.health_max
				elif item.objtype == "magnet":
					for exp in self.experienceGroup:
						exp.setMinDistance(10000)	
		
		for bullet in self.bulletGroup:
			for enemy in self.EnemyGroup:
				if pygame.sprite.collide_rect(bullet, enemy):
					self.damageEnemy(bullet, enemy)
		for enemy in self.EnemyGroup:
			if pygame.sprite.collide_circle(self.player, enemy):
				if self.player.hitCooldown <= 0:
					self.player.hitCooldown = 1
					if self.player.buffs["dodge count"] > 0 and random.random() >= 0.75:
						self.player.buffs["dodge count"] -= 1
					else:
						damageperc = 1
						for weaponname, attr in [(weaponname, attr) for weaponname, attr in enemy.status_effects.items() if weaponname in self.player_weapons.keys()]:
							weapon = self.player_weapons[weaponname]
							if attr["active"]:
								damageperc *= (1 - weapon.status_effects["weaken"])
						if "Berserk" in self.player_passives.keys():	#TODO: make it usable with more buffs/nerfs for enemy damage.
							damageperc *= (1 + self.player_passives["Berserk"].value)
						if self.player.buffs["barrier"] >= enemy.damage * damageperc:
							self.player.buffs["barrier"] -= enemy.damage * damageperc
						else:
							remainder = enemy.damage * damageperc - self.player.buffs["barrier"]
							self.player.buffs["barrier"] = 0
							self.player.health_current -= remainder
					if self.player.health_current <= 0:
						self.openDeathMenu()
		
		for exp in self.experienceGroup:
			if pygame.sprite.collide_circle(exp, self.player):
				self.player.experience_queue += int(exp.value)
				exp.kill()

	def damageEnemy(self, bullet: Bullet, enemy: Enemy):
		weapon = self.player_weapons[bullet.weaponname]
		if bullet.weaponname == "Damaging Field":
			if enemy.hitCooldown <= 0:
				#self.writeOnScreen(str(enemy.status_effects[weapon.name]), bullet.position.x, bullet.position.y)
				enemy.status_effects[weapon.name].update({"active":True})
				enemy.status_effects[weapon.name].update({"duration":0.2})
				enemy.health -= bullet.damage
				enemy.hitCooldown = 0.1
		elif enemy not in bullet.enemiesHit:
			bullet.pierce -= 1
			if bullet.crit:
				critState = 2
			else:
				critState = 1
			flatbuff = sum([0]+[val for val in self.player.buffs["damage flat"].values()])
			percbuff = math.prod([1 + val for val in self.player.buffs["damage percentage"].values()]) * critState
			enemy.health -= (bullet.damage + flatbuff) * (1 + weapon.status_effects["weaken"]) * percbuff
			bullet.enemiesHit.append(enemy)
			enemy.hitCooldown = 0.5
			enemy.status_effects[weapon.name].update({"active":True})
			enemy.status_effects[weapon.name].update({"duration":0.2})
			if bullet.weaponname == "Cluster Bombs" and "mine" not in bullet.objtype:
				b = weapon.getClusters(bullet)
				weapon.bullets.add(b)
				self.bulletGroup.add(b)
				bullet.kill()
			elif bullet.weaponname == "Scatter Rifle" and "scatter" not in bullet.objtype and bullet.pierce == 0:
				b = weapon.getScatters(bullet)
				weapon.bullets.add(b)
				self.bulletGroup.add(b)
				bullet.kill()
			elif bullet.objtype == "bullet mine":
				bullet.kill()
			elif bullet.pierce == 0:
				bullet.kill()
				
		if enemy.health <= 0:
			# if enemy in self.EnemyGroup:
			self.spawnEnemyDrops(enemy)
			enemy.kill()
			if bullet.weaponname == "Attack Drone":
				bullet.kill()


	def spawnWeaponKit(self):
		if len([weapon for weapon in self.weaponlist if weapon.level < 5]) > 0:
			if self.WeaponKitCooldown <= 0:
				chance = random.random()
				if chance > 0.5:
					randpos = pygame.Vector2(
						random.randint(round(self.player.position.x + 250), round(self.player.position.x + 500)) * self.getSign(), 
						random.randint(round(self.player.position.y + 250), round(self.player.position.y + 500)) * self.getSign()
						)
					kit = WeaponKit(randpos)
					self.ItemGroup.add(kit)
					self.WeaponKitCooldown = 70  - (self.time // 30) - self.player.buffs["gunslinger"]
					if self.WeaponKitCooldown < 15:
							self.WeaponKitCooldown = 15
				else:
					self.WeaponKitCooldown = 5
			else:
				self.WeaponKitCooldown -= self.dt
	
	def spawnMagnet(self):
		if self.MagnetCooldown <= 0:
			chance = random.random()
			if chance > 0.25:
				randpos = pygame.Vector2(
						random.randint(round(self.player.position.x + 250), round(self.player.position.x + 500)) * self.getSign(), 
						random.randint(round(self.player.position.y + 250), round(self.player.position.y + 500)) * self.getSign()
						)
				magnet = Magnet(randpos)
				self.ItemGroup.add(magnet)
				self.MagnetCooldown = 120  - (self.time // 30)  #TODO MAKE IT A SETTING/MODIFIER
				if self.MagnetCooldown < 60:
					self.MagnetCooldown = 60
			else:
				self.MagnetCooldown = 10
		else:
			self.MagnetCooldown -= self.dt
	
	def spawnEnemies(self):
		if self.EnemyCooldown <= 0:
			for i in range(10 + int((self.time // 30))):
				chance = random.random()
				if chance > 0.3 - (self.time // 60) * 0.02:

					randpos = pygame.Vector2(
						random.randint(round(self.player.position.x + 500), round(self.player.position.x + 1000)) * self.getSign(), 
						random.randint(round(self.player.position.y + 500), round(self.player.position.y + 1000)) * self.getSign()
						)
					enemy = Enemy(randpos, (self.time // 60) + 1)
					enemy.setStatusDict(self.weaponlist)
					self.EnemyGroup.add(enemy)
					self.EnemyCooldown = 10         #TODO MAKE IT A SETTING/MODIFIER
					if self.EnemyCooldown < 10:
						self.EnemyCooldow = 10
		else:
			self.EnemyCooldown -= self.dt
	
	def spawnEnemyDrops(self, enemy: Enemy):
		chance = random.random()

		if chance < 0.05:
			position = pygame.Vector2(enemy.position.x - enemy.width/2, enemy.position.y - enemy.height/2)
			kit = HealthKit(position)
			self.ItemGroup.add(kit)

		if chance < 0.25 and enemy.type == "miniboss":
			e = Experience(enemy.position, 20, "purple", enemy.level * 5000)
		elif (chance < 1/3 and enemy.type == "brute") or ( chance < 0.9 and enemy.type == "miniboss"):
			e = Experience(enemy.position, 16, "orange", enemy.level * 1000)
		elif chance < 0.2 or enemy.type == "brute" or enemy.type == "miniboss":
			e = Experience(enemy.position, 12, "yellow", enemy.level * 100)
		else:
			e = Experience(enemy.position, 8, "white", enemy.level * 20)

		self.experienceGroup.add(e)
	
	def updateItemPosition(self):
		for item in self.ItemGroup:
			if item.objtype == "weaponkit" or item.objtype == "healthkit":
				item.setPositionBasedOnMovement(self.settings.speed, self.dt)
				rect = pygame.Rect(item.position.x, item.position.y, item.width, item.height)
				pygame.draw.rect(self.screen, item.colour, rect)
				pygame.draw.rect(self.screen, "black", rect, 3)

				if item.objtype == "healthkit":
					if item.lifetime > 0:
						item.lifetime -= self.dt
					else:
						item.kill()

			elif item.objtype == "magnet":
				item.setPositionBasedOnMovement(self.settings.speed, self.dt)
				rect = pygame.Rect(item.position.x, item.position.y, item.width, item.height)
				pygame.draw.arc(self.screen, "black", rect, math.radians(0), math.radians(180), 23)
				pygame.draw.arc(self.screen, "red", rect, math.radians(90), math.radians(180), 20)
				pygame.draw.arc(self.screen, "blue", rect, math.radians(0), math.radians(90), 20)
				pygame.draw.arc(self.screen, "black", rect, math.radians(0), math.radians(180), 3)

				pygame.draw.line(self.screen, "black", (item.position.x + 23/2, item.position.y + item.height / 2), (item.position.x + 23/2, item.position.y + item.height), 20)
				pygame.draw.line(self.screen, "red", (item.position.x + 19/2, item.position.y + item.height / 2), (item.position.x + 19/2, item.position.y + item.height), 19)
				pygame.draw.line(self.screen, "gray50", (item.position.x + 19/2, item.position.y + item.height * 3 / 4), (item.position.x + 19/2, item.position.y + item.height), 19)
				pygame.draw.line(self.screen, "black", (item.position.x + 1, item.position.y + item.height / 2), (item.position.x + 1, item.position.y + item.height), 3)

				pygame.draw.line(self.screen, "black", (item.position.x + item.width - 31/2, item.position.y + item.height / 2), (item.position.x + item.width - 31/2, item.position.y + item.height), 18)
				pygame.draw.line(self.screen, "blue", (item.position.x + item.width - 27/2, item.position.y + item.height / 2), (item.position.x + item.width - 27/2, item.position.y + item.height), 18)
				pygame.draw.line(self.screen, "gray50", (item.position.x + item.width - 27/2, item.position.y + item.height * 3 / 4), (item.position.x + item.width - 27/2, item.position.y + item.height), 18)
				pygame.draw.line(self.screen, "black", (item.position.x + item.width - 6/2, item.position.y + item.height / 2), (item.position.x + item.width - 6/2, item.position.y + item.height), 4)

				pygame.draw.line(self.screen, "black", (item.position.x, item.position.y + item.height), (item.position.x + 20, item.position.y + item.height), 2)
				pygame.draw.line(self.screen, "black", (item.position.x + item.width - 22, item.position.y + item.height), (item.position.x + item.width - 1, item.position.y + item.height), 2)
		
			#self.writeOnScreen(self.screen, str(kit.position.x)+" "+str(kit.position.y), kit.position.x, kit.position.y)

	def updatePointingArrowPosition(self):
		for item in self.ItemGroup:
			distEastBorder = item.position.x - self.screen.get_width()
			distWestBorder = item.position.x
			distNorthBorder = item.position.y
			distSouthBorder = item.position.y - self.screen.get_height()

			
			if not (distEastBorder < 0 and distWestBorder > 0 and distNorthBorder > 0 and distSouthBorder < 0):
				distance = math.sqrt((item.position.x - self.player.position.x)**2 + (item.position.y - self.player.position.y)**2) + 1
				sinus = abs((item.position.y - self.player.position.y)/distance) * self.compare_subtraction(item.position.y, self.player.position.y)
				cosinus = abs((item.position.x - self.player.position.x)/distance) * self.compare_subtraction(item.position.x, self.player.position.x)
				
				PlayerItemDistX = abs(item.position.x - self.player.position.x)
				PlayerItemDistY = abs(item.position.y - self.player.position.y)
				
				PlayerArrowDistY = PlayerItemDistY * (self.settings.screen_width/2 / PlayerItemDistX)	#

				if PlayerArrowDistY > self.settings.screen_height/2:
					PlayerArrowDistX = PlayerItemDistX * (self.settings.screen_height/2 / PlayerItemDistY)
					PlayerArrowDistY = self.settings.screen_height/2
				
				else:
					PlayerArrowDistX = self.settings.screen_width/2
				
				pointA = pygame.Vector2((self.player.position.x + PlayerArrowDistX * self.compare_subtraction(item.position.x, self.player.position.x)), (self.player.position.y + PlayerArrowDistY * self.compare_subtraction(item.position.y, self.player.position.y)))
				pointT = pygame.Vector2((pointA.x-50*cosinus), (pointA.y-50*sinus))												# The foot of the altitude of point A
				pointB = pygame.Vector2((pointT.x + 2/5*(pointA.y - pointT.y)), (pointT.y + -2/5*(pointA.x - pointT.x)))		# Rotating the segment between T and A by 90°
				pointC = pygame.Vector2((pointT.x + -2/5*(pointA.y - pointT.y)), (pointT.y + 2/5*(pointA.x - pointT.x)))		# math rules 😎
				
				pygame.draw.polygon(self.screen, item.colour, [pointA, pointB, pointC])
				pygame.draw.polygon(self.screen, "black", [pointA, pointB, pointC], 5)

	def updateEnemyPosition(self):
		for enemy in self.EnemyGroup:

			enemy.position_original.x = enemy.position.x
			enemy.position_original.y = enemy.position.y
			enemy.position_destination.x = self.player.position.x
			enemy.position_destination.y = self.player.position.y
		
			distance = math.sqrt((enemy.position_destination.x - enemy.position_original.x)**2 + (enemy.position_destination.y - enemy.position_original.y)**2) + 1
			sinus = abs((enemy.position_destination.y - enemy.position_original.y)/distance) * self.compare_subtraction(enemy.position_destination.y, enemy.position_original.y)
			cosinus = abs((enemy.position_destination.x - enemy.position_original.x)/distance) * self.compare_subtraction(enemy.position_destination.x, enemy.position_original.x)

			slowness = 1
			if "Slowing Aura" in self.player_passives.keys():
				aura = self.player_passives["Slowing Aura"]
				if pygame.sprite.collide_circle(aura, enemy):
					slowness *= (1 - aura.value)
			for weaponname, attr in enemy.status_effects.items():
				if attr["active"]:
					weapon = self.player_weapons[weaponname]
					slowness *= (1 - weapon.status_effects["slow"])
					if weapon.status_effects["knockback"] > 0.0:
						slowness = -weapon.status_effects["knockback"]
						break

			enemy.position.x += cosinus * enemy.speed * 0.1 * slowness
			enemy.position.y += sinus * enemy.speed * 0.1 * slowness

			enemy.updateStatusDict(self.dt)

			enemy.setPositionBasedOnMovement(self.settings.speed, self.dt)
			if enemy.hitCooldown > 0:
				enemy.colour = "darkred"
				enemy.hitCooldown -= self.dt
			else:
				enemy.colour = "red"

			if slowness != 1:
				enemy.colour = (125, 0, 64)

			pygame.draw.rect(self.screen, "blue", enemy.rect)		#Enemy hitbox
			pygame.draw.circle(self.screen, enemy.colour, enemy.position, enemy.radius)
			pygame.draw.circle(self.screen, "black", enemy.position, enemy.radius, 3)
			#self.writeOnScreen(self.screen, str(enemy.position.x)+" "+str(enemy.position.y), enemy.position.x, enemy.position.y)
	
	def updateExperiencePosition(self):
		for exp in self.experienceGroup:
			exp.position_destination.x = self.player.position.x
			exp.position_destination.y = self.player.position.y
		
			distance = math.sqrt((exp.position_destination.x - exp.position.x)**2 + (exp.position_destination.y - exp.position.y)**2) + 1

			tempX = exp.position.x
			tempY = exp.position.y
			exp.setPositionBasedOnMovement(self.settings.speed, self.dt)
			

			if distance < exp.min_distance:
				if tempX != exp.position.x or tempY != exp.position.y:
					exp.position.x += (exp.position_destination.x - exp.position.x) * 0.225
					exp.position.y += (exp.position_destination.y - exp.position.y) * 0.225
				else:
					exp.position.x += (exp.position_destination.x - exp.position.x) * 0.075
					exp.position.y += (exp.position_destination.y - exp.position.y) * 0.075

			if exp.colour == "white":	#TEMPORARY
				if exp.r == 254 and exp.g < 254 and exp.b == 0:
					exp.g += 34
					if exp.g >= 254:
						exp.g = 254
				elif  exp.r > 0 and exp.g == 254 and exp.b < 254:
					exp.r -= 34
					if exp.r <= 0:
						exp.r = 0
				elif exp.r == 0 and exp.g == 254 and exp.b < 254:
					exp.b += 34
					if exp.b >= 254:
						exp.b = 254
				elif exp.r == 0 and exp.g > 0 and exp.b == 254:
					exp.g -= 34
					if exp.g <= 0:
						exp.g = 0
				elif exp.r < 254 and exp.g == 0 and exp.b == 254:
					exp.r += 34
					if exp.r >= 254:
						exp.r = 254
				elif exp.r == 254 and exp.g == 0 and exp.b > 0:
					exp.b -= 34
					if exp.b <= 0:
						exp.b = 0
				pygame.draw.circle(self.screen, (exp.r, exp.g, exp.b, 255), exp.position, exp.radius)

			else:
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
	
	def getCrit(self):
		if "Crit Chance" in self.player_passives.keys():
			chance = self.player_passives["Crit Chance"].value
			if random.random() <= chance:
				return True
		return False

	def attackCycle(self, mouse_pos: pygame.Vector2):
		self.writeOnScreen(" ".join([key for key in self.player_weapons.keys()]))
		for weapon in self.player_weapons.values():
			if weapon.name == "Flamethrower" and weapon.image_projectile == None:
				weapon.loadImages()
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

				weapon.setPositionBasedOnMovement(self.settings.speed, self.dt , 0.55)

			if weapon.name == "Homing Arrow":
				weapon.position_original.x = weapon.position.x
				weapon.position_original.y = weapon.position.y
				tempX = weapon.position.x
				tempY = weapon.position.y
				weapon.setPositionBasedOnMovement(self.settings.speed, self.dt)
				for pos in weapon.pathlist:
					pos.x += weapon.position.x - tempX
					pos.y += weapon.position.y - tempY

				continue_rotation = False
				closestEnemies: List[Union[Enemy, None]] = self.getClosestEnemy(weapon, 5)
				if closestEnemies:
					closestEnemies = [enemy for enemy in closestEnemies if enemy.hitCooldown <= 0]
					if len(closestEnemies) > 0:
						weapon.position_destination = pygame.Vector2(closestEnemies[0].position.x, closestEnemies[0].position.y)
						if math.sqrt((self.player.position.x - weapon.position_destination.x)**2 + (self.player.position.y - weapon.position_destination.y)**2) + 1 < 1500:
							distance = math.sqrt((weapon.position_destination.x - weapon.position_original.x)**2 + (weapon.position_destination.y - weapon.position_original.y)**2) + 1
							sinus = abs((weapon.position_destination.y - weapon.position_original.y)/distance) * self.compare_subtraction(weapon.position_destination.y, weapon.position_original.y)
							cosinus = abs((weapon.position_destination.x - weapon.position_original.x)/distance) * self.compare_subtraction(weapon.position_destination.x, weapon.position_original.x)

							weapon.position.x += cosinus * weapon.speed
							weapon.position.y += sinus * weapon.speed
						else:
							continue_rotation = True
					else:
						continue_rotation = True
				else:
					continue_rotation = True
				if continue_rotation:
					if weapon.position_destination.x == 0 and weapon.position_destination.y == 0:
						weapon.position_destination.x = self.player.position.x - 100
						weapon.position_destination.y = self.player.position.y - 100

					weapon.position_destination.x = self.player.position.x + 200 * math.cos(weapon.rotation * math.pi / 180)
					weapon.position_destination.y = self.player.position.y - 200 * math.sin(weapon.rotation * math.pi / 180)

					weapon.position.x += (weapon.position_destination.x - weapon.position.x) * 0.035
					weapon.position.y += (weapon.position_destination.y - weapon.position.y) * 0.035
				
				if len(weapon.pathlist) == 20 + weapon.level * 2:
					weapon.pathlist.pop(0)
				weapon.pathlist.append(pygame.Vector2(weapon.position_original.x, weapon.position_original.y))
					
			if weapon.cooldown_current <= 0:
				if weapon.name == "Energy Orb":
					if len(weapon.bullets) < (weapon.level + 1):
						weapon.bullets.empty()
						weapon.rotation = -360 / (weapon.level + 1)
						for ball in range(weapon.level + 1):
							weapon.rotation += 360 / (weapon.level + 1)

							bullet_pos = pygame.Vector2(weapon.position.x, weapon.position.y)
							bullet_pos_original = pygame.Vector2(weapon.position_original.x, weapon.position_original.y)
							bullet_pos_destination = pygame.Vector2(weapon.position_destination.x, weapon.position_destination.y)
							b = Bullet(weapon.name, bullet_pos, bullet_pos_original, bullet_pos_destination, weapon.bulletLifeTime, weapon.damage, weapon.pierce, self.getCrit(), "bullet", weapon.size*2)
							b.addRotation(weapon.rotation)
							weapon.bullets.add(b)
							self.bulletGroup.add(b)
						weapon.setOnCooldown()
				else:
					bullet_pos = pygame.Vector2(weapon.position.x, weapon.position.y)
					bullet_pos_original = pygame.Vector2(weapon.position_original.x, weapon.position_original.y)

					if weapon.name == "Attack Drone" or weapon.name == "Damaging Field":
						if weapon.name == "Damaging Field":
							n = (weapon.level + 1) // 2
						elif weapon.name == "Attack Drone":
							n = weapon.level
						closestEnemies: List[Union[Enemy, None]] = self.getClosestEnemy(weapon, n)
						b = []
						if closestEnemies:
							for enemy in closestEnemies:
								bullet_pos_destination = pygame.Vector2(enemy.position.x, enemy.position.y)
								b.append(Bullet(weapon.name, bullet_pos, bullet_pos_original, bullet_pos_destination, weapon.bulletLifeTime, weapon.damage, weapon.pierce, self.getCrit(), "bullet", weapon.size))
					else:
						bullet_pos_destination = pygame.Vector2(weapon.position_destination.x, weapon.position_destination.y)
						b = Bullet(weapon.name, bullet_pos, bullet_pos_original, bullet_pos_destination, weapon.bulletLifeTime, weapon.damage, weapon.pierce, self.getCrit(), "bullet", weapon.size)
					weapon.setOnCooldown()
					if "angled" in weapon.pattern:
						b.addAnimationRotation(0)
						b.addRotation(weapon.rotation)
					for c in range(weapon.charge_max - 1):
						if random.random() > 0.975 - weapon.level * 0.065:
							weapon.cooldown_current = 0.02
							weapon.charge_current -= 1
						if  weapon.charge_current == 0:
							weapon.charge_current = weapon.charge_max
							weapon.cooldown_current = weapon.cooldown_max

					weapon.bullets.add(b)
					self.bulletGroup.add(b)
			else:
				if weapon.name == "Energy Orb":
					if len(weapon.bullets) < (weapon.level + 1):
						weapon.updateCooldown(self.dt)
				else:
					weapon.updateCooldown(self.dt)
			
			for bullet in weapon.bullets:
				#self.writeOnScreen(str(bullet.crit), bullet.position.x, bullet.position.y) #Writing if the bullet is crit or not
				if bullet.weaponname == "Homing Arrow":
					if isinstance(bullet.lifeTime, float):
						if bullet.lifeTime <= 0:
							bullet.remove(weapon.bullets)
							bullet.kill()
						else:
							bullet.lifeTime -= self.dt

				if "thrown" in weapon.pattern and bullet.weaponname != "Damaging Field":
					if bullet.position_destination.x == 0 and bullet.position_destination.y == 0:
						bullet.position_destination.x = mouse_pos.x
						bullet.position_destination.y = mouse_pos.y

					distance = math.sqrt((bullet.position_destination.x - bullet.position_original.x)**2 + (bullet.position_destination.y - bullet.position_original.y)**2) + 1
										
					sinus = abs((bullet.position_destination.y - bullet.position_original.y)/distance) * self.compare_subtraction(bullet.position_destination.y, bullet.position_original.y)
					cosinus = abs((bullet.position_destination.x - bullet.position_original.x)/distance) * self.compare_subtraction(bullet.position_destination.x, bullet.position_original.x)
					if "mine" in bullet.objtype:
						if math.sqrt((bullet.position.x - bullet.position_original.x)**2 + (bullet.position.y - bullet.position_original.y)**2) + 1 >= distance - 15:
							bullet.position.x = bullet.position_destination.x
							bullet.position.y = bullet.position_destination.y
							bullet.setPositionBasedOnMovement(self.settings.speed, self.dt)
							bullet.position_destination.x = bullet.position.x
							bullet.position_destination.y = bullet.position.y
						else:
							tempX = bullet.position.x
							tempY = bullet.position.y
							bullet.setPositionBasedOnMovement(self.settings.speed, self.dt)
							bullet.position_destination.x += bullet.position.x - tempX
							bullet.position_destination.y += bullet.position.y - tempY
							bullet.position.x += cosinus * weapon.speed * 0.35
							bullet.position.y += sinus * weapon.speed * 0.35
						
					
					elif math.sqrt((bullet.position.x - bullet.position_original.x)**2 + (bullet.position.y - bullet.position_original.y)**2) + 1 >= distance - 10:
						bullet.position.x = bullet.position_destination.x
						bullet.position.y = bullet.position_destination.y
						# bullet.position_original.x = bullet.position_destination.x
						# bullet.position_original.y = bullet.position_destination.y

						#tempX = bullet.position.x
						#tempY = bullet.position.y
						bullet.setPositionBasedOnMovement(self.settings.speed, self.dt )

						bullet.position_destination.x = bullet.position.x# - tempX
						bullet.position_destination.y = bullet.position.y# - tempY
					else:
						# Throw angle/graph: 
						# A parabola that goes through position_original (the player) and position_destination (the mouse). It's concave when the mouse is higher up than the player, it's convex when the mouse is lower.

						# Equation:
						# f(x) = -(bullet.position_destination.y - bullet.position_original.y)/(bullet.position_destination.x - bullet.position_original.x)**2 * (x - bullet.position_destination.x)**2 + bullet.position_destination.y

						bullet.position.x += cosinus * weapon.speed

						if abs(bullet.position_destination.x - bullet.position_original.x) > 100:
							bullet.position.y = -(bullet.position_destination.y - bullet.position_original.y)/(1 + (bullet.position_destination.x - bullet.position_original.x)**2) * (bullet.position.x - bullet.position_destination.x)**2 + bullet.position_destination.y
						else:
							bullet.position.y += sinus * weapon.speed


						tempX = bullet.position.x
						tempY = bullet.position.y
						bullet.setPositionBasedOnMovement(self.settings.speed, self.dt)

						bullet.position_destination.x += bullet.position.x - tempX
						bullet.position_destination.y += bullet.position.y - tempY
						# bullet.position_original.x += bullet.position.x - tempX
						# bullet.position_original.y += bullet.position.y - tempY

					if "mine" in bullet.objtype:
						bullet.rect = pygame.Rect(bullet.position.x, bullet.position.y, bullet.width, bullet.height)
						center = pygame.Vector2(bullet.position.x + bullet.width/2, bullet.position.y + bullet.height/2)
						pygame.draw.circle(self.screen, "black", center, bullet.width/2)
						pygame.draw.circle(self.screen, "red", center, 1)
					elif "cluster" in weapon.pattern:
						bullet.rect = pygame.Rect(bullet.position.x, bullet.position.y, bullet.width, bullet.height)
						pygame.draw.rect(self.screen, weapon.colour, bullet.rect)
						pygame.draw.rect(self.screen, "black", bullet.rect, 3)
				
					if isinstance(bullet.lifeTime, float) or isinstance(bullet.lifeTime, int):
						if bullet.lifeTime <= 0:
							if bullet.weaponname == "Cluster Bombs" and "mine" not in bullet.objtype:
								b = weapon.getClusters(bullet)
								weapon.bullets.add(b)
								self.bulletGroup.add(b)
							bullet.remove(weapon.bullets)
							bullet.kill()
						else:
							if bullet.weaponname == "Cluster Bombs" and "mine" not in bullet.objtype:
								self.writeOnScreen(str(round(bullet.lifeTime)),bullet.position.x + bullet.width * 2 / 7, bullet.position.y + bullet.height * 2 / 7)
							bullet.lifeTime -= self.dt
					#self.writeOnScreen(str(distance), bullet.position.x, bullet.position.y)
				if "pet" in weapon.pattern:
					bullet.position.x = bullet.position_destination.x
					bullet.position.y = bullet.position_destination.y

					tempX = bullet.position.x
					tempY = bullet.position.y
					bullet.setPositionBasedOnMovement(self.settings.speed, self.dt )

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

					tempX = bullet.position.x
					tempY = bullet.position.y
					bullet.setPositionBasedOnMovement(self.settings.speed, self.dt)
					if weapon.name == "Scatter Rifle":
						bullet.position_destination.x += bullet.position.x - tempX
						bullet.position_destination.y += bullet.position.y - tempY
						bullet.position.x += (bullet.position_destination.x - bullet.position.x) * 0.002 * weapon.speed
						bullet.position.y += (bullet.position_destination.y - bullet.position.y) * 0.002 * weapon.speed
					else:
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
					
					if weapon.name == "Scatter Rifle":
						pygame.draw.circle(self.screen, weapon.colour, bullet.position, bullet.radius)
						if weapon.level >= 3:
							pygame.draw.circle(self.screen, "black", bullet.position, bullet.radius, 3)
						if weapon.level == 5:
							pygame.draw.circle(self.screen, "blue4", bullet.position, bullet.radius/1.3)

					if isinstance(bullet.lifeTime, float):
						if bullet.lifeTime <= 0:
							if bullet.weaponname == "Scatter Rifle" and bullet.objtype != "bullet scatter":
								b = weapon.getScatters(bullet)
								weapon.bullets.add(b)
								self.bulletGroup.add(b)
								bullet.remove(weapon.bullets)
								bullet.kill()
							else:
								bullet.remove(weapon.bullets)
								bullet.kill()
						else:
							bullet.lifeTime -= self.dt

				if "circle" in weapon.pattern:
					if bullet.rotation == 360:
						bullet.rotation = 0

					bullet.position.x = self.player.position.x + weapon.distance * math.cos(bullet.rotation * math.pi / 180)
					bullet.position.y = self.player.position.y + weapon.distance * math.sin(bullet.rotation * math.pi / 180)
					bullet.setPositionBasedOnMovement(self.settings.speed, self.dt)

					pygame.draw.rect(self.screen, "blue", bullet.rect)		#Bullet hitbox
					pygame.draw.circle(self.screen, weapon.colour, (bullet.position.x, bullet.position.y), weapon.size)

					if weapon.level >= 3:
						pygame.draw.circle(self.screen, "pink", (bullet.position.x, bullet.position.y), weapon.size/2)
					if weapon.level == 5:
						pygame.draw.circle(self.screen, "white", (bullet.position.x, bullet.position.y), weapon.size/4)

					bullet.rotation += weapon.speed * 0.05

					if isinstance(bullet.lifeTime, float) or isinstance(bullet.lifeTime, int):
						if bullet.lifeTime <= 0:
							bullet.remove(weapon.bullets)
							bullet.kill()
						else:
							bullet.lifeTime -= self.dt
				
				if "angled" in weapon.pattern:
					if bullet.position_destination.x == 0 and bullet.position_destination.y == 0:
						bullet.position_destination.x = mouse_pos.x
						bullet.position_destination.y = mouse_pos.y

					bullet.position_original.x = self.player.position.x
					bullet.position_original.y = self.player.position.y
					
					center = pygame.Vector2(
						(bullet.position_destination.x - bullet.position_original.x) / 2 + bullet.position_original.x, 
						(bullet.position_destination.y - bullet.position_original.y) / 2 + bullet.position_original.y, 
						)

					#ellipse = (((bullet.position.x - center.x) * math.cos(angle) + (bullet.position.y - center.y) * math.sin(angle))**2)/(((bullet.position_destination.x - bullet.position_original.x)/2 + 1)**2 + ((bullet.position_destination.y - bullet.position_original.y)/2 + 1)**2) + (((bullet.position.x - center.x) * math.sin(angle) - (bullet.position.y - center.y) * math.cos(angle))**2)/(((bullet.position_destination.x - bullet.position_original.x)/4 + 1)**2 + ((bullet.position_destination.y - bullet.position_original.y)/4 + 1)**2)                    
					# Based on the equations:
					# x = a * cos(ω) }
					# y = b * sin(ω) } where 0 <= ω <= 2π
					# AND:
					# ((x-u)^2)/(a^2) + ((x-v)^2)/(b^2) = 1, where u and v is the shift of the center point on the x and y axis respectively
					# I just rotate the whole thing by the angle of the throw

					# Computing the ellipse's half-axis' -> Instead of a fixed value, I made it so the ellipse's size/area is relative to the throw distance.
					ax = ((bullet.position_destination.x - bullet.position_original.x) / 2)
					ay = ((bullet.position_destination.y - bullet.position_original.y) / 2)

					focus_point1 = pygame.Vector2(bullet.position_original.x + ax / 5, bullet.position_original.y + ay / 5)
					focus_point2 = pygame.Vector2(bullet.position_destination.x - ax / 5, bullet.position_destination.y - ay / 5)

					cx = (focus_point2.x - focus_point1.x) / 2
					cy = (focus_point2.y - focus_point1.y) / 2

					bx = (math.sqrt(ax**2 - cx**2) / 1.25) # A little trade secret: This isn't really an ellipse. I should't divide it by 1.25. A boomerang flies on an elongated ellipse, so I actually need this and not a proper one (sadly).
					by = (math.sqrt(ay**2 - cy**2) / 1.25) #  https://decoboomerangs.com/en/article/how-a-boomerang-flies#:~:text=Long-range%20boomerangs%20have%20a,to%20140%20meters%20or%20more.

					distance = math.sqrt((bullet.position_destination.x - bullet.position_original.x)**2 + (bullet.position_destination.y - bullet.position_original.y)**2) + 1
					angle = math.acos((bullet.position_destination.x - bullet.position_original.x)/distance) * self.compare_subtraction(bullet.position_destination.y, bullet.position_original.y)

					bullet.position.x =  2 * center.x + math.sqrt(ax**2 + ay**2) * math.cos((bullet.rotation + 180) *  math.pi / 180) + math.sqrt(ax**2 + ay**2) * math.cos(0) - bullet.position_destination.x
					bullet.position.y =  2 * center.y + math.sqrt(bx**2 + by**2) * math.sin((bullet.rotation + 180) *  math.pi / 180) + math.sqrt(bx**2 + by**2) * math.sin(0) - bullet.position_destination.y
					
					bullet.position.x -= bullet.position_original.x
					bullet.position.y -= bullet.position_original.y

					bullet.position.rotate_rad_ip(angle)

					bullet.position.x += bullet.position_original.x
					bullet.position.y += bullet.position_original.y
					

					tempX = bullet.position.x
					tempY = bullet.position.y
					bullet.setPositionBasedOnMovement(self.settings.speed, self.dt)
					bullet.position_destination.x -= (tempX - bullet.position.x)
					bullet.position_destination.y -= (tempY - bullet.position.y)
					bullet.position_original.x -= (tempX - bullet.position.x)
					bullet.position_original.y -= (tempY - bullet.position.y)
					bullet.rotation += weapon.speed * 0.1 * (1 + abs(math.sin(bullet.rotation * math.pi / 180)))
					bullet.animation_rotation += weapon.speed * 0.3 * (1 + abs(math.sin(30 * math.pi / 180)))

					bullet.rect = pygame.Rect(bullet.position.x, bullet.position.y, weapon.size*3, weapon.size*3)
					pygame.draw.arc(self.screen, weapon.colour, bullet.rect, math.radians(0 + bullet.animation_rotation), math.radians(120 + weapon.level * 25 + bullet.animation_rotation), 7 + weapon.level)
					
					if weapon.level >= 3:
						pygame.draw.arc(self.screen, "blue", bullet.rect, math.radians(0 + bullet.animation_rotation), math.radians(140 + weapon.level * 20 + bullet.animation_rotation), 2 + weapon.level)

					if weapon.level == 5:
						pygame.draw.arc(self.screen, "indianred3", bullet.rect, math.radians(0 + bullet.animation_rotation), math.radians(140 + weapon.level * 20 + bullet.animation_rotation), 2)


					if (pygame.sprite.collide_circle(bullet, self.player) and bullet.rotation >= 180) or bullet.rotation >= 720:
						bullet.remove(weapon.bullets)
						bullet.kill()

			if "pet" in weapon.pattern:
				pygame.draw.circle(self.screen, weapon.colour, (weapon.position.x, weapon.position.y), weapon.size)
				if weapon.level >= 3: 
					pygame.draw.circle(self.screen, "black", (weapon.position.x, weapon.position.y), weapon.size, 2)
				
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
			
			if weapon.name == "Homing Arrow":
				if len(weapon.pathlist[len(weapon.pathlist)-8:]) > 1 and weapon.level >= 3:
					poslist = weapon.pathlist[len(weapon.pathlist)-8:] + weapon.pathlist[len(weapon.pathlist)-8:][::-1]
					pygame.draw.polygon(self.screen, weapon.colour, [(pos.x + weapon.size / 4 * self.compare_subtraction(self.player.position.x, pos.x), pos.y) for pos in poslist], weapon.size)
				
				if weapon.level < 3:
					pygame.draw.circle(self.screen, weapon.colour, weapon.position, weapon.size)
				weapon.rotation += weapon.speed * 0.07
	
	def passiveCycle(self):
		self.writeOnScreen(" ".join([":".join([name, str(passive.level)]) for name, passive in self.player_passives.items()]), 0 , 100)
		for passive in self.player_passives.values():
			if passive.name == "Gunslinger":
				if passive.count > 0:
					passive.count -= 1
					position = pygame.Vector2(
						self.player.position.x + 750 * random.random() * self.getSign(),
						self.player.position.y + 750 * random.random() * self.getSign()
					)
					self.ItemGroup.add(WeaponKit(position))
			if passive.cooldown_current <= 0:
				if passive.name == "Health Regeneration":
					self.player.health_current += self.player.buffs["health regen"]
					if self.player.health_current > self.player.health_max:
						self.player.health_current = self.player.health_max
					passive.cooldown_current = passive.cooldown_max
				
				if passive.name == "Protective Barrier":
					self.player.buffs["barrier"] = passive.value
					passive.cooldown_current = passive.cooldown_max

				if passive.name == "Dodge":
					if self.player.buffs["dodge count"] < passive.value:
						self.player.buffs["dodge count"] += 1
					passive.cooldown_current = passive.cooldown_max
			else:
				passive.updateCooldown(self.dt)
	
	def transparentCycle(self):
		if "Slowing Aura" in self.player_passives.keys():
			passive = self.player_passives["Slowing Aura"]
			passive.setHitbox(self.player.position, passive.value * 5 + 49 + 50 * passive.level)
			pygame.draw.circle(self.traspscreen, (250, 150, 150, 255/100 * 55), passive.position, passive.radius)
			pygame.draw.circle(self.screen, (0,0,0, 255), passive.position, passive.radius, 1)

		if "Damaging Field" in self.player_weapons.keys():
			weapon = self.player_weapons["Damaging Field"]
			for bullet in weapon.bullets:
				if weapon.name == "Damaging Field":
					bullet.position.x = bullet.position_destination.x
					bullet.position.y = bullet.position_destination.y
					bullet.setPositionBasedOnMovement(self.settings.speed, self.dt )

					bullet.position_destination.x = bullet.position.x
					bullet.position_destination.y = bullet.position.y

					transparency = abs(10 - bullet.lifeTime * self.compare_subtraction(bullet.lifeTime, 0) / weapon.bulletLifeTime * 10)
					if 255/100 * (25 + 4 * transparency) > 255:
						transparency = 18.75
					getDecentSize = transparency * 200
					if getDecentSize >= 6 * weapon.size / 8:
						getDecentSize = 6 * weapon.size / 8
					bullet.width = getDecentSize + 2 * weapon.size / 8 * transparency / 10
					bullet.height = getDecentSize + 2 * weapon.size / 8 * transparency / 10
					bullet.rect = pygame.Rect(bullet.position.x - bullet.width/2, bullet.position.y - bullet.height/2, bullet.width, bullet.height)
					pygame.draw.circle(self.traspscreen, (217, 78, 63, 255/100 * (25 + 4 * transparency)), (bullet.position.x, bullet.position.y), bullet.width/2 - 3.5)
					pygame.draw.circle(self.screen, (0,0,0, 255), (bullet.position.x, bullet.position.y),bullet.width/2, 4)

					if isinstance(bullet.lifeTime, float) or isinstance(bullet.lifeTime, int):
						if bullet.lifeTime <= 0:
							bullet.remove(weapon.bullets)
							bullet.kill()
						else:
							bullet.lifeTime -= self.dt
		if "Homing Arrow" in self.player_weapons.keys():
			weapon = self.player_weapons["Homing Arrow"]
			if len(weapon.pathlist[:len(weapon.pathlist)-6]) > 1:
				if weapon.level < 3:
					poslist = weapon.pathlist + weapon.pathlist[::-1]
				if weapon.level >= 3:
					poslist = weapon.pathlist[:len(weapon.pathlist)-6] + weapon.pathlist[:len(weapon.pathlist)-6][::-1]
				if weapon.level == 5:
					poslistStart = poslist[round(len(poslist)/4):round(len(poslist)*3/4)]
					poslistEnd = [pos for pos in poslist if pos not in poslistStart]
					poslistStart.append(poslistEnd[len(poslistEnd)//2])
					pygame.draw.polygon(self.traspscreen, (255,50,50,255/100*55), poslistStart, weapon.level + 1)
					pygame.draw.polygon(self.traspscreen, (255,100,0,255/100*55), poslistEnd, weapon.level + 1)
				else:
					pygame.draw.polygon(self.traspscreen, (255,50,50,255/100*55), poslist, weapon.level + 1)

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