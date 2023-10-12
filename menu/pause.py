import pygame
import sys
from settings import *
from level import Level
from overworld import Overworld
from ui import UI
from gameover import GameOver
from pausabtn import PauseButton

class PauseScreen:
    def __init__(self, screen, resume_callback, quit_callback, return_to_overworld_callback):
        # Inicializa la pantalla de pausa
        self.screen = screen
        # Crea botones para "Reanudar" y "Salir"
        self.resume_button = PauseButton(None, (screen.get_width() // 2, screen.get_height() // 2 - 50), "Reanudar")
        self.quit_button = PauseButton(None, (screen.get_width() // 2, screen.get_height() // 2 + 50), "Salir")
        # Asigna las funciones de callback para "Reanudar" y "Salir"
        self.resume_callback = resume_callback
        self.quit_callback = quit_callback
        self.return_to_overworld_callback = return_to_overworld_callback
    
    def run_pause(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Si se presiona ESC, se llama a la función de reanudar y se sale del bucle
                        self.resume_callback()
                        running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.resume_button.checkForClick(event):
                        running = False
                        # Si se hace clic en "Reanudar", se llama a la función de reanudar y se sale del bucle
                        self.resume_callback()
                    elif self.quit_button.checkForClick(event):
                        running = False
                        # Si se hace clic en "Salir", se llama a la función de salir y regresar al Overworld
                        self.quit_callback()
                        self.return_to_overworld_callback()  # Regresa al Overworld

            # Actualiza el color de los botones cuando se pasa el mouse sobre ellos
            self.resume_button.changeColor(pygame.mouse.get_pos())
            self.quit_button.changeColor(pygame.mouse.get_pos())

            # Rellena la pantalla de pausa con color negro
            self.screen.fill("Black")
            # Actualiza y muestra los botones en la pantalla
            self.resume_button.update(self.screen)
            self.quit_button.update(self.screen)
            pygame.display.update()
