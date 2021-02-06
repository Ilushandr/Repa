import os
import sys
from io import BytesIO
import pygame
import requests

KEYS = (pygame.K_PAGEDOWN, pygame.K_PAGEUP,
        pygame.KEYUP, pygame.KEYDOWN,
        pygame.K_LEFT, pygame.K_RIGHT)
url_static = 'http://static-maps.yandex.ru/1.x/'


class Map:
    def __init__(self, coord, zoom, layer='map', size=(650, 450)):
        self.lon, self.lat = coord
        self.z = zoom
        self.layer = layer
        self.w, self.h = size
        self.update_map()

    def update_map(self):
        params = {
            'l': self.layer,
            'll': f'{self.lon},{self.lat}',
            'z': self.z,
            'size': f'{self.w},{self.h}'
        }
        response = requests.get(url_static, params)
        if not response:
            raise RuntimeError('Ошибка выполнения запроса')
        self.map = pygame.image.load(BytesIO(response.content))

    def update(self, event):
        if event.key == pygame.K_PAGEUP and self.z < 17:
            self.z = min(17, self.z + 1)
            self.update_map()
        elif event.key == pygame.K_PAGEDOWN and self.z > 0:
            self.z = max(0, self.z - 1)
        if event.key in KEYS:
            self.update_map()


pygame.init()
screen = pygame.display.set_mode((650, 450))
coord = (38.2052612, 44.4192543)
z = 17
map = Map(coord, z)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            map.update(event)
    screen.blit(map.map, (0, 0))
    pygame.display.flip()
pygame.quit()
