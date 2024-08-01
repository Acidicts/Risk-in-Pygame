import pygame as pg

from src.geo import Country, World


class Player:
    def __init__(self, country, world, color) -> None:
        self.country = country
        self.world = world
        self.color = color

        self.country.color = self.color

        self.timer = pg.time.get_ticks()

        self.controlled_countries = [self.country.name]

        self.neighbors = self.get_neighbors()

    def update(self, phase) -> None:
        if phase == "place_units":
            self.place_units()
        elif phase == "move_units":
            self.move_units()
        elif phase == "attack":
            self.attack_country()

    def place_units(self) -> None:
        now = pg.time.get_ticks()

        for country in self.controlled_countries:

            c = self.world.countries.get(country)

            if c.hovered and pg.mouse.get_pressed()[0] and now - self.timer > 300:
                self.timer = now
                self.country.units += 1

    def move_units(self) -> None:
        pass

    def attack_country(self) -> None:
        pass

    def get_neighbors(self) -> list:
        neighbors = []

        for country in self.controlled_countries:
            for neighbor in self.world.countries[country].neighbors:
                if neighbor not in self.controlled_countries:
                    neighbors.append(neighbor)

        return list(set(neighbors))
