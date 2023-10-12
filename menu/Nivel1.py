import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld
from ui import UI
from gameover import GameOver
from pause import PauseScreen

class Game:
    def __init__(self):
        # Atributos del juego
        self.max_level = 2
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0
        

        # Configura la música de fondo
        pygame.mixer.music.load('audio/level_music.wav')
        pygame.mixer.music.set_volume(0.5)

        # Interfaz de usuario
        self.ui = UI(screen)

        # Creación del mundo principal
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        self.paused = False

        # Superficie para pantalla de pausa
        self.pause_message = pygame.font.Font(None, 36).render("Juego en pausa", True, (255, 255, 255))

        # Variable para controlar el estado del botón de pausa
        self.pause_button_clicked = False

        # Variable para controlar el estado de la tecla espaciadora
        self.space_pressed = False

        # Importa la clase PauseButton
        from pausabtn import PauseButton

        # Crea un botón de regreso en el juego
        self.back_button = PauseButton(None, (50, 50), "Regresar")  # Ajusta las coordenadas según tu diseño

    def create_level(self, current_level):
        # Detiene la música de nivel antes de reproducirla nuevamente
        pygame.mixer.music.stop()
        self.level = Level(current_level, screen, self.create_overworld, self.change_coins, self.change_health)
        self.status = 'level'
        # Reproduce la música de fondo del nivel
        pygame.mixer.music.play(-1)

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        # Reproduce la música de fondo del mapa principal
        pygame.mixer.music.play(-1)

    def change_coins(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.cur_health += amount

    def check_game_over(self):
        if self.cur_health <= 0 or (self.status == 'level' and self.level.player.sprite.rect.y > screen_height):
            self.cur_health = 100
            self.coins = 0
            self.max_level = 0
            # Reproduce la música de fondo del mapa principal
            pygame.mixer.music.load('audio/overworld_music.wav')
            pygame.mixer.music.play(-1)
            game_over = GameOver(screen)
            while True:
                if game_over.handle_events():
                    self.overworld = Overworld(0, self.max_level, screen, self.create_level)
                    self.status = 'overworld'
                    return
                game_over.draw()
                pygame.display.update()

    def show_pause_screen(self):
        # Pausa el juego
        self.paused = True
        pygame.mixer.music.pause()
        # Muestra la pantalla de pausa
        pause_screen = PauseScreen(screen, self.resume_game, self.quit_callback, self.return_to_overworld)
        pause_screen.run_pause()

    def resume_game(self):
        self.paused = not self.paused
        if self.paused:
            pygame.mixer.music.pause()
            self.show_pause_screen()
        else:
            pygame.mixer.music.unpause()

    def return_to_overworld(self):
        self.status = 'overworld'
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        pygame.mixer.music.unpause()

    def quit_callback(self):
        self.status = 'overworld'
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        pygame.mixer.music.stop()  # Detiene la música de fondo
        self.paused = False  # Agrega esta línea para salir del bucle de pausa

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    if self.paused:
                        pygame.mixer.music.pause()
                        self.show_pause_screen()
                    else:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_SPACE and self.status == 'overworld' and not self.space_pressed:
                    # Detiene la música de fondo del mapa principal antes de reproducirla nuevamente
                    pygame.mixer.music.stop()
                    # Reproduce la música de fondo del mapa principal
                    pygame.mixer.music.load('audio/overworld_music.wav')
                    pygame.mixer.music.play(-1)
                    self.space_pressed = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.space_pressed = False

        if not self.paused:
            pygame.mixer.music.unpause()

            if self.status == 'overworld':
                self.overworld.run()
            else:
                self.level.run()
                self.ui.show_health(self.cur_health, self.max_health)
                self.ui.show_coins(self.coins)
                self.check_game_over()

                if self.cur_health <= 0 or self.level.player.sprite.rect.y > screen_height:
                    game_over = GameOver(screen)
                    while True:
                        if game_over.handle_events():
                            self.overworld = Overworld(0, self.max_level, screen, self.create_level)
                            self.status = 'overworld'
                            return
                        game_over.draw()
                        pygame.display.update()

# Configuración de Pygame
pygame.init()
clock = pygame.time.Clock()
FPS = 60
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()

while True:
    game.run()
    pygame.display.update()
    clock.tick(FPS)
