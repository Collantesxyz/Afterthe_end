import pygame
from support import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_height, screen_width
from tiles import Tile, StaticTile, Crate, Coin, Palm
from enemy import Enemy
from decoration import Sky, Water, Clouds
from player import Player
from particles import ParticleEffect
from game_data import levels

class Level:
	def __init__(self, current_level, surface, create_overworld, change_coins, change_health):
		# Configuración general
		self.display_surface = surface  # Superficie de visualización del juego
		self.world_shift = 0  # Desplazamiento del mundo
		self.current_x = None  # Posición actual en el eje X

		# Audio
		self.coin_sound = pygame.mixer.Sound('audio/effects/coin.wav')
		self.stomp_sound = pygame.mixer.Sound('audio/effects/stomp.wav')

		# Conexión con el mundo exterior (overworld)
		self.create_overworld = create_overworld  # Función para volver al overworld
		self.current_level = current_level  # Nivel actual
		level_data = levels[self.current_level]  # Datos del nivel actual
		self.new_max_level = level_data['unlock']  # Desbloqueo de niveles

		# Configuración del jugador
		player_layout = import_csv_layout(level_data['player'])  # Diseño del jugador
		self.player = pygame.sprite.GroupSingle()  # Grupo de sprites del jugador
		self.goal = pygame.sprite.GroupSingle()  # Grupo de sprites de objetivos
		self.player_setup(player_layout, change_health)  # Configuración del jugador

		# Interfaz de usuario
		self.change_coins = change_coins  # Función para cambiar la cantidad de monedas

		# Partículas de polvo
		self.dust_sprite = pygame.sprite.GroupSingle()  # Grupo de partículas de polvo
		self.player_on_ground = False  # Variable para controlar si el jugador está en el suelo

		# Partículas de explosión
		self.explosion_sprites = pygame.sprite.Group()  # Grupo de partículas de explosión

		# Configuración del terreno
		terrain_layout = import_csv_layout(level_data['terrain'])  # Diseño del terreno
		self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')  # Grupo de sprites de terreno

		# Configuración de la hierba
		grass_layout = import_csv_layout(level_data['grass'])  # Diseño de la hierba
		self.grass_sprites = self.create_tile_group(grass_layout, 'grass')  # Grupo de sprites de hierba

		# Configuración de las cajas
		crate_layout = import_csv_layout(level_data['crates'])  # Diseño de las cajas
		self.crate_sprites = self.create_tile_group(crate_layout, 'crates')  # Grupo de sprites de cajas

		# Configuración de las monedas
		coin_layout = import_csv_layout(level_data['coins'])  # Diseño de las monedas
		self.coin_sprites = self.create_tile_group(coin_layout, 'coins')  # Grupo de sprites de monedas

		# Palmeras en primer plano
		fg_palm_layout = import_csv_layout(level_data['fg palms'])  # Diseño de palmeras en primer plano
		self.fg_palm_sprites = self.create_tile_group(fg_palm_layout, 'fg palms')  # Grupo de sprites de palmeras en primer plano

		# Palmeras en segundo plano
		bg_palm_layout = import_csv_layout(level_data['bg palms'])  # Diseño de palmeras en segundo plano
		self.bg_palm_sprites = self.create_tile_group(bg_palm_layout, 'bg palms')  # Grupo de sprites de palmeras en segundo plano

		# Enemigos
		enemy_layout = import_csv_layout(level_data['enemies'])  # Diseño de enemigos
		self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')  # Grupo de sprites de enemigos

		# Restricciones
		constraint_layout = import_csv_layout(level_data['constraints'])  # Diseño de restricciones
		self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraint')  # Grupo de sprites de restricciones

		# Decoración
		self.sky = Sky(8)  # Cielo
		level_width = len(terrain_layout[0]) * tile_size  # Ancho del nivel
		self.water = Water(screen_height - 20, level_width)  # Agua
		self.clouds = Clouds(400, level_width, 30)  # Nubes

	# Método para crear un grupo de sprites a partir de un diseño
	def create_tile_group(self, layout, tipo):
		sprite_group = pygame.sprite.Group()

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index * tile_size
					y = row_index * tile_size

					if tipo == 'terrain':
						terrain_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(tile_size, x, y, tile_surface)
						
					if tipo == 'grass':
						grass_tile_list = import_cut_graphics('graphics/decoration/grass/grass.png')
						tile_surface = grass_tile_list[int(val)]
						sprite = StaticTile(tile_size, x, y, tile_surface)
					
					if tipo == 'crates':
						sprite = Crate(tile_size, x, y)

					if tipo == 'coins':
						if val == '0':
							sprite = Coin(tile_size, x, y, 'graphics/coins/gold', 5)
						if val == '1':
							sprite = Coin(tile_size, x, y, 'graphics/coins/silver', 1)

					if tipo == 'fg palms':
						if val == '0':
							sprite = Palm(tile_size, x, y, 'graphics/terrain/palm_small', 38)
						if val == '1':
							sprite = Palm(tile_size, x, y, 'graphics/terrain/palm_large', 64)

					if tipo == 'bg palms':
						sprite = Palm(tile_size, x, y, 'graphics/terrain/palm_bg', 64)

					if tipo == 'enemies':
						sprite = Enemy(tile_size, x, y)

					if tipo == 'constraint':
						sprite = Tile(tile_size, x, y)

					sprite_group.add(sprite)
		
		return sprite_group

	# Método para configurar el jugador y los objetivos
	def player_setup(self, layout, change_health):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * tile_size
				y = row_index * tile_size
				if val == '0':
					sprite = Player((x, y), self.display_surface, self.create_jump_particles, change_health)
					self.player.add(sprite)
				if val == '1':
					hat_surface = pygame.image.load('graphics/character/esqui.png').convert_alpha()
					sprite = StaticTile(tile_size, x, y, hat_surface)
					self.goal.add(sprite)

	# Método para gestionar la colisión de los enemigos con restricciones
	def enemy_collision_reverse(self):
		for enemy in self.enemy_sprites.sprites():
			if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
				enemy.reverse()

	# Método para crear partículas al saltar
	def create_jump_particles(self, pos):
		if self.player.sprite.facing_right:
			pos -= pygame.math.Vector2(10, 5)
		else:
			pos += pygame.math.Vector2(10, -5)
		jump_particle_sprite = ParticleEffect(pos, 'jump')
		self.dust_sprite.add(jump_particle_sprite)

	# Método para gestionar la colisión horizontal del jugador
	def horizontal_movement_collision(self):
		player = self.player.sprite
		player.collision_rect.x += player.direction.x * player.speed
		collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()
		for sprite in collidable_sprites:
			if sprite.rect.colliderect(player.collision_rect):
				if player.direction.x < 0: 
					player.collision_rect.left = sprite.rect.right
					player.on_left = True
					self.current_x = player.rect.left
				elif player.direction.x > 0:
					player.collision_rect.right = sprite.rect.left
					player.on_right = True
					self.current_x = player.rect.right

	# Método para gestionar la colisión vertical del jugador
	def vertical_movement_collision(self):
		player = self.player.sprite
		player.apply_gravity()
		collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()

		for sprite in collidable_sprites:
			if sprite.rect.colliderect(player.collision_rect):
				if player.direction.y > 0: 
					player.collision_rect.bottom = sprite.rect.top
					player.direction.y = 0
					player.on_ground = True
				elif player.direction.y < 0:
					player.collision_rect.top = sprite.rect.bottom
					player.direction.y = 0
					player.on_ceiling = True

		if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
			player.on_ground = False

	# Método para controlar el desplazamiento horizontal del jugador y la pantalla
	def scroll_x(self):
		player = self.player.sprite
		player_x = player.rect.centerx
		direction_x = player.direction.x

		if player_x < screen_width / 4 and direction_x < 0:
			self.world_shift = 8
			player.speed = 0
		elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
			self.world_shift = -8
			player.speed = 0
		else:
			self.world_shift = 0
			player.speed = 8

	# Método para verificar si el jugador está en el suelo
	def get_player_on_ground(self):
		if self.player.sprite.on_ground:
			self.player_on_ground = True
		else:
			self.player_on_ground = False

	# Método para crear partículas de polvo al aterrizar
	def create_landing_dust(self):
		if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
			if self.player.sprite.facing_right:
				offset = pygame.math.Vector2(10, 15)
			else:
				offset = pygame.math.Vector2(-10, 15)
			fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
			self.dust_sprite.add(fall_dust_particle)

	# Método para verificar la muerte del jugador y volver al overworld
	def check_death(self):
		if self.player.sprite.rect.top > screen_height:
			self.create_overworld(self.current_level, 0)

	# Método para verificar la victoria del jugador y avanzar al siguiente nivel
	def check_win(self):
		if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
			self.create_overworld(self.current_level, self.new_max_level)

	# Método para verificar colisiones con las monedas y actualizar el contador de monedas
	def check_coin_collisions(self):
		collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
		if collided_coins:
			self.coin_sound.play()
			for coin in collided_coins:
				self.change_coins(coin.value)

	# Método para verificar colisiones con los enemigos y gestionar las interacciones
	def check_enemy_collisions(self):
		enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)

		if enemy_collisions:
			for enemy in enemy_collisions:
				enemy_center = enemy.rect.centery
				enemy_top = enemy.rect.top
				player_bottom = self.player.sprite.rect.bottom
				if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
					self.stomp_sound.play()
					self.player.sprite.direction.y = -15
					explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
					self.explosion_sprites.add(explosion_sprite)
					enemy.kill()
				else:
					self.player.sprite.get_damage()

	# Método principal para ejecutar el juego o nivel completo
	def run(self):
		# Ejecutar todo el juego o nivel completo

		# Cielo
		self.sky.draw(self.display_surface)
		self.clouds.draw(self.display_surface, self.world_shift)

		# Palmeras en segundo plano
		self.bg_palm_sprites.update(self.world_shift)
		self.bg_palm_sprites.draw(self.display_surface)

		# Partículas de polvo
		self.dust_sprite.update(self.world_shift)
		self.dust_sprite.draw(self.display_surface)

		# Terreno
		self.terrain_sprites.update(self.world_shift)
		self.terrain_sprites.draw(self.display_surface)

		# Enemigos
		self.enemy_sprites.update(self.world_shift)
		self.constraint_sprites.update(self.world_shift)
		self.enemy_collision_reverse()
		self.enemy_sprites.draw(self.display_surface)
		self.explosion_sprites.update(self.world_shift)
		self.explosion_sprites.draw(self.display_surface)

		# Cajas
		self.crate_sprites.update(self.world_shift)
		self.crate_sprites.draw(self.display_surface)

		# Hierba
		self.grass_sprites.update(self.world_shift)
		self.grass_sprites.draw(self.display_surface)

		# Monedas
		self.coin_sprites.update(self.world_shift)
		self.coin_sprites.draw(self.display_surface)

		# Palmeras en primer plano
		self.fg_palm_sprites.update(self.world_shift)
		self.fg_palm_sprites.draw(self.display_surface)

		# Jugador
		self.player.update()
		self.horizontal_movement_collision()

		self.get_player_on_ground()
		self.vertical_movement_collision()
		self.create_landing_dust()

		self.scroll_x()
		self.player.draw(self.display_surface)
		self.goal.update(self.world_shift)
		self.goal.draw(self.display_surface)

		self.check_death()
		self.check_win()

		self.check_coin_collisions()
		self.check_enemy_collisions()

		# Agua
		self.water.draw(self.display_surface, self.world_shift)
