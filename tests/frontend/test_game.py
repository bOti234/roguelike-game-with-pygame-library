import os
import pygame
import time
import pyautogui
from frontend.models.game import Game, StatBar, Passive, Weapon, Event, PlayerCharacter, Enemy, Experience, Bullet
from ..fixtures import pygame_setup, game

# Mocking doesn't have seemed to work, since the project was made without the knowledge of mocks, and my pygame elements (screen, images, so on) are created in a completely different way
# I don't know if I have the time to change everything now, so I'm not going to risk it.
# This is why I'm going to use event injection instead. During testing, the game will open and do everything on it's own. 
# During this process do not press anything on your keyboard and don't move your mouse, cause that will obstruct the test.

def game_start(game: Game, test = True):
	game.gameStart(
		'normal',
		'normal',
		60,
		800,
		600,
		None,
		test
	)


def test_game_init(game: Game):
	assert game.difficultylist == ["easy", "normal", "hard"]
	assert game.speedlist == ["slow", "normal", "fast"]


def test_game_start(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	
	assert game.settings.difficulty == 'normal'
	assert game.settings.speed == game.setSpeed('normal')
	assert game.settings.fps == 60
	assert game.settings.screen_width == 800
	assert game.settings.screen_height == 600
	# Bunch of other stuff

	#pygame.event.post(pygame.QUIT)
	assert [passive.name for passive in game.passivelist] == ['Health Regeneration', 'Berserk', 'Crit Chance', 'Dodge', 'Gunslinger', 'Protective Barrier', 'Slowing Aura', 'Greater Strength', 'Greater Vitality', 'Enhanced Wisdom', 'Increased Reach', 'Second Chance']
	assert [weapon.name for weapon in game.weaponlist] == ['High-tech Rifle', 'Energy Orb', 'Boomerang', 'Flamethrower', 'Damaging Field', 'Attack Drone', 'Cluster Bombs', 'Pistols', 'Scatter Rifle', 'Homing Arrow', 'Laser Beam', 'Energy Sword']


def test_game_setSpeed(game: Game):
	response0 = game.setSpeed('slow')
	response1 = game.setSpeed('normal')
	response2 = game.setSpeed('fast')
	response3 = game.setSpeed('gibberish')

	assert response0 == 300
	assert response1 == 400
	assert response2 == 500
	assert response3 == 400


def test_game_stopsound(pygame_setup, game: Game):
	game_start(game)
	game.stopSound()
	assert pygame.mixer.Channel(0).get_busy() == False


def test_game_playsound(pygame_setup, game: Game):
	game_start(game)

	dirname = os.path.dirname(__file__)
	filename = os.path.join(dirname, '../../assets/audio/Boomerang Sound.wav')
	sound = pygame.mixer.Sound(filename)
	game.playSound(sound)
	assert pygame.mixer.Channel(0).get_busy() == True


def test_game_setupPygameScreens(pygame_setup, game: Game):
	game_start(game)
	new_width = 400
	new_height = 300
	game.settings.screen_width = new_width
	game.settings.screen_height = new_height
	game.setupPygameScreens()

	assert pygame.image.tostring(game.screen, 'RGBA') == pygame.image.tostring(pygame.Surface((new_width, new_height), pygame.HWSURFACE), 'RGBA')
	assert pygame.image.tostring(game.traspscreen, 'RGBA') == pygame.image.tostring(pygame.Surface((new_width, new_height), pygame.SRCALPHA), 'RGBA')
	assert pygame.image.tostring(game.traspscreen_hud, 'RGBA') == pygame.image.tostring(pygame.Surface((new_width, new_height), pygame.SRCALPHA), 'RGBA')

	assert game.sizeratio_x == new_width / game.settings.fullscreen_width
	assert game.sizeratio_y == new_height / game.settings.fullscreen_height


def test_game_setupPygameElements(pygame_setup, game: Game):
	game_start(game)
	game.setupPygameElements()
	
	dirname = os.path.dirname(__file__)
	filepath = os.path.join(dirname, '../../assets/audio/')
	test_sounds = {
		'main_menu_music': pygame.mixer.Sound(filepath+'main_menu_music.mp3'),
		'ingame_menu_music': pygame.mixer.Sound(filepath+'ingame_menu_music.mp3'),
		'death_menu_music': pygame.mixer.Sound(filepath+'death_menu_music.mp3'),
		'forest_music': pygame.mixer.Sound(filepath+'forest_music.mp3'),
		'popupwindow_sound': pygame.mixer.Sound(filepath+'popupwindow_sound.wav'),
		'experience_pickup_sound': pygame.mixer.Sound(filepath+'experience_pickup_sound.wav'),
		'enemy_hit_sound': pygame.mixer.Sound(filepath+'enemy_hit_sound.wav'),
		'player_hit_sound': pygame.mixer.Sound(filepath+'player_hit_sound.wav')
	}

	assert pygame.mixer.get_num_channels() == 12
	assert game.sounds.keys() == test_sounds.keys()
	assert len([True for sound in game.sounds.values() if isinstance(sound, pygame.mixer.Sound)]) == len(test_sounds.values())


def test_game_drawLoadingGif(pygame_setup, game: Game):
	game_start(game)
	game.setupPygameElements()
	game.time = None
	expected_screen = game.screen.copy()
	response = game.drawLoadingGif()

	expected_screen.blit(response, (0, 0))
	after_screen = game.screen.copy()

	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


def test_game_getStatBars(pygame_setup, game: Game):
	game_start(game)
	game.setupPygameElements()
	response = game.getStatBars()

	assert [True for bar in response if isinstance(bar, StatBar)].count(True) == len(response)


def test_game_getPassives(game: Game):
	response = game.getPassives()
	assert isinstance(response, list) and len(response) > 0
	assert [True for passive in response if isinstance(passive, Passive)].count(True) == len(response)


def test_game_getWeapons(game: Game):
	game.player = PlayerCharacter(40, pygame.Vector2(800 / 2, 600 / 2), 200, game.setSpeed('normal'))
	response = game.getWeapons()
	assert isinstance(response, list) and len(response) > 0
	assert [True for weapon in response if isinstance(weapon, Weapon)].count(True) == len(response)


def test_game_getEvents(game: Game):
	response = game.getEvents()
	assert isinstance(response, list) and len(response) > 0
	assert [True for event in response if isinstance(event, Event)].count(True) == len(response)


def test_game_openmainmenu(pygame_setup, game: Game):
	game_start(game)
	game.setupPygameElements()
	response = game.openMainMenu()

	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
	assert response == 'test'


def test_game_openInGameMenu(pygame_setup, game: Game):
	game_start(game)
	game.setupPygameElements()
	response = game.openInGameMenu()

	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
	assert response == 'test'

def test_game_openItemListMenu(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.setupPygameElements()
	response = game.openItemListMenu()

	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
	assert response == 'test'


def test_game_openDeathMenu(pygame_setup, game: Game):
	game_start(game)
	game.setupPygameElements()
	response = game.openDeathMenu()

	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
	assert response == 'test'


def test_game_openSelectWeaponMenu(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.setupPygameElements()
	response = game.openSelectWeaponMenu()

	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
	assert response == 'test'


def test_game_getRandomWeapons(game: Game):
	game.player = PlayerCharacter(40, pygame.Vector2(800 / 2, 600 / 2), 200, game.setSpeed('normal'))
	game.weaponlist = game.getWeapons()
	game.player_weapons = {}
	response = game.getRandomWeapons()

	assert isinstance(response, list) and len(response) == 3
	assert [True for weapon in response if isinstance(weapon, Weapon)].count(True) == 3

	game.weaponlist = game.weaponlist[:2]
	response = game.getRandomWeapons()

	assert isinstance(response, list) and len(response) == 2
	assert [True for weapon in response if isinstance(weapon, Weapon)].count(True) == 2

	game.weaponlist = []
	response = game.getRandomWeapons()

	assert isinstance(response, list) and len(response) == 0


def test_game_openLevelUpMenu(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.setupPygameElements()
	response = game.openLevelUpMenu()

	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
	assert response == 'test'


def test_game_getRandomPassives(game: Game):
	game.player = PlayerCharacter(40, pygame.Vector2(800 / 2, 600 / 2), 200, game.setSpeed('normal'))
	game.passivelist = game.getPassives()
	game.player_passives = {}
	response = game.getRandomPasives()

	assert isinstance(response, list) and len(response) == 3
	assert [True for passive in response if isinstance(passive, Passive)].count(True) == 3

	game.passivelist = game.passivelist[:2]
	response = game.getRandomPasives()

	assert isinstance(response, list) and len(response) == 2
	assert [True for passive in response if isinstance(passive, Passive)].count(True) == 2

	game.passivelist = []
	response = game.getRandomPasives()

	assert isinstance(response, list) and len(response) == 0

def test_game_drawPlayer(pygame_setup, game: Game):
	game_start(game, 'need_just_settings')
	game.setupPygameScreens()

	expected_screen = game.screen.copy()

	game.drawPlayer()

	pygame.draw.circle(expected_screen, "skyblue", (game.player.position.x, game.player.position.y), game.player.radius)
	after_screen = game.screen.copy()

	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


def test_game_drawHUDElements(pygame_setup, game: Game):
	game_start(game, 'need_just_settings')
	game.setupPygameElements()

	expected_screen = game.screen.copy()
	game.time = 0
	game.gamescore = 0
	game.current_boss = 'something'

	game.drawHUDElements()

	# Draw time box:
	font = pygame.font.Font(None, 30)
	minutes = round(game.time//60)
	seconds = round(game.time - 60 * (game.time // 60))
	if seconds == 60:
		seconds = 0
		minutes += 1
	time_text = str(minutes)+":"+str(seconds)
	time_box = pygame.Rect(game.settings.screen_width/2 - font.size("999:99")[0]/2, 8, font.size("999:99")[0] + 10, font.get_linesize() + 5)
	pygame.draw.rect(expected_screen, "skyblue", time_box, 0, 15)
	pygame.draw.rect(expected_screen, "black", time_box, 3, 15)
	text = font.render(time_text, True, 'black')
	expected_screen.blit(text, (time_box.x + (time_box.width - font.size(time_text)[0])/2, time_box.y + 5))

	# Draw Score box:
	score_text = str(int(round(game.gamescore)))
	box_width = font.size("99999999")[0] if font.size("99999999")[0] > font.size(score_text)[0] else font.size(score_text)[0]
	score_box = pygame.Rect(game.settings.screen_width/2 - box_width/2, 40, box_width + 10, font.get_linesize() + 5)
	pygame.draw.rect(expected_screen, (10, 43, 57), score_box, 0, 15)
	pygame.draw.rect(expected_screen, "cyan", score_box, 3, 15)
	text = font.render(score_text, True, (200, 255, 255))
	expected_screen.blit(text, (score_box.x + (score_box.width - font.size(score_text)[0])/2, score_box.y + 5))

	# Draw Boss alert:
	if game.current_boss is not None:
		font_border = pygame.font.Font(None, 35)
		text_bg = font_border.render('Boss appeared', True, 'black')
		text = font.render('Boss appeared', True, 'red')
		expected_screen.blit(text_bg, (game.settings.screen_width/2 - font_border.size('Boss appeared')[0]/3 - 2, 98))
		expected_screen.blit(text, (game.settings.screen_width/2 - font.size('Boss appeared')[0]/3, 100))

	# Draw the inventory button:
	inventory_background_rect = pygame.Rect(game.inventory_button.rect.x - 7, game.inventory_button.rect.y - 7, game.inventory_button.rect.width + 14, game.inventory_button.rect.height + 14)
	pygame.draw.rect(expected_screen, (10, 43, 57), inventory_background_rect, 0, 5)
	pygame.draw.rect(expected_screen, "cyan", inventory_background_rect, 4, 5)
	game.inventory_button.draw(expected_screen)

	keyboard_button_rect = pygame.Rect(inventory_background_rect.x + inventory_background_rect.width - 30, inventory_background_rect.y + inventory_background_rect.height - 30, 35, 35)
	pygame.draw.rect(expected_screen, (10, 43, 57), keyboard_button_rect, 0)
	pygame.draw.rect(expected_screen, 'cyan', keyboard_button_rect, 3)
	font = pygame.font.Font(None, 40)
	text = font.render('E', True, 'white')
	expected_screen.blit(text, (keyboard_button_rect.x + 8.5, keyboard_button_rect.y + 7))

	after_screen = game.screen.copy()

	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


def test_game_drawStatBoxes(pygame_setup, game: Game):
	game_start(game, 'need_just_settings')
	game.setupPygameScreens()
	game.passivelist = game.getPassives()
	passive = [passive for passive in game.passivelist if passive.name == 'Protective Barrier'][0]
	game.player_passives = {passive.name: passive}

	expected_screen = game.screen.copy()
	expected_transparent_screen = game.traspscreen_hud.copy()

	game.drawStatBoxes()

	for bar in game.statbarlist:
		if bar.stat_type == "barrierbar":
			if "Protective Barrier" in game.player_passives.keys():
				pygame.draw.rect(expected_transparent_screen, bar.stat_background_rgba, bar.border_rect, 0, bar.border_radius)
		else:
			pygame.draw.rect(expected_transparent_screen, bar.stat_background_rgba, bar.border_rect, 0, bar.border_radius)
	expected_screen.blit(expected_transparent_screen, (0,0))
	
	for bar in game.statbarlist:
		if bar.stat_type == 'healthbar':
			newWidth = (game.player.width - 4) * game.player.health_current / game.player.health_max
		if bar.stat_type == 'barrierbar':
			newWidth = (game.player.width - 4) * game.player.status_effects["barrier"] / passive.value
		if bar.stat_type == 'experiencebar':
			newWidth = (game.settings.screen_width) * game.player.experience_current / game.player.experience_max
		bar.stat_rect.width = newWidth

		pygame.draw.rect(expected_screen, bar.stat_colour, bar.stat_rect, 0, bar.border_radius)
		pygame.draw.rect(expected_screen, bar.border_colour, bar.border_rect, bar.border_width, bar.border_radius)

	font = pygame.font.Font(None, 30)
	exp_progress_txt = str(game.player.experience_current)+" / "+str(game.player.experience_max)

	posX = game.settings.screen_width/2 - font.size(exp_progress_txt)[0]//2
	posY = game.settings.screen_height - 20
	text = []
	for i, char in enumerate(exp_progress_txt):
		rgb = expected_screen.get_at((round(posX + i * font.size("_")[0]), posY))[:3]
		if rgb[0] + rgb[1] + rgb[2] >= 383:
			resp_colour = "black"
		else:
			resp_colour = "white"
		text.append(font.render(char, True, resp_colour))
	
	for i, t in enumerate(text):
		expected_screen.blit(t, (posX + i * font.size("_")[0], posY))

	after_screen = game.screen.copy()
	after_transpaerent_screen = game.traspscreen_hud.copy()

	assert pygame.image.tostring(expected_transparent_screen, 'RGBA') == pygame.image.tostring(after_transpaerent_screen, 'RGBA')
	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


def test_game_getBackgroundImage(pygame_setup, game: Game):
	game.backgroundimage = None
	game.getBackgroundImage()

	assert isinstance(game.backgroundimage, pygame.Surface)


def test_game_drawBackground(pygame_setup, game: Game):
	game_start(game, 'need_just_settings')
	game.setupPygameElements()

	expected_screen = game.screen.copy()

	game.drawBackground()

	expected_screen.fill("#124a21")
	image_rect = game.backgroundimage.get_rect()
	steps_x = game.background.x // (image_rect.width)
	steps_y = game.background.y // (image_rect.height)
	
	expected_screen.blit(game.backgroundimage, (game.background.x - image_rect.width * (1 + steps_x), game.background.y - image_rect.height * (1 + steps_y)))
	expected_screen.blit(game.backgroundimage, (game.background.x - image_rect.width * (1 + steps_x), game.background.y - image_rect.height * (0 + steps_y)))
	expected_screen.blit(game.backgroundimage, (game.background.x - image_rect.width * (0 + steps_x), game.background.y - image_rect.height * (1 + steps_y)))
	expected_screen.blit(game.backgroundimage, (game.background.x - image_rect.width * (0 + steps_x), game.background.y - image_rect.height * (0 + steps_y)))

	after_screen = game.screen.copy()

	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


def test_game_checkKeysPressed(pygame_setup, game: Game):
	game_start(game)
	game.running = True
	game.dt = 0.05

	original_x = game.background.x
	original_y = game.background.y
	
	game.test['data'] = [False] * 500
	game.test['data'][pygame.K_a] = True
	game.checkKeysPressed()

	assert game.background.x == original_x + game.player.speed * 0.05

	game.background.x = original_x
	
	game.test['data'] = [False] * 500
	game.test['data'][pygame.K_d] = True
	game.checkKeysPressed()

	assert game.background.x == original_x - game.player.speed * 0.05

	game.background.x = original_x
	
	game.test['data'] = [False] * 500
	game.test['data'][pygame.K_w] = True
	game.checkKeysPressed()

	assert game.background.y == original_y + game.player.speed * 0.05

	game.background.y = original_y
	
	game.test['data'] = [False] * 500
	game.test['data'][pygame.K_s] = True
	game.checkKeysPressed()

	assert game.background.y == original_y - game.player.speed * 0.05

	game.background.y = original_y
	
	game.test['data'] = [False] * 500
	game.test['data'][pygame.K_w] = True
	game.test['data'][pygame.K_a] = True
	game.checkKeysPressed()

	assert game.background.y == original_y + game.player.speed * 0.05 + game.player.speed * ( 0.05 / 2**(1/2) -  0.05)
	assert game.background.x == original_x + game.player.speed * 0.05 + game.player.speed * ( 0.05 / 2**(1/2) -  0.05)

	game.background.y = original_y
	game.background.x = original_x
	
	game.test['data'] = [False] * 500
	game.test['data'][pygame.K_w] = True
	game.test['data'][pygame.K_d] = True
	game.checkKeysPressed()

	assert game.background.y == original_y + game.player.speed * 0.05 + game.player.speed * ( 0.05 / 2**(1/2) -  0.05)
	assert game.background.x == original_x - game.player.speed * 0.05 - game.player.speed * ( 0.05 / 2**(1/2) -  0.05)

	game.background.y = original_y
	game.background.x = original_x
	
	game.test['data'] = [False] * 500
	game.test['data'][pygame.K_s] = True
	game.test['data'][pygame.K_a] = True
	game.checkKeysPressed()

	assert game.background.y == original_y - game.player.speed * 0.05 - game.player.speed * ( 0.05 / 2**(1/2) -  0.05)
	assert game.background.x == original_x + game.player.speed * 0.05 + game.player.speed * ( 0.05 / 2**(1/2) -  0.05)

	game.background.y = original_y
	game.background.x = original_x
	
	game.test['data'] = [False] * 500
	game.test['data'][pygame.K_s] = True
	game.test['data'][pygame.K_d] = True
	game.checkKeysPressed()

	assert game.background.y == original_y - game.player.speed * 0.05 - game.player.speed * ( 0.05 / 2**(1/2) -  0.05)
	assert game.background.x == original_x - game.player.speed * 0.05 - game.player.speed * ( 0.05 / 2**(1/2) -  0.05)


def test_game_updateGameScore(game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	pos = pygame.Vector2(0,0)
	test_enemy_lvl_1 = Enemy(game.weaponlist, pos)
	test_enemy_lvl_2 = Enemy(game.weaponlist, pos, 2)

	test_exp_val_20 = Experience(pos)
	test_exp_val_2000 = Experience(pos, value = 2000)

	game.gamescore = 0
	original_score = game.gamescore
	game.updateGameScore('enemy killed', test_enemy_lvl_1)

	assert game.gamescore == original_score + 100 * test_enemy_lvl_1.level
	game.gamescore = 0

	game.updateGameScore('enemy killed', test_enemy_lvl_2)

	assert game.gamescore == original_score + 100 * test_enemy_lvl_2.level
	game.gamescore = 0

	game.updateGameScore('second passed')

	assert game.gamescore == original_score + 10
	game.gamescore = 0

	game.updateGameScore('exp picked up', test_exp_val_20)

	assert game.gamescore == original_score + 1 + test_exp_val_20.value//100
	game.gamescore = 0

	game.updateGameScore('exp picked up', test_exp_val_2000)

	assert game.gamescore == original_score + 1 + test_exp_val_2000.value//100
	game.gamescore = 0


def test_game_checkHitBoxes(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.setupPygameElements()
	pos = pygame.Vector2(game.player.position.x, game.player.position.y)
	test_enemy = Enemy(game.weaponlist, pos)
	game.EnemyGroup.add(test_enemy)

	original_player_health = game.player.health_current
	game.checkHitboxes()

	assert game.player.health_current == original_player_health - test_enemy.damage
	
	weapon = game.weaponlist[0]
	test_bullet = Bullet(weapon.name, pos, pos, pos, weapon.bulletLifeTime, weapon.damage, weapon.pierce, False, 'bullet', weapon.size)
	game.bulletGroup.add(test_bullet)

	original_enemy_health = test_enemy.health
	game.checkHitboxes()

	assert test_enemy.health == original_enemy_health - test_bullet.damage
	test_enemy.kill()
	test_bullet.kill()

	test_experience = Experience(pos)
	game.experienceGroup.add(test_experience)

	original_exp_value = game.player.experience_queue
	game.checkHitboxes()

	assert game.player.experience_queue == original_exp_value + test_experience.value
	assert test_experience not in game.experienceGroup


def test_game_damageEnemy(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.setupPygameElements()
	pos = pygame.Vector2(game.player.position.x, game.player.position.y)
	test_enemy = Enemy(game.weaponlist, pos)
	game.EnemyGroup.add(test_enemy)

	weapon = game.weaponlist[0]
	test_bullet = Bullet(weapon.name, pos, pos, pos, weapon.bulletLifeTime, weapon.damage, weapon.pierce, False, 'bullet', weapon.size)
	game.bulletGroup.add(test_bullet)

	original_enemy_health = test_enemy.health
	game.damageEnemy(test_bullet, test_enemy)

	assert test_enemy.health == original_enemy_health - test_bullet.damage
	original_enemy_health = test_enemy.health
	original_bullet_pierce = test_bullet.pierce
	
	test_enemy.hitCooldown = 0
	game.damageEnemy(test_bullet, test_enemy)

	assert test_enemy.health == original_enemy_health
	assert test_bullet.pierce == original_bullet_pierce

	test_enemy.hitCooldown = 1
	test_bullet.enemiesHit.remove(test_enemy)

	assert test_enemy.health == original_enemy_health
	assert test_bullet.pierce == original_bullet_pierce

	test_enemy.hitCooldown = 0

	test_bullet.damage = test_enemy.health
	test_bullet.pierce = 1
	game.damageEnemy(test_bullet, test_enemy)

	assert test_enemy not in game.EnemyGroup
	assert test_bullet not in game.bulletGroup

def test_game_spawnWeaponKit(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.dt = 0.05

	game.WeaponKitCooldown = 0
	original_itemgroup_len = len(game.ItemGroup)
	game.spawnWeaponKit()

	assert len(game.ItemGroup) == original_itemgroup_len + 1
	assert game.WeaponKitCooldown != 0

	original_itemgroup_len = len(game.ItemGroup)
	game.WeaponKitCooldown = 1
	original_cooldown = game.WeaponKitCooldown
	game.spawnWeaponKit()
	assert len(game.ItemGroup) == original_itemgroup_len
	assert game.WeaponKitCooldown == original_cooldown - 0.05

	for weapon in game.weaponlist:
		if len(game.player_weapons) == 5:
			break
		game.player_weapons.update({weapon.name: weapon})
	
	for weapon in game.player_weapons.values():
		weapon.upgradeItem(game.player, 5)
	
	original_itemgroup_len = len(game.ItemGroup)
	game.WeaponKitCooldown = 0
	game.spawnWeaponKit()
	assert len(game.ItemGroup) == original_itemgroup_len


def test_game_spawnMagnet(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.dt = 0.05

	game.MagnetCooldown = 0
	original_itemgroup_len = len(game.ItemGroup)
	game.spawnMagnet()

	assert len(game.ItemGroup) == original_itemgroup_len + 1
	assert game.MagnetCooldown != 0

	original_itemgroup_len = len(game.ItemGroup)
	game.MagnetCooldown = 1
	original_cooldown = game.MagnetCooldown
	game.spawnMagnet()
	assert len(game.ItemGroup) == original_itemgroup_len
	assert game.MagnetCooldown == original_cooldown - 0.05

def test_game_spawnEnemies(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.dt = 0.05

	game.EnemyCooldown = 0
	original_enemygroup_len = len(game.EnemyGroup)
	game.spawnEnemies()

	assert len(game.ItemGroup) > original_enemygroup_len	# I can only check if it's bigger, since the number of enemies spawned is randomized.
	assert game.EnemyCooldown != 0

	original_enemygroup_len = len(game.EnemyGroup)
	game.EnemyCooldown = 1
	original_cooldown = game.EnemyCooldown
	game.spawnEnemies()
	assert len(game.EnemyGroup) == original_enemygroup_len
	assert game.EnemyCooldown == original_cooldown - 0.05

def test_game_spawnEnemyDrops(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')
	game.dt = 0.05
	enemy = Enemy(game.weaponlist, pygame.Vector2(0,0))

	original_experience_len = len(game.experienceGroup)
	original_itemgroup_len = len(game.ItemGroup)
	game.spawnEnemyDrops(enemy)

	assert len(game.experienceGroup) == original_experience_len + 1
	assert len(game.ItemGroup) == original_itemgroup_len + 1

def test_game_getClosestEnemy(pygame_setup, game: Game):
	game_start(game, 'need_weapon_passive_event_test')

	field = [weapon for weapon in game.weaponlist if weapon.name == 'Damaging Field'][0]
	drone = [weapon for weapon in game.weaponlist if weapon.name == 'Attack Drone'][0]
	arrow = [weapon for weapon in game.weaponlist if weapon.name == 'Homing Arrow'][0]
	
	enemylist = game.getClosestEnemy(field, 0)
	assert enemylist is None

	enemy1 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 100, game.player.position.y))
	enemy2 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 200, game.player.position.y))
	enemy3 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 300, game.player.position.y))
	enemy4 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 400, game.player.position.y))
	enemy5 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 500, game.player.position.y))
	enemy6 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 600, game.player.position.y))
	enemy7 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 700, game.player.position.y))
	enemy8 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 800, game.player.position.y))
	enemy9 = Enemy(game.weaponlist, pygame.Vector2(game.player.position.x + 900, game.player.position.y))
	game.EnemyGroup.add([enemy1, enemy2, enemy3, enemy4, enemy5, enemy6, enemy7, enemy8, enemy9])

	enemylist = game.getClosestEnemy(field, 0)
	assert enemylist is None

	enemylist = game.getClosestEnemy(field, 1)
	assert len(enemylist) == 1

	enemylist = game.getClosestEnemy(field, 9)	# One of them is out of range
	assert len(enemylist) == 8

	enemylist = game.getClosestEnemy(drone, 1)
	assert len(enemylist) == 1

	enemylist = game.getClosestEnemy(drone, 3)	# One of them is out of range
	assert len(enemylist) == 2

	enemylist = game.getClosestEnemy(arrow, 1)
	assert len(enemylist) == 1

	enemylist = game.getClosestEnemy(arrow, 5)	# One of them is out of range
	assert len(enemylist) == 4

def test_game_getCrit(pygame_setup, game: Game):
	game.player_passives = {}
	response = game.getCrit()
	assert not response

	game_start(game, 'need_weapon_passive_event_test')

	crit_chance = [passive for passive in game.passivelist if passive.name == 'Crit Chance'][0]
	game.player_passives.update({'Crit Chance': crit_chance})
	game.player_passives['Crit Chance'].value = 1

	response = game.getCrit()
	assert response

def test_game_writeOnScreen(pygame_setup, game: Game):
	game_start(game)
	game.setupPygameElements()

	expected_screen = game.screen.copy()
	txt, x, y, colour, size = 'test text', 20, 15, 'red', 55
	game.writeOnScreen(txt, x, y, colour, size)

	font = pygame.font.Font(None, size)
	text = font.render(txt, True, colour)
	expected_screen.blit(text, (x, y))

	after_screen = game.screen.copy()

	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')

def test_game_compareSutraction(pygame_setup, game: Game):
	response = game.compare_subtraction(5, 4)
	assert response == 1

	response = game.compare_subtraction(4, 5)
	assert response == -1