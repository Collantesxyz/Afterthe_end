# Importa las constantes y módulos necesarios desde otros archivos
from settings import vertical_tile_number, tile_size, screen_width
import pygame
from tiles import AnimatedTile, StaticTile
from support import import_folder
from random import choice, randint

# Define la clase Sky que representa el cielo en el juego
class Sky:
	def __init__(self, horizon, style='level'):
		# Carga las imágenes para el cielo superior, medio e inferior
		self.top = pygame.image.load('graphics/decoration/sky/sky_top.png').convert()
		self.bottom = pygame.image.load('graphics/decoration/sky/sky_bottom.png').convert()
		self.middle = pygame.image.load('graphics/decoration/sky/sky_middle.png').convert()
		self.horizon = horizon

		# Ajusta el tamaño de las imágenes para que se ajusten a la pantalla
		self.top = pygame.transform.scale(self.top, (screen_width, tile_size))
		self.bottom = pygame.transform.scale(self.bottom, (screen_width, tile_size))
		self.middle = pygame.transform.scale(self.middle, (screen_width, tile_size))

		self.style = style
		if self.style == 'overworld':
			# Carga imágenes de palmeras y nubes para el escenario de "overworld"
			palm_surfaces = import_folder('graphics/overworld/palms')
			self.palms = []

			# Genera ubicaciones aleatorias para las palmeras y las almacena en una lista
			for surface in [choice(palm_surfaces) for image in range(10)]:
				x = randint(0, screen_width)
				y = (self.horizon * tile_size) + randint(50, 100)
				rect = surface.get_rect(midbottom=(x, y))
				self.palms.append((surface, rect))

			cloud_surfaces = import_folder('graphics/overworld/clouds')
			self.clouds = []

			# Genera ubicaciones aleatorias para las nubes y las almacena en una lista
			for surface in [choice(cloud_surfaces) for image in range(10)]:
				x = randint(0, screen_width)
				y = randint(0, (self.horizon * tile_size) - 100)
				rect = surface.get_rect(midbottom=(x, y))
				self.clouds.append((surface, rect))

	# Dibuja el cielo en la superficie especificada
	def draw(self, surface):
		for row in range(vertical_tile_number):
			y = row * tile_size
			if row < self.horizon:
				surface.blit(self.top, (0, y))
			elif row == self.horizon:
				surface.blit(self.middle, (0, y))
			else:
				surface.blit(self.bottom, (0, y))

		# Si el estilo es 'overworld', dibuja las palmeras y las nubes
		if self.style == 'overworld':
			for palm in self.palms:
				surface.blit(palm[0], palm[1])
			for cloud in self.clouds:
				surface.blit(cloud[0], cloud[1])

# Define la clase Water que representa el agua en el juego
class Water:
	def __init__(self, top, level_width):
		# Configura la animación de las baldosas de agua
		water_start = -screen_width
		water_tile_width = 192
		tile_x_amount = int((level_width + screen_width * 2) / water_tile_width)
		self.water_sprites = pygame.sprite.Group()

		# Crea baldosas animadas de agua y las agrega al grupo
		for tile in range(tile_x_amount):
			x = tile * water_tile_width + water_start
			y = top
			sprite = AnimatedTile(192, x, y, 'graphics/decoration/water')
			self.water_sprites.add(sprite)

	# Dibuja el agua en la superficie especificada, aplicando un desplazamiento
	def draw(self, surface, shift):
		self.water_sprites.update(shift)
		self.water_sprites.draw(surface)

# Define la clase Clouds que representa las nubes en el juego
class Clouds:
	def __init__(self, horizon, level_width, cloud_number):
		# Carga imágenes de nubes y define las coordenadas de aparición
		cloud_surf_list = import_folder('graphics/decoration/clouds')
		min_x = -screen_width
		max_x = level_width + screen_width
		min_y = 0
		max_y = horizon
		self.cloud_sprites = pygame.sprite.Group()

		# Crea nubes estáticas y las agrega al grupo
		for cloud in range(cloud_number):
			cloud = choice(cloud_surf_list)
			x = randint(min_x, max_x)
			y = randint(min_y, max_y)
			sprite = StaticTile(0, x, y, cloud)
			self.cloud_sprites.add(sprite)

	# Dibuja las nubes en la superficie especificada, aplicando un desplazamiento
	def draw(self, surface, shift):
		self.cloud_sprites.update(shift)
		self.cloud_sprites.draw(surface)
