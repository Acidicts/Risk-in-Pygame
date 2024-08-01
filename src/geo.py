import json
import pygame as pg
import random

from pandas import Series
from shapely.geometry import Point, Polygon
from src.utils import draw_text, draw_multiline_text


class Country:
    def __init__(self, name, coords) -> None:
        self.name = name
        self.coords = coords

        self.polygon = Polygon(coords)
        self.center = self.get_center()

        self.units = random.randint(1, 3)
        self.color = (72, 126, 176)
        self.hovered = False

        self.controlled_by = self.name
        self.has_attacked = False

    def update(self, mouse_pos) -> None:
        self.hovered = False

        if Point(mouse_pos[0], mouse_pos[1]).within(self.polygon):
            self.hovered = True

    def draw(self, screen, scroll, font) -> None:
        if self.hovered:
            col = (255, 0, 0)
        else:
            col = self.color
        pg.draw.polygon(screen, col, [(x - scroll.x, y - scroll.y) for x, y in self.coords])
        pg.draw.polygon(screen, (255, 255, 255), [(x - scroll.x, y - scroll.y) for x, y in self.coords], width=1)
        draw_text(screen, font, str(self.units), (255, 255, 255),
                  self.center.x - scroll[0], self.center.y - scroll[1], True)

    def get_center(self) -> pg.Vector2:
        return pg.Vector2(
            Series([x for x, y in self.coords]).mean(),
            Series([y for x, y in self.coords]).mean(),
            )


class World:

    MAP_WIDTH = 2.05 * 4000
    MAP_HEIGHT = 1.0 * 4000

    def __init__(self, base_path) -> None:
        self.BASE_PATH = base_path

        self.geo_data = {}
        self.read_geo_data()
        self.font = pg.font.SysFont(None, 20)

        self.countries = self.create_countries()
        self.create_neighbors()

        self.scroll = pg.Vector2(3650, 395)

        self.hovered_country = None
        self.hover_surf = pg.Surface((300, 100), pg.SRCALPHA)
        self.hover_surf.fill((25, 42, 86, 155))

        self.battle_res = None

    def read_geo_data(self) -> None:
        with open(self.BASE_PATH + "/data/country_coords.json", "r") as f:
            self.geo_data = json.load(f)

    def create_countries(self) -> dict:
        countries = {}

        for name, coords in self.geo_data.items():
            xy_coords = []

            for coord in coords:
                x = (self.MAP_WIDTH / 360) * (180 + coord[0])
                y = (self.MAP_HEIGHT / 180) * (90 - coord[1])
                xy_coords.append((x, y))

            countries[name] = Country(name, xy_coords)

        return countries

    def draw(self, surf) -> None:
        for country in self.countries.values():
            country.draw(surf, self.scroll, self.font)
        if self.hovered_country is not None:
            self.draw_hovered_country(surf)

    def update(self) -> None:
        mouse_pos = pg.mouse.get_pos()

        self.update_camera()
        self.hovered_country = None

        for country in self.countries.values():
            country.update((mouse_pos[0] + self.scroll.x, mouse_pos[1] + self.scroll.y))
            if country.hovered:
                self.hovered_country = country

    def update_camera(self) -> None:
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.scroll.y -= 5
        if keys[pg.K_s]:
            self.scroll.y += 5

        if keys[pg.K_a]:
            self.scroll.x -= 5
        if keys[pg.K_d]:
            self.scroll.x += 5

        if keys[pg.K_SPACE]:
            self.scroll = pg.Vector2(3650, 395)

    def draw_hovered_country(self, surf) -> None:
        surf.blit(self.hover_surf, (1280 - 310, 720 - 110))
        draw_text(
            surf,
            self.font,
            self.hovered_country.name,
            (255, 255, 255),
            1280 - 160, 720 - 90,
            True
        )

        draw_multiline_text(
            surf,
            pg.font.SysFont(None, 20),
            [f"Units: {str(self.hovered_country.units)}"],
            (255, 255, 255),
            1280 - 160, 720 - 70,
            True,
            20)

    def create_neighbors(self) -> None:
        for k, v in self.countries.items():
            v.neighbors = self.get_country_neighbors(k)

    def get_country_neighbors(self, country) -> list:
        neighbors = []

        country_poly = self.countries.get(country).polygon

        for other_country_key, other_country_value in self.countries.items():
            if country != other_country_key:
                if country_poly.intersects(other_country_value.polygon):
                    neighbors.append(other_country_key)

        islands = {
            "United Kingdom": ["Ireland", "France", "Iceland"],
            "Ireland": ["United Kingdom", "Iceland"],
            "Iceland": ["United Kingdom", "Ireland"],
            "France": ["United Kingdom"],
            "Denmark": ["Norway", "Sweden"],
            "Norway": ["Denmark"],
            "Sweden": ["Denmark"],
            "Finland": ["Estonia"],
            "Estonia": ["Finland"],
        }

        for island, neighbor in islands.items():
            if country == island:
                neighbors += neighbor

        return neighbors

    def battle(self, attacker, defender) -> None:
        a_c = self.countries[attacker]
        d_c = self.countries[defender]

        a_c.has_attacked = True

        res = {
            "attacking": attacker,
            "defending": defender,
            "victory": False,
            "attacking_country_losses": 0,
            "defending_country_losses": 0,
        }

        while a_c.units > 1 and d_c.units > 0:

            if a_c.units - d_c.units > 2:
                attack_dice = max(random.randint(1, 6), random.randint(1, 6))
            else:
                attack_dice = random.randint(1, 6)

            defender_dice = random.randint(1, 6)
            
            if attack_dice > defender_dice:
                d_c.units -= 1
                res["defending_country_losses"] += 1
            else:
                a_c.units -= 1
                res["attacking_country_losses"] += 1
            
            if d_c.units == 0:
                res["victory"] = True
        
        if res["victory"]:
            d_c.units = 1
            a_c.units -= 1
            
        self.battle_res = res
        