import pygame
from game_data import levels
from support import import_folder
from decoration import Sky
import os
import sys

# Obtiene la ruta al directorio raíz del proyecto (GameAlexisLzL)
ruta_directorio = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_directorio)
from botones import Button

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, path):
        super().__init__()
        self.frames = import_folder(path)  # Carga las imágenes del nodo
        self.frame_index = 0
        self.image = self.frames[self.frame_index]  # Establece la imagen inicial
        if status == 'available':
            self.status = 'available'  # Define el estado como disponible
        else:
            self.status = 'locked'  # Define el estado como bloqueado
        self.rect = self.image.get_rect(center=pos)

        # Zona de detección para el ícono
        self.detection_zone = pygame.Rect(self.rect.centerx - (icon_speed / 2),
                                         self.rect.centery - (icon_speed / 2), icon_speed, icon_speed)

    def animate(self):
        # Realiza la animación del nodo cambiando de imagen
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        if self.status == 'available':
            self.animate()  # Si está disponible, anima el nodo
        else:
            tint_surf = self.image.copy()
            tint_surf.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surf, (0, 0))  # Oscurece la imagen si está bloqueada

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load('graphics/overworld/hat.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center = self.pos  # Actualiza la posición del ícono

class Overworld:
    def __init__(self, start_level, max_level, surface, create_level):
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level

        self.moving = False
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 8

        self.setup_nodes()  # Inicializa los nodos
        self.setup_icon()  # Inicializa el ícono
        self.sky = Sky(8, 'overworld')  # Crea el fondo del cielo

        self.start_time = pygame.time.get_ticks()
        self.allow_input = False
        self.timer_length = 300

        return_button_pos = (50, 50)
        return_button = Button(None, return_button_pos, "", pygame.font.Font(None, 36), (255, 255, 255), (200, 200, 200))
        self.return_button = return_button

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()

        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                node_sprite = Node(node_data['node_pos'], 'available', self.speed, node_data['node_graphics'])
            else:
                node_sprite = Node(node_data['node_pos'], 'locked', self.speed, node_data['node_graphics'])
            self.nodes.add(node_sprite)

    def draw_paths(self):
        if self.max_level > 0:
            points = [node['node_pos'] for index, node in enumerate(levels.values()) if index <= self.max_level]
            # pygame.draw.lines(self.display_surface, '#a04f45', False, points, 6)
            # Dibuja líneas que conectan los nodos disponibles en el mapa

    def setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()
        if 0 <= self.current_level < len(self.nodes.sprites()):
            icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
            self.icon.add(icon_sprite)
        else:
            # Lógica de manejo de error si self.current_level está fuera de los límites
            pass

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.moving and self.allow_input:
            if keys[pygame.K_RETURN]:
                self.create_level(self.current_level)

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)

    def input_timer(self):
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.timer_length:
                self.allow_input = True

    def run(self):
        self.input_timer()
        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.nodes.update()

        self.sky.draw(self.display_surface)  # Dibuja el fondo del cielo
        self.draw_paths()  # Dibuja las rutas entre los nodos
        self.nodes.draw(self.display_surface)  # Dibuja los nodos
        self.icon.draw(self.display_surface)  # Dibuja el ícono

        self.return_button.update(self.display_surface)  # Actualiza el botón de retorno

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Implementa tu lógica para pausar el juego, si es necesario
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.return_button.checkForInput(event.pos):
                        from start import bienvenida
                        bienvenida()
                        # Lógica para regresar al estado 'start.py'
                        pygame.quit()  # Cierra Pygame
                        sys.exit()  # Sale del programa
