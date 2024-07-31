import os
import pygame as pg
from src.geo import World


class Game:
    def __init__(self, screen, clock, window_size) -> None:
        self.screen = screen
        self.clock = clock
        self.window_size = window_size
        self.playing = True

        self.BASE_PATH = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/").replace("/src", "")

        self.world = World(self.BASE_PATH)

    def run(self) -> None:
        while self.playing:
            self.clock.tick(60)

            self.screen.fill((0, 0, 0))

            self.events()
            self.update()
            self.draw()

            pg.display.update()

    def events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.playing = False

    def update(self) -> None:
        pass

    def draw(self) -> None:
        self.world.draw(self.screen)
