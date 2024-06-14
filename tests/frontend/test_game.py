import os
import pygame
from frontend.models.game import Game, StatBar, Passive, Weapon, Event, PlayerCharacter
from ..fixtures import server, pygame_setup, game

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


# def test_game_init(game: Game):
# 	assert game.difficultylist == ["easy", "normal", "hard"]
# 	assert game.speedlist == ["slow", "normal", "fast"]


# def test_game_start(pygame_setup, game: Game):
# 	game_start(game, 'need_weapon_passive_event_test')
	
# 	assert game.settings.difficulty == 'normal'
# 	assert game.settings.speed == game.setSpeed('normal')
# 	assert game.settings.fps == 60
# 	assert game.settings.screen_width == 800
# 	assert game.settings.screen_height == 600
# 	# Bunch of other stuff

# 	#pygame.event.post(pygame.QUIT)
# 	assert [passive.name for passive in game.passivelist] == ['Health Regeneration', 'Berserk', 'Crit Chance', 'Dodge', 'Gunslinger', 'Protective Barrier', 'Slowing Aura', 'Greater Strength', 'Greater Vitality', 'Enhanced Wisdom']
# 	assert [weapon.name for weapon in game.weaponlist] == ['High-tech Rifle', 'Energy Orb', 'Boomerang', 'Flamethrower', 'Damaging Field', 'Attack Drone', 'Cluster Bombs', 'Pistols', 'Scatter Rifle', 'Homing Arrow', 'Laser Beam', 'Energy Sword']


# def test_game_setSpeed(game: Game):
# 	response0 = game.setSpeed('slow')
# 	response1 = game.setSpeed('normal')
# 	response2 = game.setSpeed('fast')
# 	response3 = game.setSpeed('gibberish')

# 	assert response0 == 300
# 	assert response1 == 400
# 	assert response2 == 500
# 	assert response3 == 400


# def test_game_stopsound(pygame_setup, game: Game):
# 	game_start(game)
# 	game.stopSound()
# 	assert pygame.mixer.Channel(0).get_busy() == False


# def test_game_playsound(pygame_setup, game: Game):
# 	game_start(game)

# 	dirname = os.path.dirname(__file__)
# 	filename = os.path.join(dirname, '../../assets/audio/Boomerang Sound.wav')
# 	sound = pygame.mixer.Sound(filename)
# 	game.playSound(sound)
# 	assert pygame.mixer.Channel(0).get_busy() == True


# def test_game_setupPygameScreens(pygame_setup, game: Game):
# 	game_start(game)
# 	new_width = 400
# 	new_height = 300
# 	game.settings.screen_width = new_width
# 	game.settings.screen_height = new_height
# 	game.setupPygameScreens()

# 	assert pygame.image.tostring(game.screen, 'RGBA') == pygame.image.tostring(pygame.Surface((new_width, new_height), pygame.HWSURFACE), 'RGBA')
# 	assert pygame.image.tostring(game.traspscreen, 'RGBA') == pygame.image.tostring(pygame.Surface((new_width, new_height), pygame.SRCALPHA), 'RGBA')
# 	assert pygame.image.tostring(game.traspscreen_hud, 'RGBA') == pygame.image.tostring(pygame.Surface((new_width, new_height), pygame.SRCALPHA), 'RGBA')

# 	assert game.sizeratio_x == new_width / game.settings.fullscreen_width
# 	assert game.sizeratio_y == new_height / game.settings.fullscreen_height


# def test_game_setupPygameElements(pygame_setup, game: Game):
# 	game_start(game)
# 	game.setupPygameElements()
	
