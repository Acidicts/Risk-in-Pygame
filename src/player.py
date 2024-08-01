import pygame as pg

from src.geo import Country, World


class Player:
    def __init__(self, country, world, color) -> None:
        self.buffer = 0
        self.country = country
        self.world = world
        self.color = color

        self.country.color = self.color

        self.timer = pg.time.get_ticks()

        self.controlled_countries = [self.country.name]
        self.neighbors = None

        self.has_attacked = False

        self.move_country_from = ""
        self.move_country_to = ""
        self.move_n_units = 0

        self.attack_country_from = ""
        self.attack_country_to = ""

    def update(self, phase) -> None:
        if phase == "place_units":
            self.place_units()
        elif phase == "move_units":
            self.move_units()
        elif phase == "attack_country":
            self.attack_country()

    def place_units(self) -> None:
        now = pg.time.get_ticks()

        for country in self.controlled_countries:

            c = self.world.countries.get(country)

            if c.hovered and pg.mouse.get_pressed()[0] and now - self.timer > 300:
                self.timer = now
                self.country.units += 1

    def move_units(self) -> None:

        now = pg.time.get_ticks()

        if self.move_country_from == "":
            for country in self.controlled_countries:
                c = self.world.countries[country]

                if c.hovered and pg.mouse.get_pressed()[0] and not c.has_attacked:
                    self.move_country_from = c.name

        if self.move_country_to == "" and self.move_country_from != "":
            for country in self.controlled_countries:
                c = self.world.countries[country]

                if c.hovered and pg.mouse.get_pressed()[0] and c.name != self.move_country_from:
                    self.move_country_to = c.name

        if pg.mouse.get_pressed()[2]:
            self.move_country_from = ""
            self.move_country_to = ""

        keys = pg.key.get_pressed()

        if self.move_country_from != "" and self.move_country_to != "":
            c_from = self.world.countries[self.move_country_from]
            c_to = self.world.countries[self.move_country_to]

            self.move_n_units += int(now - self.timer > 200) * (int(keys[pg.K_UP]) - int(keys[pg.K_DOWN]))

            if self.move_n_units != self.buffer:
                self.timer = now
                self.buffer = self.move_n_units

            if keys[pg.K_RETURN]:
                if c_from.units > self.move_n_units > 0:
                    c_from.units -= self.move_n_units
                    c_to.units += self.move_n_units

                    self.move_country_from = ""
                    self.move_country_to = ""
                    self.move_n_units = 0

                    self.timer = now

    def attack_country(self) -> None:
        if self.attack_country_from == "":
            for country in self.controlled_countries:
                c = self.world.countries[country]

                if c.hovered and pg.mouse.get_pressed()[0] and not c.has_attacked:
                    self.attack_country_from = c.name

        if self.attack_country_to == "" and self.attack_country_from != "":
            for country in self.world.countries[self.attack_country_from].neighbors:
                if country not in self.controlled_countries:
                    c = self.world.countries[country]

                    if c.hovered and pg.mouse.get_pressed()[0]:
                        self.attack_country_to = c.name

        if pg.mouse.get_pressed()[2]:
            self.attack_country_from = ""
            self.attack_country_to = ""

        keys = pg.key.get_pressed()
        if keys[pg.K_RETURN] and self.attack_country_from != "" and self.attack_country_to != "":
            self.world.battle(self.attack_country_from, self.attack_country_to)

            if self.world.battle_res["victory"]:
                c = self.world.countries[self.attack_country_to]

            self.attack_country_to = ""
            self.attack_country_from = ""

    def get_neighbors(self) -> list:
        neighbors = []

        for country in self.controlled_countries:
            for neighbor in self.world.countries[country].neighbors:
                if neighbor not in self.controlled_countries:
                    neighbors.append(neighbor)

        return list(set(neighbors))

    def conquer(self, country):
        country.controlled_by = self.country.name
        country.color = self.color
        self.controlled_countries.append(country.name)
        self.neighbors = self.get_neighbors()
        self.controlled_countries = list(set(self.controlled_countries))

    def reset_turn(self) -> None:
        self.timer = 0

        self.move_country_to = ""
        self.move_country_from = ""

        self.attack_country_from = ""
        self.attack_country_to = ""

        for country in self.controlled_countries:
            self.world.countries[country].has_attacked = False
