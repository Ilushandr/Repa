from io import BytesIO
import os
import pygame
import requests

KEYS = (pygame.K_PAGEDOWN, pygame.K_PAGEUP,
        pygame.K_UP, pygame.K_DOWN,
        pygame.K_LEFT, pygame.K_RIGHT,
        pygame.K_m, pygame.K_s, pygame.K_h)
url_static = 'http://static-maps.yandex.ru/1.x/'
lon_delta = 300
lat_delta = 100


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
        filename = 'temp_img.png'
        with open(filename, 'wb') as file:
            file.write(response.content)
        self.map = pygame.image.load(filename)
        os.remove(filename)

    def update(self, event):
        if event.key == pygame.K_PAGEUP:
            self.z = min(17, self.z + 1)
        elif event.key == pygame.K_PAGEDOWN:
            self.z = max(0, self.z - 1)
        elif event.key == pygame.K_RIGHT:
            self.lon = ((self.lon + 180 + lon_delta * 2 ** -self.z) % 360 - 180)
        elif event.key == pygame.K_LEFT:
            self.lon = ((self.lon + 180 - lon_delta * 2 ** -self.z) % 360 - 180)
        elif event.key == pygame.K_UP:
            self.lat = min(85, self.lat + lat_delta * 2 ** -self.z)
        elif event.key == pygame.K_DOWN:
            self.lat = max(-85, self.lat - lat_delta * 2 ** -self.z)
        elif event.key == pygame.K_m:
            self.layer = 'map'
        elif event.key == pygame.K_s:
            self.layer = 'sat'
        elif event.key == pygame.K_h:
            self.layer = 'sat,skl'
        if event.key in KEYS:
            self.update_map()


pygame.init()
screen = pygame.display.set_mode((650, 450))
coord = (38.2052612, 44.4192543)
z = 15
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