# 	dirname = os.path.dirname(__file__)
# 	filepath = os.path.join(dirname, '../../assets/audio/')
# 	test_sounds = {
# 		'main_menu_music': pygame.mixer.Sound(filepath+'main_menu_music.mp3'),
# 		'ingame_menu_music': pygame.mixer.Sound(filepath+'ingame_menu_music.mp3'),
# 		'death_menu_music': pygame.mixer.Sound(filepath+'death_menu_music.mp3'),
# 		'forest_music': pygame.mixer.Sound(filepath+'forest_music.mp3'),
# 		'popupwindow_sound': pygame.mixer.Sound(filepath+'popupwindow_sound.wav'),
# 		'experience_pickup_sound': pygame.mixer.Sound(filepath+'experience_pickup_sound.wav'),
# 		'enemy_hit_sound': pygame.mixer.Sound(filepath+'enemy_hit_sound.wav'),
# 		'player_hit_sound': pygame.mixer.Sound(filepath+'player_hit_sound.wav')
# 	}

# 	assert pygame.mixer.get_num_channels() == 12
# 	assert game.sounds.keys() == test_sounds.keys()
# 	assert len([True for sound in game.sounds.values() if isinstance(sound, pygame.mixer.Sound)]) == len(test_sounds.values())


# def test_game_drawLoadingGif(pygame_setup, game: Game):
# 	game_start(game)
# 	game.setupPygameElements()
# 	game.time = None
# 	expected_screen = game.screen.copy()
# 	response = game.drawLoadingGif()

# 	expected_screen.blit(response, (0, 0))
# 	after_screen = game.screen.copy()

# 	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


# def test_game_getStatBars(pygame_setup, game: Game):
# 	game_start(game)
# 	game.setupPygameElements()
# 	response = game.getStatBars()

# 	assert [True for bar in response if isinstance(bar, StatBar)].count(True) == len(response)


# def test_game_getPassives(game: Game):
# 	response = game.getPassives()
# 	assert isinstance(response, list) and len(response) > 0
# 	assert [True for passive in response if isinstance(passive, Passive)].count(True) == len(response)


# def test_game_getWeapons(game: Game):
# 	game.player = PlayerCharacter(40, pygame.Vector2(800 / 2, 600 / 2), 200, game.setSpeed('normal'))
# 	response = game.getWeapons()
# 	assert isinstance(response, list) and len(response) > 0
# 	assert [True for weapon in response if isinstance(weapon, Weapon)].count(True) == len(response)


# def test_game_getEvents(game: Game):
# 	response = game.getEvents()
# 	assert isinstance(response, list) and len(response) > 0
# 	assert [True for event in response if isinstance(event, Event)].count(True) == len(response)


# def test_game_openmainmenu(pygame_setup, game: Game):
# 	game_start(game)
# 	game.setupPygameElements()
# 	response = game.openMainMenu()

# 	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
# 	assert response == 'test'


# def test_game_openInGameMenu(pygame_setup, game: Game):
# 	game_start(game)
# 	game.setupPygameElements()
# 	response = game.openInGameMenu()

# 	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
# 	assert response == 'test'


# def test_game_openInventoryMenu(pygame_setup, game: Game):          #TODO
# 	pass


# def test_game_openItemListMenu(pygame_setup, game: Game):
# 	game_start(game, 'need_weapon_passive_event_test')
# 	game.setupPygameElements()
# 	response = game.openItemListMenu()

# 	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
# 	assert response == 'test'


# def test_game_openDeathMenu(pygame_setup, game: Game):
# 	game_start(game)
# 	game.setupPygameElements()
# 	response = game.openDeathMenu()

# 	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
# 	assert response == 'test'


# def test_game_openSelectWeaponMenu(pygame_setup, game: Game):
# 	game_start(game, 'need_weapon_passive_event_test')
# 	game.setupPygameElements()
# 	response = game.openSelectWeaponMenu()

# 	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
# 	assert response == 'test'


# def test_game_getRandomWeapons(game: Game):
# 	game.player = PlayerCharacter(40, pygame.Vector2(800 / 2, 600 / 2), 200, game.setSpeed('normal'))
# 	game.weaponlist = game.getWeapons()
# 	game.player_weapons = {}
# 	response = game.getRandomWeapons()

