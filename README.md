# Programming-II.-Assignment-II.
Github repository for the second assignment of Programming II.

## Updates:

### Update v1.0.0

-Uploaded first version, the working base of the game and class system.

### Update v1.0.1

-Made the game more flexible with more settings.

-Added attributes and functions to Weapon class.

-Added weapon cycle function to Game class.

-Added base weapon with reactive position based on player movement. Currently not checking hitbox.

### Update v1.0.2

-Added images directory with some images for menu buttons.

-Created in-game menu/pause system, still have to implement options menu.

### Update v1.0.3

-Added new weapon with a circle pattern.

-Added weapon kits and made them spawn every few seconds.

-Modified previous code so that the game objects are also sprites. -> easier to work with them and calculate collision with them.

-Made weapon kit's disappear on collision with the player.

### Update v1.0.4

-Added updates to readme.

-Created bullet class so that I can put them in a sprite group.

-Created several images for the weapon selection kit.

-Added base functions to weapon selection kit.

-Updated base rifle and energy ball.

-Created flamethrower and boomerang.

-Added upgrade methods to rifle, energy ball and boomerang.

-Added design to rifle, energy ball and boomerang.

### Update v1.0.5

-Fixed formatting of readme.

### Update v1.0.6

-Added Flamethrower scaling and design.

-Added Pistols mechanics, scaling and design.

-Started working on Drone following the player. (Still not right)

### Update v1.0.7

-Added Flamethrower projectile image.

-Updated Flamethrower projectiles when shot.

-Updated scaling of the level of Flamethrower.

### Update v1.1.0

-Added enemies, spawning and moving enemies. Added scaling to enemies.

-Added damage, damage scaling to weapons and enemies.

-Added collision checking between bullets and enemies. When collision happens, the damage of the bullet is removed from the enemies health.

-When an enemy is hit, it changes colour and it cannot be damaged by the same bullet for a short period of time.

-When enemies health drops to (or below) zero, the enemy is removed.

-Added basic timer, game level scales with each 30/60 seconds.

-Finished drone follow, added drone scaling, bullet mechanics.

### Update v1.1.1

-Added experience orbs, made them spawn when an enemy is defeated. Made them disappear when they collidee with the player.

-When the player moves close enough to an experience orb, the orb will flow to the player.

-Added a magnet item, that randomly spawns every 120-60 seconds. When picked up by the player, all experience orbs from almost anywhere fly towards the player.

-Added experience stat to player, leveling function when they pick up enough experience orbs.

-When the player levels up, the amount of experience will be greater to reach the next level than the last one. 

-Added scaling the player stats for speed, and health.

-Added damage function to enemies when they touch the player. When the player is damaged, they cannot be damaged for 1 second.

-Added experience bar on the bottom side of the screen. Also added health bar under the player.

-Made the experience bar change based on the percentage of the current experience / required experience for the next level.

-Made the health bar change based on the current health / max health of the player.

-Started working on passive talents and skills. When the player levels up, they will be able to choose from 3 options to either get a new skill or upgrade a previous one.

-Added a few images for the passive skills and one for the talents.

-Started working on the description for the passive skills.

### Update v1.1.2

-Finished description of passives. Started working on the description of weapons.

-Adjusted balance of all weapons and weaponkit spawn rate.

-Moved images around in the selector menu. Added description in the menu.

-Started working on the movement of boomerang.

-Added todo list in readme.

### Update v1.1.3

-Fixed the movement of boomerang. 

-Added return feature to the movement of boomerang.

### Update v1.1.4

-Renamed Remote Explosion to Cluster Bombs. Finished mechanics of cluster bomb. Adjusted balance of cluster bomb. Finished design of cluster bomb.

-Finished mechanics of damaging field. Adjusted balance of damaging field. Finished design of damaging field.

-Added status effect attributes to weapons and enemies. Enemies are now slowed when they enter damaging field. Enemies are now knocked back when damaged by several weapons.

-When the player collects a large amount of experience orbs, they will now select passives almost immediately after the previous one, this way the gameplay won't be that annoying. It still needs to be fine tuned. 

-Redid the calculations of all kinds of damage, so now I can change it with buffs and debuffs from different sources.

-Implemented health regeneration, protective barrier and greater strength. Created barrier bar over the health bar.

-When the player is damaged, the damage is first removed from the barrier.

### Update v1.1.5

-Implemented crit chance, berserk, slowing aura, gunslinger, dodge and greater vitality.

-Changed the z-indexes of some of the classes I paint over the screen. Transparent objects now appear under the player, the other bullets and the enemies.

-Transparent objects can make the game lag, so they might have to be changed later.

-Changed the list of player passives and weapons to dictionaries, so that I can access these passives and weapons without any iteration.

-Added some text on the screen, they still need their design to be edited though. (player weapons, player passives and levels, player max health, item names when selecting)

### Update v1.2.0

-Changed map range to infinite. Removed borders and movement restrictions.

-Added proper background that has clean cut edges. This way it seems like the background is infinite, because they are repeated next to each other.

-Made the background follow the player, so wherever they go there's a background behind them. I also don't have to load a thousand images every time.

## TODO list:

-Creating a buffs (and debuffs) list/dict/class for the player where I manage all the stat buffs for weapons, bullets, kits, player.

-Putting the exp orbs behind/under the enemies. Currently they are drawn over the enemies

-Making the design of the selectors better (e.g., fixing image sizes, positions, making letters larger, creating borders for the boxes, other colours)

-Adding an option to upgrade damage / attack speed for the weaponkit when every weapon upgrade is maxed out.

-Adding an option to upgrade player speed / heal player / create a weapon kit when every other passive is maxed out.

-Fixing balance of enemies. (stats and spawn rate)

-Fixing balance of rifle and orb.

-Fixing the hitbox of orb and cluster bombs.

-Fixing the balance with crowd control.

-Fixing descriptions of passives and weapons.

-Implementing all passives.

-Reducing lag when a large amount of sprite is on the screen. (e.g., experience disappeears after awhile / multiple ones for one big orb, reduce bullet counts (especially with culster bombs), reduce enemy count)

-Creating all talent images. Implementing all talents.

-Fixing the issue when a key from awsd is still pressed down when the selector menu opens, after the user chooses an option, the player character teleports based on the pressed button.

-Expanding the map, adding in background elements (e.g. stones, trees, a pond where the player can't go, etc.)

-Cleaning up the code by removing any unnececary lines and making it more efficient.

-New weapon: A cannon that shoots an orb that spreads in all direction after reaching a set distance/enemy.

-New weapon idea: Yondu's arrow.

There are other problems that need to be fixed, but those didn't really come to my mind. There are also biger parts of the project that are not yet implemented, those come later (e.g., main menu, settings menu, map selector, starter weapon selector, log in/sign up. user profile editing, scoreboard, etc.)