# 	assert isinstance(response, list) and len(response) == 3
# 	assert [True for weapon in response if isinstance(weapon, Weapon)].count(True) == 3

# 	game.weaponlist = game.weaponlist[:2]
# 	response = game.getRandomWeapons()

# 	assert isinstance(response, list) and len(response) == 2
# 	assert [True for weapon in response if isinstance(weapon, Weapon)].count(True) == 2

# 	game.weaponlist = []
# 	response = game.getRandomWeapons()

# 	assert isinstance(response, list) and len(response) == 0


# def test_game_openLevelUpMenu(pygame_setup, game: Game):
# 	game_start(game, 'need_weapon_passive_event_test')
# 	game.setupPygameElements()
# 	response = game.openLevelUpMenu()

# 	assert pygame.mouse.get_cursor() == pygame.cursors.arrow
# 	assert response == 'test'


# def test_game_getRandomPassives(game: Game):
# 	game.player = PlayerCharacter(40, pygame.Vector2(800 / 2, 600 / 2), 200, game.setSpeed('normal'))
# 	game.passivelist = game.getPassives()
# 	game.player_passives = {}
# 	response = game.getRandomPasives()

# 	assert isinstance(response, list) and len(response) == 3
# 	assert [True for passive in response if isinstance(passive, Passive)].count(True) == 3

# 	game.passivelist = game.passivelist[:2]
# 	response = game.getRandomPasives()

# 	assert isinstance(response, list) and len(response) == 2
# 	assert [True for passive in response if isinstance(passive, Passive)].count(True) == 2

# 	game.passivelist = []
# 	response = game.getRandomPasives()

# 	assert isinstance(response, list) and len(response) == 0


# # def test_game_gameRun(pygame_setup, game: Game):
# #     pass


# def test_game_drawPlayer(pygame_setup, game: Game):
# 	game_start(game, 'need_just_settings')
# 	game.setupPygameScreens()

# 	expected_screen = game.screen.copy()

# 	game.drawPlayer()

# 	pygame.draw.circle(expected_screen, "skyblue", (game.player.position.x, game.player.position.y), game.player.radius)
# 	after_screen = game.screen.copy()

# 	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


def test_game_drawHUDElements(pygame_setup, game: Game):
	game_start(game, 'need_just_settings')
	game.setupPygameElements()

	expected_screen = game.screen.copy()
	game.time = 0
	game.gamescore = 0

	game.drawHUDElements()

	# Draw time box:
	font = pygame.font.Font(None, 30)
	time_text = str(0)+":"+str(0)
	time_box = pygame.Rect(game.settings.screen_width/2 - font.size("999:99")[0]/2, 8, font.size("999:99")[0] + 10, font.get_linesize() + 5)
	pygame.draw.rect(expected_screen, "skyblue", time_box, 0, 15)
	pygame.draw.rect(expected_screen, "black", time_box, 3, 15)
	text = font.render(time_text, True, 'black')
	expected_screen.blit(text, (time_box.x + (time_box.width - font.size(time_text)[0])/2, time_box.y + 5))

	# Draw Score box:
	score_text = str(0)
	box_width = font.size("99999999")[0] if font.size("99999999")[0] > font.size(score_text)[0] else font.size(score_text)[0]
	score_box = pygame.Rect(game.settings.screen_width/2 - box_width/2, 40, box_width + 10, font.get_linesize() + 5)
	pygame.draw.rect(expected_screen, (10, 43, 57), score_box, 0, 15)
	pygame.draw.rect(expected_screen, "cyan", score_box, 3, 15)
	text = font.render(score_text, True, (200, 255, 255))
	expected_screen.blit(text, (score_box.x + (score_box.width - font.size(score_text)[0])/2, score_box.y + 5))

	# Draw the inventory button:
	inventory_background_rect = pygame.Rect(game.inventory_button.rect.x - 7, game.inventory_button.rect.y - 7, game.inventory_button.rect.width + 14, game.inventory_button.rect.height + 14)
	pygame.draw.rect(game.screen, (10, 43, 57), inventory_background_rect, 0, 5)
	pygame.draw.rect(game.screen, "cyan", inventory_background_rect, 4, 5)
	game.inventory_button.draw(expected_screen)

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
		pygame.draw.rect(expected_transparent_screen, bar.stat_background_rgba, bar.border_rect, 0, bar.border_radius)

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

	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


# def test_game_getBackgroundImage(pygame_setup, game: Game):
# 	game.backgroundimage = None
# 	game.getBackgroundImage()

# 	assert isinstance(game.backgroundimage, pygame.Surface)


# def test_game_drawBackground(pygame_setup, game: Game):
# 	game_start(game, 'need_just_settings')
# 	game.setupPygameElements()

# 	expected_screen = game.screen.copy()

# 	game.drawBackground()

# 	expected_screen.fill("#124a21")
# 	image_rect = game.backgroundimage.get_rect()
# 	steps_x = game.background.x // (image_rect.width)
# 	steps_y = game.background.y // (image_rect.height)
	
# 	expected_screen.blit(game.backgroundimage, (game.background.x - image_rect.width * (1 + steps_x), game.background.y - image_rect.height * (1 + steps_y)))
# 	expected_screen.blit(game.backgroundimage, (game.background.x - image_rect.width * (1 + steps_x), game.background.y - image_rect.height * (0 + steps_y)))
# 	expected_screen.blit(game.backgroundimage, (game.background.x - image_rect.width * (0 + steps_x), game.background.y - image_rect.height * (1 + steps_y)))
# 	expected_screen.blit(game.backgroundimage, (game.background.x - image_rect.width * (0 + steps_x), game.background.y - image_rect.height * (0 + steps_y)))

# 	after_screen = game.screen.copy()

# 	assert pygame.image.tostring(expected_screen, 'RGBA') == pygame.image.tostring(after_screen, 'RGBA')


# def test_game_checkKeysPressed(pygame_setup, game: Game):
#     pass

# def test_game_updateGameScore(pygame_setup, game: Game):
#     pass

# def test_game_checkHitBoxes(pygame_setup, game: Game):
#     pass

# def test_game_damageEnemy(pygame_setup, game: Game):
#     pass

# def test_game_spawnWeaponKit(pygame_setup, game: Game):
#     pass

# def test_game_spawnMagnet(pygame_setup, game: Game):
#     pass

# def test_game_spawnEnemies(pygame_setup, game: Game):
#     pass

# def test_game_spawnEnemyDrops(pygame_setup, game: Game):
#     pass

# def test_game_updateItemPosition(pygame_setup, game: Game):
#     pass

# def test_game_updatePointingArrowPosition(pygame_setup, game: Game):
#     pass

# def test_game_updateEnemyPosition(pygame_setup, game: Game):
#     pass

# def test_game_updateExperiencePosition(pygame_setup, game: Game):
#     pass

# def test_game_getClosestEnemy(pygame_setup, game: Game):
#     pass

# def test_game_getCrit(pygame_setup, game: Game):
#     pass

# def test_game_startEvent(pygame_setup, game: Game):
#     pass

# def test_game_populateEventEnemies(pygame_setup, game: Game):
#     pass

# def test_game_updateEventTimer(pygame_setup, game: Game):
#     pass

# def test_game_attackCycle(pygame_setup, game: Game):
#     pass

# def test_game_passiveCycle(pygame_setup, game: Game):
#     pass

# def test_game_trasparentCycle(pygame_setup, game: Game):
#     pass

# def test_game_writeOnScreen(pygame_setup, game: Game):
#     pass

# def test_game_compareSutraction(pygame_setup, game: Game):
#     pass

# def test_game_getSign(pygame_setup, game: Game):
#     pass